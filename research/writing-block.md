# BOOKFORGE — AI QUICK EDIT
**ĐẶC TẢ CHỨC NĂNG & NGUYÊN TẮC UI/UX**

**Module:** Canvas Editor — Công cụ AI biên tập nhanh  
**Phiên bản:** 1.1  
**Đối tượng:** Product, UI/UX, Engineering, AI Team

---

## I. Mục tiêu sản phẩm

AI Quick Edit là bộ tiện ích hỗ trợ người dùng chỉnh sửa nhanh một phần nội dung đang soạn thảo trên Canvas.

**Mục tiêu:**
- Xử lý các nhu cầu biên tập thông thường ngay trên văn bản.
- Giảm thao tác, không làm gián đoạn trải nghiệm soạn thảo.
- Nâng cao chất lượng ngôn ngữ trong bối cảnh giáo dục.
- Kế thừa Từ điển Sư phạm và Đường ray Tạo sinh của BookForge.
- Cho phép người dùng xem xét và kiểm soát mọi thay đổi trước khi áp dụng.

**Giới hạn:** Chỉ xử lý cục bộ. Các nhiệm vụ phân tích chuyên môn, đánh giá học thuật, kiểm chứng kiến thức, xây dựng giáo án và tạo học liệu phức tạp thuộc phạm vi AI Assistant/Agent.

---

## II. Danh mục công cụ

Chỉ triển khai 5 chức năng, sử dụng chung một giao diện tương tác.

| Công cụ | Mục đích | Nguyên tắc xử lý |
|---|---|---|
| **1. Sửa chính tả** | Sửa lỗi chính tả, dấu câu, viết hoa, lỗi đánh máy | Không thay đổi cách diễn đạt hoặc ý nghĩa khi không cần thiết |
| **2. Chỉnh diễn đạt** | Làm câu văn mạch lạc, tự nhiên, phù hợp văn phong | Giữ nguyên nội dung cốt lõi và thuật ngữ chuyên môn |
| **3. Rút gọn** | Lược bỏ phần dư thừa, tăng tính súc tích | Không làm mất luận điểm, dữ kiện quan trọng |
| **4. Viết tiếp** | Phát triển tiếp ý đang viết | Dựa trên nội dung gốc và ngữ cảnh gần nhất; tránh lặp ý |
| **5. Viết theo yêu cầu** | Cho phép người dùng nhập prompt ngắn để AI xử lý nội dung được chọn | Thực hiện đúng yêu cầu, trong phạm vi biên tập cục bộ |

Bốn công cụ đầu xử lý ngay sau khi người dùng lựa chọn. Công cụ thứ năm yêu cầu nhập prompt trước khi thực thi.

Không bổ sung nhiều preset văn phong, cấu hình môn học hoặc chức năng AI chuyên sâu vào menu.

---

## III. Tích hợp Từ điển Sư phạm

### 1. Vấn đề cần giải quyết

AI biên tập thông thường có thể vô tình:
- Thay đổi thuật ngữ chuyên môn thành từ phổ thông không tương đương.
- Viết sai hoặc làm lệch nghĩa của khái niệm sư phạm.
- Sử dụng cách diễn đạt không phù hợp với đối tượng giáo dục.
- Chỉnh sửa thiếu nhất quán tên môn học, thuật ngữ, học liệu và quy ước của nhà trường.

**Yêu cầu:** AI Quick Edit cần kế thừa Từ điển Sư phạm như một lớp tham chiếu ngôn ngữ và thuật ngữ, không biến công cụ thành hệ thống phân tích kiến thức.

### 2. Cách áp dụng

**A. Bảo toàn thuật ngữ**

Nhận diện và ưu tiên giữ nguyên thuật ngữ chuyên môn, tên riêng, khái niệm môn học và các cách viết chuẩn có trong từ điển.

Ví dụ: Không tùy tiện thay đổi thuật ngữ "phản ứng oxi hóa – khử" thành cách diễn đạt khác làm sai bản chất.

**B. Chuẩn hóa cách diễn đạt**

Sử dụng cách viết, thuật ngữ và quy ước ngôn ngữ đã được định nghĩa trong từ điển khi phù hợp với nội dung.

**C. Điều chỉnh theo bối cảnh**

Khi tài liệu đã có metadata như cấp học, môn học, loại tài liệu hoặc đối tượng người đọc, sử dụng các thông tin đó để lựa chọn quy tắc ngôn ngữ phù hợp.

Không yêu cầu người dùng nhập lại thông tin đã có.

**D. Bảo vệ ý nghĩa chuyên môn**

Khi AI phát hiện một thuật ngữ có thể không chuẩn nhưng không đủ căn cứ để sửa, ưu tiên giữ nguyên hoặc cảnh báo ngắn thay vì tự quyết định thay thế.

### 3. Nguyên tắc sử dụng

- Từ điển là nguồn tham chiếu, không phải công cụ tự động sửa toàn bộ nội dung.
- Ưu tiên thuật ngữ đã được xác thực và đúng bối cảnh.
- Không cưỡng ép thay thế những cách diễn đạt hợp lệ.
- Không bổ sung định nghĩa hoặc kiến thức ngoài yêu cầu biên tập.
- Không làm tăng số bước thao tác của người dùng.

**UI:** Không cần một giao diện Từ điển Sư phạm riêng. Việc áp dụng diễn ra tự động. Chỉ hiển thị chú thích ngắn khi có thuật ngữ quan trọng được giữ nguyên hoặc chuẩn hóa.

---

## IV. Tích hợp Đường ray Tạo sinh (Generative Rails)

### 1. Mục tiêu

Generative Rails là cơ chế kiểm soát chất lượng và giới hạn hoạt động của AI, áp dụng xuyên suốt quá trình xử lý.

Đối với AI Quick Edit, cần thiết kế ba lớp:

### A. Input Rails — Kiểm soát đầu vào

**Vấn đề:** AI có thể thiếu bối cảnh, nhận vùng chọn không phù hợp hoặc xử lý vượt quá phạm vi người dùng mong muốn.

**Yêu cầu:**
- Xác định nội dung được chọn và loại tác vụ.
- Thu nhận ngữ cảnh gần nhất nếu cần thiết.
- Kế thừa metadata tài liệu và Từ điển Sư phạm phù hợp.
- Kiểm tra giới hạn nội dung, quyền truy cập và chính sách sử dụng.
- Hạn chế truyền dữ liệu không cần thiết hoặc thông tin cá nhân đến mô hình bên thứ ba.
- Phân biệt nội dung tài liệu với chỉ dẫn người dùng, tránh việc văn bản được chọn điều khiển AI ngoài ý muốn.

### B. Generation Rails — Kiểm soát tạo sinh

**Vấn đề:** AI có xu hướng viết lại quá mức, thêm ý, thay đổi thuật ngữ hoặc vượt khỏi nhiệm vụ ban đầu.

**Yêu cầu:**
- Mỗi công cụ có phạm vi xử lý và giới hạn rõ ràng.
- Giữ đúng mục đích: sửa lỗi, diễn đạt, rút gọn, viết tiếp hoặc xử lý prompt.
- Áp dụng quy tắc ngôn ngữ từ Từ điển Sư phạm.
- Bảo toàn dữ kiện, số liệu, công thức, tên riêng và thuật ngữ.
- Không tự thêm kiến thức, dẫn chứng hoặc kết luận không được yêu cầu.
- Ưu tiên kết quả ngắn gọn, trực tiếp, không sinh lời giải thích dài dòng.

**Ví dụ:** Khi người dùng chọn "Sửa chính tả", AI không được viết lại văn bản chỉ vì nhận thấy có cách diễn đạt hay hơn.

### C. Output Rails — Hậu kiểm đầu ra

**Vấn đề:** Kết quả AI có thể không phù hợp với yêu cầu hoặc vô tình làm sai lệch nội dung.

**Yêu cầu:**
- Kiểm tra kết quả có đúng loại tác vụ hay không.
- Đối chiếu các thuật ngữ quan trọng với Từ điển Sư phạm.
- Phát hiện thay đổi bất thường về số liệu, tên riêng, công thức hoặc nội dung cốt lõi.
- Phát hiện nội dung bổ sung không có cơ sở trong các tác vụ yêu cầu bảo toàn ý nghĩa.
- Kiểm tra nội dung đầu ra có phù hợp để đưa trở lại Canvas.

**Hành vi khi không đạt:**
- Lỗi đơn giản: có thể xử lý lại nội bộ trong giới hạn hợp lý.
- Không đủ tin cậy: hiển thị cảnh báo hoặc yêu cầu người dùng xem lại.
- Lỗi nghiêm trọng: không cung cấp kết quả như một đề xuất hợp lệ để áp dụng.

Rails là lớp hỗ trợ kiểm soát, không bảo đảm tuyệt đối tính chính xác của mọi nội dung AI.

### 2. Nguyên tắc vận hành

Generative Rails hoạt động phía sau giao diện.

Không cần tạo các bước kiểm tra, cấu hình hoặc phê duyệt riêng cho người dùng. Chỉ hiển thị thông báo khi kết quả có vấn đề thực sự cần người dùng chú ý.

---

## V. UI/UX — Thiết kế thống nhất

### 1. Context Menu

**Điều kiện:** Người dùng quét chọn văn bản và nhấp chuột phải trong Canvas.

Hiển thị nhóm "Công cụ AI" với 5 chức năng:

1. Sửa chính tả
2. Chỉnh diễn đạt
3. Rút gọn
4. Viết tiếp
5. Viết theo yêu cầu

**Nguyên tắc thiết kế:**
- Menu gọn, có icon tương ứng.
- Không có submenu nhiều tầng.
- "Viết theo yêu cầu" được phân tách nhẹ để dễ nhận diện.
- Màu sắc, icon, trạng thái hover đồng nhất với hệ thống BookForge.
- Có cách truy cập tương đương không phụ thuộc hoàn toàn vào chuột phải.

### 2. AI Review Panel

Sau khi chọn công cụ, mở một panel nhỏ cạnh vùng văn bản được chọn.

**Các thành tố bắt buộc:**

| Thành tố | Nội dung / Hành vi |
|---|---|
| Header | Icon AI, tên công cụ, nút đóng |
| Nội dung gốc | Hiển thị chính xác vùng được chọn, chỉ đọc |
| Đề xuất của AI | Hiển thị nội dung sau xử lý, cho phép chỉnh sửa |
| Thông tin thay đổi | Đánh dấu hoặc mô tả ngắn những thay đổi chính nếu hữu ích |
| Prompt | Hiện với "Viết theo yêu cầu" hoặc khi chọn "Tinh chỉnh" |
| Footer | Thử lại, Tinh chỉnh, Bỏ qua, Thay thế/Chèn sau |

**Nguyên tắc hiển thị:**
- Hai vùng "Nội dung gốc" và "Đề xuất của AI" phải được phân biệt trực quan.
- Không yêu cầu người dùng chuyển sang giao diện khác để review.
- Ưu tiên bố cục dọc, dễ đọc và tiết kiệm diện tích.
- Panel không được chiếm phần lớn không gian soạn thảo.
- Nội dung dài có thể cuộn; các nút hành động luôn dễ tiếp cận.
- Không cần bộ so sánh phiên bản phức tạp.

### 3. Các thao tác người dùng

**Thử lại:** AI tạo một phương án khác bằng yêu cầu hiện tại, không thay đổi Canvas.

**Tinh chỉnh:** Hiển thị ô prompt để người dùng nhập yêu cầu bổ sung. AI xử lý dựa trên nội dung gốc và bản đề xuất hiện tại.

**Chỉnh sửa thủ công:** Người dùng có thể sửa trực tiếp kết quả AI trước khi xác nhận.

**Thay thế:** Thay đúng vùng đã chọn bằng kết quả sau review.

**Chèn sau:** Thêm nội dung mới vào sau vùng chọn mà không xóa nội dung cũ. Đây là thao tác mặc định của "Viết tiếp".

**Bỏ qua:** Đóng panel, không tác động đến tài liệu.

Với "Viết theo yêu cầu", cho phép lựa chọn Thay thế hoặc Chèn sau trước khi xác nhận.

Không mở thêm hộp thoại xác nhận sau khi người dùng nhấn Apply.

---

## VI. Quy trình sử dụng thống nhất

**Bước 1 — Chọn nội dung**

Người dùng quét chọn một đoạn trên Canvas và mở menu AI.

**Bước 2 — Chọn chức năng**

Bốn công cụ biên tập nhanh xử lý ngay. Công cụ "Viết theo yêu cầu" hiển thị ô prompt trước.

**Bước 3 — AI xử lý**

Hệ thống kết hợp:
- Nội dung vùng chọn.
- Ngữ cảnh cần thiết.
- Từ điển Sư phạm.
- Các quy tắc Generative Rails.
- Chỉ dẫn của người dùng (nếu có).

**Bước 4 — Review**

Hiển thị nội dung gốc và kết quả. Người dùng có thể đọc lại, chỉnh sửa hoặc yêu cầu AI điều chỉnh tiếp.

**Bước 5 — Xác nhận**

Người dùng chọn Thay thế, Chèn sau hoặc Bỏ qua.

Chỉ khi xác nhận thành công, Canvas mới được cập nhật.

---

## VII. Các tình huống cần xử lý

| Tình huống | Hành vi mong muốn |
|---|---|
| AI không tìm thấy lỗi chính tả | Thông báo không có lỗi cần sửa; không tạo thay đổi giả |
| Kết quả không đúng yêu cầu | Cho phép Thử lại hoặc Tinh chỉnh |
| AI làm thay đổi thuật ngữ quan trọng | Rails kiểm tra, ưu tiên phục hồi hoặc cảnh báo |
| AI sinh nội dung quá dài | Giới hạn phù hợp với công cụ; tránh biến Quick Edit thành tác vụ soạn thảo toàn phần |
| Người dùng sửa tài liệu trong lúc AI xử lý | Kiểm tra vùng gốc trước khi Apply, không ghi đè nhầm |
| Người dùng đóng panel | Giữ nguyên tài liệu |
| AI xử lý thất bại | Có thông báo và tùy chọn Thử lại |
| Nội dung chọn không phù hợp hoặc quá dài | Đề nghị chọn đoạn ngắn hơn hoặc sử dụng AI Assistant |
| Kết quả được người dùng sửa thủ công | Áp dụng phiên bản đã được người dùng chỉnh sửa, không dùng lại bản AI ban đầu |

---

## VIII. Nguyên tắc nghiệm thu

Sản phẩm đạt yêu cầu khi:

1. Người dùng có thể sử dụng đầy đủ 5 công cụ từ cùng một menu.
2. Tất cả chức năng có trải nghiệm Review & Apply thống nhất.
3. Người dùng luôn xem được nội dung gốc và kết quả trước khi áp dụng.
4. Có thể Thử lại, Tinh chỉnh hoặc chỉnh sửa thủ công kết quả.
5. Không tự động ghi đè tài liệu.
6. Chỉ thay đổi đúng vùng chọn, giữ định dạng phù hợp và hỗ trợ hoàn tác.
7. Từ điển Sư phạm hỗ trợ bảo toàn, chuẩn hóa thuật ngữ đúng bối cảnh.
8. Generative Rails kiểm soát phạm vi tạo sinh và hậu kiểm những thay đổi quan trọng.
9. Hệ thống không bổ sung các bước thao tác không cần thiết.
10. Giao diện phù hợp với thiết kế chung của BookForge.

---

## IX. Kết luận triển khai

**AI Quick Edit là tiện ích biên tập, không phải một AI Agent thu nhỏ.**

Kiến trúc sản phẩm được thống nhất theo ba thành phần:

- **5 công cụ biên tập nhanh:** giải quyết các tác vụ đơn giản.
- **1 giao diện Review & Apply:** bảo đảm người dùng luôn kiểm soát thay đổi.
- **Từ điển Sư phạm + Generative Rails:** nâng cao chất lượng ngôn ngữ, bảo vệ thuật ngữ và hạn chế sai lệch tạo sinh.

Người dùng chỉ thấy một công cụ chỉnh sửa nhanh, đơn giản. Các lớp kiểm soát và tối ưu chất lượng được BookForge xử lý phía sau, không tạo thêm gánh nặng thao tác.