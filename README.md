# Cách làm việc với AI trong BookForge

`tech_docs/` là thư mục làm việc riêng của bạn, lập trình viên khác **không có**.

| Nơi | Dùng để |
|---|---|
| `README.md` (file này) | Cách làm chung |
| [`prompts.md`](prompts.md) | Câu lệnh mẫu để dán vào khung chat |
| [`templates.md`](templates.md) | Khung tài liệu |
| [`spec-check.md`](spec-check.md) | Cách kiểm và cập nhật spec, **chỉ đọc khi việc có spec** |
| `tasks/<slug>/`, `research/` | Hồ sơ từng việc, tài liệu tham khảo |

## 1. Năm nguyên tắc

1. **Lấy code mới nhất trước khi tìm hiểu** (mục 8).
2. **Mọi nhận định phải chỉ ra được vị trí trong code** (`file:dòng`). Không đoán tên hàm, tên file, chữ trên màn hình.
3. **Mỗi việc chỉ một agent làm từ đầu đến cuối** (Claude hoặc Gemini, bạn chọn lúc bắt đầu). Không chia việc cho AI khác hay subagent. Chỉ đổi agent khi bạn quyết định. Mọi kết luận phải dựa trên code vừa mở hoặc lệnh vừa chạy; bạn là người chốt.
4. **Không tự commit, push hay đổi nhánh** khi bạn chưa yêu cầu rõ ràng. Ngoại lệ duy nhất: đổi nhánh để bắt đầu code ở bước 4 (mục 8).
5. **Không nhắc `tech_docs`** trong bất kỳ file nào thuộc `backend/` hoặc `frontend/`, kể cả tên `analysis.md`, `plan.md`, `manual-test.md`.

## 2. Chọn cách làm

| Cách làm | Khi nào | Tạo những gì |
|---|---|---|
| **Việc thường, chỉ plan** | Lỗi đã rõ chỗ hoặc thay đổi ít, không đụng cơ sở dữ liệu, phân quyền hay mã lỗi | `plan.md`, `manual-test.md`; lý do ghi trong commit hoặc PR |
| **Việc thường, plan + spec** | Tính năng mới, đổi điều người dùng thấy, hoặc đụng cơ sở dữ liệu, phân quyền, mã lỗi | Thêm `analysis.md` và spec ngắn trong `backend/` |
| **Việc có spec** | Đã có sẵn tài liệu đặc tả (ví dụ `backend/docs/product/<phân-hệ>/specs/...`) | `analysis.md`, `plan.md`, `manual-test.md`; cập nhật spec đó (`spec-check.md`) |

Với việc thường, **AI phải hỏi bạn trước khi tạo file: chỉ plan hay plan + spec**, kèm một câu lời khuyên. AI không tự chọn, trừ khi câu lệnh đã ghi sẵn.

## 3. Luồng 7 bước

```text
1. Tìm hiểu → 2. Lập kế hoạch → 3. Kiểm kế hoạch → 4. Làm và kiểm từng Task → 5. Nghiệm thu → 6. Kiểm tay toàn bộ → 7. Lưu spec + Commit
```

| Bước | Làm gì | Ghi vào |
|---|---|---|
| **1. Tìm hiểu** | Đọc code thật, nêu hiện trạng và phương án. Có `analysis.md` thì viết mục 0 cho bạn đọc. Chỉ plan: ghi hiện trạng vào mục 1 của `plan.md` rồi sang bước 2 | `analysis.md` |
| **2. Lập kế hoạch** | Chia Task và viết tiêu chí đạt trước khi code (mục 4) | `plan.md` |
| **3. Kiểm kế hoạch** | Làm liền sau bước 2, kiểm 4 điều ở mục 5 | `plan.md` |
| **4. Làm** | Từng Task: code, chạy kiểm tra, agent bấm thử, rồi bạn kiểm | Code, `plan.md`, `manual-test.md` |
| **5. Nghiệm thu** | Đọc lại toàn bộ diff, đối chiếu kế hoạch, chạy **toàn bộ** kiểm tra như CI | `plan.md` |
| **6. Kiểm tay** | Agent chạy lại mọi kịch bản, rồi bạn bấm luồng chính (mục 6) | `manual-test.md` |
| **7. Lưu spec + Commit** | Khi bạn yêu cầu (mục 7, mục 8) | `plan.md` |

**Cuối bước 1, trước khi báo bạn:** mở lại code và spec / yêu cầu gốc, kiểm `file:dòng` có thật không, mục 0 có tóm tắt sai hoặc hứa nhiều, ít hơn không.

**AI phải dừng lại hỏi bạn khi:**
- Việc thường, lúc chọn cách làm (mục 2).
- Xong bước 1 (chỉ plan: bỏ qua điểm dừng này), xong bước 3, và xong **mỗi Task** ở bước 4.
- Lấy code mới bị xung đột, hoặc đang có thay đổi dở dang.
- Thực tế khác kế hoạch đến mức phải đổi hướng.
- Cần một quyết định về nghiệp vụ mà tài liệu chưa trả lời.

**Mở phiên mới (vẫn cùng agent) khi:** bắt đầu bước 4 · sửa hai lần vẫn sai, khi đó viết lại câu lệnh thay vì sửa lần ba · chuyển sang việc khác. Bước 5 và 6 làm tiếp trong phiên đang code. Hồ sơ trong `tasks/<slug>/` phải đủ để phiên mới làm tiếp được.

## 4. Chia Task

- **Mỗi Task là một phần chức năng bạn bấm thử được**, gồm cả backend lẫn frontend nếu cần. Không chia theo tầng kiểu làm hết backend rồi mới làm frontend.
- **Viết tiêu chí trước khi code:** mỗi Task có "Đúng khi thấy", "Sai nếu thấy" và lệnh kiểm tra.
- **Từ lúc `APPROVED`, agent không tự sửa tiêu chí hay xóa test để cho đạt.** Thấy tiêu chí sai thì báo bạn.
- Phần không bấm thử được (migration, tác vụ nền): gộp vào Task dùng nó. Không gộp được thì ghi rõ "Không bấm thử được" và lệnh chứng minh nó chạy đúng.
- Một Task nên làm xong trong một phiên. Lớn hơn thì tách.
- Kế hoạch chỉ ghi quyết định, file, tiêu chí và lệnh kiểm tra. Không viết sẵn code trong kế hoạch.

## 5. Kiểm kế hoạch và trạng thái

**Bước 3 chỉ kiểm 4 điều, bằng cách mở code và chạy lệnh thật:**
1. Mọi `file:dòng`, tên hàm trong kế hoạch có thật.
2. Mọi lệnh kiểm tra có thật và chạy được.
3. Mỗi mục tiêu hoặc nghiệp vụ đều có Task tương ứng, và mỗi điều bạn đã chốt đều có trong kế hoạch.
4. Mỗi Task đều có tiêu chí đạt.

Thấy sai thì sửa ngay. **Cần bạn quyết** là việc đổi điều đã chốt, đổi điều người dùng thấy hoặc làm khác spec; agent không tự sửa những việc này. Hết chỗ sai và hết việc cần quyết thì chốt `APPROVED`, rồi **dừng báo bạn**; chỉ sang bước 4 khi bạn cho làm.

**Trạng thái ghi ở đầu `plan.md`:** `DRAFT` (nháp hoặc còn việc cần quyết) → `APPROVED` (chờ bạn cho làm) → `IN_PROGRESS` → `VERIFIED` (nghiệm thu và kiểm tay đạt, chờ commit) → `COMMITTED`. `NEEDS_FIX` khi nghiệm thu hoặc kiểm tay phát hiện lỗi. `plan.md` là **nguồn sự thật duy nhất** của một việc. Không tạo thêm file rời (`status.md`, `audit.md`...).

## 6. Kiểm tay

Bắt buộc với **mọi** việc, ở hai lúc: sau mỗi Task (theo tiêu chí của Task) và ở bước 6 (toàn bộ).

- **AI bấm thử trước** bằng công cụ điều khiển trình duyệt, ghi kết quả và ảnh chụp vào `manual-test.md`. Thao tác không tự làm được thì nhờ bạn làm bước đó. Không có công cụ thì báo bạn, chỉ viết hướng dẫn; bạn bấm, AI đọc lỗi ở terminal.
- **Rồi đến bạn:** AI hướng dẫn từng kịch bản một, chờ bạn báo kết quả mới sang kịch bản sau.
- Chữ trên nút, ô nhập, tiêu đề phải **đúng như trên màn hình**, chép từ code đang chạy.
- Bước 6 thêm các kịch bản nếu liên quan: để trống hoặc nhập sai · file lạ · người không có quyền · bấm hủy hoặc tải lại trang · mở thử file xuất ra · chức năng cũ gần đó vẫn chạy.
- **Khi bạn báo lỗi:** AI tự tìm nguyên nhân, ghi vào `manual-test.md`, đổi `NEEDS_FIX`, chỉ sửa khi bạn cho phép. Sửa xong chạy lại kiểm tra tự động, rồi bạn kiểm lại kịch bản đó và các kịch bản liên quan.

## 7. Lưu spec (bước 7, trước khi commit)

`tech_docs/` chỉ mình bạn có, nên `backend/` là nơi duy nhất người khác tra lại nghiệp vụ. Kế hoạch **không** chép sang `backend/`, chỉ lưu phần code không tự nói được: nghiệp vụ, quyết định và lý do, phần cố ý chưa làm.

| Cách làm | Làm gì |
|---|---|
| Chỉ plan | Không tạo file. Ghi lý do trong commit hoặc PR |
| Plan + spec | **Tạo** spec ngắn `backend/docs/superpowers/specs/YYYY-MM-DD-<slug>.md` theo `templates.md` |
| Có spec | **Cập nhật** spec theo `spec-check.md` mục 4 |

- Viết cho **lập trình viên khác**, ghi đúng những gì đã làm thật, tự đọc hiểu được. Không nhắc `tech_docs`, `analysis.md`, `plan.md`, `manual-test.md`.
- Việc chỉ đụng frontend cũng lưu spec vào `backend/`.
- Báo bạn spec vừa tạo hoặc các chỗ đã sửa, **chờ bạn đồng ý** rồi mới commit, cùng nhánh với code.

## 8. Git

**Lấy code mới (bước 1):** `git fetch` rồi đọc theo `origin/dev` (`backend/`, `frontend/`) hoặc `origin/main` (`tech_docs/`). Chỉ `git pull` khi đang ở nhánh chính và không có thay đổi dở; ngược lại **báo bạn, không tự đổi nhánh**. Ghi mốc code vào đầu hồ sơ.

**Trước dòng code đầu tiên (bước 4), ở từng repo sẽ sửa:**
1. `git status`. Có thay đổi dở dang → **dừng, báo bạn**, không tự cất hay bỏ.
2. `git checkout dev` rồi `git pull origin dev`.
3. `git checkout -b feat/<slug>` (hoặc `fix/<slug>`). Việc đụng hai repo thì dùng cùng tên nhánh.
4. Ghi mã commit của `dev` vào Nhật ký. Mốc code đã cũ thì kiểm lại các `file:dòng`.

Xung đột, hoặc nhánh đã tồn tại → dừng, báo bạn. Không code thẳng trên `dev` / `main`. Việc phụ thuộc nhánh chưa vào `dev`: làm đủ các bước trên rồi merge nhánh đó vào; xung đột thì dừng, báo bạn. **Trước bước 5 và trước commit:** cập nhật nhánh theo `origin/dev` mới nhất rồi chạy lại kiểm tra.

**Commit (bước 7, chỉ khi bạn yêu cầu):**
- Message tiếng Anh `<type>(<scope>): <mô tả>`, với `<type>` là `feat` | `fix` | `docs` | `test` | `refactor` | `merge`; xem `git log --oneline -10` để chọn `<scope>`.
- **Không** thêm `Co-Authored-By` hay bất kỳ dấu ghi tên AI nào.
- Chỉ `git add` từng file của việc này, không `git add -A`.
- `git diff --cached | grep tech_docs` phải không ra gì.
- Chỉ `push` khi bạn yêu cầu rõ ràng. Merge vào `dev` dùng `--no-ff` và **giữ nhánh** (theo `backend/CLAUDE.md`).

## 9. Đặt tên `<slug>`

Tên duy nhất của một việc, dùng cho `tasks/<slug>/`, spec trong `backend/` và nhánh. AI tự đặt ở bước 1 nếu bạn chưa đặt và báo lại ngay; chỉ đổi được trước bước 2.

**2–3 từ tiếng Anh**, viết thường, nối bằng `-`. Không tiếng Việt, không chứa ngày, `feat`, `fix`, `task`, `plan`, `audit`, `spec`. Ví dụ đúng: `canvas-page-scroll`, `export-exam-docx`.

## 10. Chi tiết kỹ thuật tìm ở đâu

| Cần biết | Tìm ở |
|---|---|
| Lệnh kiểm tra | `backend/.github/workflows/ci.yml`, `frontend/.github/workflows/ci.yml`; chạy **đúng các lệnh trong đó** |
| Quy ước code | `backend/CLAUDE.md`, `frontend/CONVENTION.md` |
| Cách dự án hay làm | 2–3 tài liệu gần nhất trong `backend/docs/superpowers/` |
| Cách chạy app ở máy | `backend/LOCAL_QUICKSTART.md` |

## 11. Những chỗ hay vấp

1. **Spec có thể đã cũ.** Lần pkg-00: 36/38 tham chiếu trong kế hoạch đầu tiên không tồn tại.
2. **Thêm thì được, đừng thay cái đang chạy.** Sửa đè phần cũ dễ làm gãy chỗ khác.
3. **Thêm một mục mới có thể làm đỏ test đếm số lượng ở nơi khác.** Tìm hết các chỗ đang đếm hoặc liệt kê danh sách đó.
4. **Nghiệm thu phải chạy toàn bộ test như CI.** Chạy một phần sẽ bỏ sót (lần trước sót 4 lỗi).
5. **Ghi kết quả thật:** dán lệnh đã chạy và dòng kết quả cuối, không ghi chung chung "đạt".
6. **Lỗi có sẵn khác lỗi do mình gây ra.** Chạy kiểm tra một lần trước khi sửa và ghi lại.

## 12. Đo và xem lại

Mỗi việc ghi vào mục Số đo của `plan.md`: thời gian đến lúc merge · số lỗi bạn bắt được khi kiểm tay · số lần phải sửa sau merge. Cảm giác "nhanh hơn" thường không đáng tin, nên dựa vào số. Sau khoảng 10 việc, dùng câu lệnh "Xem lại luật" trong `prompts.md` để bỏ những bước không có tác dụng.
