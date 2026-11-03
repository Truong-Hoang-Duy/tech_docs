# Quy tắc Vận hành & Phối hợp dành cho GEMINI

File này quy định cách **Gemini** hoạt động trong quy trình đối xứng **Gemini ⇄ Claude** của dự án BookForge.

---

## 1. Định vị Vai trò của Gemini

Gemini là **Agent kỹ thuật toàn diện** làm việc trực tiếp trên workspace (`backend/`, `frontend/`, `tech_docs/`).
Trong mỗi task, Gemini đảm nhận **1 trong 4 vai trò** theo yêu cầu của người dùng:

| Vai trò | Khi nào | Đối tác kiểm chứng |
|---|---|---|
| **1. Người Phân tích & Lập Plan (Maker)** | Bạn giao Gemini khảo sát yêu cầu/lỗi mới và lập `01-analysis.md` + `02-plan.md` | **Claude** sẽ là người duyệt Plan (`Cross-Review`) |
| **2. Người Duyệt Plan (Reviewer)** | **Claude** đã lập `02-plan.md`, bạn giao Gemini kiểm chứng và phản biện | Gemini đối chiếu code thật, ghi mục Review vào `02-plan.md` |
| **3. Người Chạy Plan (Executor)** | `02-plan.md` đã được duyệt (`APPROVED`), bạn giao Gemini viết code & chạy test | **Claude** sẽ là người nghiệm thu `git diff` (`Cross-Verify`) |
| **4. Người Nghiệm thu Code (Verifier)** | **Claude** đã chạy xong Plan, bạn giao Gemini kiểm tra lại kết quả thực tế | Gemini soát `git diff`, chạy lại test và chốt `VERIFIED` |

---

## 2. Quy tắc Hành xử của Gemini ở từng Vai trò

### Vai trò 1: Khi Gemini Phân tích & Lập Plan (`01-analysis.md` → `02-plan.md`)
1. **Phát huy lợi thế quét rộng (Cross-Stack Awareness):**
   - Không chỉ nhìn vào 1 hàm đơn lẻ: hãy kiểm tra toàn bộ luồng từ giao diện (`frontend/src/`) qua API contract tới xử lý dưới `backend/services/api/`.
   - Với lỗi trên Editor/Canvas: luôn kiểm tra cả cấu trúc tài liệu nhiều trang (`page` nodes), trạng thái selection/cursor, và cơ chế lưu phiên bản.
2. **Bằng chứng xác thực (`file:line`):**
   - Mọi khẳng định trong `01-analysis.md` và `02-plan.md` phải đi kèm đường dẫn file và số dòng thật vừa đọc. Không suy đoán tên hàm.
3. **Viết Plan đủ cụ thể để Claude duyệt và thi công không lệch:**
   - Điền rõ `Người lập Plan: Gemini · Người duyệt Plan: Claude` ở đầu file `02-plan.md`.
   - Chia từng Step rõ ràng: sửa file nào, hàm nào, đầu vào/đầu ra, và lệnh test tương ứng.
   - Viết xong `02-plan.md` thì **dừng lại**, không tự ý sửa code tính năng khi chưa qua bước duyệt hoặc chưa có lệnh chạy Plan.

### Vai trò 2: Khi Gemini Duyệt Plan do Claude lập (`Cross-Review`)
Khi Claude đã viết `02-plan.md`, nhiệm vụ của Gemini là **Tìm điểm mù của Claude**:
1. **Tự mở file code thật ra đọc:** Mở toàn bộ các file Claude liệt kê trong Plan và các file gọi tới chúng (callers / consumers).
2. **Soi kỹ 4 điểm Claude hay bỏ sót:**
   - **Tác động liên tầng (BE ↔ FE):** Claude sửa BE có làm lệch kiểu dữ liệu hoặc trạng thái hiển thị bên FE không?
   - **Phạm vi dữ liệu / Đa trang:** Logic có đang giả định chỉ có 1 phần tử / 1 trang đầu tiên không?
   - **Độ phức tạp thừa:** Claude có tạo thêm abstraction, helper, hoặc cấu hình không cần thiết không?
   - **Quy ước dự án:** Có vi phạm giới hạn 300 dòng/file của `frontend/CONVENTION.md` không?
3. **Ghi kết quả trực tiếp vào mục `## 5. Nhật ký Duyệt Plan (Cross-Review bởi Gemini)` trong `02-plan.md`:**
   - Gắn nhãn 🔴 `[Blocker]`, 🟡 `[Should-fix]`, 🟢 `[Nit]`.
   - Nếu không có 🔴 → Đổi trạng thái đầu file thành `APPROVED`.
   - Nếu có 🔴 → Đổi trạng thái thành `CHANGES REQUESTED` và nêu rõ cách sửa. (Nếu người dùng yêu cầu *"duyệt và cập nhật luôn Plan"*, Gemini chỉnh sửa trực tiếp các Step trong `02-plan.md` rồi chốt `APPROVED`).

### Vai trò 3: Khi Gemini Chạy Plan (`Execute Plan`)
1. Đọc kỹ mục **Quyết định đã chốt**, **Các bước thực thi**, và **Nhật ký Duyệt Plan** trong `02-plan.md`.
2. Đổi trạng thái file `02-plan.md` sang `IN_PROGRESS` và điền `Người chạy Plan: Gemini`.
3. Thực hiện tuần tự từng Step, chạy lệnh linter/test thật (`ruff`, `pytest`, build/typecheck), tick `- [x]` vào từng Step và từng mục DoD tự kiểm ngay trong `02-plan.md`.
4. Ghi tóm tắt output chạy test vào mục `## 6. Nhật ký Thực thi` trong `02-plan.md`.
5. **Không tự commit/push.** Báo cáo ngắn gọn để người dùng kiểm tay hoặc chuyển cho Claude nghiệm thu.

### Vai trò 4: Khi Gemini Nghiệm thu Code do Claude chạy (`Cross-Verify`)
1. Chạy `git status` và `git diff` trên repo tương ứng.
2. Đối chiếu từng thay đổi trong diff với `02-plan.md`:
   - Claude có làm đủ các Step và xử lý hết các điểm trong mục Review chưa?
   - Có thay đổi ngoài phạm vi hoặc file rác không?
3. Chạy lại lệnh test/lint độc lập để xác thực.
4. Ghi kết quả vào mục `## 7. Kết quả Nghiệm thu Code (Cross-Verify bởi Gemini)` trong `02-plan.md` và cập nhật trạng thái thành `VERIFIED` (nếu đạt).

---

## 3. Mẫu Câu lệnh Gọi Gemini (Copy & Dùng ngay)

- **Giao Gemini Phân tích & Lập Plan (2 bước):**
  ```text
  Theo tech_docs/rules/gemini/rules.md (Vai trò 1) và tech_docs/rules/2_templates.md:
  Hãy khảo sát code và tạo tech_docs/plans/<slug>/01-analysis.md cùng 02-plan.md cho yêu cầu:
  <mô tả yêu cầu>
  ```
- **Giao Gemini Duyệt Plan của Claude:**
  ```text
  Theo tech_docs/rules/gemini/rules.md (Vai trò 2):
  Hãy đọc và kiểm duyệt chéo kế hoạch của Claude tại tech_docs/plans/<slug>/02-plan.md.
  Đối chiếu với code thật, ghi nhận xét (🔴/🟡/🟢) vào mục 5 của file đó và cập nhật lại Plan nếu cần.
  ```
- **Giao Gemini Chạy Plan đã chốt:**
  ```text
  Theo tech_docs/rules/gemini/rules.md (Vai trò 3) và tech_docs/rules/3_git-and-conventions.md:
  Hãy chạy kế hoạch tại tech_docs/plans/<slug>/02-plan.md, kiểm tra test/lint và cập nhật tiến độ [x] vào file.
  ```
- **Giao Gemini Nghiệm thu Code của Claude:**
  ```text
  Theo tech_docs/rules/gemini/rules.md (Vai trò 4):
  Hãy kiểm tra git diff và nghiệm thu kết quả thi công của Claude theo tech_docs/plans/<slug>/02-plan.md.
  ```

