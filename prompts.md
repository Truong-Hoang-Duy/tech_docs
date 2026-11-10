# Câu lệnh mẫu

Copy câu lệnh, điền các chỗ `<...>`, rồi dán vào khung chat. Trong lúc đang làm, bạn chỉ cần nhắn trả lời tự nhiên bằng lời thường (không cần copy câu lệnh phụ).

---

## 1. Bắt đầu công việc (Dùng cho cả 4 cách làm)

```text
Đọc tech_docs/README.md. Lấy code mới nhất (Phần I.3), chưa sửa code, tìm hiểu các file:dòng liên quan đến yêu cầu bên dưới.
- Nếu tôi để trống "Cách làm": tóm tắt ngắn hiện trạng và khuyên tôi nên chọn cách nào trong 4 cách ở README Phần II ("Chỉ hỏi", "Làm nhanh", "Việc thường", hoặc "Việc có spec"), rồi chờ tôi chốt.
- Khi đã có "Cách làm", thực hiện đúng quy trình của cách đó ở README Phần III:
  + Chỉ hỏi (Cách 1): trả lời ngắn gọn luồng giao diện → backend → dữ liệu (kèm file:dòng), phân quyền/cờ khoá và chỗ dễ lỗi ngay trong chat; không tạo file.
  + Làm nhanh (Cách 2): làm đúng 4 bước của Cách 2 ngay trong phiên này (tạo nhánh từ dev → sửa code tổng quát không gài ví dụ test vào prompt/code + chủ động suy luận test thêm cả logic Backend lẫn giao diện/ký hiệu toán học/kịch bản biên + viết/chạy test → tự tạo dữ liệu nền & tự bấm thử → gửi hướng dẫn kiểm tay trên UI hoàn chỉnh theo checklist 4 mục ở Phần I.4 → chờ tôi báo OK rồi hỏi commit + push nhánh và merge vào dev); không tạo file trong tech_docs/tasks/.
  + Việc thường (Cách 3): đọc thêm tech_docs/templates.md, thực hiện Giai đoạn 1 (tạo tech_docs/tasks/<slug>/analysis.md và báo tôi mục 0 kèm các điều cần quyết; khi tôi nhắn chốt trong chat thì lập luôn plan.md, tự kiểm 4 điều và chốt APPROVED).
  + Việc có spec (Cách 4): hỏi tôi đường dẫn spec (nếu chưa có). Khi tôi nhắn đường dẫn vào phiên chat, ghi ngay vào hồ sơ (`analysis.md`, `plan.md`) để mọi bước sau tự động hiểu ngữ cảnh; đọc thêm tech_docs/spec-check.md và tech_docs/templates.md, thực hiện Giai đoạn 1 (kiểm 3 lớp vào analysis.md, báo tôi mục 0 kèm các điều cần quyết; khi tôi nhắn chốt trong chat thì lập luôn plan.md, tự kiểm 4 điều và chốt APPROVED).

Yêu cầu: <mô tả việc cần làm, lỗi cần sửa, hoặc câu hỏi>
Cách làm (tuỳ chọn): <để trống để AI khuyên | Chỉ hỏi | Làm nhanh | Việc thường | Việc có spec>
```

---

## 2. Code, Kiểm thử & Hoàn tất (Chỉ dùng cho Cách 3 & Cách 4 — mở phiên chat mới khi `plan.md` đã `APPROVED`)

```text
Đọc tech_docs/README.md và hồ sơ trong tech_docs/tasks/<slug>/ (plan.md đã APPROVED).
Thực hiện Giai đoạn 2 (Code & Hoàn tất) theo đúng README Phần III:
1. Tạo nhánh từ dev mới nhất theo README Phần I.3.
2. Làm lần lượt từ đầu đến hết tất cả các Task trong plan.md (không dừng chờ kiểm tay ở từng Task): với mỗi Task, sửa code tổng quát (không gài cứng kịch bản test vào prompt/code) → viết/chạy test → chủ động suy luận thêm nhiều trường hợp để tự test và bấm thử cả về logic Backend lẫn giao diện hiển thị (theo Phần I.4: dữ liệu biên, đồng bộ các luồng, bố cục hợp lý chưa, có lỗi ký hiệu toán học/định dạng không...) → ghi kết quả vào Nhật ký và đánh dấu [x] trong plan.md rồi sang Task tiếp theo.
3. Khi đã xong hết tất cả các Task: tự đọc lại diff, chạy toàn bộ kiểm tra như CI (nghiệm thu), tự tạo sẵn dữ liệu nền và viết hướng dẫn kiểm tra tay trên UI hoàn chỉnh ngay trong phiên chat (test hết các chức năng, logic, giao diện hiển thị, ký hiệu toán học và kịch bản biên theo checklist 4 mục ở Phần I.4, tách rõ phần cố định 100% và phần văn bản do LLM sinh tương đối).
4. Chờ tôi xác nhận kiểm tay OK: đổi trạng thái plan.md sang VERIFIED; ở Cách 3 thì hỏi tôi muốn tạo plan, spec hay cả 2 và lưu ở thư mục nào trong backend/ (tôi xác nhận mới tạo), còn ở Cách 4 thì cập nhật file spec gốc; cuối cùng hỏi tôi có đồng ý commit + push nhánh và merge vào dev không.

Slug công việc (hoặc để trống nếu chỉ có 1 việc đang APPROVED): <tên slug>
```

---

## 3. Cứu hộ (Khi mất phiên chat hoặc hôm sau làm tiếp Cách 3 / Cách 4)

```text
Đọc tech_docs/README.md và các file trong tech_docs/tasks/<slug>/, kiểm tra git status và git log gần đây ở backend/ và frontend/, rồi tóm tắt trong 5 dòng: đang ở giai đoạn/Task nào, đã xong gì, việc tiếp theo cần làm ngay là gì.
```
