# Quy tắc Git, Quy ước Code & Tài liệu Dự án

Tài liệu này áp dụng bắt buộc cho cả **Gemini** và **Claude** khi thao tác trên hai repo `backend/` (`bookforge`) và `frontend/` (`bookforge-fe`).

---

## 1. Quy tắc Thao tác Git

1. **Không tự ý Commit / Push / Đổi nhánh:**
   - Cả Gemini và Claude **tuyệt đối không** tự chạy `git commit` hay `git push` khi người dùng chưa yêu cầu rõ ràng (VD: *"commit đi"*, *"commit và push"*).
   - Giữ thay đổi trên working tree để người dùng hoặc Agent đối diện thực hiện bước **Nghiệm thu Code chéo (Cross-Verify)**.
2. **Quy tắc Nhánh (Branch):**
   - Không code trực tiếp trên nhánh `dev`. Nếu đang ở `dev`, tạo nhánh mới có tên ngắn gọn theo tính năng (`feat/<slug>` hoặc `fix/<slug>`).
   - Nếu task đụng cả hai repo (`backend/` và `frontend/`), đặt **cùng một tên nhánh** ở cả hai bên.
   - Khi merge vào `dev`: ưu tiên `git merge --no-ff <branch>` và **giữ nguyên nhánh sau khi merge** (không chạy `git branch -d`).
3. **Quy tắc Commit Message:**
   - Ngôn ngữ: **Tiếng Anh**, ngắn gọn, trực diện.
   - Định dạng bắt buộc: `<type>(<scope>): <mô tả việc đã làm>`
     - `<type>`: `feat` | `fix` | `docs` | `test` | `refactor` | `merge`.
     - `<scope>`: tên module/khu vực bị thay đổi (VD: `api`, `chat`, `question-bank`, `editor`, `canvas`, `auth`, `ops`).
   - Trước khi commit, chạy `git log --oneline -10` trong repo đó để chọn `scope` nhất quán với lịch sử.
   - **Cấm tuyệt đối:** Không thêm dòng `Co-Authored-By`, không gắn watermark/attribution của AI (Claude, Gemini, Antigravity...) vào commit message hoặc mô tả PR.
4. **Quy trình 5 bước khi được lệnh Commit:**
   - **Bước 1:** Kiểm tra `02-plan.md` xem các mục DoD tự động đã `[x]` và kết luận nghiệm thu đã đạt chưa.
   - **Bước 2:** Chạy `git status` và `git diff` để rà soát phạm vi. Chỉ `git add` từng file thuộc phạm vi Plan (không `git add -A` mù quáng).
   - **Bước 3:** Nếu có file `.md` nằm trong `backend/` hoặc `frontend/`, kiểm tra chắc chắn không chứa chuỗi `tech_docs` (§3).
   - **Bước 4:** Tạo commit theo đúng chuẩn mục 1.3.
   - **Bước 5:** Chỉ `git push` khi có lệnh yêu cầu push rõ ràng.

---

## 2. Quy ước Code & Kiểm tra Kỹ thuật (BE & FE)

### 2.1 Backend (`backend/` — Repo `bookforge`)
- **Công cụ điều hướng:** Ưu tiên dùng Serena MCP (`find_symbol`, `find_referencing_symbols`, ...) hoặc công cụ tìm kiếm chính xác theo biểu tượng khi truy vết hàm/class.
- **Ràng buộc kiến trúc bắt buộc:**
  - **Không giữ DB Lock qua lời gọi LLM / HTTP ngoài:** Không mở transaction giữ row lock trong lúc chờ kết quả từ OpenAI/Gemini/Gotenberg/RAG.
  - **Phân quyền & Đa tổ chức (Multi-tenant):** Mọi truy vấn và endpoint mới phải kiểm tra `organization_id` / quyền truy cập tài liệu và feature flag liên quan (`feature_enabled`).
  - **Mã lỗi & Hợp đồng:** Tuân thủ hệ thống `ErrorCode` hiện hữu, không tự chế format lỗi ngoài chuẩn của `register_error_handlers`.
- **Kiểm tra Migration DB Local (Chạy trước khi thi công/test BE):**
  ```bash
  uv run --directory backend/services/api alembic current
  uv run --directory backend/services/api alembic heads
  ```
  Nếu `current` lệch `heads` trên SQLite local (`storage/bookforge.db`), sao lưu file DB trước khi chạy `alembic upgrade head`.
- **Lệnh kiểm tra bắt buộc (Mechanical Gates):**
  ```bash
  uv run --directory backend/services/api ruff check .
  uv run --directory backend/services/api ruff format --check .
  uv run --directory backend/services/api pytest <đường_dẫn_test_liên_quan>
  ```

### 2.2 Frontend (`frontend/` — Repo `bookforge-fe`)
- **Tuân thủ nghiêm ngặt `frontend/CONVENTION.md`:**
  - **Giới hạn kích thước:** Tối đa **300 dòng / file**, **100 dòng / function**. Nếu vượt quá, tách các thành phần phụ vào thư mục `partial/` hoặc `partials/` cùng cấp.
  - **Quy tắc đặt tên:**
    - Tên file: `kebab-case.ts` / `kebab-case.tsx` (trừ thư mục Component dùng `PascalCase/index.tsx`).
    - Type / Interface: Tiền tố `T` (VD: `TDocumentItem`).
    - Hàm gọi API: Tiền tố `API` (VD: `APIGetDocument`).
    - React Query Hook: Tiền tố `useQuery` / `useMutation`.
- **Lưu ý đặc thù với TiptapEditor / Canvas:**
  - Tài liệu trên Canvas có thể ở chế độ **phân trang nhiều trang (`page` nodes)** hoặc **tài liệu phẳng**. Mọi logic duyệt khối (block traversal, decoration, scroll/jump) phải duyệt đệ quy hoặc qua toàn bộ các node `page`, **không bao giờ giả định chỉ có `doc.child(0)` (Trang 1)**.

---

## 3. Ràng buộc Cách ly `tech_docs/` (Hard Constraint)

`backend/`, `frontend/`, và `tech_docs/` là **ba thư mục/repo độc lập**. Người nhận code trên `backend` hoặc `frontend` không có thư mục `tech_docs/`.

- **Cấm tuyệt đối trong mọi file thuộc `backend/` và `frontend/`:**
  - Không chứa đường dẫn `tech_docs/...` hoặc `../tech_docs/...`.
  - Không nhắc tên các file nội bộ của quy trình như `01-analysis.md`, `02-plan.md`.
  - Khi cần xuất tài liệu sang `backend/docs/tasks/` hoặc `backend/handoff/frontend/`, phải **chép toàn bộ nội dung kỹ thuật cần thiết vào trong file đó** để tài liệu tự đứng độc lập.
- **Chiều ngược lại được phép:** Các file trong `tech_docs/plans/` và `tech_docs/rules/` được trỏ thẳng tới mọi đường dẫn trong `backend/` và `frontend/`.

