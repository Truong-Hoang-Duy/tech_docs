# [Tên Project / Feature]

> **📌 Cách dùng file này:** Đính kèm file template này vào đầu cuộc trò chuyện, sau đó mô tả feature/project bạn cần viết tài liệu. Claude sẽ dựa vào khung này để soạn báo cáo kỹ thuật hoàn chỉnh.
>
> **📌 Hướng dẫn cho Claude khi dùng template này:**
> - Đây là khung tham khảo, **không phải form bắt buộc điền đủ 100%**. Bỏ mục không liên quan, thêm mục cần thiết mà template chưa có.
> - Không cần giữ nguyên thứ tự/tên mục nếu ngữ cảnh dự án hợp lý hơn với cách trình bày khác.
> - Ưu tiên nội dung **cụ thể, có thể hành động được** hơn là làm đầy đủ hình thức. Tránh câu chung chung kiểu "cải thiện hiệu năng" — hãy hỏi lại số liệu cụ thể nếu cần.
> - Nếu thiếu thông tin quan trọng để viết một mục (VD: chưa rõ data model, chưa rõ constraint hạ tầng), **hỏi lại người dùng** thay vì tự suy đoán hoặc bịa ra.
> - Với project nhỏ (script, fix nhỏ, prototype), có thể rút gọn chỉ còn Overview + Requirements + Technical Design + Implementation Plan.
> - Giữ văn phong ngắn gọn, dùng bullet point nhiều hơn đoạn văn dài; chỉ viết văn xuôi khi cần giải thích logic phức tạp.

---

## 1. Tổng quan (Overview)

- **Tên:**
- **Trạng thái:** Draft / In Review / Approved
- **Tác giả:**
- **Ngày cập nhật:**
- **Tóm tắt:** *2–3 câu mô tả đây là gì, giải quyết vấn đề gì.*

## 2. Bối cảnh & Vấn đề (Context & Problem)

*Hiện trạng đang thế nào, pain point là gì, tại sao cần làm bây giờ.*

## 3. Mục tiêu & Non-goals

- **Mục tiêu:** *Kết quả cụ thể cần đạt được.*
- **Non-goals:** *Những gì KHÔNG nằm trong phạm vi lần này — tránh scope creep.*

## 4. Yêu cầu (Requirements)

### Functional
- *Hệ thống phải làm được gì.*

### Non-functional
- *Performance, security, scalability, khả năng bảo trì...*

### Constraints
- *Giới hạn về công nghệ, thời gian, ngân sách, hạ tầng sẵn có.*

## 5. Thiết kế kỹ thuật (Technical Design)

### Kiến trúc tổng thể
*Có thể mô tả bằng sơ đồ (mermaid/ASCII) hoặc bullet mô tả luồng component.*

### Data model / Schema
*Nếu có DB: bảng, field, quan hệ.*

### API design
*Endpoint, method, request/response format (nếu có).*

### Luồng xử lý chính
*Sequence các bước xử lý cho case chính.*

## 6. Lựa chọn thay thế đã cân nhắc (Alternatives Considered)

- *Phương án khác đã nghĩ tới, vì sao không chọn.*

## 7. Rủi ro & Đánh đổi (Risks & Trade-offs)

- *Rủi ro kỹ thuật, edge case, trade-off giữa các lựa chọn.*

## 8. Kế hoạch triển khai (Implementation Plan)

- [ ] *Task 1*
- [ ] *Task 2*
- [ ] *Task 3*

*Ưu tiên theo thứ tự, có thể chia milestone nếu project lớn.*

## 9. Testing & Rollout

- **Cách test:** *unit / integration / manual...*
- **Kế hoạch deploy:** 
- **Rollback plan (nếu có sự cố):**

## 10. Câu hỏi mở (Open Questions)

- *Những điểm chưa chốt, cần xác nhận thêm trước khi code.*
