# 01 — Brief khảo sát: Thinking Chat Agent (hiển thị quá trình suy luận & tool log theo thời gian thực)

## Mục tiêu tính năng
- Cho người dùng thấy **quá trình** AI ra đáp án, không chỉ đáp án: chuỗi bước tư duy, tài liệu/công cụ đã dùng, bước nào thất bại và đổi hướng.
- Ba khối UI: **Summary Bar** (tóm tắt số lượng hoạt động), **Execution Timeline** (thinking steps + knowledge/tool logs + status indicators), phát dần theo thời gian thực trong lúc AI đang chạy.
- Đối tượng chính: người học (giá trị giáo dục — hiểu "tại sao ra đáp án đó"); ràng buộc đã biết: hệ thống đã có 2 luồng chat riêng (canvas trong `editor.py` và chat ngoài canvas trong `chat.py`), cả hai đã có endpoint SSE.
- Người dùng nói **thay thế hoàn toàn giao diện Chat hiện tại** — tức đây không phải panel phụ, mà là đổi khuôn hiển thị của message.
- **KHÔNG làm ở vòng này**: thay đổi chất lượng lời giải/mô hình, thêm công cụ giải toán mới (SymPy…) nếu hiện chưa có, hay đụng tới luồng sinh câu hỏi/đề thi trong `question_bank`.

## Phía dự đoán
Cả hai — và phần nặng nhất nhiều khả năng ở **BE** (phải có dữ liệu bước để phát ra; nếu agent hiện không lặp vòng và không gọi tool thì không có gì để hiển thị, FE làm đẹp cũng vô nghĩa). FE là tầng tiêu thụ event + render timeline + replay khi tải lại phiên.
**Đây mới là dự đoán. Claude Code chốt lại sau khảo sát.**

## Giả định cần kiểm chứng
- Tôi đang giả định luồng chat hiện tại **đã** có agent loop nhiều vòng và có gọi tool (retrieval, đọc tài liệu), chỉ là không phát các bước đó ra ngoài. Nếu thực tế là một lượt gọi LLM thẳng, phạm vi phình từ "hiển thị" thành "xây agent".
- Tôi đang giả định hai endpoint `POST /assistant/stream` (editor) và `POST /messages/stream` (chat) đã phát SSE nhiều loại event, nên thêm loại event mới là mở rộng chứ không phải dựng kênh mới.
- Tôi đang giả định `retrieval_traces` ghi lại nguồn tài liệu đã truy hồi và đủ để dựng dòng "Đọc tài liệu: X".
- Tôi đang giả định `canvas_chat_messages` / `chat_messages` hiện chỉ lưu nội dung cuối cùng, nên timeline muốn xem lại sau khi tải lại trang thì phải thêm chỗ lưu.
- Tôi đang giả định hai màn chat (canvas và ngoài canvas) dùng chung component render ở FE; nếu là hai bản riêng thì chi phí FE nhân đôi.
- Tôi đang giả định "thinking steps" lấy từ reasoning của mô hình (`LLM_OP_*_REASONING_EFFORT` gợi ý điều này), chứ không phải văn bản do một prompt phụ sinh ra.

## Câu hỏi khảo sát

### Cụm [BE]
- **Q1. [ĐỊNH VỊ][BE]** Khi người dùng gửi một câu hỏi trong chat của canvas (`POST /api/documents/{document_id}/editor/assistant/stream`), luồng đi qua những hàm/module nào từ endpoint tới lúc gọi mô hình? Trong đó có **vòng lặp nhiều bước** (agent loop) hay chỉ một lần gọi LLM rồi trả về?
- **Q2. [ĐỊNH VỊ][BE]** Hai endpoint SSE của chat (`editor.py` `/assistant/stream` và `chat.py` `/messages/stream`) hiện phát ra **những loại event nào** — liệt kê tên event và shape payload từng loại. Có event nào đang mang thông tin trung gian (tool đang chạy, nguồn tài liệu, trạng thái) mà FE chưa dùng không?
- **Q3. [ĐỊNH VỊ][BE]** Ở lớp gọi LLM dùng chung, khi mô hình trả về phần reasoning/thinking, code hiện **nhận và làm gì** với nó (bỏ đi, log, hay stream ra)? Những `LLM_OP_*` nào đang có `*_REASONING_EFFORT` được set khác mặc định cho luồng chat/editor?
- **Q4. [ĐỊNH VỊ][BE]** Agent chat gọi được những **công cụ (tool) nào** — khai báo ở đâu, tên từng tool là gì, và mỗi lần gọi tool thì đối số/kết quả có được ghi lại ở đâu không (DB, log, hay chỉ nằm trong bộ nhớ của request)?
- **Q5. [XÁC MINH][BE]** Bảng `retrieval_traces` (`models/document.py`) có những cột nào, được ghi ở bước nào của luồng chat, và có liên kết được tới **từng message** (chứ không chỉ tới `documents.id`) không?
- **Q6. [XÁC MINH][BE]** `canvas_chat_messages` và `chat_messages` hiện có những cột nào? Có cột JSON/text tự do nào có thể đính kèm dữ liệu timeline không, hay phải thêm cột/bảng mới?
- **Q7. [XÁC MINH][BE]** `chat.py` và `editor.py` dùng **chung một lớp agent/service** hay là hai bản triển khai riêng? Nếu chung thì tên module đó là gì và điểm nào là chỗ duy nhất cần chèn để phát event bước.
- **Q8. [XÁC MINH][BE]** Khi tải lại một phiên cũ (`GET /api/chat/sessions/{session_id}` và `GET /api/documents/{document_id}/editor/chat/sessions/{session_id}`), response trả về những trường gì cho **mỗi message**? Có đủ để dựng lại timeline sau khi F5 không?

### Cụm [FE]
- **Q9. [ĐỊNH VỊ][FE]** Trong màn chat của canvas, chỗ nào **nhận từng chunk SSE và đẩy vào state** — component/hook nào, và kiểu dữ liệu (type/interface) của một message trong state đó là gì?
- **Q10. [XÁC MINH][FE]** `src/lib/read-sse-stream` có chữ ký thế nào, và khi gặp một **loại event chưa biết** thì nó bỏ qua, ném lỗi, hay ngắt stream? (Quyết định việc thêm event mới có phá client cũ không.)
- **Q11. [ĐỊNH VỊ][FE]** Giao diện chat trong canvas và giao diện chat ngoài canvas là **một component dùng chung** trong `src/components/Chat` hay hai bản riêng ở hai template? Nếu chung, chỗ render một bong bóng message nằm ở file nào?
- **Q12. [XÁC MINH][FE]** `use-chat-modes` + `GET /api/chat/modes` đang trả về những mode nào và mode ảnh hưởng gì tới cách render message? (Để biết timeline nên bật cho mọi mode hay chỉ một số.)

## Cần trích nguyên văn
- Chữ ký hàm handler của hai endpoint chat dạng stream, và chữ ký của hàm/lớp agent mà chúng gọi vào.
- Danh sách đầy đủ **tên event SSE + shape payload** của cả hai luồng stream, dạng nguyên văn.
- Định nghĩa model của bảng lưu message chat trong canvas và message chat ngoài canvas — **liệt kê cột và kiểu**.
- Định nghĩa model của bảng lưu vết truy hồi, bảng lưu hành động AI, và bảng nhật ký sự kiện — liệt kê cột và kiểu (để biết dữ liệu timeline có sẵn tới đâu).
- Khai báo tool của agent chat: tên tool + schema tham số của từng tool.
- Kiểu TypeScript của một message trong state chat ở FE, và kiểu response của API lấy chi tiết một phiên chat.
- Chữ ký hàm đọc SSE ở FE.
- Giá trị hiện tại và nơi sử dụng của các biến môi trường chi phối vòng lặp agent: giới hạn số request, giới hạn số lần gọi tool, timeout một lượt của editor, cùng cờ mở rộng ngân sách agent và cờ liên quan tới công cụ tài liệu trong chat.

## Ngưỡng dừng
Đủ thông tin để chốt thiết kế khi trả lời được cả ba câu:
1. **Có dữ liệu bước hay không** — agent hiện có lặp vòng và gọi tool không, và mỗi bước hiện đang bị bỏ đi ở điểm nào trong code (tên hàm cụ thể).
2. **Kênh truyền** — thêm loại event vào SSE hiện có là đủ, hay phải sửa giao thức; và client cũ có vỡ khi gặp event lạ không.
3. **Chỗ lưu** — timeline chỉ sống trong lúc stream, hay phải persist; nếu persist thì vào cột/bảng nào và ai đọc lại.
Kèm điều kiện: biết rõ hai luồng chat dùng chung hay tách, ở cả BE lẫn FE — vì nó quyết định khối lượng công việc gấp đôi hay không.

---

## Câu hỏi cho bạn (nghiệp vụ — chỉ bạn trả lời được)
1. **Phạm vi lần này**: làm cho chat trong canvas trước, hay cả chat ngoài canvas cùng lúc? ("thay thế hoàn toàn giao diện Chat hiện tại" có bao gồm cả hai không?)
2. **Người xem timeline là ai**: học sinh (cần ngôn ngữ giáo dục, ẩn chi tiết kỹ thuật) hay cả giáo viên/người quản trị (muốn thấy cả tên tool, lỗi thật, số token)? Nếu cả hai thì có cần mức hiển thị khác nhau không?
3. **Sau khi trả lời xong**: timeline cần **xem lại được** khi mở lại phiên chat cũ, hay chỉ cần hiện lúc AI đang chạy rồi thu gọn/biến mất? (Đây là điểm quyết định có phải thêm chỗ lưu trong DB hay không, ảnh hưởng lớn tới khối lượng.)
4. **Mặc định hiển thị**: timeline mở sẵn toàn bộ, hay mặc định thu gọn thành Summary Bar và người dùng bấm mới xem chi tiết?
5. **Đánh đổi bạn chấp nhận**: nếu để AI thực sự đi nhiều bước (thử — sai — đổi phương pháp) thì câu trả lời sẽ **chậm hơn và tốn token hơn** so với hiện tại. Bạn chấp nhận chậm hơn tới mức nào, và nếu buộc phải chọn: (a) thật sự chạy nhiều bước, hay (b) giữ tốc độ hiện tại và chỉ trình bày minh bạch những gì hệ thống vốn đã làm?