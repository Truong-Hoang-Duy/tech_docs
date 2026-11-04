# Khuôn mẫu Tài liệu Chuẩn (Templates)

Mọi tài liệu trong `tech_docs/plans/<slug>/` viết bằng **tiếng Việt**, ngắn gọn, trực diện, giữ nguyên tên hàm/biến/đường dẫn trong dấu backtick `` ` ``, không dùng YAML frontmatter.

---

## 1. Khuôn mẫu `01-analysis.md` (Bước 1: Phân tích)

Đặt tại: `tech_docs/plans/<slug>/01-analysis.md`

````markdown
# 01 — Phân tích: <Tên ngắn gọn của tính năng / lỗi>

**Ngày:** YYYY-MM-DD · **Người phân tích:** <Gemini | Claude> · **Phía tác động:** <BE | FE | Cả hai>

## 1. Mục tiêu & Phạm vi
- **Yêu cầu cần đạt:** <1–3 gạch đầu dòng mô tả hành vi mong muốn>
- **Ngoài phạm vi (Không làm):** <Những phần cắt bỏ để tránh phình phạm vi>

## 2. Hiện trạng & Nguyên nhân gốc (Có bằng chứng `file:line`)
- **Luồng hiện tại:** <Mô tả ngắn gọn luồng chạy từ điểm đầu tới điểm cuối>
- **Vị trí & Nguyên nhân cốt lõi:**
  - `<đường_dẫn_file>:<số_dòng>` — <Giải thích vì sao gây lỗi hoặc thiếu tính năng>
  ```<ngôn_ngữ>
  <Trích đoạn code thực tế liên quan, tối đa 15 dòng>
  ```

## 3. Điểm va chạm & Ràng buộc Kỹ thuật
- **Database / Migration:** <Có đổi bảng/cột không? Nếu có nêu rõ>
- **Hợp đồng API (BE ↔ FE):** <Endpoint nào, request/response shape có đổi không?>
- **Ràng buộc quy ước:** <Feature flag liên quan, giới hạn 300 dòng/file của FE, phân quyền, v.v.>

## 4. Phương án Đề xuất
> *(Nếu có 2 hướng cần cân nhắc thì nêu Phương án A / B kèm ưu nhược điểm và Khuyến nghị. Nếu bài toán đã rõ ràng thì trình bày thẳng Phương án tối ưu).*

- **Hướng giải quyết:** <Mô tả rõ cách sửa>
- **Lý do chọn / Đánh đổi:** <Vì sao cách này an toàn và gọn nhất>

## 5. Câu hỏi cần chốt (Nếu có)
- <Bỏ trống hoặc ghi "Không" nếu đã đủ thông tin để lập Plan>
````

---

## 2. Khuôn mẫu `02-plan.md` (Bước 2 & 3: Lập Plan, Duyệt chéo & Chạy Plan)

Đặt tại: `tech_docs/plans/<slug>/02-plan.md`
*(Nếu dùng chế độ **Fast-Track** cho task nhỏ, gộp thêm mục "Hiện trạng & Nguyên nhân gốc (`file:line`)" vào ngay mục 1).*

````markdown
# 02 — Kế hoạch & Thực thi: <Tên tính năng / lỗi>

**Ngày:** YYYY-MM-DD · **Phía:** <BE | FE | Cả hai>
**Người lập Plan:** <Gemini | Claude> · **Người duyệt Plan:** <Claude | Gemini>
**Người chạy Plan:** <Gemini | Claude | Chưa chạy> · **Trạng thái:** <DRAFT | APPROVED | IN_PROGRESS | VERIFIED>

## 1. Bối cảnh & Quyết định đã chốt
- **Tóm tắt bài toán:** <2–3 dòng tóm tắt nguyên nhân gốc và mục tiêu, kèm `file:line` chính>
- **Quyết định kỹ thuật đã chốt (Bất biến khi thi công):**
  1. <Quyết định 1>
  2. <Quyết định 2>

## 2. Cấu trúc File thay đổi

| Phía | File (tính từ gốc `backend/` hoặc `frontend/`) | Thao tác (`Sửa` / `Tạo` / `Xoá`) | Trách nhiệm / Nội dung thay đổi |
|---|---|---|---|
| BE | `services/api/src/bookforge_api/...` | Sửa | <Mô tả 1 dòng> |
| FE | `src/components/...` | Sửa | <Mô tả 1 dòng> |

## 3. Các bước thực thi (Implementation Steps)

### Step 1: <Tên bước 1 — VD: Cập nhật logic xử lý ở Backend>
- [ ] **Trạng thái thực thi**
- **File:** `<đường_dẫn_file>:<dòng>`
- **Chi tiết thay đổi:**
  - <Hàm/biến nào cần sửa, đầu vào/đầu ra, cách xử lý edge-case>
- **Kiểm tra nhanh:** `<lệnh chạy kiểm tra bước này>`

### Step 2: <Tên bước 2 — VD: Cập nhật giao diện / extension ở Frontend>
- [ ] **Trạng thái thực thi**
- **File:** `<đường_dẫn_file>:<dòng>`
- **Chi tiết thay đổi:**
  - <Mô tả cụ thể thay đổi>
- **Kiểm tra nhanh:** `<lệnh chạy kiểm tra bước này>`

### Step 3: <Tên bước 3 — VD: Bổ sung / Cập nhật Unit & Integration Tests>
- [ ] **Trạng thái thực thi**
- **File:** `<đường_dẫn_file_test>`
- **Kịch bản test:**
  1. <Trường hợp chuẩn (happy path)>
  2. <Trường hợp biên / lỗi (edge case)>

## 4. Điều kiện Nghiệm thu (DoD)

### 4.1 Tự kiểm bằng máy (Agent chạy & tick sau khi có output thật)
- [ ] Linter & Format xanh: `uv run --directory backend/services/api ruff check . && uv run --directory backend/services/api ruff format --check .` (nếu đụng BE)
- [ ] Test tự động xanh: `<lệnh pytest hoặc test FE cụ thể>`
- [ ] Build / Typecheck FE không lỗi (nếu đụng FE)
- [ ] Không có file thừa hoặc vượt giới hạn dòng quy định (`frontend/CONVENTION.md` ≤ 300 dòng/file)

### 4.2 Kiểm tay trên giao diện (Dành cho người dùng)
- [ ] `(kiểm tay)` <Bước thao tác cụ thể trên màn hình → Kết quả kỳ vọng nhìn thấy>

---

## 5. Nhật ký Duyệt Plan (Cross-Review bởi <Claude | Gemini>)
- **Ngày duyệt:** YYYY-MM-DD
- **Đối chiếu code thật:** <Đã mở những file nào để xác nhận>
- **Phát hiện & Phản biện:**
  - 🔴 **[Blocker]** <Không có / Hoặc nêu rõ chỗ sai kèm `file:line` và cách sửa>
  - 🟡 **[Should-fix]** <Không có / Hoặc đề xuất cải thiện>
  - 🟢 **[Nit]** <Không có / Hoặc góp ý nhỏ>
- **Kết luận Duyệt Plan:** `APPROVED` | `CHANGES REQUESTED`
- **Cập nhật sau Review:** <Ghi ngắn gọn đã chỉnh lại mục nào trong Plan theo góp ý>

---

## 6. Nhật ký Thực thi & Quyết định phát sinh (Ghi khi Chạy Plan)
- **Môi trường / Migration DB:** <Trạng thái kiểm tra trước khi chạy>
- **Quyết định phát sinh (nếu có):** <Ghi lại nếu thực tế lúc code cần điều chỉnh nhỏ>
- **Kết quả chạy lệnh kiểm tra (tóm tắt output):**
  - `<lệnh 1>` → `<kết quả>`

---

## 7. Kết quả Nghiệm thu Code (Cross-Verify bởi <Gemini | Claude>)
- **Ngày nghiệm thu:** YYYY-MM-DD
- **Đối chiếu `git status` / `git diff`:** <Khớp phạm vi Plan hay có điểm lệch?>
- **Kiểm chứng test độc lập:** <Kết quả chạy lại test/lint>
- **Nhận xét chất lượng code:** <Đánh giá ngắn gọn>
- **Kết luận cuối cùng:** `VERIFIED (Sẵn sàng Commit)` | `NEEDS FIX`
````

---

## 3. Khuôn mẫu Xuất Task Doc vào Repo Backend (Tuỳ chọn)

Chỉ dùng khi người dùng yêu cầu lưu task spec vào `backend/docs/tasks/YYYY-MM-DD-<slug>[-frontend].md`.
> **⚠️ Ràng buộc bắt buộc:** Tuyệt đối không chứa chuỗi `tech_docs` hay nhắc tên `01-analysis.md`, `02-plan.md` trong file này.

````markdown
# Task — <Mô tả việc, tiếng Việt>

**Ngày:** YYYY-MM-DD
**Loại:** forward spec
**Repo triển khai:** <bookforge | bookforge-fe>

> **Cách đọc tài liệu này:** Đọc mục "Quyết định đã chốt" trước khi sửa code. Hoàn thành tới đâu tick `- [x]` vào mục "DoD" tới đó.

## Bối cảnh
<Tóm tắt vấn đề và nguyên nhân gốc kèm `file:line`>

## Phạm vi / Ngoài phạm vi
- **Trong phạm vi:** ...
- **Ngoài phạm vi:** ...

## Quyết định đã chốt
1. ...

## Việc cần làm
### 1. <Hạng mục 1>
- **Vị trí:** `<file:line>`
- **Thay đổi:** ...

## DoD — hoàn thành khi
- [ ] ...
- [ ] `(kiểm tay)` ...

## Tham chiếu nhanh các file
- `<đường dẫn tương đối trong repo>` — <vai trò>
````

