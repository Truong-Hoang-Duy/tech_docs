# Phân tích năng lực trích xuất câu hỏi từ tài liệu (Exam Extract / OCR)

> **Mục đích**: đánh giá hiện trạng tính năng "nhập câu hỏi từ đề thi PDF" trước khi bàn phương án code.
> Trả lời 5 câu hỏi nghiên cứu, dựa hoàn toàn trên code đang chạy.
>
> Tài liệu nền: [ngan-hang-cau-hoi-tong-quan.md](tech_docs/ngan-hang-cau-hoi-tong-quan.md)
> Ngày rà soát: 2026-08-19.

---

## 0. Tóm tắt điều hành

| # | Câu hỏi | Kết luận ngắn |
| --- | --- | --- |
| 1 | Hệ thống chỉ OCR ra câu tự luận? | **Đúng.** `question_type='essay'` bị hard-code. Prompt còn cấm model đọc đáp án. |
| 2 | Điều kiện tạo từng loại câu hỏi? | Dữ liệu OCR thu được (`stem`, `parts`, `score`, `figure_ids`) **chỉ đủ cho 1/9 loại**. |
| 3 | AI cần thêm gì? | 4 hạng mục gốc + 3 hạng mục phát sinh từ bài toán scan (§6). |
| 4 | Đầu ra đủ tiêu chí chưa? | **Chưa**, 3 lớp thiếu hụt cộng dồn — và §6 thêm lớp thứ 4 (mất bảng biểu). |
| 5 | PDF scan / ảnh có khả thi? | **Khả thi, và đã chạy sẵn** — pipeline *luôn* raster hoá, không bao giờ đọc lớp text. Nhưng kèm 5 rủi ro riêng, trong đó **1 lỗi mất trắng dữ liệu**. |
| 6 | PDF thường (born-digital) thì sao? | **Đây mới là trường hợp tệ nhất về mặt lãng phí.** Repo đã có sẵn đường xử lý born-digital tốt hơn hẳn — dựng lại LaTeX, đặt đúng vị trí hình, phát hiện bảng — **và luồng extract bỏ qua toàn bộ**. |

**Bốn điều đáng ngạc nhiên nhất tìm thấy trong code:**

1. Pipeline extract **không hề đọc lớp văn bản của PDF** — kể cả khi PDF có sẵn text layer chính xác 100%. Mọi trang đều bị raster hoá thành PNG 200 DPI rồi cho vision model đọc lại.
2. Phần markdown mà Mistral OCR trả về (chứa **bảng biểu** đã được nhận dạng) **bị vứt bỏ hoàn toàn** — chỉ giữ lại ảnh cắt.
3. **Một cửa sổ 2 trang lỗi JSON → mất toàn bộ kết quả của cả file.** Đề 20 trang trích thành công 9/10 cửa sổ vẫn trả về 0 câu.
4. Module [`ingest/figure_anchors.py`](backend/services/api/src/bookforge_api/ingest/figure_anchors.py) giải quyết **đúng** bài toán "hình bị dồn xuống cuối" mà `build_card_stem` đang mắc — và docstring ghi rõ nó đã được đo **trên một đề thi 99 trang, đặt đúng 151/153 hình**. Luồng extract không dùng.

---

## 1. Pipeline thực tế đang chạy

Endpoint: [`POST /api/question-cards/extract`](backend/services/api/src/bookforge_api/api/question_cards.py#L978-L1163)
Service: [question_exam_extract.py](backend/services/api/src/bookforge_api/services/question_exam_extract.py)

Điểm dễ hiểu nhầm nhất: **đây là hai mô hình chạy song song với hai vai trò khác nhau**, không phải "một bước OCR".

```
      PDF upload (≤ 20 trang, ≤ giới hạn gói)
                    │
                    ▼
      rasterize_pdf() — MỌI trang → PNG 200 DPI
                    │            (không đọc text layer, xem §6)
                    ▼
      is_blank_page() — bỏ trang "trắng" (heuristic < 20KB)
                    │
        ┌───────────┴────────────┐
        ▼                        ▼
  Mistral OCR              Vision LLM (op: question_exam_extract)
  (song song 10 luồng)     (song song 4 luồng, cửa sổ 2 trang)
        │                        │
        │ markdown ──► ✗ VỨT BỎ  │ nhận PNG trang + ảnh cắt
        │ images  ──► ✓ giữ lại  │ detail:'high', max_tokens 8192
        │   (bbox + base64)      │ reasoning_effort: 'low'
        │                        ▼
        │                  JSON {exams:[{questions:[…]}]}
        │                        │ 1 lần sửa lỗi JSON
        └────────────┬───────────┘
                     ▼
        build_card_stem() — ghép stem + parts + ![figure](url)
                     ▼
        create_card(question_type='essay')  ← HARD-CODE
```

**Vai trò Mistral OCR ở đây chỉ là cắt hình minh hoạ.** Tại [question_exam_extract.py:469](backend/services/api/src/bookforge_api/services/question_exam_extract.py#L469):

```python
_markdown, images = ocr_fn(image_path)   # markdown bị bỏ ngay tại đây
return page_no, list(images or [])
```

**Vai trò đọc đề thuộc về vision LLM.** Nó nhận thẳng ảnh trang, trả JSON theo khuôn cố định trong [question_exam_extract_prompts.py](backend/services/api/src/bookforge_api/llm/question_exam_extract_prompts.py):

```json
{"exams": [{
  "school": null, "title": null,
  "questions": [{
    "number": "7", "score": 0.75, "pages": [1, 2],
    "stem": "...",
    "parts": [{"label": "a", "stem": "..."}],
    "figure_ids": ["p01-img-2.jpeg"]
  }]
}]}
```

### Hằng số cấu hình ([core/settings.py](backend/services/api/src/bookforge_api/core/settings.py#L124-L169))

| Tham số | Mặc định | Ghi chú |
| --- | --- | --- |
| `exam_extract_page_ceiling` | 20 | Vượt → 400 `quota_request_too_large` |
| `exam_extract_window_pages` | 2 | Số trang mỗi lần gọi LLM |
| `exam_extract_llm_concurrency` | 4 | Số cửa sổ chạy song song |
| `ocr_page_concurrency` | 10 | Số trang OCR song song |
| DPI raster hoá | **200, hard-code** | Không có setting, xem §6 |
| `max_tokens` mỗi cửa sổ | 8192 | |
| `llm_question_exam_extract_reasoning_effort` | `low` | |

---

## 2. Câu 1 — Xác nhận: hệ thống chỉ trả về câu tự luận

Đúng, và có **hai** cơ chế độc lập cùng dẫn tới kết quả đó:

**(a) Loại câu bị ép cứng.** Tại [question_cards.py:1082-1086](backend/services/api/src/bookforge_api/api/question_cards.py#L1082-L1086):

```python
payload=QuestionCardCreateRequest(
    folder_id=folder_id,
    question_type='essay',          # ← không có nhánh nào khác
    score=question.score,
    content_json={'stem': stem},    # ← không rubric, không reference_answer
```

**(b) Schema đầu ra của model không có chỗ chứa loại câu khác.** Khuôn JSON không có `question_type`, không có `options`, không có `answer`, không có `statements`. Về bản chất nó mô tả đúng hình dạng một câu tự luận nhiều ý.

**(c) Prompt cấm đọc đáp án — có chủ đích.** Nguyên văn `exam_extract_system_prompt`:

> `- Transcribe only. Do not solve. Do not invent answers.`

Tức là kể cả khi đề gốc **có in sẵn đáp án**, hệ thống cũng không lấy. Đây là lựa chọn thiết kế, không phải giới hạn kỹ thuật — điểm này quan trọng khi bàn phương án ở §4.

**(d) FE không cho chọn loại.** [ExamExtractDrawer.tsx](frontend/src/templates/QuestionBankPage/components/exam-extract/ExamExtractDrawer.tsx) chỉ có 2 nhóm trường: "A. Tệp đề thi" (chọn PDF) và "B. Nơi lưu" (chọn thư mục). Không có ô chọn dạng câu hỏi.

---

## 3. Câu 2 — Điều kiện tạo từng loại câu hỏi, đối chiếu dữ liệu OCR

Điều kiện lấy từ `PAYLOAD_MODELS` ([schemas/question_bank.py:39-136](backend/services/api/src/bookforge_api/schemas/question_bank.py#L39-L136)).

| Loại | Field bắt buộc để lưu được | Validate chặt? | OCR hiện cấp đủ? |
| --- | --- | --- | --- |
| `essay` — Tự luận | `stem` | ✅ | ✅ **Đủ tối thiểu** (nhưng rỗng rubric/đáp án) |
| `multiple_choice` — Trắc nghiệm | `stem` + `options` ≥2, **≥1 `is_correct: true`** | ✅ | ❌ Không có `options` |
| `true_false` — Đúng/Sai nhiều ý | `stem` + `statements` ≥1, mỗi ý có `is_true` | ✅ | ❌ Không có `statements` |
| `short_answer` — Trả lời ngắn | `stem` + `answer` | ✅ | ❌ Không có `answer` |
| `visual` — Hình ảnh/Biểu đồ | `stem` + `visual_asset_key` | ✅ | ⚠️ Có ảnh nhưng nhét vào `stem` dạng markdown, không tạo card `visual` |
| `fill_blank` — Điền khuyết | `blanks` ≥1, mỗi blank có `answer` | ❌ *(không validate khi tạo)* | ❌ Không có `blanks` |
| `matching` — Ghép đôi | `pairs` ≥1 (`left`/`right`) | ❌ | ❌ Không có `pairs` |
| `ordering` — Sắp xếp | `items` ≥2, `order` duy nhất | ❌ | ❌ Không có `items` |
| `passage` — Đọc hiểu | `passage` + `answer` | ❌ | ❌ Không tách `passage` khỏi `stem` |

> **Lưu ý về cột "Validate chặt"**: 4 loại đánh ❌ rơi về `BaseCardPayload` — chỉ kiểm `stem`,
> phần còn lại lọt thẳng vào DB không ai soát (`extra='allow'`). Nghĩa là *về mặt kỹ thuật* có thể
> nhét dữ liệu vào, nhưng không có gì đảm bảo đúng hình dạng.

**Kết luận §3**: dữ liệu pipeline thu được — `stem`, `parts[]`, `score`, `figure_ids`, `pages`, `number`
— **chỉ vừa đủ điều kiện tối thiểu cho đúng 1/9 loại**. Và ngay với `essay`, thiếu đúng phần mà tài liệu
hướng dẫn chuyên gia ([huong-dan-chuan-bi-ngan-hang-cau-hoi.md §3.3](backend/docs/product/huong-dan-chuan-bi-ngan-hang-cau-hoi.md))
xếp vào tầng **"CÂU VÀNG — phần quan trọng nhất"**: đáp án tham khảo và phân tích/rubric.

---

## 4. Câu 3 — AI cần thêm gì để trích được các loại câu hỏi khác

### 4.1 Mở schema đầu ra + dạy model phân loại dạng câu

Schema hiện tại là "một khuôn cho mọi câu". Cần thêm `question_type` do model tự suy từ bố cục trang:

| Dấu hiệu trên trang | Loại suy ra |
| --- | --- |
| 4 dòng A/B/C/D ngay sau câu dẫn | `multiple_choice` |
| 4 mệnh đề a/b/c/d + yêu cầu "Đúng hay Sai?" | `true_false` (đúng cấu trúc THPT 2025) |
| Chỗ trống `___` trong câu | `fill_blank` |
| Đoạn văn dài + nhóm câu hỏi phụ | `passage` |
| Hai cột cần nối | `matching` |

Cách làm đã có tiền lệ trong chính repo: `/generate` dùng `build_output_model(question_type)`
([question_cards_ai.py:111-123](backend/services/api/src/bookforge_api/services/question_cards_ai.py#L111-L123))
để ép LLM trả đúng model mà API validate. Khác biệt ở đây: một tài liệu **trộn nhiều loại**, nên cần
discriminated union, hoặc validate hậu kỳ từng câu theo `PAYLOAD_MODELS.get(question_type)` và
**skip từng câu lỗi** (bắt chước `/convert`) thay vì fail cả lô.

### 4.2 Quyết định lại chính sách đáp án

`multiple_choice` / `true_false` / `short_answer` **bắt buộc có đáp án** mới lưu được. Hai hướng:

- **(i) Đề có in đáp án** (đề + đáp án cùng file, hoặc bảng đáp án cuối tài liệu): cho model đọc và gắn
  `is_correct` / `is_true` / `answer`, kèm cờ chất lượng buộc người xác nhận. Hạ tầng cờ **đã có sẵn**
  (`infer_quality_flags`, `review_reasons`) — không cần xây mới.
- **(ii) Đề không có đáp án**: trích ra "khung câu hỏi thiếu đáp án", để `answer_uncertain` tự bật
  (hàm `_has_answer` đã tự phát hiện), buộc giáo viên điền trước khi duyệt.

### 4.3 Bổ sung quy tắc LaTeX vào prompt extract

Đây là thiếu sót rõ và **dễ vá nhất**. Prompt extract chỉ có một dòng `Math as LaTeX ($...$ or $$...$$)`,
trong khi prompt sinh câu (`question_generation_system_prompt`) có `_MATH_FORMAT_RULE` chi tiết + hàm
`_install_latex_output_validator` bắt model viết lại khi phát hiện công thức thô. **Luồng extract không
gọi validator này.** Với đề Toán/Lý/Hoá, đây là rủi ro chất lượng trực tiếp.

### 4.4 Gắn ảnh đúng vị trí, không dồn vào `stem`

`build_card_stem` nhét mọi `figure_urls` vào cuối `stem` dạng `![figure](url)`. Với trắc nghiệm có hình
trong *từng phương án* (rất phổ biến ở đề Hoá/Sinh — sơ đồ, cấu trúc phân tử), ảnh cần gắn vào
`options[i].text`, không phải dồn cuối câu.

> Ba hạng mục nữa phát sinh từ bài toán PDF scan — xem §6.4.

---

## 5. Câu 4 — Đầu ra hiện tại có đáp ứng đủ tiêu chí không

**Không.** Ba lớp thiếu hụt cộng dồn (lớp thứ tư ở §6):

### Lớp 1 — 8/9 loại không tạo được trực tiếp

Muốn có `multiple_choice` từ đề gốc phải đi vòng: OCR → `essay` (chỉ có `stem`) → `/convert`.
Nhưng bước 2 có rủi ro đã được chính tác giả ghi chú trong code
([question_cards_ai.py:210-214](backend/services/api/src/bookforge_api/services/question_cards_ai.py#L210-L214)):
việc AI phải **bịa distractors** cho MC hoặc **bịa rubric** cho essay từ một câu vốn không có đáp án —
nguyên văn: *"các cặp map cơ học sẽ sinh ra rác"*.

Và `/convert` chỉ nhận 4 loại đích generatable → `fill_blank` / `matching` / `ordering` / `passage` / `visual`
**không đạt được bằng bất kỳ đường AI nào hiện có**, kể cả đi vòng.

### Lớp 2 — Ngay `essay` cũng thiếu phần giá trị nhất

Không `rubric`, không `reference_answer`, không `max_score`. Chỉ là "khung đề bài trần".

### Lớp 3 — Mất `cognitive_level` và `difficulty`

Payload extract không set hai trường này → luôn `None` → câu trích ra **lọt khỏi mọi bộ lọc theo mức độ
nhận thức / độ khó** ở màn hình ngân hàng câu hỏi, cho tới khi có người sửa tay từng câu.

### Những gì đang làm ĐÚNG và nên giữ nguyên

- **Truy vết nguồn đầy đủ**: `metadata_json.citation` ghi `filename`, `pages`, `question_number` —
  và điều này **tự động tắt cờ `missing_source`**, đúng thiết kế.
- **Luôn sinh ở trạng thái `new`** → vào thẳng hàng đợi duyệt, không có câu AI nào "born approved".
- **Ghi `AIAction` cả khi thất bại** (`_record_failed_extract`) → truy vết được chi phí và lỗi.
- **Tính chi phí OCR riêng** theo số trang (`record_provider_cost`, `unit_kind='pages'`).

---

## 6. Câu 5 — PDF scan / ảnh: khả thi không, và ảnh hưởng ngược lại

### 6.1 Trả lời ngắn: KHẢ THI — và scan đi **đúng cùng một đường** với PDF thường

Lý do nằm ở [`rasterize_pdf`](backend/services/api/src/bookforge_api/services/question_exam_extract.py#L346-L355):

```python
for index, page in enumerate(document, start=1):
    pixmap = page.get_pixmap(dpi=200, alpha=False)
    pages.append((index, pixmap.tobytes('png'), pixmap.width, pixmap.height))
```

**Mọi trang đều bị raster hoá thành ảnh, không có nhánh nào đọc `page.get_text()`.** Pipeline extract
hoàn toàn "mù" với sự khác biệt born-digital / scan. Nghĩa là:

> PDF scan **không phải trường hợp đặc biệt cần hỗ trợ thêm** — nó đã chạy được từ đầu.
> Chất lượng phụ thuộc năng lực vision model, không phụ thuộc lớp văn bản.

### 6.2 Nhưng đây cũng là một sự lãng phí có thể đo được

Repo **đã có sẵn** hạ tầng phân luồng born-digital/scan — chỉ là luồng extract không dùng.
[`ingest/pipeline.py:route_document_lane`](backend/services/api/src/bookforge_api/ingest/pipeline.py#L72-L113):

```python
avg_chars = sum(len(text) for text in sample_texts) / max(1, sample_pages)
has_text = avg_chars > 120
...
return 'structured_text' if avg_chars > 260 else 'ocr_structured'
```

Và [`ingest/page_markdown.py`](backend/services/api/src/bookforge_api/ingest/page_markdown.py#L24) còn ghi
rõ nguồn từng trang: `source: str  # "ocr" | "born_digital" | "failed"`.

Hệ quả: với đề thi soạn Word → xuất PDF (**rất phổ biến**), hệ thống **vứt bỏ lớp text chính xác 100%**
để đọc lại bằng vision — chậm hơn, tốn token hơn, và tạo nguy cơ sai OCR ở chỗ vốn không thể sai.

### 6.3 Khả thi theo từng hạng mục

| Hạng mục | Trên PDF scan | Cơ sở |
| --- | --- | --- |
| Câu hỏi (`stem`, `parts` a/b/c) | ✅ **Khả thi** | Vision LLM đọc trực tiếp ảnh trang |
| Số câu, điểm số | ✅ Khả thi | Đã có trong schema (`number`, `score`) |
| Hình / biểu đồ | ✅ **Khả thi** | Mistral OCR trả bbox + base64 crop; nó là OCR model nên hoạt động trên ảnh |
| Công thức Toán/Lý/Hoá | ⚠️ **Rủi ro cao** | Prompt extract thiếu quy tắc LaTeX, **không có validator** (§4.3) |
| **Bảng biểu** | ❌ **Bị mất** | Mistral OCR nhận dạng bảng và trả trong `markdown` — **field này bị vứt** ([dòng 469](backend/services/api/src/bookforge_api/services/question_exam_extract.py#L469)). Vision LLM phải tự đọc lại bảng thành text thô trong `stem` |
| Đáp án | ❌ Bị prompt cấm | Không liên quan scan (§2c) |

### 6.4 Năm rủi ro riêng của PDF scan

**① DPI cố định 200, không thích ứng với nguồn** — hard-code, không có setting.
- Scan gốc **300 DPI → bị hạ mẫu**: mất nét chữ nhỏ, đặc biệt chỉ số dưới trong công thức hoá học
  (H₂SO₄, Fe³⁺) và số mũ trong công thức toán.
- Scan gốc **150 DPI → bị nội suy lên**: không thêm thông tin, chỉ tăng dung lượng và chi phí.

**② Heuristic trang trắng lệch hướng với scan** — [`is_blank_page`](backend/services/api/src/bookforge_api/services/question_exam_extract.py#L358-L359):

```python
return len(png_bytes) < BLANK_PNG_BYTES or width < 32 or height < 32   # 20KB
```

Trang scan trắng có nhiễu/hạt → PNG nén kém → > 20KB → **không bị bỏ qua** → tốn cả OCR lẫn token cho
trang trống. (Ngược lại, trang born-digital thưa chữ lại dễ bị bỏ nhầm.)

**③ ⚠️ Một cửa sổ hỏng → mất toàn bộ kết quả cả file** — đây là rủi ro **nghiêm trọng nhất**.
Trong [`extract_exam`](backend/services/api/src/bookforge_api/services/question_exam_extract.py#L519-L536):

```python
for outcome in outcomes:
    ...
    if outcome.error is not None:
        ...
        return _failed_result(...)      # ← vứt luôn questions của MỌI cửa sổ khác
    questions.extend(outcome.questions)
```

Mỗi cửa sổ chỉ có **1 lần sửa lỗi JSON**. Scan nhiễu làm xác suất model trả JSON hỏng cao hơn hẳn.
Với đề 20 trang = 10 cửa sổ, **chỉ cần 1 cửa sổ hỏng là mất trắng cả 10** — người dùng chờ hết thời
gian xử lý rồi nhận về 0 câu.

**④ Không có bước tiền xử lý ảnh nào** — không deskew (chỉnh nghiêng), không khử nhiễu, không nhị phân
hoá, không xử lý bleed-through (chữ mặt sau hằn qua). Scan lệch vài độ hoặc chụp bằng điện thoại là
tình huống thực tế phổ biến với giáo viên.

**⑤ Trần 20 trang dễ vượt** — đề thi scan thường kèm cả đáp án và hướng dẫn chấm.

### 6.5 Ảnh hưởng ngược lại 4 câu trước

| Câu | Thay đổi | Chi tiết |
| --- | --- | --- |
| **§2 (chỉ ra essay)** | **Không đổi** | `question_type='essay'` hard-code, độc lập hoàn toàn với chuyện scan hay không. |
| **§3 (điều kiện từng loại)** | **Không đổi về bản chất, nhưng độ tin cậy giảm** | Xem cảnh báo dưới. |
| **§4 (AI cần thêm gì)** | **+3 hạng mục** | Xem dưới. |
| **§5 (đầu ra đủ chưa)** | **Xấu đi — thêm lớp 4** | Xem dưới. |

**⚠️ Rủi ro âm thầm mới phát hiện (ảnh hưởng §3):** trên scan chất lượng kém, model rất dễ nhầm
**phương án A/B/C/D của câu trắc nghiệm** thành **các ý con a/b/c của câu tự luận** — vì schema chỉ có
chỗ chứa `parts[]`, model sẽ "ép" dữ liệu vào khuôn có sẵn. Kết quả: một câu trắc nghiệm bị lưu thành
câu tự luận có 4 ý con, **không có lỗi nào được báo**, và cờ chất lượng cũng không bắt được vì `stem`
vẫn hợp lệ. Đây là loại lỗi tốn nhiều công sửa tay nhất.

**Ba hạng mục bổ sung cho §4:**

- **4.5 — Phân luồng born-digital / scan.** Tái dùng `route_document_lane` đã có: PDF có text layer thì
  đọc thẳng text (nhanh, chính xác, rẻ), chỉ scan mới đi đường vision.
- **4.6 — DPI thích ứng + tiền xử lý ảnh.** Đọc DPI gốc của ảnh nhúng để chọn DPI raster hoá; thêm
  deskew/khử nhiễu cho nhánh scan.
- **4.7 — Giữ lại markdown của Mistral OCR** để cứu bảng biểu, thay vì vứt ở dòng 469.

**Lớp thiếu hụt thứ 4 cho §5:**

- **Bảng biểu bị mất** (§6.3) — nghiêm trọng với đề Hoá (bảng tuần hoàn, bảng số liệu),
  Lý (bảng đo), Địa (bảng thống kê).
- **Không có thước đo độ tin cậy nào** — không confidence score, không cờ "OCR chất lượng thấp",
  không đánh dấu trang scan xấu. Giáo viên không biết câu nào cần soát kỹ hơn câu nào.

---

## 7. Câu 6 — PDF thường (born-digital): nghịch lý lớn nhất

### 7.1 Trả lời ngắn

PDF born-digital (đề soạn Word/LaTeX → xuất PDF, có lớp văn bản) **đi đúng cùng một đường với PDF scan**
— vì `rasterize_pdf` không phân biệt (§6.1). Nhưng đây mới là trường hợp **tệ nhất về mặt lãng phí**:

> Với PDF scan, vision là lựa chọn *duy nhất* — cách làm hiện tại là hợp lý.
> Với PDF born-digital, repo **đã có sẵn** một đường xử lý tốt hơn hẳn ở mọi mặt, đã được kiểm chứng
> trên chính đề thi, và luồng extract **bỏ qua hoàn toàn**.

### 7.2 Đường born-digital đã có sẵn trong repo

[`ingest/born_digital_markdown.py`](backend/services/api/src/bookforge_api/ingest/born_digital_markdown.py)
dùng `pymupdf4llm` engine cổ điển — **không OCR**, đọc thẳng text layer. Nó gọi thêm hai module tinh vi:

**① [`math_layout.py`](backend/services/api/src/bookforge_api/ingest/math_layout.py) — dựng lại công thức từ hình học trang.**
Không đoán bằng thị giác mà đọc `page.get_text('dict')` lấy font, cỡ chữ, bbox từng span, cộng với
`page.get_drawings()` để tìm **gạch phân số** (`_fraction_bars`), rồi suy ra chỉ số trên/dưới bằng tỉ lệ
cỡ chữ (`_SCRIPT_SIZE_RATIO = 0.78`). Quan trọng nhất — dòng 9 của module ghi rõ: **"emits LaTeX inside `$...$`"**,
và dòng 734 xác nhận `'$%s$' % latex if is_math else latex`.

→ Nghĩa là với PDF born-digital, **LaTeX được dựng lại chính xác từ dữ liệu gốc**, không phải do model
đoán từ ảnh. Đây đúng thứ mà §4.3 đang thiếu.

**② [`figure_anchors.py`](backend/services/api/src/bookforge_api/ingest/figure_anchors.py) — đặt hình đúng vị trí.**
Docstring mô tả **chính xác lỗi mà `build_card_stem` đang mắc**:

> *"pymupdf4llm ... appends every ref after the page text, footer included. The reader then gets the
> chart for question 3 sitting below question 5."*

Nó khôi phục vị trí y thật bằng hai tín hiệu (kích thước rect suy ngược từ pixel + thứ tự đọc), và
**đã được đo trên một đề thi 99 trang: đặt đúng 151/153 hình**.

**③ Bảng biểu được phát hiện sẵn.** `chunk.get('tables')` từ `pymupdf4llm` — `_with_rebuilt_math` còn
cố ý *không* dựng lại math trên trang có bảng để tránh "đánh đổi một bảng thật lấy một cái hình đặt đúng chỗ".

### 7.3 So sánh trực diện trên cùng một file PDF born-digital

| Hạng mục | Luồng extract hiện tại | Luồng born-digital đã có |
| --- | --- | --- |
| Văn bản câu hỏi | Vision đọc lại từ ảnh 200 DPI | `pymupdf4llm` đọc thẳng text layer — **chính xác tuyệt đối** |
| Công thức Toán/Hoá | Vision đoán, **không có validator LaTeX** | `math_layout` dựng từ hình học, **emit LaTeX `$...$`** |
| Vị trí hình | Dồn hết xuống cuối `stem` | `figure_anchors` đặt đúng y — 151/153 trên đề 99 trang |
| Chất lượng file hình | Mistral OCR crop lại từ ảnh raster | Trích ảnh nhúng gốc, 150 DPI, không qua raster |
| Bảng biểu | **Mất** | `chunk['tables']` có sẵn |
| Chi phí OCR | **$0.001/trang** ([token_rates.py:175](backend/services/api/src/bookforge_api/services/token_rates.py#L175)) | **$0** — không gọi OCR |
| Chi phí LLM | Toàn bộ trang dạng ảnh, `detail:'high'` | Chỉ cần phân đoạn text → JSON, rẻ hơn nhiều |
| Cơ chế bảo vệ | 1 lần sửa JSON, hỏng là mất cả file | `_letters(rebuilt) < 0.9 * _letters(page.get_text())` — tự phát hiện mất chữ |

Với đề 20 trang born-digital, riêng phần OCR đang tiêu **~$0.02 hoàn toàn vô ích** mỗi lần tải lên,
chưa kể chi phí vision token cho việc đọc lại thứ đã có sẵn dạng text.

### 7.4 Born-digital sửa được gì, và KHÔNG sửa được gì

Đây là phần quan trọng nhất khi lập kế hoạch — born-digital giải quyết **vấn đề chất lượng đầu vào**,
nhưng **không chạm tới** vấn đề schema đầu ra.

| Vấn đề đã nêu | Born-digital có sửa? |
| --- | --- |
| §6.4① DPI cố định 200 | ✅ Không còn liên quan — không raster hoá |
| §6.4② Heuristic trang trắng lệch | ✅ Không còn liên quan |
| §6.4④ Nghiêng, nhiễu, bleed-through | ✅ Không tồn tại |
| §6.3 Mất bảng biểu | ✅ Sửa được — `tables` có sẵn |
| §4.3 Thiếu LaTeX | ✅ Sửa được — LaTeX dựng từ hình học |
| §4.4 Hình dồn cuối `stem` | ✅ Sửa được — `figure_anchors` |
| §6.5 Nhầm A/B/C/D thành ý con a/b/c | ✅ **Cải thiện mạnh** — xem 7.5 |
| §2 `question_type='essay'` hard-code | ❌ **Không** — lỗi ở tầng route |
| §2c Prompt cấm đọc đáp án | ❌ **Không** — quyết định sản phẩm |
| §6.4③ Một cửa sổ hỏng mất cả file | ❌ **Không** — vẫn nguyên (dù xác suất lỗi giảm) |
| §5 lớp 3 Mất `cognitive_level`/`difficulty` | ❌ **Không** |
| Trần 20 trang | ❌ **Không** |

### 7.5 Một lợi thế mà vision không bao giờ có

Rủi ro âm thầm ở §6.5 — model nhầm **phương án A/B/C/D** thành **ý con a/b/c** — với born-digital là bài
toán **có thể giải bằng dấu hiệu cấu trúc**, không cần đoán:

`math_layout._collect_spans` đã trả về `font`, `size`, `x0/y0/x1/y1` cho từng span. Phương án trắc nghiệm
có đặc trưng hình học rất rõ: nhãn "A." "B." "C." "D." nằm ở **cùng một toạ độ x**, cách đều nhau theo y,
thường 2 hoặc 4 cột đều nhau. Ý con tự luận "a)" "b)" thì thụt lề khác và độ dài nội dung khác hẳn.

Vision model chỉ nhìn thấy pixel; born-digital có sẵn số đo. Đây là tín hiệu **miễn phí** để phân loại
`multiple_choice` vs `essay` — trực tiếp phục vụ §4.1.

### 7.6 Ba cái bẫy khi triển khai phân luồng

**① `route_document_lane` chỉ lấy mẫu 6 trang đầu.**
[pipeline.py:76](backend/services/api/src/bookforge_api/ingest/pipeline.py#L76): `sample_pages = min(page_count, 6)`
rồi ra **một quyết định cho cả tài liệu**. Đề thi thực tế hay ở dạng lai — 10 trang đề soạn máy + phụ lục
scan ở cuối, hoặc ngược lại. Với question extract nên quyết định **theo từng trang**, không theo tài liệu.

**② PDF đã qua OCR phần mềm rẻ tiền là cái bẫy nguy hiểm nhất.**
Loại này *có* text layer nên `avg_chars > 120` phân loại thành born-digital — nhưng text đó là **rác OCR**
(sai dấu tiếng Việt, dính chữ, công thức vỡ). Đường born-digital sẽ tin tưởng lớp text rác đó và cho ra kết
quả tệ hơn cả vision. Cần thêm kiểm tra chất lượng text layer, không chỉ đếm ký tự — ví dụ tỉ lệ ký tự
tiếng Việt hợp lệ, tỉ lệ từ có trong từ điển.

**③ Đầu ra born-digital là markdown theo trang, không phải câu hỏi.**
`extract_born_digital_markdown` trả `list[PageMarkdown]`, vẫn cần **một bước LLM phân đoạn markdown thành
câu hỏi**. Nhưng đó là bài toán *text vào → JSON ra*, rẻ hơn và ổn định hơn hẳn *ảnh vào → JSON ra*.
Ngoài ra file hình được ghi ra `image_dir` trên đĩa, cần chuyển vào kho ảnh câu hỏi
(`store_image` + `register_object`) như luồng hiện tại đang làm với crop của Mistral.

→ Nên đây **không phải** việc cắm dây là xong; nhưng phần khó (đọc text, dựng LaTeX, định vị hình,
bắt bảng) thì đã xong và đã được kiểm chứng.

---

## 8. Bảng tổng hợp khoảng trống, xếp theo đề xuất ưu tiên

> **Thứ tự này đã được sửa lại sau §7.** Ở bản trước, "phân luồng born-digital" xếp thứ 7 vì tưởng nó
> chỉ là tối ưu chi phí. Thực tế nó **kéo theo miễn phí** 3 hạng mục khác (LaTeX, bảng biểu, vị trí hình)
> cho toàn bộ tập PDF born-digital — nên phải xếp cao hơn nhiều.

| # | Hạng mục | Loại | Chi phí sửa | Vì sao xếp ở đây |
| --- | --- | --- | --- | --- |
| 1 | Bỏ all-or-nothing khi 1 cửa sổ lỗi (§6.4③) | Sửa lỗi | **Thấp** | Đang gây mất trắng dữ liệu. **Phải sửa trước** khi mở schema — schema phức tạp hơn ⇒ JSON dễ lỗi hơn ⇒ càng dễ mất trắng. Áp dụng cho cả scan lẫn born-digital. |
| 2 | Thêm quy tắc LaTeX + validator vào prompt extract (§4.3) | Chất lượng | **Thấp** | `_install_latex_output_validator` đã có sẵn, chỉ cần gọi. Vá tạm cho nhánh scan cho tới khi có #4. |
| 3 | Giữ markdown OCR để cứu bảng biểu (§4.7) | Mất dữ liệu | Thấp–TB | Dữ liệu đã trả về rồi, chỉ đang bị vứt ở [dòng 469](backend/services/api/src/bookforge_api/services/question_exam_extract.py#L469). |
| 4 | **Phân luồng born-digital theo từng trang** (§7) | Nền tảng | **TB–Cao** | Kéo theo #2, #3, #6 miễn phí cho tập born-digital; cắt $0.001/trang OCR; cấp tín hiệu cấu trúc cho #5 (§7.5). Cẩn thận 3 cái bẫy ở §7.6. |
| 5 | Mở schema đa loại + `question_type` (§4.1) | Tính năng lõi | **Cao** | Phần chính. Đứng sau #4 vì born-digital cấp sẵn tín hiệu font/toạ độ để phân loại đáng tin hơn nhiều. |
| 6 | Chính sách đáp án (§4.2) | Quyết định sản phẩm | TB | Cần chốt hướng (i) hay (ii) **trước khi** code #5. |
| 7 | Gắn ảnh vào đúng `options[i]` (§4.4) | Chất lượng | TB | Phụ thuộc #5. Nhánh born-digital đã có `figure_anchors` lo phần định vị. |
| 8 | Bổ sung `cognitive_level` / `difficulty` (§5 lớp 3) | Chất lượng dữ liệu | Thấp | Để AI suy đoán kèm cờ chờ xác nhận. |
| 9 | Kiểm tra chất lượng text layer (§7.6②) | Chống hồi quy | TB | Chỉ cần khi #4 đã chạy — chặn PDF "OCR rác" đi nhầm nhánh born-digital. |
| 10 | Tiền xử lý ảnh scan, thước đo độ tin cậy (§6.4④, §6.5) | Chất lượng | Cao | Làm sau khi có số liệu thực tế về tỉ lệ lỗi, và chỉ còn ảnh hưởng tập scan. |

### Ghi chú về phạm vi ảnh hưởng

Không phải hạng mục nào cũng chạm tới cả hai loại PDF — điều này quyết định thứ tự làm:

| Hạng mục | PDF scan | PDF born-digital |
| --- | --- | --- |
| #1 all-or-nothing | ✅ Ảnh hưởng nặng hơn (JSON dễ lỗi) | ✅ Vẫn ảnh hưởng |
| #2 LaTeX validator | ✅ Cần thiết | ⚪ Thừa nếu có #4 |
| #3 Cứu bảng biểu | ✅ Cần thiết | ⚪ Thừa nếu có #4 |
| #4 Phân luồng | ⚪ Không đổi gì | ✅ Toàn bộ lợi ích |
| #5 Schema đa loại | ✅ | ✅ (đáng tin hơn) |
| #6 Chính sách đáp án | ✅ | ✅ |
| #10 Tiền xử lý ảnh | ✅ | ⚪ Không liên quan |

---

## 9. Phụ lục

### Mã lỗi liên quan

| Mã | Khi nào |
| --- | --- |
| `exam_extract_invalid_file` | Không phải `.pdf`, hoặc PyMuPDF không mở được |
| `exam_extract_no_pages` | Mọi trang đều bị `is_blank_page` loại |
| `quota_request_too_large` | Vượt `exam_extract_page_ceiling` (20) — `dimension='exam_extract_pages'` |
| `editor_assistant_unavailable` | Chưa cấu hình model cho op `question_exam_extract` |
| `editor_assistant_failed` | Lỗi provider, hoặc JSON hỏng sau 1 lần sửa (§6.4③) |
| `file_empty` / `file_too_large` | Theo `plan.max_upload_bytes` |

### File liên quan

| File | Vai trò |
| --- | --- |
| [services/question_exam_extract.py](backend/services/api/src/bookforge_api/services/question_exam_extract.py) | Pipeline chính: raster, OCR, cửa sổ, parse JSON |
| [llm/question_exam_extract_prompts.py](backend/services/api/src/bookforge_api/llm/question_exam_extract_prompts.py) | Prompt hệ thống + khuôn JSON |
| [api/question_cards.py:978-1163](backend/services/api/src/bookforge_api/api/question_cards.py#L978-L1163) | Endpoint `/extract`, tạo card, ghi chi phí |
| [llm/mistral_ocr.py](backend/services/api/src/bookforge_api/llm/mistral_ocr.py) | Provider OCR (cắt hình) |
| [llm/question_bank_prompts.py](backend/services/api/src/bookforge_api/llm/question_bank_prompts.py) | Prompt sinh/đổi loại — **có `_MATH_FORMAT_RULE` để đối chiếu** |
| [services/question_cards_ai.py](backend/services/api/src/bookforge_api/services/question_cards_ai.py) | `/generate`, `/convert`, LaTeX validator |
| [components/exam-extract/](frontend/src/templates/QuestionBankPage/components/exam-extract/) | UI drawer nhập đề |

**Hạ tầng born-digital có sẵn (§7) — luồng extract chưa dùng:**

| File | Vai trò |
| --- | --- |
| [ingest/pipeline.py:72-113](backend/services/api/src/bookforge_api/ingest/pipeline.py#L72-L113) | `route_document_lane` — phân luồng born-digital/OCR |
| [ingest/born_digital_markdown.py](backend/services/api/src/bookforge_api/ingest/born_digital_markdown.py) | Trích markdown + hình từ PDF có text layer, không OCR |
| [ingest/math_layout.py](backend/services/api/src/bookforge_api/ingest/math_layout.py) | Dựng lại công thức từ hình học trang → **LaTeX `$...$`** |
| [ingest/figure_anchors.py](backend/services/api/src/bookforge_api/ingest/figure_anchors.py) | Khôi phục vị trí y thật của hình — **đo trên đề 99 trang, 151/153** |
| [ingest/page_markdown.py](backend/services/api/src/bookforge_api/ingest/page_markdown.py) | Ghi nguồn từng trang: `"ocr" \| "born_digital" \| "failed"` |
| [services/token_rates.py:154-175](backend/services/api/src/bookforge_api/services/token_rates.py#L154-L175) | Giá Mistral OCR: **$0.001/trang** |

### Test hiện có

`tests/test_question_exam_extract.py` (parse JSON, window, remap trang, figure ids),
`tests/test_question_cards_extract_api.py` (endpoint), `tests/test_math_extraction.py`.
