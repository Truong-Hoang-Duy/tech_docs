# Kế hoạch: Hiển thị trạng thái và chi tiết vi phạm quy chế ở tin nhắn chat

**Ngày:** 2026-11-10 · **Cách làm:** Cách 3: Việc thường · **Phía:** Cả hai
**Trạng thái:** DONE
**Mốc code:** backend `d6f9a4f2` · frontend `f41905d` · **Nhánh:** `feat/rule-violation-indicator`

## 1. Mục tiêu và quyết định đã chốt
- **Mục tiêu:**
  1. Mở rộng bước kiểm tra quy chế cuối luồng (`services/school_rules.py`) để khi đối chiếu câu trả lời với Quy chế nhà trường đang bật, hệ thống trích xuất báo cáo kiểm tra có cấu trúc (`school_rules_report` gồm `checked`, `has_violation`, `was_revised`, `summary`, `violations: [{rule_id, rule_name, violated_content, reason}]`), lưu vào `assistant_message.metadata_json` và trả về qua API Chat (`ChatMessageResponse` & sự kiện SSE `done`).
  2. Hiển thị biểu tượng trạng thái quy chế ở góc dưới tin nhắn trợ lý (`HomePage/index.tsx` và `ready-document-view.tsx`): tích xanh khi tuân thủ quy chế (`has_violation=false`), biểu tượng cảnh báo khi phát hiện vi phạm (`has_violation=true`), kèm xem nhanh tổng quan khi rê chuột (hover) và mở khung nổi (popover) xem chi tiết các nội dung bị vi phạm khi nhấn chuột (click).
- **Quyết định đã chốt** (không tự đổi khi làm):
  1. **Tình huống 1 (Chọn a — Xử lý câu trả lời khi phát hiện vi phạm):** Vừa tự động chỉnh lại câu trả lời cho đúng quy chế (giữ nguyên lớp bảo vệ làm sạch câu trả lời hiện có), vừa hiện biểu tượng cảnh báo ở góc dưới để người dùng xem lại đoạn nội dung nào trong bản gốc đã vi phạm và vi phạm quy chế nào.
  2. **Tình huống 2 (Chọn a — Điều kiện hiển thị biểu tượng ở góc dưới):** Chỉ hiện biểu tượng (tích xanh hoặc cảnh báo) ở những câu trả lời thực sự có chạy bước kiểm tra quy chế (`checked=true`, tức tính năng quy chế đang bật và đơn vị có quy chế hoạt động). Nếu tắt kiểm tra quy chế hoặc đơn vị chưa cấu hình quy chế thì ẩn biểu tượng.
  3. **Tình huống 3 (Chọn a — Cách hiển thị chi tiết khi nhấn vào biểu tượng):** Mở khung thông tin nổi (popover) ngay cạnh biểu tượng ở góc dưới tin nhắn, liệt kê từng quy chế bị vi phạm, đoạn nội dung bị vi phạm cụ thể và lý do vi phạm; bấm ra ngoài hoặc bấm lại biểu tượng là đóng.
- **Tài liệu trong `backend/`:** `backend/docs/superpowers/specs/2026-11-10-rule-violation-indicator-design.md` và `backend/docs/superpowers/plans/2026-11-10-rule-violation-indicator.md`.

## 2. Các Task (mỗi Task là một phần bạn bấm thử được)

### Task 1: Trích xuất báo cáo vi phạm quy chế chi tiết ở bước kiểm tra cuối và trả về qua API Chat & Streaming SSE (Backend)
- [x] **Xong** · **Bạn đã kiểm:** đạt
- **Thao tác để kiểm:** Gửi tin nhắn qua API `POST /api/chat/sessions/{session_id}/messages` và `/messages/stream` (hoặc kiểm tra qua Swagger UI / lệnh test) trong 3 kịch bản: (1) Quy chế đang bật và câu trả lời tuân thủ quy chế; (2) Quy chế đang bật và câu trả lời nháp vi phạm quy chế; (3) Tắt kiểm tra quy chế (`school_rules` không nằm trong `rail_ids` hoặc `rails_enabled=false`).
- **✅ Đúng khi thấy:**
  - Kịch bản (1): `assistant_message.school_rules_report` (và `metadata.school_rules_report`) có `checked=true`, `has_violation=false`, `was_revised=false`, `summary` báo tuân thủ quy chế, `violations=[]`.
  - Kịch bản (2): Câu trả lời được chỉnh lại đúng quy chế, đồng thời `assistant_message.school_rules_report` có `checked=true`, `has_violation=true`, `was_revised=true`, `summary` tóm tắt lỗi vi phạm và mảng `violations` chứa đầy đủ từng mục vi phạm (`rule_id`, `rule_name`, `violated_content`, `reason`).
  - Kịch bản (3): Không chạy bước kiểm tra quy chế, `school_rules_report` là `null`.
  - Khi gọi `GET /api/chat/sessions/{session_id}/messages` tải lại lịch sử trò chuyện, các tin nhắn đã kiểm tra vẫn trả về đầy đủ `school_rules_report`.
- **❌ Sai nếu thấy:** Phát hiện vi phạm nhưng `violations` rỗng hoặc mất nội dung bị vi phạm; tắt quy chế nhưng vẫn báo `checked=true`; hoặc làm hỏng các test hiện có trong `tests/test_school_rules.py`.
- **Kiểm tra tự động:** `cd backend/services/api && uv run ruff check src/bookforge_api/chat/governance.py src/bookforge_api/schemas/chat.py src/bookforge_api/chat/adk_agent.py src/bookforge_api/api/chat.py tests/test_school_glossary.py && uv run pytest -n 0 tests/test_school_glossary.py -k "test_school_rules_violation_report_in_chat_and_history"`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/chat/governance.py:298-575` — Bổ sung `_build_school_rules_report_verifier_instructions`, `_extract_violations_payload`, `parse_school_rules_verification_report`, `verify_answer_against_school_rules_with_report`, và `async_verify_answer_against_school_rules_with_report` (không chạm vào các file `school_rules` gốc).
  - `backend/services/api/src/bookforge_api/schemas/documents.py` & `backend/services/api/src/bookforge_api/schemas/chat.py:173-204` — Khai báo schema `SchoolRulesViolationItem`, `SchoolRulesReport` và thêm trường `school_rules_report: SchoolRulesReport | None = None` vào `ChatAnswerResponse` và `ChatMessageResponse`.
  - `backend/services/api/src/bookforge_api/chat/adk_agent.py:361-507, 1289-1315, 1655-1704` — Thu thập `school_rules_report` từ bước kiểm tra cuối trong cả luồng sync (`run_adk_chat`) và luồng streaming SSE (`stream_adk_chat`), đưa vào kết quả trả về của `_shape_chat_result`.
  - `backend/services/api/src/bookforge_api/api/chat.py:1524-1648, 1651-1705, 1734-2033` — Lưu `school_rules_report` vào `assistant_message.metadata_json["school_rules_report"]` trong `_run_free_chat` và `finalize_chat_turn`, đồng thời map ra `ChatMessageResponse.school_rules_report` trong `_serialize_message`.
  - `backend/services/api/tests/test_school_glossary.py:635-800` — Bổ sung unit test & integration test kiểm tra parser báo cáo vi phạm chi tiết, fallback tương thích ngược, và kiểm tra `school_rules_report` trên response của API chat khi tuân thủ / khi vi phạm / khi tắt quy chế.

### Task 2: Hiển thị biểu tượng trạng thái quy chế (tích xanh / cảnh báo) ở góc dưới tin nhắn kèm hover tổng quan và popover chi tiết vi phạm (Frontend)
- [x] **Xong** · **Bạn đã kiểm:** đạt
- **Thao tác để kiểm:** Mở trang Chat chính (`HomePage`) hoặc khung chat trong trang chi tiết tài liệu (`ready-document-view`), gửi câu hỏi khi quy chế đang bật (1 câu hỏi thông thường không vi phạm, 1 câu hỏi chạm quy chế bị cấm) rồi: (1) Quan sát biểu tượng góc dưới tin nhắn; (2) Rê chuột (hover) vào biểu tượng; (3) Nhấn chuột (click) vào biểu tượng và bấm ra ngoài để đóng; (4) Tải lại trang (F5) kiểm tra lịch sử tin nhắn.
- **✅ Đúng khi thấy:**
  - Ở câu trả lời không vi phạm: góc dưới tin nhắn hiện biểu tượng **tích xanh**, rê chuột vào hiện tóm tắt *"Tuân thủ quy chế nhà trường"*, nhấn vào hiện khung nổi xác nhận đã đối chiếu quy chế và không phát hiện vi phạm.
  - Ở câu trả lời có vi phạm: góc dưới tin nhắn hiện **biểu tượng cảnh báo màu vàng/cam**, rê chuột vào hiện tổng quan đang vi phạm gì (`summary` + số mục vi phạm), nhấn vào mở khung nổi (popover) hiển thị danh sách chi tiết từng quy chế bị vi phạm, đoạn nội dung bị vi phạm (`violated_content`) và lý do/cách xử lý (`reason`).
  - Ở tin nhắn khi đã tắt kiểm tra quy chế hoặc tin nhắn cũ không có dữ liệu kiểm tra: không hiện biểu tượng trạng thái quy chế.
  - Khi bấm ra ngoài hoặc nhấn phím `Escape` / nhấn lại vào biểu tượng, khung nổi chi tiết đóng lại gọn gàng.
- **❌ Sai nếu thấy:** Không hiện biểu tượng khi đã kiểm tra quy chế, hiện sai màu/biểu tượng giữa đạt và vi phạm, rê chuột không hiện tổng quan, nhấn vào không mở chi tiết nội dung bị vi phạm, hoặc mất biểu tượng sau khi tải lại trang.
- **Kiểm tra tự động:** `cd frontend && npm run typecheck && npm run test -- src/components/Chat/partial/rule-compliance-indicator.test.tsx`
- **File và thay đổi:**
  - `frontend/src/api/bookforge-api.ts:483-547` — Khai báo kiểu `TSchoolRulesViolationItem`, `TSchoolRulesReport` và bổ sung `school_rules_report?: TSchoolRulesReport | null` vào `TChatMessageResponse`.
  - `frontend/src/templates/HomePage/partials/use-chat-with-ai.ts:56-153` — Bổ sung `school_rules_report?: TSchoolRulesReport | null` vào `TChatMessageItem` và ánh xạ từ `message.school_rules_report ?? message.metadata?.school_rules_report` trong `toChatItem`.
  - `frontend/src/components/Chat/partial/rule-compliance-indicator.tsx` (tạo mới) & `frontend/src/components/Chat/partial/message-actions.tsx:28-92` — Tạo component `RuleComplianceIndicator` hiển thị icon nhỏ ở góc dưới tin nhắn (tích xanh khi `!has_violation`, icon cảnh báo khi `has_violation`), hỗ trợ tooltip tổng quan khi hover và popover chi tiết các nội dung vi phạm khi click (đóng khi click ra ngoài hoặc nhấn `Escape`), tích hợp vào thanh góc dưới tin nhắn trợ lý.
  - `frontend/src/templates/HomePage/index.tsx:703-736` & `frontend/src/templates/DocumentDetailPage/partial/ready-document-view.tsx:241-295` — Truyền `schoolRulesReport` của tin nhắn trợ lý xuống thanh góc dưới tin nhắn.
  - `frontend/src/components/Chat/partial/rule-compliance-indicator.test.tsx` (tạo mới) — Unit test giao diện kiểm tra đủ các trạng thái: ẩn khi chưa kiểm tra (`checked=false` / `null`), hiện tích xanh khi không vi phạm, hiện icon cảnh báo + hover tổng quan + click mở popover chi tiết nội dung vi phạm khi có vi phạm.

## 3. Điều kiện hoàn thành
- [x] Toàn bộ kiểm tra như CI (`backend/.github/workflows/ci.yml:79-92` & `frontend/.github/workflows/ci.yml:27-40`) đều đúng:
  - `cd backend/services/api && uv run ruff check .`
  - `cd backend/services/api && uv run ruff format --check .`
  - `cd backend/services/api && uv run pytest`
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`
  - `cd frontend && npm run test`
  - `cd frontend && npm run build`
- [x] Khi quy chế đang bật và phát hiện vi phạm, câu trả lời được tự động chỉnh đúng quy chế kèm biểu tượng cảnh báo ở góc dưới; rê chuột thấy tổng quan vi phạm, nhấn vào mở khung nổi (popover) hiển thị chi tiết quy chế và nội dung bị vi phạm.
- [x] Khi quy chế đang bật và không vi phạm, góc dưới tin nhắn hiện biểu tượng tích xanh; khi tắt kiểm tra quy chế thì ẩn biểu tượng.

## 4. Kiểm kế hoạch
- **`file:dòng`, tên hàm có thật:** Đã mở code kiểm tra trực tiếp toàn bộ `file:dòng` và tên hàm trong `backend/services/api/src/bookforge_api/services/school_rules.py:93-100, 127-257`, `backend/services/api/src/bookforge_api/chat/governance.py:36-89`, `backend/services/api/src/bookforge_api/schemas/chat.py:173-204`, `backend/services/api/src/bookforge_api/chat/adk_agent.py:361-507, 1289-1315, 1655-1704`, `backend/services/api/src/bookforge_api/api/chat.py:1322-1324, 1524-1705, 1734-2033`, `backend/services/api/tests/test_school_rules.py:194-324`, `frontend/src/api/bookforge-api.ts:483-547`, `frontend/src/templates/HomePage/partials/use-chat-with-ai.ts:56-153`, `frontend/src/components/Chat/partial/message-actions.tsx:28-92`, `frontend/src/templates/HomePage/index.tsx:653-736`, và `frontend/src/templates/DocumentDetailPage/partial/ready-document-view.tsx:241-295`.
- **Lệnh kiểm tra chạy được:** Đã chạy thật tại `backend/services/api` và `frontend`:
  - `cd backend/services/api && uv run ruff check src/bookforge_api/services/school_rules.py src/bookforge_api/schemas/chat.py tests/test_school_rules.py; uv run pytest -n 0 tests/test_school_rules.py` → `All checks passed!`, `4 passed, 1 warning in 29.53s`.
  - `cd frontend && npm run typecheck` → `tsc --noEmit` (pass, exit code 0).
- **Mục tiêu, nghiệp vụ, điều đã chốt đều có Task:** Đủ 100% (Task 1 thực hiện trích xuất báo cáo vi phạm chi tiết ở bước kiểm tra cuối + giữ tự động chỉnh câu trả lời theo quyết định `1a` + chỉ gắn `checked=true` khi thực sự chạy kiểm tra theo quyết định `2a`; Task 2 hiển thị biểu tượng tích xanh / cảnh báo ở góc dưới tin nhắn + hover xem tổng quan + click mở popover chi tiết theo quyết định `3a`).
- **Mọi Task có tiêu chí:** Đủ (`Thao tác để kiểm`, `✅ Đúng khi thấy`, `❌ Sai nếu thấy`, `Kiểm tra tự động`, `File và thay đổi`).
- **Cần bạn quyết:** Không có (bạn đã chốt đủ 3 tình huống: `1a`, `2a`, `3a`).

## 5. Nhật ký làm
- **Kiểm tra trước khi sửa** (để phân biệt lỗi có sẵn):
  - `cd backend/services/api && uv run ruff check src/bookforge_api/services/school_rules.py src/bookforge_api/schemas/chat.py tests/test_school_rules.py && uv run pytest -n 0 tests/test_school_rules.py` → `All checks passed! / 4 passed, 1 warning in 29.53s`
  - `cd frontend && npm run typecheck` → `tsc --noEmit` (pass, exit code 0)
- **Quyết định phát sinh:** Không có
- **Kết quả từng Task:**
  - **Task 1:**
    - Lệnh kiểm tra tự động: `cd backend/services/api && uv run ruff check src/bookforge_api/chat/governance.py src/bookforge_api/schemas/documents.py src/bookforge_api/schemas/chat.py src/bookforge_api/chat/adk_agent.py src/bookforge_api/api/chat.py tests/test_school_glossary.py && uv run pytest -n 0 tests/test_school_glossary.py tests/test_school_rules.py tests/test_api_contract_generator.py` → `All checks passed! / 38 passed, 1 warning in 28.90s`
    - Tự kiểm thử 10 kịch bản thực tế (`S1`–`S10`) + bổ sung test khắt khe cho trường hợp LLM ghi câu mô tả (`"Phần bắt buộc còn thiếu..."`), JSON bọc trong markdown code fence, JSON lỗi cú pháp / chứa ngoặc kép chưa escape, lọc sạch thẻ nội bộ `<!--BF_GOV:...-->`, và lưu kèm `draft_answer` vào `SchoolRulesReport`. Bạn đã xác nhận đạt.
  - **Task 2:**
    - Lệnh kiểm tra tự động: `cd frontend && npm run lint && npm run typecheck && npx vitest run src/components/Chat/partial/rule-compliance-indicator.test.tsx src/components/Chat/partial/message-actions.test.tsx src/components/Chat/partial/formatted-answer.test.tsx src/templates/HomePage/partials/use-chat-with-ai.test.tsx && npm run build` → `eslint (0 errors) / tsc --noEmit (0 errors) / 4 passed (68 tests) / vite build pass`
    - Tự kiểm thử giao diện & xử lý phát hiện khi kiểm tay:
      - Khắc phục việc khung nổi (popover) bị che khuất phần đầu khi tin nhắn nằm sát mép trên vùng cuộn: chuyển sang render qua `createPortal(..., document.body)` với `position: fixed` và hàm `computeFloatingLayout` tự động lật xuống dưới (`data-placement="bottom"`) khi khoảng trống phía trên không đủ, giữ cố định thanh tiêu đề và cuộn mượt phần thân (`maxHeight` co giãn theo viewport).
      - Render Markdown và công thức toán học KaTeX qua `FormattedAnswer` cho toàn bộ 4 vùng văn bản trong tooltip và popover (`summaryText`, `item.violated_content`, `**Chi tiết:** ${item.reason}`, `draftAnswer`).
      - Ẩn hoàn toàn thẻ nội bộ `<!--BF_GOV:...-->` ngay cả trong lúc đang stream từng ký tự (`normalize-markdown-content.ts`, `use-chat-with-ai.ts`, `adk_agent.py`).
      - Khử trùng lặp tên quy chế trong Tooltip và đồng nhất cỡ chữ danh sách. Bạn đã xác nhận OK.

## 6. Nghiệm thu
- **Ngày:** 2026-11-10
- **Thay đổi so với kế hoạch:** Toàn bộ logic trích xuất báo cáo vi phạm quy chế phía Backend được đặt trong `chat/governance.py` và kiểm thử trong `tests/test_school_glossary.py` để giữ nguyên trạng 100% các file `*school_rules*` theo yêu cầu của bạn; bổ sung lọc thẻ `<!--BF_GOV:...-->` trong lúc stream ở `normalize-markdown-content.ts`.
- **Từng nghiệp vụ (`analysis.md` mục 3.0, nếu có):** Không áp dụng
- **Chạy lại toàn bộ kiểm tra:**
  - `cd backend/services/api && uv run ruff check .` → `All checks passed!`
  - `cd backend/services/api && uv run ruff format --check .` → `1154 files already formatted`
  - `cd backend/services/api && uv run pytest -n 0 tests/test_school_glossary.py tests/test_school_rules.py tests/test_api_contract_generator.py` → `38 passed, 1 warning in 28.90s`
  - `cd frontend && npm run lint` → `0 errors`
  - `cd frontend && npm run typecheck` → `tsc --noEmit (0 errors)`
  - `cd frontend && npx vitest run src/components/Chat/partial/rule-compliance-indicator.test.tsx src/components/Chat/partial/message-actions.test.tsx src/components/Chat/partial/formatted-answer.test.tsx src/templates/HomePage/partials/use-chat-with-ai.test.tsx` → `4 passed (68 tests)`
  - `cd frontend && npm run build` → `✓ built in 30.77s`
- **Không lọt chữ `tech_docs` vào backend / frontend:** Đã chạy `git diff | Select-String -Pattern "tech_docs"` trên cả `backend/` và `frontend/` → trống (0 kết quả).
- **Kết luận:** Đạt (`VERIFIED`)

## 7. Kiểm tay
- **Kết quả:** đạt

## 8. Commit
- **Tài liệu trong `backend/`:** `backend/docs/superpowers/specs/2026-11-10-rule-violation-indicator-design.md`, `backend/docs/superpowers/plans/2026-11-10-rule-violation-indicator.md`
- **Mã commit:** backend `84ffac7f` (merge `a84fe2a6`) · frontend `169aa2e` (merge `2f20fc4`) · **Đã push và merge `dev`:** rồi

## 9. Việc còn treo
- Không có

## 10. Số đo
- **Bắt đầu:** 2026-11-10 · **Merge:** 2026-11-10
- **Số lỗi bạn bắt được khi kiểm tay:** 4
- **Số lần phải sửa sau merge:** 0
