# Kế hoạch: Tích hợp Từ điển SGK & Đường ray tạo sinh cho phần Chat (Backend & Handoff FE)

**Ngày:** 2026-11-07 · **Cách làm:** Cách 3: Việc thường · **Phía:** BE
**Trạng thái:** APPROVED
**Mốc code:** backend `e0518935` · frontend `08819f6` · **Nhánh:** `feat/chat-glossary-context`

## 1. Mục tiêu và quyết định đã chốt
- **Mục tiêu:**
  1. Đóng gói kho Từ điển SGK (29 tệp JSON 10 môn THPT từ `review-station` đã lọc watermark + bộ từ điển `"Chung (sư phạm, giáo dục)"`) vào SQLite + FTS5 tại Backend (`services/school_glossary.py`, `data/school_glossary.jsonl.gz`).
  2. Mở rộng API `GET /api/chat/modes`, API phiên chat (`POST/GET/PATCH /api/chat/sessions`) và API gửi tin nhắn (`POST /api/chat/sessions/{session_id}/messages`, `/messages/stream`) để cung cấp danh mục và thực thi cấu hình `context_settings` (bật/tắt Từ điển SGK + bật/tắt 5 quy tắc Đường ray tạo sinh) cho cả Chat chung và 5 Agent chuyên biệt.
  3. Khi hoàn tất nghiệm thu, hỏi và xuất tài liệu `plan` / `spec` cùng **Tài liệu Handoff cho Frontend** theo đường dẫn bạn chỉ định.
- **Quyết định đã chốt** (không tự đổi khi làm):
  1. **Chỉ sửa Backend (`Phía: BE`)**: Không sửa code trong repo `frontend/`, không sửa khung chat trong trình soạn thảo Canvas (`chat/editor_agent.py`).
  2. **Đường ray tạo sinh (`generative_rails`)**: Không đẻ thêm quy tắc mới; trả về **đầy đủ 5 quy tắc có sẵn của hệ thống** (`sovereignty` — Tôn trọng chủ quyền biển đảo Việt Nam; `academic_style` — Phong cách học thuật & sư phạm chuẩn mực; `source_grounding` — Bám sát nguồn tài liệu, không bịa trích dẫn; `academic_integrity` — Liêm chính học thuật & Quyết định 705; `school_rules` — Tuân thủ quy chế nhà trường) và **cho phép bật/tắt tự do tất cả 5 quy tắc** (`locked: false`).
  3. **Danh mục Từ điển sư phạm (`glossaries`)**: Khớp thiết kế giao diện — nhóm hiển thị chính (`is_primary: true`) gồm `chung` (*Chung (sư phạm, giáo dục)*), `toan` (*Toán học*), `ngu_van` (*Ngữ văn*), `khtn` (*Khoa học tự nhiên* — nhóm gộp tự kích hoạt `vat_ly`, `hoa_hoc`, `sinh_hoc`); nhóm mở rộng trong menu *Khác...* (`is_primary: false`) gồm 8 môn lẻ (`vat_ly`, `hoa_hoc`, `sinh_hoc`, `lich_su`, `dia_ly`, `gdktpl`, `tieng_anh`, `tin_hoc`).
  4. **Đặt tên tiếng Anh thông dụng**: Dùng `chat-glossary-context` và `school_glossary` / `glossary`, không dùng từ `pedagogical` cho tên file/schema mới.
- **Tài liệu trong `backend/`:** Chốt khi hoàn tất Giai đoạn 2 (sẽ hỏi bạn tạo `plan`, `spec` và đường dẫn lưu **Tài liệu Handoff cho Frontend**).

## 2. Các Task (mỗi Task là một phần bạn bấm thử được)

### Task 1: Đóng gói Kho Từ điển SGK (10 môn THPT + bộ từ điển Chung) và dịch vụ tra cứu `SchoolGlossaryService`
- [ ] **Xong** · **Bạn đã kiểm:** chưa
- **Thao tác để kiểm:** Chạy lệnh kiểm tra tự động hoặc mở terminal tại `backend/services/api` chạy lệnh tra cứu thử từ điển môn Toán / Sinh học / Chung và nhóm gộp `khtn`.
- **✅ Đúng khi thấy:**
  - File `data/school_glossary.jsonl.gz` tự bung ra `school_glossary.sqlite` chứa đầy đủ 29 bộ từ điển SGK (10 môn khối 10–12) và bộ từ điển `chung` (GDPT 2018), hoàn toàn không còn dính chữ `Kết nối tri thức`, `KNTT`, `Global Success` hay tên NXB.
  - Khi tra cứu theo bài học (ví dụ: *Toán 10 - Bài 1: Mệnh đề* hoặc *Sinh học 12 - Bài 1*) trả về đúng danh sách thuật ngữ (`term`, `aliases`, `english`, `notation`, `meaning`, `usage_context`, `source_status`) kèm quy ước chương (`conventions`).
  - Khi chọn nhóm `khtn`, hệ thống tự động mở rộng tra cứu trên cả 3 môn `vat_ly`, `hoa_hoc`, `sinh_hoc`.
- **❌ Sai nếu thấy:** Thiếu môn học, còn sót tên bộ sách/NXB, hoặc tra cứu theo bài học/văn bản trả về rỗng.
- **Kiểm tra tự động:** `cd backend/services/api && uv run pytest -n 0 tests/test_school_glossary.py tests/test_bookforge_default_kb.py`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/services/school_glossary.py` (tạo mới) — Nạp 29 file `review-station/data/glossary/units/*.json` + bộ từ điển `chung`, lọc qua `strip_brand_watermarks` (`services/bookforge_default_kb.py:140-185`), khởi tạo SQLite + FTS5 (`glossary_chapters`, `glossary_terms`, `glossary_terms_fts`), cung cấp `SchoolGlossaryService` (`lookup_lesson_glossary`, `lookup_text_glossary`, `expand_glossary_domains`, `format_glossary_prompt_block`).
  - `backend/services/api/src/bookforge_api/data/school_glossary.jsonl.gz` (tạo mới) — Bundle dữ liệu từ điển đã chuẩn hóa.
  - `backend/services/api/tests/test_school_glossary.py` (tạo mới) — Kiểm tra đủ 10 môn THPT + bộ `chung`, kiểm tra chống rò rỉ thương hiệu, tra cứu theo bài học, tra cứu FTS5 theo văn bản và gộp nhóm `khtn`.

### Task 2: Mở rộng API Danh mục tùy chọn Chat (`GET /api/chat/modes`) và Lưu cấu hình `context_settings` theo phiên Chat (`POST/GET/PATCH /api/chat/sessions`)
- [ ] **Xong** · **Bạn đã kiểm:** chưa
- **Thao tác để kiểm:** Mở Swagger UI (`http://localhost:8000/docs`) hoặc gọi API `GET /api/chat/modes`, `POST /api/chat/sessions`, `PATCH /api/chat/sessions/{session_id}` và `GET /api/chat/sessions/{session_id}`.
- **✅ Đúng khi thấy:**
  - `GET /api/chat/modes` trả về thêm trường `context_options` gồm:
    - `glossaries`: 4 mục `is_primary=true` (`chung`, `toan`, `ngu_van`, `khtn` có `expanded_ids=["vat_ly","hoa_hoc","sinh_hoc"]`) và 8 mục `is_primary=false` (`vat_ly`, `hoa_hoc`, `sinh_hoc`, `lich_su`, `dia_ly`, `gdktpl`, `tieng_anh`, `tin_hoc`).
    - `generative_rails`: đủ 5 quy tắc (`sovereignty`, `academic_style`, `source_grounding`, `academic_integrity`, `school_rules`) với `locked=false` và `default_enabled=true`.
    - `default_settings`: `{ "glossary_enabled": true, "glossary_ids": ["chung"], "rails_enabled": true, "rail_ids": ["sovereignty", "academic_style", "source_grounding", "academic_integrity", "school_rules"] }`.
  - Khi gọi `PATCH /api/chat/sessions/{session_id}` cập nhật `context_settings` (ví dụ bật thêm từ điển `toan` và tắt 1 quy tắc đường ray), `GET /api/chat/sessions/{session_id}` trả về đúng `context_settings` đã lưu.
- **❌ Sai nếu thấy:** `GET /api/chat/modes` thiếu trường `context_options`, quy tắc bị khóa `locked=true`, hoặc `PATCH /api/chat/sessions/{session_id}` không lưu được `context_settings`.
- **Kiểm tra tự động:** `cd backend/services/api && uv run pytest -n 0 tests/test_api_contract_generator.py tests/test_school_glossary.py`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/models/document.py:294-325` — Thêm cột `context_settings_json: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)` vào `ChatSession`.
  - `backend/services/api/alembic/versions/0127_chat_session_context_settings.py` (tạo mới) — Migration thêm cột `context_settings_json` vào bảng `chat_sessions` (kiểm tra tồn tại cột an toàn như `0126_user_and_role_position.py:19-33`).
  - `backend/services/api/src/bookforge_api/schemas/chat.py:16-46, 84-106, 169-177` — Khai báo `ChatContextSettings`, `ChatGlossaryOption`, `ChatRailOption`, `ChatContextOptions`; bổ sung `context_settings` vào `ChatSessionCreateRequest`, `ChatSessionUpdateRequest`, `ChatSessionListItem`, `ChatMessageCreateRequest` và `context_options` vào `ChatModeOptionsResponse`.
  - `backend/services/api/src/bookforge_api/api/chat.py:449-489, 2580-2606, 2697-2810` — Cập nhật `_serialize_session`, `get_chat_modes`, `create_chat_session`, `update_chat_session` để trả về và lưu `context_settings`.

### Task 3: Thực thi bật/tắt 5 quy tắc Đường ray tạo sinh & Bơm ngữ cảnh Từ điển vào luồng Chat chính (`POST /api/chat/sessions/{session_id}/messages` & `/messages/stream`)
- [ ] **Xong** · **Bạn đã kiểm:** chưa
- **Thao tác để kiểm:** Gửi tin nhắn qua `POST /api/chat/sessions/{session_id}/messages` (hoặc `/messages/stream`) trong 2 kịch bản: (1) Bật từ điển `toan` + bật đường ray; (2) Tắt từ điển hoặc tắt từng quy tắc trong `rail_ids` (kể cả tắt `sovereignty` hoặc `academic_integrity` hoặc `school_rules`).
- **✅ Đúng khi thấy:**
  - Khi bật `glossary_enabled=true` với `glossary_ids=["chung", "toan"]`, system prompt nhận được khối `<school_glossary>` chứa đúng các thuật ngữ SGK Toán khớp với câu hỏi, và `assistant_message.metadata.context_settings` ghi nhận rõ bộ từ điển + đường ray đã áp dụng.
  - Khi tắt một quy tắc trong `rail_ids` (hoặc đặt `rails_enabled=false`), quy tắc đó thực sự được gỡ khỏi bước kiểm tra preflight (`evaluate_preflight_policy`), khối chỉ dẫn hệ thống (`build_governance_instruction`), và bước kiểm duyệt cuối (`verify_answer_against_school_rules`).
  - Khi không truyền `context_settings`, hành vi mặc định giữ nguyên 100% như cũ (không làm đỏ bất kỳ test cũ nào của `test_governance_instruction.py` hay `test_chat_page_awareness.py`).
- **❌ Sai nếu thấy:** Tắt quy tắc trên `context_settings` nhưng hệ thống vẫn chặn hoặc vẫn bơm quy tắc đó vào prompt; hoặc làm hỏng các test kiểm tra `GOVERNANCE_INSTRUCTION` mặc định.
- **Kiểm tra tự động:** `cd backend/services/api && uv run pytest -n 0 tests/test_governance_instruction.py tests/test_chat_page_awareness.py tests/test_school_glossary.py`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/chat/governance.py:25-111` — Hỗ trợ tham số tùy chọn `active_rail_ids: set[str] | None = None` trong `build_governance_instruction` (khi `active_rail_ids is None` hoặc đủ 5 quy tắc thì trả về nguyên vẹn `GOVERNANCE_INSTRUCTION` để tương thích tuyệt đối với test cũ; khi tắt từng quy tắc thì chỉ ghép các quy tắc đang bật).
  - `backend/services/api/src/bookforge_api/services/governance/policy_guard.py:120-254` — Hỗ trợ `active_rail_ids: set[str] | None = None` trong `evaluate_preflight_policy` để bỏ qua kiểm tra chặn `academic_integrity` khi quy tắc này bị tắt.
  - `backend/services/api/src/bookforge_api/chat/adk_agent.py:1749-1941, 1969-2088` — Truyền `context_settings` và `glossary_section` vào `_agent_instruction`, `_build_chat_agent`, `run_adk_chat`; điều khiển quy tắc `source_grounding`, `academic_style`, `school_rules` theo `active_rail_ids`.
  - `backend/services/api/src/bookforge_api/api/chat.py:1400-1587, 1970-2135, 2352-2545, 3307-3540, 3566-3715` — Hợp nhất `payload.context_settings` với `session.context_settings_json`, truyền xuống `_run_free_chat`, `_run_scoped_chat`, `_stream_chat_events`, và ghi vào `assistant_message.metadata`.

### Task 4: Tích hợp Từ điển SGK vào 5 Agent chuyên biệt (`Phiếu điền khuyết`, `Ma trận đề`, `Tạo đề kiểm tra`, `Dịch học thuật`, `Thiết kế Infographic`)
- [ ] **Xong** · **Bạn đã kiểm:** chưa
- **Thao tác để kiểm:** Gọi lần lượt 5 Agent chuyên biệt qua API Chat (`agent_id` tương ứng) hoặc chạy bộ kiểm tra tích hợp 5 Agent kèm `context_settings` bật từ điển môn học.
- **✅ Đúng khi thấy:**
  - **Agent Phiếu điền khuyết** (`agent-phieu-dien-khuyet`): Nguồn bài học và prompt sinh phiếu được đính kèm danh sách thuật ngữ chuẩn (`in_source` / `described`), `aliases` và `meaning` của bài học đó từ `SchoolGlossaryService`.
  - **Agent Ma trận đề** (`agent-ma-tran-de`): Nguồn phạm vi kiểm tra có đầy đủ thuật ngữ chuẩn và quy ước chương (`conventions`) từ từ điển SGK.
  - **Agent Tạo đề kiểm tra** (`agent-tao-de-kiem-tra`): Hàm tách từ khóa chủ đề (`_tokenize_topic`) mở rộng thêm `aliases` và `term` từ từ điển để khớp câu hỏi trong Ngân hàng câu hỏi chính xác hơn.
  - **Agent Dịch học thuật** (`agent-dich-hoc-thuat`): Tự động tra cứu các thuật ngữ SGK xuất hiện trong văn bản cần dịch (cặp Tiếng Việt `term` ↔ Tiếng Anh `english` / `notation` + `meaning`) và đưa vào ngữ cảnh dịch + Bảng thuật ngữ đối chiếu.
  - **Agent Thiết kế Infographic** (`agent-thiet-ke-infographic`): Bơm danh sách thuật ngữ, kí hiệu và giải nghĩa chuẩn của bài học vào `generate_infographic_spec`.
- **❌ Sai nếu thấy:** Một trong 5 Agent không nhận được ngữ cảnh từ điển khi `glossary_enabled=true` hoặc vẫn tra cứu từ điển khi người dùng đã tắt (`glossary_enabled=false`).
- **Kiểm tra tự động:** `cd backend/services/api && uv run pytest -n 0 tests/test_school_glossary.py tests/test_bookforge_default_kb.py`
- **File và thay đổi:**
  - `backend/services/api/src/bookforge_api/chat/capabilities.py:385-780` — Truyền `context_settings` vào các tool của 5 Agent chuyên biệt.
  - `backend/services/api/src/bookforge_api/chat/phieu_dien_khuyet_agent.py:293-360, 887-970, 1079-1178` — Bổ sung khối thuật ngữ chuẩn của bài học từ `SchoolGlossaryService` vào `resolve_or_propose_phieu_source_text` và `generate_phieu_dien_khuyet`.
  - `backend/services/api/src/bookforge_api/chat/ma_tran_de_agent.py:520-585, 604-700, 747-901` — Bổ sung thuật ngữ và `conventions` chương vào `resolve_or_propose_matrix_source` và `generate_ma_tran_de`.
  - `backend/services/api/src/bookforge_api/chat/de_kiem_tra_agent.py:143-162, 700-920` — Mở rộng `_tokenize_topic` và kiểm tra thuật ngữ bằng `SchoolGlossaryService` khi `glossary_enabled=true`.
  - `backend/services/api/src/bookforge_api/chat/dich_hoc_thuat_agent.py:59-160, 239-302` & `chat/adk_agent.py:1889-1890` — Tự động đính kèm bảng tra cứu thuật ngữ Việt ↔ Anh (`term`, `english`, `notation`, `meaning`) vào ngữ cảnh dịch học thuật.
  - `backend/services/api/src/bookforge_api/chat/infographic_agent.py:1178-1235, 1355-1454, 1576-1682` — Bổ sung thuật ngữ và kí hiệu chuẩn của bài học vào `resolve_or_propose_infographic_source` và `generate_infographic_spec`.

## 3. Điều kiện hoàn thành
- [ ] Toàn bộ kiểm tra như CI (`backend/.github/workflows/ci.yml:84-96`) đều đúng:
  - `cd backend/services/api && uv run ruff check .`
  - `cd backend/services/api && uv run ruff format --check .`
  - `cd backend/services/api && uv run pytest`
- [ ] Đóng gói đủ 29 bộ từ điển SGK (10 môn lớp 10–12) từ `review-station/data/glossary/units/*.json` + bộ từ điển `chung`, không rò rỉ tên bộ sách/nhà xuất bản.
- [ ] Tất cả 5 quy tắc Đường ray tạo sinh và 12 tùy chọn Từ điển sư phạm (4 mục chính + 8 môn lẻ trong *Khác...*) hoạt động đúng theo 3 quyết định đã chốt (`1b, 2a, 3a`).
- [ ] Ở bước nghiệm thu cuối Giai đoạn 2: hỏi bạn việc tạo `plan` / `spec` và **hỏi đường dẫn để xuất file Tài liệu Handoff cho Frontend** (đầy đủ 6 mục đã nghiên cứu tại `analysis.md` mục 5.2).

## 4. Kiểm kế hoạch
- **`file:dòng`, tên hàm có thật:** Đã mở code kiểm tra trực tiếp toàn bộ `file:dòng` và tên hàm trong `models/document.py:294-325`, `schemas/chat.py:16-46, 84-106, 169-177`, `api/chat.py:449-489, 1400-1587, 1970-2135, 2352-2545, 2580-2606, 2697-2810, 3307-3540, 3566-3715`, `chat/governance.py:25-111`, `services/governance/policy_guard.py:120-254`, `services/school_rules.py:93-124, 168-227`, `chat/adk_agent.py:1749-1941, 1969-2088`, `services/bookforge_default_kb.py:140-185, 298-391`, và 5 file `*_agent.py`.
- **Lệnh kiểm tra chạy được:** Đã chạy thật tại `backend/services/api`:
  `uv run ruff check src/bookforge_api/chat/governance.py src/bookforge_api/schemas/chat.py; uv run pytest -n 0 tests/test_governance_instruction.py tests/test_api_contract_generator.py` → `All checks passed!`, `51 passed in 10.26s`.
- **Mục tiêu, nghiệp vụ, điều đã chốt đều có Task:** Đủ 100% (Task 1 đóng gói dữ liệu từ điển 10 môn + `chung` + nhóm `khtn`; Task 2 mở rộng API `/api/chat/modes` và `/api/chat/sessions` với 5 quy tắc `locked=false` + danh mục từ điển theo thiết kế; Task 3 thực thi bật/tắt 5 quy tắc đường ray và bơm từ điển vào Chat chính; Task 4 tích hợp từ điển vào 5 Agent chuyên biệt; Mục 3 & Mục 8 khóa bước hỏi và tạo tài liệu Handoff cho Frontend).
- **Mọi Task có tiêu chí:** Đủ (`Thao tác để kiểm`, `✅ Đúng khi thấy`, `❌ Sai nếu thấy`, `Kiểm tra tự động`, `File và thay đổi`).
- **Cần bạn quyết:** Không có (bạn đã chốt đủ 3 điểm: `1b`, `2a`, `3a`).

## 5. Nhật ký làm
- **Kiểm tra trước khi sửa** (để phân biệt lỗi có sẵn): `cd backend/services/api && uv run ruff check src/bookforge_api/chat/governance.py src/bookforge_api/schemas/chat.py && uv run pytest -n 0 tests/test_governance_instruction.py tests/test_api_contract_generator.py` → `All checks passed! / 51 passed in 10.26s`
- **Quyết định phát sinh:** Chưa có
- **Kết quả từng Task:** Chưa chạy (sẽ thực hiện ở Giai đoạn 2)

## 6. Nghiệm thu
- **Ngày:** Chưa thực hiện
- **Thay đổi so với kế hoạch:** Chưa thực hiện
- **Từng nghiệp vụ (`analysis.md` mục 3.0, nếu có):** Không áp dụng
- **Chạy lại toàn bộ kiểm tra:** Chưa thực hiện
- **Không lọt chữ `tech_docs` vào backend / frontend:** Chưa thực hiện
- **Kết luận:** Chưa thực hiện

## 7. Kiểm tay
- **Kết quả:** Chưa thực hiện (sẽ hướng dẫn và xác nhận trực tiếp trong phiên chat ở Giai đoạn 2)

## 8. Commit
- **Tài liệu trong `backend/`:** Chờ bạn xác nhận ở cuối Giai đoạn 2 (`plan` / `spec` + đường dẫn lưu **Tài liệu Handoff cho Frontend**)
- **Mã commit:** backend `chưa commit` · **Đã push và merge `dev`:** chưa

## 9. Việc còn treo
- Không có

## 10. Số đo
- **Bắt đầu:** 2026-11-07 · **Merge:** Chưa merge
- **Số lỗi bạn bắt được khi kiểm tay:** 0
- **Số lần phải sửa sau merge:** 0
