# Quy trình Tối ưu: Phân tích → Lập & Duyệt Plan → Chạy Plan

Quy trình này được thiết kế để loại bỏ mọi bước giấy tờ rườm rà, tập trung vào **chứng cứ code thật (`file:line`)** và **kiểm duyệt chéo 2 chiều giữa Gemini và Claude**.

---

## 1. Nguyên tắc Vàng

1. **Kéo mã nguồn mới nhất trước khi chạy Bước 1:** Trước khi bắt đầu Bước 1 (hoặc ngay đầu Bước 1), bắt buộc phải kéo mã nguồn mới nhất từ nhánh chính (`main` / `dev`) của `backend/`, `frontend/`, và `tech_docs/` về local. Tuyệt đối không khảo sát hay lập Plan trên code cũ.
2. **Đọc code thật ngay từ bước đầu:** Không viết tài liệu phỏng đoán khi chưa mở code. Mọi nhận định về hiện trạng hoặc nguyên nhân lỗi phải kèm `file:line`.
3. **Đảo vai Kiểm duyệt (Maker ⇄ Reviewer):**
   - **Gemini lập Plan** → **Claude duyệt Plan** (hoặc ngược lại).
   - **Claude chạy Plan** → **Gemini nghiệm thu Code** (hoặc ngược lại).
4. **Tối giản số lượng file (Tối đa 2 file / tính năng):**
   - Toàn bộ quá trình của một task nằm trong `tech_docs/plans/<slug>/` với tối đa 2 file: `01-analysis.md` và `02-plan.md`.
   - **`02-plan.md` là nguồn sự thật duy nhất (Single Source of Truth):** Chứa cả kế hoạch, ý kiến duyệt chéo, trạng thái tiến độ (`- [x]`), quyết định phát sinh, và kết quả nghiệm thu. Không tạo thêm `status.md`, `qa.md`, `00-desc.md`, hay `01-brief.md` rời rạc.

---

## 2. Bước 1 — Kéo Code Mới Nhất, Phân tích & Khảo sát (`01-analysis.md`)

### 2.0 Thao tác bắt buộc trước / ngay đầu Bước 1: Đồng bộ mã nguồn mới nhất
Trước khi mở file khảo sát ở Bước 1, Agent A bắt buộc thực hiện:
- Kiểm tra `git status` và kéo mã nguồn mới nhất từ nhánh chính trên remote về máy local cho cả 3 thư mục:
  - `tech_docs/`: `git pull origin main`
  - `backend/` và `frontend/`: cập nhật nhánh chính mới nhất (`git checkout main && git pull origin main` hoặc `git checkout dev && git pull origin dev` tuỳ nhánh tích hợp chính của repo).
- Nếu working tree đang có thay đổi dở dang gây xung đột khi pull, dừng lại báo ngay cho người dùng trước khi làm tiếp.

### 2.1 Chế độ Chuẩn (Dành cho tính năng mới hoặc bug phức tạp, đụng nhiều file / cả BE + FE)

1. **Đầu vào:** Bạn nêu yêu cầu hoặc mô tả lỗi bằng lời thường.
2. **Thực hiện (Agent A — Gemini hoặc Claude):**
   - Thực hiện mục **2.0 (Kéo mã nguồn mới nhất về local)**.
   - Tự đặt `<slug>` **chỉ 2–3 từ tiếng Anh** (`kebab-case`, ví dụ: `canvas-page-scroll`, `export-exam-docx`), tuân thủ [`3_git-and-conventions.md`](3_git-and-conventions.md) §4.
   - Mở repo (`backend/` và/hoặc `frontend/`) để truy vết luồng chạy thực tế.
   - Ghi kết quả vào `tech_docs/plans/<slug>/01-analysis.md` theo khuôn mẫu tại [`2_templates.md`](2_templates.md) §1:
     - **Mục tiêu & Phạm vi:** Phía tác động (`BE` / `FE` / `Cả hai`), phạm vi làm và không làm.
     - **Hiện trạng & Nguyên nhân gốc:** Luồng thực tế kèm `file:line` và đoạn trích code ngắn (≤ 15 dòng).
     - **Ràng buộc & Điểm va chạm:** DB schema/migration, hợp đồng API BE↔FE, feature flags, giới hạn file FE (`CONVENTION.md`).
     - **Phương án giải quyết:** Nếu có nhiều cách làm, nêu ngắn gọn 2 phương án kèm đánh đổi thực tế (hiệu năng, độ phức tạp, rủi ro) và **khuyến nghị 1 phương án**. Nếu cách giải quyết đã rõ ràng, trình bày thẳng phương án tối ưu.
   - **Dừng lại** để bạn xem hoặc chuyển sang Bước 2.

### 2.2 Chế độ Gọn — Fast-Track (Dành cho task nhỏ, bug đã rõ vị trí, sửa ≤ 3 file)

- **Bỏ qua `01-analysis.md`, nhưng vẫn bắt buộc chạy mục 2.0 (Kéo mã nguồn mới nhất về local) trước tiên.**
- Agent A khảo sát code vừa cập nhật và viết thẳng vào `tech_docs/plans/<slug>/02-plan.md` (gộp mục *Hiện trạng & Nguyên nhân gốc* lên đầu file `02-plan.md`), sau đó chuyển thẳng sang bước Duyệt Plan (Mục 3.2).

---

## 3. Bước 2 — Lập Plan & Duyệt chéo (`02-plan.md`)

### 3.1 Lập Plan (Agent A)

Từ `01-analysis.md` (và các chốt của bạn nếu có), Agent A tạo file `tech_docs/plans/<slug>/02-plan.md` theo khuôn mẫu tại [`2_templates.md`](2_templates.md) §2, đảm bảo:
- **Quyết định đã chốt:** Các nguyên tắc kỹ thuật không được tự ý thay đổi khi code.
- **Bảng cấu trúc file:** Liệt kê chính xác mọi file sẽ `Tạo mới` / `Sửa` / `Xoá` ở `backend/` và `frontend/`.
- **Các bước thực thi (Steps):** Chia nhỏ theo thứ tự hợp lý (thường là: *DB/Model → Service/API BE → Test BE → API/Hook FE → UI Component FE*). Mỗi Step chỉ rõ file, hàm, kiểu dữ liệu, và logic cần thay đổi.
- **Tiêu chí nghiệm thu (DoD):**
  - Mục tự kiểm bằng lệnh (`pytest`, `ruff`, `npm run build` / `tsc`).
  - Mục `(kiểm tay)` cho thao tác trên giao diện.

### 3.2 Duyệt Plan chéo (Agent B — Đối diện với Agent A)

> - Nếu **Gemini** viết `02-plan.md` → Gọi **Claude** vào duyệt.
> - Nếu **Claude** viết `02-plan.md` → Gọi **Gemini** vào duyệt.

**Quy trình bắt buộc của Agent B khi duyệt Plan:**
1. **Không tin mù quáng vào tài liệu của Agent A:** Agent B bắt buộc phải mở các file thật trong `backend/` và `frontend/` được nhắc tới trong Plan (và các file gọi tới chúng) để kiểm chứng.
2. **Soát theo 4 lăng kính kiểm duyệt:**
   - **Lăng kính 1 — Sự thật Code (`file:line`):** Tên file, hàm, dòng code, kiểu dữ liệu mà Agent A dẫn ra có khớp với code hiện tại không?
   - **Lăng kính 2 — Rủi ro & Tác động dây chuyền:**
     - Có bỏ sót trường hợp biên không? *(VD: Editor nhiều trang thay vì 1 trang, dữ liệu rỗng, quyền truy cập org, giữ DB lock khi gọi LLM, quên migration Alembic)*.
     - Thay đổi ở BE có làm gãy FE hiện tại không (và ngược lại)?
   - **Lăng kính 3 — Tối giản & Đúng chuẩn (Anti Over-engineering):**
     - Giải pháp có bị phức tạp hoá, đẻ thêm hàm/class/config thừa không?
     - Có vi phạm [`3_git-and-conventions.md`](3_git-and-conventions.md) không (độ dài file FE ≤ 300 dòng, hàm ≤ 100 dòng, chuẩn mã lỗi BE)?
   - **Lăng kính 4 — Độ phủ DoD:** Các lệnh test trong DoD có chạy được thật và kiểm tra trúng lỗi/tính năng không?
3. **Ghi kết quả vào mục `## 6. Nhật ký Duyệt Plan (Cross-Review)` trong `02-plan.md`:**
   - Phân loại từng điểm phát hiện theo mức độ:
     - 🔴 **Blocker:** Sai sự thật code, lỗi logic, gây regression, thiếu bảo mật/migration. **Bắt buộc sửa Plan trước khi code.**
     - 🟡 **Should-fix:** Cách làm chưa gọn, thiếu edge-case phụ, hoặc thiếu test quan trọng.
     - 🟢 **Nit / Gợi ý nhỏ:** Đặt tên, làm rõ câu chữ.
   - Đưa ra kết luận: **`APPROVED (Sẵn sàng chạy Plan)`** hoặc **`CHANGES REQUESTED (Cần cập nhật Plan)`**.
4. **Cập nhật chốt Plan:** Nếu có điểm 🔴 hoặc 🟡 hợp lý, cập nhật trực tiếp vào các mục trên của `02-plan.md` để có bản kế hoạch hoàn chỉnh trước khi thi công.

---

## 4. Bước 3 — Chạy Plan & Nghiệm thu chéo

### 4.1 Chạy Plan (Agent Thực thi — Gemini hoặc Claude)

Bạn có thể giao việc chạy Plan cho chính Agent vừa lập/sửa Plan, hoặc giao cho Agent phù hợp hơn với loại tác vụ (xem gợi ý tại [`gemini/rules.md`](gemini/rules.md) và [`claude/rules.md`](claude/rules.md)).

**6 Luật kỷ luật khi Chạy Plan:**
1. **Kiểm tra môi trường trước khi sửa code:**
   - Nếu chạm `backend/`: Kiểm tra trạng thái nhánh git và DB migration local (`uv run --directory backend/services/api alembic current` vs `heads`).
2. **Làm đúng phạm vi hợp đồng `02-plan.md`:** Không tự ý refactor ngoài lề, không thêm tính năng ngoài Plan, không đổi "Quyết định đã chốt".
3. **Thực tế khác Plan → Dừng và báo:** Nếu khi đang sửa phát hiện xung đột không lường trước, dừng lại, cập nhật vào mục *Quyết định phát sinh* trong `02-plan.md` và hỏi ý kiến nếu làm đổi hướng thiết kế.
4. **Thực thi và kiểm tra từng bước:**
   - Hoàn thành Step nào → tick `- [x]` vào Step đó trong `02-plan.md`.
   - Nếu task đụng cả BE và FE → hoàn tất và chạy pass test phần BE trước, sau đó mới làm phần FE.
5. **Chạy cổng kiểm tra tự động (Mechanical Gates):**
   - **Backend:**
     - `uv run --directory backend/services/api ruff check .`
     - `uv run --directory backend/services/api ruff format --check .`
     - `uv run --directory backend/services/api pytest <đường_dẫn_test>`
   - **Frontend:**
     - Chạy kiểm tra TypeScript / build hoặc test tương ứng trong `frontend/`.
   - Chỉ tick `- [x]` vào mục DoD tự kiểm sau khi lệnh chạy thực tế báo xanh.
6. **Không tự ý `git commit` hay `git push`:** Giữ nguyên thay đổi trên working tree để phục vụ bước Nghiệm thu chéo và chờ lệnh commit từ bạn.

### 4.2 Nghiệm thu Code chéo (Agent Duyệt — Đối diện với Agent Thực thi)

Sau khi Agent Thực thi báo đã chạy xong Plan:
1. Agent Duyệt mở `02-plan.md` và chạy `git status` + `git diff` trên repo (`backend/` và/hoặc `frontend/`).
2. Kiểm tra:
   - Mọi Step và quyết định trong `02-plan.md` đã được hiện thực hoá chính xác chưa?
   - Có file rác, log thừa, hay thay đổi ngoài phạm vi lọt vào diff không?
   - Chạy lại các lệnh kiểm tra (`ruff`, `pytest`, build/typecheck) để xác thực độc lập.
   - Soát lỗi tiềm ẩn trong code mới viết.
3. Ghi kết quả vào mục `## 8. Kết quả Nghiệm thu Code` ở cuối `02-plan.md`:
   - Nếu đạt toàn bộ → Kết luận **`VERIFIED (Sẵn sàng Commit)`** và hướng dẫn ngắn gọn các bước `(kiểm tay)` trên giao diện cho bạn (nếu có).
   - Nếu còn lỗi 🔴 → Chỉ rõ `file:line` và cách sửa để xử lý dứt điểm.

---

## 5. Khi nào cần xuất sang `backend/docs/tasks/`?

Mặc định, toàn bộ quá trình làm việc hằng ngày chỉ cần nằm gọn trong `tech_docs/plans/<slug>/02-plan.md`.
Chỉ khi bạn muốn **lưu lại đặc tả công việc vào lịch sử Git của repo `backend`**, hãy yêu cầu Agent xuất `02-plan.md` thành `backend/docs/tasks/YYYY-MM-DD-<slug>.md` (theo mẫu tại [`2_templates.md`](2_templates.md) §3 và tuân thủ quy tắc không nhắc tới `tech_docs` tại [`3_git-and-conventions.md`](3_git-and-conventions.md) §3).

