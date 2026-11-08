# Tìm hiểu: Hoàn thiện Backend AI Quick Edit (Từ điển Sư phạm, Đường ray Tạo sinh & Hậu kiểm Thuật ngữ)

**Ngày:** 2026-11-08 · **Cách làm:** Cách 3: Việc thường · **Phía:** BE
**Mốc code:** backend `48a28e31` · frontend `fbd52874`
**Spec (nếu có):** Không có (Tài liệu tham khảo: `tech_docs/research/writing-block.md`, `tech_docs/research/bao-cao-ai-quick-edit.md`)

## 0. Việc này sẽ làm gì
**Để làm gì:** Hoàn thiện toàn bộ tầng xử lý phía sau (Backend) cho bộ công cụ chỉnh sửa nhanh bằng AI (**AI Quick Edit**) khi người dùng bôi đen văn bản trên trình soạn thảo (Canvas) và Sơ đồ tư duy (Mindmap): kết nối thật với **Bộ Từ điển Sư phạm & SGK (10 môn cấp THPT + bộ từ điển Chung)**, bổ sung gợi ý chuẩn hóa từ đồng nghĩa, tự động lấy thông tin môn/lớp từ hồ sơ tài liệu trong cơ sở dữ liệu, đưa công cụ **Sửa chính tả** vào chung hàng rào bảo vệ thuật ngữ, và tách cảnh báo riêng khi thuật ngữ chuyên môn bị thay đổi — kết hợp trực tiếp với giao diện Figma mới nhất đã có sẵn trên nhánh phát triển.

**Làm xong, ai sẽ thấy gì khác:**
| Vai trò | Trước đây | Sau khi làm |
|---|---|---|
| Giáo viên / Người dùng trên Canvas & Mindmap | Giao diện menu chuột phải 5 công cụ AI và bảng xem trước (Review Panel) đã có sẵn dòng *"Đã giữ nguyên: ..."* và khung cảnh báo vàng/đỏ, nhưng ở phía sau đang nối vào cổng Từ điển rỗng nên: (1) chưa nhận diện và khóa bảo vệ thuật ngữ SGK theo môn/lớp; (2) chưa gợi ý chuẩn hóa từ đồng nghĩa về thuật ngữ chuẩn; (3) *Sửa chính tả* chưa nhận danh sách thuật ngữ chuyên môn cần bảo vệ; (4) cảnh báo mất thuật ngữ chuyên môn đang bị gộp chung với tên riêng thông thường. | (1) Khi dùng bất kỳ công cụ nào trong 5 công cụ AI, hệ thống tự động tra cứu kho Từ điển SGK & Sư phạm (tự suy luận môn/lớp từ tài liệu đang mở + nội dung đoạn văn) và đổ danh sách thuật ngữ SGK được bảo vệ vào ngay dòng *"Đã giữ nguyên: ..."* trên bảng xem trước; (2) tự động gợi ý chuẩn hóa từ đồng nghĩa/viết tắt về thuật ngữ chuẩn SGK; (3) *Sửa chính tả* bảo toàn thuật ngữ/kí hiệu chuyên môn và hỗ trợ tinh chỉnh theo yêu cầu; (4) hiện cảnh báo riêng *"Thuật ngữ chuyên môn có thể đã bị thay đổi: ..."* trên khung cảnh báo có sẵn nếu AI làm rơi thuật ngữ. |

**Lần này không làm:**
- Không sửa giao diện người dùng (phần giao diện được kéo về bản mới nhất trên nhánh phát triển và giữ nguyên hoàn toàn).
- Không thay đổi cấu trúc bảng cơ sở dữ liệu Từ điển SGK (tận dụng các bảng và dữ liệu từ điển đã có sẵn).
- Không đụng tới luồng Trợ lý Chat AI bên phải màn hình.

**Người dùng và dữ liệu đang có bị ảnh hưởng:** Không. Các tài liệu đang có và giao diện chuột phải hiện tại giữ nguyên; những tài liệu chưa gắn nhãn môn học vẫn tự động dùng bộ từ điển *Chung (sư phạm, giáo dục)* kết hợp suy luận môn/lớp từ tiêu đề tài liệu trong cơ sở dữ liệu và nội dung đoạn văn.

**Bạn cần quyết:**
1. **Phạm vi thực hiện giữa hệ thống phía sau và Giao diện:**
   - (a) **Chỉ tập trung làm ở phía xử lý máy chủ (Backend), còn giao diện kéo bản mới nhất về và giữ nguyên:** Tận dụng trọn vẹn giao diện bảng xem trước chuẩn thiết kế hiện có (nơi đã có sẵn chỗ hiển thị danh sách *"Đã giữ nguyên: ..."* và khung cảnh báo vàng/đỏ).
   - (b) Sửa cả giao diện để thêm nút mới.
   - **AI khuyên:** (a), vì giao diện mới nhất vừa được đồng bộ chuẩn thiết kế và đã dựng sẵn đầy đủ vùng hiển thị thuật ngữ được giữ nguyên lẫn cảnh báo · **Bạn chốt:** Chọn (a) — chỉ tập trung vào phía máy chủ, phần giao diện kéo bản mới nhất về và giữ nguyên.

**Làm xong, bạn sẽ thấy nó chạy thế nào:**
Mở một tài liệu trên Canvas, quét chọn một đoạn văn có chứa thuật ngữ chuyên môn (ví dụ *"quang hợp"*, *"lục lạp"*, *"năng lực đặc thù"*), bấm chuột phải chọn **Công cụ AI** -> **Sửa chính tả** hoặc **Chỉnh diễn đạt**. Bảng kết quả hiện ra giữ nguyên đúng thuật ngữ SGK kèm dòng chú thích *"Đã giữ nguyên: quang hợp, lục lạp..."* ngay trên giao diện có sẵn; nếu đoạn văn dùng từ đồng nghĩa chưa chuẩn, AI ưu tiên chuẩn hóa về thuật ngữ SGK; nếu AI vô tình làm mất thuật ngữ trong lúc rút gọn/viết lại, khung cảnh báo vàng hiện rõ *"Thuật ngữ chuyên môn có thể đã bị thay đổi: ..."*.

**So với nghiệp vụ đã có:**
- **Giữ:** Toàn bộ giao diện chuẩn thiết kế hiện có, cấu trúc dữ liệu trả về của cổng chỉnh sửa nhanh, cơ chế kiểm tra độ dài, số liệu, công thức, đường dẫn và hạn mức ví.
- **Đổi:** Thay cổng từ điển rỗng ở phía sau bằng kết nối thật tới kho Từ điển SGK & Sư phạm; đưa công cụ *Sửa chính tả* vào chung luồng bảo vệ thuật ngữ và hỗ trợ tinh chỉnh; tách riêng cảnh báo thuật ngữ chuyên môn khỏi tên riêng thông thường.
- **Thêm:** Tự động làm giàu thông tin môn/lớp từ hồ sơ tài liệu trong cơ sở dữ liệu (tiêu đề, thông tin đính kèm) và nội dung đoạn chọn; bổ sung cơ chế gợi ý chuẩn hóa từ đồng nghĩa về thuật ngữ chuẩn vào chỉ dẫn cho AI.

---
*(Từ mục 1 trở xuống là phần kỹ thuật cho agent.)*

## 1. Mục tiêu và phạm vi
- **Cần đạt (Chỉ `backend` tại mốc `48a28e31`, `frontend` kéo mới nhất `fbd52874`):**
  1. **Task 1 — Kết nối Bộ Từ điển Sư phạm & SGK (`SchoolGlossaryService`) vào `quick_edit_rails.py` và làm giàu ngữ cảnh tài liệu từ DB:**
     - Xây dựng `SchoolGlossaryPedagogicalDictionary` trong `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:165-194` kết nối với dữ liệu của `SchoolGlossaryService` (`backend/services/api/src/bookforge_api/services/school_glossary.py:188-301, 408-708`), đăng ký làm bộ từ điển mặc định cho `_pedagogical_dictionary` (vẫn giữ nguyên lớp `DefaultPedagogicalDictionary` làm stub rỗng cho các test đơn vị gọi trực tiếp).
     - Hỗ trợ đủ 3 cơ chế của Mục III trong `writing-block.md`:
       - **(A) Khóa thuật ngữ bắt buộc (`protected_terms`):** Nhận diện các thuật ngữ chuẩn xuất hiện trong đoạn văn (từ bộ từ điển `chung` + bộ từ điển môn học/khối lớp suy luận được, hoặc quét các thuật ngữ chuyên môn đặc trưng từ chỉ mục từ điển SGK trên RAM khi chưa rõ môn) để đưa vào `ProtectedTokens.terms` -> tự động trả về trong `preserved_terms` cho UI hiển thị.
       - **(B) Chuẩn hóa thuật ngữ đồng nghĩa (`normalization_hints`):** Nhận diện các từ đồng nghĩa (`aliases`) xuất hiện trong đoạn văn để sinh gợi ý chuẩn hóa `"<alias>" -> "<term>"` (kèm kí hiệu `notation` nếu có) đưa vào `_build_custom_query()` (`quick_edit_rails.py:372-442`).
       - **(C) Làm giàu ngữ cảnh môn học/khối lớp từ DB và văn bản:** Trong `api/assistant_tools.py:92-109, 645-709`, khi người dùng gửi `document_ids`, tự động đọc `title`, `document_type`, `metadata_json` của bản ghi `Document` để bổ sung `subject`, `grade`, `doc_type` vào `doc_metadata` (kết hợp `parse_subject_and_grade` trên `title`, `doc_metadata` và văn bản).
  2. **Task 2 — Đồng bộ Đường ray Tạo sinh cho công cụ `spellcheck` & Hậu kiểm thuật ngữ chuyên môn (`terms_changed`):**
     - Nâng cấp luồng `spellcheck` trong `quick_edit_rails.py:476-492, 745-780`, `api/assistant_tools.py:634-668`, `llm/editor_tools.py:314-320`:
       - Củng cố prompt `build_spellcheck_prompt` (`llm/editor_tools.py:314-320`) và bộ lọc hậu kiểm trong `evaluate_provider_output` (`quick_edit_rails.py:745-780`) để `spellcheck` không sửa nhầm các thuật ngữ chuyên môn/công thức nằm trong `protected.terms` và `protected.formulas`.
       - Khi `spellcheck` được gọi kèm yêu cầu tinh chỉnh (`instruction` hoặc `previous_suggestion`) hoặc khi retry do lỗi Output Rails (`retry_findings`), xây dựng `custom_query` có kiểm soát và định tuyến xử lý để không làm mất yêu cầu tinh chỉnh của người dùng.
     - Trong `_check_protected` (`quick_edit_rails.py:693-702`), tách các thuật ngữ chuyên môn bị mất (`protected.terms`) thành cảnh báo riêng có mã `terms_changed` (*"Thuật ngữ chuyên môn có thể đã bị thay đổi: ..."*) thay vì gộp chung vào `names_changed` của tên riêng (`protected.proper_nouns`).
- **Không làm:**
  - Không sửa bất kỳ file nào trong `frontend/`.
  - Không tạo migration DB mới (bảng `school_glossary_chapters` và `school_glossary_terms` đã có từ `0127_school_glossary.py`).

## 2. Hiện trạng (kèm `file:dòng`)
- `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:165-194`: `PedagogicalDictionary` đang gán `_pedagogical_dictionary = DefaultPedagogicalDictionary()`, trả về `()` rỗng nên `ProtectedTokens.terms` luôn rỗng nếu không monkeypatch.
- `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:325-361`: `collect_protected_tokens()` gọi `dictionary.protected_terms(text, metadata)` để điền `ProtectedTokens.terms`.
- `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:372-442`: `_build_custom_query()` đã tiêm `metadata`, `protected.ordered()`, `previous_suggestion`, `instruction`, `retry_findings`, nhưng chưa tiêm danh sách gợi ý chuẩn hóa đồng nghĩa (`alias -> term`) từ Từ điển Sư phạm.
- `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:476-492`: Khi `tool == 'spellcheck'`, `build_input_rails()` luôn trả về `custom_query=''` và `option=None` kể cả khi có `instruction` / `previous_suggestion` hoặc `retry_findings`.
- `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:693-702`: `_check_protected()` đang cộng dồn `protected.terms` bị thiếu vào chung `missing_names` và trả về mã `names_changed`.
- `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:745-780`: `evaluate_provider_output()` xử lý dict trả về từ `spellcheck` nhưng chưa loại bỏ các `issues` sửa nhầm chính thuật ngữ SGK đã được khóa trong `protected.terms`.
- `backend/services/api/src/bookforge_api/api/assistant_tools.py:92-109, 645-709`: Endpoint `POST /api/assistant-tools/quick-edit` đã truy vấn bảng `Document` để kiểm tra quyền truy cập (`_validated_document_ids`), nhưng chưa trích xuất `doc.title`, `doc.document_type`, `doc.metadata_json` để bổ sung ngữ cảnh môn/lớp cho `payload.doc_metadata`.

## 3. Kiểm tra spec
Không áp dụng (Cách 3: Việc thường).

## 4. Điểm va chạm
1. **Tương thích ngược với toàn bộ unit test hiện có (`tests/test_quick_edit_rails.py`, `tests/test_assistant_quick_edit.py`):**
   - `test_collect_protected_tokens_auto_detects_kinds` (`test_quick_edit_rails.py:92-106`) truyền trực tiếp `DefaultPedagogicalDictionary()` và kiểm tra `assert tokens.terms == ()`. Do đó phải giữ nguyên `DefaultPedagogicalDictionary` trả về `()`, và tạo lớp mới `SchoolGlossaryPedagogicalDictionary` gán cho `_pedagogical_dictionary`.
   - Các câu mẫu trong test cũ (như `BOILING = 'Nước sôi ở 100 độ C khi áp suất bình thường.'` khi test rút gọn/viết lại thành `'Nước sôi ở 100 độ C.'` tại `test_assistant_quick_edit.py:363-378`) không truyền `subject`. Để không sinh cảnh báo giả (`terms_changed`) làm đổi `status` từ `ok` sang `needs_review` ở các câu văn đời thường khi tài liệu không có ngữ cảnh môn học, `SchoolGlossaryPedagogicalDictionary` sẽ:
     - Luôn tra bộ từ điển `chung` (chứa các thuật ngữ sư phạm đặc thù như *năng lực đặc thù, phẩm chất chủ yếu, yêu cầu cần đạt, rubric...*).
     - Tra bộ từ điển môn học cụ thể (`sinh_hoc`, `vat_ly`, `hoa_hoc`, `toan`, v.v.) khi xác định được môn học từ `doc_metadata` (`subject`, `title`) hoặc từ nội dung văn bản (`parse_subject_and_grade`).
2. **Hợp đồng hàm `prov.spellcheck` trong `_StubProvider` (`test_assistant_quick_edit.py:59-62, 144-145`):**
   - Khi `tool == 'spellcheck'` ở lần gọi thông thường (không có `instruction`, `previous_suggestion`, `retry_findings`), `rails.provider_text` giữ nguyên là `text` và `rails.custom_query == ''`, gọi `prov.spellcheck(text=rails.provider_text, max_output_tokens=...)` như cũ.
   - Khi `tool == 'spellcheck'` có `instruction` / `previous_suggestion` hoặc `retry_findings`, `build_input_rails` tạo `custom_query` và `_quick_edit_provider_call` sử dụng `prov.editor_rewrite` (với `option='Proofread'`) để thực hiện tinh chỉnh/thử lại có hướng dẫn.

## 5. Phương án đề xuất
1. **Trong `backend/services/api/src/bookforge_api/services/quick_edit_rails.py`:**
   - Thêm lớp `SchoolGlossaryPedagogicalDictionary`:
     - Sử dụng dữ liệu từ điển đã cache trên RAM của `school_glossary._load_glossary_seed_rows()` và `parse_subject_and_grade` để tra cứu cực nhanh (< 1ms).
     - Cung cấp `protected_terms(text, doc_metadata)`: trả về các thuật ngữ chuẩn xuất hiện trong `text` thuộc bộ từ điển `chung` và môn học/khối lớp xác định từ `doc_metadata` (`subject`, `grade`, `title`) hoặc từ `text`.
     - Cung cấp `normalization_hints(text, doc_metadata)`: trả về danh sách gợi ý chuẩn hóa `"<alias>" -> "<term>"` khi `text` chứa từ đồng nghĩa (`aliases`) trong từ điển đang kích hoạt.
   - Trong `_build_custom_query()`: nếu `normalization_hints` khác rỗng, chèn chỉ dẫn chuẩn hóa thuật ngữ vào prompt.
   - Trong `build_input_rails()` và `evaluate_provider_output()`:
     - Hỗ trợ `spellcheck` khi có `instruction` / `previous_suggestion` / `retry_findings`.
     - Trong `evaluate_provider_output()`, nếu kết quả JSON của `spellcheck` có mục `issues` sửa mất một thuật ngữ nằm trong `protected.terms` và làm thuật ngữ đó biến mất khỏi `fixed_text`, tự động khôi phục thuật ngữ được bảo vệ trong `fixed_text` và loại bỏ `issue` sửa nhầm đó.
   - Trong `_check_protected()`: tách `missing_terms` khỏi `missing_names`, trả về `RailFinding('terms_changed', 'warning', f'Thuật ngữ chuyên môn có thể đã bị thay đổi: {_short_list(missing_terms)}.')`.
2. **Trong `backend/services/api/src/bookforge_api/api/assistant_tools.py`:**
   - Thêm hàm `_enrich_quick_edit_metadata(db, payload, document_ids)` để lấy `title`, `document_type`, `metadata_json` từ bản ghi `Document` (khi có `document_ids`) và kết hợp `context_before` / `context_after` nhằm điền `subject`, `grade`, `doc_type` vào `payload.doc_metadata` trước khi chạy `_run_quick_edit`.

## 6. Câu hỏi kỹ thuật còn mở
Không còn (đã chốt toàn bộ ở Mục 0).
