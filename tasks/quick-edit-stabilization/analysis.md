# Tìm hiểu: Ổn định & Hoàn thiện Bộ Công cụ AI Biên tập Nhanh trên Canvas

**Ngày:** 2026-11-18 · **Cách làm:** Cách 3: Việc thường · **Phía:** Cả hai
**Mốc code:** backend `5fbd25ce` · frontend `e22a99b9`
**Spec (nếu có):** Không có (Tài liệu tham khảo: `tech_docs/research/writing-block.md`, `tech_docs/research/bao-cao-ai-quick-edit.md`)

## 0. Việc này sẽ làm gì
**Để làm gì:** Khắc phục tình trạng thiếu ổn định ở bộ 5 công cụ AI biên tập nhanh khi quét chọn văn bản trên trình soạn thảo tài liệu (Sửa chính tả, Chỉnh diễn đạt, Rút gọn, Viết tiếp, Viết theo yêu cầu), đồng thời hoàn thiện khả năng tự nhận diện Từ điển Sư phạm theo nội dung bài học, bảo toàn công thức Toán học và định dạng xuống dòng khi xem trước/áp dụng.

**Làm xong, ai sẽ thấy gì khác:**
| Vai trò | Trước đây | Sau khi làm |
|---|---|---|
| Giáo viên dùng 5 công cụ AI chuột phải trên trình soạn thảo | Chọn **Rút gọn** trên câu vốn đã ngắn thì bị cắt cụt mất động từ/ý nghĩa hoặc lộ ký tự gạch đứng `\|`; chọn **Viết theo yêu cầu** để dịch sang tiếng Anh lại ra câu lai nửa Anh nửa Việt; **Chỉnh diễn đạt** đôi lúc viết hoa vô lý giữa câu; **Sửa chính tả** chưa bảo vệ hết thuật ngữ chuyên môn ngay từ đầu. | **Rút gọn** luôn cho kết quả ngắn gọn hơn đoạn dài hoặc giữ nguyên câu đã tối giản (không cắt cụt mất nghĩa, không lộ ký tự kỹ thuật); **Viết theo yêu cầu** thực hiện đúng lệnh định dạng/dịch thuật mà không bị khóa chữ tiếng Việt cản trở (và nhớ gợi ý trước khi đổi yêu cầu nối tiếp); **Chỉnh diễn đạt**, **Viết tiếp**, **Sửa chính tả** bám đúng ý, bảo toàn thuật ngữ và không thêm lỗi viết hoa. |
| Giáo viên biên tập bài học có thuật ngữ & công thức Toán | Nếu tiêu đề tài liệu không ghi rõ tên môn học (ví dụ *"Bài 5: Quang hợp ở thực vật"*), hệ thống bỏ sót toàn bộ thuật ngữ môn Sinh học. Khi quét chọn đoạn có công thức Toán hoặc nhiều gạch đầu dòng, công thức bị xóa mất trắng khi thay thế và các dòng bị gộp dính thành một dòng ngang. | Hệ thống tự nhận diện đúng môn học ngay từ nội dung bài học để bảo vệ chuẩn thuật ngữ Sách giáo khoa (và không áp nhầm vào văn bản đời thường). Công thức Toán học và cấu trúc xuống dòng/gạch đầu dòng được giữ nguyên vẹn từ lúc xem trước đến lúc thay thế vào tài liệu. |
| Giáo viên xem lại kết quả trên bảng xem trước | Dòng thông báo bên dưới đôi lúc vẫn ghi *"Đã rút gọn"* dù kết quả chưa đạt; ở mục **Viết theo yêu cầu**, gõ lệnh sửa nối tiếp lần hai không bám theo gợi ý vừa tạo. | Giữ nguyên bố cục 3 nút gọn chuẩn thiết kế cho 4 công cụ đầu; thông báo trạng thái phản ánh trung thực kết quả; mục **Viết theo yêu cầu** khi đổi sang lệnh mới sẽ tinh chỉnh nối tiếp ngay trên gợi ý hiện có. |

**Lần này không làm:** Không sửa dữ liệu gốc của bộ Từ điển Sách giáo khoa; không thêm nút mới vào chân bảng xem trước của 4 công cụ đầu; không sửa khung công cụ AI riêng trên trang trình chiếu Slide (tách sang một việc riêng); không mở khóa lại menu AI chuột phải trong các ô nhập nhỏ của Sơ đồ tư duy; không sửa luồng trò chuyện dài bên khung trợ lý chat chính.

**Người dùng và dữ liệu đang có bị ảnh hưởng:** Không. Các tài liệu, bài thuyết trình và cuộc trò chuyện đã lưu vẫn giữ nguyên toàn bộ.

**Bạn cần quyết:**
1. **Tình huống 1 — Cách bật/tắt Từ điển Sư phạm cho 5 công cụ chuột phải trên trình soạn thảo (tránh bị lệch khi người dùng đổi công tắc ở khung Chat chính bên ngoài):**
   - (a) Tự động ngầm 100% theo nội dung bài học (độc lập với công tắc ở khung Chat): hễ nhận ra đoạn văn thuộc môn học phổ thông thì tự bảo vệ thuật ngữ chuẩn, còn văn bản hành chính/đời thường thì tự bỏ qua → Giáo viên không cần bấm bật/tắt thêm bước nào và không lo tắt nhầm ở một cuộc trò chuyện bên ngoài làm hỏng phần biên tập tài liệu.
   - (b) Đi theo công tắc "Từ điển" ở cột Trợ lý Soạn thảo nằm ngay bên phải màn hình tài liệu (nếu chưa chỉnh riêng thì lấy theo Cài đặt chung của cá nhân / nhà trường), tách biệt hoàn toàn với khung Chat chính bên ngoài → Cho phép giáo viên tự tắt thủ công trên trình soạn thảo, nhưng nếu đang thu gọn cột phải thì dễ quên trạng thái đang bật hay tắt.
   - **AI khuyên:** a, vì 5 công cụ chuột phải là tiện ích chỉnh sửa tại chỗ không nên tăng bước thao tác bật/tắt thủ công · **Bạn chốt:** Chọn (a) — tự động ngầm 100% theo nội dung bài học, độc lập với công tắc ở khung Chat.
2. **Tình huống 2 — Khi bấm "Rút gọn" trên một câu hoặc tiêu đề vốn đã rất ngắn, không còn từ thừa (ví dụ câu mục tiêu bài học 4–6 từ):**
   - (a) Giữ nguyên câu gốc và báo nhẹ *"Đoạn văn đã ngắn gọn, không cần rút gọn thêm"* → Không cắt mất động từ quan trọng (như làm mất chữ *"Nêu"* trong mục tiêu bài học), không viết cụt lủn và không bao giờ diễn giải dài thêm.
   - (b) Luôn ép AI phải bỏ bớt chữ bằng mọi giá → Dễ làm gãy ngữ pháp, viết kiểu điện tín hoặc làm mất ý nghĩa sư phạm của câu ngắn.
   - **AI khuyên:** a, vì bảo toàn an toàn ý nghĩa cho tiêu đề, định nghĩa và câu ngắn chuẩn · **Bạn chốt:** Chọn (a) — giữ nguyên câu gốc đã tối giản và báo nhẹ không cần rút gọn thêm.
3. **Tình huống 3 — Cách xử lý thao tác "Tinh chỉnh" (nhập yêu cầu sửa tiếp dựa trên kết quả AI vừa sinh):**
   - (a) Thêm nút **Tinh chỉnh** vào chân bảng xem trước của 4 công cụ đầu; bấm vào mới mở ô nhập yêu cầu bổ sung (tăng chân bảng từ 3 nút lên 4 nút).
   - (b) Luôn mở sẵn ô nhập yêu cầu ngay từ đầu cho cả 5 công cụ.
   - (c) Giữ nguyên thiết kế 3 nút gọn hiện tại cho 4 công cụ đầu (`Thử lại`, `Bỏ qua`, `Thay thế`/`Chèn sau` + bấm vào sửa tay); chỉ ở công cụ thứ 5 (**Viết theo yêu cầu**), khi đổi câu yêu cầu mới trên kết quả đang hiển thị thì truyền kèm gợi ý hiện tại để AI sửa nối tiếp.
   - **AI khuyên:** c nếu ưu tiên giữ nguyên bố cục 3 nút chuẩn thiết kế hiện tại; a nếu muốn mở nút riêng như tài liệu cũ · **Bạn chốt:** Chọn (c) — giữ nguyên bố cục 3 nút cho 4 công cụ đầu, chỉ nối ngữ cảnh gợi ý trước khi đổi lệnh trong **Viết theo yêu cầu**.
4. **Tình huống 4 — Có gộp sửa luôn lỗi nút "Rút gọn" trên khung sửa nhanh của bài thuyết trình (Slide) trong lần này không?**
   - (a) Gộp sửa luôn trong đợt này để nút **Rút gọn** trên Slide thực sự thu gọn văn bản.
   - (b) Chỉ xử lý bộ 5 công cụ chuột phải trên trình soạn thảo tài liệu, tách phần Slide sang một việc riêng.
   - **AI khuyên:** a, hoặc tách riêng nếu muốn thu hẹp phạm vi · **Bạn chốt:** Chọn (b) — chỉ làm trên trình soạn thảo tài liệu Canvas, tách phần Slide sang việc riêng.

**Làm xong, bạn sẽ thấy nó chạy thế nào:** Mở một tài liệu giáo án có công thức Toán học và thuật ngữ chuyên môn (kể cả khi tiêu đề không ghi tên môn), bôi đen một đoạn và bấm chuột phải chọn **Công cụ AI**: chọn **Rút gọn** thì câu dài được cô đọng rõ rệt còn câu tối giản được giữ nguyên an toàn; chọn **Viết theo yêu cầu** để dịch sang tiếng Anh hay gạch đầu dòng vẫn giữ đúng yêu cầu, và nếu gõ yêu cầu sửa tiếp lần hai thì AI sửa nối tiếp trên bản gợi ý đang thấy; khi bấm **Thay thế**, công thức Toán học và xuống dòng được giữ nguyên vẹn trên trang tài liệu.

**So với nghiệp vụ đã có:** Giữ: Danh mục đúng 5 công cụ trong menu chuột phải, bố cục 3 nút chân bảng của 4 công cụ đầu, bảng xem trước tại chỗ, cơ chế chống ghi đè nhầm khi người dùng đang gõ · Đổi: Chuẩn hóa yêu cầu và hậu kiểm cho từng công cụ (bỏ ép rút gọn câu tối giản, bỏ khóa cứng tiếng Việt khi dịch thuật, sửa chuẩn hóa viết hoa sai, tự thử lại khi sai lệch độ dài/lặp ý), nâng cấp nhận diện môn học tự động cho Từ điển Sư phạm, giữ công thức Toán học và cấu trúc xuống dòng khi chọn/áp dụng · Thêm: Kế thừa gợi ý hiện tại khi đổi lệnh mới ở công cụ **Viết theo yêu cầu**.

---
*(Từ mục 1 trở xuống là phần kỹ thuật cho agent.)*

## 1. Mục tiêu và phạm vi
- **Cần đạt:**
  1. **Ổn định toàn diện 5 công cụ Quick Edit (Backend — Prompt, Model Settings & Output Rails):**
     - Tách riêng ràng buộc theo từng công cụ trong `quick_edit_rails.py` và `editor_tools.py` (loại bỏ ghép chỉ dẫn mâu thuẫn; không dùng dấu phân cách `' | '` dễ rò rỉ sang output AI; không tiêm `normalization_hints` vào `shorten` khi làm dài câu; cho phép `custom` dịch ngoại ngữ / xuất markdown danh sách theo đúng lệnh người dùng mà không bị `QUY TẮC CHUNG` / khóa từ tiếng Việt cản trở; truyền danh sách thuật ngữ bảo vệ trực tiếp vào lần gọi đầu của `spellcheck`).
     - Nâng cấp kiểm soát độ dài và vòng lặp retry nội bộ (`_run_quick_edit` trong `assistant_tools.py`): giới hạn `max_output_tokens` hợp lý cho `shorten`/`refine`, nâng các vi phạm bản chất công cụ (`not_shorter`, `too_long`, `repeats_original`) thành kích hoạt retry có chỉ dẫn sửa cụ thể, lọc sạch thẻ ẩn `<!--BF_GOV:...-->`, xử lý lặp bán phần ở `continue`, sửa cảnh báo `temperature` khi dùng model reasoning trong `pydantic_text_provider.py`.
     - Giữ nguyên câu vốn đã tối giản khi gọi `shorten` và trả trạng thái `no_change` với thông điệp nhẹ nhàng (theo quyết định Tình huống 2.a).
  2. **Hoàn thiện tích hợp Từ điển Sư phạm & SGK tự động ngầm (Backend — Tình huống 1.a):**
     - Nâng cấp `SchoolGlossaryPedagogicalDictionary` và `_enrich_quick_edit_payload` để: (i) thêm `title` vào `QuickEditDocMetadata`; (ii) bổ sung nhận diện môn học đa tầng dựa trên `SchoolGlossaryService._get_academic_glossary_index().scan_passage()` + `expand_glossary_domains` (hỗ trợ môn tổ hợp và tài liệu không ghi tên môn ở tiêu đề, kèm ngưỡng chống dương tính giả trên văn bản đời thường); (iii) sửa lỗi viết hoa đầu từ giữa câu khi chuẩn hóa đồng nghĩa (`normalization_hints`).
     - Giữ cơ chế tự động ngầm 100% theo nội dung bài học trên Quick Edit, độc lập với công tắc ở Chat chính (không thêm `context_settings`).
  3. **Bảo toàn Công thức Toán học (KaTeX), Cấu trúc Đoạn/Danh sách & Chèn "Viết tiếp" trên Canvas (Frontend):**
     - Trong `quick-edit-core.ts` và `assistant-editor-actions.ts`: serialize đầy đủ node `inlineMath` (`$...$`) và `blockMath` (`$$...$$`) cũng như ranh giới block (`\n`) khi chụp vùng chọn (`captureQuickEditSelection`) và đối chiếu vị trí (`locateQuickEditRange` / `rangeText`); phân tích ngược `$...$` / `$$...$$` và cấu trúc xuống dòng thành ProseMirror `inlineMath`/`blockMath` + block nodes khi `applyReplacement` / `insertBelow` (giữ hoàn tác `Ctrl+Z` 1 bước); hoàn thiện xử lý dấu câu cho `continueAtSelection` (`.,;:!?)]`).
     - Render công thức KaTeX an toàn trong `QuickEditPanel.tsx` khi xem trước và cập nhật `describeQuickEditResult` trung thực theo `status`/`warnings`, bật highlight diff đề xuất cho `shorten`.
  4. **Kế thừa gợi ý trước cho "Viết theo yêu cầu" mà giữ nguyên bố cục 3 nút cho 4 công cụ đầu (Frontend — Tình huống 3.c):**
     - Trong `use-quick-edit.ts`, khi người dùng đang ở bảng kết quả của `custom` và nhập `instruction` mới khác lần vừa chạy, truyền `previous_suggestion: panel.review.draft` lên `APIQuickEdit` để AI sửa nối tiếp trên gợi ý hiện có (giữ nguyên lệnh bấm `Thử lại` thì vẫn sinh phương án mới từ bản gốc). Không thay đổi bố cục 3 nút chân bảng của 4 công cụ đầu trong `QuickEditPanel.tsx`.
- **Không làm:**
  - Không sửa khung công cụ AI riêng trên Slide / `ToolbarAiMenu` (`ppt-slide-editor-popover.tsx`, `assistant-tool-definitions.ts`) — tách sang việc riêng (Tình huống 4.b).
  - Không thêm nút "Tinh chỉnh" vào footer 4 công cụ đầu trong `QuickEditPanel.tsx` (Tình huống 3.c).
  - Không thêm `context_settings` vào `QuickEditRequest` (Tình huống 1.a).
  - Không thay đổi seed JSON từ điển (`data/glossary/*.json`) hay tạo migration Alembic mới.
  - Không mở khóa Quick Edit trên `FlowNodeTitleInput.tsx` / `FlowNodeDescriptionEditor.tsx` (đang đặt `aiLocked` có chủ đích).
  - Không thay đổi cơ chế trừ ví BFT, bảng `AIAction` hay idempotency của `assistant_tools.py`.

## 2. Hiện trạng (kèm `file:dòng`)
- **Luồng hiện tại:**
  - *Canvas Quick Edit (5 công cụ chuột phải / `Alt + /`):* Người dùng bôi đen trên Tiptap → `TiptapEditor/index.tsx:605-624` mở `QuickEditOverlay.tsx` → `use-quick-edit.ts:100-195` gọi `captureQuickEditSelection` (`quick-edit-core.ts:60-95`) và gửi `POST /api/assistant-tools/quick-edit` (`api/assistant-tools-api.ts:172-174`) → `api/assistant_tools.py:724-763` làm giàu metadata (`_enrich_quick_edit_payload` tại `685-721`) rồi gọi `_run_quick_edit` (`658-682`) chạy `build_input_rails` → `prov.spellcheck` / `prov.editor_rewrite` (`pydantic_text_provider.py:299-361`) → `evaluate_provider_output` (`quick_edit_rails.py:1093-1112`) → `assemble_response` (`1125-1145`) → `QuickEditPanel.tsx` hiển thị và gọi `applyQuickEditSuggestion` (`quick-edit-core.ts:143-163`).
  - *ToolbarAiMenu / Slide Popover (`ppt-slide-editor-popover.tsx`):* `ppt-slide-editor-popover.tsx:233-268` gọi `runAssistantTool` (`assistant-tool-definitions.ts:143-275`) sang các route mini-tool cũ (`/spellcheck`, `/summarize`, `/continue-writing`, `/style-rewrite`, `/rewrite`).
- **Chỗ cần sửa / nguyên nhân (kèm số liệu đo thực tế trên nhánh `dev`):**
  1. **`shorten` viết dài ra / cắt cụt mất nghĩa / lộ ký tự kỹ thuật:**
     - `frontend/src/components/TiptapEditor/partial/assistant-tool-definitions.ts:200-207`: Khi `toolId === "shorten"`, Slide Popover (`ppt-slide-editor-popover.tsx:245`) và `ToolbarAiMenu` gọi `APISummarizeText` → `editor_tools.py:360` ép *"summary nên dài khoảng 2-5 câu"*. Đo thực tế câu 12 từ (47 ký tự) bị viết thành 30 từ (129 ký tự, dài gấp 2,7 lần).
     - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:76-79, 720-726, 808`: `_TOOL_TASKS['shorten']` ép *"Kết quả phải ngắn hơn văn bản được chọn"* mà không cho phép giữ nguyên câu đã tối giản; `_build_custom_query` nối `GIỮ NGUYÊN CÁC MỤC SAU` bằng `' | '` (`dòng 721`) nên đo thực tế câu *"Năm 1945, Việt Nam giành độc lập."* trả về `"1945 | Việt Nam giành độc lập."`; `normalization_hints` vẫn được truyền vào `shorten` (`dòng 808`).
     - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:925-930` & `api/assistant_tools.py:642, 675-679`: `not_shorter` chỉ là `warning`, nên `_run_quick_edit` (`if not evaluated.has_error: break`) không hề retry khi kết quả dài hơn bản gốc; `_QUICK_EDIT_OUTPUT_TOKEN_CAPS` (`assistant_tools.py:642`) chỉ giới hạn `'continue': 600`.
     - `frontend/src/components/TiptapEditor/quick-edit/quick-edit-core.ts:266-267`: `describeQuickEditResult` luôn hiển thị *"Đã rút gọn, giữ nguyên ý chính."* bất kể `warnings` có `not_shorter` hay `too_long`.
  2. **Prompt mâu thuẫn, viết hoa sai, dịch thuật bị kẹt tiếng Việt, lộ thẻ nội bộ, cảnh báo temperature:**
     - `backend/services/api/src/bookforge_api/llm/editor_tools.py:165-175, 295-301, 365-377`: `editor_rewrite_user_prompt` luôn chèn `rewrite_instruction(option, custom_query)` chồng lên `custom_query` của rails; `editor_rewrite_system_prompt` (`dòng 369`) truyền `surface='editor'` vào `build_governance_instruction` (`chat/governance.py:148, 172-174`) khiến LLM được phép sinh `<!--BF_GOV:...-->`, trong khi `quick_edit_rails.py:843-867` (`sanitize_output`) chưa lọc thẻ này.
     - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:710-721`: `QUY TẮC CHUNG` áp đặt chung *"không dùng markdown"*, *"giữ nguyên ... thuật ngữ"* và `chat/governance.py:107` đặt *"Mặc định trả lời bằng tiếng Việt"* ngay cả với `tool == 'custom'`. Đo thực tế lệnh *"Dịch đoạn này sang tiếng Anh"* trên câu Sinh học trả về `"The process of quang hợp takes place in lục lạp..."` vì bị khóa thuật ngữ tiếng Việt.
     - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:45, 864-866, 903-924`: `DEFAULT_MIN_OUTPUT_CHARS = 400` khiến đoạn 40–100 ký tự phình gấp 3–5 lần vẫn qua; `sanitize_output` chỉ cắt lặp ở `continue` khi khớp trọn `text.startswith(original)` từ đầu.
     - `backend/services/api/src/bookforge_api/llm/pydantic_text_provider.py:86, 304`: Truyền cứng `temperature=0.4` cho model reasoning OpenAI (`gpt-5.6-luna`), gây `UserWarning` khi chạy thật.
  3. **Từ điển Sư phạm trong Quick Edit & Sửa chính tả:**
     - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:191-251, 372-415`: `infer_subject_and_grade_from_context` chỉ dùng regex tường minh tên môn (thiếu môn gộp, bỏ sót bài học không ghi tên môn ở tiêu đề — đo thực tế tiêu đề *"Bài 5: Quang hợp ở thực vật"* nhận `0` thuật ngữ thay vì `4` thuật ngữ như khi có chữ *"Sinh học 11"*). Dòng `374` đọc `doc_metadata.get('title')` nhưng `schemas/assistant_tools.py:114-128` (`QuickEditDocMetadata`) chưa có trường `title` và đặt `extra='ignore'`.
     - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:454-457`: `normalization_hints` chèn nguyên chuỗi `entry.term` viết hoa chữ cái đầu mục (ví dụ `"Chu trình C₃"`, `"Hợp chất hữu cơ"`), dẫn đến đo thực tế xuất hiện `"...tạo ra Hợp chất hữu cơ cho cây."` giữa câu.
     - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:778-794` & `llm/editor_tools.py:304-323`: `spellcheck` lần 1 bỏ qua `protected.terms` trong prompt, chỉ hậu kiểm `.replace(..., 1)` (`quick_edit_rails.py:1081-1084`).
     - `backend/services/api/src/bookforge_api/schemas/assistant_tools.py:131-142`, `api/assistant_tools.py:724-763`, `frontend/src/components/TiptapEditor/quick-edit/use-quick-edit.ts:165-173`: Chưa nối `context_settings` / `resolve_effective_context_settings` (`services/regulations.py:782-791`) nếu đi theo công tắc bật/tắt.
  4. **Công thức Toán học (KaTeX), xuống dòng & UX Tinh chỉnh trên Canvas:**
     - `frontend/src/components/TiptapEditor/extensions.ts:387-398`, `quick-edit/quick-edit-core.ts:68, 101, 143-163`, `partial/assistant-editor-actions.ts:155-197`: `InlineMath`/`BlockMath` có `atom: true` và không có `renderText`, nên `doc.textBetween(from, to, " ")` xóa trắng mọi node công thức và gộp dính các đoạn/gạch đầu dòng thành một dòng ngang. `applyReplacement` và `QuickEditPanel.tsx:459-463, 504-512` không parse/render `$...$` / `$$...$$`, làm mất node Toán khi bấm Thay thế.
     - `frontend/src/components/TiptapEditor/partial/assistant-editor-actions.ts:272-274`: `continueAtSelection` chỉ tránh thêm khoảng trắng cho `.` và `,` (thiếu `; : ! ? ) ]`).
     - `frontend/src/components/TiptapEditor/quick-edit/use-quick-edit.ts:165-173, 225-260` & `QuickEditPanel.tsx:515-535, 626-684`: Chưa truyền `previous_suggestion` và chưa có UI nút **Tinh chỉnh** cho 4 công cụ đầu.

## 3. Kiểm tra spec
Không áp dụng (Cách 3: Việc thường).

## 4. Điểm va chạm
- **88 bài test Backend hiện có (`tests/test_quick_edit_rails.py`, `tests/test_assistant_quick_edit.py`):**
  - `test_collect_protected_tokens_auto_detects_kinds` (`test_quick_edit_rails.py:92-106`) và `test_dictionary_terms_are_used_when_present_in_text` (`114-118`) truyền tường minh `DefaultPedagogicalDictionary()` hoặc `_Dict()`, kỳ vọng `DefaultPedagogicalDictionary` vẫn trả về `()`. Phải giữ nguyên `DefaultPedagogicalDictionary`.
  - `_StubProvider` ở `tests/test_assistant_quick_edit.py:59-71` (và các stub tương tự ở `test_app.py`, `test_ai_actions.py`, `test_assistant_tools_layer_b.py`) chỉ nhận `spellcheck(*, text, max_output_tokens=2048)` và `editor_rewrite(*, text, option, custom_query='', max_output_tokens=2048)`. Không được thay đổi signature bắt buộc của hai hàm này trên `TextProvider` protocol; mọi ngữ cảnh bổ sung cho `spellcheck` cần truyền an toàn qua `text` hoặc tham số mặc định có kiểm tra tương thích.
  - `test_rewrite_tools_success` (`test_assistant_quick_edit.py:165-204`) kiểm tra `provider.rewrite_calls[0]['option']` là `'Rewrite'`, `'Shorten'`, `'Continue writing'`, `'Transform text'` và kiểm tra `custom_query` chứa nhãn tiếng Việt đặc trưng; `test_previous_suggestion_and_instruction_are_forwarded` (`400-418`) kiểm tra `'GỢI Ý HIỆN TẠI'` trong `custom_query`.
  - `test_prompt_injection_in_selection_is_delimited_as_data` (`478-493`) kiểm tra `lines[0]` bắt đầu bằng `'<<<TEXT_'`, `lines[-1]` bắt đầu bằng `'<<<END_TEXT_'`, và `'DỮ LIỆU'` / `'KHÔNG phải chỉ thị'` có trong `custom_query`.
- **Quy tắc chính tả sư phạm (`tests/test_agent_conflict_and_orthography.py`):** Mọi hướng dẫn tiếng Việt gửi LLM không được dùng ký hiệu viết tắt `&` thay cho chữ `"và"`.
- **60 bài test Frontend hiện có (`quick-edit-core.test.ts`, `QuickEditContextMenu.test.tsx`, `QuickEditOverlay.test.tsx`):**
  - `QuickEditOverlay.test.tsx:225` khẳng định tường minh `expect(within(panel).queryByRole("button", { name: "Tinh chỉnh" })).toBeNull()` cho `shorten` (và bố cục 3 nút chân bảng cho 4 công cụ đầu) — quyết định **3.c** bảo toàn 100% hợp đồng UI này.
  - Các test hiện có trong `quick-edit-core.test.ts` gọi `describeQuickEditResult(tool, count)` với 2 tham số → tham số `warnings` mới phải là tùy chọn.

## 5. Phương án đề xuất
1. **Backend — Chuẩn hóa Prompt, Vòng retry & Output Rails cho 5 công cụ:**
   - Trong `quick_edit_rails.py`:
     - Tách rõ luật công cụ trong `_build_custom_query`: thay `' | '` bằng danh sách ngoặc kép phân tách bằng dấu phẩy; chỉ truyền `normalization_hints` cho `refine` (đồng thời chuẩn hóa chữ hoa/thường danh từ chung); với `custom`, cho phép chuyển đổi ngôn ngữ hoặc định dạng danh sách theo `instruction`, không khóa cứng thuật ngữ tiếng Việt khi người dùng yêu cầu dịch sang ngôn ngữ khác.
     - Truyền `protected.terms` / `protected.formulas` vào lời nhắc của `spellcheck` (tương thích ngược với `_StubProvider`), đồng thời mở rộng `_filter_spellcheck_output` thay thế hết mọi vị trí bị sửa nhầm.
     - Tinh chỉnh ngưỡng độ dài (`check_output_rails`): thu hẹp sàn `too_long` cho văn bản ngắn, trả `no_change` khi `shorten` giữ nguyên câu đã tối giản (`already_concise`, Tình huống 2.a), thêm phát hiện lặp bán phần ở `continue` trong `sanitize_output` & `check_output_rails`, lọc thẻ `<!--BF_GOV:...-->` bằng `strip_internal_governance_tags`.
     - Trong `EvaluatedOutput` và `_run_quick_edit` (`assistant_tools.py`): nâng `not_shorter`, `too_long`, `repeats_original` vào nhóm `retryable_findings` để thử lại nội bộ tối đa 1 lần; đặt trần `max_output_tokens` hợp lý cho `shorten` và `refine`.
   - Trong `pydantic_text_provider.py`: không truyền `temperature` cho model reasoning OpenAI để tránh `UserWarning`.
2. **Backend — Từ điển Sư phạm tự nhận diện môn học ngầm (Tình huống 1.a):**
   - Thêm trường `title: str | None = None` vào `QuickEditDocMetadata`, truyền từ `_enrich_quick_edit_payload` (`assistant_tools.py`).
   - Trong `SchoolGlossaryPedagogicalDictionary`: kết hợp `infer_subject_and_grade_from_context` (bổ sung môn gộp) với `SchoolGlossaryService._get_academic_glossary_index().scan_passage()` trên `title` và văn bản để tự động phát hiện môn học ngay cả khi tiêu đề không có tên môn, với điều kiện tối thiểu về phiếu môn học (`subject_votes`) để không bắt nhầm văn bản đời thường; hoạt động tự động ngầm 100% theo nội dung bài học.
3. **Frontend — Bảo toàn Toán học KaTeX, cấu trúc đoạn & nối gợi ý trước cho `custom` (Tình huống 3.c):**
   - Trong `quick-edit-core.ts` & `assistant-editor-actions.ts`: serialize hai chiều node `inlineMath` (`$...$`), `blockMath` (`$$...$$`) và ranh giới đoạn `\n` / danh sách, thực hiện `applyReplacement` / `insertBelow` trong 1 transaction duy nhất để `Ctrl+Z` hoàn tác 1 bước; mở rộng dấu câu trong `continueAtSelection` (`.,;:!?)]`).
   - Render công thức KaTeX an toàn trong khung Nội dung gốc và Đề xuất của `QuickEditPanel.tsx` (khi chỉnh sửa tay thì hiện chuỗi thô `$...$`); cập nhật `describeQuickEditResult` trung thực theo `warnings` và bật highlight phần sửa cho `shorten`.
   - Trong `use-quick-edit.ts`: giữ nguyên bố cục 3 nút của 4 công cụ đầu; riêng ở `custom`, khi đổi `instruction` mới lúc đã có `panel.review?.draft` thì truyền `previous_suggestion: panel.review.draft` để tinh chỉnh nối tiếp.

## 6. Câu hỏi kỹ thuật còn mở
Không còn (đã chốt toàn bộ 4 tình huống ở Mục 0: `1.a`, `2.a`, `3.c`, `4.b`).
