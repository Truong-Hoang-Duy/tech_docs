# Khung tài liệu

Viết bằng **tiếng Việt**, ngắn gọn, giữ nguyên tên hàm / biến / đường dẫn trong dấu `` ` ``. Mục nào không có nội dung thì ghi "Không có".

Hồ sơ của một việc nằm trong `tech_docs/tasks/<slug>/`:
1. [`analysis.md`](#1-analysismd--tìm-hiểu) — tìm hiểu (chỉ plan thì không có)
2. [`plan.md`](#2-planmd--kế-hoạch-và-hồ-sơ) — kế hoạch và hồ sơ
3. [`manual-test.md`](#3-manual-testmd--kiểm-tay) — kiểm tay

Việc chọn plan + spec tạo thêm [một spec ngắn trong `backend/`](#4-spec-ngắn-trong-backend) ở bước 7.

---

## 1. `analysis.md` — Tìm hiểu

**Mục 0 viết cho người không đọc code**, tối đa một trang: không tên file, tên hàm, thuật ngữ lập trình (bắt buộc dùng thì giải thích trong ngoặc); câu ngắn, theo góc nhìn người dùng. Phần kỹ thuật chỉ ghi điều phục vụ kế hoạch.

````markdown
# Tìm hiểu: <tên việc>

**Ngày:** YYYY-MM-DD · **Agent:** <Claude | Gemini> · **Cách làm:** <plan + spec | có spec> · **Phía:** <BE | FE | Cả hai>
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

**Ngày:** YYYY-MM-DD · **Cách làm:** <chỉ plan | plan + spec | có spec> · **Phía:** <BE | FE | Cả hai> · **Agent:** <Claude | Gemini>
**Trạng thái:** <DRAFT | APPROVED | IN_PROGRESS | NEEDS_FIX | VERIFIED | COMMITTED>
**Mốc code:** backend `<mã commit>` · frontend `<mã commit>` · **Nhánh:** `feat/<slug>`

## 1. Mục tiêu và quyết định đã chốt
- **Mục tiêu:** <2–3 dòng>
- **Hiện trạng** (chỉ khi không có `analysis.md`): <nguyên nhân kèm `file:dòng`>
- **Quyết định đã chốt** (không tự đổi khi làm):
  1. <…>
- **Spec trong backend:** `<đường dẫn>` (plan + spec: `docs/superpowers/specs/YYYY-MM-DD-<slug>.md`, tạo ở bước 7 · chỉ plan: "Không có")

## 2. Các Task (mỗi Task là một phần bạn bấm thử được)
### Task 1: <phần chức năng, nói theo góc nhìn người dùng>
- [ ] **Xong** · **Bạn đã kiểm:** <chưa | đạt>
- **Thao tác để kiểm:** <đi tới đâu, bấm gì; hoặc "Không bấm thử được" kèm lý do>
- **✅ Đúng khi thấy:** <kết quả nhìn thấy được>
- **❌ Sai nếu thấy:** <dấu hiệu lỗi>
- **Kiểm tra tự động:** `<lệnh>` (việc có spec: viết test → thấy hỏng → viết code → thấy đúng)
- **File và thay đổi:** `<file>:<dòng>` — <làm gì, xử lý trường hợp biên nào>

## 3. Điều kiện hoàn thành
- [ ] Toàn bộ kiểm tra như CI đều đúng: `<các lệnh lấy từ file CI>`
- [ ] <tiêu chí riêng của việc này>

## 4. Kiểm kế hoạch (bước 3)
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
- **Ngày:** YYYY-MM-DD · **Nhánh đã cập nhật theo:** `origin/dev` @ `<mã commit>`
- **Thay đổi so với kế hoạch:** <khớp / lệch chỗ nào>
- **Từng nghiệp vụ (`analysis.md` mục 3.0, nếu có):** <đạt hết / chưa đạt: …>
- **Chạy lại toàn bộ kiểm tra:** `<lệnh>` → `<kết quả>`
- **Không lọt chữ `tech_docs` vào backend / frontend:** <đã kiểm>
- **Kết luận:** `VERIFIED` | `NEEDS_FIX` (kèm `file:dòng` cần sửa)

## 7. Kiểm tay
- **Kết quả:** <Đạt hết / còn kịch bản nào chưa đạt> (chi tiết ở `manual-test.md`)

## 8. Commit
- **Spec trong backend:** `<đường dẫn>` — <plan + spec: tạo mới | có spec: các chỗ đã sửa | chỉ plan: "Không có">
- **Mã commit:** backend `<…>` · frontend `<…>` · **Đã push:** <có / chưa>

## 9. Việc còn treo
- <Hoặc "Không có">

## 10. Số đo
- **Bắt đầu:** YYYY-MM-DD · **Merge:** YYYY-MM-DD
- **Số lỗi bạn bắt được khi kiểm tay:** <số>
- **Số lần phải sửa sau merge:** <số, điền khi xem lại luật>
````

---

## 3. `manual-test.md` — Kiểm tay

Chỉ nằm trong `tech_docs`. Mỗi Task một kịch bản, **chép nguyên tiêu chí từ `plan.md`, không tự sửa**. Bước 6 thêm các kịch bản chung.

````markdown
# Kiểm tay: <tên việc>

## Chuẩn bị
<Những gì cần có trước khi kiểm>

## Kịch bản 1: <Task 1>
1. **Mở màn hình:** <đi tới đâu, thấy tiêu đề gì>
2. **Thao tác:** <bấm / điền / chọn / tải lên, đúng thứ tự và đúng chữ trên màn hình>
3. **✅ Đúng khi thấy:** <kết quả nhìn thấy được>
4. **❌ Sai nếu thấy:** <dấu hiệu lỗi>

Kết quả — AI: ☐ Đạt ☐ Không đạt · Bạn: ☐ Đạt ☐ Không đạt · Ghi chú: <…>

## Bảng kết quả
| Kịch bản | AI | Bạn | Ghi chú |
|---|---|---|---|
````

---

## 4. Spec ngắn trong `backend/`

Lưu ở `backend/docs/superpowers/specs/YYYY-MM-DD-<slug>.md`, khoảng một trang. Chỉ ghi điều code không tự nói được; ghi đúng những gì đã làm thật. **Không** nhắc `tech_docs`, `analysis.md`, `plan.md`, `manual-test.md`.

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
