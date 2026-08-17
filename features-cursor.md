# Tính năng: Tương tác xử lý con trỏ (cursor) & thay đổi nội dung xung quanh

**Ngày tìm hiểu:** 2026-08-02

## 1. Tổng quan

Editor dùng **TipTap v3 (ProseMirror)** ở frontend. Toàn bộ logic cursor/selection tập trung trong `frontend/src/components/TiptapEditor/`, tương ứng phía backend là `backend/services/api/src/bookforge_api/editor/` và `backend/services/api/src/bookforge_api/chat/`.

Luồng tổng quát:

1. Người dùng đặt caret / bôi đen (chọn) text trong TipTap.
2. Frontend lưu vị trí selection vào state + hiển thị bằng decoration "chốt" (persistent selection).
3. Khi gửi yêu cầu AI (chat hoặc toolbar AI), frontend đóng gói vị trí con trỏ thành `editor_context` (`{kind:'cursor', position}` hoặc `{kind:'selection', anchor, head}`).
4. Backend nhận, dùng module `caret.py` để dịch vị trí ProseMirror (số nguyên) sang block index + character offset cụ thể trong document.
5. Backend chèn "hint" (đánh dấu vị trí bằng token đặc biệt) vào prompt cho LLM, chỉ đạo AI thao tác đúng tại điểm đó.
6. LLM trả về `change_set` (danh sách block cần replace/insert/delete, theo **block index**).
7. Frontend áp `change_set` thành một ProseMirror transaction duy nhất, map đúng vị trí tuyệt đối trong document, rồi highlight tạm thời vùng vừa đổi.

## 2. Danh sách file liên quan

### Frontend

- [frontend/src/components/TiptapEditor/index.tsx](../frontend/src/components/TiptapEditor/index.tsx) — component gốc editor, đồng bộ trạng thái selection.
- [frontend/src/components/TiptapEditor/persistent-selection-extension.ts](../frontend/src/components/TiptapEditor/persistent-selection-extension.ts) — Extension ProseMirror hiển thị highlight cho selection đã "chốt" kể cả khi mất focus.
- [frontend/src/components/TiptapEditor/partial/editor-context-payload.ts](../frontend/src/components/TiptapEditor/partial/editor-context-payload.ts) — xây payload `editor_context` gửi backend.
- [frontend/src/components/TiptapEditor/partial/assistant-editor-actions.ts](../frontend/src/components/TiptapEditor/partial/assistant-editor-actions.ts) — các hàm chèn/thay nội dung tại range cụ thể (toolbar AI: rewrite, continue, insert below...).
- [frontend/src/components/TiptapEditor/partial/assistant-change-set.ts](../frontend/src/components/TiptapEditor/partial/assistant-change-set.ts) — áp `change_set` từ AI thành 1 transaction ProseMirror.
- [frontend/src/components/TiptapEditor/change-highlight-extension.ts](../frontend/src/components/TiptapEditor/change-highlight-extension.ts) — highlight tạm thời (2.5s) các block vừa bị AI sửa.
- [frontend/src/components/TiptapEditor/pending-change-review-extension.ts](../frontend/src/components/TiptapEditor/pending-change-review-extension.ts) — hiển thị preview thay đổi AI đề xuất trước khi Accept.
- [frontend/src/components/TiptapEditor/partial/document-ai-chat-panel.tsx](../frontend/src/components/TiptapEditor/partial/document-ai-chat-panel.tsx) — panel chat AI, lắp ráp request gửi backend, xử lý accept/undo review.
- [frontend/src/components/TiptapEditor/partial/toolbar-ai-menu.tsx](../frontend/src/components/TiptapEditor/partial/toolbar-ai-menu.tsx) — menu AI nổi khi bôi đen văn bản.
- [frontend/src/api/bookforge-api.ts](../frontend/src/api/bookforge-api.ts) — định nghĩa type `TEditorContext`, `TEditorAssistantRequest/Response`, `TEditorChangeSetEntry` (contract FE/BE).

### Backend

- [backend/services/api/src/bookforge_api/editor/caret.py](../backend/services/api/src/bookforge_api/editor/caret.py) — **file lõi**: dịch vị trí ProseMirror sang block index + char offset (giả lập thuật toán `nodeSize` của ProseMirror).
- [backend/services/api/src/bookforge_api/chat/editor_agent.py](../backend/services/api/src/bookforge_api/chat/editor_agent.py) — xây prompt AI, chèn token đánh dấu vị trí con trỏ/selection vào nội dung gửi LLM.
- [backend/services/api/src/bookforge_api/api/editor.py](../backend/services/api/src/bookforge_api/api/editor.py) — FastAPI router, endpoint `POST /api/documents/{id}/editor/assistant`, trích xuất caret/selection từ request.
- [backend/services/api/src/bookforge_api/editor/block_document.py](../backend/services/api/src/bookforge_api/editor/block_document.py) — model "Block" đại diện document, xử lý "cursor affordance" (đoạn rỗng cuối trang) và các thao tác insert/replace theo block.
- [backend/services/api/src/bookforge_api/chat/editor_edit_tools.py](../backend/services/api/src/bookforge_api/chat/editor_edit_tools.py) — tool function LLM gọi để đọc/sửa document theo block id (gồm cả tool read-only: `read_blocks`, `get_outline`, `search_document`).
- [backend/services/api/src/bookforge_api/editor/block_view.py](../backend/services/api/src/bookforge_api/editor/block_view.py) — `project_block()` (render block thành `<block id="bN$" type="...">`) và `sentinel_id()`/`strip_sentinel()` (sinh & validate block id có hậu tố `$`).
- [backend/services/api/src/bookforge_api/editor/block_diff.py](../backend/services/api/src/bookforge_api/editor/block_diff.py) — tính diff giữa blocks gốc và blocks sau khi AI sửa, sinh `change_set`.
- [backend/services/api/src/bookforge_api/schemas/documents.py](../backend/services/api/src/bookforge_api/schemas/documents.py) — Pydantic schema `EditorContext`, `EditorAssistantRequest` (mirror của type FE).
- [backend/services/api/src/bookforge_api/services/geometry/generation.py](../backend/services/api/src/bookforge_api/services/geometry/generation.py) — sinh hình học (JSXGraph) chèn tại vị trí con trỏ đã resolve.
- [backend/services/api/src/bookforge_api/api/documents.py](../backend/services/api/src/bookforge_api/api/documents.py) — endpoint `POST /upload`, tạo `Document` ban đầu và enqueue job ingest.
- [backend/services/api/src/bookforge_api/ingest/pipeline.py](../backend/services/api/src/bookforge_api/ingest/pipeline.py) — worker ingest: OCR/parse PDF/DOCX/PPTX/ảnh, build `content_html`, set `editor_capability = view_only`.
- [backend/services/api/src/bookforge_api/editor/markdown_document.py](../backend/services/api/src/bookforge_api/editor/markdown_document.py) — `build_editor_html()` ghép nội dung từng trang thành `<section data-page="N">`.
- [backend/services/api/src/bookforge_api/models/document.py](../backend/services/api/src/bookforge_api/models/document.py) — model `Document` (metadata, `editor_capability`, `visibility`...) và `EditorDocument` (lưu `content_html`/`content_markdown` theo version).
- [backend/services/api/src/bookforge_api/services/access.py](../backend/services/api/src/bookforge_api/services/access.py) — `effective_document_access()`, `document_permissions()`, `get_document_for_edit/view()` — nguồn chân lý cho quyền đọc/sửa tài liệu.

## 3. Sơ đồ luồng thực thi

```
[UI - TipTap Editor]
  người dùng click / gõ trong document
        │
        ▼
  editor.on("selectionUpdate")           (index.tsx)
        │  lưu savedSelectionRange + hasPlacedCaret
        ▼
  PersistentSelection decoration          (persistent-selection-extension.ts)
        │  highlight vùng chọn kể cả khi mất focus (vd mở chat AI)
        ▼
  ── người dùng gọi AI (chat panel / toolbar AI) ──
        │
        ▼
  buildEditorContext(selection, hasPlacedCaret)   (editor-context-payload.ts)
        │  => { kind: 'cursor', position } | { kind: 'selection', anchor, head } | undefined
        ▼
  POST /api/documents/{id}/editor/assistant       (document-ai-chat-panel.tsx -> bookforge-api.ts)
        │  body: { editor_context, message, ... }
        ▼
[BACKEND - FastAPI]
  ask_editor_assistant()                           (api/editor.py)
        │  _resolve_context_kind / _cursor_position / _selection_range
        ▼
  caret.py: block_index_at_position() / caret_in_text_block()
        │  dịch position (int ProseMirror) -> (block_index, char_offset)
        │  _real_block_index(): nếu rơi vào "cursor affordance" -> lùi về block thật
        ▼
  editor_agent.py: _cursor_hint() / _selection_hint()
        │  chèn CARET_TOKEN ⟦CARET⟧ hoặc SELECTION_START/END_TOKEN vào text block
        │  ghép vào prompt: "Act relative to that exact spot..."
        ▼
  run_editor_assistant()  ->  LLM agent loop
        │  LLM gọi tool trong editor_edit_tools.py (theo block id, KHÔNG theo vị trí tuyệt đối)
        │    read_blocks / update_block / insert_blocks / delete_blocks / move_block / insert_html_blocks
        ▼
  block_document.py: apply_replace_blocks / apply_insert_blocks ...
        │  cập nhật danh sách block trong bộ nhớ
        ▼
  block_diff.py: tính change_set (so sánh blocks gốc vs blocks mới)
        │  op: replace | insert | delete, theo block index, kèm old_fingerprint để verify
        ▼
  Response: EditorAssistantResponse { change_set, ... }
        │
        ▼
[UI - áp dụng kết quả]
  pending-change-review-extension.ts
        │  hiển thị preview (widget/node decoration) tại đúng vị trí sẽ chèn/xoá
        ▼
  người dùng bấm "Accept"
        ▼
  applyChangeSet(editor, response)                 (assistant-change-set.ts)
        │  blockSpans(doc): tính {start,end} vị trí ProseMirror của từng block-index
        │  sắp entries theo vị trí giảm dần -> tr.replaceWith/delete/insert
        │  map lại highlightRanges qua stepMap sau mỗi bước
        ▼
  change-highlight-extension.ts
        │  highlight tạm thời (2.5s) vùng vừa đổi; findNearestBlock() xử lý range rỗng (insert điểm)
        ▼
  [Document đã cập nhật, hiển thị trên UI]
```

Ngoài luồng AI ở trên, còn có luồng **thao tác trực tiếp tại vị trí con trỏ** (không qua AI generate mà chỉ áp lại kết quả AI trả sẵn, hoặc actions từ toolbar):

```
toolbar-ai-menu.tsx (bôi đen text) -> getSelectionRange(editor)
        │
        ▼
assistant-editor-actions.ts
  - applyReplacement(editor, range, text): editor.chain().insertContentAt(range, content)
  - insertBelow(): tìm vị trí ngay dưới khối chứa selection rồi insertContentAt
  - continueAtSelection(): chèn text AI-continue tại range.to (điểm cuối selection/caret)
  - replaceTextOccurrenceInRange(): tìm & thay 1 đoạn cụ thể trong phạm vi range
```

## 4. Giải thích logic quan trọng

### 4.1. Phân biệt "cursor thật do người dùng đặt" vs "cursor bị dịch chuyển tự động"
`index.tsx` (`syncSelection`) chỉ set `hasPlacedCaret = true` khi selection rỗng (collapsed) **và** `editor.isFocused`. Điều này tránh trường hợp con trỏ bị ProseMirror tự dịch chuyển (do load nội dung, áp change-set...) bị hiểu nhầm là hành động chủ ý của người dùng, dẫn đến gửi sai `editor_context` cho AI.

### 4.2. Vì sao chỉ tin `editor_context`, không tin field `selection` cũ (legacy)
`api/editor.py` cố tình chỉ trích xuất caret/selection từ `payload.editor_context`, không dùng field `selection` legacy để xác định vị trí — tránh AI bị bias theo giá trị mặc định/cũ còn sót lại từ các phiên bản API trước.

### 4.3. "Cursor affordance" — đoạn rỗng cuối trang
Editor tự thêm 1 paragraph rỗng ở cuối trang để người dùng có chỗ đặt con trỏ (giống việc nhấn Ctrl+End trong Word). Cả `caret.py::_real_block_index()` và `block_document.py::is_cursor_affordance()`/`_insert_blocks()` đều xử lý: nếu caret rơi vào đoạn này, tự động lùi về block nội dung thật gần nhất, tránh AI ghi nội dung "ra ngoài trang" hoặc bị lệch vị trí chèn.

### 4.4. Dịch vị trí ProseMirror sang block/offset
ProseMirror biểu diễn vị trí bằng 1 số nguyên (position) tính theo toàn bộ document. Backend không có runtime ProseMirror nên `caret.py` phải **giả lập thuật toán tính `nodeSize`** của ProseMirror thông qua parser HTML riêng (`_NodeSizeParser`) để suy ra chính xác block nào chứa vị trí đó và offset ký tự bên trong block (nếu là block dạng text phẳng như paragraph/heading/code_block). Với các block phức tạp (list, table, hình...), chỉ xác định được block index, không có offset ký tự.

### 4.5. Token đánh dấu vị trí trong prompt AI
Backend chèn các token đặc biệt (`⟦CARET⟧`, `⟦SEL_START⟧`/`⟦SEL_END⟧`) trực tiếp vào text của block để LLM "nhìn thấy" chính xác điểm cần thao tác trong ngữ cảnh văn bản xung quanh, kèm chỉ dẫn "Act relative to that exact spot". Có 3 tầng fallback trong `_cursor_hint()`: (1) biết chính xác block + ký tự, (2) chỉ biết block (không có offset), (3) hint chung khi không xác định được gì.

`editor_edit_tools.py::sanitize_editor_markdown()` lọc bỏ các token này nếu LLM lỡ echo lại vào nội dung sinh ra, tránh rò rỉ token vào tài liệu đã lưu.

### 4.6. Áp change_set an toàn khi vị trí có thể lệch
`change_set` trả về theo **block index**, không phải vị trí tuyệt đối — vì giữa lúc AI xử lý và lúc người dùng bấm Accept, document có thể đã thay đổi. `assistant-change-set.ts::applyChangeSet()`:
- Tính lại `blockSpans(doc)` tại thời điểm áp dụng (map index -> vị trí ProseMirror hiện tại).
- Sắp các entry theo vị trí **giảm dần** trước khi áp, để việc xoá/chèn ở vị trí sau không làm lệch offset của các entry trước đó.
- Có `old_fingerprint` để verify nội dung gốc chưa đổi; nếu fingerprint không khớp → gọi `fallback()` thay nguyên document thay vì áp từng phần (tránh corrupt document).
- Highlight ranges được map lại qua từng `stepMap` của transaction để luôn trỏ đúng vị trí sau khi doc đã đổi kích thước.

### 4.7. Review trước khi áp (pending change review)
Trước khi người dùng "Accept" một đề xuất AI, `pending-change-review-extension.ts` hiển thị preview ngay tại vị trí sẽ chèn/xoá bằng ProseMirror decoration (widget cho insert, node decoration cho delete/replace) — không sửa document thật cho tới khi user xác nhận.

## 5. Kịch bản: hỏi thông tin thuần túy về vị trí con trỏ/selection (không yêu cầu sửa)

Ví dụ thực tế: người dùng bôi đen 1 đoạn rồi hỏi "vị trí đang bôi" → bot trả lời "Đoạn bạn đang bôi nằm trong block b3$. Cụ thể là phần gạch đầu dòng dưới mục ..., ở dòng: '...'" — bot biết chính xác block id và mô tả lại nội dung xung quanh **mà không sửa gì cả**.

### 5.1. Định dạng Block ID `"bN$"` — sinh ra từ đâu

Có 2 lớp:

1. **ID gốc `bN`** — [backend/services/api/src/bookforge_api/editor/block_document.py](../backend/services/api/src/bookforge_api/editor/block_document.py) hàm `BlockDocument.from_html()` (~dòng 229-261): khi parse `content_html` thành các block top-level (qua `_BlockSplitter`, một `HTMLParser` con tách `h1-h6/p/ul/ol/blockquote/pre/table/hr/figure/img/math`...), mỗi block được gán `id=f'b{idx + 1}'` — **đánh số theo thứ tự parse HTML lần này** (1-based), không phải UUID bền vững. Block được AI chèn mới giữa phiên dùng id khác, dạng `nN` (từ `_new_id()`), để không đụng độ với `bN` đã tồn tại.
2. **Sentinel `$`** — hàm `sentinel_id(block)` trong `block_view.py` (`return f'{block.id}$'`). Bắt buộc phải có `$` ở cuối; `strip_sentinel()` từ chối id không có `$` — đây là cơ chế phát hiện khi LLM hallucinate/cắt cụt id (model bịa hoặc cắt ngắn id gần như luôn làm rớt mất `$`). Trong instruction gửi cho agent (`_editor_loop_instruction()`) có nhắc thẳng: *"Block ids ALWAYS include the trailing $ — write 'b7$', not 'b7'. An id without it is rejected."*

Vì id đánh lại theo mỗi lần parse HTML, `"b3$"` chỉ có nghĩa **trong phạm vi 1 lượt xử lý request** — không nên coi là ID bền vững để tham chiếu chéo giữa các lần khác nhau.

### 5.2. Vì sao bot trả lời được ngay mà không cần gọi tool

`_selection_hint()` trong [backend/services/api/src/bookforge_api/chat/editor_agent.py](../backend/services/api/src/bookforge_api/chat/editor_agent.py) (~dòng 523-607) đã tự cấp sẵn ngữ cảnh vào prompt theo 3 tầng:

- **Luôn có**: dòng `[Đoạn người dùng đang chọn]: {selected_text}`.
- **Tầng 1** (selection nằm gọn trong 1 block text phẳng — trường hợp phổ biến nhất): in nguyên `project_block(block)` dạng `<block id="b3$" type="...">...</block>`, kèm đánh dấu chính xác điểm bắt đầu/kết thúc selection bằng token `⟦SEL⟧...⟦/SEL⟧` chèn vào text.
- **Tầng 2** (biết block nhưng không biết offset ký tự — vd list/table phức tạp): in `project_block` của block đó, nói rõ "exact character offsets are not available".
- **Tầng 2b** (selection trải nhiều block): nếu tổng nội dung < `SELECTION_HINT_CHAR_BUDGET` (4000 ký tự) thì in hết các block liên quan; nếu vượt ngân sách chỉ nói "covers N blocks, from bX$ to bY$. Use read_blocks to read them" — lúc này agent **mới cần** chủ động gọi tool đọc thêm.
- **Tầng 3** (không xác định được `selection_range`): chỉ có `selected_text` thuần, không có block id.

Vì hint đã chứa sẵn cả block id lẫn nội dung xung quanh, LLM trả lời trực tiếp bằng text mà **không gọi bất kỳ write-tool nào** (`update_block`, `insert_blocks`...) — không có sửa đổi nào xảy ra. Không có instruction tường minh kiểu "nếu chỉ hỏi vị trí thì đừng gọi tool sửa"; điều này chỉ là hệ quả tự nhiên của cách pydantic-ai Agent hoạt động (chỉ gọi tool khi model tự thấy cần).

### 5.3. Tool đọc block (read-only) khi cần thêm ngữ cảnh

[backend/services/api/src/bookforge_api/chat/editor_edit_tools.py](../backend/services/api/src/bookforge_api/chat/editor_edit_tools.py) có các tool thuần đọc, không sửa document:

- `read_blocks(doc, start_id=None, end_id=None)` (~dòng 103-129): nhận **block id có sentinel** (`"b3$"`) làm mốc start/end (bỏ trống thì đọc toàn bộ); trả về `{'markdown': ..., 'truncated': bool, 'note': str}` — `markdown` là chuỗi ghép các `<block id="bN$" type="...">...</block>`. Có giới hạn `READ_BLOCKS_CHAR_BUDGET` (14000 ký tự ≈ 3.5k token), vượt quá sẽ báo `truncated=True` và gợi ý thu hẹp phạm vi.
- `get_outline()` (~dòng 79-100): trả outline gồm `block_id`, `title/level/word_count` — dùng để agent định vị nhanh trong tài liệu dài trước khi đọc chi tiết.
- `search_document()` (~dòng 132-144): tìm theo từ khoá, trả `block_id` + `snippet`.

Với tài liệu nhỏ, `run_editor_assistant_on_html()` preload luôn toàn bộ nội dung vào instructions và nói thẳng với model: *"You already have the entire content — do NOT call get_outline or read_blocks; answer directly..."*. Với tài liệu lớn, model được yêu cầu gọi `get_outline` trước rồi `read_blocks`/`search_document` khi cần.

### 5.4. Response trả về khi không có sửa đổi nào

Trong `run_editor_assistant_on_html()` (~dòng 1644-1673), dù model không gọi tool sửa nào, code vẫn build response đầy đủ:

```python
change_set = build_change_set(doc)   # doc không đổi -> change_set = []
return {
    'answer': plain_text(answer) or 'Mình đã xử lý xong.',   # câu trả lời text tự nhiên của model
    'change_set': change_set,          # [] — không có write-tool nào chạy
    'content_html': rendered_html,     # giữ nguyên, doc không mutate
    'summary': edit_summary.summarize(change_set),  # rỗng khi change_set rỗng
    ...
}
```

`answer` chính là field `EditorResponse.answer` mà model tự soạn (ví dụ câu "Đoạn bạn đang bôi nằm trong block b3$..."), được truyền nguyên vẹn lên tới response của API `/editor/assistant`.

### 5.5. Frontend phân biệt "trả lời text thuần" vs "đề xuất thay đổi"

[frontend/src/components/TiptapEditor/partial/document-ai-chat-panel.tsx](../frontend/src/components/TiptapEditor/partial/document-ai-chat-panel.tsx) (~dòng 437, 525-556):

```ts
const hasReviewableChanges = (response.change_set?.length ?? 0) > 0;
```

- **`change_set` rỗng** (câu hỏi thông tin thuần túy như "vị trí đang bôi"): `hasReviewableChanges = false` → chat bubble chỉ render `<FormattedAnswer content={message.content} />` (text trả lời), **không** có `ReviewCard`, **không** highlight vùng nào trong editor, editor trở lại editable ngay lập tức.
- **`change_set` có phần tử** (yêu cầu sửa nội dung): `hasReviewableChanges = true` → panel gọi `setPendingChangeReview()` để highlight vùng bị ảnh hưởng trực tiếp trong editor, chat bubble render thêm `<ReviewCard>` với các nút "Xem vị trí / Hoàn tác / Chấp nhận".

### 5.6. Tóm tắt luồng đầu-cuối cho câu hỏi "vị trí đang bôi"

```
FE: gửi editor_context {kind:'selection', anchor, head} + selected_text + content_html snapshot
        ▼
api/editor.py: _resolve_context_kind = 'selection', _selection_range = (anchor, head)
        ▼
run_editor_assistant(): doc = BlockDocument.from_html(content_html)  -- gán id bN/nN
        ▼
_selection_hint(doc, selection_range, ...)
        │  caret.selection_block_range / caret.selection_in_text_block định vị block + offset ký tự
        │  build hint: <block id="b3$" ...> + đánh dấu ⟦SEL⟧...⟦/SEL⟧
        ▼
LLM (pydantic_ai Agent) nhận prompt đã có đủ ngữ cảnh
        │  trả lời trực tiếp qua EditorResponse.answer, KHÔNG gọi write-tool
        │  (có thể gọi read_blocks/search_document nếu cần thêm, nhưng không bắt buộc)
        ▼
change_set = build_change_set(doc) = []   (doc không bị mutate)
        ▼
Response: { answer: "Đoạn bạn đang bôi nằm trong block b3$...", change_set: [], summary: '' }
        ▼
FE: hasReviewableChanges = false -> chỉ hiện chat bubble text, không ReviewCard, không highlight editor
```

## 6. Tài liệu upload — vì sao read-only, và tool đọc hoạt động thế nào trên đó

Câu hỏi cụ thể: khi người dùng **upload** file (PDF/DOCX/PPTX/ảnh) thay vì tự soạn trong editor, các tool read-only (`read_blocks`, `get_outline`, `search_document`) hoạt động ra sao, và có khác biệt gì so với tài liệu tạo trực tiếp trong app?

### 6.1. Luồng upload → có content_html

- `POST /upload` ([backend/services/api/src/bookforge_api/api/documents.py](../backend/services/api/src/bookforge_api/api/documents.py), hàm `upload_document`): chỉ tạo bản ghi `Document(status='queued', ...)` và lưu file gốc vào storage — **chưa có `content_html`** ở bước này. Việc parse thật sự (OCR, convert docx/pptx, trích văn bản PDF) được đẩy sang **worker nền** qua `enqueue_ingest`.
- Worker chạy `ingest_document_workspace()` (`backend/services/api/src/bookforge_api/ingest/pipeline.py`): trích nội dung từng trang (OCR nếu là ảnh scan, `pymupdf4llm` nếu PDF born-digital, convert riêng cho pptx), rồi `build_editor_html()` (`backend/services/api/src/bookforge_api/editor/markdown_document.py`) ghép mỗi trang thành một khối `<section data-page="N">...</section>`, nối lại thành `content_html` hoàn chỉnh.
- Kết quả được ghi vào bảng `EditorDocument` (field `content_html`, `content_markdown`) — **cùng một bảng** dùng cho tài liệu tạo trực tiếp trong app (qua chat, `create_document_from_markdown`/`create_document_from_draft_html`). Về schema, upload và tự soạn dùng chung cơ chế lưu trữ.

### 6.2. Điểm khác biệt mấu chốt: `editor_capability = view_only`

Ngay trong bước ingest, pipeline **luôn set cứng** `document.editor_capability = EDITOR_CAPABILITY_VIEW_ONLY` cho mọi tài liệu upload (PDF/DOCX/PPTX/ảnh) — **bất kể ai là owner**. Ngược lại, tài liệu tạo trong app qua chat luôn được set `editor_capability='editable'`. Đây là field trên model `Document` ([backend/services/api/src/bookforge_api/models/document.py](../backend/services/api/src/bookforge_api/models/document.py)), độc lập với quyền chia sẻ (`DocumentShare`, `visibility`, `public_permission`).

`services/access.py::document_permissions()` tính `can_edit_content = can_edit AND document.editor_capability == 'editable'` — đây là **nguồn chân lý duy nhất** quyết định AI/người dùng có được sửa nội dung hay không. Route ghi/sửa trong `api/editor.py` (endpoint `/editor/assistant` và các endpoint block khác) đều gọi `get_document_for_edit()` rồi `_assert_document_editable()` **trước khi** parse `content_html` — nếu tài liệu là `view_only`, request bị chặn ngay ở tầng route, AI không có cơ hội gọi bất kỳ tool ghi nào (`update_block`, `insert_blocks`, `delete_blocks`...).

→ **Hệ quả thực tế**: với tài liệu vừa upload, chatbot AI mặc định chỉ có thể *trả lời câu hỏi / mô tả nội dung* (dùng tool đọc), **không thể tự sửa** trừ khi có một cơ chế khác (ngoài phạm vi đã khảo sát) chuyển `editor_capability` sang `editable` — có thể là một nút "Convert to editable"/"Bật chỉnh sửa" ở UI, chưa xác nhận được trong lần nghiên cứu này (xem mục câu hỏi mở bên dưới).

### 6.3. Vì sao tool đọc vẫn hoạt động bình thường trên tài liệu view-only

Việc **đọc** chỉ yêu cầu `can_view_document()` (qua `get_document_for_view()`), hoàn toàn không bị chặn bởi `editor_capability` — nghĩa là AI **luôn đọc được** nội dung tài liệu upload qua `read_blocks`/`get_outline`/`search_document` miễn người dùng có quyền xem, dù không sửa được.

Về mặt implementation, 3 tool này (`read_blocks`, `get_outline`, `search_document` trong `editor_edit_tools.py`) nhận tham số duy nhất là `doc: BlockDocument` — một đối tượng **hoàn toàn nằm trong bộ nhớ của request hiện tại**, không có tham số `db: Session`, không import SQLAlchemy, không gọi lại storage. `doc` được parse **một lần duy nhất mỗi request** ở đầu `editor_agent.py` (`doc = BlockDocument.from_html(content_html)`), với `content_html` đã được route load sẵn từ `EditorDocument` mới nhất trong DB **trước khi** vào agent loop. Do đó 3 tool đọc này chỉ project lại dữ liệu đã có sẵn trong `doc.blocks` — tuyệt đối không có khả năng ghi hay truy vấn thêm DB/storage. Việc kiểm tra quyền được thực hiện đúng 1 lần, ở tầng route, trước khi bất kỳ tool nào chạy.

### 6.4. Khác biệt cấu trúc block khi parse tài liệu upload

`BlockDocument.from_html()`/`_BlockSplitter` ([block_document.py](../backend/services/api/src/bookforge_api/editor/block_document.py)) xử lý `<section data-page="N">` — "vỏ" bao mỗi trang mà ingest pipeline sinh ra cho tài liệu upload — và lưu vào field `page_attrs` trên từng `Block`. Tài liệu tự soạn trong TipTap thường không có các `<section data-page>` này nên `page_attrs = None` cho phần lớn/mọi block.

Tuy nhiên việc đánh số `bN` (id) chạy tuần tự qua toàn bộ block **bất kể ranh giới trang** — nghĩa là `read_blocks`/`get_outline`/`search_document` trả về cho AI một luồng `b1, b2, b3...` liên tục xuyên suốt các trang; **AI không tự động biết ranh giới trang** vì `page_attrs` không được expose ra ngoài qua các tool đọc này (chỉ ảnh hưởng nội bộ khi `to_html()` tái tạo lại `<section data-page>` bao quanh khi ghi ngược, đảm bảo cấu trúc phân trang không bị mất nếu tài liệu sau này được chuyển sang editable và chỉnh sửa).

Ngoài phần trang, cơ chế parse block (mapping thẻ→loại block, xử lý ảnh/figure, công thức toán...) là **giống hệt nhau** cho mọi nguồn HTML — không có nhánh code riêng theo nguồn gốc tài liệu (`source_kind`). Tài liệu upload thường có nhiều block hơn tài liệu tương đương tự soạn, do mỗi trang PDF/DOCX tạo ranh giới `<section>` riêng và nội dung OCR/markdown-converted thường tách đoạn khác cách gõ tay.

## 7. Câu hỏi / điểm chưa rõ — cần tìm hiểu thêm lần sau

- Chưa xác định cơ chế **lock/khoá đồng thời**: nếu 2 người cùng sửa document (collab realtime) thì `editor_context` (vị trí con trỏ) của người A còn hợp lệ khi người B đã chèn nội dung trước đó không? Cần đọc thêm phần collaboration/websocket (nếu có) trong backend.
- `editor.py::_geometry_anchor()` xử lý anchor cho tính năng chèn hình học (JSXGraph) — chưa rõ toàn bộ luồng `services/geometry/generation.py` sinh hình như thế nào, cần đọc kỹ thêm để hiểu cách AI quyết định kích thước/loại hình chèn tại vị trí con trỏ.
- Chưa kiểm tra cơ chế lưu xuống DB: `block_document.py` thao tác trên blocks trong bộ nhớ, nhưng chưa rõ điểm nào commit xuống database (model/schema DB tương ứng, transaction/versioning ra sao) — cần tìm thêm ở tầng service/repository lưu document.
- Chưa rõ giới hạn/validate độ dài `editor_context` hoặc rate-limit khi gọi liên tục endpoint `/editor/assistant`.
- Block ID `"bN$"` được đánh lại theo mỗi lần parse HTML trong 1 request — chưa rõ điều gì xảy ra nếu người dùng tiếp tục hỏi/sửa dựa trên id đã nhắc ở câu trả lời trước (turn trước) nhưng document đã thay đổi cấu trúc (id có thể trỏ nhầm block) — cần xem cơ chế lưu lịch sử hội thoại (`chat history`) có "chốt" lại snapshot block id theo từng turn hay không.
- Chưa đọc kỹ `SELECTION_HINT_CHAR_BUDGET` (4000 ký tự) và `READ_BLOCKS_CHAR_BUDGET` (14000 ký tự) được cấu hình/điều chỉnh ở đâu, có phụ thuộc vào model/context window đang dùng không.
- Chưa xác nhận được cơ chế **chuyển `editor_capability` từ `view_only` sang `editable`** cho tài liệu đã upload (ví dụ nút "Bật chỉnh sửa"/"Convert to editable" ở UI) — route xử lý việc này nằm ngoài phạm vi các file đã đọc ở mục 6, cần tìm thêm trong `api/documents.py` hoặc route riêng.
- Chưa rõ `page_attrs` (đánh dấu ranh giới trang cho tài liệu upload) có được AI "nhìn thấy" qua cách nào khác ngoài 3 tool đọc đã khảo sát không — ví dụ liệu `project_block()` trong `block_view.py` có in kèm số trang vào output cho model hay hoàn toàn ẩn đi.
