# Ngân hàng câu hỏi (Question Bank) — Tài liệu tìm hiểu

> **Mục đích**: hiểu ngân hàng câu hỏi đang *thực sự* hoạt động thế nào trong code hiện tại —
> các thực thể, cách tạo câu hỏi, cấu trúc dữ liệu từng loại câu hỏi, vòng đời duyệt,
> và đường đi từ câu hỏi ra đề thi.
>
> Tài liệu này mô tả **hiện trạng code**, không phải tầm nhìn sản phẩm.
> Bản mô tả tầm nhìn (có cả phần chưa xây) nằm ở
> [backend/docs/product/question-bank.md](backend/docs/product/question-bank.md).
> Hợp đồng API chi tiết cho FE: [backend/docs/QUESTION_BANK_API_GUIDE.md](backend/docs/QUESTION_BANK_API_GUIDE.md).
>
> Ngày rà soát: 2026-08-17.

---

## Mục lục

1. [Bức tranh tổng thể](#1-bức-tranh-tổng-thể)
2. [Các thực thể và mô hình dữ liệu](#2-các-thực-thể-và-mô-hình-dữ-liệu)
3. [Hệ phân loại: Môn → Lớp → Thư mục](#3-hệ-phân-loại-môn--lớp--thư-mục)
4. [Thư mục câu hỏi](#4-thư-mục-câu-hỏi)
5. [Năm cách tạo câu hỏi](#5-năm-cách-tạo-câu-hỏi)
6. [Cấu trúc `content_json` theo từng loại câu hỏi](#6-cấu-trúc-content_json-theo-từng-loại-câu-hỏi)
7. [Quy tắc kiểm tra dữ liệu và các cạm bẫy](#7-quy-tắc-kiểm-tra-dữ-liệu-và-các-cạm-bẫy)
8. [Vòng đời và quy trình duyệt](#8-vòng-đời-và-quy-trình-duyệt)
9. [Tìm kiếm, lọc, thao tác hàng loạt](#9-tìm-kiếm-lọc-thao-tác-hàng-loạt)
10. [Thùng rác](#10-thùng-rác)
11. [Từ câu hỏi ra đề thi](#11-từ-câu-hỏi-ra-đề-thi)
12. [Đẩy sang Cohota](#12-đẩy-sang-cohota)
13. [Quota và chi phí AI](#13-quota-và-chi-phí-ai)
14. [Bản đồ màn hình FE ↔ API ↔ file code](#14-bản-đồ-màn-hình-fe--api--file-code)
15. [Danh mục API đầy đủ](#15-danh-mục-api-đầy-đủ)
16. [Những gì chưa có](#16-những-gì-chưa-có)

---

## 1. Bức tranh tổng thể

Ngân hàng câu hỏi là hệ thống quản lý **Question Card (QuC)** — đơn vị học liệu nhỏ nhất,
có cấu trúc, có metadata, có vòng đời duyệt, và có thể tái tổ hợp thành đề thi.

Luồng chính từ lúc sinh ra tới lúc in đề:

```
                 ┌─ tạo tay (form / notebook)
                 ├─ AI sinh hàng loạt (/generate)
   Câu hỏi ◄─────┼─ AI đổi loại (/convert)
   (QuestionCard)├─ nhân bản (/duplicate)
                 └─ Excel intake (offline, chuyên gia điền)
        │
        │  status: new → in_review → approved / rejected
        ▼
   Duyệt (review queue / review session)
        │
        ▼
   Giỏ câu hỏi (Cart, riêng từng user)
        │
        ▼
   Bộ câu hỏi (Collection)  ── readiness = mọi câu đều approved
        │
        ▼
   Đề thi (TestPaper) ──► Canvas document (in DOCX/PDF)
        ├─► Thẻ đáp án (AnswerCard)
        └─► Mã đề (TestPaperVariant: trộn câu, trộn phương án)
```

Ba nguyên tắc xuyên suốt trong code:

1. **Mọi thứ đóng khung trong `organization_id`.** Không có truy vấn nào vượt tổ chức.
2. **Câu hỏi thuộc thư mục thì thư mục là nguồn chân lý.** `subject`/`grade`/`topic` của
   câu hỏi luôn bị ghi đè theo thư mục ở cả lúc tạo lẫn lúc sửa.
3. **AI chỉ được sinh những gì backend tự kiểm tra được.** 9 loại câu hỏi tồn tại, nhưng AI
   chỉ sinh 4 loại — 4 loại đó có model Pydantic để validate, nên payload sai sẽ bị chính
   validator của mình chặn thay vì lọt xuống DB.

---

## 2. Các thực thể và mô hình dữ liệu

File: [backend/services/api/src/bookforge_api/models/question_bank.py](backend/services/api/src/bookforge_api/models/question_bank.py)

| Bảng | Vai trò |
| --- | --- |
| `question_folders` | Thư mục chứa câu hỏi. Có `subject`, `grade`, màu, quyền, tags. |
| `question_cards` | Câu hỏi. Trái tim của hệ thống. |
| `question_review_sessions` + `_items` | Phiên duyệt: gom N câu cho 1 người duyệt, theo dõi tiến độ. |
| `question_cart_items` | Giỏ câu hỏi — **riêng từng user**, không phải từng tổ chức. |
| `question_collections` + `_items` | Bộ câu hỏi có thứ tự, dùng để dựng đề. |
| `test_papers` + `_items` | Đề thi + snapshot từng câu tại thời điểm chốt đề. |
| `test_paper_variants` | Mã đề (trộn thứ tự câu / phương án theo seed). |
| `answer_cards` | Thẻ đáp án gắn 1-1 với đề thi. |

### Các trường quan trọng của `QuestionCard`

| Trường | Ý nghĩa |
| --- | --- |
| `code` | Mã hiển thị dạng `Q-0001`, **duy nhất trong tổ chức**. Sinh bằng cách quét mọi mã `Q-%` rồi lấy max + 1 (`_next_question_code`). |
| `folder_id` | Thư mục. `NULL` = "chưa phân loại". |
| `subject` / `grade` / `topic` | Bị đồng bộ theo thư mục nếu có thư mục (`topic` = **tên thư mục**). |
| `question_type` | 1 trong 9 loại (xem §6). |
| `cognitive_level` | `nhan_biet`, `thong_hieu`, `van_dung`, `phan_tich`, `danh_gia`, `sang_tao`. |
| `difficulty` | 1–5. Nhãn: Rất dễ / Dễ / Trung bình / Khó / Rất khó. |
| `status` | `new`, `in_review`, `approved`, `rejected` — **chỉ 4 trạng thái**. |
| `score`, `estimated_time_seconds` | Điểm và thời gian dự kiến, dùng để tính tổng cho giỏ/bộ/đề. |
| `content_json` | Nội dung câu hỏi, **hình dạng phụ thuộc `question_type`** (xem §6). |
| `metadata_json` | Nguồn, thông tin AI đã sinh, citation… (xem §7). |
| `tags` | Mảng chuỗi, tự khử trùng lặp và trim. |
| `source_document_id` | Tài liệu gốc nếu câu hỏi sinh từ tài liệu. |
| `source_card_id` | Câu gốc nếu là bản nhân bản. |
| `review_reasons`, `quality_flags` | Lý do cần duyệt và cờ chất lượng (một phần **tự suy ra**, xem §8). |
| `review_priority`, `assigned_reviewer_id`, `due_at` | Quản trị hàng đợi duyệt. |
| `deleted_at` / `restored_at` / `purged_at` | Thùng rác 3 mức: xoá mềm → khôi phục → xoá vĩnh viễn. |

**Lưu ý về `purged_at`**: câu đã purge không bao giờ xuất hiện lại ở bất kỳ truy vấn nào,
kể cả thùng rác — nhưng bản ghi vẫn nằm trong DB (không xoá cứng).

---

## 3. Hệ phân loại: Môn → Lớp → Thư mục

File: [backend/services/api/src/bookforge_api/question_taxonomy.py](backend/services/api/src/bookforge_api/question_taxonomy.py)

Đây là danh mục **cứng trong code**, không phải bảng DB. Cấu trúc 3 cấp:

- **Cấp học**: `cap_1` (lớp 1–5), `cap_2` (lớp 6–9), `cap_3` (lớp 10–12).
- **Lớp**: chuỗi số trần `"1"`…`"12"`. Nhãn "Lớp N" được render ở tầng taxonomy.
- **Môn**: danh sách riêng cho từng cấp, **cascading** — một môn chỉ hợp lệ với các lớp thuộc cấp của nó.

Ví dụ: `Tự nhiên và Xã hội` chỉ có ở cấp 1; `Hóa học` chỉ có từ cấp 2 trở lên;
`Giáo dục kinh tế và pháp luật` chỉ có ở cấp 3.

Hệ quả: **tạo thư mục với cặp môn–lớp sai sẽ bị từ chối** (422). Thư mục có cặp môn–lớp
không hợp lệ (do dữ liệu cũ) sẽ rơi vào nhánh `uncategorized` của cây thư mục.

FE lấy danh mục này qua `GET /api/question-folders/taxonomy`, trả về `caps`, `grades`,
`subjects_by_cap` — đủ để dựng dropdown cascading mà không hard-code lại phía FE.

Cây thư mục (`GET /api/question-folders/tree`) trả về cấu trúc:

```
Môn (subject)
 └── Lớp (grade)
      └── Thư mục (folder)  ← đây là "chủ đề"
```

Kèm `card_count` ở mọi cấp và một nhánh `uncategorized`.

---

## 4. Thư mục câu hỏi

### Tạo thư mục

`POST /api/question-folders`

```json
{
  "name": "Chương 1 — Cân bằng hóa học",
  "description": "Câu hỏi ôn tập chương 1",
  "subject": "Hóa học",
  "grade": "11",
  "color": "#3B82F6",
  "visibility": "private",
  "question_add_policy": "owner_only",
  "tags": ["hk1", "on-tap"]
}
```

- `subject` và `grade` là **bắt buộc** và phải là cặp hợp lệ theo taxonomy.
- `color` phải khớp `^#[0-9A-Fa-f]{6}$`, được chuẩn hoá thành CHỮ HOA.
- Request dùng `extra='forbid'` — gửi thừa trường sẽ bị 422.
- **Không có `parent_id` trong request tạo**: model DB hỗ trợ thư mục lồng nhau, nhưng API
  hiện chưa mở đường tạo thư mục con. Trên thực tế thư mục là danh sách phẳng, nhóm theo
  môn/lớp bằng chính hai trường đó.

### Quyền trên thư mục

Hai trục quyền độc lập
([question_bank_access.py](backend/services/api/src/bookforge_api/services/question_bank_access.py)):

| Trục | Giá trị | Ý nghĩa |
| --- | --- | --- |
| `visibility` | `private` | Chỉ chủ sở hữu + admin nhìn thấy. |
| | `organization` | Mọi thành viên tổ chức nhìn thấy. |
| `question_add_policy` | `owner_only` | Chỉ chủ sở hữu + admin được thêm câu vào. |
| | `organization_members` | Mọi thành viên được thêm câu vào. |

Quyền trên **câu hỏi**:

- **Xem**: bất kỳ ai trong tổ chức (`get_card_for_view`).
- **Sửa/xoá/duyệt**: chủ sở hữu câu hỏi hoặc admin (`get_card_for_management`).
  Người khác nhận `question_card_not_found` — cố tình trả 404 thay vì 403 để không lộ sự tồn tại.

### Sửa và xoá thư mục

- `PATCH` cho phép đổi `subject`/`grade`, có kiểm tra lại taxonomy.
- **Gỡ tag khỏi thư mục có tác dụng phụ**: nếu một tag bị gỡ và **không còn thư mục nào**
  trong tổ chức cung cấp tag đó, tag sẽ bị gỡ khỏi mọi câu hỏi đang mang nó. Số câu bị ảnh
  hưởng được ghi vào audit event.
- `DELETE` chỉ xoá được thư mục **rỗng** (không có thư mục con và không có câu hỏi chưa xoá),
  ngược lại trả `question_folder_not_empty`.

---

## 5. Năm cách tạo câu hỏi

### 5.1 Tạo tay — `POST /api/question-cards`

Đường cơ bản nhất, dùng bởi cả modal tạo nhanh lẫn màn hình notebook.

```json
{
  "folder_id": "f-uuid",
  "question_type": "multiple_choice",
  "cognitive_level": "thong_hieu",
  "difficulty": 3,
  "score": 0.25,
  "estimated_time_seconds": 90,
  "tags": ["chuong-1"],
  "content_json": {
    "stem": "Chất nào sau đây là chất điện li mạnh?",
    "options": [
      { "key": "A", "text": "\\(\\mathrm{NaCl}\\)", "is_correct": true },
      { "key": "B", "text": "\\(\\mathrm{CH_3COOH}\\)", "is_correct": false },
      { "key": "C", "text": "\\(\\mathrm{H_2O}\\)", "is_correct": false },
      { "key": "D", "text": "\\(\\mathrm{C_2H_5OH}\\)", "is_correct": false }
    ],
    "explanation": "NaCl phân li hoàn toàn trong nước."
  },
  "metadata_json": {},
  "source_document_id": null
}
```

Điều xảy ra ở backend (`create_card`):

1. Nếu có `folder_id` → kiểm tra quyền thêm câu vào thư mục đó.
2. `content_json` được validate theo `question_type` (§7).
3. `tags` được trim + khử trùng lặp.
4. Nếu có thư mục → **ghi đè** `subject`, `grade`, `topic` bằng dữ liệu thư mục.
5. Cấp `code` `Q-XXXX`, gán `owner_user_id` = người tạo, `organization_id` = tổ chức người tạo.
6. Ghi audit event `question_card_created`.

`status` mặc định là `new` — tức là đã nằm sẵn trong hàng đợi duyệt.

### 5.2 AI sinh hàng loạt — `POST /api/question-cards/generate`

Màn hình: drawer "Tạo câu hỏi hàng loạt"
([MassQuestionGenerateDrawer.tsx](frontend/src/templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.tsx)).

```json
{
  "folder_id": "f-uuid",
  "subject": "Hóa học",
  "grade": "11",
  "topic": "Cân bằng hóa học",
  "question_type": "multiple_choice",
  "num_questions": 5,
  "cognitive_level": "van_dung",
  "difficulty": 3,
  "hint": "Ưu tiên bài toán tính hằng số cân bằng",
  "source_text": "…ngữ liệu dán vào, tối đa 20.000 ký tự…",
  "source_label": "SGK Hóa 11 — bài 5",
  "expert_agent_id": null
}
```

Ràng buộc:

- `folder_id` **bắt buộc** (khác với tạo tay).
- `question_type` chỉ nhận **4 loại**: `multiple_choice`, `true_false`, `short_answer`, `essay`.
- `num_questions`: 1–100 ở mức schema, nhưng **trần thật là theo gói** (`max_question_set_questions`).
  Vượt gói → 400 `quota_request_too_large`, không phải 422.
- **Hai nguồn grounding loại trừ nhau**: `expert_agent_id` (lấy ngữ liệu từ corpus của Expert Agent)
  hoặc `source_text` (dán tay). Gửi cả hai → 422.

Thứ tự kiểm tra ở route (`api/question_cards.py:generate`) — cố ý để mọi check rẻ chạy trước
khi tốn token: quota (429) → giới hạn số câu theo gói (400) → quyền thư mục (404) → mới gọi model.

Điều xảy ra tiếp
([question_cards_ai.py](backend/services/api/src/bookforge_api/services/question_cards_ai.py)):

1. Dựng agent PydanticAI với `output_type = { cards: list[PayloadModel] }` — **chính model mà
   API dùng để validate**, nên LLM không thể trả về hình dạng API từ chối.
2. Cài **output validator LaTeX**: nếu phát hiện công thức thô (`x^2`, `log_2(x)`, `<sub>`,
   `y = 2x - 1`, `(x^2-4)/(x-2)`, `H2O -> …`) nằm ngoài vùng LaTeX, model bị bắt viết lại toàn bộ.
3. Cho phép **2 lượt tự sửa** (`OUTPUT_REPAIR_PASSES = 2`). Batch validate **nguyên khối** —
   một câu hỏng làm hỏng cả lô, đây là chủ ý: trả 4/5 câu bị coi là sản phẩm tệ hơn là thử lại sạch.
4. Mỗi payload trả về được đưa qua `create_card` như câu tạo tay, kèm
   `metadata_json.generated_by = { provider, model, operation, at }`.
5. Nếu có grounding → thêm `metadata_json.citation`, việc này **tắt cờ `missing_source`**.
6. Ghi `AIAction` với token usage, `source='question_bank'`.

Toàn bộ chạy trong một transaction: sinh xong mới commit.

Lỗi thường gặp: `editor_assistant_unavailable` (chưa cấu hình model cho operation `question_bank`),
`editor_assistant_failed` (502 — provider lỗi hoặc model không sửa nổi payload sau 2 lượt).

### 5.3 AI đổi loại câu hỏi — `POST /api/question-cards/convert`

```json
{ "card_ids": ["c1", "c2"], "target_type": "true_false" }
```

- Tối đa 100 câu/lần, `target_type` cũng chỉ 4 loại sinh được (`visual` bị loại — AI không
  thể bịa ra `visual_asset_key`).
- Khác `/generate` ở chỗ **lỗi từng câu là `skipped`, không phải lỗi cả request**. Response
  trả `{ converted: [...], skipped: [{id, reason}] }`.
- Câu nguồn quá dài (> 20.000 ký tự payload) bị skip chứ **không bị cắt ngắn**.
- Metadata của câu mới chỉ mang theo đúng 4 khóa nguồn (`source_document_id`, `citation`,
  `citations`, `sources`) — để câu grounded vẫn grounded. `generated_by` được ghi mới với
  `mode: 'convert'`, và thêm `converted_from: { card_id, code, question_type }`.

### 5.4 Nhân bản — `POST /api/question-cards/{id}/duplicate`

Copy sâu `content_json`, `metadata_json`, `tags`; giữ nguyên thư mục/môn/lớp/loại/mức;
**reset `status` về `new`**, `version` về 1, gán `source_card_id` trỏ về câu gốc, cấp mã mới.

### 5.5 Nhập từ Excel (offline)

Dành cho việc thu thập câu hỏi từ chuyên gia bên ngoài.

- Script sinh workbook: [backend/scripts/build_qb_intake_template.py](backend/scripts/build_qb_intake_template.py)
- Hướng dẫn cho giáo viên: [backend/docs/product/huong-dan-chuan-bi-ngan-hang-cau-hoi.md](backend/docs/product/huong-dan-chuan-bi-ngan-hang-cau-hoi.md)
- File mẫu đã sinh: `backend/docs/product/BookForge-Ngan-hang-cau-hoi-Hoa-hoc-thay-Kien.xlsx`

Workbook có 6 sheet (Hướng dẫn / Danh mục bài / Câu hỏi / Lỗi sai phổ biến / Ví dụ / Danh mục chọn)
và **3 tầng cột phân biệt bằng màu** — màu chính là chỉ dẫn:

| Màu | Tầng | Ý nghĩa |
| --- | --- | --- |
| Đỏ `C00000` | BẮT BUỘC | Thiếu là không nhập được. |
| Xanh đậm `1F4E79` | NÊN CÓ | Cố gắng điền cho mọi câu. |
| Xanh lá `375623` | CÂU VÀNG | Phần giá trị nhất — phân tích, lỗi sai phổ biến. |

Bốn dạng câu trong template bám cấu trúc thi THPT 2025: Trắc nghiệm 4 lựa chọn,
Đúng/Sai 4 ý, Trả lời ngắn, Tự luận.

### 5.6 Màn hình Notebook — nhập nhanh nhiều câu

[QuestionImportNotebookPage.tsx](frontend/src/templates/QuestionBankPage/components/import-notebook/QuestionImportNotebookPage.tsx)
(`/question-bank/import`) là UI dạng "sổ tay" nhiều ô: mỗi ô là một câu, có trạng thái riêng
(`draft` / `dirty` / `saving` / `saved` / `error`). Nó không phải một API riêng — bên dưới vẫn
gọi `APICreateQuestionCard` / `APIUpdateQuestionCard` / `APIGenerateQuestionCards` /
`APIUploadQuestionCardImage`.

---

## 6. Cấu trúc `content_json` theo từng loại câu hỏi

File: [backend/services/api/src/bookforge_api/schemas/question_bank.py](backend/services/api/src/bookforge_api/schemas/question_bank.py) (dòng 39–136)

**Trường chung** (`BaseCardPayload`) — mọi loại đều có:

| Trường | Bắt buộc | Ghi chú |
| --- | --- | --- |
| `stem` | ✅ | Đề bài. Tối thiểu 1 ký tự. |
| `explanation` | — | Lời giải / giải thích. Thiếu → cờ `missing_explanation`. |
| `hint` | — | Gợi ý. |

> `model_config = ConfigDict(extra='allow')` — payload câu hỏi **cho phép trường lạ**. Đây là
> chủ ý (để chứa dữ liệu mở rộng), nhưng nghĩa là gõ sai tên trường sẽ **không báo lỗi**,
> dữ liệu lặng lẽ nằm lại trong `content_json`.

### Bảng 9 loại

| `question_type` | Nhãn | Validate chặt? | AI sinh được? |
| --- | --- | --- | --- |
| `multiple_choice` | Trắc nghiệm | ✅ | ✅ |
| `true_false` | Đúng / Sai | ✅ | ✅ |
| `short_answer` | Trả lời ngắn | ✅ | ✅ |
| `essay` | Tự luận | ✅ | ✅ |
| `visual` | Hình ảnh / Biểu đồ | ✅ | ❌ |
| `fill_blank` | Điền khuyết | ❌ | ❌ |
| `matching` | Ghép đôi | ❌ | ❌ |
| `ordering` | Sắp xếp | ❌ | ❌ |
| `passage` | Đọc hiểu | ❌ | ❌ |

**"Validate chặt"** = có mặt trong `PAYLOAD_MODELS`
([services/question_cards.py:104](backend/services/api/src/bookforge_api/services/question_cards.py#L104)).
Bốn loại còn lại rơi về `BaseCardPayload` — nghĩa là **chỉ `stem` được kiểm tra**, phần còn
lại lọt thẳng vào DB không ai soát. Schema Pydantic của chúng (`FillBlankPayload`, …) **có tồn tại**
nhưng hiện chỉ được dùng bởi bộ mapper Cohota, không dùng khi tạo/sửa câu.

### 6.1 `multiple_choice` — Trắc nghiệm

```json
{
  "stem": "Chất nào sau đây là chất điện li mạnh?",
  "options": [
    { "key": "A", "text": "NaCl", "is_correct": true,  "rationale": "Phân li hoàn toàn" },
    { "key": "B", "text": "CH3COOH", "is_correct": false, "rationale": "Điện li yếu" }
  ],
  "explanation": "…",
  "hint": "…"
}
```

Ràng buộc: `options` ≥ 2 phần tử, và **ít nhất một phương án `is_correct: true`**
(cho phép nhiều đáp án đúng).

### 6.2 `true_false` — Đúng / Sai nhiều ý

```json
{
  "stem": "Xét các phát biểu về cân bằng hóa học:",
  "lead_in": "Mỗi ý sau đây đúng hay sai?",
  "statements": [
    { "text": "Tăng nhiệt độ luôn làm cân bằng chuyển dịch theo chiều thuận",
      "is_true": false, "explanation": "Phụ thuộc chiều thu/toả nhiệt" },
    { "text": "Chất xúc tác không làm chuyển dịch cân bằng", "is_true": true }
  ]
}
```

Ràng buộc: `statements` ≥ 1. Đây là dạng "Đúng/Sai 4 ý" theo cấu trúc thi THPT 2025.

### 6.3 `short_answer` — Trả lời ngắn

```json
{
  "stem": "Tính pH của dung dịch HCl 0,01M.",
  "answer": "2",
  "accepted_variants": ["2,0", "2.0"],
  "case_sensitive": false,
  "unit_required": false,
  "explanation": "…"
}
```

### 6.4 `essay` — Tự luận

```json
{
  "stem": "Trình bày ảnh hưởng của nhiệt độ tới tốc độ phản ứng.",
  "length": "long",
  "rubric": [
    "Nêu đúng quan hệ nhiệt độ – tốc độ (1đ)",
    "Giải thích theo thuyết va chạm (1đ)"
  ],
  "reference_answer": "…",
  "max_score": 2.0
}
```

`length` ∈ `{"short", "long"}` (mặc định `short`). `max_score` ≥ 0.

### 6.5 `visual` — Câu hỏi có hình

```json
{
  "stem": "Quan sát đồ thị và cho biết…",
  "visual_asset_key": "question-cards/assets/images/…",
  "answer": "…"
}
```

`visual_asset_key` **bắt buộc**. Ảnh được upload trước qua
`POST /api/question-cards/assets/images` (≤ 5MB, png/jpg/webp), trả về `storage_key` để điền vào đây.

### 6.6 Bốn loại chưa validate chặt

Hình dạng *dự kiến* (theo schema có sẵn) — nhưng nhắc lại: hiện backend **không ép** khi tạo câu.

```jsonc
// fill_blank
{ "stem": "…___… ", "blanks": [{ "id": "b1", "answer": "oxi", "accepted_variants": ["O2"] }] }

// matching
{ "stem": "Ghép chất với tính chất", "pairs": [{ "id": "p1", "left": "NaCl", "right": "Điện li mạnh" }] }

// ordering  (≥2 mục, `order` phải duy nhất)
{ "stem": "Sắp xếp các bước", "items": [{ "id": "i1", "text": "Cân hoá chất", "order": 1 }] }

// passage
{ "stem": "Theo đoạn văn, …", "passage": "…toàn văn ngữ liệu…", "answer": "…" }
```

---

## 7. Quy tắc kiểm tra dữ liệu và các cạm bẫy

### Ba tầng validate khác nhau

| Tầng | Cấu hình | Hành vi khi gửi trường lạ |
| --- | --- | --- |
| Request bao ngoài (`QuestionCardCreateRequest`) | `extra='forbid'` | **422** |
| Payload nội dung (`content_json`) | `extra='allow'` | Chấp nhận, lưu nguyên |
| Request thư mục | `extra='forbid'` | **422** |

Payload sai hình dạng → `ApiException(ErrorCode.question_card_invalid_payload)`.

### Những hành vi dễ gây bất ngờ

1. **Thư mục ghi đè môn/lớp/chủ đề.** Bạn gửi `subject: "Toán"` nhưng `folder_id` trỏ tới
   thư mục Hóa 11 → câu hỏi sẽ là Hóa 11, `topic` = tên thư mục. Điều này áp dụng cả khi
   `PATCH` (kể cả khi bạn không đụng tới `folder_id`).
2. **Đổi `question_type` bằng `PATCH` sẽ validate lại `content_json` theo loại mới.** Nếu
   không gửi kèm `content_json` mới, nội dung cũ bị đem đi validate theo hình dạng mới → dễ 422.
3. **`code` sinh bằng cách quét toàn bộ mã của tổ chức.** Không phải sequence — hai request
   tạo đồng thời về lý thuyết có thể tranh mã (được chặn bởi unique index `org + code`).
4. **Tìm kiếm `q` chạy trong Python, không trong SQL.** `list_cards` khi có `q` sẽ **tải toàn
   bộ** câu hỏi khớp filter rồi lọc và phân trang trong bộ nhớ. Nhanh khi ngân hàng nhỏ,
   là điểm cần theo dõi khi ngân hàng lớn.
5. **Lọc `tag` dùng `LIKE '%"tag"%'` trên JSON đã cast sang chuỗi** — hoạt động, nhưng khớp
   theo chuỗi con có dấu nháy, không phải truy vấn JSON thật.

### `metadata_json` — những khóa có ý nghĩa

Không phải blob tuỳ ý; một số khóa **thay đổi hành vi hệ thống**:

| Khóa | Tác dụng |
| --- | --- |
| `citation` / `citations` / `sources` / `source_document_id` | Bất kỳ khóa nào có mặt → coi như câu **có nguồn**, tắt cờ `missing_source`. |
| `generated_by` | `{ provider, model, operation, at }` — dấu vết AI đã sinh. |
| `converted_from` | `{ card_id, code, question_type }` — vết đổi loại. |
| `duplicate_candidate` / `duplicate_group_id` | Bật cờ `possible_duplicate`. |
| `low_confidence` | Bật cờ `low_confidence`. |

### Quy tắc LaTeX

Áp dụng cho **nội dung AI sinh** (validator ở tầng agent):

- Inline: `\(...\)` hoặc `$...$`
- Display: `\[...\]` hoặc `$$...$$`
- **Cấm**: thẻ HTML `<sub>`, `<sup>`, `<math>`…; công thức thô như `x^2`, `log_2(x)`,
  `lim(x->2)`, `y = 2x - 1`, `(x^2 - 4)/(x - 2)`, `H2 -> H2O`, `mol/L` viết trần.

Câu tạo tay **không** bị validator này chặn, nhưng FE render bằng
[LatexText.tsx](frontend/src/templates/QuestionBankPage/components/common/LatexText.tsx),
nên viết đúng LaTeX vẫn là điều kiện để hiển thị đẹp.

---

## 8. Vòng đời và quy trình duyệt

### 8.1 Bốn trạng thái

```
        tạo mới / nhân bản / AI sinh
                    │
                    ▼
                 [new] ──── gán người duyệt ────► [in_review]
                    │                                  │
                    │            ┌─────────────────────┤
                    │            ▼                     ▼
                    │       [approved]            [rejected]
                    │            ▲                     │
                    └────────────┴─── needs_fix ───────┘
                          (quay về [new])
```

`decision` → `status` (`REVIEW_FINAL_STATUS_BY_DECISION`):

| Quyết định | Trạng thái kết quả | Yêu cầu bắt buộc |
| --- | --- | --- |
| `approved` | `approved` | — (và **xoá sạch `quality_flags`**) |
| `needs_fix` | **`new`** | `reasons` ≥ 1, `note` ≥ 10 ký tự, `fix_actions` ≥ 1 |
| `rejected` | `rejected` | `note` bắt buộc |

Với `needs_fix`, `quality_flags` được hợp nhất: cờ tự suy ∪ `fix_actions` ∪ `{needs_fix}`.

> **Điểm đáng lưu ý**: gộp về 4 trạng thái nghĩa là **không còn cách phân biệt câu do AI tạo
> với câu do người viết bằng `status`**. Dấu vết duy nhất là `metadata_json.generated_by`
> (hàm `_is_ai_generated` đọc đúng chỗ này).

### 8.2 Cờ chất lượng tự suy (`infer_quality_flags`)

Chạy mỗi lần serialize câu hỏi — **không lưu tĩnh**, nên luôn phản ánh dữ liệu hiện tại:

| Cờ | Điều kiện |
| --- | --- |
| `missing_source` | Không có `source_document_id` và không có khóa nguồn nào trong metadata. |
| `missing_explanation` | `content_json.explanation` rỗng. |
| `answer_uncertain` | Không tìm thấy đáp án: MC không có phương án đúng; T/F không có `statements`; loại khác không có `answer` / `reference_answer` / `rubric`. |
| `possible_duplicate` | metadata có `duplicate_candidate` hoặc `duplicate_group_id`. |
| `low_confidence` | metadata có `low_confidence`. |

`infer_review_reasons` ánh xạ các cờ trên thành lý do cần duyệt; nếu không có lý do nào,
mặc định là `manual_review` (hiển thị "AI Generated" trên UI).

### 8.3 Hàng đợi duyệt

`GET /api/question-cards/review-queue` — chỉ lấy câu ở `new`, `in_review`, `rejected`
(`REVIEW_LIST_STATUSES`). Sắp xếp theo `review_priority` giảm dần, rồi `updated_at`.

Lọc được theo: `folder_id`, `subject`, `grade`, `question_type`, `cognitive_level`,
`status`, `priority`, `assigned_reviewer_id`, `q`.

Các thao tác trên một câu:

| Endpoint | Việc |
| --- | --- |
| `POST /{id}/assign` | Gán người duyệt. Nếu câu đang `new` → **tự chuyển sang `in_review`**. Người duyệt phải là user `role='user'`, đang active, cùng tổ chức. |
| `POST /{id}/priority` | Đặt `low`/`medium`/`high`/`urgent` + `due_at`. |
| `POST /{id}/approve` | Duyệt. |
| `POST /{id}/reject` | Từ chối, `note` bắt buộc. |
| `POST /{id}/request-changes` | Yêu cầu sửa (`needs_fix`). |

Hàng loạt: `POST /bulk/review` (≤ 500 id, cùng ràng buộc về note/reasons/fix_actions),
`POST /bulk/approve`, `POST /quality-check` (chạy lại bộ suy cờ cho tối đa 500 câu).

### 8.4 Phiên duyệt (Review Session)

Dùng khi cần duyệt liên tục một lô câu và theo dõi tiến độ.

- `POST /review-sessions` — tạo phiên từ ≤ 200 id, tiêu đề tự sinh nếu không truyền.
- `POST /review-sessions/{id}/items` — thêm câu vào phiên đang chạy.
- `GET /review-sessions/{id}/items/{card_id}` — lấy chi tiết một câu **kèm `sources`**
  (tài liệu gốc / câu gốc) để người duyệt đối chiếu.
- `POST /review-sessions/{id}/items/{card_id}/decision` — quyết định. **Chỉ `approved` /
  `rejected`** ở cấp phiên (không có `needs_fix`); `rejected` bắt buộc có `note`.
- `POST /review-sessions/{id}/bulk-decision`, `POST /review-sessions/{id}/complete`.

Trạng thái phiên: `active`, `paused`, `completed`, `cancelled`. Tiến độ (`reviewed_count`,
`pending_count`, `progress_percent`) được tính lại sau mỗi quyết định.

---

## 9. Tìm kiếm, lọc, thao tác hàng loạt

### Lọc danh sách câu hỏi — `GET /api/question-cards`

| Tham số | Ghi chú |
| --- | --- |
| `folder_id` | Truyền `"none"` để lấy câu **chưa phân thư mục**. |
| `subject`, `grade`, `topic`, `question_type`, `cognitive_level`, `difficulty`, `status` | So khớp tuyệt đối. |
| `tag`, `source_document_id`, `owner_user_id` | |
| `q` | Tìm toàn văn (lọc trong bộ nhớ, xem §7). |
| `sort` | `-updated_at` (mặc định), `updated_at`, `-created_at`, `created_at`, `difficulty`, `-difficulty`. Giá trị lạ tự rơi về `updated_at`. |
| `page`, `page_size` | `page_size` ≤ 100. |

`GET /api/question-cards/filter-options` trả sẵn danh sách giá trị + **số lượng** cho từng
bộ lọc, để FE không phải tự đếm.

### Thao tác hàng loạt — `POST /api/question-cards/bulk`

```json
{ "ids": ["c1","c2"], "action": "move", "params": { "folder_id": "f-uuid" } }
```

Actions: `move`, `set_status`, `add_tags`, `remove_tags`, `delete`, `assign_reviewer`.
Tối đa 500 id. Response luôn tách `succeeded` và `skipped: [{id, reason}]` — thao tác hàng loạt
**không bao giờ thất bại toàn bộ vì một câu**.

`PATCH /api/question-cards/bulk-update` khác ở chỗ cho phép **mỗi câu một bộ thay đổi riêng**
(≤ 100 câu), mỗi mục bắt buộc có ít nhất một trường thay đổi.

### Phát hiện trùng — `POST /api/question-cards/check-duplicates`

Nhóm câu theo `stem` đã chuẩn hoá (lowercase + gộp khoảng trắng). Không truyền `ids` thì
quét toàn bộ. Trả về các nhóm ≥ 2 câu cùng đề.

---

## 10. Thùng rác

Ba mức, ba mốc thời gian:

| Hành động | Endpoint | Hiệu ứng |
| --- | --- | --- |
| Xoá mềm | `DELETE /api/question-cards/{id}` | Đặt `deleted_at`, xoá `restored_at`. |
| Khôi phục | `POST /{id}/restore` | Xoá `deleted_at`, đặt `restored_at`. **Đồng thời khôi phục mọi thư mục cha đã bị xoá** (đi ngược `parent_id`, có chống lặp vô hạn). |
| Xoá vĩnh viễn | `POST /{id}/purge` | Đặt `purged_at`. Biến mất khỏi mọi truy vấn, kể cả thùng rác. |

`GET /api/question-cards/trash` liệt kê câu có `deleted_at` **hoặc** `restored_at` — tức là
màn hình thùng rác cũng hiển thị các câu vừa được khôi phục, để người dùng thấy kết quả thao tác.

---

## 11. Từ câu hỏi ra đề thi

### 11.1 Giỏ câu hỏi (Cart)

`/api/question-cart` — **riêng từng user**, không chia sẻ trong tổ chức.

- `POST /items` thêm câu, `POST /reorder` sắp thứ tự, `DELETE /items/{card_id}`, `DELETE` xoá sạch.
- `POST /bulk` với action `remove` / `set_status` / `add_tags` / `remove_tags` / `keep_approved`.
- `POST /keep-approved` — giữ lại chỉ câu đã duyệt.
- Response luôn kèm **`summary`** (tổng số, phân bố theo loại / mức nhận thức / trạng thái,
  tổng điểm ước tính, tổng thời gian ước tính, số câu thiếu nguồn…) và **`warnings`**
  (mã cảnh báo, mức độ `info`/`warning`/`error`, danh sách `card_ids`, gợi ý hành động).

### 11.2 Bộ câu hỏi (Collection)

Tạo trực tiếp (`POST /api/question-collections`) hoặc từ giỏ (`POST /api/question-cart/collections`,
có tuỳ chọn `only_approved`).

Trường đáng chú ý trong response:

- `readiness_status`: `ready` khi **mọi câu còn sống trong bộ đều `approved`**, ngược lại `not_ready`.
- `item_count`, `part_count`, `usage_count`, `estimated_total_score`, `estimated_time_seconds`,
  `question_type_counts`, `subjects`, `grades`, `cognitive_levels`.

`duration_minutes`: 1–300.

### 11.3 Đề thi (Test Paper)

`POST /api/test-papers` — phải truyền **đúng một trong hai**: `collection_id` **hoặc** `card_ids`.

- Nếu dựng từ collection và collection **chưa `ready`** → lỗi `question_collection_not_ready`.
- Mỗi câu được **snapshot** vào `test_paper_items.snapshot_json` — sửa câu gốc sau đó
  không làm đề đổi theo (muốn cập nhật thì gọi `POST /{id}/refresh-from-source`).

`settings_json` được validate mềm nhưng có ràng buộc thật:

| Khóa | Kiểu / giới hạn |
| --- | --- |
| `show_score`, `essay_new_page`, `include_answer_card` | boolean |
| `answer_space_lines` | số nguyên 1–30 |
| `test_date` | chuỗi `YYYY-MM-DD` |
| `term`, `school_name`, `subject`, `grade`, `paper_code`, `instructions` | ≤ 255 ký tự |

Các thao tác khác: thêm/xoá/sắp xếp câu, gán tiêu đề phần (`/items/section`),
`GET /{id}/matrix-check` (đối chiếu ma trận đề), `GET /{id}/canvas-sync-status`,
`POST /{id}/canvas/regenerate`.

### 11.4 Thẻ đáp án và mã đề

- **Answer Card**: 1-1 với đề thi. `GET /{id}/answer-card`, `POST /{id}/answer-card/refresh`,
  `POST /{id}/answer-card/sync` với `mode` ∈ `update_existing` / `create_new_version` / `keep_existing`.
- **Variants (mã đề)**: `POST /{id}/variants` với `paper_codes` (≤ 50, không trùng, không rỗng),
  `shuffle_questions`, `shuffle_options`, `seed`. Mỗi mã đề sinh ra Canvas document riêng cho
  cả đề lẫn đáp án — trộn theo seed nên tái lập được.

Đề thi và thẻ đáp án đều đổ ra **Canvas document**, tức là dùng chung đường xuất DOCX/PDF
với phần soạn thảo tài liệu.

---

## 12. Đẩy sang Cohota

Tích hợp xuất câu hỏi sang hệ LMS Cohota:

- `POST /api/question-cards/{id}/cohota` — đẩy một câu.
- `POST /api/question-collections/{id}/cohota` — đẩy cả bộ, response tách rõ
  `pushed_count` / `failed_count` / `skipped_count` và kết quả từng câu.

Bộ mapper ([integrations/cohota_mapper.py](backend/services/api/src/bookforge_api/integrations/cohota_mapper.py))
chuẩn hoá nội dung sang định dạng Cohota — và **luôn làm việc trên bản copy sâu**, không bao giờ
sửa dữ liệu BookForge. Nó là nơi duy nhất hiện đang dùng schema của 4 loại câu chưa validate chặt
(fill_blank / matching / ordering / passage), nên nó phải tự vá dữ liệu thiếu (ví dụ tự dựng
`blanks` từ `answer` nếu câu điền khuyết không có mảng `blanks`).

Câu không map được → `CohotaMappingError`, tính là `failed`, không làm hỏng cả lô.

---

## 13. Quota và chi phí AI

Mọi thao tác AI trong ngân hàng câu hỏi đều đi qua hệ quota chung:

1. `require_ai_action` — chặn sớm nếu hết lượt (429).
2. `validate_question_set_request` — trần số câu theo gói (`max_question_set_questions`,
   trần hạ tầng 100) → 400 `quota_request_too_large`.
3. `provider_max_output_tokens` — tính ngân sách token đầu ra từ gói và độ dài input ước tính
   (`len(source_text)/4 + 256`). Ngân sách cơ sở: **4096** cho `/generate`, **2048** cho `/convert`.
4. `record_ai_action` — ghi lại provider, model, token usage, `source='question_bank'`,
   `action_type='question_set_generation'`. **Ghi cả khi thất bại** (status `failed`) để còn
   truy vết được.
5. `stamp_post_task_headers` — trả về header quota còn lại sau thao tác.

Operation dùng để chọn model: `question_bank` (xem `model_router`).

---

## 14. Bản đồ màn hình FE ↔ API ↔ file code

Router: [frontend/src/App.tsx](frontend/src/App.tsx) (dòng 71–103).
Toàn bộ template: [frontend/src/templates/QuestionBankPage/](frontend/src/templates/QuestionBankPage/)

| Route | Màn hình | File | API chính |
| --- | --- | --- | --- |
| `/question-bank` | Tổng quan / dashboard | `components/overview/OverviewScreen.tsx` | `GET /question-cards/dashboard` |
| `/question-bank/folders` | Danh sách thư mục + cây | `components/folder-list/FolderListScreen.tsx` | `GET /question-folders/tree`, `/question-folders` |
| (trong folder) | Danh sách câu hỏi dạng thẻ | `components/cards/CardsPage.tsx`, `QuestionList.tsx` | `GET /question-cards` |
| `/question-bank/editor/:cardId` | Trình soạn câu hỏi | `components/editor/QuestionCardEditorPage.tsx` | `PATCH /question-cards/{id}` |
| `/question-bank/import` | Notebook nhập nhiều câu | `components/import-notebook/QuestionImportNotebookPage.tsx` | `POST /question-cards`, `/generate` |
| `/question-bank/review` | Hàng đợi duyệt | `components/review/QuestionReviewQueuePage.tsx` | `GET /question-cards/review-queue` |
| `/question-bank/review/sessions/:id` | Phiên duyệt | `components/review/QuestionReviewSessionPage.tsx` | `/question-cards/review-sessions/*` |
| `/question-bank/sets` | Bộ câu hỏi | `components/sets/QuestionCollectionSetsPage.tsx` | `/question-collections` |
| `/question-bank/exams` | Đề thi | `components/exams/QuestionTestPapersPage.tsx` | `/test-papers` |
| `/question-bank/trash` | Thùng rác | `components/trash/QuestionTrashPage.tsx` | `GET /question-cards/trash` |

Các thành phần dùng chung đáng chú ý:

- `components/mass-generate/MassQuestionGenerateDrawer.tsx` + `mass-generate-payload.ts` —
  dựng payload `/generate`, **tự thực thi quy tắc loại trừ hai nguồn grounding** ở phía FE
  (expert corpus thắng, xoá `source_text`).
- `components/quick-edit/QuickQuestionEditDrawer.tsx` — sửa nhanh không rời danh sách.
- `components/detail/QuestionDetailFigmaDrawer.tsx` — xem chi tiết câu hỏi.
- `components/cart/QuestionCartDrawer.tsx` — giỏ câu hỏi.
- `components/common/LatexText.tsx`, `QuestionRichTextInput.tsx` — render/nhập nội dung có LaTeX.
- `question-bank-shared.ts`, `question-folder-taxonomy.ts`, `question-detail-model.ts` — logic dùng chung.
- `question-bank-taxonomy.contract.json` — **hợp đồng taxonomy giữa FE và BE**, được test hai phía
  (`test_question_bank_taxonomy.py` ở backend, `question-bank-taxonomy.test.ts` ở frontend).

Client API: [frontend/src/api/question-bank-api.ts](frontend/src/api/question-bank-api.ts) —
khoảng 80 hàm `API*`, đặt tên khớp 1-1 với endpoint.

---

## 15. Danh mục API đầy đủ

### Thư mục — `/api/question-folders`

| Method | Path | Việc |
| --- | --- | --- |
| POST | (gốc) | Tạo thư mục |
| GET | (gốc) | Danh sách (có `q`) |
| GET | `/taxonomy` | Danh mục môn/lớp/cấp |
| GET | `/tree` | Cây Môn → Lớp → Thư mục |
| GET/PATCH/DELETE | `/{folder_id}` | Chi tiết / sửa / xoá (chỉ khi rỗng) |

### Câu hỏi — `/api/question-cards`

| Method | Path | Việc |
| --- | --- | --- |
| POST / GET | (gốc) | Tạo / danh sách |
| GET | `/trash` | Thùng rác |
| GET | `/dashboard`, `/review-dashboard` | Thống kê |
| GET | `/review-queue`, `/review-queue/options`, `/reviewers` | Hàng đợi duyệt |
| GET | `/filter-options` | Giá trị + số lượng cho bộ lọc |
| POST | `/generate` | AI sinh hàng loạt |
| POST | `/convert` | AI đổi loại |
| POST | `/quality-check` | Chạy lại bộ suy cờ chất lượng |
| POST | `/check-duplicates` | Phát hiện trùng đề |
| POST | `/bulk`, `/bulk/review`, `/bulk/approve` | Thao tác hàng loạt |
| PATCH | `/bulk-update` | Sửa hàng loạt, mỗi câu một payload |
| POST/GET | `/review-sessions…` | Phiên duyệt (9 endpoint) |
| POST | `/assets/images` | Upload ảnh cho câu hỏi |
| GET/PATCH/DELETE | `/{card_id}` | Chi tiết / sửa / xoá mềm |
| POST | `/{card_id}/duplicate` | Nhân bản |
| POST | `/{card_id}/approve`, `/reject`, `/assign`, `/priority`, `/request-changes` | Duyệt |
| POST | `/{card_id}/restore`, `/purge` | Khôi phục / xoá vĩnh viễn |
| POST | `/{card_id}/cohota` | Đẩy sang Cohota |

### Giỏ — `/api/question-cart`

`GET` (gốc), `GET /summary`, `POST /items`, `POST /reorder`, `POST /bulk`,
`POST /keep-approved`, `POST /collections`, `DELETE /items/{card_id}`, `DELETE` (gốc — xoá sạch giỏ).

### Bộ câu hỏi — `/api/question-collections`

`POST` / `GET` (gốc), `GET/PATCH/DELETE /{id}`, `POST /{id}/items`,
`DELETE /{id}/items/{card_id}`, `POST /{id}/reorder`, `GET /{id}/summary`, `POST /{id}/cohota`.

### Đề thi — `/api/test-papers`

`POST` / `GET` (gốc), `GET /templates`, `GET/PATCH/DELETE /{id}`,
`POST /{id}/items`, `DELETE /{id}/items/{card_id}`, `POST /{id}/items/reorder`,
`POST /{id}/items/section`, `GET /{id}/canvas-sync-status`, `GET /{id}/matrix-check`,
`POST /{id}/canvas/regenerate`, `POST /{id}/refresh-from-source`,
`GET /{id}/answer-card`, `POST /{id}/answer-card/refresh`, `POST /{id}/answer-card/sync`,
`POST/GET /{id}/variants`.

### Mã lỗi riêng của ngân hàng câu hỏi

[backend/services/api/src/bookforge_api/errors/codes.py](backend/services/api/src/bookforge_api/errors/codes.py) (dòng 101–110)

| Mã | Khi nào |
| --- | --- |
| `question_folder_not_found` | Không tồn tại **hoặc không đủ quyền** |
| `question_card_not_found` | Tương tự, cho câu hỏi |
| `question_folder_not_empty` | Xoá thư mục còn câu hỏi / thư mục con |
| `question_folder_cycle` | Vòng lặp cha–con |
| `question_collection_not_ready` | Dựng đề từ bộ chưa duyệt hết |
| `question_card_invalid_payload` | `content_json` sai hình dạng theo loại |
| `question_card_invalid_field` | Trường không hợp lệ |
| `question_review_session_not_found` / `_invalid_state` | Phiên duyệt |
| `question_generation_no_grounding` | Không tìm được ngữ liệu trong corpus của expert |

---

## 16. Những gì chưa có

Để tránh đọc nhầm spec sản phẩm thành hiện trạng:

| Hạng mục | Trạng thái |
| --- | --- |
| 4 loại `fill_blank` / `matching` / `ordering` / `passage` | Lưu được, nhưng **không validate** khi tạo/sửa; AI không sinh được |
| AI sinh loại `visual` | Không — AI không thể bịa `visual_asset_key` |
| JSXGraph (đồ thị động trong câu hỏi) | Chưa; `visual` mới chỉ lưu khóa ảnh tĩnh |
| Thư mục lồng nhau | Model có `parent_id`, API **không mở đường tạo** |
| Phân biệt câu AI vs câu người bằng `status` | Không còn — chỉ còn dấu vết ở `metadata_json.generated_by` |
| "Question Set" như một primitive riêng | Không tồn tại; primitive nhóm câu duy nhất là **Collection** |
| Metadata nhóm E (thống kê sử dụng thực tế) | Chưa xây |
| "Smart Balance" khi dựng bộ đề | Mới là thống kê read-only, chưa tự cân bằng |
| Tìm kiếm toàn văn ở tầng DB | Chưa — lọc trong bộ nhớ (§7) |

---

## Đọc tiếp

| Tài liệu | Dùng khi |
| --- | --- |
| [backend/docs/QUESTION_BANK_API_GUIDE.md](backend/docs/QUESTION_BANK_API_GUIDE.md) | Cần payload mẫu đầy đủ 9 loại + hợp đồng FE |
| [backend/docs/QUESTION_CARD_MOCK_DATA_9_TYPES.json](backend/docs/QUESTION_CARD_MOCK_DATA_9_TYPES.json) | Cần dữ liệu mẫu để test |
| [backend/docs/product/question-bank.md](backend/docs/product/question-bank.md) | Cần hiểu ý đồ sản phẩm và lộ trình |
| [backend/docs/product/huong-dan-chuan-bi-ngan-hang-cau-hoi.md](backend/docs/product/huong-dan-chuan-bi-ngan-hang-cau-hoi.md) | Chuẩn bị workbook cho chuyên gia điền |
| [backend/docs/REVIEW_STANDARDS.md](backend/docs/REVIEW_STANDARDS.md) | Tiêu chuẩn duyệt nội dung |
| `backend/services/api/tests/test_question_bank_*.py` | Muốn xem hành vi thực tế được chốt bằng test |
