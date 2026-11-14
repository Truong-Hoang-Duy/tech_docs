# Tìm hiểu: Hoàn thiện Từ điển sư phạm công tắc Bật/Tắt theo Review Round 1 & Đồng bộ nhánh chính

**Ngày:** 2026-11-14 · **Cách làm:** Cách 3: Việc thường · **Phía:** Cả hai
**Mốc code:** backend nhánh `f26feec6` (`origin/dev` mới nhất `af4b3933`) · frontend nhánh `18fd8a5e` (`origin/dev` mới nhất `91ffb5d1`)
**Spec (nếu có):** Không có (Tài liệu đối chiếu yêu cầu: `tech_docs/research/2026-11-14-glossary-toggle-only-review.md`)

## 0. Việc này sẽ làm gì
**Để làm gì:** Khắc phục triệt để các điểm hạn chế được chỉ ra trong bản đánh giá đợt 1 của tính năng **công tắc Bật/Tắt Từ điển sư phạm**, đồng thời cập nhật đồng bộ với toàn bộ các tính năng mới nhất vừa được đưa lên hệ thống chung để sẵn sàng gộp chính thức.

**Làm xong, ai sẽ thấy gì khác:**
| Vai trò | Trước đây (bản đợt 1) | Sau khi hoàn thiện (đợt 2) |
|---|---|---|
| Giáo viên dùng Trợ lý chuyên biệt (Ma trận đề, Phiếu điền khuyết, Infographic, Đề kiểm tra) | Khi nhập môn học gộp (*Khoa học tự nhiên*, *Lịch sử và Địa lí*, *Giáo dục công dân*), bỏ trống tên môn, hoặc tiêu đề có chứa cụm từ sư phạm chung (*Kiểm tra định kì*, *Yêu cầu cần đạt*, *Đánh giá năng lực*), trợ lý chỉ lấy thuật ngữ sư phạm chung mà làm rơi toàn bộ thuật ngữ chuyên môn của bài học. | Nhận diện đầy đủ các môn thành phần trong môn gộp và luôn lấy trọn vẹn cả thuật ngữ sư phạm chung lẫn thuật ngữ chuyên môn của môn học. |
| Giáo viên hỏi đáp trên khung Trò chuyện & Trợ lý Dịch học thuật | Câu hỏi vừa có cụm sư phạm (*yêu cầu cần đạt*, *kế hoạch bài dạy*) vừa có thuật ngữ chuyên môn ngắn bị mất từ điển môn học; hỏi tiếp sang câu thứ hai (*"Tạo 3 câu hỏi vận dụng về phần này"*) bị quên môn học của câu đầu; khoảng 55 cặp thuật ngữ tiếng Anh có dấu gạch chéo bị sót khi dịch học thuật. | Hỏi kết hợp sư phạm với kiến thức môn học hay hỏi nối tiếp nhiều lượt đều giữ đúng từ điển môn học; khôi phục đầy đủ toàn bộ các cặp thuật ngữ song ngữ cho trợ lý Dịch học thuật. |
| Giáo viên dùng Sơ đồ tư duy & Trình soạn thảo | Khi bấm chỉnh sửa nhánh trên Sơ đồ tư duy Lịch sử, Sinh học hoặc sơ đồ công việc đời thường, hệ thống đọc nhầm ký hiệu đánh số thẻ nội bộ thành công thức Toán học; tạo sơ đồ nhanh từ khung trò chuyện hoặc chỉ bật Từ điển ở cài đặt mặc định toàn trường thì chưa được tự động áp dụng. | Sơ đồ tư duy chỉ đọc đúng nội dung chữ của người dùng để nhận diện đúng môn (và không chèn nhầm từ điển vào sơ đồ đời thường), đồng thời áp dụng đầy đủ trạng thái Từ điển của phiên làm việc cũng như mặc định toàn trường. |

**Lần này không làm:** Không thay đổi nội dung kho dữ liệu từ điển gốc trong cơ sở dữ liệu; không quay lại giao diện chọn thủ công từng môn học đã lược bỏ ở đợt 1.

**Người dùng và dữ liệu đang có bị ảnh hưởng:** Không. Mọi cuộc trò chuyện cũ, cài đặt đã lưu và toàn bộ các tính năng mới vừa bổ sung trên hệ thống chung (tạo nhanh thư mục câu hỏi, chuyển đề sang ngân hàng câu hỏi, đổi tên mục *Đường ray sư phạm* thành *Quy tắc tạo sinh*) đều được bảo toàn nguyên vẹn.

**Bạn cần quyết:**
1. **Tình huống 1 — Chữ hiển thị trên nút trạng thái Từ điển bên dưới ô nhập tin nhắn:**
   Giao diện đợt 1 đang hiển thị gọn là **Từ điển: Bật** / **Từ điển: Tắt**, trong khi phần gợi ý viết tài liệu ở bản đánh giá có nhắc ví dụ chữ *Từ điển sư phạm: Đang bật*.
   - (a) Giữ nguyên chữ ngắn gọn **Từ điển: Bật** / **Từ điển: Tắt** trên màn hình và cập nhật tài liệu bàn giao khớp đúng chữ này → Ngắn gọn, cân xứng với nút **Quy tắc tạo sinh** kế bên và giữ nguyên trải nghiệm bạn đã kiểm thử đạt ở đợt 1.
   - (b) Đổi chữ trên nút thành **Từ điển sư phạm: Đang bật** khi bật và **Từ điển: Tắt** khi tắt → Diễn giải đầy đủ hơn nhưng chiếm thêm chiều ngang thanh công cụ.
   - **AI khuyên:** a, vì ngắn gọn, đồng bộ với nút **Quy tắc tạo sinh** và không làm xáo trộn giao diện đã ổn định · **Bạn chốt:** Chọn a
2. **Tình huống 2 — Cách giữ mạch môn học khi người dùng hỏi nối tiếp nhiều lượt trong một cuộc trò chuyện:**
   - (a) Khi câu hỏi mới không nhắc rõ môn học hay thuật ngữ chuyên môn (ví dụ: *"Tạo cho tôi 3 câu hỏi vận dụng về phần này"*), hệ thống mượn ngữ cảnh từ 1–2 câu hỏi liền trước và tên tài liệu đang mở; ngược lại nếu câu hỏi mới đã nêu rõ kiến thức của một môn khác thì ưu tiên ngay môn của câu hỏi mới, không kéo theo thuật ngữ môn cũ → Giữ đúng mạch khi hỏi tiếp mà không bị lẫn môn khi đổi chủ đề.
   - (b) Luôn gộp chung câu hỏi hiện tại với các câu hỏi trước đó để tra cứu cùng lúc → Dễ bị trộn lẫn thuật ngữ môn cũ khi người dùng hỏi sang môn khác trong cùng cuộc trò chuyện.
   - **AI khuyên:** a, vì xử lý tự nhiên và chính xác cả lúc hỏi nối tiếp lẫn lúc đổi chủ đề · **Bạn chốt:** Chọn a
3. **Tình huống 3 — Quy tắc viết chữ "và" thay cho dấu "&" mới áp dụng trên hệ thống chung:**
   Hệ thống chung vừa có quy tắc chuẩn chính tả sư phạm: không dùng dấu `&` thay cho chữ *"và"* trong văn bản hướng dẫn gửi cho trí tuệ nhân tạo.
   - (a) Đổi dấu `&` sang chữ **`VÀ`** trong tiêu đề bảng từ điển gửi cho trí tuệ nhân tạo theo đúng yêu cầu bắt buộc của bản đánh giá, còn tiêu đề các cửa sổ cài đặt trên màn hình thì giữ nguyên như hệ thống chung đang hiển thị → Vượt qua toàn bộ bài kiểm tra chính tả mới mà không gây lệch giao diện chung.
   - (b) Đổi toàn bộ dấu `&` thành chữ `"và"` trên cả tiêu đề các cửa sổ cài đặt giao diện.
   - **AI khuyên:** a, vì đáp ứng đúng 100% tiêu chí nghiệm thu của bản đánh giá và khớp hoàn toàn với nhánh chính hiện tại · **Bạn chốt:** Chọn a

**Làm xong, bạn sẽ thấy nó chạy thế nào:** Khi tạo Ma trận đề, Phiếu điền khuyết, Infographic với môn *Khoa học tự nhiên* hoặc bỏ trống môn, hệ thống vẫn lấy đúng thuật ngữ chuyên môn; hỏi câu kết hợp như *"Nêu yêu cầu cần đạt khi dạy về enthalpy"* hay hỏi nối tiếp sang lượt thứ hai vẫn nhận diện đúng môn Hóa học/Sinh học; dịch đoạn văn tiếng Anh có từ đồng nghĩa gạch chéo vẫn tra ra đủ thuật ngữ; chỉnh sửa nhánh trên Sơ đồ tư duy Lịch sử/Sinh học nhận đúng thuật ngữ môn đó thay vì bị nhầm sang Toán học.

**So với nghiệp vụ đã có:** Giữ: Công tắc Bật/Tắt Từ điển sư phạm duy nhất trên 3 màn hình và tương thích ngược dữ liệu phiên cũ · Đổi: Khắc phục 4 lỗi nhận diện/truyền ngữ cảnh ở Trợ lý chuyên biệt, câu hỏi kết hợp sư phạm, từ đồng nghĩa gạch chéo và Sơ đồ tư duy; đồng bộ bản đang làm với hệ thống chung mới nhất · Thêm: Giữ mạch môn học cho câu hỏi nối tiếp nhiều lượt, tự nhận mặc định toàn trường cho Trình soạn thảo/Sơ đồ tư duy, và cập nhật tài liệu bàn giao giao diện.

---
*(Từ mục 1 trở xuống là phần kỹ thuật cho agent.)*

## 1. Mục tiêu và phạm vi
- **Cần đạt (đóng toàn bộ mục Definition of Done trong `tech_docs/research/2026-11-14-glossary-toggle-only-review.md`):**
  1. **Rebase sạch cả 2 repo lên `origin/dev` mới nhất (`🔴 5`):** Backend từ `a5d3fce1` lên `af4b3933` (`43` commit) và Frontend từ `6a32c01d` lên `91ffb5d1` (`41` commit, 8 file xung đột), bảo toàn 100% tính năng mới của `origin/dev` và tuân thủ quy tắc chính tả sư phạm (`VÀ` thay cho `&` trong `format_glossary_prompt_block`).
  2. **Khắc phục 4 lỗi chặn về logic & luồng dữ liệu (`🔴 1` → `🔴 4`) kèm kiểm thử hai chiều ($P \land \neg P$):**
     - `🔴 1`: Hỗ trợ môn tổ hợp/bí danh (`Khoa học tự nhiên`, `KHTN`, `Lịch sử và Địa lí`, `GDCD`) trong `lookup_lesson_glossary` và luôn gọi bổ sung `resolve_auto_glossary_terms` ở các Agent chuyên biệt khi kết quả chưa có thuật ngữ chuyên môn (`subject_key != 'chung'`).
     - `🔴 2`: Không để thuật ngữ `chung` làm tắt bước quét sub-token (`enthalpy`, `nhị phân`) trong `scan_passage` hoặc khóa cứng `allowed_subjects = {'chung'}` trong `resolve_auto_glossary_terms`.
     - `🔴 3`: Chỉ giữ nguyên dấu `/` viết liền không khoảng trắng (`phổi/phút`, `S/V`, `G1/S`, `m/s`) trong `extract_headword_variants`, khôi phục tách đồng nghĩa song ngữ có khoảng trắng ` / ` (`Climograph`, `Folktale`...) và làm sạch dấu `*` / ngoặc con cho `search_academic_glossary`.
     - `🔴 4`: Loại bỏ khung kỹ thuật `selection_block` (`[n-1]`, `"Sơ đồ"`, `"liên kết"`, `"type="`) khỏi đầu vào từ điển của `flow_agent.py`; dùng `resolve_effective_context_settings(db, org_id, context_settings)` cho cả `flow_agent.py` và `editor_agent.py`; truyền `context_settings` từ `FlowArtifactPage` (`ai-action`) và lệnh `/mindmap` ở Frontend.
  3. **Hoàn thiện 2 mục `🟡 Should-fix` (`🟡 1`, `🟡 2`) & kiểm chứng `🟢 Nits`:**
     - `🟡 1`: Bổ sung ngữ cảnh 1–2 lượt hỏi gần nhất của người dùng trong `history` và tiêu đề tài liệu phiên vào `lookup_text` của `_run_free_chat` và `_build_chat_agent`.
     - `🟡 2`: Cập nhật tài liệu `backend/docs/frontend/chat-glossary-context.md` khớp hoàn toàn với kiến trúc công tắc Bật/Tắt và tên gọi mới trên `origin/dev`.
- **Không làm:**
  - Không sửa đổi dữ liệu seed JSON trong `bookforge_api/data/glossary/` hay schema cơ sở dữ liệu Alembic (giữ nguyên 1 head `0137_internal_support_admin`).
  - Không tự ý merge vào `dev` khi bạn chưa cho phép.

## 2. Hiện trạng (kèm `file:dòng`)
- **Luồng hiện tại trên nhánh `feat/glossary-toggle-only` (`f26feec6` / `18fd8a5e`) & nguyên nhân từng điểm review:**
  1. **`🔴 1` — Rơi thuật ngữ chuyên môn ở Agent chuyên biệt:**
     - `backend/services/api/src/bookforge_api/services/school_glossary.py:1600-1625` (`lookup_lesson_glossary`): Dòng `1601` gọi `parse_subject_and_grade(combined)` chỉ trả về 1 môn đơn lẻ (trả `(None, None)` với `'Khoa học tự nhiên'`, `'KHTN'`, `'GDCD'`, `''` và chỉ trả `'dia_ly'` với `'Lịch sử và Địa lí'`). Khi `glossary_ids is None` và `inferred_subject is None`, `active_domains = ['chung']`, `target_subjects = []` (`dòng 1609-1618`), sau đó bước 3 (`dòng 1662-1669`) khớp các từ phổ biến trong tiêu đề (*Kiểm tra định kì*, *Yêu cầu cần đạt*, *Đánh giá năng lực*) vào miền `chung`.
     - `backend/services/api/src/bookforge_api/chat/ma_tran_de_agent.py:563-579`, `chat/infographic_agent.py:1200-1217`, `chat/phieu_dien_khuyet_agent.py:425-442`: Cả 3 hàm đều đặt điều kiện `if not terms:` trước khi gọi `resolve_auto_glossary_terms`, nên chỉ cần dính 1 mục từ `chung` là bỏ qua toàn bộ thuật ngữ môn học trong `scope_description`. Tại `chat/de_kiem_tra_agent.py:123-129`, `lookup_lesson_glossary` cũng chịu cùng hạn chế môn tổ hợp.
  2. **`🔴 2` — Mục từ `chung` chặn quét sub-token chuyên môn và khóa cứng `allowed_subjects = {'chung'}`:**
     - `backend/services/api/src/bookforge_api/services/school_glossary.py:1443-1458` (`_AcademicGlossaryIndex.scan_passage`): `has_strong_hit = any(sc >= 8.0 for sc in scores.values())` trả `True` ngay khi khớp 1 mục `chung` (`sc >= 8.0`), dù `subject_votes` vẫn rỗng `{}` — làm bỏ qua `scientific_subtoken_map` (`enthalpy`) và `vi_compound_subgram_map` (`nhị phân`).
     - `backend/services/api/src/bookforge_api/services/school_glossary.py:2158-2160` (`resolve_auto_glossary_terms`): Nhánh `elif any(sc >= 8.0 for sc in p_scores.values()): allowed_subjects = {'chung'}` khóa cứng miền tra cứu vào `{'chung'}`, chặn cả bước `query_fts` (`dòng 2264-2279`) lấy thuật ngữ môn Hóa/Tin.
  3. **`🔴 3` — Hồi quy `extract_headword_variants` làm gãy 55+ cặp đồng nghĩa song ngữ `Phrase / SingleWord`:**
     - `backend/services/api/src/bookforge_api/services/school_glossary.py:705-709`: `rest_slash = src[idx_ch + 1 :].strip()` xóa khoảng trắng sau dấu `/`, khiến các mục từ song ngữ cách khoảng trắng như `'Temperature and precipitation chart / Climograph'`, `'Fairy tale / Folktale'` thỏa điều kiện `' ' in piece and ' ' not in rest_slash` và không được tách thành biến thể độc lập cho `search_academic_glossary`.
     - `backend/services/api/src/bookforge_api/services/school_glossary.py:783-787`: Trong `paren_groups`, lệnh `grp.replace(';', '/').split('/')` cắt ngang ngoặc lồng nhau và dấu `*` trong `'Đồng phân hình học (geometric isomers (*cis-* / *trans-* isomers))'`.
  4. **`🔴 4` — Khung `[n-1]` của Flow làm lệch sang Tổ hợp Toán & thiếu nối `context_settings` + mặc định đơn vị:**
     - `backend/services/api/src/bookforge_api/chat/flow_agent.py:749-773, 1020-1026, 1184-1190`: `run_flow_action` truyền `selection_block` (sinh bởi `_flow_selection_hint`, chứa `- [n-1] ... id="n-1" (type="...")`, `"Sơ đồ"`, `"liên kết"`) vào `_resolve_flow_glossary_block`; chuỗi `n-1` khớp 5 mục từ Tổ hợp/Cấp số cộng môn Toán (`+40` phiếu `toan`). Ngoài ra `flow_agent.py:754` (`if context_settings is None: return ''`) và `chat/editor_agent.py:490` (`if context_settings is not None:`) bỏ qua `resolve_effective_context_settings(db, org_id, context_settings)` (`services/regulations.py:717-738`).
     - `frontend/src/templates/FlowArtifactPage/index.tsx:2369-2382` (`APIRunFlowAiActionWithEngine`) và `frontend/src/templates/HomePage/partials/use-chat-with-ai.ts:981-987` → `chat-mindmap-slash.ts:518-528` (`executeChatMindmapSlashCommand`): Chưa truyền `context_settings` (dù `TFlowAiActionRequest` và `TGenerateFlowRequest` tại `src/api/flow-artifacts-api.ts:57, 71` đã khai báo trường này).
  5. **`🔴 5` — Xung đột và lệch quy tắc so với `origin/dev` mới nhất:**
     - Backend (`origin/dev` `af4b3933`): `llm/pydantic_text_provider.py:187-205` trên `origin/dev` bổ sung `FREE_CHAT_CONFLICT_INSTRUCTION` vào `answer_without_context` và chuyển `editor_rewrite` / `spellcheck` / `risk_scan` / `editor_summary` sang `_run_structured_editor_op`; `services/school_glossary.py:1614` trên `origin/dev` đổi header mặc định sang `'TỪ ĐIỂN THUẬT NGỮ SGK VÀ SƯ PHẠM CHUẨN...'` (kiểm soát bởi `tests/test_agent_conflict_and_orthography.py:75-95`).
     - Frontend (`origin/dev` `91ffb5d1`): Xung đột trên 8 file do `origin/dev` cập nhật `withWorkspacePrefix("/school-rules")`, đổi nhãn *Đường ray sư phạm* → *Quy tắc tạo sinh* (`AgentContextSettingsDialog.tsx:180-191, 373-381, 520-525`, `ModalSettings/index.tsx:1659-1679`, `agent-settings-model.ts:757-777`), thêm `QuestionGenerateHandoffCard` (`HomePage/index.tsx`), thêm `initialPrefill` + `writableFolders` + tạo nhanh thư mục (`MassQuestionGenerateDrawer.tsx`), và hằng số mức module `EMPTY_MODES` / `EMPTY_EXPERTS` / `EMPTY_AGENTS` (`use-chat-modes.ts`).
  6. **`🟡 1` & `🟡 2` — Ngữ cảnh hội thoại nhiều lượt & Tài liệu hợp đồng FE:**
     - `backend/services/api/src/bookforge_api/api/chat.py:1553-1561` và `chat/adk_agent.py:1031-1042`: Mới chỉ truyền `query` (và `attached_text[:1500]`) mà chưa xét 1–2 tin nhắn user trước đó trong `history` hay tiêu đề tài liệu phiên khi câu hỏi tiếp nối không lặp lại tên khái niệm/môn học.
     - `backend/docs/frontend/chat-glossary-context.md:11-60`: Vẫn mô tả giao diện cũ gồm 12 checkbox từ điển, menu `Khác...`, `glossary_enabled: true` mặc định và quy tắc đồng bộ checkbox `khtn`.

## 3. Kiểm tra spec (chỉ việc có spec, xem `spec-check.md`; việc khác ghi "Không áp dụng")
Không áp dụng.

## 4. Điểm va chạm
- **Bảo toàn tuyệt đối code mới trên `origin/dev` khi rebase:**
  - Trên Backend, `pydantic_text_provider.py` phải giữ nguyên cả `FREE_CHAT_CONFLICT_INSTRUCTION` lẫn `glossary_section`, và mọi chuỗi hướng dẫn tiếng Việt trong `school_glossary.py` không được chứa ký tự `&` thay cho từ nối `"và"` để vượt qua `tests/test_agent_conflict_and_orthography.py`.
  - Trên Frontend, `MassQuestionGenerateDrawer.tsx` có `+394` dòng tính năng mới trên `origin/dev` (`initialPrefill`, RBAC `writableFolders`, inline quick-folder creation) — khi rebase phải giữ đầy đủ 100% 3 tính năng này, chỉ thay riêng phần UI `C. Từ điển sư phạm` sang công tắc `Switch` đơn. Đồng thời giữ nguyên việc đổi tên *Đường ray sư phạm* → *Quy tắc tạo sinh* trên `origin/dev`.
- **Chống nhiễu môn cũ ở hội thoại nhiều lượt (`🟡 1`):**
  - Nếu ghép lịch sử hội thoại không khéo vào cùng chuỗi `query`, câu hỏi mới khi đổi sang môn khác sẽ bị cộng phiếu của môn ở lượt trước. Do đó cần ưu tiên nhận diện trên `query` của lượt hiện tại trước; chỉ khi lượt hiện tại chưa xác định được môn học chuyên biệt mới fallback sang 1–2 lượt hỏi gần nhất của người dùng và tiêu đề tài liệu trong phiên.
- **Kiểm thử hai chiều ($P \land \neg P$):**
  - Mọi điểm sửa từ `🔴 1` đến `🔴 4` và `🟡 1` đều phải có cặp assertion hai chiều: kịch bản lỗi cũ được sửa ($P$) và kịch bản biên đối ứng không sinh dương tính giả ($\neg P$).

## 5. Phương án đề xuất
1. **Làm trực tiếp trên nhánh `feat/glossary-toggle-only` & Rebase lên `origin/dev` mới nhất (`🔴 5`):**
   - **Không tạo nhánh mới:** Checkout và làm tiếp trực tiếp trên nhánh `feat/glossary-toggle-only` ở cả `backend` (`f26feec6`) và `frontend` (`18fd8a5e`).
   - Thực hiện `git rebase origin/dev` lần lượt trên `backend` (lên `af4b3933`) và `frontend` (lên `91ffb5d1`), sau đó kiểm tra từng file bằng `git diff origin/dev...HEAD` để chắc chắn không làm rơi bất kỳ thay đổi nào của `origin/dev`.
2. **Xử lý triệt để `🔴 1`, `🔴 2`, `🔴 3` trong `school_glossary.py` & các Agent chuyên biệt:**
   - `lookup_lesson_glossary`: Kết hợp `expand_glossary_domains(resolve_question_subject_glossary_ids(subject_and_grade), glossary_enabled=True)` với `parse_subject_and_grade(combined)` để mở rộng đúng các môn tổ hợp (`Khoa học tự nhiên` → `vat_ly`, `hoa_hoc`, `sinh_hoc`; `Lịch sử và Địa lí` → `lich_su`, `dia_ly`; `GDCD` → `gdktpl`). Ở `ma_tran_de_agent.py`, `infographic_agent.py`, `phieu_dien_khuyet_agent.py`, gọi bổ sung `resolve_auto_glossary_terms` bất cứ khi nào `not any(t.get('subject_key') != 'chung' for t in terms)` và gộp khử trùng lặp với các mục `chung`.
   - `scan_passage` & `resolve_auto_glossary_terms`: Đổi `has_strong_hit` thành `has_strong_subject_hit` (chỉ tính mục có `subject_key != 'chung'`) và gỡ nhánh khóa cứng `allowed_subjects = {'chung'}` khi `p_votes` rỗng.
   - `extract_headword_variants`: Chỉ giữ nguyên `/` khi không có khoảng trắng ở cả hai phía (`idx_ch > 0 and not src[idx_ch - 1].isspace() and idx_ch + 1 < n_src and not src[idx_ch + 1].isspace()`); với các nhóm ngoặc lồng nhau như `geometric isomers (*cis-* / *trans-* isomers)`, trích xuất sạch phần ngoài ngoặc con và các biến thể hợp lệ, loại bỏ dấu `*` bọc ngoài.
3. **Xử lý `🔴 4` cho Flow/Mindmap & Canvas Editor (Backend + Frontend):**
   - Backend `flow_agent.py`: Sửa `_resolve_flow_glossary_block(db, user, context_settings, *text_parts)` gọi `resolve_effective_context_settings(db, _resolve_user_org_id(user), context_settings)`; tại `run_flow_action` và `run_flow_chat_edit`, bỏ hẳn `selection_block` khỏi đầu vào từ điển, chỉ truyền văn bản người dùng sạch (`payload.title`, `payload.instruction`, `payload.selected_text`, cùng `node.title` và mô tả sạch của node mục tiêu / các node liên quan). Tương tự tại `editor_agent.py`, dùng `resolve_effective_context_settings` thay cho `if context_settings is not None:`.
   - Frontend: Truyền `context_settings: toChatContextSettings(loadAgentSettings("mindmap"))` vào `APIRunFlowAiActionWithEngine` tại `FlowArtifactPage/index.tsx` và truyền `context_settings: outgoingContextSettings` qua `executeChatMindmapSlashCommand` tại `use-chat-with-ai.ts` → `chat-mindmap-slash.ts`.
4. **Xử lý `🟡 1` & `🟡 2`:**
   - Trong `api/chat.py` (`_run_free_chat`) và `chat/adk_agent.py` (`_build_chat_agent`), nếu câu hỏi hiện tại chưa tự khớp được môn học chuyên biệt (chỉ ra rỗng hoặc chỉ ra `chung`), dùng thêm tối đa 2 tin nhắn `user` gần nhất trong `history` (giới hạn độ dài) và tiêu đề các tài liệu của phiên để suy luận bổ sung từ điển môn học (theo quyết định ở Tình huống 2).
   - Cập nhật `backend/docs/frontend/chat-glossary-context.md` phản ánh chính xác hợp đồng API/UI hiện hành (theo quyết định ở Tình huống 1).

## 6. Câu hỏi kỹ thuật còn mở
Đã đưa toàn bộ 3 điểm cần chốt lên mục 0 dưới dạng tình huống người dùng.
