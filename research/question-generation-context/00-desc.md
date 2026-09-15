# 00 — Mô tả: Ô nhập ngữ cảnh khi tạo câu hỏi trong thư mục câu hỏi

**Phía:** cả hai

## Người dùng muốn gì

Người dùng đang ở **Ngân hàng câu hỏi → một thư mục câu hỏi**, định bấm nút tạo câu hỏi mới.
Họ muốn có thêm **một ô nhập ngữ cảnh** để tự mô tả mình cần câu hỏi thế nào, rồi câu hỏi được tạo ra bám theo mô tả đó.

Ví dụ nội dung người dùng sẽ gõ vào ô:

```text
Bạn là giáo viên dạy toán lớp 10, hãy giúp tôi tạo 10 câu hỏi trắc nghiệm
chủ đề phương pháp tọa độ trong không gian, mức độ dễ,
bám sát chương trình sách giáo khoa mới 2025.
```

## Hôm nay đang ra sao

Ở màn hình tạo câu hỏi hàng loạt trong thư mục câu hỏi, **không có ô nhập ngữ cảnh**. Người dùng chỉ có 3 nút (ô chọn Loại câu hỏi):

1. Tạo câu hỏi tự luận
2. Tạo câu hỏi trắc nghiệm
3. Tạo câu hỏi điền vào chỗ trống (Trả lời ngắn)

Vì vậy người dùng không truyền được ý muốn của mình (chủ đề, lớp, mức độ, số lượng, chương trình…) để điều chỉnh câu hỏi được tạo ra.

## Ràng buộc

Chưa ghi.

## Không làm lần này

Chưa ghi — nên bổ sung trước khi sang khảo sát, để phạm vi không phình.

## Chỗ tôi không chắc

- Mô tả hiện trạng ở trên (đúng màn hình nào, có đúng 3 nút đó không) chưa chắc đã chính xác — cần đối chiếu với màn hình thật.
- Tên tính năng nói "Tạo câu hỏi mới", phần hiện trạng lại nói "tạo câu hỏi hàng loạt" — hai cái là một hay là hai chỗ khác nhau?
- Ô ngữ cảnh là **một ô dùng chung** cho cả 3 nút, hay mỗi dạng câu hỏi có ô riêng?
- Nếu người dùng ghi dạng câu hỏi ngay trong ngữ cảnh (ví dụ ghi "trắc nghiệm") nhưng lại bấm nút "Tạo câu hỏi tự luận", thì theo cái nào?
- Hôm nay khi bấm 1 trong 3 nút, câu hỏi được tạo dựa trên cái gì (tài liệu trong thư mục, thiết lập nào khác)? Ngữ cảnh mới sẽ **thêm vào** cái đó hay **thay thế** nó?
- Nếu ngữ cảnh có nói đến 1 trong các ô chọn (ví dụ thang Bloom, hoặc mức độ nhận thức), thì tạo sinh câu hỏi vẫn cần tuân thủ theo phần đã chọn ở các ô chọn hiện tại được không?