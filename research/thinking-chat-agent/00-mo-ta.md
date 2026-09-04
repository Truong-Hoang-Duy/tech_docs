**Phía:** cả hai

## Người dùng muốn gì
Dự án hiện tại mỗi khi tạo canvas, chỉ phản hồi văn bản dựa trên câu lệnh ngay lập tức. 
Thay vì vậy, tôi muốn hệ thống Chat Agent tích hợp mô hình Thinking Chat Agent, 
cho phép người dùng theo dõi trực quan và minh bạch toàn bộ quá trình AI "suy nghĩ" 
và xử lý tác vụ theo thời gian thực:

Bảng tổng quan tiến trình (Summary Bar):
- Hiển thị tóm tắt toàn bộ hoạt động AI đã thực hiện để tìm ra lời giải (ví dụ: “Đã tra cứu 5 công thức, đọc 3 tài liệu giáo khoa, phân tích 2 dạng bài tương tự”).

Dòng thời gian suy luận & xử lý (Execution Timeline):
- Mỗi bước tư duy của AI được trình bày minh bạch theo chuỗi hành động:
    - Ý định & Phân tích (Thinking Steps): Các dòng trạng thái ngắn mô tả hướng tư duy của AI (ví dụ: “Đang phân tích dạng bài toán đồ thị hàm số...”, “Phát hiện công thức áp dụng chưa tối ưu, đổi sang phương pháp biến đổi nâng cao...”).
    - Tra cứu & Trích xuất kiến thức (Knowledge & Tool Logs): Hiển thị trực tiếp các nguồn tài liệu hoặc công cụ mà AI đã gọi (ví dụ: Đọc tài liệu: SGK Toán 12 - Chương 2, Tìm kiếm định lý: Đạo hàm hàm hợp, Chạy công cụ: Máy tính đại số SymPy).
    - Kiểm tra & Báo trạng thái (Status Indicators): Đánh dấu rõ các bước thử nghiệm, sai sót hoặc kết quả (ví dụ: nhãn Failed - Thử lại phương pháp khác khi phương pháp 1 không ra đáp số) để thể hiện tư duy sửa lỗi logic.

Giá trị giáo dục:
- Giúp học sinh/sinh viên hiểu rõ "tại sao lại ra đáp án đó" thay vì chỉ chép lời giải, từ đó học được phương pháp tư duy, cách tra cứu tài liệu và quy trình giải quyết vấn đề.


## Hôm nay đang ra sao
Hiện tại, khi người dùng gửi câu lệnh tới Chat Agent (ví dụ: “Bài tập này có thể giải bằng phương pháp nào?” hoặc “Trình bày lời giải chi tiết theo từng bước”), hệ thống chỉ trả về kết quả cuối cùng mà không hiển thị quá trình tư duy hay các bước xử lý trung gian.
Cụ thể: Agent chỉ trả lời thẳng câu trả lời cuối cùng mà không giải thích lý do, không hiển thị các bước suy luận nội bộ, không cho thấy AI đã đọc tài liệu nào, áp dụng định lý gì, hoặc đã thử phương pháp nào trước khi đưa ra kết quả.
Điều này khiến người dùng không nắm bắt được quy trình giải quyết vấn đề của AI, gây khó khăn trong việc học hỏi phương pháp tư duy và khó tin cậy vào kết quả nhận được.


## Chỗ tôi không chắc
- Các chỗ sẽ áp dụng Thinking Chat Agent: 
    - Các tính năng và yêu cầu trong hệ thống hiện tại sẽ được tích hợp vào Chat Agent, thay thế hoàn toàn giao diện Chat hiện tại.