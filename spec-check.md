# Kiểm và cập nhật spec (Chỉ dùng cho Cách 4: Việc có spec)

> **Ranh giới áp dụng:** File này **chỉ dùng cho Cách 4 (Việc có spec)** trong [`README.md`](README.md). **Cách 1 (Chỉ hỏi)**, **Cách 2 (Làm nhanh)** và **Cách 3 (Việc thường)** không dùng file này.

**Nguyên tắc:**
- Khi bạn nhắn đường dẫn spec vào phiên chat ở Giai đoạn 1, AI ghi ngay đường dẫn đó vào đầu `analysis.md` và `plan.md`; từ đó ở mọi bước sau AI tự động lấy đường dẫn spec và ngữ cảnh từ hồ sơ mà không hỏi lại bạn.
- Spec do người khác viết nên **mặc định làm theo**. AI **không tự sửa file spec** khi đang tìm hiểu và code, và **không tự làm khác spec**. Chỗ nghi sai hoặc không làm được thì ghi ra, phân mức để **bạn chốt**. Mọi chỗ làm khác spec phải ghi vào "Quyết định đã chốt" của `plan.md`, kèm lý do và ai đồng ý. Khi hoàn tất ở cuối Giai đoạn 2, những chỗ đã chốt được sửa vào file spec (mục 4).

## 1. Giai đoạn 1 (Tìm hiểu): kiểm theo 3 lớp, đúng thứ tự

**Lớp 1 — Nghiệp vụ** (ghi vào mục 3.0 của `analysis.md`):
- **Nguồn nghiệp vụ:** thường chỉ có spec. Spec dẫn tới tài liệu gốc, hoặc bạn đưa thêm tài liệu thì đọc cả những tài liệu đó. Không tự suy thêm nghiệp vụ ngoài các nguồn này.
- Liệt kê **từng nghiệp vụ** bằng lời thường: ai, làm gì, trong tình huống nào, kết quả ra sao.
- So với **nghiệp vụ đang chạy** (đọc code để biết, trả lời bằng lời nghiệp vụ): chức năng nào đổi hành vi · vai trò nào mất hoặc thêm quyền · mỗi vai trò có còn làm được việc chính không · có mâu thuẫn với nghiệp vụ đang có hoặc gói trước không.
- Xếp mỗi nghiệp vụ vào một loại:

| Loại | Nghĩa | Cách xử lý |
|---|---|---|
| **Giữ nguyên** | Đúng như nguồn nghiệp vụ và không đổi điều đang chạy | Làm theo |
| **Làm rõ** | Nguồn chưa nói chi tiết, cần bổ sung để làm được | AI đề xuất, ghi lại để bạn biết |
| **Mở rộng / Đổi** | Thêm hoặc đổi điều nguồn chưa có, hoặc đổi nghiệp vụ đang chạy | Chỉ làm khi cần thiết và bạn đã chốt |

- Nguồn nghiệp vụ mâu thuẫn nhau, hoặc mâu thuẫn với điều đang chạy → AI không tự chọn, đưa lên "Bạn cần quyết".

**Lớp 2 — Spec có làm được không** (ghi vào mục 3b):
1. Tiêu chí nghiệm thu có đạt được **trong gói này** không, hay phụ thuộc gói khác?
2. Có tự mâu thuẫn, hoặc mâu thuẫn với spec / quyết định khác không?
3. Có làm hỏng chức năng đang chạy không?
4. Có bỏ sót trường hợp quan trọng không (dữ liệu cũ, người không có quyền, lỗi giữa chừng)?
5. Cách kiểm chứng spec đề ra có chạy được thật không?
6. Chỗ nào viết mơ hồ, hiểu được nhiều cách?
7. Có rủi ro về an toàn dữ liệu, bảo mật không?

**Lớp 3 — Spec còn khớp code không** (ghi vào mục 3a): tên file, số thứ tự, tên hàm, cấu trúc dữ liệu spec nhắc tới có còn đúng không. Chỉnh thuần kỹ thuật thì không đưa lên phần bạn đọc; nếu làm đổi nghiệp vụ thì đưa lên "Bạn cần quyết".

## 2. Phân mức vấn đề của spec

| Mức | Nghĩa | AI làm gì |
|---|---|---|
| 🔴 | Không làm được, hoặc sai rõ ràng | **Dừng**, hỏi bạn trước khi lập kế hoạch |
| 🟡 | Làm được nhưng nên điều chỉnh | Đề xuất cách chỉnh, bạn chốt |
| 🟢 | Chưa rõ nhưng nhỏ | Chọn cách hợp lý nhất, ghi lại để bạn biết |

Mọi nghiệp vụ loại **Mở rộng / Đổi** và mọi điểm 🔴 / 🟡 cần chốt đều phải đưa lên "Bạn cần quyết" ở mục 0.

## 3. Khi lập kế hoạch và code (Cuối Giai đoạn 1 & Giai đoạn 2)

- **Lập và kiểm `plan.md`:** từng nghiệp vụ ở mục 3.0 phải có Task tương ứng · chỗ làm khác spec đã được bạn chốt · mỗi Task làm theo thứ tự viết test → thấy test hỏng → viết code → thấy test đúng.
- **Nghiệm thu & Kiểm tay:** đối chiếu từng nghiệp vụ ở mục 3.0 và từng tiêu chí nghiệm thu của spec (chỉ đạt một phần thì ghi rõ và chuyển vào "Việc còn treo"). Kịch bản kiểm tay phủ các nghiệp vụ ở mục 3.0; loại **Mở rộng / Đổi** phải có kịch bản riêng.

## 4. Khi hoàn tất (Cuối Giai đoạn 2): cập nhật spec

Nếu chỉ kế hoạch ghi chỗ làm khác spec mà file spec để nguyên, người khác kiểm theo spec sẽ tưởng code sai.

- **Ở đâu:** spec đã nằm trong `backend/` thì sửa ngay trên file đó, không tạo bản thứ hai. Chưa nằm trong `backend/` (tài liệu rời, dán trong chat…) thì chép vào `backend/docs/superpowers/specs/YYYY-MM-DD-<slug>.md` rồi sửa.
- **Sửa gì:** (1) "Quyết định đã chốt" làm khác spec hoặc bổ sung điều spec chưa nói; (2) tham chiếu sai đã nêu ở mục 3a của `analysis.md`; (3) "Quyết định phát sinh" ở bước 4 có làm khác spec.
- **Không sửa gì khác:** giữ ngôn ngữ, định dạng, cách đánh số. Tiêu chí nghiệm thu chưa đạt thì **giữ nguyên**, chỉ ghi vào "Lịch sử thay đổi" là chưa đạt.
- **Không bao giờ sửa** văn bản gốc của PO (ví dụ `raw-extracts/`, `sources/`).
- **Ghi lại:** cuối spec thêm hoặc nối tiếp mục "Lịch sử thay đổi": ngày · `<slug>` · từng thay đổi kèm lý do · ai chốt. Không nhắc `tech_docs`, `analysis.md`, `plan.md`.
- **Spec khác bị ảnh hưởng:** liệt kê ra báo bạn, chỉ sửa khi bạn đồng ý.
