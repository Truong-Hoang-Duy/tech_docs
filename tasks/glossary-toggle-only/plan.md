# Kế hoạch: Chuẩn hóa Từ điển sư phạm thành công tắc Bật/Tắt duy nhất và tự động nhận diện đa môn học

**Ngày:** 2026-11-12 · **Cách làm:** Cách 3: Việc thường · **Phía:** Cả hai
**Trạng thái:** VERIFIED
**Mốc code:** backend `a5d3fce1` · frontend `6a32c01d` · **Nhánh:** `feat/glossary-toggle-only`

## 1. Mục tiêu và quyết định đã chốt
- **Mục tiêu:**
  1. Chuẩn hóa toàn bộ giao diện cấu hình **Từ điển sư phạm** trên Chat/Canvas (`AgentContextSettingsDialog`), Cài đặt toàn cục (`ModalSettings`) và Ngân hàng câu hỏi (`MassQuestionGenerateDrawer`) thành **công tắc Bật/Tắt duy nhất** (`glossary_enabled`), loại bỏ hoàn toàn giao diện chọn môn thủ công và đổi nhãn pill thành `Từ điển: Bật` / `Từ điển: Tắt`.
  2. Xây dựng bộ máy tự động nhận diện môn học và tra cứu thuật ngữ trên toàn bộ **11 miền dữ liệu** (`chung` + 10 môn cấp THPT) tại `SchoolGlossaryService`, hoạt động chính xác ngay cả khi câu hỏi không nêu tên môn và chặn dương tính giả trên văn bản đời thường.
  3. Đồng bộ thực thi cờ `glossary_enabled` và bơm `<school_glossary>` tự động trên mọi luồng sinh nội dung AI phía Backend (Free chat, Scoped ADK chat, 5 Agent chuyên biệt, Canvas Editor, Flow/Mindmap và Ngân hàng câu hỏi), đồng thời khử lỗi lặp cập nhật trạng thái khi chuyển trang sau khi chat.
- **Quyết định đã chốt** (không tự đổi khi làm):
  1. **Nhãn pill dưới khung chat (Tình huống 1 — Chọn a):** Chỉ hiển thị gọn `Từ điển: Bật` khi `glossary_enabled=true` và `Từ điển: Tắt` khi `glossary_enabled=false`.
  2. **Tự động nhận diện đa môn không cần ghi tên môn (Tình huống 2 — Chọn a):** Quét trên toàn bộ 11 miền (`chung`, `toan`, `ngu_van`, `vat_ly`, `hoa_hoc`, `sinh_hoc`, `lich_su`, `dia_ly`, `gdktpl`, `tieng_anh`, `tin_hoc`), nhận diện cả thuật ngữ khoa học vay mượn 1 từ, cấu trúc ngữ pháp Tiếng Anh lẫn cụm thuật ngữ tiếng Việt, kèm quy tắc ngôn ngữ học tổng quát chống khớp nhầm từ đời thường.
  3. **Đồng bộ toàn bộ luồng AI phía máy chủ (Tình huống 3 — Chọn a):** Áp dụng nhất quán trên cả Free chat, Scoped ADK chat, 5 Agent chuyên biệt, Trình soạn thảo Canvas, Flow/Mindmap và Tạo sinh câu hỏi ở Ngân hàng câu hỏi; giữ tương thích ngược trường `glossary_ids` trong payload API.
- **Tài liệu trong `backend/`:** Chốt khi hoàn tất (hỏi bạn muốn tạo `plan`, `spec`, cả 2 hay cập nhật tài liệu hiện có sau khi xác nhận kiểm tay `VERIFIED`).

## 2. Các Task (làm liền mạch hết các Task rồi mới kiểm tay tổng thể trên UI)

### Task 1: Bộ máy tự động nhận diện môn học và tra cứu Từ điển sư phạm trên toàn bộ 11 miền dữ liệu (Backend Core)
- [x] **Xong (AI đã tự test & bấm thử)**
- **Thao tác tự kiểm:** Chạy bộ kiểm thử tự động `tests/test_school_glossary.py` và gọi trực tiếp `SchoolGlossaryService.resolve_auto_glossary_terms` / `resolve_question_bank_glossary` với các câu hỏi không nêu tên môn trải đều cả 11 miền dữ liệu, câu hỏi thuật ngữ đơn (`enthalpy`), câu hỏi không dấu, và các câu giao tiếp đời thường có từ dễ trùng âm.
- **✅ Đúng khi thấy:**
  - *(1) Phần cố định / cấu trúc (khớp 100%):* Khi `glossary_enabled=False` luôn trả về `([], [])` và chuỗi rỗng `""`; khi `glossary_enabled=True`, câu hỏi chuyên môn không ghi tên môn tự động trả về đúng `subject_key` của môn đó (trải đủ 10 môn THPT + `chung`) kèm khối `<school_glossary>` sạch tên bộ sách/NXB; các câu đời thường (*"Xin chào hôm nay thời tiết thế nào"*, *"Đội mũ bảo hiểm an toàn giao thông"*, *"Chúc mừng nhân ngày 20/11"*) trả về `0` thuật ngữ môn học bị nhận nhầm; `resolve_question_bank_glossary` tự suy luận đúng `active_domains` (ví dụ `['chung', 'hoa_hoc']`) kể cả khi `glossary_ids=None` hoặc `['chung']`.
  - *(2) Phần câu chữ do LLM sinh:* Chưa gọi LLM ở tầng dịch vụ tra cứu này (không áp dụng).
- **❌ Sai nếu thấy:** Câu hỏi ngắn như *"Giải thích ngắn gọn khái niệm enthalpy"* trả về rỗng; từ tiếng Việt có dấu khớp nhầm sang mục từ Tiếng Anh không dấu; từ ghép đời thường (*"an toàn"*, *"mũ bảo hiểm"*, *"tính chất vật lí"*, *"bối cảnh lịch sử"*) kích hoạt nhầm môn Toán / GDKT&PL / Vật lí / Lịch sử; hoặc lọt watermark tên bộ sách/NXB.
- **Điểm suy luận tự test thêm:** Kiểm tra phân biệt từ đơn tiếng Việt và từ vay mượn khoa học qua cấu trúc cụm nguyên âm (`_count_vowel_clusters`); tách tiêu đề ngữ pháp Tiếng Anh trước dấu `:` (`Relative clauses: ...`); câu hỏi tiếng Việt gõ không dấu (`menh de phu dinh`); chống lỗi cú pháp FTS5 với ký tự đặc biệt (`AND`, `OR`, dấu ngoặc, dấu nháy kép); mở rộng thuật ngữ anh em cùng bài học (`anchor_lessons`) để câu hỏi ngắn vẫn có đủ hệ thuật ngữ đối chiếu.
- **Kiểm tra tự động:** `cd d:\Project\bookforge\backend\services\api && uv run pytest -n 0 tests/test_school_glossary.py`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/services/school_glossary.py:691-986, 1111-1485, 1866-1909, 2096-2429` — Nâng cấp `extract_headword_variants`, xây dựng bộ phân tích ngữ cảnh môn học `_detect_curriculum_subject_in_text`, kiểm tra ranh giới từ ghép `_has_false_vi_compound_boundary`, hàm `resolve_auto_glossary_terms`, `resolve_auto_glossary_prompt_block` và nâng cấp `resolve_question_bank_glossary` cho chế độ chỉ dùng công tắc Bật/Tắt.
  - `backend/services/api/tests/test_school_glossary.py:941-1380` — Bổ sung bộ test bao phủ tự động nhận diện toàn bộ 11 miền không cần ghi tên môn, thuật ngữ đơn khoa học, câu không dấu, cách ly từ đồng âm và chống nhận nhầm từ ghép đời thường.

### Task 2: Đồng bộ bơm ngữ cảnh Từ điển tự động trên tất cả các luồng AI phía máy chủ (Chat, 5 Agent chuyên biệt, Canvas/Flow & Ngân hàng câu hỏi)
- [x] **Xong (AI đã tự test & bấm thử)**
- **Thao tác tự kiểm:** Gọi API gửi tin nhắn Chat tự do (`_run_free_chat`), Chat ADK / 5 Agent chuyên biệt (`Phiếu điền khuyết`, `Ma trận đề`, `Tạo đề kiểm tra`, `Dịch học thuật`, `Infographic`), Trợ lý Canvas/Flow và `POST /api/question-cards/generate` ở cả hai chế độ `glossary_enabled=true` và `glossary_enabled=false`.
- **✅ Đúng khi thấy:**
  - *(1) Phần cố định / cấu trúc (khớp 100%):* Khi `glossary_enabled=true`, system prompt của cả Free chat (`PydanticAITextProvider.answer_without_context`), ADK chat, 5 Agent chuyên biệt, Canvas Editor, Flow/Mindmap và Question Bank đều nhận được khối `<school_glossary>` tự động theo ngữ cảnh mà không cần truyền `glossary_ids`; `QuestionCard.metadata_json["glossary"]` lưu đúng `enabled: true` và `active_domains` của môn học. Khi `glossary_enabled=false`, không có bất kỳ khối `<school_glossary>` nào được bơm vào prompt và không lộ thẻ `<school_glossary>` ra câu trả lời hiển thị cho người dùng.
  - *(2) Phần câu chữ do LLM sinh (đối chiếu tương đối theo ý nghĩa & quy tắc):* Với câu hỏi dùng thuật ngữ chương trình cũ (ví dụ *cân bằng Hacđi–Vanbec*, *gen*, *alen*, *axit axetic*, *este*), khi **Từ điển: Bật** câu trả lời chuẩn hóa sang đúng thuật ngữ GDPT 2018 (*cân bằng Hardy – Weinberg*, *gene*, *allele*, *acetic acid*, *ester*); khi **Từ điển: Tắt** câu trả lời diễn đạt tự nhiên theo ngữ cảnh đầu vào của người dùng mà không cưỡng bức đổi sang danh mục từ điển.
- **❌ Sai nếu thấy:** Chat tự do không nhận được `glossary_section` trong system instructions; các mock provider cũ trong test bị lỗi `TypeError` do lệch tham số `answer_without_context`; tắt từ điển nhưng agent vẫn tự tra cứu `<school_glossary>`; hoặc thẻ kỹ thuật `<school_glossary>` bị rò rỉ ra nội dung chat.
- **Điểm suy luận tự test thêm:** Kiểm tra tương thích ngược bằng `inspect.signature(provider.answer_without_context)` cho các custom/fake provider trong toàn bộ suite test; kiểm tra trường hợp người dùng dán trực tiếp đoạn ngữ liệu chương trình cũ vào Agent Phiếu điền khuyết (phân biệt rõ hành vi giữ trung thực ngữ liệu gốc của bài tập đục lỗ với chuẩn hóa thuật ngữ khi tạo mới từ Kho tri thức mặc định); kiểm tra câu hỏi trắc nghiệm mức độ *Vận dụng* nhiều tham số không ghi tên môn.
- **Kiểm tra tự động:** `cd d:\Project\bookforge\backend\services\api && uv run pytest -n 0 tests/test_school_glossary.py tests/test_question_bank_prompts.py tests/test_question_cards_generate_api.py tests/test_pydantic_text_provider.py tests/test_dich_hoc_thuat_agent.py`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/api/chat.py:1551-1582` — Chuyển `_run_free_chat` sang gọi `resolve_auto_glossary_prompt_block` và truyền an toàn `glossary_section` vào `provider.answer_without_context`.
  - `backend/services/api/src/bookforge_api/llm/providers.py:126-130, 184-189` & `llm/pydantic_text_provider.py:177-192` — Bổ sung tham số `glossary_section: str = ''` và gắn vào system `instructions` của `PydanticAITextProvider.answer_without_context`.
  - `backend/services/api/src/bookforge_api/chat/adk_agent.py:1033-1043`, `de_kiem_tra_agent.py:110-128`, `ma_tran_de_agent.py:556-581`, `phieu_dien_khuyet_agent.py:419-443`, `infographic_agent.py:1194-1218` — Chuyển sang tra cứu tự động đa miền qua `SchoolGlossaryService` khi `glossary_enabled=True`.
  - `backend/services/api/src/bookforge_api/chat/editor_agent.py:488-540, 617-621, 697-722, 822-826` & `chat/flow_agent.py:748-820, 1020-1036, 1184-1200` — Tự động bơm khối `<school_glossary>` theo nội dung tài liệu/yêu cầu trong Trình soạn thảo Canvas và Sơ đồ tư duy Flow khi `glossary_enabled=True`.
  - `backend/services/api/tests/test_question_cards_generate_api.py:679-743` — Bổ sung test `test_generate_toggle_only_auto_resolves_subject_glossary_without_glossary_ids` kiểm tra cả trường hợp lược bỏ `glossary_ids` lẫn gửi `glossary_ids=['chung']`.

### Task 3: Chuẩn hóa giao diện Từ điển sư phạm thành công tắc Bật/Tắt duy nhất trên 3 màn hình (Chat/Canvas, Cài đặt toàn cục & Ngân hàng câu hỏi)
- [x] **Xong (AI đã tự test & bấm thử)**
- **Thao tác tự kiểm:** Mở trình duyệt tại `http://localhost:3000`, kiểm tra lần lượt: (1) Thanh chip bên dưới ô nhập chat và hộp thoại **Cài đặt ngữ cảnh & công cụ** / **Từ điển sư phạm**; (2) Hộp thoại Cài đặt tài khoản → tab **Ngữ cảnh & Quy chế** (`Ngữ cảnh & Quy chế toàn cục`) và trang **Quy chế nhà trường** (`Cài đặt Toàn cục (Từ điển & Quy chế)`); (3) Trang **Ngân hàng câu hỏi** → nút **Tạo sinh câu hỏi** → mục **C. Từ điển sư phạm**.
- **✅ Đúng khi thấy:**
  - *(1) Phần cố định / cấu trúc (khớp 100%):*
    - Trên thanh công cụ dưới ô nhập chat và thanh tóm tắt Toàn cục: chip từ điển chỉ hiển thị đúng chữ **`Từ điển: Bật`** hoặc **`Từ điển: Tắt`** (không còn `Từ điển: Chung`, `Từ điển: Toán học +1`).
    - Trong hộp thoại **Cài đặt ngữ cảnh & công cụ** (`AgentContextSettingsDialog`), mục **Từ điển sư phạm** chỉ có mô tả *"Ưu tiên chuẩn thuật ngữ, kí hiệu và định nghĩa theo Chương trình GDPT 2018. Hệ thống tự động nhận diện môn học theo ngữ cảnh."* và công tắc `Switch` Bật/Tắt ở bên phải; hoàn toàn không còn dãy nút chọn môn hay menu `Khác...`.
    - Trong tab **Ngữ cảnh & Quy chế** (`ModalSettings`), mục **Từ điển sư phạm mặc định** chỉ còn công tắc `Switch` Bật/Tắt; bấm **Lưu** và tải lại trang (F5) giữ nguyên trạng thái đã lưu.
    - Trong ngăn **Tạo sinh câu hỏi** (`MassQuestionGenerateDrawer`), mục **C. Từ điển sư phạm** chỉ còn công tắc `Switch` Bật/Tắt (tự khóa `disabled` khi đang tạo câu hỏi `isSubmitting`).
  - *(2) Phần câu chữ do LLM sinh:* Không áp dụng riêng cho tầng hiển thị công tắc (được kiểm chung khi gửi câu hỏi/tạo câu hỏi ở Task 2).
- **❌ Sai nếu thấy:** Còn sót bất kỳ chip môn học (`Chung`, `Toán học`, `Ngữ văn`, `Khoa học tự nhiên`) hoặc nút `Khác...` nào trên cả 3 màn hình; công tắc `Switch` vẫn cho gạt khi đang `Đang tạo...` trong ngăn Tạo sinh câu hỏi; bấm **Hủy** vẫn làm đổi trạng thái ngoài khung chat; hoặc tải lại trang (F5) bị mất trạng thái Bật/Tắt.
- **Điểm suy luận tự test thêm:** Kiểm tra nút **Khôi phục mặc định** ở cả phạm vi Cục bộ (`local`) và Toàn cục (`global`); kiểm tra các phiên chat cũ trong DB từng lưu `glossary_ids: []` hoặc `glossary_ids: ["toan"]` khi nạp lên vẫn hiển thị đúng `Từ điển: Bật` / `Từ điển: Tắt` theo `glossary_enabled`; kiểm tra bố cục hộp thoại trên màn hình hẹp không bị tràn chữ hoặc lệch hàng công tắc `Switch`.
- **Kiểm tra tự động:** `cd d:\Project\bookforge\frontend && npm run typecheck && npx vitest run src/components/TiptapEditor/agent-settings/agent-settings-model.test.ts src/components/TiptapEditor/agent-settings/AgentSettings.test.tsx src/components/TiptapEditor/partial/document-ai-chat-panel-agent-settings.test.tsx src/templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.test.tsx`
- **File và thay đổi:**
  - `frontend/src/components/Switch/index.tsx:6-29` — Bổ sung prop `disabled?: boolean` (khóa thao tác click và làm mờ `opacity-50 cursor-not-allowed` khi đang gửi dữ liệu).
  - `frontend/src/components/TiptapEditor/agent-settings/agent-settings-model.ts:445-451, 688-690, 744-750` — Cập nhật `toChatContextSettings`, `isGlossaryActive` (chỉ phụ thuộc `Boolean(settings.glossary_enabled)`) và `formatGlossaryPillLabel` trả về `"Từ điển: Bật"` / `"Từ điển: Tắt"`.
  - `frontend/src/components/TiptapEditor/agent-settings/AgentContextSettingsDialog.tsx:209-227` — Thu gọn thẻ `Từ điển sư phạm` thành công tắc `Switch` duy nhất, gỡ bỏ toàn bộ state/chip chọn môn lẻ và popover `Khác...`.
  - `frontend/src/components/ModalSettings/index.tsx:1488-1518` — Thu gọn mục `Từ điển sư phạm mặc định` trong `GlobalContextSettingsPanel` thành công tắc `Switch` duy nhất.
  - `frontend/src/templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.tsx:819-843` — Thu gọn mục `C. Từ điển sư phạm` thành công tắc `Switch` duy nhất có hỗ trợ `disabled={isSubmitting}`, chỉ gửi `glossary_enabled` lên API.
  - Cập nhật các file unit test giao diện tương ứng: `agent-settings-model.test.ts`, `AgentSettings.test.tsx`, `document-ai-chat-panel-agent-settings.test.tsx`, `MassQuestionGenerateDrawer.test.tsx`.

### Task 4: Ổn định vòng lặp cập nhật trạng thái `context_settings` khi chuyển trang sau khi chat (Frontend Stability)
- [x] **Xong (AI đã tự test & bấm thử)**
- **Thao tác tự kiểm:** Đăng nhập `http://localhost:3000`, gửi 1–2 tin nhắn ở khung Chat chính (có bật/tắt `Từ điển sư phạm`), ngay sau khi AI trả lời xong bấm chuyển liên tục sang các mục khác trên thanh điều hướng bên trái (**Tài liệu**, **Ngân hàng câu hỏi**, **Quy chế nhà trường**) rồi quay lại **Trò chuyện**.
- **✅ Đúng khi thấy:**
  - *(1) Phần cố định / cấu trúc (khớp 100%):* Chuyển trang mượt tức thì, không bị đơ tab trình duyệt, console không phát sinh lỗi `Maximum update depth exceeded`, và khi quay lại phiên chat cũ trạng thái `Từ điển: Bật` / `Từ điển: Tắt` vẫn giữ đúng như đã chọn.
  - *(2) Phần câu chữ do LLM sinh:* Không áp dụng.
- **❌ Sai nếu thấy:** Sau khi gửi tin nhắn chat, bấm sang trang khác trên thanh điều hướng bị treo cứng giao diện hoặc lặp vô hạn `setContextSettings`.
- **Điểm suy luận tự test thêm:** Kiểm tra tham chiếu mảng `modes`, `experts`, `agents` trả về từ `useChatModes()` giữ nguyên ổn định (`toBe`) qua các lần re-render bằng unit test chuyên biệt trong `use-chat-modes.test.tsx`; kiểm tra `areChatContextSettingsEqual` chặn cập nhật thừa ở cả `HomePage/index.tsx` và `use-chat-with-ai.ts`.
- **Kiểm tra tự động:** `cd d:\Project\bookforge\frontend && npx vitest run src/hooks/use-chat-modes.test.tsx src/templates/HomePage/index.test.tsx`
- **File và thay đổi:**
  - `frontend/src/hooks/use-chat-modes.ts:51-76` & `src/hooks/use-chat-modes.test.tsx:160-176` — Bọc `useMemo` cho `modes`, `experts`, `agents` và kết quả trả về để giữ tham chiếu ổn định giữa các lần render.
  - `frontend/src/templates/HomePage/index.tsx:79, 858-865`, `src/templates/HomePage/partials/use-chat-with-ai.ts:35, 364-368` & `src/templates/HomePage/index.test.tsx:480-496` — Dùng `areChatContextSettingsEqual` chặn gọi `setContextSettings` lặp khi giá trị cấu hình ngữ cảnh không đổi.

## 3. Điều kiện hoàn thành
- [x] Toàn bộ kiểm tra lint, format, typecheck, build và các bộ test liên quan như CI (`backend/.github/workflows/ci.yml:85-98` & `frontend/.github/workflows/ci.yml:30-42`) đều đạt:
  - `cd d:\Project\bookforge\backend\services\api && uv run ruff check .`
  - `cd d:\Project\bookforge\backend\services\api && uv run ruff format --check .`
  - `cd d:\Project\bookforge\backend\services\api && uv run pytest -n 0 tests/test_school_glossary.py tests/test_question_bank_prompts.py tests/test_question_cards_generate_api.py tests/test_pydantic_text_provider.py tests/test_dich_hoc_thuat_agent.py`
  - `cd d:\Project\bookforge\frontend && npm run lint`
  - `cd d:\Project\bookforge\frontend && npm run typecheck`
  - `cd d:\Project\bookforge\frontend && npx vitest run` (trên toàn bộ các bộ test bị ảnh hưởng)
  - `cd d:\Project\bookforge\frontend && npm run build`
- [x] Mục **Từ điển sư phạm** trên cả 3 màn hình (`AgentContextSettingsDialog`, `ModalSettings`, `MassQuestionGenerateDrawer`) chỉ còn công tắc Bật/Tắt duy nhất; nhãn pill hiển thị đúng `Từ điển: Bật` / `Từ điển: Tắt`.
- [x] Backend tự động nhận diện chính xác cả 11 miền từ điển (`chung` + 10 môn THPT) khi `glossary_enabled=true` kể cả khi câu hỏi không nêu tên môn, và ngắt hoàn toàn khi `glossary_enabled=false`.
- [x] Bạn xác nhận kiểm tay trên UI hoàn chỉnh đạt (`VERIFIED`).

## 4. Kiểm kế hoạch
- **`file:dòng`, tên hàm có thật:** Đã mở code kiểm tra trực tiếp từng `file:dòng` và tên hàm trong `backend/services/api/src/bookforge_api/services/school_glossary.py:691-986, 1111-1485, 1866-1909, 2096-2429`, `api/chat.py:1551-1582`, `llm/providers.py:126-130, 184-189`, `llm/pydantic_text_provider.py:177-192`, `chat/adk_agent.py:1033-1043`, `chat/de_kiem_tra_agent.py:110-128`, `chat/ma_tran_de_agent.py:556-581`, `chat/phieu_dien_khuyet_agent.py:419-443`, `chat/infographic_agent.py:1194-1218`, `chat/editor_agent.py:488-540, 617-621, 697-722, 822-826`, `chat/flow_agent.py:748-820, 1020-1036, 1184-1200`, cùng các file Frontend `Switch/index.tsx:6-29`, `agent-settings-model.ts:445-451, 688-690, 744-750`, `AgentContextSettingsDialog.tsx:112-227`, `ModalSettings/index.tsx:140-171, 1461-1518`, `MassQuestionGenerateDrawer.tsx:449-464, 819-875`, `use-chat-modes.ts:51-76`, `HomePage/index.tsx:858-865`, `use-chat-with-ai.ts:364-368`.
- **Lệnh kiểm tra chạy được:** Đã chạy thật toàn bộ các lệnh `ruff`, `pytest`, `npm run lint`, `npm run typecheck`, `npx vitest run`, `npm run build` tại `backend/services/api` và `frontend`.
- **Mục tiêu, nghiệp vụ, điều đã chốt đều có Task:** Đủ 100% (Task 1 giải quyết nhận diện tự động 11 miền theo Tình huống 2a; Task 2 giải quyết đồng bộ tất cả luồng AI theo Tình huống 3a; Task 3 giải quyết công tắc Bật/Tắt duy nhất và nhãn `Từ điển: Bật`/`Tắt` theo Tình huống 1a; Task 4 bảo đảm độ ổn định điều hướng UI sau khi chat).
- **Mọi Task có tiêu chí:** Đủ (`Thao tác tự kiểm`, `✅ Đúng khi thấy` tách rõ phần cố định 100% và phần LLM sinh tương đối, `❌ Sai nếu thấy`, `Điểm suy luận tự test thêm`, `Kiểm tra tự động`, `File và thay đổi`).
- **Cần bạn quyết:** Không có (đã chốt đủ 3 tình huống ở `analysis.md` mục 0).

## 5. Nhật ký làm
- **Kiểm tra trước khi sửa** (để phân biệt lỗi có sẵn):
  - Nhánh `feat/glossary-toggle-only` tạo từ `dev` tại backend `a5d3fce1` và frontend `6a32c01d`; chạy migration DB local `uv run alembic upgrade head` (`0128 -> 0137`) thành công.
- **Quyết định phát sinh:**
  - Chuyển quy trình quản lý công việc từ *Cách 2: Làm nhanh* sang *Cách 3: Việc thường* theo yêu cầu của bạn do phạm vi mở rộng trên nhiều màn hình Frontend và toàn bộ các luồng nhận diện tự động ở Backend.
  - Bổ sung ổn định tham chiếu trong `use-chat-modes.ts` và kiểm tra `areChatContextSettingsEqual` (Task 4) sau khi phát hiện lỗi treo điều hướng khi tự kiểm thử trên trình duyệt.
  - Đã nạp dữ liệu nền BF Token (`50,970,184`) và Credit (`100,000`) kèm `ResourceLot` hợp lệ cho tài khoản `duy@gmail.com` (cùng các tài khoản test local) để phục vụ kiểm tay.
- **Kết quả từng Task:**
  - **Task 1 & Task 2 (Backend):**
    - `cd d:\Project\bookforge\backend\services\api && uv run ruff format --check .` → `1209 files already formatted`
    - `cd d:\Project\bookforge\backend\services\api && uv run ruff check .` → `All checks passed!`
    - `cd d:\Project\bookforge\backend\services\api && uv run pytest -n 0 tests/test_school_glossary.py tests/test_question_bank_prompts.py tests/test_question_cards_generate_api.py tests/test_pydantic_text_provider.py tests/test_dich_hoc_thuat_agent.py` → `73 passed in 54.18s`
    - Tự kiểm thử gọi LLM thật trên trình duyệt local với câu hỏi trắc nghiệm *Vận dụng* nhiều tham số không ghi tên môn: khi `Từ điển: Tắt` giữ nguyên cách viết *Hacđi–Vanbec / gen / alen*; khi `Từ điển: Bật` tự động nhận diện môn Sinh học + Chung và chuẩn hóa sang *cân bằng Hardy – Weinberg / gene / allele / kiểu gene*.
  - **Task 3 & Task 4 (Frontend):**
    - `cd d:\Project\bookforge\frontend && npm run lint` → `0 errors`
    - `cd d:\Project\bookforge\frontend && npm run typecheck` → `tsc --noEmit` (exit code 0)
    - `cd d:\Project\bookforge\frontend && npx vitest run src/components/TiptapEditor/agent-settings/agent-settings-model.test.ts src/components/TiptapEditor/agent-settings/AgentSettings.test.tsx src/components/TiptapEditor/partial/document-ai-chat-panel-agent-settings.test.tsx src/hooks/use-chat-modes.test.tsx src/templates/HomePage/index.test.tsx src/templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.test.tsx` → `6 passed (47 tests)`
    - `cd d:\Project\bookforge\frontend && npm run build` → `vite build` thành công (exit code 0).

## 6. Nghiệm thu
- **Ngày:** 2026-11-12
- **Thay đổi so với kế hoạch:** Khớp đầy đủ 4 Task (13 file Backend + 14 file Frontend).
- **Từng nghiệp vụ (`analysis.md` mục 3.0, nếu có):** Không áp dụng (Cách 3: Việc thường).
- **Chạy lại toàn bộ kiểm tra:**
  - `cd d:\Project\bookforge\backend\services\api && uv run ruff check .` → `All checks passed!`
  - `cd d:\Project\bookforge\backend\services\api && uv run ruff format --check .` → `1209 files already formatted`
  - `cd d:\Project\bookforge\backend\services\api && uv run pytest -n 0 tests/test_school_glossary.py tests/test_question_bank_prompts.py tests/test_question_cards_generate_api.py tests/test_pydantic_text_provider.py tests/test_dich_hoc_thuat_agent.py` → `73 passed in 54.18s`
  - `cd d:\Project\bookforge\frontend && npm run lint` → `0 errors`
  - `cd d:\Project\bookforge\frontend && npm run typecheck` → `exit code 0`
  - `cd d:\Project\bookforge\frontend && npx vitest run ...` → `6 passed (47 tests)`
  - `cd d:\Project\bookforge\frontend && npm run build` → `vite build pass`
- **Không lọt chữ `tech_docs` vào backend / frontend:** Đã kiểm tra bằng `git -C d:\Project\bookforge\backend diff HEAD | Select-String -Pattern 'tech_docs|analysis\.md|plan\.md'` và `git -C d:\Project\bookforge\frontend diff HEAD | Select-String -Pattern 'tech_docs|analysis\.md|plan\.md'` → trống (0 kết quả).
- **Kết luận:** `VERIFIED`

## 7. Kiểm tay (Trên UI hoàn chỉnh sau khi xong hết các Task)
- **Kết quả:** Đạt hết (bạn đã xác nhận kiểm tay OK trên `http://localhost:3000`).

## 8. Commit
- **Tài liệu trong `backend/`:** Đang hỏi bạn xác nhận (`plan` / `spec` / cả 2 / không tạo).
- **Mã commit:** backend `f26feec6` · frontend `18fd8a5e` · **Đã push và merge `dev`:** Đã push nhánh `feat/glossary-toggle-only` lên `origin`; chưa merge `dev` theo yêu cầu của bạn.

## 9. Việc còn treo
- Chờ bạn xác nhận có tạo tài liệu trong `backend/` hay không và khi nào được phép merge vào `dev`.

## 10. Số đo
- **Bắt đầu:** 2026-11-12 · **Merge:** Chưa merge
- **Số lỗi bạn bắt được khi kiểm tay:** 0
- **Số lần phải sửa sau merge:** 0
