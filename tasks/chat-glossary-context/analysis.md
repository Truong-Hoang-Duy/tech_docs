# Tìm hiểu: Tích hợp Từ điển SGK & Đường ray tạo sinh cho phần Chat (Backend & Handoff FE)

**Ngày:** 2026-11-07 · **Cách làm:** Cách 3: Việc thường · **Phía:** BE
**Mốc code:** backend `e0518935` · frontend `08819f6`
**Spec (nếu có):** Không có

## 0. Việc này sẽ làm gì
**Để làm gì:** Xây dựng toàn bộ phần xử lý phía máy chủ (Backend) để cung cấp **Bộ từ điển Sách giáo khoa (SGK)** và **Đường ray tạo sinh** (các quy tắc kiểm soát nội dung có sẵn trong hệ thống) cho phần Chat chính và 5 Agent chuyên biệt; đồng thời xuất **Tài liệu bàn giao cho Frontend (FE Handoff)** để đội ngũ làm giao diện chỉ việc nối vào và hiển thị lên màn hình.

**Làm xong, ai sẽ thấy gì khác:**
| Vai trò | Trước đây | Sau khi làm |
|---|---|---|
| Giáo viên / Người dùng ở trang Chat chính | 5 Agent chuyên biệt (Phiếu điền khuyết, Ma trận đề, Tạo đề kiểm tra, Dịch học thuật, Thiết kế Infographic) và phần Chat chưa có bộ từ điển thuật ngữ SGK nên đôi khi dùng từ chung chung; các quy tắc kiểm soát nội dung chạy ngầm cố định, không bật/tắt được theo phiên chat. | Hệ thống có sẵn kho Từ điển SGK (10 môn cấp THPT + bộ từ điển Chung) và danh mục các quy tắc Đường ray tạo sinh; khi gửi tin nhắn hoặc dùng 5 Agent, máy chủ tự động tra cứu đúng bộ từ điển đang bật và chỉ áp dụng các quy tắc Đường ray người dùng chọn. |
| Lập trình viên giao diện (Frontend) | Chưa có đầu mối lấy danh sách từ điển, danh sách quy tắc Đường ray tạo sinh, trạng thái mặc định và nơi gửi cấu hình khi bấm nút **Áp dụng** trên cửa sổ **Cài đặt ngữ cảnh & công cụ**. | Có đầy đủ đầu mối lấy danh mục, lưu cấu hình theo từng cuộc trò chuyện và gửi kèm tin nhắn, cùng tài liệu bàn giao chi tiết (dữ liệu mẫu, chữ hiển thị trên màn hình, bảng mã) để ghép thẳng vào giao diện. |

**Lần này không làm:**
- Không sửa trực tiếp mã nguồn bên phía giao diện (`frontend`) và không đụng tới khung chat trong trình soạn thảo văn bản (Canvas).
- Không tự nghĩ thêm quy tắc kiểm soát mới ngoài các quy tắc đã có sẵn trong hệ thống.

**Người dùng và dữ liệu đang có bị ảnh hưởng:** Không. Các cuộc trò chuyện cũ và ứng dụng đang chạy không bị ảnh hưởng; nếu giao diện chưa truyền cấu hình mới lên thì máy chủ tự động dùng cấu hình mặc định (bật sẵn Từ điển Chung và đầy đủ các quy tắc Đường ray như hiện tại).

**Bạn cần quyết:**
1. **Tình huống 1 — Danh sách các quy tắc trả về trong mục "Đường ray tạo sinh" để hiển thị lên trình duyệt:**
   Hiện trong hệ thống đang có sẵn 5 quy tắc kiểm soát nội dung: *(1) Tôn trọng chủ quyền biển đảo Việt Nam, (2) Phong cách học thuật & sư phạm chuẩn mực, (3) Bám sát nguồn tài liệu (không bịa trích dẫn), (4) Liêm chính học thuật (không giải hộ đề thi/không ra quyết định kỷ luật thay nhà trường), (5) Tuân thủ quy chế nhà trường*.
   - (a) Trả về gọn **4 quy tắc tiêu biểu**: *Tôn trọng chủ quyền biển đảo Việt Nam*, *Phong cách học thuật & sư phạm*, *Bám sát nguồn tài liệu (không bịa trích dẫn)*, *Tuân thủ quy chế nhà trường*.
   - (b) Trả về đầy đủ **tất cả 5 quy tắc** để giao diện hiển thị thành 5 ô tích.
   - **AI khuyên:** (a), vì gọn gàng, khớp bố cục cửa sổ **Cài đặt ngữ cảnh & công cụ** trên thiết kế dự kiến · **Bạn chốt:** **(b) — Trả về đầy đủ tất cả 5 quy tắc**

2. **Tình huống 2 — Có cho phép tắt quy tắc "Tôn trọng chủ quyền biển đảo Việt Nam" không:**
   - (a) Cho phép người dùng bật/tắt tự do **tất cả** các quy tắc trong mục Đường ray tạo sinh (kể cả quy tắc chủ quyền biển đảo) theo đúng thao tác tích chọn trên trình duyệt.
   - (b) Đánh dấu quy tắc *Tôn trọng chủ quyền biển đảo Việt Nam* là "luôn bật" (`locked: true`) để giao diện hiển thị ở trạng thái khóa bật và máy chủ luôn giữ quy tắc này, còn các quy tắc khác cho bật/tắt tự do.
   - **AI khuyên:** (a) nếu bạn muốn cho phép bật/tắt toàn bộ các mục trên trình duyệt như yêu cầu vừa nêu, hoặc (b) nếu muốn khóa an toàn pháp lý · **Bạn chốt:** **(a) — Cho phép bật/tắt tự do tất cả các quy tắc**

3. **Tình huống 3 — Danh sách môn học trả về trong mục "Từ điển sư phạm" cho giao diện:**
   Dữ liệu từ điển đã biên tập hiện có 10 môn cấp THPT (*Toán, Ngữ văn, Vật lí, Hóa học, Sinh học, Lịch sử, Địa lí, Giáo dục kinh tế và pháp luật, Tiếng Anh, Tin học*), còn trên ảnh thiết kế hiển thị dòng đầu gồm: *Chung (sư phạm, giáo dục), Toán học, Ngữ văn, Khoa học tự nhiên, Khác...*
   - (a) Trả về đúng cấu trúc trên ảnh thiết kế: nhóm hiển thị chính gồm *Chung (sư phạm, giáo dục)*, *Toán học*, *Ngữ văn*, *Khoa học tự nhiên* (nhóm gộp: khi bật sẽ tự động kích hoạt 3 bộ từ điển *Vật lí, Hóa học, Sinh học*), và nhóm mở rộng trong menu *Khác...* gồm các môn lẻ (*Vật lí, Hóa học, Sinh học, Lịch sử, Địa lí, GDKT&PL, Tiếng Anh, Tin học*).
   - (b) Không dùng nhóm gộp *Khoa học tự nhiên*, trả về thẳng 10 môn cấp THPT + bộ từ điển *Chung* (4 mục đầu hiện chính, các môn còn lại nằm trong *Khác...*).
   - **AI khuyên:** (a), vì vừa khớp 100% với ảnh thiết kế giao diện của bạn, vừa khai thác đủ 10 bộ từ điển môn học đang có · **Bạn chốt:** **(a) — Khớp ảnh thiết kế: Chung, Toán học, Ngữ văn, Khoa học tự nhiên (gộp Vật lí, Hóa học, Sinh học) và menu Khác... gồm các môn lẻ**

**Làm xong, bạn sẽ thấy nó chạy thế nào:**
Khi gọi vào máy chủ lấy tùy chọn trang Chat, máy chủ trả về đầy đủ danh sách Từ điển, danh sách Đường ray tạo sinh và cấu hình mặc định. Khi gửi tin nhắn Chat hoặc gọi 1 trong 5 Agent chuyên biệt kèm cấu hình Từ điển và Đường ray, câu trả lời và học liệu sinh ra (Phiếu điền khuyết, Ma trận đề, Đề kiểm tra, Bản dịch học thuật, Infographic) sẽ dùng đúng thuật ngữ chuẩn SGK của môn đã chọn và tuân thủ đúng các quy tắc Đường ray đang bật. Cuối cùng, bạn sẽ nhận được file **Tài liệu bàn giao cho Frontend (FE Handoff)** tại đường dẫn bạn chọn.

**So với nghiệp vụ đã có:**
- **Giữ:** Toàn bộ luồng hoạt động hiện tại của trang Chat và 5 Agent chuyên biệt khi người dùng không đổi cài đặt.
- **Đổi:** Tách các quy tắc kiểm soát đang chạy ngầm cố định thành danh sách có mã định danh để trình duyệt hiển thị và bật/tắt theo từng phiên chat; nâng cấp 5 Agent chuyên biệt để tra cứu thuật ngữ chuẩn từ Từ điển SGK trước khi sinh nội dung.
- **Thêm:** Kho dữ liệu Từ điển SGK (10 môn + từ điển Chung), thông tin cấu hình ngữ cảnh trên API Chat, và tài liệu bàn giao kỹ thuật cho Frontend.

---
*(Từ mục 1 trở xuống là phần kỹ thuật cho agent.)*

## 1. Mục tiêu và phạm vi
- **Cần đạt (Chỉ sửa `backend`):**
  1. Đóng gói 29 tệp dữ liệu từ điển SGK Schema v2.3 từ `review-station/data/glossary/units/*.json` (10 môn lớp 10–12, lọc sạch tên bộ sách/NXB qua `strip_brand_watermarks`) + bộ từ điển `"Chung (sư phạm, giáo dục)"` (`general`) vào SQLite + FTS5 (`data/school_glossary.jsonl.gz` → `school_glossary.sqlite` qua `services/school_glossary.py`).
  2. Mở rộng API `GET /api/chat/modes` (`ChatModeOptionsResponse`), API phiên chat (`POST /api/chat/sessions`, `PATCH /api/chat/sessions/{session_id}`, `GET /api/chat/sessions/{session_id}`) và API gửi tin nhắn (`POST /api/chat/sessions/{session_id}/messages`, `/messages/stream`) để cung cấp danh mục và nhận/lưu `context_settings` (gồm `glossary` và `generative_rails`).
  3. Kết nối `context_settings` vào bộ kiểm soát quy tắc (`chat/governance.py`, `services/governance/policy_guard.py`, `services/school_rules.py`) và bơm ngữ cảnh thuật ngữ SGK vào `chat/adk_agent.py` cùng 5 Agent chuyên biệt (`phieu_dien_khuyet_agent.py`, `ma_tran_de_agent.py`, `de_kiem_tra_agent.py`, `dich_hoc_thuat_agent.py`, `infographic_agent.py`).
  4. Chuẩn bị đầy đủ nội dung kỹ thuật để ở bước hoàn tất (Giai đoạn 2) xuất **Tài liệu Handoff cho Frontend** theo đường dẫn bạn chỉ định.
- **Không làm:**
  - Không sửa bất kỳ file nào trong repo `frontend/`.
  - Không sửa luồng chat trong trình soạn thảo Canvas (`chat/editor_agent.py`).
  - Không đẻ thêm quy tắc kiểm soát mới ngoài các quy tắc đã có trong hệ thống.

## 2. Hiện trạng (kèm `file:dòng`)
- **Luồng hiện tại ở Backend & Nguồn dữ liệu:**
  1. **Nguồn dữ liệu Từ điển tại `review-station`:**
     - `review-station/glossary_station.py:94-163` và `review-station/dict_md.py:121-190`: Đọc 29 file JSON từ điển Schema v2.3 tại `review-station/data/glossary/units/*.json` (gồm `toan_10..12`, `ngu_van_10..12`, `vat_ly_10..12`, `hoa_10..12`, `sinh_10..12`, `lich_su_10..12`, `dia_10..12`, `gd_kt_va_pl_10,12`, `tieng_anh_10,12`, `tin_hoc_10`, `tin_hoc_khmt_11..12`, `tin_hoc_thud_12`).
     - Mỗi file gồm `dictionaries[]` (`conventions` — quy ước chương) và `terms[]` (`id`, `term`, `aliases`, `english`, `notation`, `meaning`, `usage_context`, `scope`, `source_status`, `location`).
  2. **Kho tri thức mặc định hiện tại (`bookforge_default_kb.py`):**
     - `backend/services/api/src/bookforge_api/services/bookforge_default_kb.py:140-185, 298-391, 628-660`: Đã có hàm `strip_brand_watermarks`, `parse_subject_and_grade` và cơ chế tự bung SQLite + FTS5 từ file nén `.jsonl.gz`, nhưng mới chỉ chứa 3 bảng `books`, `lessons`, `atomic_units`, chưa có dữ liệu từ điển Schema v2.3.
  3. **API Chat & Schema hiện tại (`schemas/chat.py`, `models/document.py`, `api/chat.py`):**
     - `backend/services/api/src/bookforge_api/schemas/chat.py:16-46, 84-106, 169-177`:
       - `ChatModeOptionsResponse` (`schemas/chat.py:169-177`) trả về từ `GET /api/chat/modes` (`api/chat.py:2580-2606`) hiện có `assistant_name`, `modes`, `experts`, `agents`, `workspace_enabled`.
       - `ChatSessionCreateRequest` (`schemas/chat.py:16-23`), `ChatSessionUpdateRequest` (`schemas/chat.py:25-33`), `ChatSessionListItem` / `ChatSessionResponse` (`schemas/chat.py:84-106`) và model `ChatSession` (`models/document.py:294-325`) chưa lưu cấu hình `context_settings` của phiên chat.
       - `ChatMessageCreateRequest` (`schemas/chat.py:35-46`) có `ConfigDict(extra='forbid')` với `message`, `attachment_ids`, `legal_mode`, `model_id`, `agent_id`; chưa có `context_settings`.
  4. **Các quy tắc kiểm soát đang chạy ngầm (`governance.py`, `policy_guard.py`, `workspace_prompt.py`, `school_rules.py`):**
     - `backend/services/api/src/bookforge_api/chat/governance.py:25-36, 89-110`: Hàm `build_governance_instruction(role_key, surface)` ghép cứng `GOVERNANCE_INSTRUCTION` + `_lt705_block()` + `_STUDENT_BLOCK`/`_TEACHER_BLOCK`:
       - Chủ quyền biển đảo Việt Nam (`governance.py:27`, `detect_governance_topics` tại `governance.py:37-60`).
       - Bám sát nguồn tài liệu & chống bịa đặt trích dẫn (`governance.py:28, 31` & `adk_agent.py:1760-1766`).
       - Phong cách học thuật & sư phạm chuẩn mực (`governance.py:29` & `workspace_prompt.py:33-52`).
       - Liêm chính học thuật & Quyết định 705 (`governance.py:75-98` & `policy_guard.py:120-253`).
       - Bảo mật dữ liệu cá nhân & mã nội bộ (`governance.py:30, 33` & `policy_guard.py:162-183`).
     - `backend/services/api/src/bookforge_api/services/school_rules.py:93-124, 168-227` và `api/chat.py:1440-1473`: Quy chế nhà trường (`load_active_school_rules`, `build_school_rules_instruction`, `verify_answer_against_school_rules`).
  5. **5 Agent chuyên biệt và ADK Chat (`adk_agent.py` & `*_agent.py`):**
     - `backend/services/api/src/bookforge_api/chat/adk_agent.py:1749-1941, 1969-2088`: `_agent_instruction` và `run_adk_chat` lắp ghép system instruction và chạy tool cho Chat chung + 5 Agent.
     - `backend/services/api/src/bookforge_api/chat/phieu_dien_khuyet_agent.py:293-360, 887-970, 1079-1178`: Tạo Phiếu điền khuyết.
     - `backend/services/api/src/bookforge_api/chat/ma_tran_de_agent.py:520-585, 604-700, 747-901`: Tạo Ma trận đề kiểm tra.
     - `backend/services/api/src/bookforge_api/chat/de_kiem_tra_agent.py:143-162, 700-920`: Tạo Đề kiểm tra từ Ngân hàng câu hỏi.
     - `backend/services/api/src/bookforge_api/chat/dich_hoc_thuat_agent.py:239-302` & `adk_agent.py:1889-1890`: Tạo Bản dịch học thuật.
     - `backend/services/api/src/bookforge_api/chat/infographic_agent.py:1178-1235, 1355-1454, 1576-1682`: Tạo Infographic học tập.

## 3. Kiểm tra spec
Không áp dụng (Cách 3: Việc thường — chưa có spec sẵn).

## 4. Điểm va chạm
1. **Test khóa cứng `GOVERNANCE_INSTRUCTION` khi gọi mặc định:**
   - `backend/services/api/tests/test_governance_instruction.py:25-28`, `test_chat_page_awareness.py:980`, và `test_expert_prompt.py:48, 117, 145` đều kiểm tra `assert instructions.startswith(GOVERNANCE_INSTRUCTION)`.
   - **Cách xử lý:** Khi `context_settings` là `None` hoặc giữ nguyên mặc định (bật đủ toàn bộ đường ray), `build_governance_instruction` trả về chuỗi bắt đầu bằng đúng `GOVERNANCE_INSTRUCTION` như cũ; chỉ khi người dùng chủ động tắt từng quy tắc trong `generative_rails` mới lọc bỏ đoạn quy tắc tương ứng. Khối ngữ cảnh từ điển `<school_glossary>` được nối ở phần dưới của `_agent_instruction` (`adk_agent.py:1934-1940`).
2. **Test khóa cứng số lượng bản ghi trong `bookforge_default_kb.sqlite`:**
   - `backend/services/api/tests/test_bookforge_default_kb.py:54-99` kiểm tra `books == 53`, `lessons == 1271` và quét `_FORBIDDEN_BRAND_RE`.
   - **Cách xử lý:** Đóng gói từ điển thành bundle độc lập `backend/services/api/src/bookforge_api/data/school_glossary.jsonl.gz` và SQLite riêng `school_glossary.sqlite` trong `services/school_glossary.py`, dùng lại `strip_brand_watermarks` và `parse_subject_and_grade` của `bookforge_default_kb.py`.
3. **Schema `ChatMessageCreateRequest` đặt `extra='forbid'` & OpenAPI contract test:**
   - `backend/services/api/src/bookforge_api/schemas/chat.py:36` có `ConfigDict(extra='forbid')` và `test_api_contract_generator.py:14` kiểm tra `ChatModeOptionsResponse`.
   - **Cách xử lý:** Thêm trường tùy chọn `context_settings: ChatContextSettings | None = None` vào `ChatMessageCreateRequest`, `ChatSessionCreateRequest`, `ChatSessionUpdateRequest`, `ChatSessionListItem`, và thêm `context_options: ChatContextOptions = Field(default_factory=...)` vào `ChatModeOptionsResponse` để hoàn toàn tương thích ngược.
4. **Lưu `context_settings` theo phiên Chat mà không làm gãy DB hiện có:**
   - Có thể lưu `context_settings` của phiên chat thông qua cột JSON hoặc tái sử dụng cấu trúc lưu trữ phiên chat hiện có kèm migration Alembic an toàn (`nullable=True`), hoặc kết hợp lưu trên `ChatSession` + nhận trực tiếp từ `ChatMessageCreateRequest.context_settings`.

## 5. Phương án đề xuất (Backend & Cấu trúc Tài liệu Handoff cho Frontend)

### 5.1. Kiến trúc Backend (`services/school_glossary.py` + `chat/` + `api/chat.py`)
1. **Kho Từ điển SGK (`services/school_glossary.py` & `data/school_glossary.jsonl.gz`):**
   - Nạp 29 file `review-station/data/glossary/units/*.json` + bộ từ điển `"Chung (sư phạm, giáo dục)"` (`id: "chung"`) vào `school_glossary.sqlite` (FTS5 trên `term`, `aliases`, `english`, `notation`, `meaning`).
   - Hỗ trợ 2 chế độ truy xuất:
     - **Theo bài học/chương (`lookup_lesson_glossary`)**: Khi xác định được môn, lớp, bài/chương (trong `phieu_dien_khuyet_agent.py`, `ma_tran_de_agent.py`, `infographic_agent.py`), trả về toàn bộ thuật ngữ của bài (`in_source`, `described`, `out_of_source`, `scope`) kèm `conventions` của chương.
     - **Theo văn bản/câu hỏi (`lookup_text_glossary`)**: Khi dịch học thuật (`dich_hoc_thuat_agent.py`), rút câu hỏi đề kiểm tra (`de_kiem_tra_agent.py`) hoặc hỏi đáp tự do (`adk_agent.py`), đối sánh văn bản với các bộ từ điển đang bật để lấy Top 15–25 thuật ngữ khớp nhất.
2. **Cơ chế bật/tắt Đường ray tạo sinh (`chat/governance.py`, `policy_guard.py`, `school_rules.py`):**
   - Mỗi quy tắc có sẵn được gắn mã định danh (`rule_id`), tiêu đề hiển thị (`label`), mô tả (`description`), trạng thái mặc định (`default_enabled: true`).
   - Khi `generative_rails.enabled == False` hoặc một `rule_id` không nằm trong `generative_rails.rule_ids`, hệ thống bỏ qua quy tắc đó trong system prompt, preflight check (nếu được phép tắt) và bước kiểm duyệt `school_rules`.

### 5.2. Nghiên cứu nội dung Tài liệu Handoff cho Frontend (sẽ tạo khi hoàn tất)
Theo chuẩn các file handoff hiện có trong dự án (`backend/docs/api/wallet-fe-handoff.md`, `backend/docs/api/exam-assignments-handoff.md`), tài liệu **Frontend Handoff** cho task này cần bao gồm **6 phần cốt lõi** để lập trình viên FE đọc là làm được ngay:

1. **Tổng quan Luồng Nghiệp vụ & Trạng thái Giao diện (UI State & User Flow):**
   - Cách khởi tạo trạng thái mặc định từ `GET /api/chat/modes` (`context_options.default_settings`).
   - Cách hiển thị **2 Pill tóm tắt** trên thanh ngữ cảnh của ô nhập Chat (`[📖 Từ điển: Toán học]`, `[🛡 Đường ray: Sư phạm >]`): quy tắc ghép tên khi chọn 1 môn, nhiều môn, hoặc khi tắt.
   - Cách hoạt động của nút **Khôi phục mặc định**, **Hủy**, **Áp dụng** trên modal **Cài đặt ngữ cảnh & công cụ**.
   - Quy tắc đồng bộ nhóm gộp (ví dụ khi tích **Khoa học tự nhiên** thì xử lý các môn thành phần *Vật lí, Hóa học, Sinh học* trong menu *Khác...* như thế nào).
2. **Đặc tả Chi tiết API Endpoints & JSON Payload mẫu:**
   - **`GET /api/chat/modes`**: JSON mẫu trả về trường mới `context_options`:
     - `glossaries`: Danh sách các bộ từ điển (`id`, `label`, `description`, `is_primary`, `expanded_subject_ids`, `default_selected`).
     - `generative_rails`: Danh sách các quy tắc Đường ray tạo sinh có sẵn trong hệ thống (`id`, `label`, `description`, `locked`, `default_selected`).
     - `default_settings`: Cấu hình mặc định chuẩn (`glossary_enabled`, `glossary_ids`, `rails_enabled`, `rail_ids`).
   - **`POST /api/chat/sessions/{session_id}/messages/stream` & `/messages`**: Cách truyền `context_settings` kèm `agent_id` trong body request; cách đọc thông tin ngữ cảnh đã áp dụng trong `assistant_message.metadata.context_settings` và `thinking_steps` (SSE frame `status`).
   - **`POST /api/chat/sessions`, `PATCH /api/chat/sessions/{session_id}`, `GET /api/chat/sessions/{session_id}`**: Cách lưu và khôi phục `context_settings` khi người dùng chuyển qua lại giữa các cuộc trò chuyện trong lịch sử.
3. **Bảng Nội dung Chữ hiển thị trên Giao diện (UI Copy Deck chuẩn):**
   - Toàn bộ tiêu đề, mô tả phụ, nhãn nút bấm, nhãn từng bộ từ điển và từng quy tắc Đường ray tạo sinh khớp với thiết kế để FE không phải tự đặt câu chữ.
4. **TypeScript Interfaces & API Helper mẫu cho FE:**
   - Cung cấp sẵn code khai báo TypeScript (`TChatGlossaryOption`, `TChatRailOption`, `TChatContextSettings`, `TChatContextOptions`) tương thích trực tiếp với `frontend/src/api/bookforge-api.ts` và `frontend/src/hooks/use-chat-modes.ts`.
5. **Bảng Mã lỗi & Xử lý Tình huống Biên (Edge Cases):**
   - Xử lý khi gửi `glossary_ids` hoặc `rail_ids` không hợp lệ, khi tắt toàn bộ từ điển, hoặc khi chọn Agent chuyên biệt đi kèm bộ từ điển.
6. **Gợi ý Danh sách File bên Frontend cần chỉnh sửa:**
   - Chỉ dẫn cụ thể các vị trí cần nối ở `frontend` (`src/api/bookforge-api.ts`, `src/hooks/use-chat-modes.ts`, `src/templates/HomePage/index.tsx`, `src/templates/HomePage/partials/use-chat-with-ai.ts`, `src/components/PanelMessage/index.tsx`) để FE tiết kiệm thời gian tìm kiếm.

## 6. Câu hỏi kỹ thuật còn mở
Đã đưa toàn bộ 3 quyết định nghiệp vụ lên Mục 0 ("Bạn cần quyết").
