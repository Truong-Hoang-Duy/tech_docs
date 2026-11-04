# Cách làm việc với AI trong BookForge

`tech_docs/` là thư mục làm việc riêng của bạn — lập trình viên khác **không có** thư mục này.

Bộ luật gồm 3 file:

| File | Dùng để |
|---|---|
| `README.md` (file này) | Cách làm việc chung |
| [`prompts.md`](prompts.md) | Câu lệnh mẫu để dán vào khung chat |
| [`templates.md`](templates.md) | Khung tài liệu cho từng việc |

Luật chỉ ghi **cách làm chung**. Chi tiết của từng việc (lệnh kiểm tra, quy ước code, file liên quan) do AI **tự tìm trong repo code** và ghi vào tài liệu của việc đó — xem mục 10.

Các file luật cũ được giữ ở [`archive/`](archive/) để tra cứu, không dùng nữa.

---

## 1. Năm nguyên tắc

1. **Lấy code mới nhất trước khi tìm hiểu.** Không phân tích hay lập kế hoạch trên code cũ (cách lấy: mục 8).
2. **Mọi nhận định phải chỉ ra được vị trí trong code** (`file:dòng`). Không đoán tên hàm, tên file, chữ trên màn hình.
3. **Người làm và người duyệt là hai AI khác nhau** (Gemini ⇄ Claude). Không AI nào tự lập rồi tự duyệt, tự code rồi tự nghiệm thu.
4. **Không tự commit, push hay đổi nhánh** khi bạn chưa yêu cầu rõ ràng.
5. **Không nhắc `tech_docs`** trong bất kỳ file nào thuộc `backend/` hoặc `frontend/` — kể cả tên `01-analysis.md`, `02-plan.md`, `03-manual-test.md`.

---

## 2. Chọn loại việc

| Loại việc | Khi nào |
|---|---|
| **Việc nhỏ** | Lỗi đã rõ chỗ, sửa ≤ 3 file, **không** đụng cơ sở dữ liệu, phân quyền hay mã lỗi |
| **Việc thường** | Tính năng mới hoặc lỗi lớn, nhiều file, có thể đụng cả backend và frontend |
| **Việc có spec** | Đã có sẵn tài liệu đặc tả (ví dụ `backend/docs/product/<phân-hệ>/specs/...`) |

---

## 3. Luồng 7 bước (dùng chung cho mọi loại việc)

```text
1. Tìm hiểu → 2. Lập kế hoạch → 3. Duyệt chéo → 4. Làm → 5. Nghiệm thu chéo → 6. Kiểm tay → 7. Chép kế hoạch sang backend + Commit
```

| Bước | Ai làm | Làm gì | Ghi vào |
|---|---|---|---|
| **1. Tìm hiểu** | AI A | Lấy code mới, đọc code thật, nêu hiện trạng và phương án | `01-analysis.md` |
| **2. Lập kế hoạch** | AI A | Chia bước, ghi file sẽ sửa, lệnh kiểm tra, nháp các kịch bản kiểm thử | `02-plan.md` |
| **3. Duyệt chéo** | AI B | Mở code thật đối chiếu kế hoạch, ghi nhận xét (mục 5) | `02-plan.md` — mục Duyệt chéo |
| **4. Làm** | AI bạn chọn | Làm từng bước, xong bước nào đánh dấu `[x]` và ghi kết quả | Code + `02-plan.md` — mục Nhật ký |
| **5. Nghiệm thu chéo** | AI **không** viết code ở bước 4 | Đối chiếu thay đổi với kế hoạch, chạy lại **toàn bộ** kiểm tra | `02-plan.md` — mục Nghiệm thu |
| **6. Kiểm tay** | AI bấm thử, rồi bạn | Xem mục 6 | `03-manual-test.md` |
| **7. Chép + Commit** | AI, khi bạn yêu cầu | Chép kế hoạch sang backend (mục 7), rồi commit (mục 8) | `02-plan.md` — mục Commit |

**Ba loại việc chỉ khác nhau ở 3 chỗ:**

| | Việc nhỏ | Việc thường | Việc có spec |
|---|---|---|---|
| Bước 1 | Bỏ `01-analysis.md`, ghi hiện trạng thẳng vào mục 1 của `02-plan.md` | Tìm hiểu yêu cầu | **So spec với code thật**, ghi những chỗ spec đã cũ |
| Bước 2 | Kế hoạch ngắn | Kế hoạch chia theo bước | Phần kế hoạch viết theo dạng superpowers (từng Task, 4 bước: viết test → thấy test hỏng → viết code → thấy test chạy đúng) |
| Bước 7 | Chép bản ngắn | Chép kế hoạch | Chép kế hoạch |

**AI phải dừng lại hỏi bạn khi:**
- Xong bước 1, 2, 3 — để bạn xem trước khi đi tiếp.
- Lấy code mới bị xung đột, hoặc đang có thay đổi dở dang.
- Thực tế khác kế hoạch đến mức phải đổi hướng.
- Cần một quyết định về nghiệp vụ mà tài liệu chưa trả lời.

---

## 4. Phân vai Gemini và Claude

Bạn chọn AI nào làm **AI A** (lập), AI còn lại là **AI B** (duyệt). Có thể đảo vai tuỳ việc.

| | Gemini | Claude |
|---|---|---|
| **Mạnh ở** | Đọc rộng cả repo, lần theo luồng từ giao diện xuống backend, phát hiện chỗ lệch giữa backend và frontend | Đọc sâu từng hàm, bắt trường hợp biên, an toàn dữ liệu, sửa code chính xác |
| **Nên lập kế hoạch khi** | Việc đụng rộng nhiều màn hình, nhiều điểm gọi | Việc đụng sâu logic backend, dữ liệu, phân quyền |
| **Khi duyệt, chú ý** | Có bỏ sót màn hình, luồng phụ thuộc nào không | Tên file/hàm có đúng code thật không, có trường hợp biên nào bị sót, có phức tạp thừa không |

Cả hai đều làm được mọi bước, kể cả bấm thử trên trình duyệt ở bước 6.

---

## 5. Nơi lưu file và trạng thái

**Mỗi việc một thư mục** `tech_docs/plans/<slug>/`:

| File | Nội dung |
|---|---|
| `01-analysis.md` | Tìm hiểu (việc có spec: so spec với code) |
| `02-plan.md` | **Nguồn sự thật duy nhất**: kế hoạch, nhận xét duyệt, tiến độ, quyết định phát sinh, nghiệm thu, commit |
| `03-manual-test.md` | Hướng dẫn và kết quả kiểm tay |

Không tạo thêm file rời (`status.md`, `audit.md`, `qa.md`...).

**Trạng thái ghi ở đầu `02-plan.md`:**

| Trạng thái | Nghĩa |
|---|---|
| `DRAFT` | Nháp, chưa duyệt |
| `CHANGES_REQUESTED` | Người duyệt yêu cầu sửa kế hoạch |
| `APPROVED` | Đã duyệt, sẵn sàng làm |
| `IN_PROGRESS` | Đang làm |
| `NEEDS_FIX` | Nghiệm thu hoặc kiểm tay phát hiện lỗi |
| `VERIFIED` | Đã nghiệm thu và kiểm tay đạt, chờ commit |
| `COMMITTED` | Đã chép kế hoạch sang backend và commit |

**Quy tắc duyệt chéo (bước 3):**
- Nhận xét chia 3 mức: 🔴 **Blocker** (sai sự thật code, lỗi logic, làm hỏng chỗ khác, thiếu bảo mật) · 🟡 **Should-fix** (chưa gọn, thiếu trường hợp phụ, thiếu test) · 🟢 **Nit** (đặt tên, câu chữ).
- Người duyệt **được tự sửa** điểm 🟡 / 🟢 vào kế hoạch rồi chốt `APPROVED`.
- Có điểm 🔴, hoặc phải viết lại phần lớn kế hoạch → chốt `CHANGES_REQUESTED`. Người lập sửa, người duyệt xem lại (hoặc bạn chốt). Người duyệt **không tự duyệt bản do chính mình viết lại**.

---

## 6. Kiểm tay (bước 6)

Bắt buộc với **mọi** việc, kể cả việc nhỏ — để bạn nhìn thấy kết quả trực tiếp. Làm sau nghiệm thu, trước commit.

**Ai làm:** Gemini hoặc Claude đều được — nên chọn AI **không** viết code ở bước 4 (thường là AI vừa nghiệm thu ở bước 5), để người kiểm khác người làm.

- **6a. AI bấm thử:** AI mở app bằng công cụ điều khiển trình duyệt mà nó đang có, làm lần lượt từng kịch bản kiểm thử, ghi kết quả và bằng chứng (ảnh chụp hoặc video ngắn) vào `03-manual-test.md`.
  - Gặp thao tác không tự làm được (chọn file từ máy, hộp "Bạn có chắc...?", đăng nhập bằng mã gửi về điện thoại...) → dừng lại nhờ bạn làm bước đó, rồi làm tiếp.
  - Nếu AI không có công cụ điều khiển trình duyệt → báo cho bạn, chỉ viết hướng dẫn; bạn bấm, AI đọc lỗi ở terminal và đối chiếu kết quả bạn báo.
- **6b. Bạn xem lại:** xem bằng chứng AI để lại và tự bấm luồng chính. Bạn đồng ý thì mới sang bước 7.

**Hướng dẫn kiểm tay phải đạt 5 điều:**
1. Chữ trên nút, ô nhập, tiêu đề **đúng như trên màn hình** — chép từ code đang chạy, không đoán.
2. **AI bấm thử trước** rồi mới đưa hướng dẫn cho bạn.
3. Hướng dẫn **từng kịch bản một**, chờ bạn báo kết quả rồi mới sang kịch bản sau.
4. Mỗi kịch bản có **"Đúng khi thấy"** và **"Sai nếu thấy"** để bạn tự đánh giá được.
5. Khi bạn báo lỗi, **AI tự tìm nguyên nhân trước**; chỉ sửa code khi bạn cho phép.

> **Gợi ý:** Khi viết kịch bản kiểm thử (test scenario), cân nhắc các loại: luồng chính từ đầu đến cuối · để trống hoặc nhập sai · file lạ · người không có quyền · bấm hủy hoặc tải lại trang · mở thử file xuất ra · chức năng cũ gần đó vẫn chạy. Loại nào không liên quan thì bỏ qua.

**Khi một kịch bản không đạt:** AI ghi lỗi vào `03-manual-test.md`, đổi trạng thái `NEEDS_FIX`, sửa (khi bạn cho phép), chạy lại kiểm tra tự động; sau đó bạn kiểm lại kịch bản bị lỗi và các kịch bản liên quan.

---

## 7. Chép kế hoạch sang backend (bước 7 — làm trước khi commit)

- **Mọi việc**, kể cả việc nhỏ, chép kế hoạch sang `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`, để bản chép được commit **cùng** code.
- **Chỉ chép Phần A — Kế hoạch** của `02-plan.md` (mục tiêu, quyết định, file thay đổi, các bước đã đánh dấu, điều kiện hoàn thành). **Không** chép nhận xét duyệt, nhật ký, kiểm tay.
- Bản chép phải **tự đọc hiểu được** với người không có `tech_docs`: không chứa chữ `tech_docs`, không nhắc `01-analysis.md` / `02-plan.md` / `03-manual-test.md`.
- Việc có spec giữ đúng dạng superpowers (xem `templates.md`).
- Chép xong mới sang commit (mục 8). Commit xong: ghi đường dẫn bản chép và mã commit vào mục Commit của `02-plan.md`, đổi trạng thái `COMMITTED`.

---

## 8. Git

**Lấy code mới (bước 1):**
- Chạy `git fetch` rồi đọc code theo nhánh chính trên remote: `origin/dev` cho `backend/` và `frontend/`, `origin/main` cho `tech_docs/`.
- Chỉ `git pull` khi đang đứng ở nhánh chính và không có thay đổi dở dang. Đang ở nhánh khác hoặc có thay đổi dở → **báo bạn, không tự đổi nhánh**.
- Ghi **mốc code** (mã commit đang đọc) vào đầu `01-analysis.md` và `02-plan.md`.

**Khi bắt đầu viết code (bước 4):**
- Tạo nhánh `feat/<slug>` hoặc `fix/<slug>` từ nhánh chính mới nhất. Việc đụng cả hai repo thì dùng **cùng tên nhánh** ở cả hai.
- Không code thẳng trên `dev` / `main`.
- Nếu mốc code đã cũ so với lúc lập kế hoạch, kiểm lại các vị trí `file:dòng` trước khi sửa.

**Trước nghiệm thu (bước 5) và trước commit (bước 7):** cập nhật nhánh theo `origin/dev` mới nhất rồi chạy lại kiểm tra.

**Commit (bước 7, chỉ khi bạn yêu cầu):**
- Commit message bằng **tiếng Anh**, dạng `<type>(<scope>): <mô tả>`.
  - `<type>`: `feat` | `fix` | `docs` | `test` | `refactor` | `merge`.
  - `<scope>`: khu vực bị thay đổi — chạy `git log --oneline -10` để chọn cho nhất quán.
- **Không** thêm dòng `Co-Authored-By` hay bất kỳ dấu ghi tên AI nào.
- Chỉ `git add` từng file thuộc kế hoạch (không `git add -A`).
- Kiểm không lọt chữ `tech_docs`: `git diff --cached | grep tech_docs` phải không ra gì.
- Chỉ `push` khi bạn yêu cầu push rõ ràng.
- Merge vào `dev`: dùng `--no-ff` và **giữ nhánh** sau khi merge (theo `backend/CLAUDE.md`).

---

## 9. Đặt tên `<slug>`

`<slug>` là tên định danh **duy nhất** của một việc, dùng chung cho: `tech_docs/plans/<slug>/`, `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md` và nhánh `feat/<slug>` / `fix/<slug>`.

- **2–3 từ tiếng Anh**, viết thường, nối bằng `-` (chỉ gồm `a-z`, `0-9`, `-`).
- Không tiếng Việt (kể cả không dấu), không khoảng trắng, không `_`.
- Không chứa ngày, `feat`, `fix`, `task`, `plan`, `audit`, `spec`.
- Chọn danh từ cốt lõi, bỏ từ phụ (`and`, `improvements`, `principles`...).
- Đặt **một lần** ở bước 1, không đổi về sau.
- Tên file luôn bằng tiếng Anh.

| ✅ Đúng | ❌ Sai | Lý do |
|---|---|---|
| `canvas-page-scroll` | `canvas-multi-page-review-scroll-fix` | Quá 3 từ, chứa `fix` |
| `export-exam-docx` | `xuat-de-thi-docx` | Tiếng Việt |
| `flow-ai-backend` | `2026-11-03-flow-ai` | Chứa ngày |

---

## 10. Chi tiết kỹ thuật tìm ở đâu

Luật này không chép lại chi tiết kỹ thuật. Khi làm từng việc, AI tự đọc:

| Cần biết | Tìm ở |
|---|---|
| Lệnh kiểm tra | File CI của repo: `backend/.github/workflows/ci.yml`, `frontend/.github/workflows/ci.yml` — chạy **đúng các lệnh trong đó** |
| Quy ước frontend | `frontend/CONVENTION.md` |
| Quy ước backend | `backend/CLAUDE.md` |
| Cách dự án hay làm | 2–3 kế hoạch gần nhất trong `backend/docs/superpowers/plans/` |
| Cách chạy app ở máy | `backend/LOCAL_QUICKSTART.md` |

---

## 11. Những chỗ hay vấp

1. **Code thay đổi từng ngày.** Ghi mốc code lúc lập kế hoạch; trước khi làm và trước khi commit, cập nhật nhánh theo bản mới nhất.
2. **Spec có thể đã cũ.** Tên file, số thứ tự, tên hàm trong spec phải kiểm lại trên code thật (lần pkg-00: 36/38 tham chiếu trong kế hoạch đầu tiên không tồn tại).
3. **Thêm thì được, đừng thay cái đang chạy.** Sửa đè phần cũ dễ làm gãy chỗ khác.
4. **Thêm một mục mới có thể làm đỏ test đếm số lượng ở nơi khác.** Tìm hết các chỗ đang đếm hoặc liệt kê danh sách đó.
5. **Nghiệm thu phải chạy toàn bộ test như CI.** Chạy một phần sẽ bỏ sót (lần trước sót 4 lỗi).
6. **Ghi kết quả thật**, không ghi chung chung "đạt / sạch" — dán lệnh đã chạy và dòng kết quả cuối.
7. **Lỗi có sẵn khác lỗi do mình gây ra.** Chạy kiểm tra một lần trước khi sửa và ghi lại, để phân biệt.
8. **Người duyệt không tự duyệt phần mình vừa sửa lớn.** Sửa nặng thì để `CHANGES_REQUESTED` và nhờ người kia xem lại.
