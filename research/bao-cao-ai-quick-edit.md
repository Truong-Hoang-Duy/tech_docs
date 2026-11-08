# ĐỀ XUẤT ĐỊNH HƯỚNG: TRIỂN KHAI CÔNG CỤ AI BIÊN TẬP NHANH (AI QUICK EDIT) TRÊN CANVAS

## 1. Phạm vi & Bối cảnh hiện tại
Đề xuất này dựa trên tài liệu đặc tả **BookForge — AI Quick Edit (Phiên bản 1.1)** (`writing-block.md`), tập trung hoàn thiện bộ tiện ích hỗ trợ người dùng chỉnh sửa nhanh một đoạn nội dung đang soạn thảo ngay trên **Canvas Editor** (và các vùng soạn thảo nội dung học liệu như Sơ đồ tư duy).

Qua rà soát hiện trạng hệ thống hiện tại:
1. **Về giao diện & 5 công cụ biên tập nhanh**: Hệ thống đã dựng sẵn khung **Menu chuột phải (Context Menu)** và **Bảng xem trước kết quả (AI Review Panel)** cho 5 công cụ (*Sửa chính tả, Chỉnh diễn đạt, Rút gọn, Viết tiếp, Viết theo yêu cầu*), nhưng thao tác **Tinh chỉnh bằng câu lệnh bổ sung** hiện mới chỉ mở cho công cụ *Viết theo yêu cầu*, chưa đồng bộ cho cả 4 công cụ còn lại như đặc tả.
2. **Về ngữ cảnh Từ điển Sư phạm**: Hệ thống vừa hoàn thiện **Bộ Từ điển SGK & Sư phạm chuẩn (10 môn học khối 10–12 và bộ từ điển Chung)** ở phần Chat, nhưng bên luồng AI Quick Edit trên Canvas hiện vẫn đang để cổng chờ (chưa nối dữ liệu thật), nên chưa tự động nhận diện, bảo toàn và chuẩn hóa thuật ngữ chuyên môn khi biên tập.
3. **Về Đường ray tạo sinh (Generative Rails)**: Hệ thống đã có sẵn khung 3 lớp kiểm soát (*Input Rails, Generation Rails, Output Rails*), tuy nhiên công cụ **Sửa chính tả** hiện đang chạy tách riêng nên chưa được thừa hưởng danh sách thuật ngữ và quy tắc bảo vệ từ Từ điển Sư phạm.

---

## 2. Mục tiêu của giải pháp
Hoàn thiện **AI Quick Edit** theo đúng 3 trụ cột của tài liệu đặc tả (`writing-block.md`):
1. **5 công cụ biên tập nhanh trên cùng một giao diện**: Xử lý gọn các nhu cầu chỉnh sửa cục bộ ngay tại vị trí văn bản đang chọn mà không làm gián đoạn trải nghiệm soạn thảo.
2. **1 quy trình Review & Apply thống nhất**: Người dùng luôn xem được nội dung gốc và bản đề xuất, có thể **Thử lại**, **Tinh chỉnh** (nhập thêm yêu cầu), **Chỉnh sửa thủ công** trước khi chọn **Thay thế** hoặc **Chèn sau**.
3. **Kết nối ngầm Từ điển Sư phạm & Đường ray Tạo sinh**: Tự động bảo vệ thuật ngữ chuyên môn, số liệu, công thức và kiểm soát chất lượng đầu ra ở phía sau mà không làm tăng bước thao tác của người dùng.

---

## 3. Hiện trạng các thành phần đã có sẵn trên hệ thống

Qua rà soát, hệ thống đã có sẵn nền tảng xử lý cho cả giao diện lẫn kiểm soát nội dung, có thể kế thừa trực tiếp:

### Nhóm A: Danh mục 5 công cụ biên tập cục bộ
Đã có sẵn trong menu ngữ cảnh khi quét chọn văn bản và nhấp chuột phải (hoặc dùng phím tắt `Alt + /`):
1. **Sửa chính tả**: Sửa lỗi chính tả, dấu câu, viết hoa, lỗi đánh máy; giữ nguyên cách diễn đạt.
2. **Chỉnh diễn đạt**: Làm câu văn mạch lạc, tự nhiên, phù hợp văn phong giáo dục; giữ nguyên nội dung cốt lõi.
3. **Rút gọn**: Lược bỏ phần dư thừa, tăng tính súc tích; không làm mất luận điểm và dữ kiện.
4. **Viết tiếp**: Phát triển tiếp ý đang viết dựa trên đoạn gốc và ngữ cảnh liền kề, tránh lặp ý.
5. **Viết theo yêu cầu**: Nhập yêu cầu ngắn để AI xử lý đoạn văn được chọn theo đúng chỉ dẫn.

### Nhóm B: Bảng xem trước & kiểm soát thay đổi (AI Review Panel)
- Hiển thị ngay cạnh vùng văn bản đang chọn, phân biệt trực quan giữa **Nội dung gốc** (chỉ đọc) và **Đề xuất của AI** (tự động tô màu các từ/cụm từ thay đổi).
- Cho phép bấm trực tiếp vào ô đề xuất để **chỉnh sửa thủ công** trước khi áp dụng.
- Kiểm tra an toàn trước khi cập nhật: chỉ thay đổi đúng vùng chọn, chặn ghi đè nhầm nếu vùng văn bản gốc đã bị sửa trong lúc chờ AI xử lý, giữ nguyên định dạng đoạn văn và hỗ trợ hoàn tác (`Ctrl/Cmd + Z`).

### Nhóm C: Khung 3 lớp Đường ray Tạo sinh (Generative Rails)
- **Input Rails (Kiểm soát đầu vào)**: Giới hạn độ dài vùng chọn (tối đa 5.000 ký tự), lấy ngữ cảnh lân cận, bọc tách dữ liệu tài liệu với chỉ dẫn người dùng để tránh văn bản điều khiển ngược AI, tự động ẩn thông tin cá nhân (email, số điện thoại) ở ngữ cảnh phụ và kiểm tra chính sách an toàn nội dung.
- **Generation Rails (Kiểm soát tạo sinh)**: Khóa phạm vi theo từng công cụ, ép giữ nguyên dữ kiện, số liệu, công thức, đường dẫn, tên riêng và không sinh lời giải thích thừa.
- **Output Rails (Hậu kiểm đầu ra)**: Tự động lọc bỏ nhãn mở đầu thừa (*"Dưới đây là..."*, khung markdown), đối chiếu việc mất số liệu/công thức/tên riêng và kiểm tra độ dài bất thường; tự động xử lý lại nội bộ 1 lần nếu phát hiện lỗi nghiêm trọng, hoặc hiển thị cảnh báo để người dùng xem lại.

---

## 4. Danh mục các Task triển khai hoàn thiện

Để đáp ứng đầy đủ tài liệu đặc tả AI Quick Edit (`writing-block.md`), phần công việc còn lại được chia thành **4 Task** cụ thể như sau:

### Task 1: Kết nối Bộ Từ điển Sư phạm & SGK vào AI Quick Edit (Đáp ứng Mục III)
- **Bảo toàn thuật ngữ (Mục III.2.A)**: Kết nối kho **Từ điển SGK (10 môn học khối 10–12) và Từ điển Chung (sư phạm, GDPT 2018)** vào luồng AI Quick Edit để tự động quét và khóa bảo vệ các thuật ngữ chuyên môn, khái niệm môn học, kí hiệu xuất hiện trong đoạn văn được chọn; hiển thị dòng chú thích ngắn dưới bảng kết quả (*"Đã giữ nguyên: ..."*).
- **Chuẩn hóa cách diễn đạt (Mục III.2.B)**: Khi đoạn văn chứa cách viết đồng nghĩa/chưa chuẩn đã được định nghĩa trong từ điển, nạp cặp đối chiếu chuẩn vào ngữ cảnh để AI ưu tiên sử dụng đúng thuật ngữ và quy ước ngôn ngữ của môn học.
- **Tự động điều chỉnh theo bối cảnh tài liệu (Mục III.2.C)**: Tự động đọc thông tin môn học, khối lớp, loại tài liệu từ metadata hoặc suy luận từ tiêu đề tài liệu để chọn đúng bộ từ điển môn học mà không yêu cầu người dùng nhập lại.

### Task 2: Đồng bộ Đường ray Tạo sinh & Hậu kiểm thuật ngữ cho cả 5 công cụ (Đáp ứng Mục III.2.D, IV & VII)
- **Đưa công cụ "Sửa chính tả" vào chung lớp bảo vệ thuật ngữ**: Bổ sung danh sách thuật ngữ chuyên môn, kí hiệu và công thức cần bảo toàn vào bước *Sửa chính tả* để AI chỉ sửa lỗi đánh máy/dấu câu, không tự ý sửa nhầm thuật ngữ chuyên môn hoặc kí hiệu khoa học.
- **Cảnh báo bảo vệ ý nghĩa chuyên môn (Output Rails)**: Bổ sung kiểm tra đối chiếu thuật ngữ sư phạm ở đầu ra; nếu phát hiện thuật ngữ chuyên môn trong đoạn gốc bị biến đổi hoặc lược bỏ ngoài ý muốn, hệ thống hiển thị cảnh báo rõ trên bảng Review để giáo viên kiểm soát trước khi áp dụng.

### Task 3: Bổ sung thao tác "Tinh chỉnh" thống nhất trên AI Review Panel (Đáp ứng Mục V.2, V.3 & VI)
- Bổ sung nút **Tinh chỉnh** ở thanh công cụ dưới chân bảng Review cho cả các công cụ biên tập nhanh (cùng với *Thử lại*, *Bỏ qua* và *Thay thế / Chèn sau*).
- Khi người dùng bấm **Tinh chỉnh**, hiển thị ô nhập yêu cầu bổ sung ngay trên bảng Review; AI sẽ xử lý dựa trên cả **nội dung gốc** lẫn **bản đề xuất hiện tại** để điều chỉnh tiếp theo đúng chỉ dẫn.

### Task 4: Chuẩn hóa Menu ngữ cảnh & Lối mở công cụ trên thanh soạn thảo (Đáp ứng Mục V.1 & VIII)
- Hiển thị gọn nhóm **Công cụ AI** (5 chức năng, có phân tách nhẹ ở mục *Viết theo yêu cầu*) ngay khi quét chọn văn bản và nhấp chuột phải.
- Bổ sung nút mở nhanh **Công cụ AI** trên thanh công cụ phía trên của trình soạn thảo Canvas (bên cạnh phím tắt `Alt + /` đã có) để người dùng có cách truy cập tương đương mà không phụ thuộc hoàn toàn vào chuột phải.

---

## 5. Các điểm cần thống nhất trước khi thực hiện
1. **Về cách hoạt động của Từ điển Sư phạm trong AI Quick Edit**:
   - Thống nhất áp dụng **tự động hoàn toàn ở phía sau** (luôn bật bộ từ điển *Chung* kết hợp với bộ từ điển môn học nhận diện được từ tài liệu/đoạn văn), không mở thêm hộp thoại cài đặt từ điển riêng trên bảng Quick Edit để đảm bảo nguyên tắc không tăng bước thao tác.
2. **Về thao tác "Tinh chỉnh" trên bảng Review**:
   - Mặc định ẩn ô nhập lệnh đối với 4 công cụ đầu để bảng Review gọn nhẹ; chỉ khi người dùng bấm nút **Tinh chỉnh** ở thanh công cụ dưới chân bảng thì ô nhập yêu cầu bổ sung mới mở ra (riêng công cụ *Viết theo yêu cầu* vẫn hiển thị ô nhập lệnh ngay từ đầu).
3. **Về vị trí truy cập tương đương ngoài chuột phải**:
   - Bên cạnh phím tắt `Alt + /` đã có, bổ sung thêm nút **Công cụ AI** trên thanh công cụ phía trên của trình soạn thảo Canvas (kích hoạt khi người dùng đang quét chọn văn bản).

