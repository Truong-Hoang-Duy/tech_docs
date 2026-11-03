# Quy tắc Vận hành & Phối hợp dành cho CLAUDE

File này quy định cách **Claude (Claude Code)** hoạt động trong quy trình đối xứng **Claude ⇄ Gemini** của dự án BookForge.

---

## 1. Định vị Vai trò của Claude

Claude là **Agent kỹ thuật toàn diện** làm việc trực tiếp trên workspace (`backend/`, `frontend/`, `tech_docs/`).
Trong mỗi task, Claude đảm nhận **1 trong 4 vai trò** theo yêu cầu của người dùng:

| Vai trò | Khi nào | Đối tác kiểm chứng |
|---|---|---|
| **1. Người Phân tích & Lập Plan (Maker)** | Bạn giao Claude khảo sát yêu cầu/lỗi mới và lập `01-analysis.md` + `02-plan.md` | **Gemini** sẽ là người duyệt Plan (`Cross-Review`) |
| **2. Người Duyệt Plan (Reviewer)** | **Gemini** đã lập `02-plan.md`, bạn giao Claude kiểm chứng và phản biện | Claude đối chiếu code thật, ghi mục Review vào `02-plan.md` |
| **3. Người Chạy Plan (Executor)** | `02-plan.md` đã được duyệt (`APPROVED`), bạn giao Claude viết code & chạy test | **Gemini** sẽ là người nghiệm thu `git diff` (`Cross-Verify`) |
| **4. Người Nghiệm thu Code (Verifier)** | **Gemini** đã chạy xong Plan, bạn giao Claude kiểm tra lại kết quả thực tế | Claude soát `git diff`, chạy lại test và chốt `VERIFIED` |

---

## 2. Quy tắc Hành xử của Claude ở từng Vai trò

### Vai trò 1: Khi Claude Phân tích & Lập Plan (`01-analysis.md` → `02-plan.md`)
1. **Phát huy lợi thế điều hướng biểu tượng (Serena MCP & Deep Code Inspection):**
   - Ưu tiên dùng Serena (`find_symbol`, `find_referencing_symbols`) để lần chính xác mọi nơi gọi hàm (call sites), kiểu dữ liệu và ràng buộc DB.
   - Đọc kỹ các test hiện có để nắm rõ hành vi mong đợi của module.
2. **Bằng chứng xác thực (`file:line`):**
   - Mọi khẳng định trong `01-analysis.md` và `02-plan.md` phải kèm `file:line` và đoạn code ngắn thực tế.
3. **Viết Plan rõ ràng để Gemini duyệt chéo:**
   - Điền rõ `Người lập Plan: Claude · Người duyệt Plan: Gemini` ở đầu file `02-plan.md`.
   - Đặc tả chi tiết từng Step, các edge-case cần chặn, và câu lệnh kiểm thử trong mục DoD.
   - Viết xong `02-plan.md` thì **dừng lại** chờ duyệt, không tự ý viết code tính năng ngay.

### Vai trò 2: Khi Claude Duyệt Plan do Gemini lập (`Cross-Review`)
Khi Gemini đã viết `02-plan.md`, nhiệm vụ của Claude là **Kiểm định khắt khe từng chi tiết kỹ thuật**:
1. **Kiểm chứng độc lập trên code thật:**
   - Không mặc định tin các dòng trích dẫn trong Plan của Gemini. Dùng công cụ đọc file / Serena để mở đúng `file:line` kiểm tra xem hàm, tham số, schema DB và luồng gọi có đúng như Gemini mô tả không.
2. **Soi kỹ 4 điểm trọng yếu:**
   - **Độ chính xác & Edge-cases:** Logic Gemini đề xuất có bị lỗi với dữ liệu `None`/rỗng, trùng lặp, phân trang, hay điều kiện biên không?
   - **An toàn Backend & DB:** Có nguy cơ giữ DB session/lock qua lời gọi LLM không? Có thiếu kiểm tra quyền (`organization_id`, `feature_enabled`) hoặc thiếu migration Alembic không?
   - **Tính tối giản (Surgical & Minimal):** Cách sửa của Gemini có đụng chạm thừa hoặc phá vỡ quy ước hiện tại của module không?
   - **Chất lượng Test:** Các kịch bản test trong Plan có thực sự bắt được lỗi (non-tautological) không?
3. **Ghi kết quả trực tiếp vào mục `## 5. Nhật ký Duyệt Plan (Cross-Review bởi Claude)` trong `02-plan.md`:**
   - Phân loại rõ: 🔴 `[Blocker]`, 🟡 `[Should-fix]`, 🟢 `[Nit]`.
   - Nếu không có 🔴 → Đổi trạng thái đầu file thành `APPROVED`.
   - Nếu có 🔴 → Đổi trạng thái thành `CHANGES REQUESTED` kèm hướng sửa cụ thể tại `file:line`. (Nếu người dùng yêu cầu *"duyệt và sửa luôn Plan"*, Claude cập nhật trực tiếp các Step trong `02-plan.md` và chốt `APPROVED`).

### Vai trò 3: Khi Claude Chạy Plan (`Execute Plan`)
1. Kiểm tra trạng thái môi trường và migration DB local (`alembic current` vs `heads`) trước khi sửa code BE.
2. Đổi trạng thái file `02-plan.md` sang `IN_PROGRESS` và điền `Người chạy Plan: Claude`.
3. Thực thi chính xác từng Step trong `02-plan.md` (ưu tiên dùng công cụ chỉnh sửa chính xác, giữ nguyên định dạng và quy ước code xung quanh).
4. Chạy đầy đủ các cổng kiểm tra cơ học (`ruff check`, `ruff format --check`, `pytest`, kiểm tra giới hạn dòng FE ≤ 300 dòng/file).
5. Tick `- [x]` vào từng Step và mục DoD tự kiểm sau khi thấy kết quả chạy thật, ghi tóm tắt output vào mục `## 6. Nhật ký Thực thi`.
6. **Không tự ý `git commit` hay `git push`.**

### Vai trò 4: Khi Claude Nghiệm thu Code do Gemini chạy (`Cross-Verify`)
1. Chạy `git status` và `git diff` để kiểm tra toàn bộ thay đổi mà Gemini đã thực hiện.
2. Áp dụng chuẩn kiểm duyệt BookForge:
   - So khớp diff với `02-plan.md`: đã làm đủ các Step và thoả mãn mọi Quyết định đã chốt chưa?
   - Chạy lại lệnh linter, format và test suite liên quan để xác nhận xanh 100%.
   - Soát kỹ lỗi tiềm ẩn (regression, kiểu dữ liệu, xử lý ngoại lệ, rò rỉ tài nguyên).
3. Ghi kết quả vào mục `## 7. Kết quả Nghiệm thu Code (Cross-Verify bởi Claude)` trong `02-plan.md` và đổi trạng thái thành `VERIFIED` (hoặc `NEEDS FIX` kèm `file:line` nếu phát hiện lỗi).

---

## 3. Mẫu Câu lệnh Gọi Claude (Copy & Dùng ngay)

- **Giao Claude Phân tích & Lập Plan (2 bước):**
  ```text
  Theo tech_docs/rules/claude/rules.md (Vai trò 1) và tech_docs/rules/2_templates.md:
  Hãy khảo sát code và tạo tech_docs/plans/<slug>/01-analysis.md cùng 02-plan.md cho yêu cầu:
  <mô tả yêu cầu>
  ```
- **Giao Claude Duyệt Plan của Gemini:**
  ```text
  Theo tech_docs/rules/claude/rules.md (Vai trò 2):
  Hãy đọc và kiểm duyệt chéo kế hoạch của Gemini tại tech_docs/plans/<slug>/02-plan.md.
  Mở code thật kiểm chứng từng file:line, ghi nhận xét (🔴/🟡/🟢) vào mục 5 của file đó và cập nhật lại Plan nếu cần.
  ```
- **Giao Claude Chạy Plan đã chốt:**
  ```text
  Theo tech_docs/rules/claude/rules.md (Vai trò 3) và tech_docs/rules/3_git-and-conventions.md:
  Hãy chạy kế hoạch tại tech_docs/plans/<slug>/02-plan.md, kiểm tra test/lint và cập nhật tiến độ [x] vào file.
  ```
- **Giao Claude Nghiệm thu Code của Gemini:**
  ```text
  Theo tech_docs/rules/claude/rules.md (Vai trò 4):
  Hãy kiểm tra git diff và nghiệm thu kết quả thi công của Gemini theo tech_docs/plans/<slug>/02-plan.md.
  ```

