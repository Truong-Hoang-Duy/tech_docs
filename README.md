# Cách làm việc với AI trong BookForge

`tech_docs/` là thư mục làm việc riêng của bạn, lập trình viên khác **không có**.

| Nơi | Dùng cho cách làm nào | Vai trò |
|---|---|---|
| `README.md` (file này) | **Cả 4 cách** | Quy tắc nền tảng, bảng phân định ranh giới và quy trình của từng cách |
| [`prompts.md`](prompts.md) | **Cả 4 cách** | Câu lệnh mẫu để dán vào khung chat |
| [`templates.md`](templates.md) | **Chỉ Cách 3 & Cách 4** | Khung tài liệu `analysis.md`, `plan.md` và spec ngắn |
| [`spec-check.md`](spec-check.md) | **Chỉ Cách 4 (Việc có spec)** | Cách kiểm 3 lớp và cập nhật file spec có sẵn |
| `tasks/<slug>/`, `research/` | **Chỉ Cách 3 & Cách 4** | Hồ sơ từng việc (`analysis.md`, `plan.md`), tài liệu tham khảo |

---

## Phần I. Quy tắc nền tảng (Áp dụng chung)

### 1. Bốn nguyên tắc cốt lõi
1. **Lấy code mới nhất trước khi tìm hiểu.**
2. **Mọi nhận định phải chỉ ra được vị trí trong code** (`file:dòng`). Không đoán tên hàm, tên file, chữ trên màn hình.
3. **Không tự commit, push hay đổi nhánh** khi bạn chưa yêu cầu rõ ràng. Ngoại lệ duy nhất: tạo nhánh từ `dev` để bắt đầu code (theo mục I.3).
4. **Không nhắc `tech_docs`** trong bất kỳ file nào thuộc `backend/` hoặc `frontend/`, kể cả tên `analysis.md`, `plan.md`.

### 2. Đặt tên `<slug>` (khi tạo nhánh hoặc tạo hồ sơ)
- Tên duy nhất của một việc, dùng cho nhánh Git, thư mục `tasks/<slug>/` và spec trong `backend/`. AI tự đặt khi bắt đầu nếu bạn chưa đặt và báo lại ngay.
- **2–3 từ tiếng Anh**, viết thường, nối bằng `-`. Không tiếng Việt, không chứa ngày, `feat`, `fix`, `task`, `plan`, `audit`, `spec`. Ví dụ đúng: `canvas-page-scroll`, `export-exam-docx`.

### 3. Quy chuẩn Git
- **Lấy code mới (trước khi đọc code):** `git fetch` rồi đọc theo `origin/dev` (`backend/`, `frontend/`) hoặc `origin/main` (`tech_docs/`). Chỉ `git pull` khi đang ở nhánh chính và không có thay đổi dở; ngược lại **báo bạn, không tự đổi nhánh**.
- **Tạo nhánh trước dòng code đầu tiên (ở từng repo sẽ sửa):**
  1. `git status`. Có thay đổi dở dang → **dừng, báo bạn**, không tự cất hay bỏ.
  2. `git checkout dev` rồi `git pull origin dev`.
  3. `git checkout -b feat/<slug>` (hoặc `fix/<slug>`). Việc đụng hai repo thì dùng cùng tên nhánh.
  4. Xung đột, hoặc nhánh đã tồn tại → dừng, báo bạn. Không code thẳng trên `dev` / `main`.
  5. Nếu việc đang làm cần code của một nhánh khác chưa gộp vào `dev`: vẫn tạo nhánh mới từ `dev` theo đủ các bước trên trước, rồi mới `git merge <nhánh-kia>` vào nhánh vừa tạo (xung đột thì dừng, báo bạn).
- **Commit, push và merge vào `dev`:**
  - Sau khi bạn xác nhận kiểm tay đạt (và duyệt spec nếu có), AI **hỏi bạn có muốn commit + push nhánh, sau đó merge vào `dev` không**; chỉ làm khi bạn đồng ý.
  - Commit lên nhánh đã tạo (`feat/<slug>` hoặc `fix/<slug>`). Message tiếng Anh `<type>(<scope>): <mô tả>`, với `<type>` là `feat` | `fix` | `docs` | `test` | `refactor` | `merge`; xem `git log --oneline -10` để chọn `<scope>`.
  - **Không** thêm `Co-Authored-By` hay bất kỳ dấu ghi tên AI nào.
  - Chỉ `git add` từng file của việc này, không `git add -A`. `git diff --cached | grep tech_docs` phải không ra gì.
  - Khi merge vào `dev`: cập nhật `origin/dev` mới nhất (`git fetch origin` + `git merge origin/dev`; nếu có code mới thì chạy lại kiểm tra), rồi merge vào `dev` dùng `--no-ff` và **giữ nhánh** (theo `backend/CLAUDE.md`).

### 4. Quy chuẩn Suy luận Kiểm thử & Kiểm tay (Áp dụng cho mọi việc có sửa code)
- **Chống "học tủ" (Overfitting) theo bài test:**
  - Khi viết code hoặc viết System Prompt cho LLM, phải viết **logic tổng quát theo bản chất nghiệp vụ**; tuyệt đối **không nhét các câu hỏi, tình huống hay câu chữ cụ thể của kịch bản kiểm thử vào trong prompt hoặc nhánh `if/else` của code** chỉ để vượt qua bài test đó.
  - Khi tự kiểm thử và khi thiết kế kịch bản kiểm tay, phải có cả **câu thử biến thiên (không trùng với bất kỳ ví dụ mẫu nào trong prompt/code)** để chứng minh hệ thống xử lý đúng thật.
- **AI chủ động suy luận kiểm thử (cả Logic lẫn Giao diện):** Trong lúc làm từng Task và trước khi bàn giao, AI không chỉ kiểm tra luồng chính mà phải **tự suy luận thêm các trường hợp thực tế dễ lỗi** để viết test tự động và tự kiểm tra trước:
  - **Về logic & dữ liệu (Backend ↔ Frontend):** dữ liệu biên (rỗng, thiếu trường/`null`, sai định dạng, quá dài, ký tự đặc biệt, dữ liệu cũ trong DB); đầu ra từ AI hoặc dịch vụ ngoài bất thường (lỗi cú pháp, bọc thừa ký tự/markdown, rò rỉ thẻ kỹ thuật nội bộ, timeout/lỗi kết nối); bật/tắt cấu hình và phân quyền có hiệu lực đúng ở mọi bước không; dữ liệu có đồng nhất giữa luồng thường, luồng thời gian thực (streaming) và sau khi lưu DB / tải lại lịch sử không; có làm ảnh hưởng chức năng hoặc test cũ không.
  - **Về giao diện & hiển thị (UI/UX):** bố cục hiển thị đã hợp lý, cân đối và đồng nhất chưa; khung nổi (tooltip, popover, modal, menu) hoặc nội dung dài có bị tràn, vỡ khung hay bị cắt khuất ở mép màn hình/vùng cuộn không; ký hiệu toán học (LaTeX/KaTeX), công thức, bảng biểu, Markdown, tiếng Việt ở mọi vị trí (kể cả trong khung phụ, cảnh báo, xem trước hoặc khi đang chạy chữ streaming) có hiển thị chuẩn hay bị lộ mã thô không; đủ trạng thái đang tải / rỗng / lỗi và các thao tác đóng/mở, hủy, bấm nhiều lần, tải lại trang (F5).
- **AI tự tạo dữ liệu nền và bấm thử trước:**
  - AI chỉ tạo sẵn **dữ liệu nền** (tài khoản, tài liệu, đề thi, cấu hình quy chế/từ điển...) trước khi báo bạn để bạn vào là bấm thao tác thật được ngay; **không chèn sẵn kết quả/tin nhắn trả lời giả vào DB** để thay cho việc gọi LLM thật (trừ khi cần bản ghi lịch sử cũ để kiểm tương thích ngược).
  - AI dùng công cụ điều khiển trình duyệt tự bấm thử trước. Thao tác không tự làm được thì nhờ bạn làm bước đó; không có công cụ thì báo bạn, bạn bấm và AI đọc lỗi ở terminal.
- **Rồi đến bạn kiểm tay trên UI hoàn chỉnh (ngay trong phiên chat, sau khi xong hết các Task):** Khi đã hoàn thành toàn bộ các Task của kế hoạch, AI gửi hướng dẫn **kiểm tra tay trên UI hoàn chỉnh (test hết các chức năng vừa làm + các điểm đã suy luận về logic, bố cục hiển thị, ký hiệu toán học/định dạng và kịch bản biên)** trực tiếp vào khung chat theo **checklist 4 mục bắt buộc** cho từng kịch bản (không tạo file `manual-test.md`):
  1. **Dữ liệu & Mở màn hình:** dùng bản ghi / tài khoản nào AI đã tạo sẵn, đi tới đường dẫn hoặc menu nào, thấy tiêu đề gì.
  2. **Thao tác:** bấm vào đâu trên giao diện, nút gì, điền ô nào — **chữ trên nút, ô nhập, menu, tiêu đề phải giống y hệt trên màn hình** (chép từ code đang chạy, không tự đoán).
  3. **✅ Đúng khi thấy (tách rõ 2 phần nếu có gọi LLM):**
     - *Phần cố định / cấu trúc (phải khớp chính xác 100%):* trạng thái giao diện (biểu tượng, màu sắc, vị trí khung nổi), nhãn hệ thống cố định, danh sách tên mục/thuật ngữ trích xuất từ DB, định dạng trình bày (bảng, gạch đầu dòng, công thức toán học KaTeX hiển thị chuẩn không lộ mã thô), dữ liệu giữ nguyên khi tải lại trang (F5).
     - *Phần câu chữ do LLM sinh (đối chiếu tương đối theo ý nghĩa & quy tắc):* nội dung câu trả lời, lời giải thích hoặc tóm tắt mỗi lần chạy sẽ khác nhau về cách diễn đạt, miễn là thỏa mãn đúng ràng buộc nghiệp vụ (đúng xưng hô, đúng kiến thức, giữ nguyên thuật ngữ khóa, không lộ thẻ kỹ thuật nội bộ).
  4. **❌ Sai nếu thấy:** dấu hiệu lỗi cần báo lại.
- **Khi bạn báo lỗi:** AI tự tìm nguyên nhân, chỉ sửa khi bạn cho phép. Sửa xong chạy lại kiểm tra tự động, rồi bạn kiểm lại kịch bản đó và các kịch bản liên quan.

### 5. Tra cứu kỹ thuật & Những chỗ hay vấp
| Cần biết | Tìm ở |
|---|---|
| Lệnh kiểm tra | `backend/.github/workflows/ci.yml`, `frontend/.github/workflows/ci.yml`; chạy **đúng các lệnh trong đó** |
| Quy ước code | `backend/CLAUDE.md`, `frontend/CONVENTION.md` |
| Cách dự án hay làm | 2–3 tài liệu gần nhất trong `backend/docs/superpowers/` |
| Cách chạy app ở máy | `backend/LOCAL_QUICKSTART.md` |

**Lưu ý khi làm:**
1. **Spec có thể đã cũ.** Luôn đối chiếu với code thật.
2. **Thêm thì được, đừng thay cái đang chạy.** Sửa đè phần cũ dễ làm gãy chỗ khác.
3. **Thêm một mục mới có thể làm đỏ test đếm số lượng ở nơi khác.** Tìm hết các chỗ đang đếm hoặc liệt kê danh sách đó.
4. **Ghi kết quả thật:** dán lệnh đã chạy và dòng kết quả cuối, không ghi chung chung "đạt".
5. **Lỗi có sẵn khác lỗi do mình gây ra.** Chạy kiểm tra một lần trước khi sửa và ghi lại.

---

## Phần II. Bảng phân định ranh giới 4 cách làm

Khi bạn chưa chỉ định cách làm trong câu lệnh đầu, AI tìm hiểu nhanh hiện trạng và **khuyên bạn chọn 1 trong 4 cách dưới đây** (chờ bạn chốt trước khi sửa code hoặc tạo file):

| Cách làm | Khi nào dùng (Ranh giới) | Sửa code & Tạo nhánh? | Tạo hồ sơ `tasks/<slug>/`? | Spec trong `backend/` | File quy tắc cần đọc |
|---|---|---|---|---|---|
| **Cách 1: Chỉ hỏi** | Chỉ tìm hiểu luồng, hỏi cơ chế hoặc tìm nguyên nhân lỗi; chưa giao sửa code | ❌ Không | ❌ Không | ❌ Không | Chỉ `README.md` |
| **Cách 2: Làm nhanh** | Việc nhỏ hoặc đã rõ chỗ sửa (như mở tab mới, thêm cột/avatar, sửa 1 chỗ hiển thị/logic rõ ràng), làm gọn trong **1 phiên chat** | ✅ Có | ❌ Không | ❌ Không | Chỉ `README.md` |
| **Cách 3: Việc thường** | Tính năng mới, sửa nhiều màn hình cần chia Task, hoặc đụng cơ sở dữ liệu, phân quyền, mã lỗi (**chưa có spec sẵn**) | ✅ Có | ✅ Có (`analysis.md`, `plan.md`) | Hỏi bạn khi hoàn tất (tạo plan, spec hoặc cả 2 vào thư mục bạn xác nhận) | `README.md` + `templates.md` |
| **Cách 4: Việc có spec** | Đã có sẵn tài liệu đặc tả (ví dụ `backend/docs/product/<phân-hệ>/specs/...`) | ✅ Có | ✅ Có (`analysis.md`, `plan.md`) | ✅ **Cập nhật** file spec gốc khi hoàn tất | `README.md` + `templates.md` + `spec-check.md` |

---

## Phần III. Quy trình chi tiết của từng cách làm

### Cách 1: Chỉ hỏi (Chưa giao sửa code)
1. Lấy code mới nhất theo mục I.3, không tạo hay sửa bất kỳ file nào.
2. Tìm đúng các vị trí trong code (`file:dòng`) và trả lời ngắn gọn, dễ hiểu ngay trong chat:
   - Luồng từ lúc người dùng bấm trên giao diện → gọi tới đâu ở backend → lưu vào đâu (kèm `file:dòng`).
   - Điều kiện phân quyền hay cờ bật/tắt đang khoá chức năng này (nếu có).
   - Giới hạn hiện tại hoặc chỗ dễ lỗi.

---

### Cách 2: Làm nhanh (Code luôn trong 1 phiên chat, không tạo hồ sơ)
Gói gọn 4 bước ngay trong một phiên chat, **không tạo file nào trong `tech_docs/tasks/`**:
1. **Tạo nhánh:** Kiểm tra `git status` sạch, kéo `origin/dev` mới nhất và tạo nhánh `feat/<slug>` hoặc `fix/<slug>` theo mục I.3 (AI tự đặt `<slug>` theo mục I.2 nếu bạn chưa đặt).
2. **Code, Suy luận & Kiểm tra tự động:** Tìm đúng `file:dòng`, sửa code theo yêu cầu (logic tổng quát, không gài kịch bản test vào prompt/code), chủ động suy luận thêm các trường hợp dễ lỗi cả về logic Backend lẫn hiển thị/toán học/tương tác UI theo mục I.4 để xử lý và viết/chạy lệnh kiểm tra (test/lint/typecheck).
3. **Kiểm tay trong chat:** Tự tạo sẵn dữ liệu nền (nếu cần) và tự bấm thử trước, rồi báo bạn trong chat: đã sửa file nào, kết quả chạy test, kèm **hướng dẫn kiểm tra tay trên UI hoàn chỉnh theo checklist 4 mục** ở mục I.4.
4. **Chốt:** Khi bạn xác nhận kiểm tay OK, AI hỏi bạn có muốn **commit + push nhánh, sau đó merge vào `dev`** không (theo mục I.3).

---

### Cách 3: Việc thường (2 Giai đoạn: Lập kế hoạch → Code & Hoàn tất)

Đọc thêm [`templates.md`](templates.md) để lấy khung tài liệu. Gồm **2 giai đoạn** (tương ứng 2 câu lệnh trong `prompts.md`):

#### **Giai đoạn 1 — Tìm hiểu & Lập kế hoạch (`analysis.md` → `plan.md`)**
1. **Tìm hiểu (`analysis.md`):** Đọc code thật, ghi mốc commit vào đầu hồ sơ, nêu hiện trạng và phương án, viết mục 0 cho người không đọc code. Mở lại code kiểm `file:dòng` và mục 0 rồi dừng báo bạn kèm các điều cần quyết.
2. **Lập và kiểm kế hoạch (`plan.md`):** Ngay khi bạn nhắn chốt các điều cần quyết trong chat, AI tự lập `plan.md`:
   - Chia thành các **Task rõ ràng** (cả BE lẫn FE nếu cần, không chia theo tầng; mỗi Task có "Đúng khi thấy" tách rõ phần cố định 100% và phần LLM sinh tương đối, "Sai nếu thấy", các điểm suy luận cần tự test thêm và lệnh kiểm tra; không viết sẵn code).
   - Tự mở code và chạy lệnh thật để **kiểm 4 điều bắt buộc**: (1) `file:dòng` và tên hàm có thật, (2) lệnh kiểm tra chạy được, (3) mọi mục tiêu/điều đã chốt đều có Task, (4) mọi Task đều có tiêu chí đạt.
   - Đạt đủ 4 điều thì chốt trạng thái `APPROVED` và dừng báo bạn.

#### **Giai đoạn 2 — Code, Kiểm thử & Hoàn tất (Mở phiên chat mới khi `plan.md` đã `APPROVED`)**
1. **Tạo nhánh:** Tạo nhánh từ `dev` mới nhất theo mục I.3 (ghi mã commit vào Nhật ký của `plan.md`).
2. **Làm lần lượt hết các Task (không dừng chờ kiểm tay lẻ ở từng Task):** Với mỗi Task trong `plan.md` (từ lúc `APPROVED` không tự sửa tiêu chí hay xóa test):
   - Sửa code (viết tổng quát, không gài cứng ví dụ test vào prompt/code), viết/chạy kiểm tra tự động.
   - Chủ động **suy luận thêm các trường hợp cần test cả về logic Backend lẫn hiển thị/tương tác UI** theo mục I.4 (dữ liệu biên, đồng bộ các luồng, phân quyền, bố cục giao diện hợp lý chưa, lỗi ký hiệu toán học/Markdown...), tự kiểm tra và bấm thử trước.
   - Ghi kết quả vào Nhật ký, đánh dấu `[x]` vào `plan.md` và **chuyển luôn sang làm Task tiếp theo** cho đến khi xong hết tất cả các Task.
3. **Nghiệm thu, Kiểm tay UI hoàn chỉnh & Hoàn tất (tự động chạy khi xong hết các Task):**
   - Đọc lại toàn bộ diff, đối chiếu `plan.md`, chạy **toàn bộ** kiểm tra như CI.
   - Tự chuẩn bị sẵn dữ liệu nền trên hệ thống và tự bấm thử toàn luồng, sau đó **viết hướng dẫn kiểm tra tay trên UI hoàn chỉnh ngay trong phiên chat** (theo checklist 4 mục ở mục I.4) để bạn test một lượt toàn bộ các chức năng đã làm trong plan, bao gồm kiểm tra logic, bố cục giao diện, ký hiệu toán học/định dạng và các kịch bản biên (để trống/nhập sai · không có quyền · bấm hủy/tải lại trang · câu thử biến thiên · chức năng cũ gần đó).
   - Chờ bạn xác nhận kiểm tay đạt → đổi trạng thái `plan.md` sang `VERIFIED`.
   - **Hỏi bạn trước khi tạo tài liệu lưu vào `backend/`:** hỏi bạn muốn tạo **plan**, **spec** hay **cả 2** (hoặc không tạo), và **lưu ở thư mục nào** (ví dụ `backend/docs/superpowers/plans/`, `backend/docs/superpowers/specs/`...); **chỉ tạo file sau khi bạn xác nhận** (viết cho lập trình viên khác, không nhắc `tech_docs`).
   - Sau đó hỏi bạn có đồng ý **commit + push nhánh, sau đó merge vào `dev`** không.

---

### Cách 4: Việc có spec (2 Giai đoạn như Cách 3 + Kiểm và cập nhật Spec có sẵn)

Đọc thêm [`templates.md`](templates.md) và [`spec-check.md`](spec-check.md). Đi theo **2 Giai đoạn giống Cách 3**, cộng thêm các điểm riêng cho spec:
1. **Ở Giai đoạn 1 (Tìm hiểu & Lưu ngữ cảnh spec):**
   - Nếu bạn chưa gửi đường dẫn spec, AI **hỏi bạn đường dẫn file spec ở đâu** (kèm tài liệu gốc và phạm vi nếu có).
   - Ngay khi bạn nhắn đường dẫn vào phiên chat, AI **ghi đường dẫn đó vào đầu `analysis.md` và `plan.md`**. Từ đó về sau (kể cả khi mở phiên mới ở Giai đoạn 2), AI **tự động hiểu ngữ cảnh và lấy đường dẫn spec từ hồ sơ** mà không cần bạn nhập lại.
   - Kiểm spec theo 3 lớp của `spec-check.md` (1. Nghiệp vụ · 2. Khả thi · 3. Khớp code) vào mục 3 của `analysis.md`. Chỗ nghi sai hoặc mở rộng/đổi nghiệp vụ thì đưa lên mục 0 để bạn chốt, **không tự sửa file spec** khi đang làm.
2. **Ở Giai đoạn 2 (Code, Kiểm thử & Cập nhật spec):**
   - Mỗi Task làm theo thứ tự: viết test → thấy test hỏng → viết code → thấy test đúng, đồng thời chủ động suy luận test thêm cả về logic Backend lẫn giao diện/hiển thị theo mục I.4; làm liền mạch hết tất cả các Task trong `plan.md`.
   - Khi xong hết các Task: đối chiếu đầy đủ từng nghiệp vụ ở mục 3.0 của `analysis.md` và tiêu chí nghiệm thu của spec, chạy toàn bộ kiểm tra như CI rồi gửi **hướng dẫn kiểm tra tay trên UI hoàn chỉnh** trong chat để bạn kiểm một lượt.
   - Khi bạn xác nhận kiểm tay đạt: thay vì tạo spec mới, **cập nhật lại các quyết định đã chốt vào chính file spec gốc** theo `spec-check.md` mục 4. Báo bạn danh sách chỗ đã sửa trong spec và hỏi bạn có đồng ý **commit + push nhánh, sau đó merge vào `dev`** không.
