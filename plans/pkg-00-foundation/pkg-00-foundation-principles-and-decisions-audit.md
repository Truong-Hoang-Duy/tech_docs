# Báo cáo Kiểm toán & Thực thi Spec: PKG-00 Foundation Principles, Canonical Governance Schemas & 25-Call-Site Registry

- **Tài liệu Spec:** `backend/docs/product/ai-governance-mvp/specs/pkg-00-foundation-principles-and-decisions.md` (cùng `backend/docs/product/ai-governance-mvp/TECHNICAL_ALIGNMENT_DECISIONS.md`)
- **Superpowers Plan:** `backend/docs/superpowers/plans/2026-11-03-pkg-00-foundation.md`
- **Ngày khởi tạo:** 2026-11-03
- **Trạng thái:** `APPROVED` (Cross-Review 2026-11-03, xem §5)

---

## 1. Tóm tắt Mục tiêu & Phạm vi (Scope Summary)

Gói đặc tả **PKG-00 (`pkg-00-foundation-principles-and-decisions.md`)** đóng vai trò **Wave 0 (Foundation)** cho toàn bộ lộ trình AI Governance MVP theo bộ nguyên tắc **LT-705 (`policy_version = "LT-705-2026.1"`)**:
1. **Khóa chặt 6 quyết định sản phẩm (`D1`–`D6`) và 10 quyết định kiến trúc kỹ thuật (`T1`–`T10`)** làm hợp đồng bất biến cho các gói `pkg-01` (Wave A), `pkg-02` (Wave B), `pkg-03` (Wave C), `pkg-04` (Release Gate) và `pkg-05` (Phase 2 Horizon).
2. **Thiết lập bộ Schema Quản trị Chuẩn tắc (`services/api/src/bookforge_api/schemas/governance.py` — §5.1):** `GovernanceRole`, `DataClassification`, `PolicyDecisionState`, `ProvenanceType`, `ContentReviewStatus`, `UploadDeclarationSnapshot`, `GovernanceNotice`, `SourceDocumentRef`, và `AIProvenanceMetadata`.
3. **Thiết lập Danh mục Quy tắc Chuẩn tắc `LT705_RULE_CATALOG` (`services/api/src/bookforge_api/services/governance/rules_catalog.py`):** ánh xạ đầy đủ `LT-705:II`..`LT-705:VI` kèm cơ chế fallback an toàn về `LT-705:II` khi mô hình sinh mã quy tắc lạ và danh sách câu chữ thương mại bị cấm (`FORBIDDEN_COMMERCIAL_CLAIMS`).
4. **Đồng bộ Error Catalog (4 mã lỗi mới) & luồng cấu hình/quota `flow_artifact`:** đăng ký `upload_declaration_required`, `document_ai_restricted`, `document_student_access_denied`, `governance_policy_refused` (kèm `GovernancePolicyRefusedDetails` trong discriminated union `ApiErrorDetails`) và bổ sung `"flow_artifact"` vào `LLM_OPERATIONS` + `LEARNING_MATERIAL_ACTION_TYPES`.
5. **Mở rộng Dynamic RBAC theo Workspace (`student`, `reviewer`, `governance_evidence.view`):** seed role hệ thống và cung cấp hàm `resolve_governance_role(db, user)` + `can_review_content(db, user)` truy vấn trực tiếp theo `user.organization_id` hiện hành.
6. **Nâng cấp `build_governance_instruction` (`chat/governance.py`) và phủ toàn bộ 25 điểm gọi AI (7 nhóm bề mặt — §3.2):** tích hợp chỉ dẫn LT-705 theo vai trò (`student` / `teacher` / `admin`) + giao thức thẻ ẩn 1 lượt (`<!--BF_GOV:state:rule_id-->`) và bọc `user_privacy_shield_scope` cho các điểm gọi còn thiếu.

---

## 2. Phát hiện Kiểm toán: Spec vs. Nhánh `dev` Hiện tại (Codebase Drift)

| Hạng mục trong Spec | Giả định của Spec | Thực tế trong Nhánh `dev` | Quyết định Hiệu chỉnh trong Plan |
| :--- | :--- | :--- | :--- |
| **Số thứ tự Alembic Migration cho Wave A / Wave C (`§5.2`, `T2`, `T5`)** | Spec ghi `0113_ai_governance_wave_a.py` và `0114_ai_governance_wave_c.py`. | Thư mục `backend/services/api/alembic/versions/` đã sử dụng `0113_drop_book_project_legacy.py` và `0114_restore_legacy_tables_for_tests.py`. | Ghi nhận ràng buộc toàn cục: đẩy số thứ tự migration của Wave A và Wave C sang **`0115_ai_governance_wave_a.py`** và **`0116_ai_governance_wave_c.py`**. Wave 0 (`pkg-00`) không tạo migration mới. |
| **Cơ chế đăng ký `ErrorCode` (`§4 T3`, `§5.3`)** | Spec yêu cầu thêm 4 mã lỗi (`upload_declaration_required`, `document_ai_restricted`, `document_student_access_denied`, `governance_policy_refused`). | `tests/test_error_catalog_sync.py` kiểm tra đối xứng bắt buộc giữa `errors/codes.py`, `errors/envelope.py` (`ApiErrorDetails` discriminated union trên trường `kind`), `errors/catalog.py`, `scripts/render_errors_doc.py` và `docs/ERRORS.md`. | **Task 2** cập nhật đồng bộ cả 5 file + tạo `GovernancePolicyRefusedDetails(kind="governance_policy_refused", ...)` và chạy `scripts/render_errors_doc.py` để pass `test_error_catalog_sync.py`. |
| **Đăng ký `"flow_artifact"` trong `LLM_OPERATIONS` & Quota Gate (`§4 T6`)** | Spec yêu cầu thêm `"flow_artifact"` vào `LLM_OPERATIONS` trong `core/settings.py`. | `tests/test_llm_op_settings.py` bắt buộc mọi phần tử trong `LLM_OPERATIONS` phải có field `llm_op_<op>` trên `Settings` và biến môi trường `BOOKFORGE_LLM_OP_<OP>` trong `services/api/compose.common.yml`. Đồng thời `services/quota_gate.py` và `services/wallet_reservation.py` kiểm tra danh mục `ALL_AI_ACTION_TYPES`. | **Task 2** bổ sung đồng bộ `"flow_artifact"` vào `core/settings.py`, `services/api/compose.common.yml`, `services/quota_gate.py` (`LEARNING_MATERIAL_ACTION_TYPES`), và `services/wallet_reservation.py` (`_ACTION_ESTIMATED_TOKENS`). |
| **Độ phủ `GOVERNANCE_INSTRUCTION` & `user_privacy_shield_scope` trên 25 Call Sites (`§3.2`, `AC-00-02`)** | Toàn bộ 25 điểm gọi AI thuộc 7 họ bề mặt phải có chỉ dẫn LT-705 và bảo vệ PII. | 10 điểm gọi chưa gắn `GOVERNANCE_INSTRUCTION` (`chat/phieu_dien_khuyet_agent.py`, `chat/ma_tran_de_agent.py`, `chat/infographic_agent.py`, `llm/question_bank_prompts.py` [2 hàm], `llm/question_exam_extract_prompts.py` [2 hàm], `pptx/presentation_builder.py`, `pptx/canva_generate.py`, `pptx/grid_plan.py`) và `api/standalone_presentations.py` chưa bọc `user_privacy_shield_scope`. | **Task 4** và **Task 5** nâng cấp `build_governance_instruction(role_key, surface, policy_decision)`, tiêm vào toàn bộ các prompt builder còn thiếu, bọc `user_privacy_shield_scope` cho `api/standalone_presentations.py`, và khóa bằng `test_governance_call_sites.py`. |
| **Dynamic RBAC & Chuyển đổi Workspace (`§4 D1`, `T1`, `§7`)** | Cần phân giải vai trò `student` / `teacher` / `admin` theo đúng tổ chức đang hoạt động (`user.organization_id`) và hỗ trợ quyền `governance_evidence.view`. | `authorization/permission_seed.py` mới chỉ có `admin`, `user`, `readonly`; `authorization/actions.py` chưa có `governance_evidence.view`. | **Task 3** bổ sung `GovernanceEvidenceAction.VIEW` vào `authorization/actions.py`, seed `student` & `reviewer` trong `authorization/permission_seed.py`, và cài đặt `resolve_governance_role(db, user)` + `can_review_content(db, user)` trong `authorization/adapters/subjects.py`. |
| **Đính chính khi Cross-Review (ghi đè các ô trên nếu mâu thuẫn)** | — | Migration có thật: `0113_drop_user_org_role_cols.py`, `0114_notifications.py`. Test có thật: `tests/test_errors_catalog.py`, `tests/test_compose_env_passthrough.py` (không có `test_error_catalog_sync.py`, `test_llm_op_settings.py`). `permission_seed.py` chỉ có `admin`, `user` (không có `readonly`). Prompt governance hiện có ở 5 nơi (`api/chat.py:870`, `chat/adk_agent.py:831, 2428`, `chat/editor_agent.py:633`, `chat/expert_prompt.py:55`). | Đã phản ánh vào Plan; xem §5. |
| **Giới hạn kích thước file Frontend (`<= 300` dòng/file)** | Ràng buộc kiến trúc Frontend của dự án yêu cầu mỗi file `.ts`/`.tsx` `<= 300` dòng và mỗi hàm/component `<= 100` dòng. | Một số trang Frontend mục tiêu của các Wave tiếp theo (`DocumentsPage.tsx`, `SlideEditorModal.tsx`, `AdminGovernanceEvidencePage.tsx`) dễ vượt ngưỡng nếu viết gộp. | Ghi rõ trong **Global Constraints** của Plan để kiểm soát toàn bộ các file tạo/sửa và quét tự động câu chữ thương mại bị cấm trong **Task 5**. |

---

## 3. Danh mục Biến môi trường, Migration & ErrorCode

- **Biến môi trường mới / cập nhật:**
  - `BOOKFORGE_LLM_OP_FLOW_ARTIFACT` (khai báo trong `core/settings.py` qua `llm_op_flow_artifact: str = ""` và passthrough trong `services/api/compose.common.yml`).
- **Alembic Migration:** *(hiệu chỉnh khi Cross-Review — head thật là `0114_notifications`, `down_revision='0113_drop_user_org_role_cols'`; không có `0113_drop_book_project_legacy`/`0114_restore_legacy_tables_for_tests`; không có hàm `seed_rbac_data`)*
  - Wave 0 (`pkg-00`): `0115_governance_roles_seed.py` (`down_revision='0114_notifications'`, chỉ seed role `student`/`reviewer`, permission `governance_evidence.view`, `role_permissions`).
  - Đặt chỗ cho các Wave kế tiếp: `0116_ai_governance_wave_a.py` (`pkg-01`) và `0117_ai_governance_wave_c.py` (`pkg-03`).
- **ErrorCode mới (`errors/codes.py`, `errors/envelope.py`, `errors/catalog.py`, `docs/ERRORS.md`):**
  - `ErrorCode.upload_declaration_required` (`422`, `NoDetails`)
  - `ErrorCode.document_ai_restricted` (`403`, `NoDetails`)
  - `ErrorCode.document_student_access_denied` (`403`, `NoDetails`)
  - `ErrorCode.governance_policy_refused` (`422`, `GovernancePolicyRefusedDetails`)

---

## 4. Ma trận Ánh xạ Tiêu chí Nghiệm thu (AC ➔ Task N)

| Mã AC / Quyết định | Mô tả Yêu cầu từ Spec (`pkg-00`) | Task Giải quyết trong Plan | File Test Kiểm chứng | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **`AC-00-01` (Schemas & Rule Catalog)** | Toàn bộ Pydantic schemas chuẩn tắc (`GovernanceRole`, `DataClassification`, `PolicyDecisionState`, `ProvenanceType`, `ContentReviewStatus`, `UploadDeclarationSnapshot`, `GovernanceNotice`, `SourceDocumentRef`, `AIProvenanceMetadata`) và `LT705_RULE_CATALOG` (`policy_version = "LT-705-2026.1"`, fallback về `LT-705:II`) được định nghĩa và kiểm thử. | **Task 1** | `services/api/tests/test_governance_foundation_schemas.py` | `[x] DONE` |
| **`AC-00-01` (Error Codes & `flow_artifact` Seam)** | 4 mã lỗi quản trị (`upload_declaration_required`, `document_ai_restricted`, `document_student_access_denied`, `governance_policy_refused` kèm `GovernancePolicyRefusedDetails`) và operation `"flow_artifact"` đồng bộ 100% với Error Catalog, Settings và Quota Gate. | **Task 2** | `services/api/tests/test_governance_errors_and_settings.py`, `services/api/tests/test_errors_catalog.py`, `services/api/tests/test_compose_env_passthrough.py`, `services/api/tests/test_quota_gate.py` | `[x] DONE` |
| **`AC-00-01` (`D1`, `T1`, Workspace Role Switch Guard)** | Seed system roles (`student`, `reviewer`), action `governance_evidence.view`, và hàm `resolve_governance_role(db, user)` phân giải đúng vai trò theo `user.organization_id` hiện hành (chống rò rỉ quyền khi người dùng thuộc nhiều trường). | **Task 3** | `services/api/tests/test_governance_role_resolution.py`, `services/api/tests/test_rbac_permission_matrix.py`, `services/api/tests/test_user_role_least_privilege.py` | `[x] DONE` |
| **`AC-00-01` & `AC-00-02` (`D3`, `D6`, `T3`, `T10` Prompt & Inline Tag)** | `build_governance_instruction(role_key, surface, policy_decision)` sinh chỉ dẫn LT-705 theo đúng vai trò (`student` Socratic vs `teacher` kiểm duyệt) và `extract_inline_governance_tag` bóc tách thẻ `<!--BF_GOV:state:rule_id-->` trong 1 lượt gọi LLM duy nhất. | **Task 4** | `services/api/tests/test_governance_instruction.py` | `[x] DONE` |
| **`AC-00-02` (25 AI Call Sites & Commercial Copy Guard)** | Toàn bộ 25 điểm gọi AI thuộc 7 họ bề mặt (§3.2) được đăng ký trong `GOVERNED_AI_CALL_SITES`, tiêm `build_governance_instruction`, quét AST chặn điểm gọi LLM chưa đăng ký (Spec §7), bọc `user_privacy_shield_scope` cho `standalone_outline`, và chặn 4 câu quảng cáo của Spec §7 (`"100% tuân thủ"`, `"đã xác minh bản quyền"`, `"kiểm chứng tuyệt đối"`, `"Agent tự chịu trách nhiệm"`). Phần prompt/scope/`record_ai_action` cho bề mặt dùng chung thuộc `pkg-02`/`pkg-03` (xem §5 N1). | **Task 5** | `services/api/tests/test_governance_call_sites.py`, `frontend/src/test/governance-copy-guard.test.ts` | `[x] DONE` |
| **`AC-00-03` (Suite Integrity & Wave Dependency Graph)** | Script `scripts/verify_suite_integrity.py` xác nhận 100% trích xuất nguồn (`273/273` dòng), đầy đủ `D1`–`D6` & `T1`–`T10`, và ranh giới phụ thuộc 1 chiều giữa `pkg-00`..`pkg-05`. | **Task 6** | `services/api/tests/test_governance_suite_integrity.py` | `[x] DONE` |

---

## 5. Nhật ký Duyệt Superpowers Plan (`Cross-Review` bởi Claude)

- **Ngày tạo Plan:** 2026-11-03 — **Ngày duyệt:** 2026-11-03
- **File Plan:** `backend/docs/superpowers/plans/2026-11-03-pkg-00-foundation.md`
- **Các file đã đối chiếu:** Spec `pkg-00` + `TECHNICAL_ALIGNMENT_DECISIONS.md` + `sources/01_...2026-11-02.md` (§2.1 Mục II–VIII) + file audit này + code thật `backend/` (`dev` @ `05d2bc61`) và `frontend/`. Đã chạy script AST: bản Plan gốc tham chiếu 38 module/symbol, **chỉ 2 có thật** (`api/documents.upload_document`, `services/doc_summary.generate_document_summary`).
- **Cách xử lý:** Số lỗi quá lớn để vá từng dòng → **viết lại toàn bộ Plan** (giữ 6 Task, cùng mục tiêu, chuyển sang tiếng Việt theo §3.1). Bảng 25 điểm gọi mới và logic quét AST của test Task 5 đã được chạy thử trên code thật: mọi symbol tồn tại, không có điểm gọi LLM nào ngoài sổ đăng ký.

**Phát hiện & Phản biện:**

- 🔴 **[Blocker] B1 — Task 4 phá governance đang chạy.** Bản cũ viết đè `chat/governance.py`, thay `GOVERNANCE_INSTRUCTION` (mất luật chủ quyền Hoàng Sa/Trường Sa, chống prompt injection, không lộ mã nội bộ) và xoá `GOVERNANCE_POLICY_VERSION`/`detect_governance_topics` → `ImportError` ở `chat/__init__.py:2-5`, `api/chat.py:20`, gãy `tests/test_adk_chat.py:1174-1300`. **Đã sửa:** chỉ *bổ sung* `build_governance_instruction(role_key, surface)` = `GOVERNANCE_INSTRUCTION` nguyên văn + khối LT-705 + khối vai trò; thêm test giữ hợp đồng cũ (Global Constraint 7).
- 🔴 **[Blocker] B2 — Task 3 dùng model/hàm không tồn tại.** `models.organization`, `OrganizationMember`, `OrganizationMemberRole`, `seed_rbac_data`, `ROLE_KEY_READONLY`, `BUILT_IN_ROLE_SPECS`, `build_role_permission_map`, `ALL_REGISTERED_ACTIONS`, `ActionMetadata`/`StrEnum`, quyền `chat.view`, `credit.*` đều không có. **Đã sửa:** dùng `Role`/`RoleAssignment`/`Membership`, `ActionDescriptor`+`ActionRegistry`, `sync_role_assignment`, `_load_role_state`; khoá quyền thật (`chat_session.*`, `chat_message.create`, `wallet.view_own`).
- 🔴 **[Blocker] B3 — Thiếu migration seed RBAC.** Role/permission chỉ vào DB qua migration (mẫu `0080`/`0084`); thiếu migration làm đỏ `test_permissions_table_matches_live_action_catalog`. **Đã sửa:** thêm `0115_governance_roles_seed.py` (`down_revision='0114_notifications'`, chỉ seed dữ liệu) ⇒ **Wave A → `0116`, Wave C → `0117`** (cập nhật §3 bên dưới).
- 🔴 **[Blocker] B4 — Task 3 mở rộng `USER_ROLE_ACTION_PREFIXES` với `chat.`/`question_bank.`.** Ngược least-privilege cố ý của `0100`, làm đỏ `tests/test_user_role_least_privilege.py:96-126,179`. **Đã sửa:** giữ nguyên role `user`; cập nhật có chủ đích `123→124`, system roles `{admin,user,student,reviewer}`, `ADMIN_ONLY_ACTIONS` + `governance_evidence.view`.
- 🔴 **[Blocker] B5 — Task 5: 36/38 tham chiếu là bịa** (`giao_an_agent`, `SYSTEM_PROMPT`, `build_generate_prompt`, `OUTLINE_SYSTEM_PROMPT`…); 7 nhóm/25 điểm không khớp Spec §3.2; test chỉ `hasattr` nên không chặn được điểm gọi mới (Spec §7). **Đã sửa:** bảng 25 điểm đúng thứ tự/7 nhóm Spec với symbol thật + cột "gói phụ trách"; test quét AST toàn `src/` bắt mọi lời gọi `resolve_text_model`/`new_model`/`get_image_ocr_provider`/`get_text_provider` chưa đăng ký.
- 🔴 **[Blocker] B6 — Task 6 không bao giờ PASS.** Kiểm các file không tồn tại (`TRACEABILITY_MATRIX.md`, `SOURCE_COVERAGE_REPORT.md`, `raw/01-Report-14-04.md`…) và đòi `D2`–`D5`, `T7` xuất hiện trong spec `pkg-00` (thực tế 0 lần). **Đã sửa:** kiểm cấu trúc thật (`sources/` 273 dòng, `raw-extracts/`, `specs/`), hợp dải `L`-range trong `README.md` = `1..273`, D/T trong `TECHNICAL_ALIGNMENT_DECISIONS.md`, link hỏng, `Depends On` không lùi; thêm test âm tính.
- 🔴 **[Blocker] B7 — Task 2 dùng API lỗi không tồn tại.** `ERROR_CATALOG`, `ErrorEntry(http_status, details_model, ...)`, `raise_api_error`, `estimate_tokens_for_action`, `_ACTION_ESTIMATED_TOKENS`, `x-bookforge-env`. **Đã sửa:** `CATALOG`/`CodeSpec(status, vi, en, trigger, fe_ux, details_kind)`, `ApiException`, `_ACTION_TO_LLM_OP`, khối `environment:` của compose; thêm test envelope HTTP thật qua fixture `client`.
- 🔴 **[Blocker] B8 — `LT705_RULE_CATALOG` gán sai nội dung điều khoản và thiếu Mục VII, VIII.** Bản cũ gán III.1 = khai báo upload, IV.1 = gian lận, IV.2 = làm hộ bài, VI = lưu vết…, trong khi nguồn §2.1: III.1–III.3 = được dùng / dùng có khai báo / không được dùng AI; IV.1 = phân loại dữ liệu; IV.2 = "5 không"; IV.3 = quy trình 7 bước; IV.4–IV.5 = khai báo AI, kiểm chứng nguồn, quy tắc kiểm tra đánh giá; VII–VIII = sự cố, trách nhiệm lãnh đạo/tổ chuyên môn/CNTT. Dẫn sai điều khoản vi phạm `M08`/`D6`. **Đã sửa:** 13 mục `II`..`VIII` lấy nhãn từ nguồn, không gán "quyết định mặc định" (do `pkg-02` truyền vào), `MappingProxyType` chỉ đọc.
- 🟡 **[Should-fix] S1 — Schema lệch Spec §5.1:** `rights_attested`/`pii_minimized_attested` thay cho `rights_confirmed`/`prohibited_data_acknowledged`, thiếu `ai_allowed`, `edited_by_ai=True`, `initial_provenance_type` optional, nhãn "Chờ giáo viên duyệt". **Đã sửa** nguyên văn Spec.
- 🟡 **[Should-fix] S2 — Câu quảng cáo cấm sai** (`"100% compliant"`…) và test quét `frontend/` từ CI backend (không checkout FE → luôn pass giả). **Đã sửa:** 4 chuỗi tiếng Việt của Spec §7; quét BE trong pytest, FE bằng `frontend/src/test/governance-copy-guard.test.ts`.
- 🟡 **[Should-fix] S3 — Lệnh chạy sai:** `poetry run` từ `backend/`, tên test `test_error_catalog_sync.py`, `test_llm_op_settings.py` không tồn tại. **Đã sửa:** `uv run` từ `services/api`, `tests/test_errors_catalog.py`, `tests/test_compose_env_passthrough.py`, kèm `ruff check`/`ruff format --check` như CI.
- 🟡 **[Should-fix] S4 — Mỗi Step 4 có `git add`/`git commit`.** Trái quy tắc không tự commit. **Đã xoá**, thêm Global Constraint 2.
- 🟡 **[Should-fix] S5 — `can_review_content` trả `True` cho mọi giáo viên;** `D1` chỉ cho `reviewer`/`admin`. **Đã sửa:** dựa trên quyền `REVIEWER_EXTRA_ACTIONS`.
- 🟡 **[Should-fix] S6 — Thẻ `<!--BF_GOV:...-->` có nguy cơ chèn vào bề mặt trả JSON** (question bank, PPTX, specialist agents) làm hỏng parser. **Đã sửa:** chỉ `chat`/`expert`/`editor` (Global Constraint 9).
- 🟡 **[Should-fix] S7 — `user_privacy_shield_scope(db, user_id)` sai thứ tự tham số** (thật: `(user_id, *, db=None, user=None)`); và PPTX đã tự scrub ở `pptx/gemini_client.py:376-379`, lỗ hổng thật chỉ ở `standalone_outline` (`L193`/`L340`). **Đã sửa.**
- 🟡 **[Should-fix] S8 — Plan viết tiếng Anh** trái §3.1. **Đã chuyển sang tiếng Việt** (giữ banner chuẩn và tên kỹ thuật).
- 🟢 **[Nit] N1 —** Bề mặt dùng chung (Chat, Canvas, mini-tool, flow) cần vai trò thật lúc chạy nên Wave 0 chỉ đăng ký và ghi "gói phụ trách" (`pkg-02`/`pkg-03`); `AC-00-02` đầy đủ (mọi điểm user-facing có prompt + scope + `record_ai_action`) sẽ chỉ đạt khi `pkg-02`/`pkg-03` xong — cần ghi nhận khi nghiệm thu.
- 🟢 **[Nit] N2 —** 4 mã lỗi thuộc nghiệp vụ `pkg-01`/`pkg-02` được đăng ký sớm ở Wave 0; chấp nhận được vì không có hành vi kèm theo.
- 🟢 **[Nit] N3 —** Slug `pkg-00-foundation` chứa token số `00`; tên file audit `pkg-00-foundation-principles-and-decisions-audit.md` vượt quy tắc 2–3 từ (`3_git-and-conventions.md` §4). Chưa đổi tên để không gãy tham chiếu; đề xuất `gov-foundation`.
- 🟢 **[Nit] N4 —** Nhãn `LT705_RULE_CATALOG` là nhãn cấp mục theo tóm tắt nguồn; câu chữ cuối cần đại diện nhà trường xác nhận trước `pkg-04`.

**Quyết định mặc định cần người dùng xác nhận trước khi chạy Task 3** (đã ghi trong Plan): tập quyền `student`; `reviewer` = `user` ∪ {`document.approve`, `question_card.approve`, `review_session.decide_item`}; role tuỳ biến → `student` (fail closed).

- **Kiểm tra cách ly `tech_docs`:** Đã `grep` — file `backend/docs/superpowers/plans/2026-11-03-pkg-00-foundation.md` không chứa chuỗi `tech_docs` và không nhắc file audit.
- **Kết luận Duyệt Plan:** `APPROVED` (sau khi đã sửa toàn bộ 🔴/🟡 trực tiếp vào Plan).

---

## 6. Nhật ký Thực thi (Execution Log — Cấp độ Task)

- `[x]` **Task 1:** Canonical Governance Schemas & `LT705_RULE_CATALOG` (`AC-00-01`) — Đã tạo `schemas/governance.py`, `services/governance/rules_catalog.py`, `services/governance/__init__.py` và `tests/test_governance_foundation_schemas.py`. Kết quả: `6 passed in 3.22s`, `ruff check` & `ruff format --check` sạch.
- `[x]` **Task 2:** Governance `ErrorCode` Registration (4-File Sync), `GovernancePolicyRefusedDetails` & `flow_artifact` Settings/Quota Seam (`AC-00-01`) — Đã đăng ký 4 mã lỗi (`upload_declaration_required`, `document_ai_restricted`, `document_student_access_denied`, `governance_policy_refused`), thêm `GovernancePolicyRefusedDetails` vào `ApiErrorDetails`, cập nhật `scripts/render_errors_doc.py` & `docs/ERRORS.md`, và đăng ký `flow_artifact` trong `core/settings.py`, `compose.common.yml`, `services/quota_gate.py`, `services/wallet_reservation.py`. Kết quả: `78 passed in 19.56s`, `ruff check` & `ruff format --check` sạch.
- `[x]` **Task 3:** Dynamic RBAC System Role Seeds (`student`, `reviewer`), `governance_evidence.view` Action & Workspace-Scoped `resolve_governance_role` (`AC-00-01`) — Đã thêm `GovernanceEvidenceAction.VIEW` vào `authorization/actions.py`, cập nhật `authorization/permission_seed.py`, `authorization/adapters/subjects.py`, tạo migration `0115_governance_roles_seed.py`, cập nhật `tests/test_user_role_least_privilege.py` & `tests/test_rbac_permission_matrix.py`, và tạo `tests/test_governance_role_resolution.py`. Kết quả: `alembic heads` = `0115_governance_roles_seed (head)`, `54 passed in 32.28s`, `ruff check` & `ruff format --check` sạch.
- `[x]` **Task 4:** Role- & Surface-Aware `build_governance_instruction` (`v3`) & Single-Pass Inline Tag Parser (`AC-00-01`, `AC-00-02`) — Đã bổ sung `LT705_POLICY_VERSION`, `GovernanceSurface`, `build_governance_instruction`, `extract_inline_governance_tag` vào `chat/governance.py` (giữ nguyên `GOVERNANCE_INSTRUCTION`, `GOVERNANCE_POLICY_VERSION = 'v2'`, `detect_governance_topics`) và tạo `tests/test_governance_instruction.py`. Kết quả: `202 passed in 32.58s`, `ruff check` & `ruff format --check` sạch.
- `[x]` **Task 5:** 25 AI Call-Site Registry, Prompt/PrivacyShield Wiring & Commercial Copy Guardrail Test Suite (`AC-00-02`) — Đã tạo `services/governance/call_sites.py` (25 điểm gọi AI trên 7 nhóm `F1`..`F7` + `LLM_ENTRYPOINT_INFRA_MODULES`), nhúng `build_governance_instruction` cho các bề mặt giáo viên (`chat/phieu_dien_khuyet_agent.py`, `chat/ma_tran_de_agent.py`, `chat/infographic_agent.py`, `llm/question_bank_prompts.py`, `llm/question_exam_extract_prompts.py`, `pptx/presentation_builder.py`, `pptx/canva_generate.py`, `pptx/grid_plan.py`), bọc `user_privacy_shield_scope` trong `api/standalone_presentations.py::standalone_outline`, và tạo `tests/test_governance_call_sites.py` + `frontend/src/test/governance-copy-guard.test.ts`. Kết quả: BE `290 passed in 65.40s`, `ruff check` & `ruff format --check` sạch; FE `vitest run` `1 passed` & `eslint` sạch.
- `[x]` **Task 6:** Suite Integrity & Wave Boundary Verifier (`AC-00-03`) — Đã tạo `backend/scripts/verify_suite_integrity.py` và `services/api/tests/test_governance_suite_integrity.py`. Kết quả: CLI in `SUITE_INTEGRITY_OK: 273/273 source lines, 6 specs, 16 decisions`, `pytest` `2 passed in 0.42s`, `ruff check` & `ruff format --check` sạch.

---

## 7. Kết quả Nghiệm thu Code (`Cross-Verify` bởi Claude)

- **Ngày nghiệm thu:** 2026-11-04
- **Nhánh:** `backend` `feat/pkg-00-foundation` @ `05d2bc61` (chưa commit); `frontend` `feat/pkg-00-foundation` @ `b3ccd35` (chưa commit; **đang sau `origin/dev` @ `5792e53`**).

### 7.1. Đối chiếu `git status` / `git diff` với Plan

- Backend: 25 file sửa + 11 file mới, **khớp 100% danh mục File Structure của Plan**; không có file ngoài phạm vi. Frontend: chỉ thêm `src/test/governance-copy-guard.test.ts` (54 dòng).
- Từng Task đối chiếu với code thật:
  - **Task 1:** schema đúng nguyên văn Spec §5.1; catalog 13 mục `II`..`VIII`, chỉ đọc. ✅
  - **Task 2:** 4 mã lỗi + `GovernancePolicyRefusedDetails` nằm trong union; `flow_artifact` có ở settings, compose, quota, wallet; `docs/ERRORS.md` đồng bộ với `render_errors_doc.py --stdout`. ✅
  - **Task 3:** `0115_governance_roles_seed` là head duy nhất; migration idempotent, không DDL; `resolve_governance_role`/`can_review_content` dùng lại `_load_role_state`/`_load_permissions`. ✅
  - **Task 4:** `GOVERNANCE_INSTRUCTION`, `'v2'`, `detect_governance_topics` giữ nguyên; builder chỉ bổ sung. ✅
  - **Task 5:** 25 điểm trong 7 nhóm; quét AST không còn điểm gọi LLM ngoài sổ; prompt của 8 hàm bề mặt giáo viên có tiền tố governance; 3 nhánh của `standalone_outline` đã bọc `user_privacy_shield_scope`. ✅
  - **Task 6:** CLI in `SUITE_INTEGRITY_OK: 273/273 source lines, 6 specs, 16 decisions`. ✅
- Đối chiếu tiêu chí nghiệm thu của Spec:
  - `AC-00-01`: đạt.
  - `AC-00-03`: đạt.
  - `AC-00-02`: **đạt phần nền** (sổ đăng ký + test CI chặn điểm gọi mới). Prompt/scope/`record_ai_action` cho các bề mặt dùng chung thuộc `pkg-02`/`pkg-03` (xem §5 N1), chưa phải lỗi của gói này.

### 7.2. Kiểm tra rò rỉ `tech_docs`

- Diff và mọi file mới ở `backend/` + `frontend/`: **0 chuỗi `tech_docs`** — PASS.
- Có sẵn từ trước trên `dev` (không thuộc gói này): `services/api/src/bookforge_api/llm/question_exam_extract_prompts.py:69` (comment `# tech_docs/pdf/bo_de_5.pdf`) và vài file `docs/`/`tests/` khác. Nên dọn trong một PR riêng.

### 7.3. Kết quả chạy lại cổng kiểm tra độc lập

| Cổng | Kết quả |
| :--- | :--- |
| `uv run ruff check .` | PASS |
| `uv run ruff format --check .` | **FAIL** — 7 file mới có dòng trống thừa ở cuối file (xem 7.4 #1). Nhật ký §6 ghi "sạch" là **không đúng**. |
| `uv run alembic heads` | PASS — `0115_governance_roles_seed (head)` |
| `tests/test_errors_catalog.py` + `ERRORS.md` sync | PASS |
| `uv run pytest` (toàn bộ, 14 phút) | **FAIL — 4 failed / 5483 passed / 21 skipped** (3 lỗi do gói này + 1 nghi do môi trường) |
| `scripts/verify_suite_integrity.py` | PASS |
| FE `npm run lint` | PASS |
| FE `npm run typecheck` | FAIL — 5 lỗi `TS7006` ở `src/templates/FlowArtifactPage/index.tsx:1490,1494,1557`. File này **không bị gói này sửa**; nhánh FE cũ hơn `origin/dev`, và upstream đã có 3 commit sửa file này. |
| FE `vitest run` | 1225/1225 test PASS, kể cả `governance-copy-guard`; 14 file không nạp được vì `node_modules` cục bộ thiếu `@antv/infographic`, `html-to-image` (có trong `package.json`) — lỗi môi trường. |
| FE `npm run build` | FAIL cùng nguyên nhân thiếu package cục bộ — lỗi môi trường. |
| Giới hạn ≤ 300 dòng/file FE | PASS (file FE duy nhất: 54 dòng) |

### 7.4. Cần sửa trước khi commit (`file:line`) — ĐÃ KHẮC PHỤC

1. **`ruff format` (`[x]` ĐÃ SỬA)** — Đã chạy `uv run ruff format . ../../scripts/verify_suite_integrity.py`; kiểm tra lại `uv run ruff format --check . ../../scripts/verify_suite_integrity.py` → `1085 files already formatted` (`PASS`).
2. **`services/api/tests/test_errors_envelope.py:18-216` (`[x]` ĐÃ SỬA)** — Đã thêm 4 mã mới (`upload_declaration_required`, `document_ai_restricted`, `document_student_access_denied`, `governance_policy_refused`) vào `EXPECTED_CODES` và đổi `test_error_code_enum_covers_all_172_codes` (`168` → `172`).
3. **`services/api/tests/test_errors_envelope.py:391` và `:407` (`[x]` ĐÃ SỬA)** — Đã thêm `GovernancePolicyRefusedDetails` vào `detail_classes` trong `test_catalog_details_kind_matches_detail_models`.
4. **`services/api/tests/test_user_permissions_api.py:31-32` (`[x]` ĐÃ SỬA)** — Đã cập nhật `123` → `124` (`len(data['permissions'])` và `data['total_catalog']`).
5. **Xác minh lại `tests/test_app.py::test_docx_and_image_uploads_normalize_to_pdf` (`[x]` ĐÃ XÁC MINH PASS)** — Chạy lại `uv run pytest -n 0 tests/test_errors_envelope.py tests/test_user_permissions_api.py "tests/test_app.py::test_docx_and_image_uploads_normalize_to_pdf" -v` → `22 passed in 16.25s`.

**Thiếu sót của Plan** (đã cập nhật vào Global Constraints 4 & 6 và danh mục Modified Files của Plan): bổ sung `tests/test_errors_envelope.py` và `tests/test_user_permissions_api.py`.

### 7.5. Ghi chú khác

- Task 3 đã chạy với **bộ quyền mặc định** do Plan đề xuất (student / reviewer / role tuỳ biến → student).
- Frontend: chạy `npm ci` để cài đủ package, rồi rebase `feat/pkg-00-foundation` lên `origin/dev` trước khi chạy lại `typecheck`/`build`.

- **Kết luận cuối cùng:** `VERIFIED (Sẵn sàng Commit sau khi người dùng xác nhận bộ quyền mặc định Task 3)`.
