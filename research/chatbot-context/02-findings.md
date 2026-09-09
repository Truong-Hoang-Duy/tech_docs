# 02 — Kết quả khảo sát: Đồng bộ ngữ cảnh giữa Chat chính và Mini Chat trong Canvas

> Phạm vi đọc: `bookforge` — `api/chat.py`, `api/editor.py`, `api/documents.py`, `models/document.py`, `schemas/chat.py`, `schemas/documents.py`, `services/chat_document.py`, `services/inapp_document.py`, `chat/editor_agent.py`, `services/features.py`.
> `bookforge-fe` — `src/api/bookforge-api.ts`, `src/api/document-api.ts`, `src/components/TiptapEditor/`, `src/templates/HomePage/`, `src/templates/DocumentDetailPage/`, `src/hooks/use-chat-modes.ts`.
> Trạng thái tại 2026-09-09 (`bookforge@a62910d`, `bookforge-fe@71d6d8e`, cùng `origin/dev`).
> Mọi đường dẫn tính từ gốc repo tương ứng (`bookforge` / `bookforge-fe`).

## Tóm tắt cho người đọc không có repo

Hai luồng chat đúng là **hai bảng dữ liệu tách rời hoàn toàn** (`chat_sessions`/`chat_messages` và `canvas_chat_sessions`/`canvas_chat_messages`), không có khoá ngoại nào nối chúng — brief đoán đúng chỗ này.

Nhưng có **ba điều làm đổi phương án** so với giả định của brief:

1. **Sợi dây liên kết đã tồn tại, chỉ nằm chỗ khác.** Tài liệu sinh ra từ nút "chỉnh sửa" đã mang sẵn `source_session_id` = id của chat chính, lưu trong `documents.metadata_json`, và **đã lộ ra API** cho FE. Không cần thêm bảng mới để biết "canvas này đẻ ra từ cuộc trò chuyện nào" — chỉ cần đọc cái đang có.
2. **FE không hề tạo canvas session.** Không có hàm gọi `POST .../editor/chat/sessions` nào trong toàn bộ frontend. Session canvas do **backend tự đẻ ngầm** khi người dùng gửi tin nhắn đầu tiên trong canvas. Nghĩa là điểm chèn ngữ cảnh nằm ở BE, không phải ở lời gọi tạo session của FE như brief hình dung.
3. **Đã có sẵn hai cơ chế bơm ngữ cảnh ngoài vào canvas**, đang chạy tốt: trường `attached_document_ids` (đính kèm tài liệu khác vào lượt hỏi canvas) và tiền lệ tự động thêm tài liệu vào phạm vi chat (`format_document_id`). Phương án "chia sẻ một chiều" gần như không phải xây mới hạ tầng.

Ngoài ra hệ thống **đã coi hai loại chat là một họ ở tầng hiển thị**: `GET /api/chat/sessions` trộn cả hai loại vào một danh sách lịch sử, gắn nhãn `type='canvas'`. Tiền lệ này ủng hộ hướng "một cuộc trò chuyện, hai giao diện" hơn là brief nghĩ.

Đã đối chiếu `repo-map.md` các mục liên quan (endpoint chat/editor, bảng `chat_sessions`, `canvas_chat_sessions`) — **không có dòng nào lệch thực tế**, không phải sửa gì.

## Phía nào phải sửa

**Cả hai** — và tỉ trọng lệch hẳn về BE.

**BE (`bookforge`) — nơi làm phần lớn việc:**

| File | Vì sao phải đụng |
|---|---|
| `services/api/src/bookforge_api/api/editor.py` | Nơi dựng ngữ cảnh cho canvas assistant (`execute_editor_assistant`, dòng 1232–1560) và nơi đẻ session ngầm (`_get_or_create_canvas_chat_session`, dòng 502) |
| `services/api/src/bookforge_api/models/document.py` | Thêm cột liên kết trên `CanvasChatSession` (dòng 320–342), nếu chọn hướng liên kết tường minh |
| `services/api/src/bookforge_api/schemas/documents.py` | `EditorAssistantRequest` (dòng 338) và `CanvasChatSessionCreateRequest` (dòng 374) — nơi nhận `session_id` của chat chính nếu chọn truyền từ FE |
| `services/api/alembic/versions/` | Migration mới nếu thêm cột (bản mới nhất hiện là `0087_reseed_khung_names.py`) |
| `services/api/src/bookforge_api/chat/editor_agent.py` | `run_editor_assistant` (dòng 765) — nơi `history` được nhét vào prompt |

**FE (`bookforge-fe`) — chỉ là truyền thêm một id:**

| File | Vì sao phải đụng |
|---|---|
| `src/templates/HomePage/partials/use-edit-message-to-document.ts` | Chỗ điều hướng sang canvas (dòng 32), hiện chỉ mang `document.id` |
| `src/components/Chat/partial/workspace-draft-card.tsx` | Lối vào canvas thứ hai (dòng 46), cũng chỉ mang `document_id` |
| `src/templates/DocumentDetailPage/index.tsx` | Đọc query param (dòng 196), nơi thêm param mới nếu chọn truyền qua URL |
| `src/components/TiptapEditor/partial/document-ai-chat-panel.tsx` | State session canvas (dòng 162) và payload gửi assistant (dòng 413–426) |

**Hợp đồng giữa hai bên** — đây là chỗ hai task doc gặp nhau. Hai lựa chọn, chọn cái nào phải chốt ở `03-design.md`:

- **A — BE tự suy ra, FE không sửa gì.** BE đọc `documents.metadata_json['source_session_id']` của chính document đang mở canvas để tìm ngược ra chat chính. Hợp đồng API **không đổi một chữ nào**; FE không phải làm gì cả. Nhược điểm: chỉ đúng với document sinh ra từ chat, người dùng mở canvas trên tài liệu upload thì không có gì để nối.
- **B — FE truyền tường minh.** Thêm một trường vào `EditorAssistantRequest` (ví dụ `source_chat_session_id: str | None`) và/hoặc `CanvasChatSessionCreateRequest`; FE mang `sessionId` của chat chính qua query param khi điều hướng. Hợp đồng đổi ở đúng một trường, thêm được, không phá client cũ (mọi trường mới đều `Optional`, và `EditorAssistantRequest` **không** đặt `extra='forbid'` — xem mục trích nguyên văn).

## Bản đồ vùng liên quan

**Bảng dữ liệu**

| Bảng | Model | Khoá ngoại |
|---|---|---|
| `chat_sessions` | `ChatSession` — `models/document.py:269` | `organizations.id`, `users.id` |
| `chat_messages` | `ChatMessage` — `models/document.py:302` | `chat_sessions.id` |
| `canvas_chat_sessions` | `CanvasChatSession` — `models/document.py:320` | `organizations.id`, `users.id`, `documents.id` |
| `canvas_chat_messages` | `CanvasChatMessage` — `models/document.py:344` | `canvas_chat_sessions.id` |
| `documents` | `Document` — `models/document.py:101`, cột `metadata_json` ở dòng 148 | — |

**Endpoint chat chính** (`api/chat.py`, không có prefix router, path viết thẳng)

- `GET /api/chat/sessions` — `list_chat_sessions`, dòng 2008. **Trả cả canvas session** (dòng 2044–2055).
- `POST /api/chat/sessions` — `create_chat_session`, dòng 2065.
- `GET|PATCH|DELETE /api/chat/sessions/{session_id}` — dòng 2114 trở đi.
- `GET /api/chat/models` — dòng 1987; registry model dùng chung cho **cả hai** chat.

**Endpoint canvas** (`api/editor.py`, prefix `/api/documents/{document_id}/editor` — dòng 106)

- `GET  /chat/sessions` — `list_canvas_chat_sessions`, dòng 1013.
- `POST /chat/sessions` — `create_canvas_chat_session`, dòng 1046. **FE không gọi endpoint này.**
- `GET  /chat/sessions/{session_id}` — `get_canvas_chat_session`, dòng 1084.
- `DELETE /chat/sessions/{session_id}` — dòng 1106.
- `POST /assistant` — `ask_editor_assistant`, dòng 1689.
- `POST /assistant/stream` — `stream_editor_assistant`, dòng 1703 (SSE).

**Hàm BE then chốt**

- `execute_editor_assistant` — `api/editor.py:1232`. Toàn bộ việc dựng ngữ cảnh cho canvas nằm ở đây.
- `_get_or_create_canvas_chat_session` — `api/editor.py:502`. Đẻ session ngầm.
- `run_editor_assistant` — `chat/editor_agent.py:765`. Nhận `history` và `attached_documents`.
- `persist_workspace_draft` — `services/chat_document.py:123`. Nơi gắn `source_session_id` vào document.
- `build_inapp_document` — `services/inapp_document.py:39`. Nơi metadata rơi vào `documents.metadata_json` (dòng 123).
- `_serialize` — `api/documents.py:225`. Nơi `metadata_json` được trả nguyên vẹn ra API (dòng 226 + 283).
- `_serialize_canvas_history_session` — `api/chat.py:311`. Nơi canvas session được đội lốt chat session.

**Component / hook FE**

- `useChatWithAi` — `src/templates/HomePage/partials/use-chat-with-ai.ts:91`. State session của chat chính.
- `useEditMessageToDocument` — `src/templates/HomePage/partials/use-edit-message-to-document.ts:15`. Nút "chỉnh sửa".
- `DocumentAiChatPanel` — `src/components/TiptapEditor/partial/document-ai-chat-panel.tsx:154`. Mini chat trong canvas.
- `TiptapEditor` — `src/components/TiptapEditor/index.tsx:114`. Nơi mở/đóng panel.
- `DocumentDetailPage` — `src/templates/DocumentDetailPage/index.tsx:190`. Đọc `?mode=edit` và `?canvasSession=`.
- `WorkspaceDraftCard` — `src/components/Chat/partial/workspace-draft-card.tsx:46`. Lối vào canvas thứ hai.
- `useChatModes` — `src/hooks/use-chat-modes.ts:12`. **Không liên quan tới session** — chỉ fetch danh sách mode/expert.

**Feature flag**

- `chat_workspace` — `services/features.py:48` (cột `chat_workspace_enabled`). Bật/tắt luồng "draft ở lại trong chat", quyết định lối vào canvas nào được dùng.

## Tiền đề sai trong brief

**1. "Chưa có trường nào kiểu `source_session_id`, `parent_session_id` liên kết hai session" — sai một nửa, và nửa sai là nửa quan trọng.**

Đúng là **không có** trường nào trên `canvas_chat_sessions` trỏ về `chat_sessions`. Nhưng **có** `source_session_id`: nó nằm trên **document**, trong `documents.metadata_json`, được ghi lúc tài liệu được tạo từ chat. Vì canvas luôn gắn với đúng một `document_id`, đường đi ngược đã tồn tại:

```text
canvas_chat_sessions.document_id
   → documents.id
   → documents.metadata_json['source_session_id']
   → chat_sessions.id
```

Chiều xuôi cũng có sẵn: `chat_sessions.draft_document_id` (`models/document.py:288`) trỏ thẳng tới document mà canvas đang mở.

**2. "FE tạo mới một canvas chat session khi bấm chỉnh sửa" — không đúng.**

FE **không có hàm nào** gọi `POST .../editor/chat/sessions`. Toàn bộ wrapper canvas trong `src/api/bookforge-api.ts` chỉ có `APIListCanvasSessions` (dòng 688), `APIGetCanvasSession` (dòng 700), `APIDeleteCanvasSession` (dòng 709) — chỉ GET và DELETE. Session được BE đẻ ngầm ở lượt hỏi đầu tiên, rồi FE nhận `session_id` **trong response** và ghi ngược vào URL.

**3. "Canvas chat là một luồng độc lập, không thấy được gì của chat chính" — đúng về ngữ cảnh AI, nhưng không đúng về hiển thị.**

Ở tầng danh sách lịch sử, hệ thống **đã hợp nhất** hai loại: `GET /api/chat/sessions` trả cả canvas session dưới cùng một kiểu `ChatSessionListItem`, gắn `type='canvas'`, `scope='canvas'`. Người dùng đã nhìn thấy chúng trong cùng một danh sách.

## Trả lời câu hỏi

### Q1 — [XÁC MINH][BE] Canvas chat và chat chính là hai model/bảng tách biệt, hay chung một bảng có cột phân loại?

**Trả lời:** **Bốn bảng, tách biệt hoàn toàn.** Không dùng chung bảng, không có cột phân loại. Khác biệt cấu trúc đáng chú ý:

- `ChatSession` có `scope`, `mode`, `expert_agent_id`, `document_ids_json` (danh sách tài liệu trong phạm vi), `output_type`, `draft_document_id`, `pending_ask_json` — nó là một cuộc hội thoại có **phạm vi tài liệu động**.
- `CanvasChatSession` chỉ có `document_id` (một, bắt buộc, khoá ngoại thật) và `title` — nó buộc chặt vào **đúng một tài liệu**.
- `CanvasChatMessage` có thêm các trường biên tập mà `ChatMessage` không có: `editor_version`, `selection_json`, `selected_text`, `change_set_json`, `content_html`, `summary`.

Điểm này quan trọng cho câu hỏi kiến trúc ở `00-desc.md`: **gộp một bảng sẽ mất thông tin**, vì message canvas mang trạng thái con trỏ/phiên bản tài liệu mà message chat chính không có khái niệm tương ứng.

**Bằng chứng:** `services/api/src/bookforge_api/models/document.py:269-362`

```python
class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    ...
    scope: Mapped[str] = mapped_column(String(32), default='selected', index=True)
    mode: Mapped[str] = mapped_column(String(16), default='general', ...)
    document_ids_json: Mapped[list] = mapped_column(JSON, default=list)
    draft_document_id: Mapped[str | None] = mapped_column(String(36), nullable=True, default=None)
    draft_status: Mapped[str | None] = mapped_column(String(16), nullable=True, default=None)


class CanvasChatSession(Base):
    __tablename__ = 'canvas_chat_sessions'
    ...
    document_id: Mapped[str] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), index=True)
    title: Mapped[str] = mapped_column(String(255), default='Canvas chat')
    # (không có trường nào trỏ về chat_sessions)


class CanvasChatMessage(Base):
    __tablename__ = 'canvas_chat_messages'
    session_id: Mapped[str] = mapped_column(ForeignKey('canvas_chat_sessions.id', ondelete='CASCADE'), index=True)
    editor_version: Mapped[int] = mapped_column(Integer, default=0)
    selection_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    change_set_json: Mapped[list] = mapped_column(JSON, default=list)
```

### Q2 — [ĐỊNH VỊ][BE] `POST .../editor/chat/sessions` có tham số nào nhận `session_id` hoặc ngữ cảnh chat chính không? Nếu không, hàm xử lý nằm đâu?

**Trả lời:** **Không có.** Body chỉ nhận đúng một trường `title` tuỳ chọn. Và như đã nêu ở "Tiền đề sai" — **FE không gọi endpoint này**, nên đây thậm chí không phải chỗ cần sửa.

Chỗ **thật sự** cần chèn là `_get_or_create_canvas_chat_session` trong `api/editor.py:502`, được gọi từ `execute_editor_assistant` khi lượt hỏi đầu tiên chưa có `session_id`.

**Bằng chứng:** `services/api/src/bookforge_api/schemas/documents.py:374-375`

```python
class CanvasChatSessionCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
```

`services/api/src/bookforge_api/api/editor.py:1046-1060` (hàm xử lý endpoint):

```python
def create_canvas_chat_session(
    document_id: str,
    payload: CanvasChatSessionCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> CanvasChatSessionResponse:
    document = get_document_for_edit(db, user, document_id)
    _assert_document_editable(document)
    now = utcnow()
    session = CanvasChatSession(
        organization_id=user.organization_id,
        user_id=user.id,
        document_id=document.id,
        title=_clean_canvas_title(payload.title),
        created_at=now, updated_at=now,
    )
```

`services/api/src/bookforge_api/api/editor.py:502-518` (chỗ đẻ ngầm — điểm chèn thật):

```python
def _get_or_create_canvas_chat_session(
    db: Session, user, document: Document, *, session_id: str | None, title_seed: str
) -> CanvasChatSession:
    if session_id:
        return _get_canvas_chat_session(db, user, document.id, session_id)
    now = utcnow()
    session = CanvasChatSession(
        organization_id=user.organization_id,
        user_id=user.id,
        document_id=document.id,
        title=_canvas_title_from_message(title_seed),
        created_at=now, updated_at=now,
    )
    db.add(session)
    db.flush()
    return session
```

### Q3 — [ĐỊNH VỊ][BE] `POST .../assistant` và `.../assistant/stream` lấy ngữ cảnh hội thoại từ đâu? Có cơ chế đọc dữ liệu ngoài phạm vi document/canvas không?

**Trả lời:** Canvas assistant gom ngữ cảnh từ **đúng bốn nguồn**, không nguồn nào chạm tới chat chính:

1. **Lịch sử của chính canvas session đó** — mọi lượt trước, không lọc theo phiên bản tài liệu.
2. **Ảnh chụp nội dung tài liệu đang mở** (`content_html` FE gửi lên, hoặc bản mới nhất trong DB).
3. **Vùng chọn / vị trí con trỏ** trong editor.
4. **Tài liệu đính kèm** qua `attached_document_ids` — tối đa 5, được giải quyết trong phạm vi tài liệu người dùng có quyền đọc.

**Có, cơ chế đọc dữ liệu ngoài đã tồn tại và chính là nguồn số 4.** Đây là đòn bẩy rẻ nhất cho việc chia sẻ ngữ cảnh một chiều: `attached_documents` được đưa thẳng vào phạm vi truy hồi RAG cùng với tài liệu đang mở.

`api/editor.py` **không import và không nhắc tới** `ChatSession`/`ChatMessage` một lần nào (đã grep toàn file).

**Bằng chứng:** `services/api/src/bookforge_api/api/editor.py:1400-1428`

```python
    # Feed prior turns of this canvas session back to the agent so it has
    # in-session memory. The current turn is persisted only after the run, so
    # these are exactly the earlier turns. No editor_version filter — memory
    # spans document versions.
    canvas_history = (
        [
            {'role': message.role, 'content': message.content or '', 'summary': message.summary or ''}
            for message in _canvas_session_messages(db, canvas_session.id)
        ]
        if canvas_session is not None
        else []
    )
    result = run_editor_assistant(
        db=db, user=user, document=document,
        message=payload.message,
        editor_version=payload.editor_version,
        content_html=snapshot_html,
        selected_text=payload.selected_text,
        context_kind=context_kind,
        history=canvas_history,
        attached_documents=attached_documents,
    )
```

`services/api/src/bookforge_api/chat/editor_agent.py:796` — phạm vi truy hồi RAG:

```python
    retrieval_documents = [document, *(attached_documents or [])]
```

### Q4 — [XÁC MINH][BE] Model message của hai bên có trường tham chiếu chéo nào không?

**Trả lời:** **Không có, ở cả hai chiều.** `CanvasChatMessage` chỉ có `session_id` trỏ về `canvas_chat_sessions`. `ChatMessage` chỉ có `session_id` trỏ về `chat_sessions`. Không bên nào có `document_id`, và không bên nào biết tới id của bên kia.

Ở tầng **session** thì có hai đường đi gián tiếp qua document, như đã nêu ở "Tiền đề sai" mục 1.

**Bằng chứng:** `services/api/src/bookforge_api/models/document.py:302-310` và `344-352` — đối chiếu trực tiếp:

```python
class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, ...)
    session_id: Mapped[str] = mapped_column(ForeignKey('chat_sessions.id', ondelete='CASCADE'), index=True)
    role: Mapped[str] = mapped_column(String(16), index=True)
    content: Mapped[str] = mapped_column(Text, default='')
    # ... citations_json, retrieved_nodes_json, metadata_json, token counts

class CanvasChatMessage(Base):
    __tablename__ = 'canvas_chat_messages'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, ...)
    session_id: Mapped[str] = mapped_column(ForeignKey('canvas_chat_sessions.id', ondelete='CASCADE'), index=True)
    role: Mapped[str] = mapped_column(String(16), index=True)
    content: Mapped[str] = mapped_column(Text, default='')
    # ... + editor_version, selection_json, change_set_json, content_html, summary
```

### Q5 — [ĐỊNH VỊ][BE] Có job/service nền nào đã nối document với chat chính mà canvas tái dùng được không?

**Trả lời:** **Có, một cái — và nó đã chạy sẵn cho đúng tài liệu ta quan tâm.**

Khi tài liệu được tạo từ chat chính, nó được **đưa vào chỉ mục RAG ngay** (`index_strategy=INDEX_ENQUEUE`, kèm `enqueue_reindex_knowledge`). Nghĩa là **nội dung** mà chat chính viết ra đã nằm trong kho tri thức và canvas assistant truy hồi được ngay — canvas không mù hoàn toàn về chat chính, nó thấy **sản phẩm** của cuộc trò chuyện, chỉ không thấy **cuộc trò chuyện**.

Cái còn thiếu đúng là phần hội thoại: lời người dùng dặn, ràng buộc đã chốt, những gì đã bị bác bỏ.

Ngoài ra có một **tiền lệ trực tiếp dùng lại được**: khi người dùng chọn tài liệu mẫu định dạng, BE **tự động thêm** id đó vào phạm vi của chat session. Cùng khuôn đó áp cho chiều ngược lại (tự thêm document canvas vào ngữ cảnh, hoặc tự đính kèm) là chuyện đã có đường mòn.

**Bằng chứng:** `services/api/src/bookforge_api/api/chat.py:503-518`

```python
    if 'format_document_id' in fields and not clearing_type:
        if payload.format_document_id is None:
            session.format_document_id = None
        else:
            format_id = payload.format_document_id
            next_ids = list(session.document_ids_json or [])
            if format_id not in next_ids:
                next_ids.append(format_id)
            _documents, document_ids = _validate_chat_session_scope(
                db, user, scope=session.scope, document_ids=next_ids,
            )
            session.document_ids_json = document_ids
            session.format_document_id = format_id
```

**Lưu ý ngược lại:** document nháp **không** được tự thêm vào `document_ids_json`. Chỉ `format_document_id` được thêm. Nên chat chính hiện **cũng không** truy hồi được nội dung bản nháp qua RAG trừ khi người dùng tự chọn nó vào phạm vi.

### Q6 — [ĐỊNH VỊ][FE] Nút "chỉnh sửa" nằm ở component nào, gọi API ra sao, có truyền state/context nào sang không?

**Trả lời:** Có **hai lối vào**, cả hai đều đi qua cùng một hook và **cùng chỉ mang theo `document.id`** — không có `sessionId`, không có state, không có lịch sử.

- Lối 1 — nút "chỉnh sửa" trên bong bóng tin nhắn: `useEditMessageToDocument` gọi `POST /api/documents/from-chat-message` với `{session_id, message_id}`, rồi `navigate('/documents/{id}?mode=edit')`.
- Lối 2 — thẻ bản nháp (khi bật cờ `chat_workspace`): `WorkspaceDraftCard` là một thẻ `<a href="/documents/{id}?mode=edit">`.

Điều đáng chú ý: **`session_id` của chat chính CÓ được gửi lên BE** ở bước tạo tài liệu — nó chỉ không được mang tiếp sang canvas. BE nhận nó, ghi vào `documents.metadata_json['source_session_id']`, rồi FE vứt đi.

**Bằng chứng:** `src/templates/HomePage/partials/use-edit-message-to-document.ts:27-49`

```typescript
  const finishWithDocument = (document: TDocumentResponse) => {
    if (stayInChat) {
      options.onDraftReady?.(document);
      return;
    }
    navigate(`/documents/${document.id}?mode=edit`);
  };

  const createAndOpen = useCallback(
    async (messageId: string) => {
      if (!sessionId || editingMessageId) return;
      if (stayInChat && hasDraft) { setOverwriteMessageId(messageId); return; }
      setEditingMessageId(messageId);
      try {
        const document = stayInChat
          ? await APICreateDocumentFromChatMessage(sessionId, messageId, { suppressErrorToast: true })
          : await APICreateDocumentFromChatMessage(sessionId, messageId);
        finishWithDocument(document);
```

`src/components/Chat/partial/workspace-draft-card.tsx:46` (lối vào thứ hai):

```typescript
            href={`/documents/${encodeURIComponent(draft.document_id)}?mode=edit`}
```

### Q7 — [ĐỊNH VỊ][FE] Mini chat canvas dùng hook/state nào? Có phải cùng cơ chế `use-chat-modes` với chat chính không?

**Trả lời:** **Hoàn toàn riêng, và câu hỏi có một hiểu nhầm nhỏ về `use-chat-modes`.**

`useChatModes` (`src/hooks/use-chat-modes.ts`, 28 dòng) **không quản lý session gì cả** — nó chỉ là một `useQuery` lấy danh sách mode và expert khả dụng. Hook quản lý session của chat chính là `useChatWithAi` (592 dòng), giữ `sessionId`, `messages`, `sessionDocumentIds`, `workspaceDraft`… trong `useState`.

Mini chat canvas **không dùng hook nào cả** — nó giữ `useState` cục bộ ngay trong `DocumentAiChatPanel`. Vòng đời session canvas:

1. Mở canvas → `canvasSessionId` khởi tạo từ query param `?canvasSession=`, thường là `null`.
2. Gửi tin nhắn đầu tiên → payload có `session_id: undefined` → BE đẻ session ngầm.
3. BE trả `session_id` trong response → FE `setCanvasSessionId` và **ghi vào URL bằng `history.replaceState`**.

Hai bên **có** dùng chung đúng một thứ: registry model từ `GET /api/chat/models` (`schemas/documents.py:354` ghi rõ `model_id` là "opaque id from the server-owned model registry").

**Bằng chứng:** `src/components/TiptapEditor/partial/document-ai-chat-panel.tsx:162-164` và `413-444`

```typescript
  const [canvasSessionId, setCanvasSessionId] = useState<string | null>(
    initialCanvasSessionId ?? null,
  );
  ...
      const payload = {
        session_id: canvasSessionId || undefined,
        message: nextMessage,
        editor_version: editorVersion,
        editor_context: buildEditorContext(editor.state.selection, hasPlacedCaret),
        selection: range,
        selected_text: getSelectedText(editor, range),
        content_html: snapshot,
        attached_document_ids: attachedDocuments
          .filter((attachment) => attachment.status === "ready")
          .map((attachment) => attachment.id),
      };
      ...
      if (!canvasSessionId && response.session_id) {
        setCanvasSessionId(response.session_id);
        const url = new URL(window.location.href);
        url.searchParams.set("canvasSession", response.session_id);
        window.history.replaceState(null, "", url.toString());
      }
```

`src/hooks/use-chat-modes.ts:12-24` — chứng minh hook này không liên quan session:

```typescript
export const useChatModes = () => {
  const query = useQuery({ queryKey: ["chat-modes"], queryFn: APIGetChatModes });
  const modes: TChatModeOption[] = query.data?.modes ?? [];
  const experts: TChatExpertOption[] = query.data?.experts ?? [];
  return { modes, experts, legalModeAvailable: selectLegalModeAvailable(modes), ... };
```

### Q8 — [XÁC MINH][FE] Đóng canvas có gọi request đồng bộ ngược không, hay chỉ unmount?

**Trả lời:** **Chỉ unmount. Không có request nào, và không có endpoint nào để gọi kể cả muốn.**

Ba đường thoát khỏi canvas, không đường nào ghi ngược:

- Đóng panel mini chat: `onClose={() => setIsChatOpen(false)}` — thuần state React.
- Đóng chế độ sửa: `closeEditor` chỉ đổi query param `mode` thành `view`.
- Rời trang: `goBack` điều hướng tới `documentsReturnPath`.

Nút "làm lại" trong panel (`handleReset`) còn **vứt luôn** liên kết session: đặt `canvasSessionId` về `null` và xoá param khỏi URL — lịch sử canvas cũ vẫn nằm trong DB nhưng người dùng mất đường quay lại nó từ giao diện.

**Một hệ quả UX cần biết khi thiết kế:** `useEditMessageToDocument` điều hướng **không kèm** `state: { from }`, nên `documentsReturnPath` rơi về mặc định `"/documents"`. Người dùng bấm "chỉnh sửa" từ chat rồi bấm quay lại sẽ **về trang danh sách tài liệu, không về cuộc trò chuyện**. Dù có đồng bộ ngữ cảnh hai chiều, đường quay về vẫn đứt.

**Bằng chứng:** `src/templates/DocumentDetailPage/index.tsx:238-245` và `262-265`

```typescript
  const documentsReturnPath =
    typeof location.state === "object" && location.state !== null &&
    "from" in location.state && typeof location.state.from === "string"
      ? location.state.from
      : "/documents";
  const goBack = () => navigate(documentsReturnPath);
  ...
  const closeEditor = () => {
    setDocumentModeParam(setSearchParams, "view");
    detail.setIsEditing(false);
  };
```

`src/components/TiptapEditor/partial/document-ai-chat-panel.tsx:588-598`:

```typescript
  const handleReset = () => {
    setMessages(initialMessages);
    setCanvasSessionId(null);
    setDraft("");
    pendingAttachmentIdsRef.current.clear();
    setAttachedDocuments([]);
    const url = new URL(window.location.href);
    url.searchParams.delete("canvasSession");
    window.history.replaceState(null, "", url.toString());
  };
```

## Giả định của brief — đúng / sai

| # | Giả định | Kết luận | Bằng chứng |
|---|---|---|---|
| 1 | `editor.py` và `chat.py` trỏ tới hai khái niệm session khác nhau, không chung bảng | **Đúng** — bốn bảng riêng, cấu trúc khác nhau về bản chất | `models/document.py:269, 302, 320, 344` |
| 2 | Bấm "chỉnh sửa" thì FE tạo mới canvas session, không truyền `session_id`/lịch sử | **Sai một nửa** — đúng là không truyền gì, nhưng FE **không tạo** session; BE đẻ ngầm ở lượt hỏi đầu | `document-ai-chat-panel.tsx:413-444`, `editor.py:502` |
| 3 | Chưa có trường nào (`source_session_id`, `parent_session_id`) liên kết hai session | **Sai** — `source_session_id` đã tồn tại trong `documents.metadata_json`, và `chat_sessions.draft_document_id` là chiều ngược lại | `services/chat_document.py:153`, `models/document.py:288` |
| 4 | Đóng canvas không ghi ngược nội dung mini chat vào chat chính | **Đúng** — không có request, cũng không có endpoint nào làm được việc đó | `DocumentDetailPage/index.tsx:262`, `TiptapEditor/index.tsx:276` |

## Trích nguyên văn theo yêu cầu

**Chữ ký `POST /api/chat/sessions`** — `api/chat.py:2065`, schema ở `schemas/chat.py:14`:

```python
class ChatSessionCreateRequest(BaseModel):
    title: str | None = None
    scope: str = 'selected'
    mode: ChatMode = 'general'
    document_ids: list[str] = Field(default_factory=list)
    # Required when mode == 'expert'. The server validates the grant and sets document_ids = [].
    expert_agent_id: str | None = None

def create_chat_session(
    payload: ChatSessionCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ChatSessionResponse:
```

**Chữ ký `POST /api/documents/{document_id}/editor/chat/sessions`** — `api/editor.py:1046`:

```python
def create_canvas_chat_session(
    document_id: str,
    payload: CanvasChatSessionCreateRequest,   # chỉ có: title: str | None
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> CanvasChatSessionResponse:
```

**`EditorAssistantRequest` — nơi thêm trường nếu chọn phương án B** (`schemas/documents.py:338-359`). Chú ý: **không** có `model_config = ConfigDict(extra='forbid')`, nên thêm trường mới là an toàn với client cũ:

```python
class EditorAssistantRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    editor_version: int = Field(..., ge=1)
    session_id: str | None = Field(default=None, min_length=1)     # ← session CANVAS, không phải chat chính
    editor_context: EditorContext | None = None
    selection: EditorSelectionRange | None = None                  # deprecated
    selected_text: str = Field(default='', max_length=12000)
    content_html: str = Field(default='', max_length=2_000_000)
    # Additional source documents attached from the Canvas chat composer.
    # They are resolved server-side in the current user's accessible scope.
    attached_document_ids: list[str] = Field(default_factory=list, max_length=5)
    # Opaque id from the server-owned model registry (GET /api/chat/models).
    model_id: str | None = Field(default=None, max_length=64)
```

**Đối chiếu — `ChatMessageCreateRequest` thì CÓ `extra='forbid'`** (`schemas/chat.py:33-35`). Nếu thiết kế cần thêm trường vào lượt gửi của **chat chính**, phải tính tới chuyện client cũ sẽ nhận 422:

```python
class ChatMessageCreateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    message: str = Field(..., min_length=1)
    max_mode: bool = False
```

**Nơi `source_session_id` được ghi** — `services/chat_document.py:143-160`:

```python
    if live is None:
        _quota_workspace_create(response, context)
        document = build_inapp_document(
            db,
            organization_id=user.organization_id,
            owner_user_id=user.id,
            title=resolved_title,
            content=markdown,
            content_format='markdown',
            lane='chat_markdown',
            editor_capability='editable',
            index_strategy=INDEX_ENQUEUE,
            metadata={
                'origin': 'chat_workspace',
                'output_type': session.output_type,
                'source_session_id': session.id,
                **({'source_message_id': source_message_id} if source_message_id else {}),
            },
        )
        session.draft_document_id = document.id
        session.draft_status = 'drafting'
```

**Nơi metadata rơi vào cột DB** — `services/inapp_document.py:123`:

```python
        metadata_json={'page_count': page_count, **metadata},
```

**Nơi metadata được trả ra API (FE đọc được ngay hôm nay)** — `api/documents.py:226` và `283`:

```python
def _serialize(document: Document, *, db: Session, user: User, queue_state: dict | None = None) -> DocumentResponse:
    metadata = dict(document.metadata_json or {})
    ...
    return DocumentResponse(
        ...
        metadata=metadata,
        error_message=document.error_message,
    )
```

Schema (`schemas/documents.py:76-78`) — dict mở, không lọc khoá:

```python
class DocumentResponse(DocumentListItem):
    metadata: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
```

**Shape response canvas session** (`schemas/documents.py:399-411`) — hiện chưa có chỗ nào để nói "session này nối với chat nào":

```python
class CanvasChatSessionListItem(BaseModel):
    id: str
    document_id: str
    title: str
    message_count: int = 0
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None = None


class CanvasChatSessionResponse(CanvasChatSessionListItem):
    messages: list[CanvasChatMessageResponse] = Field(default_factory=list)
```

**Nơi hai loại session đã được trộn chung** — `api/chat.py:311-323`:

```python
def _serialize_canvas_history_session(db: Session, session: CanvasChatSession) -> ChatSessionListItem:
    return ChatSessionListItem(
        id=session.id,
        type='canvas',
        title=session.title,
        scope='canvas',
        mode='general',
        document_id=session.document_id,
        document_ids=[session.document_id],
        message_count=db.query(CanvasChatMessage).filter(CanvasChatMessage.session_id == session.id).count(),
        created_at=session.created_at,
        updated_at=session.updated_at,
        last_message_at=session.last_message_at,
    )
```

## File nên upload lên web

| File | Số dòng | Vì sao cần cả file (không trích được) |
|---|---|---|
| `bookforge/services/api/src/bookforge_api/api/editor.py` | 1738 | **Đọc từ dòng 1232–1560** (`execute_editor_assistant`). Luồng có 4 nhánh thoát khác nhau, mỗi nhánh đều tự persist lượt chat và tự đẻ session — muốn chèn ngữ cảnh chat chính phải thấy hết cả 4, trích 25 dòng không đủ. Thêm dòng 502–560 cho phần đẻ/persist session. |
| `bookforge/services/api/src/bookforge_api/services/chat_document.py` | 330 | Toàn bộ vòng đời "document sinh ra từ chat" — 3 hàm tạo document đều gắn `source_session_id` theo cách hơi khác nhau. Đây là file quyết định phương án A có khả thi hay không. |
| `bookforge-fe/src/components/TiptapEditor/partial/document-ai-chat-panel.tsx` | 635 | Toàn bộ state của mini chat nằm trong một component; muốn biết chèn ngữ cảnh vào chỗ nào của FE thì phải đọc cả vòng đời mount → gửi → nhận session_id → reset. |
| `bookforge-fe/src/templates/HomePage/partials/use-chat-with-ai.ts` | 592 | Chỉ cần **nếu chọn hướng đồng bộ hai chiều**. Đây là nơi giữ toàn bộ state chat chính; hai chiều thì nó phải biết cách nhận cập nhật từ canvas. Bỏ qua nếu chốt một chiều. |

Không cần upload `models/document.py` — bốn model liên quan đã trích đủ nguyên văn ở Q1 và Q4.

## Điều brief không hỏi nhưng ảnh hưởng tới thiết kế

1. **Canvas mở được trên tài liệu không sinh ra từ chat.** `/documents/{id}?mode=edit` dùng cho mọi tài liệu, kể cả file người dùng upload. Những tài liệu đó không có `source_session_id`. Phương án phải trả lời được: canvas trong trường hợp đó thì lấy ngữ cảnh ở đâu, hay đơn giản là không có gì để đồng bộ — và giao diện nói gì với người dùng.

2. **Quan hệ là một–nhiều, không phải một–một.** Một document có thể có **nhiều** canvas session (`list_canvas_chat_sessions` trả về danh sách, sắp theo `last_message_at`). Nếu chat chính phải "thấy" canvas, nó thấy cái nào? Ngược lại, một chat session chỉ giữ **một** `draft_document_id`, và `persist_workspace_draft` **ghi đè** bản nháp cũ. Bất đối xứng này phải được quyết trong thiết kế, không thể để mở.

3. **Gộp một bảng sẽ mất dữ liệu.** `CanvasChatMessage` có `editor_version`, `selection_json`, `change_set_json`, `content_html` — chat chính không có khái niệm tương ứng. Hướng "một session, hai giao diện" ở `00-desc.md` nếu hiểu là gộp bảng thì phải kèm migration cho **toàn bộ lịch sử đang có**, và phải quyết những cột kia đi đâu. Hướng "giữ hai bảng, thêm liên kết" rẻ hơn nhiều bậc.

4. **Ngân sách token của canvas đã bị siết chặt và có lý do.** `execute_editor_assistant` tính `estimated_input_tokens` rồi mới cấp `max_output_tokens`; có cả comment trong code kể lại một sự cố cũ — tài liệu 400k ký tự từng ước lượng ~100k token vượt trần 80k, khiến `max_output_tokens` về 0 và gọi provider hỏng luôn. **Nhét thêm lịch sử chat chính vào prompt sẽ ăn thẳng vào ngân sách này.** Thiết kế phải nói rõ: tóm tắt hay nguyên văn, giới hạn bao nhiêu lượt, cắt theo tiêu chí gì.

5. **Đường quay về đã đứt sẵn.** Như đã nêu ở Q8: bấm "chỉnh sửa" rồi quay lại thì về `/documents`, không về cuộc trò chuyện. Đồng bộ ngữ cảnh mà không sửa chỗ này thì người dùng vẫn thấy hai thế giới rời nhau. Đây là một sửa nhỏ ở FE (truyền `state: { from }` khi điều hướng) nhưng nên nằm trong cùng phạm vi, nếu không sẽ thành việc mồ côi.

## Chưa xác định được

- **Đồng bộ hai chiều real-time cần hạ tầng gì.** Chưa khảo sát vì `00-desc.md` còn để ngỏ giữa một chiều và hai chiều. Cả hai chat hiện đều dùng SSE **một chiều server→client trong phạm vi một request**; không thấy WebSocket hay pub/sub nào. Nếu chốt hai chiều real-time, cần một vòng khảo sát riêng về khả năng đẩy sự kiện giữa hai tab/hai panel — có thể là hạng mục nặng nhất của cả tính năng.

- **Chi phí token thực tế của việc thêm lịch sử.** Biết là có trần và có công thức ước lượng, nhưng chưa đo lịch sử chat chính điển hình dài bao nhiêu ký tự. Cần dữ liệu thật (thống kê độ dài `chat_messages.content` theo session) mới định được nên gửi nguyên văn hay tóm tắt. Chưa chạy truy vấn nào lên DB trong vòng này.

- **Phạm vi loại trừ.** Mục "Không làm lần này" ở `00-desc.md` vẫn trống. Bốn hạng mục ở "Điều brief không hỏi" bên trên đều là ứng viên để loại ra khỏi vòng đầu — đặc biệt là mục 1 (tài liệu upload) và mục 3 (gộp bảng). Đây là quyết định của người dùng, không phải của khảo sát.
