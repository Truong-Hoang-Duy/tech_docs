# Trạng thái: Thinking Chat Agent

**Cập nhật:** 2026-09-05 · **Phía:** cả hai (trọng tâm BE) · **Giai đoạn:** thiết kế xong, đã ra task doc

## Mục tiêu
Thay khuôn hiển thị message của Chat bằng Summary Bar + Execution Timeline: phơi bày
tool đã gọi, tài liệu đã đọc, bước nào thất bại — theo thời gian thực và xem lại được
sau khi F5. Giá trị chính là giáo dục.

## Quyết định đã chốt
1. **Chỉ phơi bày, không đổi hành vi agent** (phương án b) — không tăng ngân sách vòng lặp, không đổi prompt. Vì vòng "thử–sai" thật hiện chỉ có ở nhánh hình học, và canvas đụng trần timeout 240s.
2. **Một `type` SSE mới duy nhất: `step`**, upsert theo `tool_call_id`. Không sửa giao thức, không đổi endpoint.
3. **Canvas giữ `agent.run_sync`**, gắn cảm biến vào closure tool + cầu `call_soon_threadsafe` về queue sẵn có. Loại phương án đổi sang `run_stream_events` (5 rủi ro cao, mua thêm mỗi thinking steps).
4. **Lưu vào `metadata_json`**, không bảng mới, không migration. Có trần 3 tầng: `detail` 200 ký tự → 60 step → 32 KB.
5. **Thinking steps là tuỳ chọn có cờ riêng**, phải đo `ThinkingPart` trên môi trường thật trước.
6. Hai cờ: `chat_timeline` (PRODUCT_FEATURES, bật theo org) và `chat_timeline_reasoning_enabled` (env-only).

## Phương án đang theo
Chia pha: chat ngoài canvas trước (rẻ — chỉ sửa `_aiter_agent_sse_events` + gom ở
`finalize_chat_turn`), canvas sau (đắt — cảm biến tool + 4 nhánh persist), thinking
steps cuối cùng và chỉ khi đo dương. Xong pha 1 đã có tính năng dùng được.

## File trong thư mục này
- `00-mo-ta.md` — mô tả nghiệp vụ ba khối UI và giá trị giáo dục
- `01-brief.md` — 12 câu khảo sát; 5 câu hỏi nghiệp vụ vẫn chưa được trả lời, thiết kế đi tiếp bằng mặc định làm việc
- `02-findings.md` — kết quả khảo sát: phía nào sửa, bản đồ vùng, trả lời 12 câu kèm `file:line`
- `03-design.md` — phương án, đánh đổi đã loại, kế hoạch 3 pha

## Năm chỗ thiết kế lệch repo, đã sửa trong task doc
1. `_persist_chat_turn` **không tồn tại** → tên thật là `finalize_chat_turn` (`api/chat.py:1151`).
2. Canvas có **4** nhánh persist (`:1318`, `:1458`, `:1497`, `:1556`), thiết kế đoán 3.
3. `tool_call_id` **có thật** trên cả hai event → bỏ hẳn cơ chế FIFO dự phòng.
4. Thiết kế bỏ sót **warm-continue**: `_consume_agent_sse` chạy hai lần, `seq` phải liên tục.
5. `model_router.py:254-268` ngoài phạm vi file (239 dòng) → thật là `:216-238`.

Phát hiện thêm: `RetryPromptPart` là tín hiệu thất bại thật, dùng được cho nhãn *Failed*
ở **mọi** loại câu hỏi chứ không riêng nhánh hình học — mở rộng giá trị của tính năng.

## Câu hỏi mở
1. **Chờ bạn** — 5 câu nghiệp vụ ở `01-brief.md`. Task doc đã đi bằng mặc định làm việc; đổi câu trả lời thì đổi phần nào đã ghi rõ ở `03-design.md` §0.
2. **Chờ đo trên môi trường thật** — `ThinkingPart` có xuất hiện không, trên cặp provider/model nào. Đây là việc A0 trong task doc backend.

## Bước tiếp theo
Giao hai file cho người thi công:
`backend/docs/tasks/2026-09-05-thinking-chat-agent.md` và `-frontend.md`.
Việc đầu tiên là A0 (đo `ThinkingPart`) vì nó chặn hạng mục D.
