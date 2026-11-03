# Quy tắc Nghiệp vụ: Quét Spec (`specs/`) ➔ Lập `superpowers/plans/` ➔ Thi công Code

Tài liệu này quy định quy trình làm việc bắt buộc cho **Gemini** và **Claude** đối với mọi phân hệ hoặc tính năng lớn **đã có sẵn bộ đặc tả kỹ thuật (`specs/`)** trong repo (ví dụ: `backend/docs/product/<module>/specs/` hoặc tài liệu đặc tả tương đương).

---

## 1. Bản chất & Cấu trúc 2 File của Nghiệp vụ Spec-Driven

Khác với luồng tính năng nhỏ lẻ thông thường (dùng `tech_docs/plans/<slug>/01-analysis.md` và `02-plan.md`), ở nghiệp vụ Spec-Driven, bài toán sản phẩm và kiến trúc tổng thể đã được định nghĩa sẵn trong tài liệu Spec. Vì vậy, tuyệt đối **không** lặp lại việc viết `01-analysis.md` hay `02-plan.md`, mà sử dụng **cặp 2 tài liệu chuyên biệt**:

1. **Báo cáo Quét & Điều phối Nội bộ (`tech_docs/audits/<slug>-audit.md`):**
   - Nằm trong repo `tech_docs`.
   - Đóng vai trò là **hồ sơ kiểm toán & điều phối giữa Gemini và Claude**, chứa:
     - Kết quả quét đối chiếu giữa tài liệu `specs/` và code thật trên nhánh `dev` hiện tại (*Spec-to-Code Drift*).
     - Bảng ánh xạ 100% Tiêu chí Nghiệm thu (Acceptance Criteria) và Quyết định Kiến trúc trong Spec sang từng `Task N`.
     - Biên bản Duyệt Plan chéo (`Cross-Review`), Nhật ký Thực thi (`Execution Log`), và Biên bản Nghiệm thu Code (`Cross-Verify`).
2. **Kế hoạch Thi công Chuẩn Superpowers (`backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`):**
   - Nằm trực tiếp trong repo `backend`.
   - Tuân thủ 100% định dạng chuẩn của `backend/docs/superpowers/plans/` (chia thành từng `Task N` độc lập theo chu trình TDD 4 bước có checkbox `- [ ] Step 1..4`).
   - **Ràng buộc cách ly tuyệt đối:** Vì file này nằm trong repo `backend`, nội dung của nó **cấm tuyệt đối** chứa chuỗi `tech_docs` hoặc nhắc tới file `*-audit.md`.

---

## 2. Bước 1 — Quét Kiểm tra Spec đối chiếu với Code thật (`Spec-to-Code Audit`)

> **Nguyên tắc sống còn:** Tài liệu trong `specs/` được viết tại một thời điểm cố định, trong khi nhánh `dev` của `backend/` và `frontend/` liên tục có các PR mới hợp nhất vào. **Cấm tuyệt đối** dịch thẳng từ `specs/` sang `superpowers/plans/` khi chưa quét code thật.

Khi nhận lệnh quét một gói Spec, Agent phải mở code thật và kiểm tra đủ **7 hạng mục bắt buộc** sau đây để ghi vào `tech_docs/audits/<slug>-audit.md`:

### 2.1 Kiểm tra Số thứ tự & Chuỗi kế thừa Alembic Migration (`Alembic Drift`)
- Liệt kê các file mới nhất trong `backend/services/api/alembic/versions/`.
- Đối chiếu số hiệu revision mà Spec đề xuất với `head` thực tế trên nhánh `dev` (vì có thể một PR khác vừa chiếm mất số hiệu đó).
- Chốt chính xác tên file migration mới và giá trị `down_revision` thật sự.

### 2.2 Kiểm tra Tương thích SQLite Test & PostgreSQL (`DB Dialect Safety`)
- Toàn bộ bài test tích hợp trong `backend/services/api/tests/` chạy trên **SQLite** (`conftest.py`), trong khi môi trường chạy thật dùng **PostgreSQL**.
- Kiểm tra mọi câu lệnh DDL dự kiến trong Spec:
  - Không dùng `batch_alter_table` nếu không cần thiết (dễ gây lỗi hoặc treo trên SQLite).
  - Kiểm tra `server_default`, kiểu `JSON`, `Boolean`, và cách tạo/xoá index hoặc ràng buộc trên cả hai dialect.
  - Xác nhận cách cập nhật đồng bộ cả migration Alembic lẫn `db/models.py` (vì SQLite test thường khởi tạo bảng từ `Base.metadata`).

### 2.3 Kiểm tra Nghĩa vụ Đăng ký Mã lỗi (`ErrorCode` & `Error Catalog`)
- Nếu Spec bổ sung bất kỳ mã lỗi nào vào `ErrorCode` (trong `services/api/src/bookforge_api/errors/codes.py`), báo cáo Audit phải liệt kê rõ **4 file bắt buộc phải cập nhật đồng bộ** để không làm gãy `tests/test_errors_catalog.py`:
  1. `services/api/src/bookforge_api/errors/codes.py`
  2. `services/api/src/bookforge_api/errors/catalog.py`
  3. `services/api/scripts/render_errors_doc.py`
  4. `docs/ERRORS.md` (chạy script render để sinh lại)
- Đồng thời nhắc lại quy tắc: mọi router/service phải ném `AppError(ErrorCode.<code_mới>, ...)` thay vì `HTTPException` thô.

### 2.4 Kiểm tra Biến Môi trường & Docker Compose (`Env Passthrough`)
- Nếu Spec thêm cờ hoặc biến cấu hình mới vào `core/config.py` (`Settings`), kiểm tra xem biến đó có cần khai báo passthrough trong `compose.common.yml` để vượt qua bài test `tests/test_compose_env_passthrough.py` hay không.

### 2.5 Đối chiếu Chữ ký Hàm, Schema & Điểm chạm Thực tế (`file:line`)
- Mở từng file BE và FE được nêu trong Spec để xác minh:
  - File đó đã tồn tại hay là file tạo mới?
  - Tên hàm, tham số đầu vào, kiểu trả về, dependency injection (`Depends(...)`), và schema Pydantic hiện tại ở dòng nào (`file:line`)?
  - Có điểm gọi liên quan nào trong codebase bị Spec bỏ sót không?

### 2.6 Kiểm tra Giới hạn 300 dòng/file & 100 dòng/hàm ở Frontend (`FE Convention Gate`)
- Với mọi file trong `frontend/src/` dự kiến sửa đổi, đếm số dòng hiện tại của file đó.
- Nếu file đã gần hoặc vượt **300 dòng** (hoặc hàm gần **100 dòng** theo `frontend/CONVENTION.md`), báo cáo Audit phải chỉ định rõ phương án tách component/hook phụ vào thư mục `partial/` hoặc `partials/` cùng cấp ngay từ đầu.

### 2.7 Đối chiếu các Quyết định Kiến trúc & Ranh giới Bất biến của Bộ Spec
- Kiểm tra chéo với các tài liệu quyết định kỹ thuật hoặc nguyên tắc nền tảng đi kèm bộ Spec (ví dụ: `TECHNICAL_ALIGNMENT_DECISIONS.md`, các quy tắc bảo mật đa tổ chức, không giữ DB lock qua lời gọi mạng/LLM, hoặc các ranh giới giữ cho giai đoạn sau) để đảm bảo kế hoạch không phá vỡ bất biến kiến trúc.

---

## 3. Bước 2 & 3 — Lập và Duyệt chéo `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`

### 3.1 Quy tắc Lập Superpowers Plan (Agent 1)

Từ file Spec + Báo cáo `tech_docs/audits/<slug>-audit.md`, Agent 1 tạo file `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md` theo đúng khuôn mẫu tại [`2_superpowers-templates.md`](2_superpowers-templates.md) §2:

1. **Ngôn ngữ & Phong cách:**
   - Tiêu đề, mô tả kiến trúc và hướng dẫn các bước viết bằng **tiếng Việt** rõ ràng (giữ nguyên các thuật ngữ chuẩn ở phần Header Banner `> **For agentic workers:**...` và tên hàm/biến/file/lệnh CLI).
2. **Thứ tự Chia Task (`Task 1..N`) Không Vòng lặp Phụ thuộc:**
   - Mỗi `Task N` là một lát cắt dọc nhỏ, có thể viết test và kiểm chứng độc lập trong 15–30 phút:
     - **Nhóm 1 (Hạ tầng & DB BE):** Migration Alembic + `db/models.py` + `ErrorCode` catalog + `core/config.py`.
     - **Nhóm 2 (Core Policy / Service / Domain Logic BE):** Các hàm xử lý nghiệp vụ cốt lõi, phân quyền, kiểm tra điều kiện.
     - **Nhóm 3 (Routers / Workers / Exporters BE):** Gắn logic vào các API endpoint, background worker, hoặc luồng xuất file.
     - **Nhóm 4 (Frontend Types / API / Hooks):** Cập nhật kiểu dữ liệu `T*`, hàm `API*`, React Query hooks `useQuery*` / `useMutation*`.
     - **Nhóm 5 (Frontend UI Components & Pages):** Giao diện, hộp thoại, màn hình (đảm bảo ≤ 300 dòng/file).
     - **Nhóm 6 (E2E & Acceptance Tests):** Bộ bài test nghiệm thu toàn trình theo các tiêu chí của Spec.
3. **Cấu trúc Bắt buộc của Mỗi `Task N`:**
   - **`Files:`** Chỉ rõ `Create` / `Modify` / `Test` kèm đường dẫn tương đối chuẩn.
   - **`Interfaces:`** Nêu rõ chữ ký hàm/schema mà Task này sử dụng (`Consumes`) và tạo ra (`Produces`).
   - **Chu trình 4 bước TDD có ô tích `- [ ]`:**
     - `- [ ] **Step 1: Write failing test(s) in ...**` (Đưa sẵn khung code test cụ thể).
     - `- [ ] **Step 2: Run test to verify it fails**` (Đưa sẵn lệnh `uv run pytest ...` hoặc `npm test ...` chính xác).
     - `- [ ] **Step 3: Implement minimal code in ...**` (Mô tả chi tiết logic và đoạn code cốt lõi cần thêm/sửa).
     - `- [ ] **Step 4: Run test & linter to verify it passes**` (Đưa sẵn lệnh kiểm tra).
4. **Cập nhật Ma trận Ánh xạ:**
   - Sau khi viết xong Plan, điền đầy đủ bảng **Ma trận Ánh xạ Tiêu chí Nghiệm thu (`AC` ➔ `Task N`)** trong `tech_docs/audits/<slug>-audit.md` để chứng minh không sót bất kỳ yêu cầu nào của Spec.

### 3.2 Quy tắc Duyệt chéo Superpowers Plan (`Cross-Review` bởi Agent 2)

Agent 2 (người đối diện với Agent 1) thực hiện kiểm duyệt độc lập theo 5 tiêu chí:
1. **Độ phủ Spec & Quyết định Kiến trúc:** Có tiêu chí nghiệm thu hoặc ràng buộc kỹ thuật nào trong Spec bị bỏ quên hay hiểu sai trong các Task không?
2. **Độ chính xác với Code thật & Báo cáo Audit:** Các điểm lệch trong `tech_docs/audits/<slug>-audit.md` (số migration, `ErrorCode` catalog, chữ ký hàm, tách file FE ≤ 300 dòng) đã được đưa đầy đủ vào từng Task chưa?
3. **Tính khả thi của Test (Step 1 & Step 2):** Code test mẫu trong từng Task có dùng đúng fixture thật của dự án (như `db_session`, `client`, `auth_headers` trong `conftest.py`) không, hay đang gọi fixture tưởng tượng?
4. **Kiểm tra Cách ly `tech_docs`:** Quét toàn bộ file `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md` để chắc chắn **không xuất hiện chuỗi `tech_docs`**.
5. **Ghi biên bản & Chốt Plan:**
   - Ghi toàn bộ phát hiện (🔴 **Blocker** / 🟡 **Should-fix** / 🟢 **Nit**) vào mục `## 5. Nhật ký Duyệt Superpowers Plan` trong file `tech_docs/audits/<slug>-audit.md`.
   - Sửa trực tiếp các điểm 🔴 và 🟡 vào file `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md` và đổi trạng thái trong file Audit sang `APPROVED`.

---

## 4. Bước 4 & 5 — Thực thi theo từng Task (`Execute`) & Nghiệm thu chéo (`Cross-Verify`)

### 4.1 Kỷ luật khi Chạy Superpowers Plan (Agent Thực thi)

1. **Kiểm tra trước khi chạy:**
   - Kiểm tra nhánh git ở `backend/` và `frontend/` (tạo nhánh `feat/<slug>` nếu đang ở `dev`).
   - Kiểm tra trạng thái migration local (`uv run --directory backend/services/api alembic heads`).
2. **Tuân thủ nghiêm ngặt 4 bước TDD của từng `Task N`:**
   - Thực hiện tuần tự từ `Step 1` đến `Step 4` của từng Task.
   - Sau khi `Step 4` của một Task báo xanh, đánh dấu `- [x]` vào cả 4 Step của Task đó ngay trong `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`.
3. **Chạy Cổng Kiểm tra Cơ học (Mechanical Gates) cuối mỗi cụm Task:**
   - **Backend:**
     ```bash
     uv run --directory backend/services/api ruff check .
     uv run --directory backend/services/api ruff format --check .
     uv run --directory backend/services/api pytest services/api/tests/test_errors_catalog.py <các_file_test_của_task>
     ```
   - **Frontend:**
     - Chạy kiểm tra TypeScript / Vitest / Build trong `frontend/` và kiểm tra độ dài các file vừa chạm tới không vượt quá 300 dòng.
4. **Ghi Nhật ký Thực thi vào `tech_docs/audits/<slug>-audit.md`:**
   - Mọi ghi chú phát sinh, kết quả chạy lệnh test từng cụm Task đều ghi vào mục `## 6. Nhật ký Thực thi` của `tech_docs/audits/<slug>-audit.md` (giữ cho file trong `backend/docs/superpowers/plans/` chỉ cập nhật trạng thái checkbox `- [x]`).
5. **Không tự ý Commit / Push:** Giữ nguyên working tree để Agent đối diện nghiệm thu.

### 4.2 Kỷ luật khi Nghiệm thu Code chéo (Agent Duyệt)

1. Mở `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md` và `tech_docs/audits/<slug>-audit.md`.
2. Chạy `git status` và `git diff` trên cả `backend/` và `frontend/`:
   - Đối chiếu từng Task đã tick `[x]` với code thực tế trên working tree.
   - Kiểm tra xem có chuỗi `tech_docs` nào vô tình lọt vào `backend/` hoặc `frontend/` không.
   - Chạy lại độc lập toàn bộ lệnh linter và pytest/vitest của gói công việc.
3. Ghi kết quả vào mục `## 7. Kết quả Nghiệm thu Code` trong `tech_docs/audits/<slug>-audit.md`:
   - Nếu đạt 100%: Chốt trạng thái **`VERIFIED (Sẵn sàng Commit)`** và liệt kê ngắn gọn các bước kiểm tay trên giao diện cho người dùng.
   - Nếu còn lỗi: Chỉ rõ `file:line` để sửa dứt điểm trước khi commit.
