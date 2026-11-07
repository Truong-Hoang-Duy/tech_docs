# ĐỀ XUẤT ĐỊNH HƯỚNG: TÍCH HỢP TỪ ĐIỂN SƯ PHẠM & ĐƯỜNG RAY TẠO SINH CHO PHẦN CHAT

## 1. Phạm vi & Bối cảnh hiện tại
Đề xuất này tập trung triển khai cho **phần Chat chính** (bao gồm trò chuyện chung và 5 Agent chuyên biệt: *Phiếu điền khuyết, Ma trận đề, Tạo đề kiểm tra, Dịch học thuật, Thiết kế Infographic*), **chưa triển khai cho khung chat trong trình soạn thảo (Canvas)**.

Hiện tại ở phần Chat:
1. **Về ngữ cảnh Từ điển Sách giáo khoa (SGK)**: Các Agent khi tạo sinh mới chỉ đọc nội dung văn bản bài học thô mà chưa được kết nối với **Bộ từ điển thuật ngữ SGK chuẩn (10 môn học khối 10–12)** đã được biên tập sẵn. Do đó, câu chữ sinh ra đôi khi còn chung chung, chưa khớp tuyệt đối với thuật ngữ, kí hiệu và quy ước của từng chương/bài trong SGK.
2. **Về Đường ray tạo sinh (Generative Rails)**: Hệ thống phía dưới thực tế **đã có sẵn các bộ quy tắc kiểm soát nội dung** (như tôn trọng chủ quyền biển đảo Việt Nam, giữ văn phong sư phạm/học thuật, chống bịa nguồn, liêm chính học thuật, quy chế nhà trường...). Tuy nhiên, các quy tắc này hiện đang chạy ngầm cố định ở phía hệ thống chứ chưa được hiển thị tường minh lên giao diện trình duyệt để người dùng theo dõi và chủ động bật/tắt theo nhu cầu phiên chat.

---

## 2. Mục tiêu của giải pháp
Nâng cấp phần **Cài đặt ngữ cảnh & công cụ** cho trang Chat theo 2 hướng chính:
1. **Bổ sung ngữ cảnh Từ điển sư phạm**: Đưa bộ dữ liệu Từ điển SGK vào các Agent để đảm bảo nội dung tạo sinh chuẩn xác từng thuật ngữ, kí hiệu và đúng trình độ lớp học.
2. **Hiển thị và cho phép bật/tắt Đường ray tạo sinh (Generative Rails)**: Không đẻ thêm quy tắc mới, mà tổng hợp các quy tắc kiểm soát đã có sẵn trong hệ thống để hiển thị lên giao diện trình duyệt, cho phép người dùng bật/tắt linh hoạt theo thiết kế.

---

## 3. Hiện trạng các quy tắc đã có sẵn trong hệ thống (Đường ray tạo sinh)
Qua rà soát hệ thống hiện tại, phần Chat và các Agent đang có sẵn **2 nhóm quy tắc kiểm soát nội dung** có thể đưa thẳng lên giao diện **Đường ray tạo sinh**:

### Nhóm A: Các quy tắc chuẩn mực & an toàn hệ thống (đang chạy ngầm trong mọi phiên Chat)
1. **Tôn trọng chủ quyền & biển đảo Việt Nam**: Mặc định khẳng định Hoàng Sa và Trường Sa là của Việt Nam khi trả lời các nội dung liên quan đến biển đảo, lãnh thổ, bản đồ hoặc địa danh; không trình bày thông tin sai lệch chủ quyền và không kích động thù ghét dân tộc.
2. **Văn phong sư phạm & học thuật chuẩn mực**: Giữ giọng văn lịch sự, chuẩn mực giáo dục (xưng hô *"Tôi"* – *"thầy/cô"*, sử dụng thuật ngữ đầy đủ như *"kế hoạch bài dạy"*); không dùng ngôn từ tục tĩu, xúc phạm hay kỳ thị vùng miền, dân tộc, giới tính, tôn giáo.
3. **Bám sát nguồn tài liệu & Chống bịa đặt trích dẫn**: Chỉ trích dẫn nội dung có thật trong tài liệu được cấp hoặc nguồn tra cứu pháp lý; không tự bịa số hiệu văn bản, điều luật, số trang hay tác giả; phân biệt rõ dữ kiện trong tài liệu với suy luận và nói rõ khi chưa đủ căn cứ.
4. **Liêm chính học thuật & Quy định sử dụng AI trong trường học (Quyết định 705)**:
   - Không giải hộ toàn bộ đề thi, bài kiểm tra hoặc làm thay bài tập cho học sinh (chỉ hướng dẫn tư duy từng bước).
   - Không thay mặt giáo viên/nhà trường ra quyết định kỷ luật hoặc xếp loại hạnh kiểm, học lực chính thức.
   - Các học liệu kiểm tra đánh giá do AI tạo ra luôn mang tính chất tham khảo chờ chuyên môn duyệt.
5. **Bảo vệ dữ liệu cá nhân & An toàn thông tin (Nguyên tắc "5 không")**: Không tiết lộ hoặc lặp lại thông tin cá nhân nhạy cảm (số CCCD/CMND, mật khẩu, dữ liệu tài chính, hồ sơ riêng tư của học sinh) và các thông tin nội bộ hệ thống.

### Nhóm B: Các mục Quy chế nhà trường tùy chỉnh
- Hệ thống đã có sẵn chức năng **Quy chế nhà trường** (cho phép từng trường tạo các mục quy định riêng như *Quy tắc ứng xử, Quy định học vụ, Chuẩn mực ngôn từ...* và kiểm tra lại câu trả lời của AI trước khi xuất ra).

### Định hướng đưa lên giao diện "Đường ray tạo sinh"
- Thay vì viết mới quy tắc, Backend sẽ cung cấp danh sách các quy tắc hiện có ở trên lên trình duyệt dưới dạng các tùy chọn trong mục **Đường ray tạo sinh (Generative Rails)**.
- Người dùng trên giao diện Chat có thể nhìn thấy rõ những quy tắc nào đang được áp dụng và **bật/tắt** từng quy tắc (hoặc bật/tắt cả cụm Đường ray tạo sinh) cho phiên trò chuyện, hệ thống sẽ chỉ nạp và kiểm duyệt theo đúng các quy tắc đang được bật.

---

## 4. Định hướng tích hợp Từ điển Sư phạm cho phần Chat & 5 Agent

### 4.1. Đóng gói dữ liệu & Truy xuất Từ điển
- **Hợp nhất bộ Từ điển SGK vào Kho tri thức mặc định**: Đưa toàn bộ dữ liệu từ điển của 10 môn học hiện có (lớp 10–12) vào kho tri thức của hệ thống (lọc bỏ tên riêng của bộ sách/nhà xuất bản để đảm bảo trung lập bản quyền), đồng thời bổ sung bộ từ điển **"Chung (sư phạm, giáo dục)"** chứa các khái niệm cốt lõi của Chương trình GDPT 2018.
- **Truy xuất từ điển theo 2 chế độ**:
  - *Theo Bài học/Chương*: Khi giáo viên làm học liệu theo một bài hoặc chương cụ thể, nạp toàn bộ thuật ngữ và quy ước của đúng bài/chương đó.
  - *Theo Văn bản/Câu hỏi tự do*: Khi giáo viên gửi một đoạn văn bản hoặc câu hỏi bất kỳ trong Chat, tự động quét và rút ra 15–30 thuật ngữ trong các bộ từ điển đang bật có liên quan sát nhất để cấp ngữ cảnh cho AI.

### 4.2. Ứng dụng Từ điển vào 5 Agent chuyên biệt trong phần Chat
- **Agent Phiếu điền khuyết**: Dùng từ điển để nhận diện đúng "từ khóa cốt lõi" của bài học nhằm ưu tiên đục lỗ; dùng các tên gọi tương đương hoặc thuật ngữ cùng chương làm "từ gây nhiễu" trong ngân hàng từ; dùng giải nghĩa chuẩn của từ điển để viết phần giải thích đáp án.
- **Agent Ma trận đề**: Dựa vào hệ thống thuật ngữ và quy ước của từng chương/bài để gọi tên chính xác các "Đơn vị kiến thức" và đề xuất gợi ý trọng tâm câu hỏi khớp với từng mức độ *Biết – Hiểu – Vận dụng*.
- **Agent Tạo đề kiểm tra**: Dùng danh sách thuật ngữ và các tên gọi khác trong từ điển để tìm kiếm câu hỏi từ Ngân hàng câu hỏi chính xác hơn, đồng thời chuẩn hóa lại thuật ngữ trong đề và bảng đáp án.
- **Agent Dịch học thuật**: Tra cứu trực tiếp cặp đối chiếu *Thuật ngữ Tiếng Việt ↔ Thuật ngữ Tiếng Anh / Kí hiệu chuẩn* trong từ điển SGK trước khi dịch, giúp bản dịch và Bảng thuật ngữ đối chiếu ở cuối bài chuẩn xác theo SGK.
- **Agent Thiết kế Infographic**: Nạp danh sách thuật ngữ, kí hiệu và định nghĩa tóm tắt của bài học để các tiêu đề nhánh, công thức và hộp khái niệm trên Poster ngắn gọn nhưng chuẩn xác từng chữ.

---

## 5. Các điểm cần thống nhất trước khi lên Spec chi tiết
1. **Danh sách các nút bật/tắt trong mục "Đường ray tạo sinh" trên giao diện**:
   - Từ các quy tắc đã có sẵn trong hệ thống (mục 3), chúng ta sẽ chọn hiển thị những quy tắc nào thành các ô tích (checkbox) bật/tắt trên giao diện? (Ví dụ: *Tôn trọng chủ quyền biển đảo Việt Nam*, *Phong cách học thuật & sư phạm*, *Bám sát tài liệu & không bịa nguồn*, *Tuân thủ quy chế nhà trường*...).
   - Có quy tắc nào bắt buộc luôn khóa bật (không cho tắt vì lý do pháp lý như Chủ quyền biển đảo / Bảo mật CCCD) hay cho phép bật/tắt toàn bộ trên giao diện?
2. **Cách gom nhóm môn học trong mục "Từ điển sư phạm"**:
   - Bộ dữ liệu từ điển hiện tại gồm 10 môn cấp THPT (*Toán, Ngữ văn, Vật lí, Hóa học, Sinh học, Lịch sử, Địa lí, GDKT&PL, Tiếng Anh, Tin học*).
   - Đề xuất: Trên giao diện hiển thị các mục *Chung (sư phạm, giáo dục)*, *Toán học*, *Ngữ văn*, *Khoa học tự nhiên* (tự động gộp 3 bộ từ điển *Vật lí, Hóa học, Sinh học*), và mục *Khác...* để chọn lẻ các môn còn lại.
