# Khung tài liệu (Chỉ dùng cho Cách 3: Việc thường & Cách 4: Việc có spec)

> **Ranh giới áp dụng:** File này **chỉ dùng cho Cách 3 (Việc thường) và Cách 4 (Việc có spec)** trong [`README.md`](README.md). **Cách 1 (Chỉ hỏi)** và **Cách 2 (Làm nhanh)** không tạo bất kỳ file nào trong `tech_docs/tasks/`.

Viết bằng **tiếng Việt**, ngắn gọn, giữ nguyên tên hàm / biến / đường dẫn trong dấu `` ` ``. Mục nào không có nội dung thì ghi "Không có".

Hồ sơ của một việc nằm trong `tech_docs/tasks/<slug>/`:
1. [`analysis.md`](#1-analysismd--tìm-hiểu) — tìm hiểu
2. [`plan.md`](#2-planmd--kế-hoạch-và-hồ-sơ) — kế hoạch và hồ sơ

*(Hướng dẫn kiểm tay gửi trực tiếp trong phiên chat theo `README.md` Phần I.4, không tạo file riêng).*

**Cách 3 (Việc thường)** ở cuối Giai đoạn 2 sẽ hỏi bạn muốn tạo **plan**, **spec** hay **cả 2** và lưu ở thư mục nào trong `backend/` (bạn xác nhận mới tạo; xem khung ở [mục 3](#3-tài-liệu-lưu-trong-backend)). Còn **Cách 4** thì cập nhật vào file spec có sẵn theo [`spec-check.md`](spec-check.md).

---

## 1. `analysis.md` — Tìm hiểu

**Mục 0 viết cho người không đọc code**, tối đa một trang: không tên file, tên hàm, thuật ngữ lập trình (bắt buộc dùng thì giải thích trong ngoặc); câu ngắn, theo góc nhìn người dùng. Phần kỹ thuật chỉ ghi điều phục vụ kế hoạch.

````markdown
# Tìm hiểu: <tên việc>

**Ngày:** YYYY-MM-DD · **Cách làm:** <Cách 3: Việc thường | Cách 4: Việc có spec> · **Phía:** <BE | FE | Cả hai>
**Mốc code:** backend `<mã commit>` · frontend `<mã commit>`
**Spec (nếu có):** `<đường dẫn>`

## 0. Việc này sẽ làm gì
**Để làm gì:** <1–2 câu>

**Làm xong, ai sẽ thấy gì khác:**
| Vai trò | Trước đây | Sau khi làm |
|---|---|---|

**Lần này không làm:** <…>

**Người dùng và dữ liệu đang có bị ảnh hưởng:** <… hoặc "Không">

**Bạn cần quyết:**
1. **Tình huống:** <mô tả bằng lời người dùng>
   - (a) <lựa chọn> → <sẽ ra sao>
   - (b) <lựa chọn> → <sẽ ra sao>
   - **AI khuyên:** <a / b, vì …> · **Bạn chốt:** <…>

**Làm xong, bạn sẽ thấy nó chạy thế nào:** <bấm gì, thấy gì>

**So với nghiệp vụ đã có:** Giữ: <…> · Đổi: <…> · Thêm: <…>

---
*(Từ mục 1 trở xuống là phần kỹ thuật cho agent.)*

## 1. Mục tiêu và phạm vi
- **Cần đạt:** <1–3 ý>
- **Không làm:** <phần cắt bỏ>

## 2. Hiện trạng (kèm `file:dòng`)
- **Luồng hiện tại:** <từ điểm đầu đến điểm cuối>
- **Chỗ cần sửa / nguyên nhân:** `<file>:<dòng>` — <giải thích>, trích code nếu cần (≤ 15 dòng)

## 3. Kiểm tra spec (chỉ việc có spec, xem `spec-check.md`; việc khác ghi "Không áp dụng")
### 3.0. Nghiệp vụ
**Nguồn đã đọc:** <spec; thêm tài liệu gốc nếu có>
| # | Nghiệp vụ (ai, làm gì, tình huống, kết quả) | Nguồn | So với đang chạy | Loại (Giữ nguyên / Làm rõ / Mở rộng – Đổi) | Bạn chốt |
|---|---|---|---|---|---|

### 3a. Chỗ spec khác code thật
| Spec ghi | Code thật (`file:dòng`) | Cách chỉnh trong kế hoạch |
|---|---|---|

### 3b. Vấn đề của spec
| Mục trong spec | Vấn đề | Mức (🔴 / 🟡 / 🟢) | Đề xuất | Bạn chốt |
|---|---|---|---|---|

## 4. Điểm va chạm
<Dữ liệu · giao tiếp backend ↔ frontend · phân quyền · quy ước code · test đang khoá hành vi cũ>

## 5. Phương án đề xuất
<Nếu có 2 hướng: được – mất của từng hướng và khuyến nghị. Nếu đã rõ: trình bày thẳng.>

## 6. Câu hỏi kỹ thuật còn mở
<Câu nào cần bạn quyết thì đưa lên mục 0 dưới dạng tình huống.>
````

---

## 2. `plan.md` — Kế hoạch và hồ sơ

Chỉ nằm trong `tech_docs`, không chép sang `backend/`. Kế hoạch chỉ ghi quyết định, file, tiêu chí và lệnh kiểm tra, không viết sẵn code.

````markdown
# Kế hoạch: <tên việc>

**Ngày:** YYYY-MM-DD · **Cách làm:** <Cách 3: Việc thường | Cách 4: Việc có spec> · **Phía:** <BE | FE | Cả hai>
**Trạng thái:** <DRAFT | APPROVED | IN_PROGRESS | NEEDS_FIX | VERIFIED | COMMITTED>
**Mốc code:** backend `<mã commit>` · frontend `<mã commit>` · **Nhánh:** `feat/<slug>`

## 1. Mục tiêu và quyết định đã chốt
- **Mục tiêu:** <2–3 dòng>
- **Quyết định đã chốt** (không tự đổi khi làm):
  1. <…>
- **Tài liệu trong `backend/`:** `<đường dẫn>` (Cách 3: chốt khi hoàn tất · Cách 4: đường dẫn spec gốc)

## 2. Các Task (làm liền mạch hết các Task rồi mới kiểm tay tổng thể trên UI)
### Task 1: <phần chức năng, nói theo góc nhìn người dùng>
- [ ] **Xong (AI đã tự test & bấm thử)**
- **Thao tác tự kiểm:** <đi tới đâu, bấm gì hoặc gọi API gì để kiểm>
- **✅ Đúng khi thấy:** <tách rõ: (1) Phần cố định/cấu trúc phải khớp 100% (trạng thái UI, nhãn, định dạng, công thức toán học); (2) Phần câu chữ do LLM sinh đối chiếu tương đối theo ý nghĩa & quy tắc>
- **❌ Sai nếu thấy:** <dấu hiệu lỗi>
- **Điểm suy luận tự test thêm:** <logic backend, dữ liệu biên, đồng bộ các luồng, bố cục giao diện hợp lý chưa, hiển thị ký hiệu toán học/định dạng, câu thử biến thiên không trùng ví dụ trong prompt...>
- **Kiểm tra tự động:** `<lệnh>` (việc có spec: viết test → thấy hỏng → viết code → thấy đúng)
- **File và thay đổi:** `<file>:<dòng>` — <làm gì, xử lý trường hợp biên nào>

## 3. Điều kiện hoàn thành
- [ ] Toàn bộ kiểm tra như CI đều đúng: `<các lệnh lấy từ file CI>`
- [ ] <tiêu chí riêng của việc này>

## 4. Kiểm kế hoạch
- **`file:dòng`, tên hàm có thật:** <đã kiểm / đã sửa gì>
- **Lệnh kiểm tra chạy được:** <đã chạy>
- **Mục tiêu, nghiệp vụ, điều đã chốt đều có Task:** <đủ / đã bổ sung gì>
- **Mọi Task có tiêu chí:** <đủ>
- **Cần bạn quyết:** <Không có / tình huống, các lựa chọn, AI khuyên gì>

## 5. Nhật ký làm
- **Kiểm tra trước khi sửa** (để phân biệt lỗi có sẵn): `<lệnh>` → `<dòng kết quả cuối>`
- **Quyết định phát sinh:** <…>
- **Kết quả từng Task:** `<lệnh đã chạy>` → `<dòng kết quả cuối>`

## 6. Nghiệm thu
- **Ngày:** YYYY-MM-DD
- **Thay đổi so với kế hoạch:** <khớp / lệch chỗ nào>
- **Từng nghiệp vụ (`analysis.md` mục 3.0, nếu có):** <đạt hết / chưa đạt: …>
- **Chạy lại toàn bộ kiểm tra:** `<lệnh>` → `<kết quả>`
- **Không lọt chữ `tech_docs` vào backend / frontend:** <đã kiểm>
- **Kết luận:** `VERIFIED` | `NEEDS_FIX` (kèm `file:dòng` cần sửa)

## 7. Kiểm tay (Trên UI hoàn chỉnh sau khi xong hết các Task)
- **Kết quả:** <Đạt hết / còn kịch bản nào chưa đạt> (hướng dẫn kiểm tra toàn bộ chức năng, logic, giao diện, ký hiệu toán học và kịch bản biên trực tiếp trong phiên chat)

## 8. Commit
- **Tài liệu trong `backend/`:** `<đường dẫn>` — <Cách 3: tạo mới plan / spec / cả 2 / không tạo | Cách 4: các chỗ đã sửa trong spec>
- **Mã commit:** backend `<…>` · frontend `<…>` · **Đã push và merge `dev`:** <có / chưa>

## 9. Việc còn treo
- <Hoặc "Không có">

## 10. Số đo
- **Bắt đầu:** YYYY-MM-DD · **Merge:** YYYY-MM-DD
- **Số lỗi bạn bắt được khi kiểm tay:** <số>
- **Số lần phải sửa sau merge:** <số, điền khi xem lại luật>
````

---

## 3. Tài liệu lưu trong `backend/` (Khi hoàn tất Cách 3 — theo xác nhận của bạn)

Chỉ tạo khi bạn xác nhận loại tài liệu (**plan**, **spec** hoặc **cả 2**) và **thư mục lưu** (ví dụ `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`, `backend/docs/superpowers/specs/YYYY-MM-DD-<slug>.md` hoặc thư mục bạn chọn). Chỉ ghi điều code không tự nói được; ghi đúng những gì đã làm thật. **Không** nhắc `tech_docs`, `analysis.md`, `plan.md`.

````markdown
# <Tên việc>

**Trạng thái:** đã làm xong YYYY-MM-DD · **Phía:** <BE | FE | Cả hai> · **Code chính:** `<đường dẫn>`

## 1. Nghiệp vụ và mục đích
<Vì sao cần làm việc này, ai dùng, trong tình huống nào>

## 2. Ai thấy gì khác
| Vai trò | Trước đây | Sau khi làm |
|---|---|---|

**Dữ liệu đang có bị ảnh hưởng:** <… | Không>

## 3. Quyết định đã chốt
| Quyết định | Lý do | Cách đã cân nhắc nhưng không chọn | Ai chốt |
|---|---|---|---|

## 4. Cố ý chưa làm
<Điều gì, vì sao, để lại cho việc nào | Không có>

## 5. Cách kiểm
<Tiêu chí đúng và cách kiểm ngắn gọn>
````
