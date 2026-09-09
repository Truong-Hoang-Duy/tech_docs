# Đồng bộ ngữ cảnh giữa Chat chính và Mini Chat trong Canvas

**Phía:** Cả hai (Frontend & Backend)

## Người dùng muốn gì

Khi đang trò chuyện với AI trong luồng chat chính, người dùng có thể bấm "chỉnh sửa" để mở một giao diện canvas — nơi có kèm theo một mini tool trò chuyện riêng.

**Hướng đã chốt:** giữ hai luồng chat là hai session độc lập (không gộp bảng, không gộp session). Chúng được **liên kết tường minh** với nhau, và **ngữ cảnh được làm mới mỗi khi một bên được mở lại** — không phải một lần duy nhất, và không phải thời gian thực.

Cụ thể:
- Mở canvas từ chat chính → canvas lấy một ảnh chụp ngữ cảnh mới nhất của chat chính tại thời điểm đó.
- Quay lại/mở lại chat chính (sau khi đã chat tiếp trong canvas) → chat chính lấy một ảnh chụp ngữ cảnh mới nhất của canvas (nội dung draft, các lượt trao đổi) tại thời điểm đó.
- Nếu đang mở cả hai cùng lúc và gõ ở một bên, bên kia **không** thấy ngay — chỉ thấy khi tự mở/mở lại.

## Hôm nay đang ra sao

Hai bảng dữ liệu tách rời hoàn toàn (`chat_sessions`/`chat_messages` và `canvas_chat_sessions`/`canvas_chat_messages`), không có khoá ngoại nối chúng. Tuy nhiên đã có sẵn đường nối gián tiếp qua `documents` (`source_session_id` trong `metadata_json`, và `chat_sessions.draft_document_id`) — xem chi tiết ở `02-findings.md`.

## Không làm lần này

- Đồng bộ thời gian thực (kiểu gõ bên này, bên kia thấy ngay lập tức) — cần hạ tầng kênh sống (WebSocket/pub-sub), không có sẵn hôm nay.
- Gộp hai session/bảng thành một.
- Giữ log/lịch sử đầy đủ của lần đồng bộ trước — mỗi lần mở chỉ lấy ảnh chụp **mới nhất**, không cộng dồn.

## Chỗ tôi không chắc

Đã được `02-findings.md` trả lời phần lớn cho chiều chat → canvas. Còn mở cho chiều canvas → chat:

- [ ] Chỗ nào trong code chạy mỗi khi người dùng mở lại một chat session đã tồn tại — có "hook" nào tiện để chèn ảnh chụp mới từ canvas vào đó không?
- [ ] Nếu một chat session có nhiều canvas con (một-nhiều, theo findings), thì "mới nhất" nghĩa là canvas nào?
- [ ] Nội dung draft đã được reindex vào RAG mỗi lần lưu — vậy chat chính có tự "thấy" được nội dung mới của draft qua truy hồi thông thường, hay cần một bước chèn riêng?