# Tìm hiểu: Hiển thị trạng thái và chi tiết vi phạm quy chế ở tin nhắn chat

**Ngày:** 2026-11-10 · **Cách làm:** Cách 3: Việc thường · **Phía:** Cả hai
**Mốc code:** backend `d6f9a4f2` · frontend `f41905d`
**Spec (nếu có):** Không có

## 0. Việc này sẽ làm gì
**Để làm gì:** Giúp người dùng biết ngay câu trả lời của trợ lý trong khung trò chuyện có tuân thủ các quy chế đang bật hay không thông qua một biểu tượng nhỏ ở góc dưới tin nhắn, kèm tóm tắt khi rê chuột vào và danh sách nội dung vi phạm chi tiết khi nhấn vào.

**Làm xong, ai sẽ thấy gì khác:**
| Vai trò | Trước đây | Sau khi làm |
|---|---|---|
| Giảng viên / Người dùng chat | Khi bật kiểm tra quy chế, hệ thống âm thầm đối chiếu ở bước cuối cùng rồi trả lời luôn; người dùng không biết câu trả lời vừa rồi có đạt quy chế hay đã vướng điều khoản nào. | Ở góc dưới mỗi câu trả lời có thêm biểu tượng nhỏ: **tích xanh** nếu tuân thủ đầy đủ quy chế, hoặc **biểu tượng cảnh báo** nếu phát hiện vi phạm. Rê chuột vào biểu tượng sẽ thấy tóm tắt nhanh; nhấn vào sẽ mở bảng chi tiết các điều khoản và nội dung bị vi phạm. |

**Lần này không làm:** Không thay đổi trang quản lý danh sách Quy chế nhà trường của quản trị viên; không thay đổi giao diện bảng cài đặt bật/tắt quy chế của trợ lý.

**Người dùng và dữ liệu đang có bị ảnh hưởng:** Không. Các tin nhắn cũ trong lịch sử trò chuyện vẫn hiển thị bình thường (những tin nhắn cũ chưa có dữ liệu kiểm tra quy chế chi tiết sẽ không hiện biểu tượng trạng thái quy chế).

**Bạn cần quyết:**
1. **Tình huống 1 — Khi phát hiện câu trả lời có chỗ vi phạm quy chế, nội dung câu trả lời hiển thị thế nào:**
   - (a) Vừa tự động chỉnh lại câu trả lời cho đúng quy chế (như đang chạy), vừa hiện biểu tượng cảnh báo ở góc dưới để người dùng xem lại nội dung nào đã vi phạm và vi phạm quy chế nào → Người dùng nhận được câu trả lời an toàn nhưng vẫn nắm rõ chi tiết lỗi vi phạm đã được phát hiện.
   - (b) Giữ nguyên câu trả lời gốc (không tự sửa câu chữ) và hiện biểu tượng cảnh báo kèm danh sách nội dung vi phạm ở góc dưới → Người dùng đọc nguyên bản câu trả lời và tự xem cảnh báo để đánh giá.
   - **AI khuyên:** a, vì giữ được lớp bảo vệ tự động chỉnh câu trả lời đã làm ở đợt trước, đồng thời bổ sung đầy đủ phần cảnh báo và chi tiết nội dung vi phạm theo yêu cầu mới · **Bạn chốt:** Chọn a
2. **Tình huống 2 — Khi nào hiển thị biểu tượng ở góc dưới tin nhắn:**
   - (a) Chỉ hiện biểu tượng (tích xanh hoặc cảnh báo) ở những câu trả lời thực sự có chạy bước kiểm tra quy chế (tức là tính năng quy chế đang bật và đơn vị có quy chế hoạt động) → Tránh hiện tích xanh ở những cuộc trò chuyện đã tắt kiểm tra quy chế.
   - (b) Luôn hiện biểu tượng ở mọi câu trả lời của trợ lý (nếu tắt kiểm tra quy chế thì mặc định hiện tích xanh) → Mọi tin nhắn đều có biểu tượng nhưng dễ gây hiểu lầm là đã qua kiểm duyệt quy chế.
   - **AI khuyên:** a, vì biểu tượng tích xanh chỉ trung thực và có ý nghĩa khi hệ thống thực sự đã kiểm tra quy chế · **Bạn chốt:** Chọn a
3. **Tình huống 3 — Cách hiển thị chi tiết khi nhấn vào biểu tượng ở góc dưới:**
   - (a) Mở một khung thông tin nổi ngay cạnh biểu tượng ở góc dưới tin nhắn, liệt kê từng quy chế bị vi phạm và nội dung vi phạm cụ thể; bấm ra ngoài hoặc bấm lại biểu tượng là đóng → Xem nhanh tại chỗ, không che khuất màn hình trò chuyện.
   - (b) Mở hộp thoại lớn giữa màn hình để hiển thị chi tiết → Rộng rãi hơn nhưng làm gián đoạn việc đọc cuộc trò chuyện.
   - **AI khuyên:** a, vì thao tác rê chuột xem tổng quan rồi nhấn vào mở khung chi tiết ngay tại góc dưới rất liền mạch · **Bạn chốt:** Chọn a

**Làm xong, bạn sẽ thấy nó chạy thế nào:** Khi bạn trò chuyện với trợ lý (trong lúc quy chế đang bật), ngay khi trợ lý trả lời xong, ở góc dưới câu trả lời sẽ xuất hiện biểu tượng **tích xanh** (nếu không vi phạm) hoặc **cảnh báo màu vàng/cam** (nếu phát hiện vi phạm). Bạn rê chuột vào biểu tượng sẽ thấy dòng tóm tắt (ví dụ: *"Tuân thủ quy chế"* hoặc *"Phát hiện 2 nội dung vi phạm quy chế"* kèm tóm tắt ngắn). Khi bạn nhấn chuột vào biểu tượng, khung chi tiết sẽ mở ra hiển thị rõ tên quy chế, đoạn nội dung vi phạm và lý do vi phạm.

**So với nghiệp vụ đã có:** Giữ: Công tắc bật/tắt quy chế trong cài đặt trợ lý và bước kiểm tra quy chế ở cuối luồng trả lời · Đổi: Bước kiểm tra quy chế ở cuối không chỉ trả về kết quả đạt/sửa ngầm mà trích xuất thêm danh sách nội dung vi phạm và tóm tắt để gửi về giao diện · Thêm: Biểu tượng trạng thái quy chế ở góc dưới tin nhắn (tích xanh / cảnh báo) kèm xem nhanh khi rê chuột và xem chi tiết khi nhấn vào.

---
*(Từ mục 1 trở xuống là phần kỹ thuật cho agent.)*

## 1. Mục tiêu và phạm vi
- **Cần đạt:**
  1. Mở rộng lớp kiểm tra quy chế cuối luồng (`services/school_rules.py`) để trích xuất báo cáo kiểm tra có cấu trúc (`checked`, `has_violation`, `summary`, `violations: [{rule_name, violated_content, reason}]`), đồng thời lưu vào `assistant_message.metadata_json` và trả về trong `ChatMessageResponse` cũng như sự kiện SSE `done`.
  2. Hiển thị icon trạng thái quy chế ở góc dưới tin nhắn trợ lý (`HomePage/index.tsx` / `message-actions.tsx`): không vi phạm hiện icon tick xanh, có vi phạm hiện icon cảnh báo.
  3. Hỗ trợ hover vào icon để xem tổng quan (`summary` + danh sách ngắn) và click vào icon để mở khung chi tiết hiển thị đầy đủ các nội dung bị vi phạm.
- **Không làm:**
  - Không sửa CRUD bảng `school_rules` (`api/school_rules.py`) hay giao diện quản trị Quy chế nhà trường.
  - Không thay đổi giao diện modal bật/tắt `generative_rails` (`AgentSettingsDialogs.tsx`).

## 2. Hiện trạng (kèm `file:dòng`)
- **Luồng hiện tại:**
  1. **Cấu hình bật/tắt quy chế:**
     - Frontend lưu danh sách rail đang bật trong `AgentSettingsDialog` (`frontend/src/components/TiptapEditor/agent-settings/AgentSettingsDialogs.tsx:16-59` và `agent-settings-model.ts:367-420`), gửi lên qua `context_settings.generative_rails` (`frontend/src/api/bookforge-api.ts:460-476`).
     - Backend giải mã các rail đang bật qua `resolve_active_rail_ids` (`backend/services/api/src/bookforge_api/chat/governance.py:78-89`) từ `GENERATIVE_RAIL_CATALOG` (`governance.py:36-72`, gồm `sovereignty`, `academic_style`, `source_grounding`, `academic_integrity`, `school_rules`).
     - Cờ `school_rules_enabled = "school_rules" in active_rail_ids` được tính tại `backend/services/api/src/bookforge_api/api/chat.py:1322-1324, 1524-1526, 2248-2250, 2639-2641`.
  2. **Lớp kiểm tra quy chế ở cuối (`services/school_rules.py`):**
     - Hàm `load_active_school_rules(db, organization_id)` (`backend/services/api/src/bookforge_api/services/school_rules.py:93-100`) nạp các quy chế đang bật của đơn vị khi feature `school_rules` được kích hoạt.
     - Cuối mỗi lượt sinh câu trả lời, backend gọi `verify_answer_against_school_rules` (`school_rules.py:198-226`) hoặc `async_verify_answer_against_school_rules` (`school_rules.py:229-257`) tại 4 điểm:
       - Chat ADK đồng bộ / Specialist Agent: `backend/services/api/src/bookforge_api/chat/adk_agent.py:1289-1315`.
       - Chat ADK streaming SSE / Specialist Agent: `backend/services/api/src/bookforge_api/chat/adk_agent.py:1655-1704`.
       - Free chat (chat không chọn tài liệu): `backend/services/api/src/bookforge_api/api/chat.py:1524-1572`.
       - Editor chat trong Canvas: `backend/services/api/src/bookforge_api/chat/editor_agent.py:528-541`.
  3. **Giao diện góc dưới tin nhắn trợ lý (`HomePage/index.tsx` & `message-actions.tsx`):**
     - Mỗi tin nhắn trợ lý trong `frontend/src/templates/HomePage/index.tsx:653-736` render phần nội dung markdown, sau đó ở thanh góc dưới (`index.tsx:703-736`) bên trái là `ChatMessageFeedbackBar` (`frontend/src/components/Chat/partial/chat-message-feedback.tsx:78-375`) và bên phải là `MessageActions` (`frontend/src/components/Chat/partial/message-actions.tsx:28-92`) chứa các nút icon `size-8` (Sao chép, Chỉnh sửa câu trả lời).
- **Chỗ cần sửa / nguyên nhân:**
  - `backend/services/api/src/bookforge_api/services/school_rules.py:127-185` — Prompt `_build_verifier_instructions` và hàm `parse_school_rules_verification_output` hiện chỉ yêu cầu LLM trả về `[SCHOOL_RULES_OK]` hoặc `[SCHOOL_RULES_REVISED]\n<câu trả lời đã sửa>`, chỉ trả ra `(was_revised: bool, final_answer: str)` và làm mất toàn bộ thông tin: vi phạm quy chế nào, đoạn nội dung nào trong bản nháp bị vi phạm, và tóm tắt lỗi vi phạm:
    ```python
    def parse_school_rules_verification_output(
        raw_output: str,
        draft_answer: str,
    ) -> tuple[bool, str]:
        cleaned = str(raw_output or "").strip()
        if not cleaned:
            return False, draft_answer
        if cleaned.startswith(_VERIFIER_OK_PREFIX):
            return False, draft_answer
        if cleaned.startswith(_VERIFIER_REVISED_PREFIX):
            revised = cleaned[len(_VERIFIER_REVISED_PREFIX) :].strip()
            return (True, revised) if revised else (False, draft_answer)
        return False, draft_answer
    ```
  - `backend/services/api/src/bookforge_api/chat/adk_agent.py:478-507, 1289-1315, 1655-1704` và `backend/services/api/src/bookforge_api/api/chat.py:1524-1648, 1734-2033` — Chưa truyền kết quả kiểm tra quy chế (`school_rules_report`) vào `assistant_message.metadata_json`, `ChatMessageResponse` (`schemas/chat.py:173-204`), hay payload SSE `done`.
  - `frontend/src/templates/HomePage/partials/use-chat-with-ai.ts:56-153` và `frontend/src/templates/HomePage/index.tsx:703-736` — Chưa đọc dữ liệu kiểm tra quy chế từ response/SSE và chưa có component hiển thị icon trạng thái (tick xanh / cảnh báo) kèm hover tổng quan + click xem chi tiết ở góc dưới tin nhắn.

## 3. Kiểm tra spec (chỉ việc có spec, xem `spec-check.md`; việc khác ghi "Không áp dụng")
Không áp dụng.

## 4. Điểm va chạm
- **Test đang khoá hành vi cũ:**
  - `backend/services/api/tests/test_school_rules.py:194-324` (`test_chat_and_agent_enforce_school_rules_final_check`) đang gọi trực tiếp `parse_school_rules_verification_output("[SCHOOL_RULES_OK]", "Draft")` và `parse_school_rules_verification_output("[SCHOOL_RULES_REVISED]\nĐã chỉnh theo quy chế.", "Draft")` kỳ vọng kết quả trả về là tuple 2 phần tử `(was_revised, final_answer)`, đồng thời mock response của verifier với chuỗi `[SCHOOL_RULES_REVISED]\n...`.
  - Vì vậy, cần giữ nguyên chữ ký và giá trị trả về của `parse_school_rules_verification_output(raw_output, draft_answer) -> tuple[bool, str]`, đồng thời bổ sung hàm/cấu trúc chi tiết (ví dụ `SchoolRulesVerificationReport` + `parse_school_rules_verification_report`) tương thích ngược với cả định dạng `[SCHOOL_RULES_REVISED]` cũ lẫn định dạng có kèm block chi tiết vi phạm mới.
- **Giao tiếp backend ↔ frontend & Lịch sử chat:**
  - Khi tải lại trang (`getChatMessages`), frontend dựng lại danh sách tin nhắn từ `TChatMessageResponse` (`api/chat.py:1651-1705`). Do đó `school_rules_report` phải được lưu bền vững trong `assistant_message.metadata_json["school_rules_report"]` và được serialize ra `ChatMessageResponse` để cả lúc vừa chat xong (sync/SSE) lẫn khi F5 tải lại lịch sử đều hiển thị đúng icon góc dưới.
- **Streaming SSE (`adk_agent.py:1655-1704`):**
  - Trong luồng SSE, khi verifier phát hiện vi phạm, sự kiện `answer_replace` đã được bắn xuống để cập nhật nội dung câu trả lời; báo cáo `school_rules_report` cần được đính kèm vào kết quả cuối (`finalize_chat_turn` -> `done` event `assistant_message`) để UI hiển thị icon ngay khi kết thúc stream.

## 5. Phương án đề xuất
1. **Phía Backend (`services/school_rules.py`, `schemas/chat.py`, `adk_agent.py`, `api/chat.py`):**
   - Định nghĩa cấu trúc dữ liệu `SchoolRulesViolationItem` (`rule_id`, `rule_name`, `violated_content`, `reason`) và `SchoolRulesReport` (`checked: bool`, `has_violation: bool`, `was_revised: bool`, `summary: str`, `violations: list[SchoolRulesViolationItem]`).
   - Cập nhật prompt verifier trong `_build_verifier_instructions` (`school_rules.py:127-149`) để khi phát hiện vi phạm, LLM xuất block thông tin vi phạm (JSON/tag cấu trúc gồm tóm tắt tổng quan và danh sách từng mục vi phạm: tên quy chế, nội dung bị vi phạm trong câu trả lời, lý do vi phạm) kèm nội dung câu trả lời (tuỳ theo quyết định ở Tình huống 1). Nếu LLM trả định dạng `[SCHOOL_RULES_REVISED]` ngắn gọn (như trong unit test cũ), parser tự động tạo báo cáo fallback (`has_violation=True`, `summary="Phát hiện nội dung cần điều chỉnh theo quy chế nhà trường"`, `violated_content=draft_answer`).
   - Lưu `school_rules_report` vào `assistant_message.metadata_json` trong `_run_free_chat` (`api/chat.py:1524-1648`) và `finalize_chat_turn` (`api/chat.py:1734-2033`), đồng thời expose trường `school_rules_report` trên `ChatMessageResponse` (`schemas/chat.py:173-204`).
2. **Phía Frontend (`bookforge-api.ts`, `use-chat-with-ai.ts`, `RuleComplianceIndicator`, `HomePage/index.tsx`):**
   - Bổ sung kiểu `TSchoolRulesReport` và `TSchoolRulesViolationItem` vào `frontend/src/api/bookforge-api.ts` và `TChatMessageItem` trong `use-chat-with-ai.ts`.
   - Tạo component hiển thị trạng thái quy chế ở góc dưới tin nhắn (cùng hàng với thanh action góc dưới tại `HomePage/index.tsx:703-736` và `ready-document-view.tsx:242`):
     - Khi `checked === true` và `!has_violation`: hiển thị nút icon tick xanh (`emerald`), hover hiện tooltip tổng quan *"Tuân thủ quy chế nhà trường"*, click mở popover xác nhận đã kiểm tra và không có vi phạm.
     - Khi `checked === true` và `has_violation === true`: hiển thị nút icon cảnh báo (`amber`), hover hiện tooltip tổng quan (`summary` + số lượng vi phạm), click mở popover chi tiết liệt kê từng quy chế bị vi phạm, đoạn nội dung bị vi phạm (`violated_content`) và lý do/hướng xử lý (`reason`).

## 6. Câu hỏi kỹ thuật còn mở
Đã đưa lên mục **Bạn cần quyết** ở Mục 0 (3 tình huống về: giữ hay bỏ tự động sửa câu chữ khi vi phạm, điều kiện hiển thị icon khi tắt kiểm tra quy chế, và kiểu hiển thị popover hay modal khi nhấn vào icon).
