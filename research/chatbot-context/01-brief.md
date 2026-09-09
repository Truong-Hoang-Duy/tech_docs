# 01 — Brief khảo sát: Đồng bộ ngữ cảnh giữa Chat chính và Mini Chat trong Canvas

**Gợi ý thư mục (slug):**
1. `dong-bo-canvas-chat`
2. `lien-ket-session-canvas`
3. `canvas-chat-context`
4. `hop-nhat-session-chat`

## Mục tiêu tính năng
- Người dùng bấm "chỉnh sửa" từ chat chính, mở canvas kèm mini chat riêng.
- Mini chat trong canvas hiện đang là một luồng độc lập, không thấy được ngữ cảnh của chat chính.
- Mong muốn: AI ở cả hai nơi hiểu cùng một cuộc trò chuyện, không bắt người dùng lặp lại ngữ cảnh.
- Chưa xác định phạm vi loại trừ ("Không làm lần này" trong 00-desc.md còn để trống) — cần Claude Code nêu rủi ro nếu có, chưa chốt được ở vòng này.
- Câu hỏi kiến trúc gốc: hai luồng chat là hai session độc lập (chia sẻ một phần ngữ cảnh) hay thực chất là một session, chỉ khác cách hiển thị?

## Phía dự đoán
Cả hai — dự đoán dựa trên bản đồ hiện có (`editor.py` có nhóm endpoint `chat/sessions` riêng cho canvas, `chat.py` có nhóm session riêng cho chat ngoài canvas), nhưng Claude Code sẽ chốt lại sau khi đọc model/service thật.

## Giả định cần kiểm chứng
- Tôi đang giả định `editor.py` (`/api/documents/{document_id}/editor/chat/sessions`) và `chat.py` (`/api/chat/sessions`) trỏ tới hai khái niệm session khác nhau trong DB, không dùng chung bảng.
- Tôi đang giả định khi bấm "chỉnh sửa", FE tạo mới một canvas chat session mà không truyền `session_id` hay lịch sử của chat chính vào.
- Tôi đang giả định hiện chưa có trường nào (kiểu `source_session_id`, `parent_session_id`) liên kết hai session này ở tầng dữ liệu.
- Tôi đang giả định việc đóng canvas hiện tại không có cơ chế ghi ngược nội dung mini chat vào lịch sử chat chính.

## Câu hỏi khảo sát

**[BE]**

1. **[XÁC MINH][BE]** Session/message của canvas chat (`editor.py: chat/sessions`) và của chat chính (`chat.py: sessions`) có phải hai model/bảng hoàn toàn tách biệt không, hay dùng chung một bảng session với cột phân loại?
2. **[ĐỊNH VỊ][BE]** Khi FE gọi `POST .../editor/{document_id}/chat/sessions` để tạo canvas chat, có tham số nào cho phép truyền `session_id` hoặc ngữ cảnh của chat chính vào không? Nếu không có, hàm xử lý request nằm ở đâu để biết chỗ cần thêm tham số.
3. **[ĐỊNH VỊ][BE]** `POST .../assistant` và `POST .../assistant/stream` trong `editor.py` lấy ngữ cảnh hội thoại từ đâu (document hiện tại, lịch sử canvas chat, hay có đọc thêm gì khác)? Có sẵn cơ chế nào đọc dữ liệu ngoài phạm vi document/canvas không?
4. **[XÁC MINH][BE]** Model lưu message của canvas chat và của chat chính có trường nào tham chiếu chéo sang nhau (`document_id`, `session_id` phía kia, v.v.) không?
5. **[ĐỊNH VỊ][BE]** Có job/service nào đang chạy nền (RQ job, reindex, knowledge-retrieval) đã kết nối dữ liệu giữa document và chat chính mà canvas chat có thể tái dùng để lấy ngữ cảnh không?

**[FE]**

6. **[ĐỊNH VỊ][FE]** Nút "chỉnh sửa" mở canvas nằm ở component nào, và nó gọi API tạo/lấy canvas chat session theo cách nào — có truyền state/context nào từ chat chính sang không?
7. **[ĐỊNH VỊ][FE]** Mini chat trong canvas dùng hook/state quản lý session nào — có phải cùng cơ chế với `use-chat-modes` mà chat chính dùng, hay là một state hoàn toàn riêng?
8. **[XÁC MINH][FE]** Khi người dùng đóng canvas quay lại chat chính, FE có gọi request nào để đồng bộ ngược nội dung mini chat vào chat chính không, hay chỉ unmount component?

## Cần trích nguyên văn
- Định nghĩa model/schema của canvas chat session & message (trong `editor.py` hoặc file schema liên quan) và của chat chính (`chat.py`) — để so sánh có trường liên kết nào không.
- Chữ ký hàm xử lý `POST .../editor/{document_id}/chat/sessions` và `POST /api/chat/sessions` (tham số nhận vào).
- Đoạn code FE nơi nút "chỉnh sửa" khởi tạo canvas (component + hook liên quan).

## Ngưỡng dừng
Đủ thông tin khi biết rõ: (1) canvas chat và chat chính hiện có phải hai session độc lập hoàn toàn về dữ liệu hay không; (2) có sẵn trường/cơ chế nào để liên kết hai session không, nếu chưa thì cần thêm bảng/cột nào; (3) FE hiện truyền gì (nếu có) khi mở canvas. Không cần đọc sâu hơn UI chi tiết của canvas ở vòng này.

# 01b — Bổ sung khảo sát: Làm mới ngữ cảnh hai chiều khi mở lại (không real-time)

**Phía:** Cả hai

## Bối cảnh
Vòng khảo sát trước (`02-findings.md`) đã trả lời đủ cho chiều **chat chính → canvas** (đọc lúc canvas được tạo). Vòng này bổ sung cho:
1. Việc **lặp lại** ảnh chụp đó mỗi lần canvas được **mở lại** (không chỉ lúc tạo mới).
2. Chiều ngược lại: **canvas → chat chính**, khi người dùng mở lại chat.

## Giả định cần kiểm chứng
- Tôi đang giả định canvas session đã tồn tại (`session_id` có sẵn trong URL) thì lúc mở lại chỉ gọi `GET .../chat/sessions/{session_id}` để tải lịch sử, không đi qua `_get_or_create_canvas_chat_session` (hàm đó chỉ chạy khi tạo mới) — cần xác minh, vì đây là chỗ quyết định "làm mới mỗi lần mở" phải chèn ở đâu.
- Tôi đang giả định `GET /api/chat/sessions/{session_id}` của chat chính là nơi được gọi mỗi khi người dùng mở lại một cuộc trò chuyện cũ.
- Tôi đang giả định draft document được reindex vào RAG mỗi lần `persist_workspace_draft` chạy (đã thấy `index_strategy=INDEX_ENQUEUE` ở nhánh tạo mới trong `chat_document.py`, nhưng chưa rõ nhánh cập nhật bản nháp đã có — dòng `document.editor_version`... — có trigger reindex lại không).

## Câu hỏi khảo sát

**[BE]**

1. **[ĐỊNH VỊ][BE]** `GET .../editor/chat/sessions/{session_id}` (`get_canvas_chat_session`, dòng 1088 theo findings trước) — hàm này chỉ đọc lịch sử, hay có thể chèn thêm bước "lấy ảnh chụp mới nhất từ chat chính" vào response mà không phá vỡ gì?
2. **[ĐỊNH VỊ][BE]** `GET /api/chat/sessions/{session_id}` phía chat chính — tương tự, đây có phải điểm chèn hợp lý cho "ảnh chụp mới nhất từ canvas" không?
3. **[XÁC MINH][BE]** Khi `persist_workspace_draft` cập nhật một draft đã tồn tại (nhánh `live is not None`), nội dung mới có được đẩy reindex lại (RAG) không, hay chỉ nhánh tạo mới mới có `INDEX_ENQUEUE`?
4. **[ĐỊNH VỊ][BE]** Một `chat_sessions` có thể có nhiều `canvas_chat_sessions` con (qua `document_id` → nhiều canvas). Có cách nào xác định canvas "mới nhất" gắn với đúng document đang là `draft_document_id` của session đó không (ví dụ sắp theo `last_message_at`)?
5. **[ĐỊNH VỊ][BE]** Chi phí của việc gọi lại truy vấn ảnh chụp mỗi lần `GET` session (thay vì chỉ lúc tạo) — endpoint `GET` hiện có đang nhẹ (chỉ đọc DB) hay đã có logic nặng khác cần cân nhắc?

**[FE]**

6. **[ĐỊNH VỊ][FE]** Component nào gọi `GET .../chat/sessions/{session_id}` khi người dùng mở lại canvas đã có sẵn `?canvasSession=` trên URL — đây có phải lúc mount của `DocumentAiChatPanel` không?
7. **[ĐỊNH VỊ][FE]** Tương tự, component nào gọi lấy lại session khi người dùng mở lại một cuộc trò chuyện cũ trong chat chính (`useChatWithAi` — chỗ nào trong 592 dòng đó chịu trách nhiệm)?

## Cần trích nguyên văn
- Toàn bộ hàm `get_canvas_chat_session` và hàm tương ứng phía `chat.py` cho việc mở lại một session cũ.
- Đoạn code FE gọi các endpoint đó lúc mount.

## Ngưỡng dừng
Đủ khi biết chính xác 2 điểm chèn (một ở BE-canvas, một ở BE-chat-chính) cho việc "làm mới ảnh chụp mỗi lần mở", và biết draft có tự cập nhật trong RAG hay cần chèn thủ công.