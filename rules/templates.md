# Khung tài liệu

Viết bằng **tiếng Việt**, ngắn gọn, giữ nguyên tên hàm / biến / đường dẫn trong dấu `` ` ``.
Tên file luôn bằng tiếng Anh. Các mục đánh số **cố định** — không đổi số khi bỏ trống một mục (ghi "Không có").

Ba file của một việc nằm trong `tech_docs/plans/<slug>/`:
1. [`01-analysis.md`](#1-01-analysismd--tìm-hiểu) — tìm hiểu
2. [`02-plan.md`](#2-02-planmd--kế-hoạch-và-hồ-sơ) — kế hoạch và hồ sơ
3. [`03-manual-test.md`](#3-03-manual-testmd--kiểm-tay) — kiểm tay

---

## 1. `01-analysis.md` — Tìm hiểu

*(Việc nhỏ bỏ file này, ghi hiện trạng vào mục 1 của `02-plan.md`.)*

````markdown
# Tìm hiểu: <tên việc>

**Ngày:** YYYY-MM-DD · **Người tìm hiểu:** <Gemini | Claude> · **Loại việc:** <thường | có spec> · **Phía:** <BE | FE | Cả hai>
**Mốc code:** backend `<mã commit>` · frontend `<mã commit>`
**Spec (nếu có):** `<đường dẫn>`

## 1. Mục tiêu và phạm vi
- **Cần đạt:** <1–3 ý>
- **Không làm:** <phần cắt bỏ>

## 2. Hiện trạng (kèm `file:dòng`)
- **Luồng hiện tại:** <từ điểm đầu đến điểm cuối>
- **Chỗ cần sửa / nguyên nhân:** `<file>:<dòng>` — <giải thích>, kèm trích code ngắn (≤ 15 dòng)

## 3. Kiểm tra spec (chỉ với việc có spec — xem README mục 3.1)
### 3a. Chỗ spec khác code thật
| Spec ghi | Code thật (`file:dòng`) | Cách chỉnh trong kế hoạch |
|---|---|---|

### 3b. Vấn đề của spec
| Mục trong spec | Vấn đề | Mức (🔴 / 🟡 / 🟢) | Đề xuất | Bạn chốt |
|---|---|---|---|---|

### 3c. Góp ý gửi người viết spec
<Đoạn ngắn bằng lời thường, liệt kê các điểm 🔴 / 🟡 để bạn chuyển cho người viết spec nếu cần. Hoặc "Không có">
*(Việc thường: ghi "Không áp dụng" cho cả mục 3.)*

## 4. Điểm va chạm
<Dữ liệu / cơ sở dữ liệu · giao tiếp backend ↔ frontend · phân quyền · quy ước code · test đang khoá hành vi cũ>

## 5. Phương án đề xuất
<Nếu có 2 hướng: Phương án A / B kèm được – mất, và khuyến nghị. Nếu đã rõ: trình bày thẳng.>

## 6. Câu hỏi cần bạn chốt
<Hoặc "Không có">
````

---

## 2. `02-plan.md` — Kế hoạch và hồ sơ

**Phần A** là phần sẽ được chép sang `backend/docs/superpowers/plans/` ở bước 7 → **không** nhắc `tech_docs` hay tên các file `01/02/03` trong Phần A.
**Phần B** là hồ sơ nội bộ, chỉ nằm trong `tech_docs`.

````markdown
# Kế hoạch: <tên việc>

**Ngày:** YYYY-MM-DD · **Loại việc:** <nhỏ | thường | có spec> · **Phía:** <BE | FE | Cả hai>
**Người lập:** <Gemini | Claude> · **Người duyệt:** <Claude | Gemini> · **Người làm:** <… | Chưa làm>
**Trạng thái:** <DRAFT | CHANGES_REQUESTED | APPROVED | IN_PROGRESS | NEEDS_FIX | VERIFIED | COMMITTED>
**Mốc code:** backend `<mã commit>` · frontend `<mã commit>` · **Nhánh:** `feat/<slug>`

---
# PHẦN A — KẾ HOẠCH (sẽ chép sang backend)

## 1. Mục tiêu và quyết định đã chốt
- **Mục tiêu:** <2–3 dòng>
- **Hiện trạng** (chỉ việc nhỏ): <nguyên nhân kèm `file:dòng`>
- **Quyết định đã chốt** (không tự đổi khi làm):
  1. <…>
- **Spec** (nếu có): `<đường dẫn trong repo backend>`

## 2. File thay đổi
| Phía | File | Tạo / Sửa / Xoá | Nội dung thay đổi |
|---|---|---|---|

## 3. Các bước thực hiện
### Bước 1: <tên bước>
- [ ] **Xong**
- **File:** `<file>:<dòng>`
- **Thay đổi:** <làm gì, xử lý trường hợp biên nào>
- **Kiểm tra nhanh:** `<lệnh>`

*(Việc có spec: thay các bước trên bằng dạng superpowers — xem cuối file này.)*

## 4. Điều kiện hoàn thành
- [ ] Toàn bộ kiểm tra tự động như CI đều chạy đúng: `<các lệnh lấy từ file CI>`
- [ ] <tiêu chí riêng của việc này>

---
# PHẦN B — HỒ SƠ NỘI BỘ (không chép)

## 5. Duyệt chéo (bởi <Claude | Gemini>)
- **Ngày:** YYYY-MM-DD · **Đã mở để đối chiếu:** <file nào>
- 🔴 **Blocker:** <Không có / chỗ sai kèm `file:dòng` và cách sửa>
- 🟡 **Should-fix:** <…>
- 🟢 **Nit:** <…>
- **Kết luận:** `APPROVED` | `CHANGES_REQUESTED`
- **Đã chỉnh trong kế hoạch:** <mục nào>

## 6. Nhật ký làm
- **Kiểm tra trước khi sửa** (để phân biệt lỗi có sẵn): `<lệnh>` → `<dòng kết quả cuối>`
- **Quyết định phát sinh:** <…>
- **Kết quả từng bước:** `<lệnh đã chạy>` → `<dòng kết quả cuối>`

## 7. Nghiệm thu chéo (bởi <Gemini | Claude>)
- **Ngày:** YYYY-MM-DD · **Nhánh đã cập nhật theo:** `origin/dev` @ `<mã commit>`
- **Thay đổi so với kế hoạch:** <khớp / lệch chỗ nào>
- **Chạy lại toàn bộ kiểm tra:** `<lệnh>` → `<kết quả>`
- **Không lọt chữ `tech_docs` vào backend / frontend:** <đã kiểm>
- **Kết luận:** `VERIFIED` | `NEEDS_FIX` (kèm `file:dòng` cần sửa)

## 8. Kiểm tay
- **Kết quả:** <Đạt hết / còn kịch bản nào chưa đạt> — chi tiết ở `03-manual-test.md`

## 9. Commit
- **Bản chép:** `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`
- **Mã commit:** backend `<…>` · frontend `<…>` · **Đã push:** <có / chưa>

## 10. Việc còn treo (chuyển cho việc sau)
- <Hoặc "Không có">
````

### Phần A dạng superpowers (dùng cho việc có spec)

Thay mục 3 của Phần A bằng khung sau, lặp lại cho từng Task:

````markdown
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

### Task <N>: <tên Task>

**Files:**
- Create / Modify: `<đường dẫn>`
- Test: `<đường dẫn file test>`

**Interfaces:**
- Consumes: <hàm / bảng / kiểu dữ liệu đang có mà Task này dùng>
- Produces: <hàm / bảng / kiểu dữ liệu mới Task này tạo ra>

- [ ] **Step 1: Viết test (chưa chạy được)** — <đoạn test cụ thể>
- [ ] **Step 2: Chạy test, thấy hỏng** — `<lệnh>` · Mong đợi: FAIL
- [ ] **Step 3: Viết code tối thiểu** — <thay đổi cụ thể>
- [ ] **Step 4: Chạy test và kiểm tra, thấy đúng** — `<lệnh>` · Mong đợi: PASS
````

---

## 3. `03-manual-test.md` — Kiểm tay

*(Chỉ nằm trong `tech_docs`, không chép sang backend.)*

````markdown
# Kiểm tay: <tên việc>

## Chuẩn bị
<Những gì cần có trước khi bắt đầu kiểm — AI tự điền theo từng việc>

## Kịch bản 1: <tên chức năng>
1. **Mở màn hình:** <đi tới đâu, thấy tiêu đề gì>
2. **Thao tác:** <bấm / điền / chọn / tải lên — theo đúng thứ tự và đúng chữ trên màn hình>
3. **✅ Đúng khi thấy:** <kết quả nhìn thấy được>
4. **❌ Sai nếu thấy:** <dấu hiệu lỗi>

Kết quả — AI: ☐ Đạt ☐ Không đạt · Bạn: ☐ Đạt ☐ Không đạt · Ghi chú: <…>

## Bảng kết quả
| Kịch bản | AI | Bạn | Ghi chú |
|---|---|---|---|

## Khi gặp lỗi
Báo: kịch bản nào, bước nào, thấy gì (kèm ảnh chụp nếu có).
````
