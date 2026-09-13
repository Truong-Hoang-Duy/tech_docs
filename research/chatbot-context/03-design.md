# 03 — Thiết kế: Đồng bộ ngữ cảnh giữa Chat chính và Mini Chat trong Canvas

> Dựa trên `02-findings.md` (đọc tại `bookforge@a62910d`, `bookforge-fe@71d6d8e`) cho chiều chat chính → canvas, và quyết định bổ sung của người dùng cho chiều canvas → chat chính. Chỗ nào không có bằng chứng trực tiếp trong findings được đánh dấu **[giả định]**; chỗ nào còn chờ khảo sát bổ sung được đánh dấu **[chờ 01b]**.

## Kết luận kiến trúc chốt

Trả lời câu hỏi gốc ở `00-desc.md`: **không gộp thành một session.**

`CanvasChatMessage` mang trạng thái biên tập (`editor_version`, `selection_json`, `change_set_json`, `content_html`) mà `ChatMessage` không có khái niệm tương ứng — gộp bảng nghĩa là quyết định bốn cột đó biến mất hoặc phải bịa ra bản tương đương cho lịch sử chat chính, kèm migration cho toàn bộ dữ liệu đang có. Đắt, rủi ro, và không cần thiết: đường liên kết qua `document_id` đã tồn tại sẵn (`documents.metadata_json['source_session_id']` và chiều ngược `chat_sessions.draft_document_id`), chỉ là **chưa tường minh ở tầng canvas session** và chưa được dùng để bơm ngữ cảnh.

**Hướng chọn: hai session độc lập, thêm một liên kết tường minh + chia sẻ ngữ cảnh hai chiều, làm mới mỗi khi một bên được mở lại — không phải một lần duy nhất, và không phải thời gian thực.**

Cụ thể:
- Mở canvas từ chat chính, hoặc mở lại canvas đã có → canvas lấy một ảnh chụp ngữ cảnh **mới nhất** của chat chính tại thời điểm đó.
- Mở lại chat chính (sau khi đã chat tiếp trong canvas) → chat chính lấy một ảnh chụp ngữ cảnh **mới nhất** của canvas tại thời điểm đó.
- Nếu đang mở cả hai cùng lúc và gõ ở một bên, bên kia **không** thấy ngay — chỉ thấy khi tự mở/mở lại. Đây không phải giới hạn tạm thời, mà là hành vi được chọn (đổi lấy việc không cần hạ tầng kênh sống).

## Không làm lần này

1. **Đồng bộ thời gian thực** (kiểu gõ bên này, bên kia thấy ngay lập tức). Cả hai chat hiện chỉ có SSE một chiều trong phạm vi một request; không có WebSocket/pub-sub nào để tái dùng. Đây là một hạng mục hạ tầng riêng, không phải "thêm một trường" — nếu cần, phải mở một vòng khảo sát + thiết kế mới.
2. **Gộp bảng / gộp session.** Lý do ở trên — mất dữ liệu, cần migration lớn.
3. **Ngữ cảnh cho canvas mở trên tài liệu upload** (không có `source_session_id`) — canvas vẫn hoạt động bình thường, chỉ đơn giản là không có gì để đồng bộ. Không coi đây là lỗi.

## Phương án — hợp đồng giữa BE và FE (chiều chat chính → canvas)

`02-findings.md` đưa ra hai lựa chọn (A: BE tự suy ra qua `metadata_json`; B: FE truyền tường minh). Chọn **kết hợp cả hai, B là chính, A là phương án dự phòng:**

| | A — chỉ suy ra ngầm | B — FE truyền tường minh | **Chọn: B + A dự phòng** |
|---|---|---|---|
| Hợp đồng API | Không đổi | Thêm 1 trường optional | Thêm 1 trường optional |
| Đúng cho mọi lối vào canvas | Chỉ đúng khi document sinh từ đúng một chat, và luôn là chat *gần nhất* tạo ra nó | Đúng với mọi lối điều hướng có mang query param | Đúng nhất — B ưu tiên nếu có, A vá lỗ hổng khi FE quên truyền hoặc canvas mở lại từ link cũ |
| Rủi ro | Cứng: không sửa được nếu người dùng mở canvas từ một chat *khác* với chat đã tạo ra document | Phụ thuộc FE nhớ truyền đúng lúc | Thấp nhất, đổi lại phải sửa cả hai phía |

**Vì sao không chỉ chọn A:** document chỉ giữ đúng một `source_session_id` — id của chat đã **tạo ra** nó. Nhưng người dùng có thể quay lại một document cũ và bấm "chỉnh sửa" từ một cuộc trò chuyện **khác**, mới hơn. A sẽ luôn trỏ về chat cũ, sai với ý định thật của người dùng lúc đó. B giải quyết đúng trường hợp này.

## Thiết kế BE — chiều chat chính → canvas

**1. Cột mới — migration**

Thêm `source_chat_session_id` (nullable, `ForeignKey('chat_sessions.id', ondelete='SET NULL')`, có index) vào `CanvasChatSession` (`models/document.py:320`). Nullable nên **không cần backfill** — dữ liệu cũ giữ nguyên `NULL`, coi như "không có ngữ cảnh nguồn", đúng hành vi hiện tại. File migration mới, tiếp theo `0087_reseed_khung_names.py`.

**2. Trường request mới**

Thêm vào `EditorAssistantRequest` (`schemas/documents.py:338`) — **không phải** `CanvasChatSessionCreateRequest`, vì đã xác nhận FE không gọi endpoint tạo session đó:

```python
source_chat_session_id: str | None = Field(default=None, min_length=1)
```

An toàn với client cũ vì `EditorAssistantRequest` không có `extra='forbid'` (đã xác minh ở findings).

**3. Điểm chèn liên kết — `_get_or_create_canvas_chat_session` (`api/editor.py:502`)**

Chỉ xử lý khi **tạo mới** session (nhánh `session_id is None`), vì liên kết nguồn chỉ có ý nghĩa lúc khởi tạo:

- Nếu `payload.source_chat_session_id` có giá trị: load `ChatSession`, kiểm tra `organization_id`/`user_id` khớp người gọi (như `load_assistant_message` đang làm ở `chat_document.py`) — sai chủ thì **bỏ qua âm thầm**, không raise lỗi (đây không phải tham số bắt buộc, không nên chặn người dùng vì một id lệch).
- Nếu không có, hoặc load thất bại: fallback đọc `document.metadata_json.get('source_session_id')` (Option A), cùng kiểm tra quyền tương tự.
- Ghi kết quả (nếu có) vào cột mới của `CanvasChatSession` khi `db.add(session)`.

**4. Điểm chèn ngữ cảnh — cả lúc tạo VÀ mỗi lần mở lại**

Ngữ cảnh **không** được nhét vào mọi lượt hỏi của canvas — canvas đã có `canvas_history` riêng cho các lượt sau. Thay vào đó, seed context được **tính lại mỗi khi canvas session được truy cập từ đầu** (không cộng dồn qua các lần mở):

- Chèn ở `_get_or_create_canvas_chat_session` khi **tạo mới** (dùng liên kết vừa resolve ở bước 3).
- Chèn **tương tự** ở `get_canvas_chat_session` (dòng 1088) khi **mở lại** một canvas session đã tồn tại — dùng `source_chat_session_id` đã lưu trên cột mới của `CanvasChatSession`, không cần FE gửi lại.
- Cách lấy dữ liệu (cả hai điểm chèn, dùng chung một hàm): lấy N tin nhắn gần nhất của `ChatSession` liên kết (`chat_messages` order by `created_at desc limit N`), cắt theo **số ký tự**, không tóm tắt bằng LLM ở v1 (tránh gọi provider thêm, tránh thêm điểm lỗi).
- Truyền vào `run_editor_assistant` (`chat/editor_agent.py:765`) như một tham số mới, ví dụ `seed_context: str | None`, **không** ghi vào `canvas_chat_messages` như một message thật (tránh nó hiện ra trong UI như một lượt chat) — chỉ dùng để dựng prompt của đúng lượt gọi đó.
- Chi phí thêm ở nhánh "mở lại": một truy vấn đọc `chat_messages` mỗi lần `GET` canvas session — chấp nhận được vì chỉ đọc DB, không gọi provider.
- Giới hạn cứng (ví dụ biến môi trường mới `EDITOR_SEED_CONTEXT_MAX_CHARS`, đặt cạnh nhóm `EDITOR_*` đã có ở `1_repo-map.md` §7) — bắt buộc phải có, vì findings đã chỉ rõ ngân sách token của canvas từng gãy vì ước lượng sai (tài liệu 400k ký tự → `max_output_tokens` về 0). Cộng thêm lịch sử chat chính vào cùng ngân sách đó mà không giới hạn là lặp lại đúng sự cố đã có comment cảnh báo trong code.

**5. Nhánh geometry trực tiếp (early-return trong `execute_editor_assistant`, dòng ~1310)**

**Đề xuất không seed context ở nhánh này.** Đây là nhánh xử lý yêu cầu hình học ngắn, tối ưu cho nhanh/rẻ; thêm ngữ cảnh hội thoại vào đây không phục vụ mục đích của nhánh và ăn vào cùng ngân sách token. **[giả định — cần xác nhận với người dùng, không phải sự thật đọc từ code]**

## Thiết kế BE — chiều canvas → chat chính **[chờ 01b]**

Chưa đủ dữ liệu để thiết kế chi tiết — cần hoàn thành vòng khảo sát bổ sung `01b` trước khi Claude Code thi công phần này. Phác thảo hướng đi dự kiến, chỉ để hình dung, **không phải thiết kế cuối cùng:**

- Điểm chèn nhiều khả năng là `GET /api/chat/sessions/{session_id}` phía chat chính — nơi được gọi mỗi khi người dùng mở lại một cuộc trò chuyện cũ. **[giả định, cần xác minh ở Q6/Q7 của `01b`]**
- Nội dung "ảnh chụp" nhiều khả năng là: một đoạn trích ngắn từ `canvas_chat_messages` gần nhất của canvas session **mới nhất** gắn với `draft_document_id` của chat đó (một chat có thể có nhiều canvas con — cần quy tắc chọn "mới nhất", ví dụ theo `last_message_at`). Dùng cùng cách cắt-theo-ký-tự đã chọn cho chiều kia, để nhất quán và tránh phải quyết định lại chính sách tóm tắt hai lần.
- **Rủi ro cần khảo sát rõ trước khi làm:** nếu draft chưa được reindex khi cập nhật (không chỉ lúc tạo — cần xác minh ở Q3 của `01b`), chat chính có thể đang trả lời dựa trên nội dung **cũ** của draft dù canvas đã sửa. Đây là lỗi tồn tại độc lập với tính năng này, nhưng liên quan trực tiếp, nên cần xác minh trước khi thiết kế điểm chèn.

## Thiết kế FE — chiều chat chính → canvas

| File | Thay đổi |
|---|---|
| `use-edit-message-to-document.ts` (dòng 32) | `navigate` mang thêm query param, ví dụ `?mode=edit&sourceSession=${sessionId}`. `sessionId` đã có sẵn trong hook (đang dùng để gọi `APICreateDocumentFromChatMessage`). |
| `workspace-draft-card.tsx` (dòng 46) | Cùng thêm `sourceSession` vào href. Component này render trong ngữ cảnh một `ChatSession` cụ thể nên id nhiều khả năng đã có sẵn ở prop cha — **[giả định, chưa xác minh trong findings vì file chưa được đọc sâu]**, cần Claude Code xác nhận lúc thi công. |
| `DocumentDetailPage/index.tsx` (dòng 196) | Đọc thêm query param `sourceSession`, truyền xuống `TiptapEditor` → `DocumentAiChatPanel` như một prop khởi tạo. |
| `document-ai-chat-panel.tsx` (dòng 413–426) | Thêm `source_chat_session_id` vào payload **chỉ khi `canvasSessionId` đang là `null`** (tức lượt tạo session đầu tiên) — các lượt sau không cần gửi lại, vì liên kết đã được BE lưu lại trên session. |

## Thiết kế FE — chiều canvas → chat chính **[chờ 01b]**

Chưa thiết kế — phụ thuộc vào điểm chèn BE ở trên. Dự kiến chỉ cần sửa nơi `useChatWithAi` tải lại session khi người dùng mở một cuộc trò chuyện cũ, để hiển thị/ dùng thêm trường ngữ cảnh mới trong response — xác định chính xác sau khi có `01b`.

## Sửa kèm — đường quay về đã đứt

`useEditMessageToDocument` hiện `navigate` không kèm `state: { from }`, nên `documentsReturnPath` luôn rơi về `/documents`. Đề xuất gộp vào cùng phạm vi vì đây là 2 dòng code, cùng chỗ đang sửa, và nếu bỏ qua thì tính năng "đồng bộ ngữ cảnh" vẫn để lại cảm giác "hai thế giới tách rời" ở đúng thao tác quay lại. Nếu bạn muốn tách riêng, ghi rõ vào "Không làm lần này".

## Trường hợp tài liệu không có nguồn (upload trực tiếp)

Không có `source_chat_session_id` (FE không gửi, hoặc không có gì lưu trên session) và không có `metadata_json['source_session_id']` (BE không tìm thấy) → `seed_context = None`, hành vi giống hệt hôm nay. Không hiện thông báo lỗi, không có UI đặc biệt.

## Kế hoạch triển khai

**BE trước (để có hợp đồng thật cho FE dựa vào):**
1. Migration thêm `canvas_chat_sessions.source_chat_session_id`.
2. Thêm trường `source_chat_session_id` vào `EditorAssistantRequest`.
3. Sửa `_get_or_create_canvas_chat_session`: nhận, xác thực quyền, fallback qua `metadata_json`, lưu vào session mới.
4. Viết hàm dùng chung: lấy N tin nhắn gần nhất của `ChatSession` nguồn + cắt theo ký tự + biến môi trường giới hạn.
5. Truyền `seed_context` qua `run_editor_assistant` ở nhánh tạo mới, chỉ dùng khi dựng prompt, không persist thành `CanvasChatMessage`.
6. Thêm cùng logic seed context vào `get_canvas_chat_session` (nhánh mở lại) — dùng `source_chat_session_id` đã lưu trên session, không cần FE gửi lại.
7. Test BE: tạo canvas có nguồn hợp lệ / nguồn thuộc người khác (phải bị bỏ qua êm) / không có nguồn / document upload thẳng / mở lại canvas nhiều lần, ngữ cảnh phải cập nhật theo nội dung mới nhất của chat chính.

**FE sau:**
8. Truyền `sourceSession` qua hai lối điều hướng vào canvas.
9. Đọc param ở `DocumentDetailPage`, truyền xuống panel.
10. Gửi `source_chat_session_id` trong payload lượt đầu tiên.
11. Thêm `state: { from }` khi điều hướng từ `useEditMessageToDocument`.

**Chiều canvas → chat chính — chờ `01b`:**
12. *(Chờ kết quả `01b`)* Xác định điểm chèn BE phía chat chính.
13. *(Chờ kết quả `01b`)* Xác minh cơ chế reindex của draft, sửa nếu đang thiếu.
14. *(Chờ kết quả `01b`)* Thiết kế + thi công điểm chèn tương ứng ở BE và FE phía chat chính.

## Chưa chốt — cần bạn quyết trước khi viết task doc

1. **Cắt theo ký tự hay tóm tắt bằng LLM?** Đề xuất cắt theo ký tự ở v1 (rẻ, không thêm lệnh gọi provider). Tóm tắt để dành cho vòng sau nếu chất lượng ngữ cảnh không đủ. Áp dụng cho cả hai chiều.
2. **Giá trị giới hạn ký tự cụ thể.** Findings ghi nhận chưa đo độ dài điển hình của `chat_messages.content` — chưa có số liệu thật để đề xuất một con số chắc chắn. Cần một truy vấn thống kê trước khi chốt hằng số này (việc của Claude Code, không phải khảo sát này).
3. **Nhánh geometry có seed context không** — đã đề xuất "không" ở trên nhưng đây là quyết định sản phẩm, không phải sự thật kỹ thuật.
4. **`WorkspaceDraftCard` có sẵn `sessionId` hay không** — cần xác nhận lúc thi công, có thể đổi cách lấy id nếu không có sẵn.
5. **Chiều canvas → chat chính** — cần chạy vòng khảo sát bổ sung `01b` trước khi có thể chốt phần thiết kế và kế hoạch tương ứng (bước 12–14 ở trên).