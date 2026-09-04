# 02 — Kết quả khảo sát: Thinking Chat Agent

> Phạm vi đọc: `bookforge` — `services/api/src/bookforge_api/{api,chat,llm,models,schemas,core}`;
> `bookforge-fe` — `src/{api,lib,components/Chat,components/TiptapEditor/partial,templates/HomePage,hooks}`.
> Trạng thái tại 2026-09-04 (`bookforge@e177816`, `bookforge-fe@73812fd`).
> Mọi đường dẫn tính từ gốc repo tương ứng.

---

## Tóm tắt cho người đọc không có repo

1. **Hai luồng chat là hai thế giới khác nhau, không dùng chung gì cả** — không chung agent ở BE, không chung component ở FE. Chi phí gần như nhân đôi.
2. **Chat ngoài canvas (HomePage) đã là agent thật**: vòng lặp nhiều bước bằng `pydantic_ai`, có tool, và **đã stream sự kiện theo thời gian thực** — hiện đã phát ra event `status` mang tên tool. Dữ liệu bước **đang có sẵn nhưng bị chặn lại ngay tại một hàm duy nhất**, và FE thì vứt đi.
3. **Chat trong canvas cũng có agent loop thật** (tối đa 25 vòng model, hàng chục tool), nhưng endpoint "stream" của nó **là stream giả**: nó chạy trọn agent trong threadpool rồi mới bắn **một** event `token` chứa nguyên câu trả lời cuối. Không có một mẩu thông tin trung gian nào rời khỏi server. Đây là phần nặng nhất của tính năng.
4. **Reasoning/thinking của mô hình bị bỏ hoàn toàn** — code chỉ đếm `thinking_tokens` để tính tiền, không nhận nội dung. `pydantic_ai` 1.94 có sẵn `ThinkingPart`/`ThinkingPartDelta` nhưng cả hai luồng đều không xử lý. Giả định của brief (thinking steps lấy từ reasoning của mô hình) **hiện chưa khả thi nếu không viết thêm**.
5. **Kênh truyền không phải sửa giao thức**: `with_sse_lifecycle` cho mọi loại event lạ đi qua, và FE `postSse` cũng vậy. Thêm event mới **không phá client cũ**.
6. **Chỗ lưu đã có sẵn**: cả `chat_messages` lẫn `canvas_chat_messages` đều có cột `metadata_json` kiểu JSON tự do, và cả hai đều được trả nguyên vẹn về FE khi mở lại phiên. Không cần bảng mới nếu chấp nhận nhét timeline vào đó.
7. **`retrieval_traces` không dùng được cho timeline**: nó gắn vào `documents.id`, không gắn message, và mỗi lượt chỉ ghi **một** dòng cho tài liệu đầu tiên — không phải nhật ký từng lần truy hồi.
8. **Không có công cụ toán (SymPy hay tương đương)**. Công cụ hiện có là truy hồi/đọc tài liệu, tra cứu pháp luật, dựng hình học JSXGraph, và sửa block tài liệu. Ví dụ "Chạy công cụ: Máy tính đại số SymPy" trong mô tả **không phản ánh được** ở vòng này (brief đã ghi rõ không làm — xác nhận là đúng, hiện không có).
9. `repo-map.md` không có dòng nào sai về vùng này; không sửa gì.

---

## Phía nào phải sửa

**Cả hai — và trọng tâm nằm ở BE**, đúng như dự đoán của brief, nhưng vì lý do khác: không phải "chưa có agent loop" mà là **có loop nhưng đường ống phát sự kiện bị bịt** (canvas) hoặc **phát ra rồi bị vứt** (ngoài canvas).

### BE — file phải đụng

| File | Việc |
|---|---|
| `services/api/src/bookforge_api/chat/adk_agent.py` | `_aiter_agent_sse_events` (dòng 1143) — điểm duy nhất cần chèn để phát bước cho chat ngoài canvas |
| `services/api/src/bookforge_api/api/editor.py` | `_stream_editor_events` (dòng 1641) — phải bỏ kiểu "chạy xong rồi mới bắn", thay bằng đường ống sự kiện thật |
| `services/api/src/bookforge_api/chat/editor_agent.py` | `run_editor_assistant_on_html` (dòng 1003) — `agent.run_sync` ở dòng 1813 phải đổi sang API stream event thì mới có bước để phát |
| `services/api/src/bookforge_api/api/chat.py` | `_stream_chat_events` (dòng 1397) — chuyển tiếp event mới; `_persist_chat_turn` — ghi timeline vào `metadata_json` |
| `services/api/src/bookforge_api/schemas/chat.py` · `schemas/documents.py` | Khai kiểu cho timeline nếu muốn nó là trường riêng thay vì nằm chìm trong `metadata` |

### FE — file phải đụng

| File | Việc |
|---|---|
| `src/templates/HomePage/partials/use-chat-with-ai.ts` | Nơi nhận frame SSE (dòng 461–486); hiện `if (frame.type !== "token") return;` — chỗ vứt bỏ event bước |
| `src/templates/HomePage/index.tsx` | Nơi render bong bóng message (dòng 203–300) — đây là "giao diện Chat hiện tại" cần thay |
| `src/components/TiptapEditor/partial/document-ai-chat-panel.tsx` | Dòng 430 truyền `() => {}` làm callback frame — **đang vứt 100% event**; và effect nạp phiên cũ ở dòng 175–225 |
| `src/components/TiptapEditor/partial/document-ai-chat-message.tsx` | Bong bóng message của canvas (`ChatBubble`, type `TDocumentAiChatMessage`) |
| **Mới** | Component Summary Bar + Execution Timeline — dùng chung được cho cả hai màn nếu nhận cùng một kiểu dữ liệu |

### Hợp đồng giữa hai phía

Đây là chỗ hai task doc gặp nhau:

- **Endpoint không đổi**: `POST /api/documents/{document_id}/editor/assistant/stream` và `POST /api/chat/sessions/{session_id}/messages/stream`.
- **Giao thức không đổi**: mỗi frame vẫn là `data: {"type": ..., "data": ..., "trace_id": ...}`; chỉ thêm giá trị mới cho `type`.
- **Lúc chạy**: BE phát thêm các `type` mới (đề xuất tên ở phần "Điều brief không hỏi"); FE tích lũy chúng vào state của message đang pending.
- **Lúc tải lại phiên**: timeline phải quay về trong `metadata` của message assistant — `GET /api/chat/sessions/{id}` và `GET /api/documents/{id}/editor/chat/sessions/{id}` đã trả nguyên `metadata` rồi, nên FE chỉ cần đọc thêm một khoá.

---

## Bản đồ vùng liên quan

**Backend (`bookforge`, gốc `services/api/src/bookforge_api/`)**

| Thứ | Vị trí |
|---|---|
| Endpoint stream chat ngoài canvas | `api/chat.py:2625` `POST /api/chat/sessions/{session_id}/messages/stream` → `stream_chat_message` (dòng 2646) |
| Producer event chat | `api/chat.py:1397` `_stream_chat_events` |
| Endpoint stream chat canvas | `api/editor.py:1703` `POST .../editor/assistant/stream` → `stream_editor_assistant` (dòng 1704) |
| Producer event canvas | `api/editor.py:1641` `_stream_editor_events` |
| Khung SSE dùng chung | `api/_sse.py:69` `with_sse_lifecycle`, `api/_sse.py:18` `format_sse_event` |
| Agent chat ngoài canvas | `chat/adk_agent.py:834` `_build_chat_agent`; tool ở `chat/adk_agent.py:743` `_register_agent_tools` |
| **Bộ lọc event của agent chat** | `chat/adk_agent.py:1143` `_aiter_agent_sse_events` ← **điểm chèn duy nhất** |
| Bảng nhãn tool → chữ tiếng Việt | `chat/adk_agent.py:1109` `_TOOL_STATUS_TEXT` |
| Ngân sách vòng lặp chat | `chat/adk_agent.py:1263` `_agent_usage_limits` |
| Agent chat canvas | `chat/editor_agent.py:765` `run_editor_assistant` → `chat/editor_agent.py:1003` `run_editor_assistant_on_html` |
| Chỗ chạy vòng lặp canvas | `chat/editor_agent.py:1813` `agent.run_sync(...)` |
| Lớp gọi LLM dùng chung | `llm/model_router.py` — `model_settings` (dòng 216), `usage_to_dict` (dòng ~110) |
| Bảng dữ liệu | `models/document.py` — `ChatSession:270`, `ChatMessage:303`, `CanvasChatSession:321`, `CanvasChatMessage:345`, `RetrievalTrace:434`, `AIAction:449`, `EventLog:476` |
| Ghi `retrieval_traces` | `chat/retrieval.py:374` `_record_trace`, gọi từ `chat/adk_agent.py:476` và `chat/retrieval.py:396` |
| Serialize message | `api/chat.py:205` `_serialize_message`; `api/editor.py:432` `_serialize_canvas_message` |
| Schema message | `schemas/chat.py:49` `ChatMessageResponse`; `schemas/documents.py:378` `CanvasChatMessageResponse` |
| Endpoint mở phiên cũ | `api/chat.py:2115` `get_chat_session`; `api/editor.py:1088` `get_canvas_chat_session` |

**Frontend (`bookforge-fe`, gốc `src/`)**

| Thứ | Vị trí |
|---|---|
| Đọc SSE | `lib/read-sse-stream.ts` — `postSse` |
| Bọc API stream | `api/bookforge-api.ts:508` `APIStreamChatMessage`; `api/bookforge-api.ts:730` `APIStreamEditorAssistant` |
| State chat ngoài canvas | `templates/HomePage/partials/use-chat-with-ai.ts` — type `TChatMessageItem` (dòng 27), callback frame (dòng 461) |
| Render chat ngoài canvas | `templates/HomePage/index.tsx:203-300` |
| State + gửi của chat canvas | `components/TiptapEditor/partial/document-ai-chat-panel.tsx` — gửi ở dòng 396–470, nạp phiên cũ ở dòng 175–225 |
| Bong bóng message canvas | `components/TiptapEditor/partial/document-ai-chat-message.tsx:20` `TDocumentAiChatMessage`, `ChatBubble` |
| Bong bóng message của `components/Chat` (**không dùng cho hai màn này**) | `components/Chat/partial/message-item.tsx`, `messages-list.tsx` |
| Hook mode | `hooks/use-chat-modes.ts` |

---

## Tiền đề sai trong brief

| Brief nói | Thực tế |
|---|---|
| "Hai màn chat dùng chung component render ở FE" (giả định) | **Sai.** Ba bộ render riêng biệt. `components/Chat/` (có `MessagesList`/`MessageItem`) chỉ được `ResearchPage`/`TemplatesPage`/`HistoryPage` dùng — mà `/research` và `/templates` đều `Navigate to="/"` (`src/App.tsx:78-80`), nên nó gần như là code chết đối với luồng chat chính. Chat ngoài canvas thật sự render inline trong `templates/HomePage/index.tsx`; chat canvas render bằng `ChatBubble` riêng. |
| "`retrieval_traces` ghi lại nguồn tài liệu đã truy hồi, đủ để dựng dòng *Đọc tài liệu: X*" | **Sai một nửa.** Bảng có `citations_json` và `metadata_json`, nhưng khoá ngoại là `documents.id` — **không có `message_id` hay `session_id`**. Mỗi lượt chat chỉ ghi **một** dòng, cho `ready_documents[0]`, kèm câu hỏi và câu trả lời cuối (`chat/adk_agent.py:475-483`). Nó là vết kiểm toán cấp tài liệu, không phải nhật ký từng lần gọi tool. |
| "Hai endpoint đã phát SSE nhiều loại event" | **Đúng với chat ngoài canvas, sai với canvas.** Canvas chỉ có `token` (một lần, nguyên câu trả lời) và `done`. |
| "Thinking steps lấy từ reasoning của mô hình, vì có `LLM_OP_*_REASONING_EFFORT`" | **Sai.** Biến đó chỉ điều khiển tham số gửi lên provider, không mở đường nhận nội dung reasoning về. Nội dung reasoning không được đọc ở bất kỳ đâu. |
| "Thêm công cụ giải toán mới (SymPy…) *nếu hiện chưa có*" | Xác nhận: **chưa có**, và cũng không có công cụ tính toán ký hiệu nào khác. |

---

## Trả lời câu hỏi

### Q1 — [ĐỊNH VỊ][BE] Luồng chat canvas đi qua những hàm nào; có agent loop không?

**Trả lời:** Luồng là
`stream_editor_assistant` → `_stream_editor_events` → `execute_editor_assistant` → `run_editor_assistant` → `run_editor_assistant_on_html` → `agent.run_sync(...)`.

**Có agent loop thật** — `pydantic_ai` `Agent.run_sync` với `request_limit=25` (4 nếu là yêu cầu hình học) và hơn 15 tool đã đăng ký. Nhưng nó **chạy đồng bộ trong threadpool**: `_stream_editor_events` chờ trọn kết quả rồi mới đẩy đúng hai item vào queue. Nghĩa là **không có bước nào rời khỏi server trong lúc agent chạy**.

**Bằng chứng:** `services/api/src/bookforge_api/api/editor.py:1641-1668`

```python
async def _stream_editor_events(*, user_id: str, document_id: str, payload_dump: dict):
    queue: asyncio.Queue = asyncio.Queue()
    done = object()

    def _run():
        with session_scope() as db:
            user = db.get(User, user_id)
            document = get_document_for_edit(db, user, document_id)
            payload = EditorAssistantRequest.model_validate(payload_dump)
            context = _quota_context_for(db, user)
            return execute_editor_assistant(
                db, user=user, document=document, payload=payload, context=context, response=None
            )

    async def _produce():
        try:
            result = await run_in_threadpool(_run)
            if result.answer:
                queue.put_nowait(('token', {'delta': result.answer}))
            queue.put_nowait(('done', result.model_dump(mode='json')))
```

**Bằng chứng (vòng lặp thật):** `services/api/src/bookforge_api/chat/editor_agent.py:1810-1821`

```python
    request_limit = 4 if geometry_request else 25
    tool_calls_limit = 4 if geometry_request else None
    try:
        result = agent.run_sync(
            message,
            message_history=_build_editor_message_history(history, settings.chat_history_max_messages),
            usage_limits=UsageLimits(
                request_limit=request_limit,
                tool_calls_limit=tool_calls_limit,
            ),
            usage=acc,
        )
```

---

### Q2 — [ĐỊNH VỊ][BE] Hai endpoint SSE phát ra những loại event nào? Có event trung gian nào FE chưa dùng không?

**Trả lời:** Mọi frame đều có shape ngoài giống nhau, do `with_sse_lifecycle` bọc:

```json
{"type": "<tên event>", "data": <payload>, "trace_id": "<request id>"}
```

Ngoài ra khung này tự phát `start`, dòng comment `: keepalive` mỗi 15 giây, và luôn kết thúc bằng đúng một `done` hoặc `error`.

**Chat ngoài canvas — `POST /api/chat/sessions/{session_id}/messages/stream`:**

| `type` | `data` | Sinh ở |
|---|---|---|
| `start` | `{"started_at": "<ISO8601>"}` | `api/_sse.py:88` |
| `retrieving` | `{}` (rỗng) | `chat/adk_agent.py:1185` — bắn một lần khi tool truy hồi đầu tiên chạy |
| `status` | `{"text": "Đang tra cứu tài liệu", "tool": "retrieve_knowledge"}` | `chat/adk_agent.py:1125-1130` |
| `token` | `{"delta": "<mẩu văn bản>"}` | `chat/adk_agent.py:1202`, `:1206` |
| `citations` | `{"citations": [...], "source_page": 0}` | `api/chat.py:1673-1681` |
| `ask_back` | payload hỏi lại của workspace | `api/chat.py:1684` |
| `done` | `ChatAnswerResponse` + `session_id`, `user_message`, `assistant_message`, `usage` | `api/chat.py:1374` `_done_payload` |
| `error` | envelope lỗi chuẩn (`code`, `message`, `status`, `details`, `trace_id`) | `api/_sse.py:132` |

**Chat canvas — `POST /api/documents/{document_id}/editor/assistant/stream`:**

| `type` | `data` |
|---|---|
| `start` | như trên |
| `token` | **một lần duy nhất**, `{"delta": "<toàn bộ câu trả lời>"}` |
| `done` | `EditorAssistantResponse.model_dump(mode='json')` |
| `error` | envelope lỗi chuẩn |

**Có event trung gian FE chưa dùng không: CÓ, ba loại.** `retrieving`, `status`, `citations` đều đang được phát mà FE **bỏ qua sạch** — callback ở FE `return` ngay với mọi `type` khác `token`/`ask_back`.

**Bằng chứng:** `chat/adk_agent.py:1109-1130`

```python
_TOOL_STATUS_TEXT = {
    'retrieve_knowledge': 'Đang tra cứu tài liệu',
    'search_corpus': 'Đang tra cứu tài liệu',
    'search_library': 'Đang tìm trong kho',
    'search_documents': 'Đang tìm trong kho',
    'read_pages': 'Đang đọc tài liệu',
    'read_section': 'Đang đọc tài liệu',
    'read_document': 'Đang đọc tài liệu',
    'find_passages': 'Đang đọc tài liệu',
    'write_draft': 'Đang ghi bản nháp',
    'check_draft': 'Đang đối chiếu khung',
    'ask_user': 'Cần xác nhận',
    'set_output': 'Đang bật đầu ra',
}


def _tool_status_event(tool_name: str | None) -> tuple[str, dict[str, str]] | None:
    name = str(tool_name or '').strip()
    text = _TOOL_STATUS_TEXT.get(name)
    if not text:
        return None
    return ('status', {'text': text, 'tool': name})
```

---

### Q3 — [ĐỊNH VỊ][BE] Lớp gọi LLM làm gì với phần reasoning/thinking? `LLM_OP_*_REASONING_EFFORT` nào khác mặc định?

**Trả lời:** Code **chỉ đếm token thinking để tính tiền, không bao giờ nhận nội dung reasoning.** `model_router.usage_to_dict` moi `reasoning_tokens`/`thoughts_tokens`/`thinking_tokens` ra khỏi `RunUsage.details`; đó là tất cả.

Ở tầng stream, `_aiter_agent_sse_events` chỉ nhận diện `PartStartEvent`/`PartDeltaEvent` mang `TextPart`/`TextPartDelta`. `pydantic_ai` 1.94.0 **có sẵn** `ThinkingPart` (`messages.py:1535`) và `ThinkingPartDelta` (`messages.py:2129`) nhưng cả hai luồng đều không import, không xử lý → **nội dung reasoning rơi vào nhánh `elif` không khớp và bị bỏ im lặng**.

`reasoning_effort` chỉ là tham số gửi lên; đặt nó còn khiến `temperature` bị bỏ đi (OpenAI từ chối sampling params khi reasoning bật).

Giá trị hiện tại trong `core/settings.py`:

| Biến | Giá trị mặc định | Liên quan luồng chat/editor? |
|---|---|---|
| `llm_editor_reasoning_effort` | `'low'` | **Có** — canvas (`chat/editor_agent.py:1051`) |
| `llm_chat_max_reasoning_effort` | `''` (không đặt) | **Có** — chat ngoài canvas, và **chỉ khi** `max_mode` **và** provider là OpenAI (`chat/adk_agent.py:872-874`) |
| `llm_question_bank_reasoning_effort` | `''` | Không |
| `llm_question_exam_extract_reasoning_effort` | `'low'` | Không |
| `llm_geometry_reasoning_effort` | `''` | Không (nhánh hình học riêng) |

Vậy: **chỉ `llm_editor_reasoning_effort = 'low'` là khác mặc định cho hai luồng này.**

**Bằng chứng:** `services/api/src/bookforge_api/llm/model_router.py:14-17` và `:216-232`

```python
# Keys PydanticAI/openai/google may use inside RunUsage.details for reasoning
# stays correct (thinking is billed at output rate; cache just gets no discount).
_REASONING_KEYS = ('reasoning_tokens', 'thoughts_tokens', 'thinking_tokens')
```

```python
def model_settings(
    *, temperature: float | None = None, max_tokens: int | None = None, reasoning_effort: str | None = None
) -> Any:
    """Provider-agnostic generation settings.

    When ``reasoning_effort`` is set we emit OpenAI's ``openai_reasoning_effort`` and DROP
    ``temperature``: OpenAI reasoning models reject sampling params while reasoning is active.
    Callers must gate this on an OpenAI-compatible provider (it is not a valid knob elsewhere).
    """
    if reasoning_effort is not None:
        from pydantic_ai.models.openai import OpenAIChatModelSettings

        openai_kwargs: dict[str, Any] = {'openai_reasoning_effort': reasoning_effort}
```

---

### Q4 — [ĐỊNH VỊ][BE] Agent chat gọi được những tool nào, khai ở đâu, đối số/kết quả có được ghi lại không?

**Trả lời:**

**Chat ngoài canvas** — khai bằng decorator `@agent.tool_plain` trong `chat/adk_agent.py`:

| Nhóm | Tool | Nơi khai | Điều kiện bật |
|---|---|---|---|
| Truy hồi | `retrieve_knowledge(query)` | `:762` | có tài liệu trong phiên |
| Expert | `search_corpus(query)` | `:755` | phiên có expert agent |
| Đọc tài liệu | `get_document_overview()`, `get_document_summaries()`, `search_documents(query)`, `get_document_outline(document_id, max_depth)`, `read_section(document_id, node_id)` | `:775-798` | cờ `chat_document_tools_enabled` |
| Đọc tài liệu (luôn có) | `read_pages(document_id, start_page, end_page, page_numbering)`, `find_passages(query)`, `read_document(document_id)` | `:800-823` | có `reader` |
| Pháp lý | `law_search`, `law_lookup`, `law_document_search`, `law_get_article`, `law_browse`, `law_get` | `:908-963` | `legal_enabled` |
| Soạn thảo pháp lý | `law_drafting_guide`, `law_draft_submit` | `:967-991` | `law_drafting_enabled` |
| Workspace | `search_library(query)`, `set_output(output_type, output_sentence)`, `write_draft(markdown, title)`, `check_draft(output_type)`, `ask_user(...)` | `:995-1010` | cờ `chat_workspace` |

**Chat canvas** — khai trong `chat/editor_agent.py` (`run_editor_assistant_on_html`):
`get_outline()` `:1247`, `read_blocks(start_id, end_id)` `:1254`, `search_document(query, max_results)` `:1261`, `update_block(block_id, content)` `:1268`, `insert_blocks(after_id, content)` `:1273`, `delete_blocks(...)` `:1567`, `move_block(block_id, after_id)` `:1579`, `plan_geometry_operations(...)` `:1278`, `apply_geometry_operations(...)` `:1321`, `create_jsxgraph_figure(...)` `:1437`, `list_jsxgraph_figures()` `:1501`, `update_jsxgraph_figure(...)` `:1507`, `draw_geometry(description, after_id, target_block_id)` `:1598`, `retrieve_knowledge(query)` `:1667`, `get_legal_template(...)` `:1674`, `apply_legal_format(title, doc_type, content_html)` `:1688`.

**Không có công cụ tính toán/CAS.**

**Đối số và kết quả có được ghi lại không: KHÔNG.** Chỉ **số đếm tổng hợp** được lưu vào `metadata_json` của message:

- Chat: `adk_tool_call_count`, `retrieved_count`, `_legal_tool_call_count`, `_expert_tool_call_count` (`chat/adk_agent.py:461-473`).
- Canvas: `adk_tool_call_count`, `document_tool_call_count`, `geometry_attempts`, `geometry_asset_ids`, `request_limit_hit`, `turn_timeout_hit`, `context_mode` (`chat/editor_agent.py:880-887`, `:1907-1918`).

Đối số cụ thể (`query` nào, đọc trang nào) và kết quả trả về **chỉ sống trong bộ nhớ của request** rồi biến mất. Đây chính là dữ liệu mà "Knowledge & Tool Logs" cần.

---

### Q5 — [XÁC MINH][BE] `retrieval_traces` có cột gì, ghi ở bước nào, có gắn được tới từng message không?

**Trả lời:** Cột: `id`, `document_id` (FK → `documents.id`), `query` (Text), `citations_json` (JSON), `answer` (Text), `metadata_json` (JSON), `created_at`.

**Không có `message_id`, không có `session_id`** → **không gắn được tới từng message**.

Được ghi ở hai chỗ: cuối một lượt chat thành công (`chat/adk_agent.py:475-483`, trong `_shape_chat_result`) — **một dòng cho cả lượt**, gắn vào `ready_documents[0]`; và khi truy hồi bị chặn (`chat/retrieval.py:395`, gọi từ `api/chat.py:1806`, `:1854`, `:1904`).

**Bằng chứng:** `services/api/src/bookforge_api/models/document.py:434-447`

```python
class RetrievalTrace(Base):
    __tablename__ = 'retrieval_traces'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), index=True)
    query: Mapped[str] = mapped_column(Text)
    citations_json: Mapped[list] = mapped_column(JSON, default=list)
    answer: Mapped[str] = mapped_column(Text, default='')
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    document: Mapped[Document] = relationship(back_populates='traces')
```

---

### Q6 — [XÁC MINH][BE] `canvas_chat_messages` và `chat_messages` có cột gì? Có cột JSON tự do không?

**Trả lời:** **Có** — cả hai đều có `metadata_json` kiểu `JSON`, không ràng buộc schema. Đây là chỗ đính timeline mà **không cần bảng mới, không cần migration**. Cả hai còn có `retrieved_nodes_json` (JSON) đang dùng cho mục đích khác.

Cột đầy đủ ở phần "Trích nguyên văn".

**Cảnh báo kích thước:** `metadata_json` được trả **nguyên vẹn** về FE ở mọi lần liệt kê message của phiên (`_serialize_message`, `_serialize_canvas_message`). Nhét timeline dài vào đó sẽ làm response của `GET .../sessions/{id}` phình theo số message. Nếu timeline dự kiến vượt vài KB/lượt thì nên tính tới bảng riêng — nhưng đó là quyết định thiết kế, không phải ràng buộc kỹ thuật.

---

### Q7 — [XÁC MINH][BE] `chat.py` và `editor.py` dùng chung agent/service hay hai bản riêng?

**Trả lời:** **Hai bản triển khai riêng hoàn toàn.**

- Chat ngoài canvas: `chat/adk_agent.py` — `_build_chat_agent` + `_aiter_agent_sse_events` (async, streaming event thật).
- Chat canvas: `chat/editor_agent.py` — `run_editor_assistant_on_html` + `agent.run_sync` (đồng bộ, blocking).

Thứ duy nhất dùng chung:

| Dùng chung | File |
|---|---|
| Khung SSE (`with_sse_lifecycle`, `format_sse_event`, `SSE_HEADERS`) | `api/_sse.py` |
| Định tuyến model & đo token (`model_router`) | `llm/model_router.py` |
| Tool truy hồi (`ScopedKnowledgeRetrievalTool`) | `chat/retrieval.py` |
| Toolset pháp lý (`LegalToolset`) | dùng ở cả hai |

**Vậy không có "một điểm duy nhất cần chèn".** Có **hai** điểm:

1. `chat/adk_agent.py:1143` `_aiter_agent_sse_events` — chèn ở đây là đủ cho chat ngoài canvas. Rẻ.
2. `api/editor.py:1641` + `chat/editor_agent.py:1813` — canvas phải **đổi kiến trúc** từ `run_sync` sang API streaming event của `pydantic_ai` trước khi có gì để chèn. Đắt.

---

### Q8 — [XÁC MINH][BE] Mở lại phiên cũ trả về gì cho mỗi message? Đủ dựng lại timeline sau F5 không?

**Trả lời:** Cả hai endpoint đều trả `messages` đầy đủ, **bao gồm nguyên `metadata`**.

- `GET /api/chat/sessions/{session_id}` → `get_chat_session` (`api/chat.py:2115`) → `_serialize_session(..., include_messages=True)` → mỗi message là `ChatMessageResponse`.
- `GET /api/documents/{document_id}/editor/chat/sessions/{session_id}` → `get_canvas_chat_session` (`api/editor.py:1088`) → `CanvasChatSessionResponse` với `CanvasChatMessageResponse`.

**Đủ để dựng lại timeline sau F5 không: hiện tại KHÔNG** — vì chưa có gì được ghi vào. Nhưng **đường ống đã sẵn**: chỉ cần BE ghi timeline vào `metadata_json` là nó tự động quay về, không phải đụng endpoint, schema hay serializer nào. Đây là phần rẻ nhất của tính năng.

Lưu ý FE: `document-ai-chat-panel.tsx:184-200` khi nạp phiên cũ chỉ ánh xạ `id`, `role`, `content`, `time`, `summary`, `content_html`, `change_set` — **`metadata` bị bỏ ngay tại FE**, phải sửa dòng này.

---

### Q9 — [ĐỊNH VỊ][FE] Chỗ nào nhận chunk SSE và đẩy vào state trong chat canvas? Kiểu message là gì?

**Trả lời:** `src/components/TiptapEditor/partial/document-ai-chat-panel.tsx:430` — và nó **truyền một callback rỗng**, tức là **mọi frame SSE đều bị vứt**. State chỉ được cập nhật một lần từ `response` (chính là `data` của event `done`).

Kiểu dữ liệu: `TDocumentAiChatMessage` trong `document-ai-chat-message.tsx:20-29` — **không có trường nào cho timeline, cũng không có `metadata`**.

**Bằng chứng:** `src/components/TiptapEditor/partial/document-ai-chat-panel.tsx:427-434`

```tsx
      let response;
      try {
        response = await APIStreamEditorAssistant(documentId, payload, () => {});
      } catch (streamError) {
        if (!shouldFallbackToJson(streamError)) throw streamError;
        response = await APIAskDocumentEditorAssistant(documentId, payload);
      }
```

**Bằng chứng:** `src/components/TiptapEditor/partial/document-ai-chat-message.tsx:20-29`

```ts
export type TDocumentAiChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
  time: string;
  summary?: string | null;
  content_html?: string | null;
  change_set?: TEditorChangeSetEntry[];
  review?: TAiReviewCard;
};
```

*(Chat ngoài canvas thì ngược lại: `use-chat-with-ai.ts:461-486` có xử lý frame, nhưng `return` ngay với mọi type khác `token`/`ask_back`.)*

---

### Q10 — [XÁC MINH][FE] `read-sse-stream` có chữ ký thế nào; gặp event lạ thì làm gì?

**Trả lời:** Event lạ **được truyền cho callback rồi bỏ qua, không lỗi, không ngắt stream**. Vòng lặp chỉ branch trên ba giá trị: `start` (đánh dấu đã mở), `error` (ném `SseProtocolError`), `done` (ghi nhận terminal). Mọi `type` khác rơi ra ngoài cả ba `if`.

**Kết luận: thêm loại event mới KHÔNG phá client cũ** — ở cả tầng `postSse` lẫn tầng `with_sse_lifecycle` phía BE.

**Bằng chứng:** `src/lib/read-sse-stream.ts` — `consume`

```ts
  const consume = (raw: string) => {
    if (raw.startsWith(":")) return;
    for (const line of raw.split("\n")) {
      if (!line.startsWith("data: ")) continue;
      const frame = JSON.parse(line.slice(6)) as TSseFrame;
      onFrame(frame);
      if (frame.type === "start") opened = true;
      if (frame.type === "error") throw new SseProtocolError("SSE error event", frame);
      if (frame.type === "done") terminal = frame;
    }
  };
```

Chữ ký:

```ts
export async function postSse(
  path: string,
  body: unknown,
  onFrame: (frame: TSseFrame) => void,
  options: { signal?: AbortSignal; headers?: HeadersInit } = {},
): Promise<TSseFrame>
```

Một lưu ý: `postSse` ném `SseProtocolError("SSE closed without done")` nếu stream đóng mà chưa thấy `done`. `with_sse_lifecycle` đã bảo đảm luôn có terminal (phát `done` tổng hợp nếu inner kết thúc lặng lẽ, `api/_sse.py:160-169`), nên hợp đồng này an toàn.

---

### Q11 — [ĐỊNH VỊ][FE] Hai giao diện chat là chung hay riêng? Chỗ render bong bóng ở file nào?

**Trả lời:** **Riêng, và thực ra là ba bộ code:**

1. **Chat ngoài canvas (đang chạy, route `/`)** — state ở `templates/HomePage/partials/use-chat-with-ai.ts`, render **inline** trong `templates/HomePage/index.tsx:203-300`. Không dùng component nào của `components/Chat/`.
2. **Chat canvas** — `components/TiptapEditor/partial/document-ai-chat-panel.tsx` + `ChatBubble` trong `document-ai-chat-message.tsx`.
3. **`components/Chat/`** (có `MessagesList` → `MessageItem`) — chỉ được `ResearchPage`, `TemplatesPage`, `HistoryPage` import; mà `/research` và `/templates` đều redirect về `/` (`src/App.tsx:78-80`). Coi như ngoài phạm vi.

**Hệ quả cho khối lượng công việc: chi phí FE nhân đôi**, đúng như brief lo. Cách giảm: viết Summary Bar + Execution Timeline thành **một component độc lập nhận một kiểu timeline chung**, rồi cắm vào cả hai chỗ render — nhưng hai bộ state vẫn phải sửa riêng.

---

### Q12 — [XÁC MINH][FE] `use-chat-modes` + `GET /api/chat/modes` trả về gì; mode ảnh hưởng render thế nào?

**Trả lời:** Response có ba trường: `modes`, `experts`, `workspace_enabled`.

`modes` hiện chỉ có **đúng một** phần tử: `{"id": "legal", "label": "Trợ lý pháp lý", "description": "", "enabled": <cờ legal_mode của org>}`. `experts` là danh sách expert agent được cấp. `workspace_enabled` là cờ `chat_workspace`.

**Mode ảnh hưởng gì tới render message:** rất ít, và không phải qua `modes`. Việc render nhánh theo `message.metadata` chứ không theo mode:
- `parseLegalDraft(message.metadata)` → thẻ dự thảo pháp lý;
- `askBackForMessage(...)` khi `workspaceActive` → thẻ hỏi lại;
- `previewHtml`/`previewSource`/`previewTitle` → khung xem trước hình học.

**Kết luận cho thiết kế: timeline nên bật cho MỌI mode.** Không có mode nào đổi khuôn render đến mức phải loại trừ, và chính các nhánh legal/workspace mới là chỗ agent chạy nhiều bước nhất (ngân sách `chat_agent_*_legal` cao hơn mặc định).

---

## Giả định của brief — đúng / sai

| # | Giả định | Kết luận | Bằng chứng |
|---|---|---|---|
| 1 | Chat hiện tại đã có agent loop nhiều vòng và gọi tool, chỉ không phát ra ngoài | **Đúng cả hai luồng** — nhưng lý do "không phát ra" khác nhau: chat ngoài canvas có phát (FE vứt), canvas không phát được vì chạy blocking | `chat/adk_agent.py:1143`; `chat/editor_agent.py:1813`; `api/editor.py:1655` |
| 2 | Hai endpoint đã phát SSE nhiều loại event → thêm event mới là mở rộng | **Đúng với chat, sai với canvas.** Canvas chỉ có `token` (1 lần) + `done`. Nhưng giao thức và khung SSE thì đúng là mở rộng được, không phải dựng kênh mới | `api/_sse.py:69`; `api/editor.py:1655-1657` |
| 3 | `retrieval_traces` đủ để dựng dòng "Đọc tài liệu: X" | **Sai.** Không có FK tới message; 1 dòng/lượt cho tài liệu đầu tiên; không phải nhật ký từng tool call | `models/document.py:434`; `chat/adk_agent.py:475-483` |
| 4 | Bảng message chỉ lưu nội dung cuối → muốn replay phải thêm chỗ lưu | **Sai một nửa.** Đúng là hiện chỉ lưu nội dung cuối, nhưng **không cần thêm bảng**: `metadata_json` đã là JSON tự do và đã được trả về FE khi mở phiên cũ | `models/document.py:303`, `:345`; `api/chat.py:205`; `api/editor.py:432` |
| 5 | Hai màn chat dùng chung component render ở FE | **Sai.** Ba bộ riêng; chi phí FE nhân đôi | `templates/HomePage/index.tsx:203`; `document-ai-chat-message.tsx:20`; `App.tsx:78-80` |
| 6 | Thinking steps lấy từ reasoning của mô hình | **Sai ở hiện trạng.** Reasoning không được nhận, chỉ đếm token. Muốn có thì phải xử lý `ThinkingPart`/`ThinkingPartDelta` — có sẵn trong `pydantic_ai` 1.94.0 nhưng chưa dùng | `llm/model_router.py:14-17`; `chat/adk_agent.py:1199-1206`; `.venv/.../pydantic_ai/messages.py:1535`, `:2129` |

---

## Trích nguyên văn theo yêu cầu

### Chữ ký handler hai endpoint stream

`services/api/src/bookforge_api/api/editor.py:1703-1712`

```python
@router.post('/assistant/stream', responses=_ASSISTANT_RESPONSES)
def stream_editor_assistant(
    request: Request,
    document_id: str,
    payload: EditorAssistantRequest,
    response: Response,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    context: QuotaContext = Depends(get_quota_context),
):
```

`services/api/src/bookforge_api/api/chat.py:2646-2654`

```python
def stream_chat_message(
    request: Request,
    session_id: str,
    payload: ChatMessageCreateRequest,
    response: Response,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    context: QuotaContext = Depends(get_quota_context),
):
```

### Chữ ký hàm agent mà chúng gọi vào

`services/api/src/bookforge_api/chat/adk_agent.py:1143-1152`

```python
async def _aiter_agent_sse_events(
    agent,
    *,
    query: str,
    message_history,
    usage_limits,
    pyd_model,
    model_settings,
    on_final,
):
```

`services/api/src/bookforge_api/chat/editor_agent.py:765-781`

```python
def run_editor_assistant(
    *,
    db: Session,
    user: User,
    document: Document,
    message: str,
    editor_version: int,
    content_html: str,
    max_output_tokens: int,
    selected_text: str = '',
    context_kind: str = 'none',
    cursor_position: int | None = None,
    selection_range: tuple[int, int] | None = None,
    model_id: str | None = None,
    history: list[dict] | None = None,
    attached_documents: list[Document] | None = None,
) -> dict[str, Any]:
```

### Vòng lặp event của agent chat — nơi bước bị bỏ

`services/api/src/bookforge_api/chat/adk_agent.py:1180-1206` (rút gọn còn phần quyết định)

```python
                    if isinstance(event, FunctionToolCallEvent):
                        if tool_name in {'ask_user', 'set_output', 'write_draft', 'check_draft'}:
                            committed_work = True
                        if tool_name in {'retrieve_knowledge', 'search_corpus'} and not retrieving_sent:
                            retrieving_sent = True
                            yield ('retrieving', {})
                        status = _tool_status_event(tool_name)
                        if status is not None:
                            yield status
                    elif isinstance(event, FunctionToolResultEvent):
                        name = getattr(event.part, 'tool_name', None)
                        if name in {'ask_user', 'set_output', 'write_draft', 'check_draft'}:
                            committed_work = True
                        if name == 'ask_user':
                            return
                        if name == 'set_output' and _tool_result_warm_continue(event.part):
                            return
                    elif isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
                        delta = event.part.content or ''
                        if delta:
                            yield ('token', {'delta': delta})
                    elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                        delta = event.delta.content_delta
                        if delta:
                            yield ('token', {'delta': delta})
```

Ba chỗ mất mát nằm ngay đây:
- `FunctionToolCallEvent` — **đối số của tool bị bỏ**, chỉ lấy tên đổi sang một câu chung chung.
- `FunctionToolResultEvent` — **kết quả tool không phát ra event nào**, chỉ dùng để quyết định dừng sớm. Đây là chỗ mất "đọc được tài liệu nào, thành công hay thất bại".
- Không có nhánh nào cho `ThinkingPart`/`ThinkingPartDelta` — **reasoning rơi vào khoảng trống**.

### Cột bảng lưu message chat ngoài canvas

`services/api/src/bookforge_api/models/document.py:302-318`

```python
class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey('chat_sessions.id', ondelete='CASCADE'), index=True)
    role: Mapped[str] = mapped_column(String(16), index=True)
    content: Mapped[str] = mapped_column(Text, default='')
    citations_json: Mapped[list] = mapped_column(JSON, default=list)
    retrieved_nodes_json: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    session: Mapped[ChatSession] = relationship(back_populates='messages')
```

### Cột bảng lưu message chat trong canvas

`services/api/src/bookforge_api/models/document.py:344-365`

```python
class CanvasChatMessage(Base):
    __tablename__ = 'canvas_chat_messages'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey('canvas_chat_sessions.id', ondelete='CASCADE'), index=True)
    role: Mapped[str] = mapped_column(String(16), index=True)
    content: Mapped[str] = mapped_column(Text, default='')
    editor_version: Mapped[int] = mapped_column(Integer, default=0)
    selection_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    selected_text: Mapped[str] = mapped_column(Text, default='')
    change_set_json: Mapped[list] = mapped_column(JSON, default=list)
    content_html: Mapped[str] = mapped_column(Text, default='')
    summary: Mapped[str] = mapped_column(Text, default='')
    citations_json: Mapped[list] = mapped_column(JSON, default=list)
    retrieved_nodes_json: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    session: Mapped[CanvasChatSession] = relationship(back_populates='messages')
```

### Bảng lưu hành động AI và nhật ký sự kiện

`ai_actions` (`models/document.py:448-475`) — cột: `id`, `organization_id`, `user_id`, `action_type`, `document_ids_json` (JSON), `input_tokens`, `output_tokens`, `total_tokens`, `status`, `error_message`, `metadata_json` (JSON), `provider`, `model`, `thinking_tokens`, `cached_input_tokens`, `bft_charged`, `cost_usd` (Numeric 12,6), `rate_catalog_version`, `created_at`.
→ Đây là bảng **tính tiền/quota**, một dòng cho cả lượt. `thinking_tokens` ở đây là số đếm, không phải nội dung.

`event_log` (`models/document.py:475-493`) — cột: `id`, `organization_id`, `actor_user_id`, `event_type`, `document_id`, `target_user_id`, `metadata_json` (JSON), `ip_address`, `user_agent`, `request_id`, `created_at`.
→ Nhật ký kiểm toán cấp nghiệp vụ (`document_question_asked` được ghi ở `api/chat.py:1686-1697`), không phải nhật ký bước.

**Kết luận: không bảng nào trong ba bảng này chứa dữ liệu bước.** Cả ba đều là số tổng hợp cấp lượt.

### Kiểu TypeScript của message trong state chat ở FE

`bookforge-fe` — `src/templates/HomePage/partials/use-chat-with-ai.ts:27-38` (chat ngoài canvas)

```ts
export type TChatMessageItem = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt?: string;
  citations?: TCitationRange[];
  metadata?: Record<string, unknown>;
  previewHtml?: string | null;
  previewSource?: string | null;
  previewTitle?: string | null;
  attachments?: TChatMessageAttachment[];
  pending?: boolean;
};
```

`src/components/TiptapEditor/partial/document-ai-chat-message.tsx:20-29` (chat canvas) — đã trích ở Q9. **Không có `metadata`.**

### Kiểu response của API lấy chi tiết một phiên chat

`services/api/src/bookforge_api/schemas/chat.py:49-63`

```python
class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: ChatMessageRole
    content: str
    citations: list[CitationRange | LegalCitation | ExpertCitation] = Field(default_factory=list)
    retrieved_nodes: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    created_at: datetime
    preview_html: str | None = None
    preview_source: str | None = None
    preview_title: str | None = None
```

`services/api/src/bookforge_api/schemas/documents.py:378-396`

```python
class CanvasChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: CanvasChatMessageRole
    content: str
    editor_version: int = 0
    selection: dict[str, Any] | None = None
    selected_text: str = ''
    change_set: list[EditorChangeSetEntry] = Field(default_factory=list)
    content_html: str = ''
    whole_document_replace: bool = False
    summary: str = ''
    citations: list[CitationRange] = Field(default_factory=list)
    retrieved_nodes: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    created_at: datetime
```

Cả hai đều có `metadata: dict[str, Any]` **không ràng buộc schema** → thêm khoá mới không cần đổi schema, không cần đổi phiên bản API.

### Chữ ký hàm đọc SSE ở FE

Đã trích ở Q10.

### Biến môi trường chi phối vòng lặp agent

Tất cả ở `services/api/src/bookforge_api/core/settings.py`. Tên biến môi trường là tên trường viết hoa (Pydantic Settings).

| Biến | Mặc định | Dùng ở |
|---|---|---|
| `chat_agent_request_limit` | `7` | `chat/adk_agent.py:1263` (`_agent_usage_limits`) |
| `chat_agent_tool_calls_limit` | `5` | như trên |
| `chat_agent_request_limit_expanded` | `14` | như trên, khi cờ expanded bật hoặc workspace bật |
| `chat_agent_tool_calls_limit_expanded` | `12` | như trên |
| `chat_agent_request_limit_legal` | `10` | như trên, khi `legal_enabled` |
| `chat_agent_tool_calls_limit_legal` | `8` | như trên |
| `chat_agent_expanded_budget_enabled` | `False` | `chat/adk_agent.py:1275` — **cờ mở rộng ngân sách agent** |
| `chat_document_tools_enabled` | `False` | `chat/adk_agent.py:773` — **cờ công cụ tài liệu trong chat**; tắt thì mất `get_document_overview`, `search_documents`, `get_document_outline`, `read_section` |
| `chat_read_max_calls` | `8` | trần đọc trang mỗi lượt (trong `ScopedDocumentReaderTool`) |
| `chat_read_total_char_budget` | `120_000` | trần ký tự đọc mỗi lượt |
| `chat_retrieval_max_queries` | `4` | trần số truy vấn `retrieve_knowledge` mỗi lượt |
| `chat_history_max_messages` | `12` | cửa sổ lịch sử, dùng cả hai luồng |
| `editor_model_timeout_seconds` | `120.0` | `chat/editor_agent.py:1065` — timeout **một lần gọi model** của canvas |
| `editor_turn_timeout_seconds` | `240.0` | `chat/editor_agent.py:1069` — **timeout một lượt của editor**; phải nhỏ hơn `response_header_timeout` của Caddy (330s) |
| `llm_editor_reasoning_effort` | `'low'` | `chat/editor_agent.py:1051` |
| `llm_chat_max_reasoning_effort` | `''` | `chat/adk_agent.py:874` |

Ngân sách canvas **không** đọc từ settings — nó **hardcode** trong code:

`services/api/src/bookforge_api/chat/editor_agent.py:1806-1811`

```python
    # Geometry tool failures used to consume up to 60 model requests, leaving
    # the Canvas spinner running for several minutes. A valid geometry turn only
    # needs an initial plan plus a small number of validation repairs, so stop
    # the agent promptly when it cannot produce valid operations.
    request_limit = 4 if geometry_request else 25
    tool_calls_limit = 4 if geometry_request else None
```

---

## File nên upload lên web

| File | Số dòng | Vì sao cần cả file (không trích được) |
|---|---|---|
| `services/api/src/bookforge_api/chat/adk_agent.py` | ~1300 | Đây là file quyết định thiết kế BE cho chat ngoài canvas. Web cần thấy đồng thời: cách tool được đăng ký (`:743-823`), cách agent được dựng (`:834-1010`), bảng nhãn tool (`:1109`), và vòng lặp event (`:1143-1226`). Bốn vùng này phải đọc cùng nhau mới thiết kế được event mới. **Đọc từ dòng 740 đến hết.** |
| `services/api/src/bookforge_api/api/editor.py` | 1738 | Cần cả luồng: preflight (`:1607`), producer stream (`:1641`), handler (`:1703`), serializer message (`:432`), và `execute_editor_assistant` (`:1380-1520`) để thấy vì sao chuyển sang stream thật lại đụng cả nhánh xử lý lỗi hình học. **Đọc dòng 1370–1738 và 420–470.** |
| `services/api/src/bookforge_api/chat/editor_agent.py` | ~1950 | Nơi phải đổi `run_sync` sang streaming. Web cần thấy toàn bộ khối tool đăng ký (`:1247-1700`) để biết mỗi tool nên hiện ra timeline như thế nào. **Đọc dòng 1003–1100 và 1240–1830.** |
| `bookforge-fe/src/templates/HomePage/partials/use-chat-with-ai.ts` | 592 | Toàn bộ vòng đời một lượt chat ở FE — tạo message lạc quan, stream, thay bằng message thật, xử lý ask_back. Timeline phải chen vào đúng vòng đời này. |
| `bookforge-fe/src/components/TiptapEditor/partial/document-ai-chat-panel.tsx` | 635 | Tương tự cho canvas, cộng thêm phần khoá editor, review change_set — timeline phải sống chung với các trạng thái đó. |
| `services/api/src/bookforge_api/api/_sse.py` | 170 | Ngắn và là hợp đồng giao thức; web nên có nguyên văn để không đề xuất thứ phá hợp đồng terminal-event. |

**Không upload:** `core/settings.py` không cần thiết ở vòng này — mọi biến liên quan đã trích đủ ở trên.

---

## Điều brief không hỏi nhưng ảnh hưởng tới thiết kế

1. **Canvas hiện khoá editor suốt lượt chạy** (`editor.setEditable(false)`, `document-ai-chat-panel.tsx:409-410`). Nếu timeline khiến người dùng thấy AI chạy 60–120 giây thay vì "đang chờ", việc tài liệu bị khoá suốt thời gian đó sẽ nổi lên thành vấn đề UX mới. Cần tính trong thiết kế.

2. **Timeout của canvas là 240 giây và bị chặn trên bởi Caddy 330 giây.** Nếu chọn phương án (a) "thực sự chạy nhiều bước" cho canvas, ngân sách 25 vòng model × 120s/lần gọi đã vượt xa 240s — nghĩa là **agent sẽ bị cắt giữa chừng thường xuyên hơn**, và timeline sẽ hiển thị chuỗi bước rồi đứt. Đây là ràng buộc hạ tầng, không sửa bằng code ứng dụng.

3. **`_stream_editor_events` cố tình không huỷ producer khi client ngắt kết nối** (`api/editor.py:1682-1683`, `finally: pass  # do not cancel producer`). Sửa sang stream thật phải giữ nguyên tính chất này, nếu không người dùng đóng tab giữa chừng sẽ mất luôn thay đổi đã ghi vào tài liệu.

4. **Chat ngoài canvas nhả session DB trước khi stream** (`_release_request_session`, `api/chat.py:2698` và chú thích ở `:1363-1366`). Mọi thứ ghi thêm trong lúc stream phải dùng `session_scope()` riêng. Nếu định ghi timeline **dần dần** trong lúc chạy (thay vì ghi một lần lúc kết thúc), phải tôn trọng ràng buộc này — và đây cũng là lý do nên ghi một lần ở cuối.

5. **Tình trạng "Failed → thử phương pháp khác" hiện chỉ tồn tại ở nhánh hình học.** `chat/editor_agent.py` có vòng sửa lỗi thật (`last_geometry_error`, `geometry_attempts`, "repair the operations/assertions at most twice"). Ở các nhánh khác, agent hầu như không có cơ chế "thử — sai — đổi hướng" nào để mà hiển thị. **Muốn Status Indicators có nội dung thật ở mọi loại câu hỏi thì phải đổi cả prompt và cấu trúc vòng lặp** — đó là thay đổi hành vi agent, vượt xa "hiển thị minh bạch cái vốn có". Đây chính là đánh đổi (a) vs (b) trong câu hỏi 5 của brief, và repo đứng về phía (b) ở hiện trạng.

---

## Chưa xác định được

1. **Provider nào đang chạy thật trên production** — code định tuyến động qua `model_router.effective_model_pair` và đọc từ biến môi trường không có trong repo. Việc `ThinkingPart` có thực sự về hay không **phụ thuộc provider**: OpenAI qua `/v1/responses` và một số model có trả reasoning summary, một số không. Cần biết cặp provider/model thật của `LLM_OP_CHAT` và `LLM_OP_EDITOR` mới khẳng định được "thinking steps thật" khả thi tới đâu.

2. **Kích thước thực tế của một timeline một lượt** — chưa đo được vì dữ liệu chưa tồn tại. Quyết định "nhét vào `metadata_json`" hay "tách bảng riêng" nên chờ con số này; ước lượng thô: 5–12 bước × (tên tool + đối số rút gọn + tóm tắt kết quả) ≈ 1–4 KB/lượt, tức `metadata_json` là đủ, nhưng cần xác nhận bằng đo thật sau khi có bản dựng đầu.

3. **Hành vi khi hai luồng dùng chung một component timeline mà shape event khác nhau** — chưa xác định được vì shape event cho canvas chưa tồn tại. Đây là việc của `03-design.md`: chốt **một** shape event dùng chung cho cả hai luồng trước khi viết code, nếu không FE sẽ phải viết hai bộ adapter.
