# Hỏi nhanh lúc thi công — ô ngữ cảnh khi tạo câu hỏi

## 2026-09-14 — Đổi nhãn ô thành "Ngữ cảnh" và thay ví dụ placeholder

**Người hỏi:** Bạn
**Bối cảnh:** sau khi thi công xong task doc FE, xem giao diện drawer "Tạo câu hỏi hàng loạt"

**Câu hỏi:**
Nhãn "Yêu cầu thêm cho AI" đổi thành "Ngữ cảnh".
Placeholder cũ `VD: Bạn là giáo viên dạy toán lớp 10, hãy tạo câu hỏi trắc nghiệm mức độ dễ, bám sát sách giáo khoa mới 2025.`
nhắc lại lớp, môn, loại câu hỏi, mức độ — những thứ drawer đã có ô chọn riêng, nên cần ví dụ khác.

**Tham khảo:** không hỏi Gemini.
**Chốt:**
- Nhãn `MassField` và `aria-label` của textarea: `Ngữ cảnh`.
- Placeholder mới: `VD: Học sinh vùng nông thôn, ưu tiên tình huống gần gũi đời sống; câu hỏi ngắn gọn, tránh đánh đố.`
  (Claude đề xuất; chỉ nói về đối tượng học sinh và văn phong, không trùng ô chọn nào.)
- Dòng phụ và tên trường API `instructions` giữ nguyên.
- Đã chép về quyết định 2 và 3 của `backend/docs/tasks/2026-09-14-question-generation-context-frontend.md`.

## 2026-09-14 — Thay câu ví dụ placeholder lần hai

**Người hỏi:** Bạn
**Bối cảnh:** sau mục trên; câu ví dụ Claude đề xuất chưa đạt

**Câu hỏi:**
Thay placeholder bằng câu người dùng đưa.

**Tham khảo:** không hỏi Gemini.
**Chốt:**
- Placeholder: `VD: Học sinh lớp 12 chuẩn bị ôn thi; câu hỏi bám sát chương trình, có tình huống thực tế đơn giản để tăng hứng thú, tránh số liệu quá phức tạp.` (giữ tiền tố `VD: ` như các ô khác trong drawer).
- Câu này có nhắc "lớp 12" dù drawer đã có ô khối/lớp — người dùng chọn, không coi là lỗi.
- Đã chép về quyết định 2 của `backend/docs/tasks/2026-09-14-question-generation-context-frontend.md`.
