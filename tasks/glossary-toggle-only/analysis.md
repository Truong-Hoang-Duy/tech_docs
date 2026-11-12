# Tìm hiểu: Chuẩn hóa Từ điển sư phạm thành công tắc Bật/Tắt duy nhất và tự động nhận diện đa môn học

**Ngày:** 2026-11-12 · **Cách làm:** Cách 3: Việc thường · **Phía:** Cả hai
**Mốc code:** backend `a5d3fce1` · frontend `6a32c01d`
**Spec (nếu có):** Không có

## 0. Việc này sẽ làm gì
**Để làm gì:** Đơn giản hóa thao tác sử dụng **Từ điển sư phạm** trên toàn hệ thống thành một **công tắc Bật/Tắt duy nhất** (bỏ hoàn toàn bước người dùng phải tự tích chọn từng môn học), đồng thời nâng cấp bộ xử lý phía sau để tự động nhận diện môn học theo ngữ cảnh câu hỏi và áp dụng chuẩn thuật ngữ Chương trình GDPT 2018 trên cả 10 môn cấp THPT cùng bộ từ điển Sư phạm chung.

**Làm xong, ai sẽ thấy gì khác:**
| Vai trò | Trước đây | Sau khi làm |
|---|---|---|
| Giáo viên / Người dùng ở trang Trò chuyện & Trình soạn thảo | Khi mở cửa sổ cài đặt phải tự tích chọn từng thẻ môn học (*Chung*, *Toán học*, *Ngữ văn*, *Khoa học tự nhiên* hoặc mở danh sách *Khác...*). Nếu quên chọn môn hoặc đang chat ở chế độ hỏi đáp tự do, hệ thống chỉ dùng bộ từ điển Chung mà bỏ sót thuật ngữ chuyên môn của môn học. | Chỉ còn duy nhất một công tắc Bật/Tắt **Từ điển sư phạm** gọn gàng; nhãn bên dưới ô nhập tin nhắn hiển thị rõ **Từ điển: Bật** hoặc **Từ điển: Tắt**. Khi bật, dù hỏi ngắn không ghi tên môn hay dùng các trợ lý chuyên biệt, hệ thống đều tự nhận diện đúng môn để chuẩn hóa thuật ngữ và kí hiệu. |
| Giáo viên tạo câu hỏi ở Ngân hàng câu hỏi | Trong ngăn **Tạo sinh câu hỏi**, dưới công tắc Từ điển vẫn hiện thêm dãy nút chọn từ điển áp dụng gây thừa thao tác dù phía trên đã chọn Môn học và Khối lớp. | Mục **C. Từ điển sư phạm** chỉ còn một công tắc Bật/Tắt duy nhất; khi bật, hệ thống tự động lấy đúng từ điển của môn học và khối lớp đã chọn ở phần trên. |
| Quản trị viên / Người dùng chỉnh Cài đặt toàn cục | Trong mục **Ngữ cảnh & Quy chế toàn cục**, phần Từ điển mặc định hiện danh sách dài các thẻ môn học và nút chọn mở rộng. | Chỉ còn công tắc Bật/Tắt **Từ điển sư phạm mặc định** thống nhất với toàn hệ thống. |

**Lần này không làm:** Không thay đổi dữ liệu gốc của các bộ từ điển trong cơ sở dữ liệu; không thay đổi danh sách hay cách hoạt động của các quy tắc trong mục **Đường ray sư phạm** và **Quy chế nhà trường**.

**Người dùng và dữ liệu đang có bị ảnh hưởng:** Không. Các cuộc trò chuyện cũ và cài đặt mặc định đã lưu trước đây vẫn hoạt động bình thường, tự động giữ nguyên trạng thái đang Bật hoặc đang Tắt mà người dùng đã chọn.

**Bạn cần quyết:**
1. **Tình huống 1 — Nhãn hiển thị ngắn gọn trên thanh công cụ bên dưới ô nhập tin nhắn:**
   - (a) Hiển thị gọn thành **Từ điển: Bật** hoặc **Từ điển: Tắt** (bỏ hẳn kiểu liệt kê tên môn như *Từ điển: Chung*, *Từ điển: Toán học +2*) → Gọn, dễ hiểu ngay trạng thái công tắc và đồng bộ với nhãn *Đường ray: Tắt*.
   - (b) Hiển thị chữ dài như *Từ điển: Tự động (GDPT 2018)* khi bật → Chiếm diện tích thanh công cụ trên màn hình nhỏ.
   - **AI khuyên:** a, vì ngắn gọn và phản ánh đúng bản chất công tắc Bật/Tắt duy nhất · **Bạn chốt:** Chọn a
2. **Tình huống 2 — Nhận diện môn học khi câu hỏi không nhắc tên môn (ví dụ chỉ hỏi ngắn một khái niệm chuyên môn):**
   - (a) Tự động quét trên toàn bộ 11 bộ từ điển (10 môn cấp THPT + bộ Sư phạm chung), nhận diện được cả thuật ngữ khoa học một từ (như *enthalpy*, *operon*, *alkane*), cấu trúc ngữ pháp Tiếng Anh lẫn cụm thuật ngữ tiếng Việt, đồng thời chặn các từ ghép đời thường dễ trùng nghĩa để không nhận nhầm môn → Giáo viên hỏi tự nhiên không cần gõ tên môn vẫn được chuẩn hóa thuật ngữ.
   - (b) Chỉ kích hoạt từ điển môn học khi người dùng ghi rõ tên môn (như *"Môn Hóa"*, *"Sinh học 12"*), còn lại chỉ dùng từ điển Sư phạm chung → Bỏ sót phần lớn câu hỏi thực tế khi giáo viên đi thẳng vào kiến thức.
   - **AI khuyên:** a, vì sát thói quen đặt câu hỏi thực tế của giáo viên · **Bạn chốt:** Chọn a (đồng ý)
3. **Tình huống 3 — Phạm vi áp dụng tự động nhận diện từ điển ở phía máy chủ:**
   - (a) Áp dụng đồng bộ trên toàn bộ các luồng sinh nội dung có dùng Từ điển sư phạm: Trò chuyện tự do (không đính kèm tài liệu), Trò chuyện theo tài liệu, 5 Trợ lý chuyên biệt (Phiếu điền khuyết, Ma trận đề, Tạo đề kiểm tra, Dịch học thuật, Infographic), Trợ lý trong Trình soạn thảo & Sơ đồ tư duy, và Tạo sinh câu hỏi ở Ngân hàng câu hỏi → Bật/Tắt công tắc có hiệu lực nhất quán ở mọi nơi.
   - (b) Chỉ áp dụng ở Trò chuyện theo tài liệu và Ngân hàng câu hỏi → Khi hỏi đáp tự do vẫn bị sót thuật ngữ chuẩn.
   - **AI khuyên:** a, để hành vi Bật/Tắt nhất quán tuyệt đối trên toàn nền tảng · **Bạn chốt:** Chọn a (đồng ý)

**Làm xong, bạn sẽ thấy nó chạy thế nào:** Trên khung trò chuyện, trình soạn thảo, cài đặt tài khoản và ngăn tạo câu hỏi hàng loạt, mục **Từ điển sư phạm** chỉ còn một công tắc gạt Bật/Tắt. Khi gạt **Bật**, bạn thử gửi một câu hỏi kiến thức hoặc câu trắc nghiệm dùng cách viết cũ mà không ghi tên môn, câu trả lời sinh ra sẽ tự động chuẩn hóa về đúng thuật ngữ và kí hiệu Chương trình GDPT 2018; khi gạt **Tắt**, hệ thống không áp bộ quy chuẩn từ điển lên câu trả lời.

**So với nghiệp vụ đã có:** Giữ: Kho dữ liệu Từ điển SGK 10 môn THPT + Sư phạm chung và toàn bộ cơ chế Đường ray sư phạm · Đổi: Chuyển giao diện chọn thủ công từng môn từ điển sang công tắc Bật/Tắt duy nhất trên cả 3 màn hình; nâng cấp cơ chế tra cứu từ lọc cứng theo mã môn người dùng chọn sang tự động nhận diện đa môn theo ngữ cảnh · Thêm: Khả năng nhận diện thuật ngữ đơn khoa học/tiếng Anh, bộ lọc chống nhận nhầm từ đời thường, và kết nối từ điển vào luồng Trò chuyện tự do cùng Trình soạn thảo/Sơ đồ tư duy.

---
*(Từ mục 1 trở xuống là phần kỹ thuật cho agent.)*

## 1. Mục tiêu và phạm vi
- **Cần đạt:**
  1. Thu gọn toàn bộ giao diện cấu hình **Từ điển sư phạm** trên Frontend (`AgentContextSettingsDialog`, `ModalSettings`, `MassQuestionGenerateDrawer`) thành công tắc Bật/Tắt duy nhất (`glossary_enabled: boolean`), bỏ toàn bộ chip chọn môn lẻ (`Chung`, `Toán học`, `Ngữ văn`, `Khoa học tự nhiên`, dropdown `Khác...`) và đổi nhãn pill sang `Từ điển: Bật` / `Từ điển: Tắt`.
  2. Xây dựng bộ máy tự động nhận diện môn học và tra cứu thuật ngữ trên toàn bộ 11 miền (`chung` + 10 môn THPT) trong `SchoolGlossaryService` (`resolve_auto_glossary_terms`, `resolve_auto_glossary_prompt_block`, `resolve_question_bank_glossary`), nhận diện chính xác cả khi câu hỏi không nêu tên môn (kể cả thuật ngữ khoa học 1 từ như `enthalpy`, tiêu đề ngữ pháp Tiếng Anh có dấu `:`, câu hỏi nhiều tham số) và chặn dương tính giả trên câu giao tiếp đời thường hoặc từ ghép trùng âm (`thuật toán`, `an toàn`, `mũ bảo hiểm`, `tính chất vật lí`, `bối cảnh lịch sử`).
  3. Đồng bộ bơm khối `<school_glossary>` khi `glossary_enabled=True` (và ngắt hoàn toàn khi `glossary_enabled=False`) trên tất cả các luồng AI: `_run_free_chat`, `_build_chat_agent` (`adk_agent.py`), 5 Agent chuyên biệt (`de_kiem_tra_agent.py`, `ma_tran_de_agent.py`, `phieu_dien_khuyet_agent.py`, `infographic_agent.py`, `dich_hoc_thuat_agent.py`), `editor_agent.py`, `flow_agent.py` và `POST /api/question-cards/generate`.
- **Không làm:**
  - Không thay đổi schema bảng `school_glossary_chapters`, `school_glossary_terms` hay bộ dữ liệu JSON gốc trong `bookforge_api/data/glossary/`.
  - Không thay đổi logic kiểm duyệt của `generative_rails` / `school_rules`.

## 2. Hiện trạng (kèm `file:dòng`)
- **Luồng hiện tại & nguyên nhân hạn chế trước khi sửa:**
  1. **Giao diện Frontend bắt người dùng chọn thủ công `glossary_ids` trên 3 màn hình:**
     - `frontend/src/components/TiptapEditor/agent-settings/AgentContextSettingsDialog.tsx:210-370` (trước sửa): Render khu vực `Chọn từ điển áp dụng` gồm các chip `primaryGlossaries` và menu mở rộng `Khác...` (`extraGlossaries`).
     - `frontend/src/components/ModalSettings/index.tsx:1423-1655` (trước sửa): `GlobalContextSettingsPanel` render khu vực `Chọn từ điển áp dụng mặc định` với danh sách chip môn học và popover `Khác...`.
     - `frontend/src/templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.tsx:192-247, 898-985` (trước sửa): Mục `C. Từ điển sư phạm` vẫn duy trì state `glossaryIds` và danh sách chip chọn môn thủ công dù người dùng đã chọn `Môn học *` và `Khối/lớp *` ở mục `A. Cấu hình chung`.
     - `frontend/src/components/TiptapEditor/agent-settings/agent-settings-model.ts:686-756` (trước sửa): `isGlossaryActive` kiểm tra `settings.glossary_enabled && settings.glossary_ids.length > 0`, còn `formatGlossaryPillLabel` ghép tên từng môn (`Từ điển: Chung`, `Từ điển: Toán học +1`).
  2. **Điểm yếu ở Backend khi bỏ chọn môn thủ công (`glossary_ids` mặc định chỉ còn `["chung"]` hoặc `None`):**
     - `backend/services/api/src/bookforge_api/api/chat.py:1551-1580` (`_run_free_chat`): Trước đây chỉ gọi `lookup_text_glossary(..., glossary_ids=ctx_settings.glossary_ids)` (nên khi mặc định `["chung"]` sẽ bỏ sót toàn bộ 10 môn THPT) và nối `glossary_block` vào chuỗi `fallback_reason` thay vì truyền vào `instructions` của `PydanticAITextProvider.answer_without_context` (`llm/pydantic_text_provider.py:177-195`).
     - `backend/services/api/src/bookforge_api/chat/adk_agent.py:1033-1043`, `de_kiem_tra_agent.py:110-128`, `ma_tran_de_agent.py:556-581`, `phieu_dien_khuyet_agent.py:419-443`, `infographic_agent.py:1194-1218`: Phụ thuộc vào `context_settings.glossary_ids` nên không tự mở rộng sang môn học thực tế của câu hỏi khi `glossary_ids == ["chung"]`.
     - `backend/services/api/src/bookforge_api/chat/editor_agent.py:488-540, 698-825` và `chat/flow_agent.py:748-820, 984-1036, 1139-1200`: Chưa tự động tra cứu `<school_glossary>` từ nội dung tài liệu/yêu cầu biên tập khi `glossary_enabled=True`.
     - `backend/services/api/src/bookforge_api/services/school_glossary.py:691-1085` (`_AcademicGlossaryIndex`): Chưa tách biến thể trước dấu `:` (như `"Relative clauses: mệnh đề quan hệ..."`), chưa nhận diện thuật ngữ khoa học vay mượn 1 từ trong câu tiếng Việt (như `"Giải thích ngắn gọn khái niệm enthalpy"`), và dễ khớp nhầm từ đơn tiếng Việt không dấu với mục từ Tiếng Anh hoặc khớp nhầm hậu tố trong từ ghép (`mũ bảo hiểm` khớp `Bảo hiểm`).
  3. **Vòng lặp render lại trên thanh điều hướng trang Chat:**
     - `frontend/src/hooks/use-chat-modes.ts:51-76`: Mảng `modes`, `experts`, `agents` tạo mới mỗi lần render kết hợp với `setContextSettings` không so sánh sâu ở `HomePage/index.tsx:858-865` và `use-chat-with-ai.ts:363-368` có thể gây `Maximum update depth exceeded` khi chuyển tab trên sidebar sau khi vừa chat xong.

## 3. Kiểm tra spec (chỉ việc có spec, xem `spec-check.md`; việc khác ghi "Không áp dụng")
Không áp dụng.

## 4. Điểm va chạm
- **Tương thích ngược hợp đồng API & dữ liệu phiên chat cũ (`context_settings_json`):**
  - Giữ nguyên trường `glossary_ids: list[str]` trong schema `ChatContextSettings` (`schemas/chat.py`) và `toChatContextSettings` (`agent-settings-model.ts:445-451`, tự điền `["chung"]` khi `dictionaryEnabled=true` và mảng rỗng) để tương thích ngược 100% với các bản ghi `chat_sessions.context_settings_json`, `user_preferences` cũ và các test contract hiện có (`test_api_contract_generator.py`).
  - Ở phía Backend, khi `glossary_enabled=True`, `resolve_auto_glossary_prompt_block` và `resolve_question_bank_glossary` (`school_glossary.py:1866-1872, 2096-2428`) tự động suy luận trên toàn bộ 11 miền dữ liệu kể cả khi client không gửi `glossary_ids` hoặc gửi `glossary_ids=["chung"]`.
- **Tương thích chữ ký hàm `provider.answer_without_context` trong các test giả lập (`FakeProvider` / `NullTextProvider`):**
  - Nhiều unit test cũ tạo mock provider có chữ ký `answer_without_context(question, fallback_reason)` không nhận `glossary_section`. Do đó tại `api/chat.py:1562-1571`, dùng `inspect.signature(provider.answer_without_context)` kiểm tra trước khi truyền `glossary_section` (và bổ sung `glossary_section: str = ''` vào `TextProvider`, `NullTextProvider` tại `llm/providers.py:127, 186` cùng `PydanticAITextProvider` tại `llm/pydantic_text_provider.py:178-190`).
- **Chống nhận nhầm môn học (False Positives) khi quét tự động 11 miền:**
  - Các từ chỉ định đề bài chung (`khái niệm`, `giải thích`, `vận dụng`, `nhận biết`, `thông hiểu`), tên môn xuất hiện trong cụm phi chuyên môn (`tính chất vật lí` trong Hóa học, `bối cảnh lịch sử` trong Ngữ văn, `thuật toán` trong Toán/Tin, `an toàn` không chứa môn `toán`, `mũ bảo hiểm` không khớp mục từ kinh tế `Bảo hiểm`, `nhân ngày 20/11` không khớp `Nhân tế bào`) phải được chặn bằng quy tắc ngôn ngữ học tổng quát trong `school_glossary.py:805-986, 1111-1255` thay vì hardcode câu test.

## 5. Phương án đề xuất
1. **Tại `services/school_glossary.py`:**
   - Mở rộng `extract_headword_variants` (`school_glossary.py:691-788`) tách phần đầu trước dấu `:` cho các mục từ ngữ pháp Tiếng Anh; bổ sung phân loại từ đơn khoa học/tiếng nước ngoài (`_is_scientific_or_foreign_single_word`, `_count_vowel_clusters`) để khớp chính xác các thuật ngữ đơn như `enthalpy`, `operon`, `ester`, `alkane`, `allele`, `gene` trong câu tiếng Việt mà không để từ Việt có dấu khớp nhầm mục từ Tiếng Anh không dấu.
   - Bổ sung bộ nhận diện môn học theo ngữ cảnh (`_detect_curriculum_subject_in_text`), kiểm tra ranh giới từ ghép tiếng Việt (`_has_false_vi_compound_boundary`), trọng số bỏ phiếu áp đảo 2/3 (`cnt * 3 >= max_vote * 2`) trong `resolve_auto_glossary_terms` (`school_glossary.py:2096-2410`) và mở rộng thuật ngữ cùng bài học (`anchor_lessons`) để câu hỏi ngắn vẫn lấy đủ hệ thuật ngữ chuẩn của bài.
2. **Tại các luồng AI Backend (`api/chat.py`, `llm/`, `chat/*_agent.py`):**
   - Chuyển toàn bộ các điểm lấy ngữ cảnh từ điển sang `resolve_auto_glossary_prompt_block` / `resolve_auto_glossary_terms` (tôn trọng tuyệt đối cờ `glossary_enabled`); truyền `glossary_section` vào system `instructions` của `PydanticAITextProvider.answer_without_context`; bổ sung bơm `<school_glossary>` cho `editor_agent.py` và `flow_agent.py`; tự động nâng cấp `glossary_ids=None` hoặc `['chung']` sang đúng môn học trong `resolve_question_bank_glossary`.
3. **Tại giao diện Frontend (`Switch`, `AgentContextSettingsDialog`, `ModalSettings`, `MassQuestionGenerateDrawer`, `agent-settings-model`, `use-chat-modes`, `HomePage`):**
   - Bổ sung thuộc tính `disabled` cho `Switch` (`Switch/index.tsx:7-28`); rút gọn cả 3 màn hình cấu hình Từ điển về duy nhất 1 `Switch` Bật/Tắt; cập nhật `isGlossaryActive` và `formatGlossaryPillLabel` trả về `"Từ điển: Bật"` / `"Từ điển: Tắt"`; bọc `useMemo` cho danh sách trong `use-chat-modes.ts` và kiểm tra `areChatContextSettingsEqual` trước khi `setContextSettings` ở `HomePage` / `use-chat-with-ai`.

## 6. Câu hỏi kỹ thuật còn mở
Không có (toàn bộ 3 tình huống nghiệp vụ ở mục 0 đã được bạn chốt).
