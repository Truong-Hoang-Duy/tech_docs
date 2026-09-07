# Tính năng: Tạo sinh câu hỏi theo thang Bloom (Backend)

## 1. Mục tiêu chung (User Intent)
Dự án cần một công cụ (API) tạo sinh câu hỏi dựa trên thang đo Bloom.
- **Thang đo:** Sử dụng thang Bloom xuôi (Nhận biết → Thông hiểu → Vận dụng → Đánh giá). Bỏ qua thang Bloom 2001 (sáng tạo) vì yêu cầu cao và chưa phù hợp hiện tại.
- **Dạng câu hỏi:** Giai đoạn này tập trung xử lý các câu hỏi trắc nghiệm đơn giản (1 đáp án đúng, nhiều đáp án đúng, đúng/sai).

## 2. Chi tiết luồng nghiệp vụ & Ngữ cảnh đầu vào (Input/Output)
- **Đầu vào (Input):** Dữ liệu có cấu trúc, được chọn từ khung chương trình đã có sẵn. Bao gồm:
  - *Kiến thức / Chủ đề:* Ví dụ "Nguyên hàm – Tích phân" (Toán 12).
  - *Năng lực / Mức Bloom:* Ví dụ "Nhận biết" (nhớ công thức, định nghĩa, khái niệm).
  - *Dạng câu hỏi:* Ví dụ "Trắc nghiệm 1 đáp án đúng".
  *(Giả định việc trích xuất nội dung từ kho học liệu đã được xử lý ở các bước trước, tool này chỉ tập trung sinh câu hỏi dựa trên tham số đầu vào).*
- **Đầu ra (Output):** Trả về cục dữ liệu bao gồm: nội dung câu hỏi, các phương án lựa chọn, đáp án đúng, giải thích chi tiết và barem điểm tương ứng.
- **Quy trình kiểm duyệt (Workflow):** Phạm vi hiện tại chỉ dừng ở tầng Backend. Kết quả sẽ được kiểm thử và xác nhận qua giao diện Swagger. Luồng Frontend cho giáo viên xem trước/chỉnh sửa/lưu sẽ được thực hiện ở phase sau.

## 3. Barem chấm điểm
- Các dạng trắc nghiệm hiện tại áp dụng logic chấm điểm "0 hoặc có điểm" (không chấm điểm từng phần như tự luận).
- Tuy nhiên, hệ thống cần hỗ trợ **cấu hình điểm linh hoạt** theo từng mức thang Bloom (Ví dụ: Nhận biết = 1 điểm, Thông hiểu = 1.5 điểm), thay vì fix cứng một điểm số cho tất cả mọi câu.

## 4. Tính đặc thù môn học & Khả năng mở rộng
- Tính năng này được thiết kế **tổng quát cho tất cả các môn học**.
- Đặc biệt lưu ý: Kiến trúc dữ liệu phải đủ mở rộng để xử lý các loại nội dung phức tạp hơn văn bản thô, chẳng hạn như hỗ trợ **công thức Toán/Lý (LaTeX), hình ảnh, đồ thị** sinh ra trong câu hỏi hoặc đáp án.
