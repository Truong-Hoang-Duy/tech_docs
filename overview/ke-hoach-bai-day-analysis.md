# Tính năng soạn Kế hoạch bài dạy — Khảo sát hiện trạng & các vấn đề

> Tài liệu khảo sát mã nguồn, trả lời câu hỏi: *hệ thống có tính năng tạo kế hoạch bài dạy không, nó chạy thế nào, đang hỏng chỗ nào.*
> Ngày khảo sát: **2026-09-08**. Repo: `d:\Project\bookforge` — `bookforge@a62910d` (BE), `bookforge-fe` (FE, working tree).
> Nguồn: đọc mã `backend/services/api/src/bookforge_api/`, `frontend/src/`, tài liệu sản phẩm `backend/docs/product/chat-workspace-v1.md`, spec `backend/docs/superpowers/specs/2026-08-25-chat-workspace-output-activation-design.md`.
> Chưa chạy thử runtime, chưa xem log/DB thật — mọi khẳng định dưới đây suy ra từ mã nguồn, chỗ nào chưa kiểm chứng được ghi rõ ở §7.

---

## Mục lục

1. [Kết luận ngắn](#1-kết-luận-ngắn)
2. [Bản đồ thành phần](#2-bản-đồ-thành-phần)
3. [Luồng hoạt động](#3-luồng-hoạt-động)
4. [Cách hệ thống kiểm khung 5512](#4-cách-hệ-thống-kiểm-khung-5512)
5. [Các vấn đề phát hiện](#5-các-vấn-đề-phát-hiện)
6. [Bảng tổng hợp vấn đề](#6-bảng-tổng-hợp-vấn-đề)
7. [Vùng chưa kiểm chứng](#7-vùng-chưa-kiểm-chứng)
8. [Tham chiếu nhanh các file](#8-tham-chiếu-nhanh-các-file)

---

## 1. Kết luận ngắn

**Có.** Tính năng tồn tại, tên nội bộ là **Chat Workspace**, loại đầu ra `giao_an` — nhãn người dùng là **"Kế hoạch bài dạy"**.

Ba đặc điểm cần nắm trước khi đọc tiếp:

- Đây **không phải một trang riêng**. Không có route `/lesson-plan`, không có bảng CSDL riêng, không có endpoint `/api/lesson-plans`. Nó là một *chế độ của Chat chính* (`/` — `HomePage`): agent gọi tool `write_draft`, server ghi nội dung thành một Document Canvas markdown thường.
- Tính năng bị **khoá sau feature flag `chat_workspace`**, mặc định **tắt** (`core/settings.py:222` — `chat_workspace_enabled: bool = False`), và còn phải được cấp riêng cho từng tổ chức trong bảng `organization_feature_flags`. Tức phải bật ở hai nơi mới thấy.
- Sản phẩm **vừa bị thu hẹp phạm vi**: bản v1 thiết kế 5 loại đầu ra (Giáo án / Kế hoạch / Báo cáo / Checklist / Tài liệu), nhưng backend hiện chỉ còn chấp nhận **duy nhất `giao_an`** (`chat/workspace.py:9`). Frontend **chưa được cập nhật theo**. Phần lớn vấn đề ở §5 sinh ra từ đúng lần thu hẹp chưa dọn hết này.

---

## 2. Bản đồ thành phần

```text
FRONTEND (bookforge-fe)
  src/templates/HomePage/                     Chat chính — nơi tính năng sống
    partials/use-chat-with-ai.ts              gửi tin, đọc SSE
    partials/workspace-ui.ts                  map session -> state UI (outputType, workspaceDraft)
  src/components/Chat/partial/
    output-chip.tsx                           chip "◎ Đầu ra" trên thanh soạn tin
    workspace-copy.ts                         nhãn tiếng Việt của 5 loại đầu ra
    workspace-draft-card.tsx                  thẻ "Đang soạn" + nút Mở / Hoàn thiện
    ask-back-card.tsx                         thẻ hỏi lại nhiều lựa chọn (xem V5 — đã chết)

BACKEND (bookforge)
  api/chat.py                                 endpoint chat, vá phiên, ghi nháp, ask-back
  chat/workspace.py                           định nghĩa loại đầu ra, chuẩn hoá, lọc option
  chat/workspace_prompt.py                    prompt hệ thống (v11) cho vai "đồng nghiệp của giáo viên"
  chat/workspace_tools.py                     WorkspaceToolset: set_output / write_draft / check_draft / search_library
  chat/output_outlines.py                     khung Phụ lục IV + bộ kiểm khung bằng regex
  chat/adk_agent.py:987-1013                  đăng ký tool cho agent theo trạng thái phiên
  services/chat_document.py:124               persist_workspace_draft — ghi markdown thành Document
  api/documents.py:464-472                    POST /from-chat-message — nút "Chỉnh sửa" trong chat

DỮ LIỆU
  bảng chat_sessions: output_type, output_sentence, format_document_id,
                      draft_document_id, draft_status, pending_ask_json
  bảng documents:     metadata origin='chat_workspace', output_type
  (không có bảng nào riêng cho kế hoạch bài dạy)
```

Ngoài ra `services/curriculum_library.py` có phân loại thư mục `Giáo án/THCS`, `Giáo án/THPT` (`CATEGORY_LESSON_PLAN`) — nhưng đó là **công cụ nạp file mẫu vào org template**, không nối vào luồng soạn ở trên. Xem V4.

---

## 3. Luồng hoạt động

### 3.1 Hai trạng thái phiên: cold và warm

Toàn bộ thiết kế xoay quanh một khoá duy nhất: `chat_sessions.output_type`.

```text
COLD  (output_type IS NULL)
  Tool agent có:   retrieve* / search_library / set_output
  Prompt nạp:      WORKSPACE_SHARED + WORKSPACE_COLD_MASTER   (không có khung 5512)
  Ghi file:        KHÔNG
        |
        |  ba cửa bật (§3.2)
        v
WARM  (output_type = 'giao_an')
  Tool agent có:   + write_draft + check_draft
  Prompt nạp:      WORKSPACE_SHARED + WORKSPACE_WARM_MASTER + khung Phụ lục IV
  Ghi file:        có — persist_workspace_draft
```

Cơ chế phân nhánh nằm ở `api/chat.py:424-432` (`_workspace_tool_names`) và `chat/adk_agent.py:1002` (chỉ đăng ký `write_draft`/`check_draft` khi `session.output_type` khác None). Đây là chốt cứng đúng hướng: model **không thể tưởng tượng ra tool nó không có**.

### 3.2 Ba cửa bật cold → warm

| Cửa | Ai quyết định | Cùng lượt tin đó có ghi file luôn không |
|---|---|---|
| Agent gọi `set_output('giao_an')` | Agent | **Có** — server tự chạy tiếp lượt warm (`_should_warm_continue`, `api/chat.py:435-441`) |
| Người dùng bấm chip ◎ → "Kế hoạch bài dạy" | Giáo viên | Không — lượt gửi kế tiếp mới warm |
| Người dùng bấm nút "Chỉnh sửa" trên một câu trả lời | Giáo viên | Có, nhưng đi đường khác — xem V2 |

### 3.3 Một lượt soạn đầy đủ

```text
Giáo viên: "Soạn kế hoạch bài dạy Toán 10 bài Phương trình bậc hai"
     |
     v
POST /api/chat/sessions/{id}/messages/stream
     |
     +- phiên cold -> agent gọi set_output('giao_an')
     |        ghi session.output_type trong bộ nhớ, trả warm_continue=True
     |
     +- server chạy TIẾP lượt thứ hai trong cùng request, lần này warm
     |        agent gọi write_draft(markdown đầy đủ)   <- chỉ đệm vào RAM
     |        agent gọi check_draft()                  <- đối chiếu khung, trả {ok, missing}
     |        agent viết lời nhắn trong chat
     |
     v
persist_workspace_draft (services/chat_document.py:124)
     +- chưa có nháp -> tạo Document mới (lane 'chat_markdown', editable)
     |                  trừ quota 1 trang ai_ready
     |                  gán session.draft_document_id, draft_status='drafting'
     +- đã có nháp   -> ghi đè: EditorDocument version+1, cập nhật storage
                        (document.md, editor/source.html, tree.json, nodes.jsonl)
     |
     v
FE hiện thẻ "Đang soạn" -> nút "Mở" mở Canvas, "Hoàn thiện" đặt draft_status='done'
```

Một phiên chat chỉ có **đúng một** nháp. Mọi lần ghi đều ghi đè lên chính file đó.

---

## 4. Cách hệ thống kiểm khung 5512

Điểm mạnh nhất của tính năng: bộ kiểm khung **không** hỏi model "xong chưa" mà tự đối chiếu bằng regex — `_check_giao_an_pl4` (`chat/output_outlines.py:103-161`). Nó trả về danh sách nhãn còn thiếu:

| Nhóm kiểm | Nội dung |
|---|---|
| Header | tên bài, môn, lớp, số tiết (tìm trong phần văn bản trước mục I) |
| Mục I | I.1 kiến thức · I.2 năng lực · I.3 phẩm chất |
| Mục II | Thiết bị dạy học |
| Mục III | HĐ1, HĐ2, HĐ3 — mỗi HĐ đủ 4 ô a) mục tiêu b) nội dung c) sản phẩm d) tổ chức |
| Chống sao chép khung | 8 chuỗi hướng dẫn in nghiêng của Phụ lục IV (`_KHUNG_ECHO`) nếu bị model chép nguyên vào bài |
| Chống kịch bản thoại | dòng bắt đầu bằng `GV:` / `HS:` trong phần tiến trình |
| Rút kinh nghiệm | báo thừa nếu có mục này mà phiên không dùng file mẫu |

HĐ4 (Vận dụng) cố ý **không** bắt buộc. Prompt yêu cầu chỉ thêm khi có nhiệm vụ thực tế.

---

## 5. Các vấn đề phát hiện

### V1 — Frontend vẫn chào 5 loại đầu ra, backend chỉ nhận 1 · **chặn người dùng**

`WORKSPACE_OUTPUT_TYPE_ORDER` liệt kê đủ 5 loại và chip render hết thành nút bấm:

- `frontend/src/components/Chat/partial/workspace-copy.ts:3-17` — nhãn 5 loại
- `frontend/src/components/Chat/partial/output-chip.tsx:103-115` — `.map()` render 5 nút, click gửi `PATCH { output_type: type }`
- `frontend/src/api/bookforge-api.ts:292-297` — union type vẫn 5 nhánh

Backend chỉ chấp nhận `giao_an`, và alias `ke_hoach` / `khbd` → `giao_an` (`chat/workspace.py:9-21`). Trong `_apply_workspace_session_patch` (`api/chat.py:492-497`), `normalize_output_type` trả `None` thì ném `validation_error`.

Hậu quả trên UI:

| Giáo viên bấm | Backend làm gì | Người dùng thấy |
|---|---|---|
| Kế hoạch bài dạy | nhận | đúng |
| Kế hoạch công việc | **âm thầm đổi thành `giao_an`** | chip lát sau hiện "Kế hoạch bài dạy" — không ai giải thích |
| Báo cáo | **422 validation_error** | thao tác thất bại, không có thông báo giải thích được |
| Checklist | **422** | như trên |
| Tài liệu | **422** | như trên |

Đây là lỗi nặng nhất về mặt người dùng: ba nút trong năm nút của một panel đang hỏng.

### V2 — Nút "Chỉnh sửa" đẩy phiên vào loại `tai_lieu` mà chính backend từ chối · **sai trạng thái**

`persist_workspace_draft` có nhánh dự phòng:

```python
# services/chat_document.py:159-160
if session.output_type is None:
    session.output_type = 'tai_lieu'
```

Nhánh này gán thẳng vào cột, **không đi qua** `normalize_output_type`. Đường vào có thật: `POST /api/documents/from-chat-message` (`api/documents.py:464-472`) — nút "Chỉnh sửa" trên một câu trả lời — gọi `persist_workspace_draft` khi feature bật và mode là `general`, kể cả lúc phiên còn cold.

Sau lần đó phiên rơi vào trạng thái mâu thuẫn:

- phiên tính là **warm** (`output_type` khác None) nên agent được cấp `write_draft`;
- prompt nạp `OUTPUT_OUTLINES['tai_lieu']` — *"No standard khung. Fallback type."* (`chat/output_outlines.py:28`) — **trái ngược** với `WORKSPACE_SHARED` đang khẳng định đầu ra Canvas duy nhất là kế hoạch bài dạy (`chat/workspace_prompt.py:19-21`);
- chip hiển thị "Tài liệu"; giáo viên bấm lại đúng chữ "Tài liệu" đó thì nhận **422**;
- `check_draft` đối chiếu theo nhánh `tai_lieu` (chỉ cần có 1 heading markdown là `ok=True`) chứ không kiểm Phụ lục IV.

Tức là: một cú bấm "Chỉnh sửa" có thể **vô hiệu hoá toàn bộ bộ kiểm khung 5512** cho phần còn lại của phiên.

### V3 — `check_draft` chỉ là lời khuyên, không phải cổng chặn · **rủi ro chất lượng**

Ở chỗ ghi file (`api/chat.py:1319-1334`), điều kiện ghi chỉ gồm: có markdown, có `context`, không có ask, và `chat_session.output_type` khác None. **Không đọc kết quả `check_draft`.**

Prompt có câu *"Do not claim the draft is finished while missing is non-empty"*, nhưng đó là ràng buộc mềm đặt lên model. Nếu model bỏ qua `check_draft`, hoặc gọi rồi lờ `missing`, file vẫn được ghi vào thư viện của giáo viên như một kế hoạch bài dạy hoàn chỉnh. Kết quả `{ok, missing}` hiện **không được lưu vào metadata Document, không hiện trên thẻ "Đang soạn"** — giáo viên không có cách nào biết bản nháp thiếu mục nào.

### V4 — Không có nguồn Chương trình GDPT 2018 / YCCĐ nào được nối vào · **rủi ro nghiệp vụ**

Khung yêu cầu rõ: *"observable verbs from YCCĐ"* (`chat/output_outlines.py:12`). Nhưng agent không có bất kỳ tool nào tra cứu yêu cầu cần đạt:

- Phiên cold, không chọn tài liệu → `knowledge_scope = isolated`, không có tool `retrieve` (`chat/adk_agent.py:458-460`).
- `search_library` chỉ chạy khi giáo viên chủ động yêu cầu tìm, **và** tổ chức bật thêm cờ `chat_document_tools`, **và** tổ chức đã có `knowledge_summary_dataset_id` (`chat/workspace_tools.py:150-160`). Ba điều kiện đồng thời.
- `services/curriculum_library.py` có nạp sẵn thư mục `Quy định/`, `Tài liệu học tập/`, `Giáo án/THCS|THPT` vào org template — nhưng **không có đoạn mã nào** trong luồng workspace đọc tới nó.

Nghĩa là trong kịch bản mặc định (giáo viên gõ "soạn kế hoạch bài dạy Toán 10 bài X", không đính kèm gì), **toàn bộ mục tiêu — kiến thức, năng lực, phẩm chất — do model tự nghĩ ra**. Đúng khung Phụ lục IV về hình thức, không có gì bảo đảm đúng YCCĐ của chương trình. Với sản phẩm dành cho giáo viên phổ thông, đây là rủi ro nghiệp vụ lớn hơn mọi lỗi kỹ thuật ở trên.

### V5 — Hạ tầng ask-back đã chết ở tầng prompt nhưng còn nguyên ở mọi tầng khác · **nợ kỹ thuật**

Prompt v11 tuyên bố dứt khoát: *"There is no ask-back. Do not offer multiple-choice cards"* (`chat/workspace_prompt.py:44`). Và đúng vậy, `ask_user` **không còn được đăng ký làm tool** — khối `adk_agent.py:987-1013` chỉ đăng ký `search_library`, `set_output`, `write_draft`, `check_draft`.

Nhưng phần còn lại vẫn sống nguyên:

| Còn tồn tại | Vị trí |
|---|---|
| `WorkspaceToolset.ask_user` | `chat/workspace_tools.py:38-88` |
| `normalize_ask_options` / `filter_kind_a_ask_options` / `prepare_ask_options` / `pack_output_actions_for_draft` | `chat/workspace.py` (~150 dòng) |
| Xử lý ask trong luồng ghi tin | `api/chat.py:1277-1316` |
| 2 endpoint `POST /ask-back` và `/ask-back/stream` | `api/chat.py:2350`, `2412` |
| Cột `chat_sessions.pending_ask_json` | model `document.py` |
| `ask-back-card.tsx` + test | frontend |
| Nhánh `if 'ask_user' in tools:` trong `_tool_policy` | `chat/workspace_prompt.py` — **không bao giờ đúng**, vì `_workspace_tool_names` không bao giờ thêm `ask_user` |

Hệ quả cụ thể, không chỉ là "code thừa": `infer_output_type_from_label` (`chat/workspace.py:106-124`) vẫn map nhãn về `bao_cao` / `checklist` / `tai_lieu`. Nếu trong CSDL còn phiên cũ có `pending_ask_json` sinh từ trước lần thu hẹp, giáo viên bấm vào option đó sẽ ăn **422** tại `_stamp_session_output` (`api/chat.py:2194-2198`).

### V6 — Test đang bảo vệ mã chết · **nợ kỹ thuật**

`services/api/tests/test_chat_workspace_units.py` vẫn khẳng định hành vi của 4 loại đã bị loại bỏ:

- dòng 62 — kiểm nội dung `OUTPUT_OUTLINES['ke_hoach']`
- dòng 90-120 — `check_draft_markdown(..., 'ke_hoach')` phải qua đủ 5 heading kế hoạch công việc
- dòng 412-429 — kiểm `bao_cao`, `checklist`, `tai_lieu`
- dòng 527-529 — `infer_output_type_from_label` phải trả `ke_hoach`, `bao_cao`

Đồng thời dòng 70-74 lại khẳng định `normalize_output_type` chỉ chấp nhận `giao_an`. Bộ test tự nó nhất quán, nhưng đọc vào thì tưởng hệ thống còn hỗ trợ 5 loại. Người sửa sau sẽ mất thời gian, và bất kỳ ai dọn mã chết cũng sẽ phải xoá test kèm theo.

### V7 — Quota chặn *sau* khi đã đốt token · **lãng phí chi phí**

Preflight quota `_preflight_workspace_draft_create` (`api/chat.py:399-411`) thoát sớm khi `session.output_type` còn None:

```python
if not session.output_type:
    return
```

Nhưng ở kịch bản phổ biến nhất — phiên cold, giáo viên gõ thẳng "soạn kế hoạch bài dạy…" — phiên chỉ trở thành warm **giữa lượt**, sau khi agent gọi `set_output`. Preflight đã chạy xong và bỏ qua từ trước đó. Việc kiểm quota thật sự xảy ra bên trong `persist_workspace_draft` → `_quota_workspace_create` (`services/chat_document.py:112-122`), tức là **sau khi model đã soạn xong cả bản kế hoạch**.

Tổ chức hết hạn hoặc hết quota sẽ: tốn trọn phần token sinh kế hoạch bài dạy → rồi nhận lỗi → không có file. Tiền mất, sản phẩm không có.

### V8 — Bản nháp không lưu định danh môn / lớp / tên bài · **hạn chế sản phẩm**

Metadata Document khi tạo (`services/chat_document.py:151-158`) chỉ có `origin`, `output_type`, `source_session_id`, `source_message_id`. Môn, khối lớp, tên bài, số tiết chỉ nằm trong **thân văn bản markdown**.

Kéo theo:

- không lọc/thống kê được "trường này đã soạn bao nhiêu KHBD môn Toán lớp 10";
- không nối được với `question_bank` (đã có sẵn `question_knowledge_frameworks`, `question_knowledge_nodes` theo khung chương trình) để sinh câu hỏi luyện tập từ chính bài vừa soạn — đây là mối nối tự nhiên nhất của sản phẩm mà hiện chưa có;
- bộ kiểm khung phải dò header bằng regex trên văn bản (`_check_giao_an_pl4`, dòng 105-115) thay vì đọc trường dữ liệu.

### V9 — "Trả lời trong chat" cắt đứt liên kết nháp, không có đường nối lại · **hạn chế sản phẩm**

Khi xoá loại đầu ra (`api/chat.py:483-491`), server xoá luôn `draft_document_id`, `format_document_id`, `draft_status`, `pending_ask_json`. Document vẫn nằm trong thư viện, nhưng **phiên chat không còn con trỏ tới nó và không có API nào gắn lại**. Muốn soạn tiếp bài đó qua chat, giáo viên phải bắt đầu lại từ đầu.

Đây có thể là quyết định sản phẩm cố ý (mỗi phiên đúng một nháp), nhưng cần ghi nhận vì nó là ngõ cụt một chiều đối với người dùng.

### V10 — Vài chỗ lệch nhỏ trong chính module workspace · **vệ sinh mã**

- `_workspace_tool_names` (`api/chat.py:424-432`) thêm `'search_library'` vào tập tên ngay dòng đầu, rồi thêm lại lần nữa có điều kiện ở dưới — nhánh điều kiện vô nghĩa.
- `OUTPUT_TYPES` vẫn là frozenset 5 phần tử (`chat/workspace.py:8`) và là thứ `check_draft_markdown` dùng để hợp lệ hoá (`chat/output_outlines.py:170-172`), trong khi `ACTIVATABLE_OUTPUT_TYPES` chỉ có 1. Hai khái niệm gần giống tên nhau, khác nghĩa, đặt cạnh nhau — nguồn nhầm lẫn cho người sửa sau, và chính là cửa để V2 lọt.
- `_activity_blocks` (`chat/output_outlines.py:91-100`) **nối** các block trùng số HĐ vào cùng một chuỗi. Nếu model đánh nhầm hai hoạt động cùng số "HĐ2", các ô a/b/c/d của hai hoạt động khác nhau sẽ được gộp lại và bộ kiểm coi là đủ — một hoạt động thiếu ô vẫn qua cửa.

---

## 6. Bảng tổng hợp vấn đề

| # | Vấn đề | Mức | Chỗ sửa chính |
|---|---|---|---|
| V1 | FE chào 5 loại, BE nhận 1 → 3 nút trả 422, 1 nút đổi loại âm thầm | **Chặn người dùng** | `workspace-copy.ts:11`, `output-chip.tsx:103` |
| V2 | Nhánh dự phòng gán `tai_lieu` đẩy phiên vào trạng thái loại không hợp lệ, vô hiệu kiểm khung 5512 | **Chặn / sai trạng thái** | `services/chat_document.py:159-160` |
| V3 | `check_draft` không chặn ghi file, kết quả `missing` không lưu, không hiển thị | **Chất lượng** | `api/chat.py:1319-1334` |
| V4 | Không nối nguồn YCCĐ / Chương trình GDPT 2018 — mục tiêu bài dạy do model tự nghĩ | **Nghiệp vụ** | thiết kế — cần tool tra cứu chương trình |
| V5 | Hạ tầng ask-back chết ở prompt, sống ở tool/API/DB/FE; option cũ trong DB gây 422 | Nợ kỹ thuật | `chat/workspace.py`, `api/chat.py:2350+` |
| V6 | Test bảo vệ hành vi của 4 loại đã loại bỏ | Nợ kỹ thuật | `tests/test_chat_workspace_units.py` |
| V7 | Quota kiểm sau khi đã sinh xong nội dung — hết quota vẫn mất token | Chi phí | `api/chat.py:399-411` |
| V8 | Nháp không lưu môn/lớp/tên bài → không thống kê, không nối question_bank | Sản phẩm | `services/chat_document.py:151` |
| V9 | "Trả lời trong chat" cắt liên kết nháp, không có đường nối lại | Sản phẩm | `api/chat.py:483-491` |
| V10 | `OUTPUT_TYPES` vs `ACTIVATABLE_OUTPUT_TYPES` dễ nhầm; nhánh thừa; gộp block HĐ trùng số | Vệ sinh mã | `chat/workspace.py:8-9`, `output_outlines.py:91` |

Thứ tự đề nghị xử lý nếu phải chọn: **V2 → V1 → V7 → V3 → V4** (V2 trước V1 vì nó làm hỏng đúng thứ giá trị nhất của tính năng — bộ kiểm khung — mà không để lại dấu vết nào cho người dùng thấy).

---

## 7. Vùng chưa kiểm chứng

Nói rõ để không tưởng là đã đủ:

- **Chưa chạy runtime.** Toàn bộ kết luận từ đọc mã. Chưa gọi thử API, chưa xem một phiên chat thật, chưa xem file nháp thật sinh ra trông thế nào.
- **Chưa xem log/DB thật.** Không biết hiện có bao nhiêu tổ chức đang bật `chat_workspace`, có bao nhiêu phiên đã rơi vào trạng thái `output_type='tai_lieu'` mô tả ở V2.
- **Chưa đo chất lượng đầu ra.** Không có nhận định nào ở đây về việc model soạn hay hay dở, đúng YCCĐ hay không — chỉ nhận định rằng **không có cơ chế nào bảo đảm điều đó** (V4).
- **Chưa đọc hết FE.** Đã đọc `output-chip.tsx`, `workspace-copy.ts`, `workspace-ui.ts`. Chưa đọc kỹ `workspace-draft-card.tsx`, `use-chat-with-ai.ts`, và luồng SSE phía FE — có thể còn chỗ lệch khác với BE.
- **Chưa đối chiếu với `docs/superpowers/plans/2026-08-25-chat-workspace-output-activation.md`** ở mức từng bước; chỉ đọc phần spec thiết kế. Một số vấn đề ở §5 có thể đã nằm trong kế hoạch dọn dẹp chưa làm.
- **Xuất file:** đã có `GET /api/documents/{id}/export?format=docx|pdf` dùng chung cho mọi Document, nên kế hoạch bài dạy tải về Word được. Chưa kiểm chứng bản DOCX xuất ra có giữ đúng khung bảng của Phụ lục IV không.

---

## 8. Tham chiếu nhanh các file

**Backend** — đường dẫn tính từ `backend/services/api/src/bookforge_api/`

| File | Vai trò |
|---|---|
| `chat/workspace.py` | `OUTPUT_TYPES` (8), `ACTIVATABLE_OUTPUT_TYPES` (9), `normalize_output_type` (13), `infer_output_type_from_label` (106) |
| `chat/output_outlines.py` | khung 5 loại (6-29), `_check_giao_an_pl4` (103), `check_draft_markdown` (162) |
| `chat/workspace_prompt.py` | prompt v11: `WORKSPACE_SHARED`, `_COLD_MASTER`, `_WARM_MASTER`, `_tool_policy` |
| `chat/workspace_tools.py` | `WorkspaceToolset` — `ask_user` (38, đã chết), `set_output` (90), `write_draft` (117), `check_draft` (124), `search_library` (133) |
| `chat/adk_agent.py` | đăng ký tool theo trạng thái (987-1013), nhãn tiến trình tiếng Việt (1118-1121) |
| `api/chat.py` | preflight quota (399), tên tool (424), warm-continue (435), vá phiên (482), ghi nháp (1326), ask-back (2189-2500) |
| `services/chat_document.py` | `persist_workspace_draft` (124), nhánh `tai_lieu` (159-160) |
| `api/documents.py` | `POST /from-chat-message` (464-472) |
| `core/settings.py` | `chat_workspace_enabled` (222) |
| `tests/test_chat_workspace_units.py`, `tests/test_chat_workspace_v1_contract.py` | 2596 dòng test |

**Frontend** — đường dẫn tính từ `frontend/src/`

| File | Vai trò |
|---|---|
| `components/Chat/partial/workspace-copy.ts` | nhãn + thứ tự 5 loại (3-17) |
| `components/Chat/partial/output-chip.tsx` | panel chip, render 5 nút (103-115) |
| `components/Chat/partial/workspace-draft-card.tsx` | thẻ "Đang soạn" |
| `components/Chat/partial/ask-back-card.tsx` | thẻ hỏi lại (đã chết phía BE) |
| `templates/HomePage/partials/workspace-ui.ts` | map session → state UI |
| `api/bookforge-api.ts` | `TWorkspaceOutputType` (292-297) |

**Tài liệu sản phẩm / thiết kế** (repo `bookforge`)

- `docs/product/chat-workspace-v1.md` — đặc tả sản phẩm gốc (còn mô tả 5 loại)
- `docs/superpowers/specs/2026-08-25-chat-workspace-output-activation-design.md` — thiết kế cold/warm, `set_output`
- `docs/superpowers/plans/2026-08-22-chat-workspace-v1-backend.md` / `-frontend.md`, `plans/2026-08-25-chat-workspace-output-activation.md`
