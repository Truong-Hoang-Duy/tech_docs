# BOOKFORGE — KẾ HOẠCH PHẠM VI QUẢN TRỊ VÀ GIẢI TRÌNH HOẠT ĐỘNG AI

**Phiên bản:** 1.0 — 02/11/2026  
**Đối tượng:** Product/BA, Engineering Lead, AI Engineering, Development, QA/QC  
**Phạm vi:** BookForge triển khai cho cơ sở giáo dục phổ thông, khởi đầu từ Quy tắc sử dụng AI của THPT Long Trường năm học 2026–2027  
**Tính chất:** Tài liệu định hướng và phân rã **vấn đề/phạm vi/tiêu chí nghiệm thu**; **không phải** thiết kế kiến trúc, đặc tả kỹ thuật, bộ prompt hoặc phương án triển khai.

> **Tuyên ngôn sản phẩm:** Quản trị AI để người dùng **được học hỏi, sáng tạo và khai thác tri thức trong môi trường an toàn, có trách nhiệm, có thể giải trình**; không dùng quản trị AI như một cơ chế kiểm duyệt tùy tiện hay mặc định nghi ngờ người dùng.

---

## 1. Mục tiêu và giới hạn

### 1.1. Kết quả cần đạt

BookForge có thể trả lời nhất quán, với bằng chứng tương ứng, cho **mọi thao tác AI**:

1. **Ai** thực hiện, thuộc trường/Workspace nào, đang có vai trò và phạm vi quyền gì?
2. **Đã sử dụng dữ liệu nào**; nếu có file thì ai tải lên, khi nào, đã khai báo điều gì, file được sử dụng ở tác vụ nào?
3. **Yêu cầu là gì**, dùng AI với mục đích nào và có phù hợp bối cảnh sư phạm, quy tắc nhà trường và quyền của người dùng hay không?
4. **Kết quả là gì**, do AI tạo ra tới mức nào, có/không có tài liệu tham chiếu nào?
5. **Quy tắc nào đã được áp dụng**, kết quả được cho phép, cần điều chỉnh hay không thể hỗ trợ vì lý do gì?
6. **Ai chịu trách nhiệm cuối cùng** với việc duyệt, sử dụng hoặc phát hành sản phẩm, nhất là nội dung kiểm tra đánh giá?
7. **Có thể truy vết** từ kết quả tạo sinh trở lại người thực hiện, lần sử dụng AI và tài nguyên tham chiếu hay không?

**Chuẩn giải trình:** có căn cứ, có người chịu trách nhiệm, có lịch sử hoạt động tối thiểu; không tuyên bố rằng AI đã chứng minh đúng/sai, có bản quyền hay hợp pháp tuyệt đối.

### 1.2. Những điều không được đánh đồng

- **Tick xác nhận quyền dùng file ≠ bằng chứng sở hữu bản quyền** và **≠ sự cho phép xử lý mọi loại dữ liệu**. Đây là tuyên bố trách nhiệm của người dùng, không thay thế nghĩa vụ bảo vệ dữ liệu của nhà trường và BookForge.
- **File được tải lên ≠ file được phép dùng với AI**. Quyền tải lên, quyền truy cập và quyền dùng làm nguồn cho một tác vụ AI là các vấn đề phải phân biệt.
- **LLM tạo nội dung ≠ LLM là nguồn kiểm chứng sự thật**. “Không dùng nguồn tham chiếu” phải được nhãn hóa đúng; không gắn trích dẫn giả.
- **AI đề xuất nhận xét/đáp án ≠ AI được quyền quyết định kết quả đánh giá chính thức**. Quyết định chuyên môn thuộc người có thẩm quyền.
- **Chính sách của một trường ≠ tự động áp dụng nguyên xi cho mọi trường**. MVP lấy Long Trường làm chính sách mẫu; các trường khác cần đối chiếu chính sách riêng.
- **Ghi log ≠ được phép giữ vô hạn nội dung cá nhân, prompt hay tài liệu**. Phạm vi truy cập và thời hạn lưu phải được quy định phù hợp.

### 1.3. Nguyên tắc phạm vi

- **Không quét nội dung file để tự phán xét hoặc quyết định quyền upload.** Người upload khai báo và chịu trách nhiệm về quyền sử dụng; BookForge ghi nhận cam kết. Xử lý OCR theo tác vụ mà người dùng chủ động yêu cầu là nghiệp vụ tri thức, **khác** với quét kiểm duyệt file lúc upload.
- **Không bỏ qua quy tắc ở bất kỳ điểm gọi AI nào:** Chat, tạo sinh, Agent, Canvas, ngân hàng câu hỏi, học liệu, tác vụ tự động dùng AI hoặc dùng nguồn tri thức.
- **Ưu tiên hướng dẫn thay vì từ chối** đối với yêu cầu hợp pháp, phù hợp giáo dục nhưng chưa rõ bối cảnh; chỉ chặn hành vi nằm ngoài quyền, vi phạm quy định rõ ràng hoặc rủi ro đáng kể.
- Mọi lời nhắc nhở/từ chối phải **lịch sự, trung tính, có lý do và dẫn đúng văn bản**; không suy diễn ý đồ, công kích hay quy kết người dùng.
- Chỉ ghi nhận **mức độ đáp ứng và bằng chứng thực tế**; không dùng nhãn “đã tuân thủ pháp luật hoàn toàn” khi chưa có đánh giá pháp lý/kiểm toán thích hợp.

---

## 2. Căn cứ và mức độ ràng buộc

| Mã | Nguồn | Nhóm yêu cầu liên quan | Phân loại |
|---|---|---|---|
| LT-705 | Quyết định **705/QĐ-THPTLT**, 29/10/2026 và **Quy tắc sử dụng AI** kèm theo, trang 1–6 | Mục đích, trách nhiệm, khai báo, dữ liệu, liêm chính, đánh giá, xử lý sự cố, phân công | **Chính sách trường** áp dụng tại Long Trường |
| AI-134 | [Luật Trí tuệ nhân tạo 134/2025/QH15](https://vanban.chinhphu.vn/?classid=1&docid=216334&pageid=27160) | Quản trị rủi ro, trách nhiệm, minh bạch, kiểm soát của con người | Pháp luật liên quan |
| AI-142 | [Nghị định 142/2026/NĐ-CP](https://vanban.chinhphu.vn/?docid=218029&pageid=27160) | Chi tiết thi hành Luật AI, phân loại và quản trị rủi ro | Pháp luật liên quan |
| AI-33 | [Quyết định 33/2026/QĐ-TTg](https://vanban.chinhphu.vn/?classid=0&docid=218658&pageid=27160) | Danh mục hệ thống AI có rủi ro cao; đặc biệt liên quan nội dung tự học/đánh giá/giám sát người học khi **đủ các điều kiện cụ thể** | Pháp luật liên quan; cần đánh giá theo use case |
| DP-91/356 | [Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15](https://vanban.chinhphu.vn/?classid=1&docid=214590&pageid=27160&typegroup=), [Nghị định 356/2025/NĐ-CP](https://vbpl.moj.gov.vn/bocongan/Pages/vbpq-thuoctinh.aspx?ItemID=187276) | Dữ liệu cá nhân, mục đích/phạm vi xử lý, trách nhiệm và an toàn | Pháp luật liên quan |
| IP-131 | [Luật sửa đổi Luật Sở hữu trí tuệ 131/2025/QH15](https://vanban.chinhphu.vn/?docid=216511&pageid=27160) | Quyền sử dụng nội dung, tài liệu và sản phẩm | Pháp luật liên quan |
| GD-2422/5588 | [Quyết định 2422/QĐ-BGDĐT và Công văn 5588/BGDĐT-GDPT](https://xaydungchinhsach.chinhphu.vn/quyet-dinh-so-2422-qd-bgddt-ve-khung-noi-dung-giao-duc-tri-tue-nhan-tao-ai-cho-hoc-sinh-pho-thong-119260820163256297.htm) | Năng lực AI, sử dụng an toàn/có đạo đức, kiểm chứng, vai trò người học | Định hướng sư phạm và triển khai |
| HCM-9261/10504 | Kế hoạch **9261/KH-SGDĐT** về giáo dục AI và [10504/KH-SGDĐT](https://thcsnguyentraigovap.hcm.edu.vn/ke-hoach/ke-hoach-trien-khai-nhiem-vu-cong-nghe-thong-tin-chuyen-doi-so-nam-hoc-2026-202/vbct/87239/766718) về CNTT/CĐS năm học 2026–2027 | Trách nhiệm triển khai tại cơ sở giáo dục, quản trị công cụ và dữ liệu | Định hướng Sở; cần đối chiếu bản ký và nội dung chi tiết trước khi khẳng định nghĩa vụ cụ thể |

**Lưu ý:** Những yêu cầu như gắn nhãn **từng câu hỏi**, tạo **hồ sơ giải trình cho mọi AI task** hoặc áp dụng một **chính sách xuyên suốt mọi Agent** là **đề xuất chuẩn sản phẩm BookForge để thực thi và chứng minh các nguyên tắc trên**, không được mặc định là câu chữ bắt buộc nguyên văn của từng văn bản.

### 2.1. Điểm quy tắc Long Trường tác động trực tiếp

- **Mục II, trang 1–2:** con người chịu trách nhiệm; minh bạch; liêm chính; bảo mật dữ liệu; bản quyền.
- **Mục III.1–III.3, trang 2–3:** phân biệt việc được dùng, được dùng có khai báo và không được dùng AI.
- **Mục IV.1–IV.3, trang 3–4:** phân loại dữ liệu, “5 không”, quy trình sử dụng AI 7 bước.
- **Mục IV.4–IV.5, trang 4:** khai báo AI, kiểm chứng nguồn và quy tắc riêng đối với kiểm tra đánh giá.
- **Mục V–VI, trang 4–5:** trách nhiệm giáo viên, nhân viên, học sinh.
- **Mục VII–VIII, trang 5–6:** xử lý sự cố; trách nhiệm lãnh đạo, tổ chuyên môn, CNTT và học sinh.

---

## 3. Phạm vi hoạt động phải bao phủ

**Ranh giới kiểm soát của MVP là tất cả các nghiệp vụ dùng AI**, không chỉ màn hình Chat.

| Điểm nghiệp vụ | Vấn đề tối thiểu phải bao phủ |
|---|---|
| **Tải file tri thức** | Xác nhận quyền sử dụng, nhận diện người upload, thời điểm, phạm vi sở hữu/quyền truy cập và trạng thái được phép dùng với AI theo khai báo |
| **OCR / chuẩn hóa / lập kho tri thức** | Ghi nhận tác vụ xử lý và quan hệ với file gốc; không nhầm xử lý tài liệu với việc được quyền công bố hoặc gửi tài liệu sang dịch vụ AI |
| **Chọn file tri thức tham chiếu** | Kiểm tra quyền người dùng đối với file và quyền sử dụng file cho mục đích đang thực hiện; ghi nhận lần sử dụng |
| **Chat with AI / hỏi đáp** | Kiểm tra yêu cầu theo bối cảnh, vai trò, phạm vi dữ liệu; biết câu trả lời có/không dùng tài liệu tham chiếu |
| **Agent sư phạm / Agent chuyên môn** | Không vượt quyền của người gọi; không bỏ qua quy tắc chung khi Agent gọi tiếp công cụ hoặc dùng tri thức |
| **Tạo học liệu / câu hỏi / đề / đáp án** | Nhận diện tính nhạy cảm của việc kiểm tra đánh giá; minh bạch nguồn và vai trò người kiểm duyệt |
| **Canvas và chỉnh sửa bằng AI** | Giữ dấu vết về phần nội dung được AI tạo hoặc AI chỉnh sửa qua các lần thao tác |
| **Slide / PPTX / DOCX / đầu ra khác** | Nhãn tạo sinh và nguồn tham chiếu có thể nhận diện khi xem lại hoặc xuất file |
| **Ngân hàng câu hỏi / đơn vị câu hỏi** | Mỗi đơn vị AI tạo có nguồn gốc riêng, không chỉ gắn nhãn ở cấp bộ đề; rõ tình trạng tham khảo/chờ chuyên môn duyệt |
| **Xuất bản / chia sẻ / sử dụng lại** | Không làm mất nhãn tạo sinh, mối liên hệ nguồn và giới hạn quyền; không đồng nhất “tạo được” với “được công bố” |

---

## 4. MVP 1 — Phạm vi tối thiểu cho Engineering/Development

### 4.1. Định nghĩa MVP

Một vòng kiểm soát và giải trình **đủ dùng, thống nhất**, áp dụng cho toàn bộ tác vụ AI hiện có. MVP ưu tiên **nhận diện quyền → xác nhận trách nhiệm → kiểm tra yêu cầu → tạo sinh trong giới hạn → gắn nhãn → truy vết**; **không** xây dựng một hệ thống GRC/pháp chế độc lập.

### 4.2. Backlog theo gói việc

| ID / mức | Vấn đề cần xử lý và giới hạn phạm vi | Kết quả nghiệm thu (ở góc độ sản phẩm) | Căn cứ |
|---|---|---|---|
| **M01 — P0** | **Không rõ ai đang dùng AI với tư cách nào.** Bao phủ danh tính đăng nhập, trường/Workspace, vai trò **học sinh – giáo viên – người quản trị AI của trường** và ranh giới quyền tương ứng. Không phát triển mô hình vai trò phức tạp trong MVP. | Cùng một yêu cầu/tài nguyên, quyền sử dụng được phân biệt theo vai trò; Agent không tự nâng quyền; có thể xác định vai trò tại thời điểm thực hiện. | LT II, III, V, VI, VIII |
| **M02 — P0** | **Thiếu cam kết của người upload và hồ sơ file.** Mọi lần upload file tri thức có xác nhận chủ động về quyền sở hữu hoặc quyền được phép sử dụng và trách nhiệm với tài liệu; nhận diện file, người upload, thời gian, phạm vi và khai báo ban đầu. **Không quét nội dung file để phán xét quyền upload.** | Không thể hoàn tất upload khi chưa xác nhận; có thể xem lại ai đã xác nhận điều gì, với file nào, vào thời điểm nào. Không hiển thị thông điệp “BookForge đã xác minh bản quyền”. | LT II, IV.1–IV.2, V |
| **M03 — P0** | **File được upload có thể bị dùng sai người/sai bối cảnh.** Bao phủ quyền truy cập, quyền chọn làm tri thức tham chiếu, tình trạng dữ liệu theo **khai báo của người dùng** và giới hạn của trường; lưu ý đề/đáp án chưa công bố, hồ sơ cá nhân, tài liệu hạn chế. Không thực hiện đánh giá pháp lý nội dung file. | Người không có quyền không sử dụng được file làm nguồn AI; file được tự khai báo thuộc diện không được đưa vào AI không thể được dùng như nguồn AI; mỗi lần sử dụng hợp lệ có thể truy vết. | LT III.3, IV.1–IV.2, V |
| **M04 — P0** | **Yêu cầu đưa vào AI thiếu kiểm soát ngữ cảnh.** Bao phủ mọi command/prompt có thể kích hoạt AI, xét mục đích sư phạm, quyền người dùng, hành vi bị cấm và nguy cơ lạm dụng. Không yêu cầu phán đoán ý định đạo đức của người dùng; không chặn chỉ vì chủ đề nhạy cảm nhưng được nghiên cứu hợp pháp. | Có phân biệt được yêu cầu phù hợp, yêu cầu cần giải thích/điều chỉnh và yêu cầu phải dừng; cùng một nguyên tắc áp dụng cho Chat, tạo sinh, Canvas và Agent. | LT II, III, IV.3–IV.5, VI |
| **M05 — P0** | **Các Agent/tác vụ AI có thể hoạt động ngoài chính sách chung.** Bao phủ toàn bộ tác vụ tạo sinh và các lần Agent sử dụng công cụ/tri thức, kế thừa phạm vi vai trò, tài nguyên và giới hạn đánh giá. Không phát triển hệ thống chính sách riêng cho từng Agent ở MVP. | Không có đường đi tác vụ AI hoặc hành động của Agent bỏ qua ranh giới quyền/chính sách; Agent không tự đưa ra quyết định kỷ luật hoặc kết quả đánh giá chính thức. | LT III.2–III.3, IV.5, V–VI |
| **M06 — P0** | **Đầu ra không rõ mức độ AI và nguồn gốc.** Bao phủ Chat answer, Canvas, Slide, PPTX, DOCX, học liệu, ngân hàng đề, **từng câu hỏi** và đầu ra của Agent. Phân biệt không dùng file tham chiếu, có dùng file, dùng hỗn hợp và nội dung được AI chỉnh sửa. | Với mỗi kết quả/đơn vị nội dung có thể biết đây là nội dung được AI hỗ trợ ở mức nào và nhận diện **đúng các file đã dùng**; nếu không có file thì ghi rõ không dùng nguồn tham chiếu, không bịa trích dẫn; nhãn không mất khi xuất/xem lại. | LT II, III.2, IV.4, V; chuẩn sản phẩm đề xuất |
| **M07 — P0** | **Thiếu bằng chứng lịch sử để giải trình.** Bao phủ tối thiểu: ai, vai trò, thời gian, file/tài nguyên liên quan, loại tác vụ, kết quả kiểm soát, đầu ra liên kết, người phê duyệt nếu có. Có thể tra cứu lịch sử sử dụng của **mỗi file** và nguồn của **mỗi sản phẩm** trong quyền cho phép. Không lưu tràn lan toàn bộ nội dung nhạy cảm chỉ để “đủ log”. | Trường có thể kiểm tra một file đã được upload khi nào, được dùng trong các tác vụ nào, bởi ai, tạo ra những kết quả nào; có thể giải trình một cảnh báo/từ chối dựa trên quy định đã áp dụng. | LT IV.3–IV.4, VII–VIII; chuẩn sản phẩm đề xuất |
| **M08 — P0** | **Thiếu cách truyền đạt quy tắc nhân văn và kiểm chứng bao phủ.** Bao phủ cảnh báo/từ chối đúng văn phong sư phạm, căn cứ điều khoản chính xác, quyền phản hồi/yêu cầu điều chỉnh; kiểm thử các hành trình trọng yếu qua vai trò và tất cả bề mặt AI. Không phát triển hệ thống khiếu nại hoặc kiểm toán nâng cao. | Không quy chụp, không công kích; lý do cụ thể, dẫn đúng mục quy tắc; không viện dẫn luật không chắc chắn; kiểm thử không phát hiện đường đi AI chính bị bỏ sót và không chặn sai hàng loạt các câu hỏi học tập hợp lệ. | LT II, III, IV.3–IV.4, VII |

**Các mục M01–M08 là một gói phát hành thống nhất.** Không xem việc bổ sung một dòng nhắc nhở vào prompt là hoàn thành kiểm soát ở những nơi người dùng, file hoặc Agent có thể vượt quyền.

### 4.3. Mức độ tối thiểu của các yêu cầu đặc biệt

**A. Cam kết khi tải file**  
Phạm vi chỉ cần làm rõ: người dùng **có quyền sở hữu hoặc đã được cho phép xử lý, tải lên và sử dụng nội dung cho mục đích đã khai báo**; không đưa lên tài liệu thuộc nhóm không được phép; người dùng chịu trách nhiệm về thông tin khai báo. BookForge ghi nhận lời xác nhận, **không xác nhận thay người dùng**. Việc kiểm soát dữ liệu cá nhân, đề thi chưa công bố và nghĩa vụ của bên cung cấp dịch vụ vẫn là vấn đề phải quản trị độc lập, không được “miễn trừ” bằng checkbox.

**B. Phân biệt vai trò tối thiểu**  
- **Học sinh:** AI hỗ trợ hiểu, luyện tập, phản biện và sáng tạo trong phạm vi giáo viên cho phép; không làm thay bài kiểm tra/bài thi hoặc tự truy cập tài liệu hạn chế.
- **Giáo viên:** có thể tạo học liệu, câu hỏi, đề, tiêu chí và nhận xét tham khảo trong quyền được cấp; chịu trách nhiệm kiểm tra nội dung và quyết định đánh giá cuối cùng.
- **Người quản trị AI của trường:** quản trị tài khoản, quyền và kiểm tra bằng chứng trong phạm vi nhà trường; **không** vì là quản trị viên mà được tự động đọc mọi dữ liệu nhạy cảm hoặc thay giáo viên ra quyết định chuyên môn.
- **Vận hành BookForge:** trách nhiệm vận hành dịch vụ được phân định với quyền quản trị nghiệp vụ nhà trường; không mặc nhiên có quyền truy cập nội dung tri thức của trường.

**C. Nhãn nguồn gốc tạo sinh tối thiểu**  
1. **AI — không dùng tài liệu tham chiếu:** kết quả từ mô hình/công cụ AI, **không có nguồn file**; không diễn đạt như thể mô hình là một nguồn học thuật được kiểm chứng.
2. **AI — có tài liệu tham chiếu:** xác định tài liệu/file thực tế tham gia tác vụ; việc dùng file **không** bảo đảm mọi câu trong đầu ra đều được file chứng minh.
3. **AI — nguồn hỗn hợp:** có tài liệu tham chiếu nhưng kết quả còn chứa nội dung suy luận/tạo sinh từ mô hình; tránh nhãn “100% từ nguồn”.
4. **AI — đã tiếp tục chỉnh sửa:** nội dung bắt nguồn từ kết quả AI và được tiếp tục sửa bằng AI hoặc người dùng; chỉ ghi nhận mức can thiệp **thực sự có thể quan sát**, không tự khẳng định người dùng đã kiểm chứng chuyên môn.

**D. Trạng thái xử lý command tối thiểu**  
- **Phù hợp:** được hỗ trợ bình thường.
- **Cần làm rõ/điều chỉnh:** hướng dẫn người dùng thu hẹp phạm vi dữ liệu, xác định mục đích hoặc đề nghị cách đặt yêu cầu an toàn hơn; không mặc định từ chối.
- **Không thể hỗ trợ trong bối cảnh hiện tại:** dừng tác vụ bị cấm/vượt quyền và nêu lý do chính xác, bình tĩnh, có dẫn chiếu phù hợp. Từ chối hành vi, không phán xét con người.

**E. Ranh giới người duyệt**  
Tạo câu hỏi, tiêu chí, đáp án hoặc nhận xét **không đồng nghĩa** với phê duyệt chính thức. Nếu sản phẩm chưa được người có thẩm quyền rà soát, BookForge không được thể hiện như đã được phê duyệt để đánh giá/kỷ luật/xếp loại học sinh.

### 4.4. Dữ liệu/bằng chứng tối thiểu phải giải trình được

| Đối tượng | Câu hỏi giải trình bắt buộc |
|---|---|
| **File tri thức** | File nào? Ai upload? Lúc nào? Đã cam kết gì? Thuộc phạm vi nào? Được dùng trong những tác vụ nào? |
| **Tác vụ AI** | Ai thực hiện? Trong vai trò nào? Khi nào? Loại tác vụ? Được phép/được hướng dẫn/bị dừng vì sao? Dùng những file nào? |
| **Agent** | Agent nào thực hiện? Dưới quyền của ai? Có sử dụng tài nguyên/công cụ nào? Có kết quả nào tạo ra? |
| **Sản phẩm AI** | Loại nội dung gì? Nhãn nguồn gốc nào? File tham chiếu nào (nếu có)? Liên quan tới tác vụ nào? Có/không có xác nhận chuyên môn? |
| **Quyết định chính sách** | Dựa vào mục/quy định nào và phiên bản chính sách nào? Người dùng được thông báo thế nào? |

**Bảo vệ log:** quyền xem log phải phù hợp vai trò và mục đích; không mặc nhiên cung cấp prompt/tài liệu/hồ sơ riêng tư cho mọi quản trị viên.

### 4.5. Các ca nghiệm thu bắt buộc (không phải hướng dẫn cách triển khai)

1. Giáo viên upload tài liệu và xác nhận quyền; lịch sử upload được ghi nhận.
2. Học sinh không có quyền chọn tài liệu nội bộ của giáo viên làm nguồn hỏi đáp.
3. Người dùng tự khai báo file thuộc loại không được đưa vào AI; tác vụ dùng file đó cho AI không được tiếp tục.
4. Giáo viên dùng file được phép để tạo câu hỏi; mỗi câu hỏi có nhãn AI và chỉ dẫn về file tham chiếu thực tế.
5. Câu hỏi không dùng file có nhãn nguồn AI không tham chiếu, **không có trích dẫn tài liệu giả**.
6. Nội dung hỗn hợp (AI + file) không được khẳng định toàn bộ đã có chứng cứ nguồn.
7. Học sinh yêu cầu làm thay toàn bộ bài kiểm tra cá nhân; tác vụ bị giới hạn kèm giải thích sư phạm, không phán xét.
8. Học sinh hỏi kiến thức về chủ đề khó hoặc tranh luận học thuật hợp pháp; vẫn được hỗ trợ trong bối cảnh học tập phù hợp.
9. Agent và Chat nhận cùng người dùng/tài nguyên thì không có khác biệt vô căn cứ về phạm vi quyền.
10. Canvas chỉnh sửa nội dung AI hoặc xuất PPTX/DOCX không làm mất dấu gốc tạo sinh.
11. Giáo viên yêu cầu AI tự quyết định xếp loại/kỷ luật học sinh; BookForge không đưa ra quyết định thay người có thẩm quyền.
12. Người quản trị được cấp quyền có thể truy ngược từ một file đến các lần dùng AI và từ một đầu ra đến file liên quan; người không có quyền không xem được dữ liệu riêng tư trong log.

### 4.6. Ngoài phạm vi MVP 1

Không đưa vào MVP: kiểm định/giám định bản quyền file; quét nội dung file tự động để phán xét upload; phân tích pháp lý tự động theo từng văn bản; DLP sâu; hệ thống cấu hình chính sách đa tầng cho hàng trăm trường; kiểm định sự thật toàn bộ đầu ra; đánh giá rủi ro tự động nâng cao; chấm điểm/kỷ luật học sinh tự động; kiểm toán pháp lý độc lập; báo cáo quản trị phức tạp; workflow duyệt nhiều cấp; chứng nhận hệ thống AI rủi ro cao.

**Giới hạn phải công bố trung thực:** MVP quản lý cam kết, quyền, phạm vi sử dụng và dấu vết. Do không kiểm tra nội dung file để phán xét upload, nó **không thể tự phát hiện mọi file bị khai báo sai**, và vì thế không thể tự tuyên bố phát hiện/chặn toàn bộ vi phạm về bản quyền, dữ liệu cá nhân hoặc tài liệu mật.

---

## 5. Phase 2 — Định hướng năng lực nền tảng

**Vai trò của Phase 2:** nâng độ tin cậy, tính thích ứng giữa các trường và khả năng giải trình sâu, **không thay đổi nguyên tắc “hỗ trợ thay vì kiểm duyệt máy móc”**. Các nhóm dưới đây là **phạm vi vấn đề tương lai**, không ấn định giải pháp kỹ thuật.

| ID | Năng lực cần mở rộng | Vấn đề/ranh giới Phase 2 | Quan hệ với MVP |
|---|---|---|---|
| **P2-01** | **Chính sách theo từng cơ sở giáo dục** | Khác biệt giữa quy tắc trường, cấp học, lớp, loại hoạt động, mức độ cho phép AI; tính hiệu lực và thay đổi phiên bản; trách nhiệm xác nhận chính sách của trường. | Nâng phạm vi M01/M04/M08, không phá lịch sử giải trình cũ. |
| **P2-02** | **Quản trị vòng đời và điều kiện sử dụng tri thức** | Phân biệt quyền sở hữu, giấy phép, phạm vi khai thác, quyền chia sẻ/xuất bản, thời hạn và tình trạng rút quyền; có thể giải trình tài liệu dẫn tới sản phẩm sau khi đổi quyền/xóa. Không áp dụng chế độ quét/đánh giá file bắt buộc tại upload trái định hướng sản phẩm. | Mở rộng M02/M03/M07. |
| **P2-03** | **Minh bạch nguồn và chất lượng nội dung theo chiều sâu** | Mức độ chứng cứ của từng nhận định, nguồn không hỗ trợ kết luận, nội dung hết hạn, khả năng sai lệch hoặc thiên kiến; ranh giới giữa trích dẫn chính xác và suy luận mô hình. | Nâng M06; không hứa “mọi câu đều đúng”. |
| **P2-04** | **Quản trị Agent theo năng lực và hành động** | Agent có chuỗi nhiệm vụ dài, tương tác nhiều công cụ và nhiều tài nguyên; quyền của người ủy nhiệm, giới hạn hành động, hành vi vượt quyền, điểm cần người xác nhận. | Phát triển M05 nhưng vẫn kế thừa chính sách chung. |
| **P2-05** | **Human review & liêm chính học thuật** | Quyền và trách nhiệm duyệt học liệu, đề, đáp án, đánh giá; khai báo mức dùng AI của học sinh; chứng cứ quá trình học tập và phản hồi khi có nghi vấn, tránh dùng dấu hiệu “giống AI” làm chứng cứ duy nhất. | Phát triển M06/M07; không tự động kết tội gian lận. |
| **P2-06** | **Giám sát, sự cố và khả năng giải trình cấp trường** | Sự cố dữ liệu, nội dung không phù hợp, quyền riêng tư và bản quyền; các bước tiếp nhận, xử lý, khắc phục; báo cáo có kiểm soát quyền truy cập, thống kê không xâm phạm học sinh. | Nâng M07/M08. |
| **P2-07** | **Đánh giá rủi ro theo use case và nghĩa vụ pháp lý** | Rà soát điều kiện để hệ thống/hoạt động thuộc danh mục AI rủi ro cao, tác động tới người học, quy mô triển khai, dữ liệu và kết quả đánh giá chính thức; xây dựng hồ sơ tuân thủ tương ứng khi có căn cứ. | Ranh giới pháp lý bao trùm MVP/Phase 2; không gắn nhãn rủi ro cao theo suy đoán. |
| **P2-08** | **Chất lượng sư phạm và trải nghiệm nhân văn** | Chất lượng cảnh báo, nguy cơ chặn nhầm, sự công bằng giữa nhóm người học, khả năng hỗ trợ người dùng sửa yêu cầu, năng lực học tập/sáng tạo; đánh giá và cải tiến dựa trên phản hồi có trách nhiệm. | Mở rộng M04/M08 và mục tiêu giáo dục từ GD-2422/5588. |

### 5.1. Những yêu cầu định hướng MVP phải giữ để Phase 2 kế thừa

1. **Danh tính, quyền và phạm vi trường** phải luôn phân biệt được, kể cả khi sau này có Agent hoặc tích hợp mới.
2. **Một file có lịch sử riêng**, không bị mất dấu qua việc dùng làm nguồn, thay đổi tên, cập nhật hoặc rút quyền.
3. **Mỗi tác vụ AI có dấu vết riêng**, đủ liên kết người dùng – dữ liệu – kết quả – căn cứ chính sách.
4. **Mỗi đầu ra có nguồn gốc riêng**, kể cả các đơn vị nhỏ như câu hỏi và phần nội dung Canvas.
5. **Chính sách có thể thay đổi theo thời gian** nhưng hồ sơ giải trình của tác vụ đã xảy ra phải giữ được ngữ cảnh chính sách tại thời điểm đó.
6. **Chính sách giới hạn quyền của Agent** phải nhất quán với quyền của người sử dụng và chủ sở hữu tài nguyên.
7. **Không xóa nhòa vai trò con người** trong phê duyệt học liệu, kết quả đánh giá và xử lý sự cố.
8. **Không lạm dụng dữ liệu giám sát** để đánh giá tâm lý, xếp hạng hoặc quy kết hành vi học sinh.

### 5.2. Ngưỡng chuyển từ MVP sang Phase 2

Phase 2 chỉ nên ưu tiên khi xuất hiện nhu cầu thực tế: trường thứ hai có quy tắc khác; khối lượng Agent tăng; quy trình duyệt học liệu trở nên thiết yếu; có hoạt động đánh giá tác động chính thức; có sự cố phải xử lý/giải trình; hoặc điều kiện triển khai làm phát sinh nghĩa vụ pháp lý mới. **Không mở Phase 2 chỉ vì cần nhiều tính năng quản trị hơn trên giấy.**

---

## 6. Ranh giới trách nhiệm giữa các nhóm

| Nhóm phụ trách | Phạm vi cần làm rõ/chịu trách nhiệm về kết quả | Ngoài phạm vi quyết định độc lập |
|---|---|---|
| **Product / BA** | Danh mục tác vụ AI, từng hành vi được/không được, ngôn ngữ quy tắc, tình huống nghiệp vụ, tiêu chí nghiệm thu và mapping chính sách | Không tự diễn giải pháp luật như cơ quan có thẩm quyền |
| **Engineering Lead** | Không bỏ sót các điểm sử dụng AI; ranh giới trách nhiệm xuyên chức năng; tính nhất quán của hồ sơ giải trình | Không tự quyết định thay trường về quyền với dữ liệu nội bộ |
| **Backend / Development** | Phạm vi danh tính, quyền, lịch sử file/tác vụ, liên kết kết quả và dữ liệu, khả năng tra cứu theo quyền | Không xác nhận tính hợp pháp của file dựa vào checkbox |
| **AI Engineering** | Phạm vi kiểm soát yêu cầu và đầu ra trên Chat/tạo sinh/Agent; phân biệt nguồn thực tế và suy luận; chất lượng cảnh báo sư phạm | Không cho AI ra quyết định học vụ/kỷ luật thay con người |
| **Frontend / Development** | Tính rõ ràng của cam kết upload, trạng thái quyền, nhãn AI/nguồn, thông điệp giải thích và khả năng xem bằng chứng phù hợp | Không thay đổi ý nghĩa văn bản pháp lý bằng cách diễn đạt tùy tiện |
| **QA/QC** | Kiểm thử quyền, nguồn, truy vết, tình huống bị cấm, chặn nhầm và sự đồng nhất giữa bề mặt tác vụ | Không xác nhận sản phẩm “tuân thủ pháp luật hoàn toàn” chỉ dựa trên test pass |
| **Đại diện nhà trường / chuyên môn / pháp chế (khi cần)** | Xác nhận quy tắc địa phương, quyền sử dụng tài liệu, tình huống kiểm tra đánh giá, yêu cầu giải trình và kết quả rà soát pháp lý | Không chuyển toàn bộ trách nhiệm chuyên môn sang nhà cung cấp phần mềm |

### 6.1. Trình tự ưu tiên cho đợt MVP

**Đợt A — Bắt buộc để có ranh giới trách nhiệm:** M01, M02, M03.  
**Đợt B — Bắt buộc để không có lối vòng qua chính sách:** M04, M05.  
**Đợt C — Bắt buộc để giải trình được sản phẩm AI:** M06, M07.  
**Cửa phát hành — Bắt buộc:** M08 và toàn bộ ca nghiệm thu mục 4.5.

Trình tự chỉ thể hiện **phụ thuộc nghiệp vụ**, không chỉ định số sprint, công nghệ, cơ sở dữ liệu, prompt hay mô hình AI.

---

## 7. Definition of Done — Khi nào MVP đủ để giới thiệu cho trường?

MVP chỉ được mô tả là **“có cơ chế quản trị và giải trình hoạt động AI theo phạm vi đã công bố”** khi đồng thời thỏa mãn:

- [ ] Có cam kết người upload, lưu nhận diện người upload và lịch sử của mỗi file tri thức.
- [ ] Quyền của học sinh, giáo viên, quản trị viên trường được phân biệt và có tác dụng thực tế với tài nguyên/tác vụ AI.
- [ ] Có phân biệt file được lưu trên BookForge và file được phép đưa vào tác vụ AI.
- [ ] Mọi tác vụ Chat/tạo sinh/Canvas/Agent và các nghiệp vụ dùng AI khác trong phạm vi phát hành đều nằm trong ranh giới kiểm soát chung.
- [ ] Có thể dừng yêu cầu vượt quyền/bị cấm và hướng dẫn lại yêu cầu chưa rõ theo ngôn ngữ sư phạm, viện dẫn đúng quy tắc.
- [ ] Không tự động đưa ra quyết định đánh giá hoặc kỷ luật học sinh thay người có thẩm quyền.
- [ ] Tất cả sản phẩm AI, kể cả câu hỏi đơn lẻ, có nhãn AI và nguồn tham chiếu **đúng mức độ có thể chứng minh**.
- [ ] Có thể giải trình từ file → các lần sử dụng → kết quả và từ kết quả → tác vụ → file, theo phân quyền.
- [ ] Có kiểm thử các ca bình thường, vi phạm, quyền hạn, nguồn hỗn hợp, thiếu nguồn và chặn nhầm.
- [ ] Nhà trường được thông tin rõ về giới hạn: không giám định bản quyền/độ sạch dữ liệu tại upload; checkbox không thay nghĩa vụ pháp lý; AI không bảo đảm đầu ra luôn chính xác.

### Quyết định sản phẩm cần thống nhất trước khi nghiệm thu

1. **Định nghĩa chính thức** của ba vai trò MVP và người có thẩm quyền duyệt từng loại học liệu/kết quả.
2. **Mức dữ liệu do người dùng tự khai báo**, trường hợp tuyệt đối không được đưa vào AI và trường hợp phải có quyền/phê duyệt phù hợp.
3. **Danh sách đầy đủ các điểm gọi AI đang có** của BookForge tại thời điểm phát hành; không thể tuyên bố “mọi hoạt động” nếu chưa kiểm kê.
4. **Ngữ nghĩa của từng nhãn nguồn** và giới hạn của việc trích dẫn file.
5. **Phạm vi thông tin trong log, ai được xem, thời hạn lưu và việc xử lý khi xóa/rút quyền**, cần đối chiếu chính sách dữ liệu và hợp đồng thực tế.
6. **Nguồn quy tắc/điều khoản được phép viện dẫn tự động**, ưu tiên chính sách nhà trường đã xác nhận và văn bản pháp luật đã kiểm tra hiệu lực.

---

## 8. Cách diễn đạt giá trị BookForge với nhà trường

> **BookForge hỗ trợ thực thi quy tắc sử dụng AI của nhà trường bằng cơ chế xác định vai trò, kiểm soát phạm vi sử dụng tri thức, ghi nhận cam kết người tải tài liệu, hướng dẫn yêu cầu AI phù hợp bối cảnh sư phạm, minh bạch nguồn gốc nội dung tạo sinh và lưu dấu vết hoạt động để giải trình theo quyền được cấp.** Nhà trường và người dùng vẫn giữ trách nhiệm chuyên môn, quyền quyết định và nghĩa vụ pháp lý tương ứng. BookForge không tự nhận đã xác minh quyền sở hữu tài liệu, không thay thế giáo viên trong quyết định đánh giá và không xem cơ chế kiểm soát là lý do để hạn chế việc học hỏi hợp pháp.

**Không sử dụng trong tài liệu thương mại MVP:** “BookForge bảo đảm 100% tuân thủ mọi quy định”; “AI đã xác minh bản quyền file”; “Mọi nội dung đã được kiểm chứng tuyệt đối”; “Có thể để Agent tự chịu trách nhiệm thay giáo viên”.

---

## 9. Tài liệu tham chiếu và lưu ý xác minh

**Nguồn cơ sở (người dùng cung cấp):**

1. `705.LT.QĐ ban hanh Quy tắc sử dụng trí tuệ nhân tạo (AI) 2026 - 2027.pdf` — Quyết định **705/QĐ-THPTLT**, ngày 29/10/2026, 1 trang.
2. `705.LT.Quy tắc ứng dụng AI năm học 2026-2027.pdf` — Quy tắc sử dụng AI kèm Quyết định 705, 6 trang. Bản `.docx` là tài liệu cùng nội dung dùng để đối chiếu.

**Nguồn công khai bổ trợ:** xem liên kết ở bảng mục 2. Văn bản của Bộ/Sở cung cấp nền tảng chính sách; các ràng buộc sản phẩm đề xuất trong kế hoạch là **diễn giải nghiệp vụ để hỗ trợ thực thi**, không thay thế văn bản gốc hoặc ý kiến của pháp chế.

**Điểm phải đánh giá riêng trước khi triển khai lớn:** tiêu chí **AI rủi ro cao** theo Quyết định 33/2026/QĐ-TTg, nhất là trường hợp nội dung tự học quy mô lớn với nguồn không kiểm soát, tự động đánh giá chính thức hoặc giám sát hành vi người học. Không suy đoán BookForge thuộc/không thuộc danh mục khi chưa đối chiếu đầy đủ use case và các điều kiện áp dụng.

**Kết luận:** **MVP xây dựng khả năng *chứng minh đã xử lý một tác vụ AI có trách nhiệm***. **Phase 2 phát triển khả năng *quản trị, đánh giá và cải tiến chính sách có trách nhiệm ở quy mô nhiều trường***. Cả hai giai đoạn cùng bảo vệ mục tiêu cao nhất: con người giữ quyền chủ động, AI mở rộng khả năng học tập và sáng tạo.
