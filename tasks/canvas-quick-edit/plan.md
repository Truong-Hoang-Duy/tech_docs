# Kế hoạch: Hoàn thiện Backend AI Quick Edit (Từ điển Sư phạm, Đường ray Tạo sinh & Hậu kiểm Thuật ngữ)

**Ngày:** 2026-11-08 · **Cách làm:** Cách 3: Việc thường · **Phía:** BE
**Trạng thái:** IN_PROGRESS
**Mốc code:** backend `48a28e31` · frontend `fbd52874` · **Nhánh:** `feat/canvas-quick-edit`

## 1. Mục tiêu và quyết định đã chốt
- **Mục tiêu:** Kết nối thật hệ thống xử lý phía sau (Backend) của bộ 5 công cụ **AI Quick Edit** với **Bộ Từ điển Sư phạm & SGK (10 môn cấp THPT + bộ từ điển Chung)**, bổ sung gợi ý chuẩn hóa từ đồng nghĩa, tự động làm giàu ngữ cảnh môn/lớp từ hồ sơ tài liệu trong DB, đưa công cụ **Sửa chính tả** vào chung hàng rào bảo vệ thuật ngữ và tách cảnh báo riêng khi thuật ngữ chuyên môn bị thay đổi.
- **Quyết định đã chốt** (không tự đổi khi làm):
  1. **Chỉ làm ở phía Backend (`backend/`), còn giao diện (`frontend/`) kéo từ working tree mới nhất (`fbd52874`) về và giữ nguyên:** Tận dụng trực tiếp vùng hiển thị *"Đã giữ nguyên: ..."* (`preserved_terms`) và khung cảnh báo (`warnings`) đã có sẵn trên giao diện bảng xem trước chuẩn Figma.
  2. **Tự động tra cứu Từ điển Sư phạm & SGK ở phía sau:** Luôn bao gồm bộ từ điển *Chung (sư phạm, GDPT 2018)* kết hợp với bộ từ điển môn học/khối lớp suy luận từ `doc_metadata`, hồ sơ `Document` trong DB (`title`, `document_type`, `metadata_json`) và nội dung đoạn văn; đồng thời giữ nguyên lớp `DefaultPedagogicalDictionary` làm stub rỗng để tương thích ngược với các unit test gọi trực tiếp.
  3. **Bảo vệ thuật ngữ cho cả 5 công cụ (bao gồm `spellcheck`) và tách mã cảnh báo `terms_changed`:** Ngăn `spellcheck` sửa nhầm thuật ngữ chuyên môn đã khóa, hỗ trợ `spellcheck` khi có yêu cầu tinh chỉnh (`instruction` / `previous_suggestion`) hoặc retry, và tách riêng cảnh báo `terms_changed` (*"Thuật ngữ chuyên môn có thể đã bị thay đổi: ..."*) khỏi `names_changed`.
- **Tài liệu trong `backend/`:** Chốt khi hoàn tất Giai đoạn 3 (theo xác nhận của bạn).

## 2. Các Task (mỗi Task là một phần bạn bấm thử được)

### Task 1: Kết nối Từ điển Sư phạm & SGK, chuẩn hóa từ đồng nghĩa và tự động làm giàu ngữ cảnh tài liệu
- [ ] **Xong** · **Bạn đã kiểm:** chưa
- **Thao tác để kiểm:** Mở một tài liệu trên trình soạn thảo Canvas (ví dụ tài liệu có tiêu đề *"Giáo án Sinh học 10 - Bài 5"* hoặc đoạn văn có thuật ngữ *"quang hợp"*, *"lục lạp"*, *"năng lực đặc thù"*), bôi đen đoạn văn → bấm chuột phải → **Công cụ AI** → chọn **Chỉnh diễn đạt** hoặc **Rút gọn**.
- **✅ Đúng khi thấy:** Bảng xem trước hiện kết quả biên tập giữ nguyên thuật ngữ SGK chuẩn và dòng thông tin bên dưới hiện rõ *"Đã giữ nguyên: quang hợp, lục lạp..."*; nếu đoạn văn chứa từ đồng nghĩa trong từ điển, chỉ dẫn gửi cho AI có kèm gợi ý chuẩn hóa về thuật ngữ chuẩn.
- **❌ Sai nếu thấy:** Dòng *"Đã giữ nguyên"* chỉ hiện số liệu/tên riêng mà không nhận diện được thuật ngữ SGK hoặc sư phạm có trong đoạn chọn.
- **Kiểm tra tự động:** `cd /Users/truonghoangduy/Documents/Project/bookforge/backend/services/api && uv run pytest tests/test_quick_edit_rails.py tests/test_assistant_quick_edit.py -k "dictionary or glossary or metadata" -q`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:165-194, 325-442, 463-525` — Xây dựng lớp `SchoolGlossaryPedagogicalDictionary` kết nối với dữ liệu từ điển đã cache của `school_glossary._load_glossary_seed_rows()` và `parse_subject_and_grade`; cài đặt làm mặc định cho `_pedagogical_dictionary` (giữ `DefaultPedagogicalDictionary` trả về `()` cho unit test); bổ sung hàm `normalization_hints(text, doc_metadata)` và tiêm gợi ý chuẩn hóa `"<alias>" -> "<term>"` vào `_build_custom_query()`. Xử lý trường hợp biên: khi tài liệu không có nhãn môn học và câu văn đời thường không nhắc tới môn học, chỉ kích hoạt bộ từ điển `chung` để không khóa nhầm từ thông thường.
  - `backend/services/api/src/bookforge_api/api/assistant_tools.py:92-109, 645-709` — Bổ sung hàm `_enrich_quick_edit_metadata(db, payload, document_ids)` đọc `title`, `document_type`, `metadata_json` từ bản ghi `Document` trong DB (khi `document_ids` được truyền lên) và suy luận `subject`, `grade`, `doc_type` để làm giàu `payload.doc_metadata` trước khi chạy `_run_quick_edit`.
  - `backend/services/api/tests/test_quick_edit_rails.py:114-126` & `backend/services/api/tests/test_assistant_quick_edit.py:381-394` — Bổ sung unit test và integration test kiểm tra nhận diện thuật ngữ SGK theo môn/lớp, gợi ý chuẩn hóa từ đồng nghĩa (`aliases`), và tự động suy luận môn/lớp từ `Document.title` / `Document.metadata_json`.

### Task 2: Đưa công cụ Sửa chính tả (`spellcheck`) vào hàng rào bảo vệ thuật ngữ & tách cảnh báo `terms_changed`
- [ ] **Xong** · **Bạn đã kiểm:** chưa
- **Thao tác để kiểm:** Quét chọn một đoạn văn có lỗi chính tả kèm thuật ngữ chuyên môn (ví dụ *"Quá trình quang hợp diễn ra ở lục lạp trong tế bào thực vât."*) → bấm chuột phải → **Công cụ AI** → chọn **Sửa chính tả**; sau đó thử chọn **Rút gọn** trên đoạn có thuật ngữ chuyên môn.
- **✅ Đúng khi thấy:** Công cụ **Sửa chính tả** chỉ sửa từ sai chính tả (*"vât"* → *"vật"*), giữ nguyên tuyệt đối thuật ngữ chuyên môn (*"quang hợp"*, *"lục lạp"*) và liệt kê vào *"Đã giữ nguyên: ..."*; nếu AI làm mất thuật ngữ chuyên môn khi biên tập, khung cảnh báo vàng hiện rõ *"Thuật ngữ chuyên môn có thể đã bị thay đổi: ..."* (mã `terms_changed`).
- **❌ Sai nếu thấy:** **Sửa chính tả** sửa nhầm thuật ngữ chuyên môn/kí hiệu nằm trong danh sách bảo vệ, hoặc khi mất thuật ngữ lại báo nhầm mã `names_changed` chung với tên riêng.
- **Kiểm tra tự động:** `cd /Users/truonghoangduy/Documents/Project/bookforge/backend/services/api && uv run pytest tests/test_quick_edit_rails.py tests/test_assistant_quick_edit.py -q`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:476-492, 655-712, 745-780` — (1) Trong `_check_protected()`, tách các thuật ngữ bị mất thuộc `protected.terms` thành cảnh báo riêng `RailFinding('terms_changed', 'warning', 'Thuật ngữ chuyên môn có thể đã bị thay đổi: ...')`; (2) trong `evaluate_provider_output()`, ngăn các mục `issues` của `spellcheck` sửa nhầm những thuật ngữ đã được khóa trong `protected.terms` / `protected.formulas`; (3) trong `build_input_rails()`, khi `tool == 'spellcheck'` có kèm `instruction` / `previous_suggestion` hoặc `retry_findings`, sinh `custom_query` có kiểm soát để hỗ trợ tinh chỉnh và thử lại.
  - `backend/services/api/src/bookforge_api/api/assistant_tools.py:634-668` — Trong `_quick_edit_provider_call()`, khi `rails.tool == 'spellcheck'` có `rails.custom_query` (trường hợp tinh chỉnh hoặc retry sau lỗi Output Rails), định tuyến qua `prov.editor_rewrite` với `option='Proofread'`; lần gọi `spellcheck` mặc định vẫn gọi `prov.spellcheck(text=rails.provider_text, ...)` để giữ nguyên hợp đồng JSON `issues`.
  - `backend/services/api/src/bookforge_api/llm/editor_tools.py:314-320` — Củng cố hướng dẫn trong `build_spellcheck_prompt` để giữ nguyên thuật ngữ chuyên môn SGK, công thức, kí hiệu khoa học và tên riêng.
  - `backend/services/api/tests/test_quick_edit_rails.py:288-378` & `backend/services/api/tests/test_assistant_quick_edit.py:123-147, 253-278` — Bổ sung test kiểm tra cảnh báo `terms_changed`, chống sửa nhầm thuật ngữ trong `spellcheck`, và luồng tinh chỉnh/retry của `spellcheck`.

## 3. Điều kiện hoàn thành
- [ ] Toàn bộ kiểm tra như CI của `backend/services/api` đều đúng:
  - `cd /Users/truonghoangduy/Documents/Project/bookforge/backend/services/api && uv run ruff check .`
  - `cd /Users/truonghoangduy/Documents/Project/bookforge/backend/services/api && uv run ruff format --check .`
  - `cd /Users/truonghoangduy/Documents/Project/bookforge/backend/services/api && uv run pytest tests/test_quick_edit_rails.py tests/test_assistant_quick_edit.py tests/test_school_glossary.py`
- [ ] Cả 5 công cụ AI Quick Edit đều nhận diện đúng thuật ngữ từ `SchoolGlossaryService` (`preserved_terms`), gợi ý chuẩn hóa từ đồng nghĩa (`aliases`), làm giàu ngữ cảnh môn/lớp từ `Document` trong DB, và cảnh báo `terms_changed` khi thuật ngữ chuyên môn bị biến đổi.
- [ ] Không có bất kỳ thay đổi nào trong `frontend/` (giữ nguyên mốc `fbd52874`) và không lọt chữ `tech_docs`, `analysis.md`, `plan.md` vào `backend/`.

## 4. Kiểm kế hoạch
- **`file:dòng`, tên hàm có thật:** Đã đọc và đối chiếu từng dòng tại `services/quick_edit_rails.py:165-194, 325-442, 476-525, 655-712, 745-780`, `api/assistant_tools.py:92-109, 634-709`, `services/school_glossary.py:188-301, 408-708`, `llm/editor_tools.py:314-320`, `tests/test_quick_edit_rails.py:1-382`, `tests/test_assistant_quick_edit.py:1-513`.
- **Lệnh kiểm tra chạy được:** Đã chạy thử `uv run pytest tests/test_quick_edit_rails.py tests/test_assistant_quick_edit.py -q` → `81 passed, 64 warnings in 40.35s`.
- **Mục tiêu, nghiệp vụ, điều đã chốt đều có Task:** Đủ 2 Task bao phủ toàn bộ yêu cầu Backend (Task 1: Từ điển Sư phạm & SGK + đồng nghĩa + ngữ cảnh tài liệu DB; Task 2: `spellcheck` + cảnh báo `terms_changed`).
- **Mọi Task có tiêu chí:** Đủ thao tác kiểm, dấu hiệu đúng/sai, lệnh kiểm tự động và danh sách `file:dòng`.
- **Cần bạn quyết:** Không có (đã chốt toàn bộ).

## 5. Nhật ký làm
- **Kiểm tra trước khi sửa** (để phân biệt lỗi có sẵn): `cd /Users/truonghoangduy/Documents/Project/bookforge/backend/services/api && uv run pytest tests/test_quick_edit_rails.py tests/test_assistant_quick_edit.py -q` → `81 passed, 64 warnings in 40.35s`
- **Tạo nhánh:** `git checkout -b feat/canvas-quick-edit` từ `dev` (`48a28e31`).
- **Quyết định phát sinh:** Không có
- **Kết quả từng Task:**
  - **Task 1:**
    - Lệnh kiểm tự động: `cd /Users/truonghoangduy/Documents/Project/bookforge/backend/services/api && uv run pytest tests/test_quick_edit_rails.py tests/test_assistant_quick_edit.py -k "dictionary or glossary or metadata" -n 0 -q` → `7 passed, 77 deselected, 8 warnings in 7.52s`
    - Dữ liệu mẫu & tự kiểm: Đã tạo tài liệu mẫu `14a43664-12a6-4180-a2a6-54beae7f9dbe` (*"Giáo án Sinh học 10 - Bài 12: Quang hợp ở thực vật"*) cho tài khoản `owner@example.com` và gọi thử trực tiếp `POST /api/assistant-tools/quick-edit` (`tool='refine'`) → kết quả `status='ok'`, `preserved_terms=['quang hợp', 'lục lạp', 'tế bào', 'năng lượng']`, và câu chứa `KHBD`, `PHT` được chuẩn hóa thành `Kế hoạch bài dạy (KHBD) và Phiếu học tập (PHT)` kèm `preserved_terms=['KHBD', 'PHT', 'yêu cầu cần đạt', 'năng lực đặc thù']`.

## 6. Nghiệm thu
- **Ngày:** Chờ thực hiện ở Giai đoạn 2
- **Thay đổi so với kế hoạch:** Chờ thực hiện ở Giai đoạn 2
- **Từng nghiệp vụ (`analysis.md` mục 3.0, nếu có):** Không áp dụng (Cách 3)
- **Chạy lại toàn bộ kiểm tra:** Chờ thực hiện ở Giai đoạn 2
- **Không lọt chữ `tech_docs` vào backend / frontend:** Chờ thực hiện ở Giai đoạn 2
- **Kết luận:** Chờ thực hiện ở Giai đoạn 2

## 7. Kiểm tay
- **Kết quả:** Chờ thực hiện ở Giai đoạn 3

## 8. Commit
- **Tài liệu trong `backend/`:** Chờ chốt ở Giai đoạn 3
- **Mã commit:** backend `74f74e2f` (nhánh `origin/feat/canvas-quick-edit`, đã push Task 1) · frontend `fbd52874` (không đổi) · **Đã push và merge `dev`:** đã push nhánh `origin/feat/canvas-quick-edit`, chờ xong Task 2 mới merge `dev`

## 9. Việc còn treo
- Không có

## 10. Số đo
- **Bắt đầu:** 2026-11-08 · **Merge:** Chờ hoàn tất
- **Số lỗi bạn bắt được khi kiểm tay:** 0
- **Số lần phải sửa sau merge:** 0

