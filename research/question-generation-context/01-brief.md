# 01 — Brief khảo sát: Ô nhập ngữ cảnh khi tạo câu hỏi trong thư mục câu hỏi

## Mục tiêu tính năng

- Ở Ngân hàng câu hỏi → thư mục câu hỏi, khi tạo câu hỏi bằng AI, người dùng có thêm **một ô văn bản tự do** để mô tả ý muốn (vai trò, lớp, chủ đề, số lượng, mức độ, chương trình…).
- Câu hỏi sinh ra phải bám theo ngữ cảnh đó, bên cạnh các ô chọn đang có (Loại câu hỏi: tự luận / trắc nghiệm / điền vào chỗ trống – trả lời ngắn).
- Người dùng muốn các ô chọn hiện tại (ví dụ thang Bloom, mức độ nhận thức) **vẫn được tuân thủ** khi ngữ cảnh nhắc tới chúng — quy tắc ưu tiên cụ thể chưa chốt.
- Ràng buộc và "Không làm lần này": `00-desc.md` **chưa ghi** — vòng khảo sát sẽ không tự giới hạn phạm vi, chỉ nêu rủi ro nếu gặp.

## Phía dự đoán

Cả hai — **mới là dự đoán**. FE chắc chắn phải thêm ô nhập; BE phải sửa nếu API sinh câu hỏi chưa nhận trường văn bản tự do. Claude Code chốt lại sau khi đọc code.

## Giả định cần kiểm chứng

- Tôi đang giả định màn hình "tạo câu hỏi hàng loạt" gọi `POST /api/question-cards/generate`. *Nếu sai:* phải định vị luồng sinh câu hỏi khác, các câu hỏi BE bên dưới đổi đích.
- Tôi đang giả định "Tạo câu hỏi mới" (tên tính năng) và "tạo câu hỏi hàng loạt" (hiện trạng) là **cùng một** hộp thoại. *Nếu sai:* có hai chỗ phải thêm ô, phạm vi FE gấp đôi.
- Tôi đang giả định request của `/generate` **chưa có** trường văn bản tự do nào. *Nếu sai* (đã có mà FE không hiển thị): việc gần như chỉ còn phía FE.
- Tôi đang giả định việc sinh chạy **đồng bộ trong request**, không qua job nền. *Nếu sai:* payload của job cũng phải mang ngữ cảnh, thêm một điểm sửa.
- Tôi đang giả định các ô chọn hiện tại (loại, Bloom, mức độ nhận thức) được chèn vào prompt và/hoặc ép ở tầng kiểm tra output. *Đây là chỗ quyết định* "ô chọn thắng ngữ cảnh" làm được bằng prompt hay bằng kiểm tra cứng.
- Tôi đang giả định số lượng câu sinh ra do tham số quyết định, không do prompt. *Nếu sai:* ngữ cảnh ghi "10 câu" có thể làm lệch số câu thực tế.
- Tôi đang giả định thẻ câu hỏi sinh ra **không lưu lại** tham số đầu vào. *Nếu sai:* có thể phải lưu thêm ngữ cảnh, đụng bảng `question_cards`.

## Câu hỏi khảo sát

**[BE]**

1. **[XÁC MINH][BE]** `POST /api/question-cards/generate` nhận request schema gồm những trường nào (loại câu hỏi, số lượng, mức Bloom / mức độ nhận thức, thư mục, tài liệu nguồn, node khung kiến thức…)? Đã có trường văn bản tự do nào (kiểu prompt / instruction / context) chưa? Chạy đồng bộ hay đẩy job nền?
2. **[ĐỊNH VỊ][BE]** Từ handler `/generate` tới lời gọi LLM, prompt được dựng ở hàm / file nào? Từng tham số của request được chèn vào prompt ra sao, có tách phần system (cố định) và phần theo request không?
3. **[ĐỊNH VỊ][BE]** Nội dung câu hỏi hôm nay được sinh dựa trên nguồn gì — tài liệu trong hệ thống (truy hồi RAG), node khung kiến thức / năng lực, hay chỉ các tham số chọn?
4. **[ĐỊNH VỊ][BE]** Sau khi LLM trả về, output được parse / kiểm tra ở đâu? Có ép cứng loại câu hỏi, số lượng câu, mức Bloom ở tầng này không, hay tin hoàn toàn vào LLM? Có quota / giới hạn token hay độ dài đầu vào nào áp lên `/generate` không?

**[FE]**

5. **[ĐỊNH VỊ][FE]** Màn hình tạo câu hỏi hàng loạt trong thư mục câu hỏi là component nào trong `src/templates/QuestionBankPage/`, mở từ đâu? Nó gồm những ô chọn nào (Loại câu hỏi và các ô khác như Bloom, mức độ nhận thức, số lượng), mỗi ô có những giá trị gì? Có entry point nào khác cũng mở luồng sinh câu hỏi (ví dụ nút "Tạo câu hỏi mới" riêng) không?
6. **[ĐỊNH VỊ][FE]** Khi bấm tạo, component gọi hàm nào trong `question-bank-api.ts`, gửi payload gì? Kết quả hiển thị ở đâu — lưu thẳng vào thư mục hay có bước xem trước / chỉnh sửa?
7. **[ĐỊNH VỊ][cả hai]** Trong mảng ngân hàng câu hỏi đã có chỗ nào cho người dùng gõ văn bản tự do gửi cho AI chưa (ví dụ `/convert`, `/extract`, `QuestionImportNotebookPage`)? Nếu có: ô nhập FE và trường nhận phía BE đặt tên, giới hạn độ dài thế nào — để tái dùng thay vì làm mới.

## Cần trích nguyên văn

- Request schema và response schema của `POST /api/question-cards/generate`.
- Đoạn dựng prompt sinh câu hỏi (phần cố định + chỗ chèn tham số).
- Đoạn parse / kiểm tra output của LLM (nếu có ép loại, số lượng, Bloom).
- Kiểu payload FE gửi cho `/generate` trong `question-bank-api.ts`.
- Phần JSX / state của form tạo câu hỏi hàng loạt: danh sách ô chọn và giá trị của từng ô.

## Ngưỡng dừng

Đủ khi biết rõ:
1. Màn hình nào, component nào phải thêm ô — một chỗ hay nhiều chỗ.
2. API sinh câu hỏi đã nhận văn bản tự do chưa; nếu chưa thì trường mới phải đi qua những lớp nào (schema → handler → job nếu có → prompt).
3. Ô chọn hiện tại được áp vào kết quả bằng prompt hay bằng kiểm tra cứng — đủ để thiết kế quy tắc ưu tiên khi ngữ cảnh mâu thuẫn với ô chọn.

Không cần đọc sâu chất lượng prompt, UI phần xem trước hay luồng duyệt câu hỏi ở vòng này.
