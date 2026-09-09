# Trạng thái: Đồng bộ ngữ cảnh giữa Chat chính và Mini Chat trong Canvas

**Cập nhật:** 2026-09-09 · **Phía:** cả hai (BE nặng, FE nhẹ) · **Giai đoạn:** khảo sát (vừa xong vòng 1)

## Mục tiêu

Người dùng bấm "chỉnh sửa" từ chat chính để mở canvas kèm mini chat. Hai luồng chat hiện không biết gì về nhau, buộc người dùng lặp lại ngữ cảnh. Mong muốn: AI ở cả hai nơi hiểu cùng một cuộc trò chuyện.

## Quyết định đã chốt

*(chưa có — vòng khảo sát vừa xong, thiết kế chưa bắt đầu)*

## Phương án đang theo

Chưa chốt. Khảo sát đã thu hẹp về hai hướng, và loại bớt một hướng:

- **Giữ hai bảng, thêm liên kết** — rẻ hơn nhiều bậc, hạ tầng gần như có sẵn.
- **Gộp một session, hai giao diện** — đắt: `canvas_chat_messages` có `editor_version`, `selection_json`, `change_set_json` mà `chat_messages` không có khái niệm tương ứng, nên gộp bảng sẽ mất dữ liệu và cần migration toàn bộ lịch sử.

Trong hướng "thêm liên kết" còn hai cách, phải chọn ở `03-design.md`:
**A** — BE tự suy ra qua `documents.metadata_json['source_session_id']` đã có sẵn, FE **không sửa gì**, hợp đồng API không đổi; nhưng không dùng được cho tài liệu upload.
**B** — FE truyền tường minh id chat chính qua URL + thêm một trường Optional vào `EditorAssistantRequest` (schema này không `extra='forbid'` nên thêm được an toàn).

## File trong thư mục này

- `00-desc.md` — mô tả nghiệp vụ; mục "Không làm lần này" **vẫn trống**.
- `01-brief.md` — 8 câu khảo sát (5 BE, 3 FE) + 4 giả định cần kiểm chứng.
- `02-findings.md` — hiện trạng có bằng chứng `file:line`; đã trả lời hết 8 câu.

## Câu hỏi mở

Chờ **người dùng** quyết (chỉ họ trả lời được):

1. Đồng bộ **một chiều** (canvas đọc chat chính) hay **hai chiều real-time**? Hai chiều là hạng mục nặng nhất — hiện không có WebSocket/pub-sub, chỉ có SSE một chiều trong phạm vi một request.
2. Mở canvas trên **tài liệu upload** (không sinh ra từ chat) thì xử lý sao — không đồng bộ, hay cho chọn thủ công?
3. Chốt "Không làm lần này" — ứng viên loại: tài liệu upload, gộp bảng, ghi ngược canvas → chat.

Chưa có dữ liệu, cần đo mới trả lời được: lịch sử chat chính điển hình dài bao nhiêu, để quyết gửi nguyên văn hay tóm tắt (canvas đã có trần token chặt, từng có sự cố `max_output_tokens` về 0).

## Bước tiếp theo

Dán `02-findings.md` lên chat web, trả lời 3 câu hỏi mở ở trên, rồi để web viết `03-design.md` — tách rõ phần BE và FE, chọn A hay B, và nói rõ cách cắt lịch sử để không vỡ ngân sách token.
