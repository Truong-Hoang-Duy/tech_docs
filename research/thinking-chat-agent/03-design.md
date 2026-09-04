# 03 — Thiết kế: Thinking Chat Agent (Summary Bar + Execution Timeline)

> Nguồn sự thật: `02-findings.md` và 6 file code đã upload
> (`chat/adk_agent.py`, `api/editor.py`, `chat/editor_agent.py`, `api/_sse.py`,
> `use-chat-with-ai.ts`, `document-ai-chat-panel.tsx`).
> Mọi khẳng định về file **chưa** upload (`api/chat.py`, `HomePage/index.tsx`,
> `document-ai-chat-message.tsx`, `lib/read-sse-stream.ts`, `core/settings.py`) đều dựa trên
> mô tả trong findings, **không** dựa trên đọc code — đã đánh dấu 🟡 ở từng chỗ.

---

## 0. Quyết định nghiệp vụ còn treo

5 câu hỏi ở `01-brief` chưa được trả lời. Thiết kế dưới đây **không đợi** chúng: mỗi câu được gán
một **mặc định làm việc** để không chặn tiến độ, kèm ghi rõ đổi câu trả lời thì đổi cái gì.

| # | Câu hỏi | Mặc định đang dùng | Đổi thì ảnh hưởng |
|---|---|---|---|
| 1 | Làm cả hai luồng chat hay chỉ một? | **Cả hai, nhưng chia pha** — chat ngoài canvas trước (Pha 1), canvas sau (Pha 2) | Nếu chỉ cần canvas → đảo thứ tự pha, nhưng chi phí gấp ~3 lần Pha 1 |
| 2 | Người xem là học sinh hay cả giáo viên/admin? | **Học sinh là mặc định**: timeline chỉ hiện nhãn nghiệp vụ tiếng Việt, không hiện tên tool kỹ thuật, không hiện lỗi thô | Nếu cần chế độ kỹ thuật → thêm một cấp `verbosity` ở FE; dữ liệu BE đã đủ, không phải sửa BE |
| 3 | Timeline có xem lại được sau F5 không? | **Có** — ghi vào `metadata_json` | Nếu không cần → bỏ toàn bộ phần persist, tiết kiệm ~20% khối lượng và xoá hẳn rủi ro phình response |
| 4 | Mặc định mở hay thu gọn? | **Thu gọn thành Summary Bar**, bấm mới bung timeline; đang chạy thì tự bung | Chỉ là CSS/state ở FE, đổi lúc nào cũng được |
| 5 | Chấp nhận chậm/tốn hơn không? | **Phương án (b)** — không đổi hành vi agent, chỉ phơi bày cái vốn đã chạy | Chọn (a) → xem §7, đây là thay đổi lớn nhất và **canvas không làm được** vì trần timeout hạ tầng |

**Lý do chọn (b) làm mặc định:** findings §"Điều brief không hỏi" mục 5 cho thấy repo hiện chỉ có
vòng "thử — sai — sửa" thật ở **nhánh hình học** (`last_geometry_error`, `geometry_attempts`,
`editor_agent.py:1295–1414`, `:1600–1622`). Ở các nhánh khác, agent không có cơ chế tự sửa để mà
hiển thị. Muốn Status Indicators có nội dung thật ở mọi loại câu hỏi thì phải đổi prompt + cấu trúc
vòng lặp — đó là dự án khác, và nó đụng trần timeout 240s của canvas.

---

## 1. Kết luận thiết kế trong một trang

1. **Một hợp đồng sự kiện duy nhất** cho cả hai luồng: thêm đúng **một** giá trị `type` mới là
   `step`, upsert theo `id`. Không sửa giao thức, không sửa endpoint, không đổi version API.
2. **Chat ngoài canvas: rẻ.** Dữ liệu bước đã chạy qua `_aiter_agent_sse_events`
   (`adk_agent.py:1143`) rồi bị vứt tại chỗ. Chèn ở đây là đủ.
3. **Canvas: đắt, nhưng có đường vòng.** Không đổi `agent.run_sync` sang async
   (rủi ro cao, §5.2). Thay vào đó **gắn cảm biến vào chính các closure tool** đã khai trong
   `run_editor_assistant_on_html` (`editor_agent.py:1247+`) và bơm sự kiện ngược về
   `asyncio.Queue` sẵn có trong `_stream_editor_events` (`api/editor.py:1641`).
4. **Không bịa bước.** Nội dung reasoning của mô hình hiện **không** được nhận
   (findings Q3); nó là *tuỳ chọn* có cờ riêng, **không** phải nền tảng của tính năng.
   Không dùng LLM phụ để "kể lại quá trình suy nghĩ" — đó là bịa hậu kỳ, phá đúng cái giá trị
   giáo dục mà tính năng muốn có.
5. **Persist bằng `metadata_json`**, không bảng mới, không migration.
6. **Summary Bar do FE tự tính** từ danh sách step. BE không phát event riêng cho nó.

---

## 2. Hợp đồng sự kiện (phần dùng chung BE ↔ FE)

Đây là thứ phải chốt **trước** khi viết code hai phía, vì nếu không FE sẽ phải viết hai bộ adapter
(findings §"Chưa xác định được" mục 3).

### 2.1 Frame lúc chạy

Khung ngoài do `with_sse_lifecycle` quy định, **không đổi** (`api/_sse.py:86–110`):

```json
{ "type": "step", "data": { ... }, "trace_id": "..." }
```

`data` — một mục timeline:

```jsonc
{
  "id": "s3",                  // duy nhất trong một lượt; dùng để upsert
  "seq": 3,                    // thứ tự phát, FE sắp theo cái này
  "kind": "tool_call",         // thinking | tool_call | note
  "label": "Đang tra cứu tài liệu",   // câu tiếng Việt, an toàn để hiện cho học sinh
  "detail": "đạo hàm hàm hợp", // tuỳ chọn: đối số đã rút gọn/che
  "status": "running",         // running | ok | failed
  "at": "2026-09-04T10:11:12.345Z"
}
```

Quy tắc:

- **Upsert theo `id`.** Một tool call phát 2 frame cùng `id`: `status: running` lúc gọi,
  rồi `ok`/`failed` lúc có kết quả. FE ghi đè, không nối thêm.
- `kind: "thinking"` chỉ xuất hiện khi cờ ở §6 bật **và** provider thật sự trả reasoning về.
- `label` là **thứ duy nhất bắt buộc hiển thị được**. `detail` có thể rỗng.
- **Không đặt tên tool kỹ thuật vào `label`.** Tên tool đi ở trường riêng `tool` (tuỳ chọn),
  để chế độ kỹ thuật (quyết định #2) dùng sau mà không phải đổi hợp đồng.

### 2.2 Frame lúc kết thúc

Không thêm event mới. Timeline hoàn chỉnh nằm trong `metadata` của message assistant, tức là nó
đã có sẵn trong payload `done` (findings Q2: `done` mang `assistant_message`).

### 2.3 Hình dạng lưu trong `metadata_json`

```jsonc
"timeline": {
  "v": 1,
  "steps": [ /* như trên, đã ở trạng thái cuối */ ],
  "summary": { "retrieved": 5, "read": 3, "tools": 9, "failed": 1, "duration_ms": 41200 },
  "truncated": false
}
```

`summary` được BE tính sẵn **dù FE cũng tính được** — lý do: session cũ có thể bị cắt bớt `steps`
(§4.3), lúc đó FE không cộng lại được con số đúng.

### 2.4 Tại sao không phá client cũ

`with_sse_lifecycle` cho mọi `type` lạ đi qua nguyên vẹn (`api/_sse.py:113–121` — nó chỉ đặc biệt
hoá `done`/`error`). 🟡 Phía FE, findings Q10 trích `read-sse-stream.ts` cho thấy `consume` gọi
`onFrame` rồi chỉ branch trên `start`/`error`/`done`. Kết luận: **thêm `step` không phá gì.**

---

## 3. Phần BE — luồng chat ngoài canvas (Pha 1)

### 3.1 Điểm sửa duy nhất

`services/api/src/bookforge_api/chat/adk_agent.py` — `_aiter_agent_sse_events` (`:1143`).

Ba chỗ mất mát, sửa từng chỗ:

| Hiện tại (`:1180–1206`) | Sửa thành |
|---|---|
| `FunctionToolCallEvent` → chỉ lấy `tool_name`, đổi qua `_TOOL_STATUS_TEXT` thành một câu chung, **đối số bị bỏ** | Vẫn phát `status` như cũ (giữ tương thích), **thêm** một `step` `kind=tool_call, status=running` có `detail` là đối số đã lọc |
| `FunctionToolResultEvent` → chỉ dùng để quyết định dừng sớm (`ask_user`, `set_output`), **không phát gì** | Thêm `step` cùng `id`, `status=ok/failed`, `detail` là digest kết quả |
| Không có nhánh cho `ThinkingPart`/`ThinkingPartDelta` → reasoning rơi vào khoảng trống | Thêm nhánh, gộp delta thành câu, phát `step` `kind=thinking` — **chỉ khi cờ bật** (§6) |

Giữ nguyên toàn bộ logic dừng sớm hiện có (`return` khi `ask_user`, khi `set_output` +
`warm_continue`) và nhánh `UsageLimitExceeded` với `_synthesize_from_partial_run` — chỉ **thêm**
`yield`, không đổi luồng điều khiển. Khi `UsageLimitExceeded` nổ, phát thêm một `step`
`kind=note, status=failed` để timeline nói rõ "đã chạm trần vòng lặp" thay vì đứt lặng.

### 3.2 Ghép cặp call ↔ result

🟡 **Đây là giả định phải kiểm chứng trước khi code.** Cần biết `FunctionToolCallEvent` và
`FunctionToolResultEvent` của `pydantic_ai` 1.94 có mang một `tool_call_id` khớp nhau không.
Đoạn code hiện tại chỉ đọc `tool_name` (`:1176–1178`, `:1187`), nên chưa chứng minh được.

- **Nếu có `tool_call_id`** → dùng làm `id`. Đúng cả khi agent gọi song song.
- **Nếu không** → dùng bộ đếm cục bộ + hàng đợi FIFO theo `tool_name`. Chấp nhận sai thứ tự trong
  trường hợp gọi song song cùng tên tool; đây là rủi ro hiển thị, không phải rủi ro dữ liệu.

### 3.3 Nội dung `detail` — quy tắc lọc

Đây là chỗ dễ rò rỉ nhất: đối số tool chứa `query` do người dùng gõ, `document_id`, và kết quả tool
chứa **nguyên văn nội dung tài liệu**. Không được bê nguyên ra timeline.

Quy tắc **allowlist theo tool**, mọi thứ ngoài danh sách bị bỏ:

| Tool (`adk_agent.py:743–823`) | `detail` lúc gọi | `detail` lúc có kết quả |
|---|---|---|
| `retrieve_knowledge`, `search_corpus`, `search_library`, `search_documents`, `find_passages` | `query`, cắt 80 ký tự | số kết quả (`len`), không có nội dung |
| `read_pages` | khoảng trang (`start_page`–`end_page`) + tên tài liệu | số trang đọc được; `coverage.truncated` → `status=failed` |
| `read_section`, `get_document_outline` | tên tài liệu | — |
| `read_document`, `get_document_overview`, `get_document_summaries` | tên tài liệu | — |
| `law_*` | từ khoá tra cứu | số điều/văn bản tìm được |
| `write_draft`, `check_draft`, `set_output`, `ask_user` | — | — |

**Tên tài liệu thay cho `document_id`:** `_aiter_agent_sse_events` hiện không có tham chiếu tới
`reader`/`documents` để tra tên. Cách rẻ nhất: **truyền vào một `label_for_document: Callable[[str], str]`**
làm tham số mới của hàm. 🟡 Chỗ gọi hàm này nằm trong `api/chat.py` (chưa upload) — cần xác nhận
danh sách `Document` có trong scope tại điểm gọi. Nếu không có, chấp nhận Pha 1 hiển thị
"Đọc tài liệu" không kèm tên, bổ sung sau.

### 3.4 Gom và ghi timeline

**Không** đổi chữ ký `on_final`, **không** trả timeline qua nó. Thay vào đó:
`_aiter_agent_sse_events` là generator yield `(type, data)`; nơi tiêu thụ nó
🟡 (`_stream_chat_events`, `api/chat.py:1397` theo findings) **tự tích luỹ các tuple có
`type == 'step'`** khi chuyển tiếp, rồi nhét vào `metadata` ở bước persist
🟡 (`_persist_chat_turn`).

Lý do làm vậy: findings §"Điều brief không hỏi" mục 4 — chat ngoài canvas **nhả session DB trước
khi stream** (`_release_request_session`). Ghi dần trong lúc chạy sẽ phải mở `session_scope()`
riêng cho mỗi bước. **Ghi một lần ở cuối, trong đúng transaction persist đã có.**

### 3.5 Đường fallback

FE có nhánh `shouldFallbackToJson` → gọi `APISendChatMessage` (non-stream). Đường đó **không**
đi qua `_aiter_agent_sse_events`, nên **không có timeline lúc chạy**. Chấp nhận: sau khi lượt xong,
message có `metadata.timeline` rỗng. FE phải xử lý `timeline == null` như "không có gì để hiện",
không phải lỗi.

🟡 Nếu muốn cả nhánh non-stream cũng có timeline thì phải xem `api/chat.py` chạy agent bằng đường
nào ở nhánh đó — chưa xác định, xem §9.

---

## 4. Phần BE — luồng canvas (Pha 2)

### 4.1 Phương án chọn: gắn cảm biến vào tool, giữ `run_sync`

**Không** đổi `agent.run_sync` (`editor_agent.py:1813`) sang `run_stream_events`. Lý do ở §5.2.

Cách làm:

1. Thêm tham số tuỳ chọn `emit: Callable[[dict], None] | None = None` vào
   `run_editor_assistant` (`:765`) → truyền xuống `run_editor_assistant_on_html` (`:1003`).
   Mặc định `None` ⇒ endpoint non-stream `/assistant` (`api/editor.py:1685`) không đổi hành vi.
2. Trong `run_editor_assistant_on_html`, bọc từng closure `@agent.tool_plain` (`:1247–1700`)
   bằng một helper phát `step` trước và sau khi gọi thân hàm. Các tool này **đã** có sẵn chỗ móc:
   chúng đều là closure trong cùng scope, đã đang `nonlocal document_tool_calls` (`:1249`),
   `nonlocal last_geometry_error` (`:1295`, `:1336`), `nonlocal geometry_attempts` (`:1600`).
3. `emit` được gọi **từ threadpool**. Trong `_stream_editor_events` (`api/editor.py:1641`), lấy
   `loop = asyncio.get_running_loop()` trước khi `run_in_threadpool(_run)`, rồi
   `emit = lambda d: loop.call_soon_threadsafe(queue.put_nowait, ('step', d))`.
   `queue` đã tồn tại, vòng `while True: item = await queue.get()` (`:1673–1679`) đã chuyển tiếp
   nguyên tuple ra ngoài — **không phải sửa gì ở vòng tiêu thụ.**

### 4.2 Cái này mua được gì mà bản `run_sync` hiện tại không có

- **Status Indicators có nội dung thật ngay lập tức.** Nhánh hình học là chỗ duy nhất trong repo có
  vòng thử–sai thật: `plan_geometry_operations` trả `{'ok': False, 'errors': [...]}` và ghi
  `last_geometry_error` (`:1299`, `:1308`, `:1317`), rồi agent gọi lại. Với cảm biến, chuỗi này
  hiện lên đúng như mô tả nghiệp vụ muốn: *"Dựng hình — Thất bại: sai ràng buộc — Thử lại"*.
- **`request_limit_hit` / `turn_timeout_hit`** (`:1825–1838`) trở thành một `step`
  `kind=note, status=failed` cuối timeline, thay vì một câu xin lỗi chung chung.
- **Không đụng** `_TurnBudgetModel`, không đụng nhánh `except` hình học ở
  `execute_editor_assistant` (`api/editor.py:1484–1520`), không đụng bất biến
  `finally: pass  # do not cancel producer` (`:1681`).

### 4.3 Cái này KHÔNG mua được

- **Không có thinking steps ở canvas.** `run_sync` không phơi ra event của mô hình.
- **Không có token streaming.** Câu trả lời vẫn về một cục ở cuối (`:1655–1657`).
- Nghĩa là: canvas sẽ có **Tool Logs + Status Indicators**, thiếu **Thinking Steps**.
  Nếu quyết định #2/#5 bắt buộc phải có thinking ở canvas → phải làm §5.2, và phải chấp nhận
  rủi ro ở đó.

### 4.4 Persist ở canvas

Giống §3.4: `execute_editor_assistant` gom `step` đã phát rồi nhét vào `response_metadata` trước
khi gọi `_persist_canvas_chat_turn` (`api/editor.py:1459–1467` và các nhánh tương đương).
🟡 Có **ít nhất 3 nhánh return** khác nhau trong `execute_editor_assistant` cùng gọi
`_persist_canvas_chat_turn` (nhánh `KnowledgeServiceError` + geometry, nhánh `Exception` + geometry,
và nhánh thành công) — cả ba đều phải được nhét timeline, nếu không lượt lỗi hình học sẽ mất đúng
cái timeline có giá trị nhất. Cần Claude Code liệt kê đủ các nhánh trước khi sửa.

### 4.5 Trần kích thước

Canvas có `request_limit = 25` (`:1810`) và `tool_calls_limit = None` cho request thường —
tức **không giới hạn số tool call**. Timeline có thể dài bất thường.

Áp trần ở tầng gom, cả hai luồng:

- tối đa **60 step** lưu vào `metadata_json`; vượt thì giữ 30 đầu + 30 cuối, đặt `truncated: true`;
- `detail` cắt **200 ký tự**;
- tổng `timeline` serialize vượt **32 KB** thì bỏ hết `detail`, giữ `label` + `status`.

Lý do: findings Q6 cảnh báo `metadata_json` được trả **nguyên vẹn** ở mọi lần liệt kê message của
phiên (`_serialize_message`, `_serialize_canvas_message`). Không có trần thì response
`GET .../sessions/{id}` phình theo số message × độ dài timeline.

**Ngưỡng để xét lại:** nếu đo thật thấy p95 > 8 KB/lượt, chuyển sang bảng riêng. Việc chuyển
**không phá FE** vì FE chỉ đọc một khoá — đổi chỗ đọc là việc của BE serializer.

---

## 5. Đánh đổi đã cân nhắc và loại

### 5.1 Loại: phát event riêng cho Summary Bar

Thêm `type: "summary"` phát dần trong lúc chạy. **Loại** vì FE cộng được từ `steps`, và mỗi event
thừa là một chỗ nữa để hai luồng lệch nhau.

### 5.2 Loại (ở Pha 2): đổi canvas sang `run_stream_events`

Đây là phương án "đúng chuẩn", cho parity hoàn toàn với chat ngoài canvas — thinking parts, token
streaming, cùng một điểm chèn. **Loại ở vòng này**, giữ lại cho Pha 3.

Lý do loại:

| Rủi ro | Bằng chứng |
|---|---|
| Toàn bộ tool của canvas là **hàm đồng bộ có I/O nặng**: đọc/ghi DB (`db`, `document`), gọi pipeline JSXGraph, render, verify (`:1321–1436`). Chạy chúng trong event loop sẽ chặn loop; chạy đúng cách đòi bọc từng tool qua threadpool | `editor_agent.py:1247–1700` |
| `agent.run_sync` được gọi trong `run_in_threadpool(_run)`, và `_run` mở `session_scope()` **đồng bộ** bọc cả lượt | `api/editor.py:1644–1653` |
| Có `_TurnBudgetModel` bọc model với deadline + per-call timeout, và `_is_timeout_exc` bắt lỗi timeout để trả câu trả lời mềm | `editor_agent.py:1065–1071`, `:1825` |
| Bất biến "không huỷ producer khi client ngắt" phải sống sót — nếu vỡ, người dùng đóng tab giữa chừng **mất thay đổi đã ghi vào tài liệu** | `api/editor.py:1681`, findings mục 3 |
| Hai nhánh `except` lớn trong `execute_editor_assistant` đang dựa vào việc `run_editor_assistant` **trả về hoặc ném**, không phải yield | `api/editor.py:1432–1520` |

Đổi kiến trúc ở đây là 5 thay đổi rủi ro cao để mua thêm **thinking steps** — thứ mà §6 cho thấy
còn chưa chắc provider có trả về. Không đáng ở vòng đầu.

### 5.3 Loại: dùng `retrieval_traces` làm nguồn timeline

Findings Q5 đóng cửa: không có `message_id`/`session_id`, một dòng cho cả lượt, gắn vào
`ready_documents[0]`. Nó là vết kiểm toán cấp tài liệu.

### 5.4 Loại: gọi LLM phụ để sinh mô tả "AI đang nghĩ gì"

Rẻ về kỹ thuật, đắt về tiền, và **sai về bản chất**: nó tạo một lời kể hậu kỳ không tương ứng với
cái agent thật sự làm. Với một tính năng bán bằng chữ "minh bạch" và "giá trị giáo dục", đây là
lựa chọn tự phá mục tiêu.

### 5.5 Loại: bảng riêng cho timeline ngay từ đầu

`metadata_json` đã là JSON tự do, đã được serialize về FE, đã được trả khi mở phiên cũ
(findings Q6, Q8). Bảng riêng là chi phí migration để giải một vấn đề chưa đo được. Áp trần §4.5
trước, đo, rồi mới quyết.

---

## 6. Thinking steps — phần rủi ro nhất

**Hiện trạng:** `model_router.usage_to_dict` chỉ moi `reasoning_tokens`/`thoughts_tokens`/
`thinking_tokens` ra để tính tiền (`model_router.py:14–17`). Nội dung reasoning không được đọc ở
bất kỳ đâu. `ThinkingPart`/`ThinkingPartDelta` có sẵn trong thư viện nhưng không được import.

**Thiết kế:** coi thinking steps là **tuỳ chọn có cờ**, không phải nền tảng.

- Timeline **phải dùng được khi không có một thinking step nào** — lúc đó nó là Tool Log +
  Status Indicator, vẫn đủ trả lời "AI đã tra cứu cái gì, đọc cái gì, thử gì hỏng".
- Cờ riêng, tách khỏi cờ bật timeline. Đề xuất hai cờ env-only (cùng nhóm với các cờ ở
  `services/features.py:24–34`): một cờ bật timeline, một cờ bật nội dung reasoning.
  🟡 Tên biến cụ thể để Claude Code đặt theo quy ước sẵn có, không chốt ở đây.

**Ba lý do phải có cờ riêng cho reasoning:**

1. **Chưa biết provider có trả về không.** findings §"Chưa xác định được" mục 1: model được định
   tuyến động qua `model_router.effective_model_pair`, cặp provider/model thật đọc từ env không có
   trong repo. Phải đo trên môi trường thật.
2. **Nội dung reasoning không phải văn bản an toàn cho người dùng cuối.** Nó có thể chứa mảnh
   system prompt, tên tool nội bộ, nguyên văn đoạn tài liệu, hoặc suy đoán sai mà mô hình tự bác bỏ
   sau đó. Với đối tượng là học sinh (quyết định #2), phơi thẳng là rủi ro.
3. **Bật `reasoning_effort` có tác dụng phụ:** `model_settings` **bỏ `temperature`** khi
   `reasoning_effort` được đặt (`model_router.py:254–268`), và canvas phải đi qua
   `OpenAIResponsesModel` mới giữ được pin (`editor_agent.py:1046–1060`). Đụng vào đây là đụng
   chất lượng đầu ra, không chỉ hiển thị.

**Việc phải làm trước khi code phần này:** một thí nghiệm nhỏ — bật log tạm ở
`_aiter_agent_sse_events` in ra `type(event)` và `type(event.part)` của mọi event trên môi trường
thật, xem `ThinkingPart` có xuất hiện không. Kết quả quyết định Pha 3 có tồn tại hay không.

---

## 7. Nếu chọn phương án (a) — thật sự cho agent chạy nhiều bước

Ghi lại ở đây để quyết định #5 có cơ sở, **không** nằm trong phạm vi triển khai bên dưới.

- **Chat ngoài canvas: khả thi.** Có sẵn cặp ngân sách mở rộng
  (`chat_agent_request_limit_expanded=14`, `chat_agent_tool_calls_limit_expanded=12`) và cờ
  `chat_agent_expanded_budget_enabled` (mặc định `False`) — findings §"Biến môi trường".
  Bật cờ là xong về mặt kỹ thuật; chi phí là token và độ trễ.
- **Canvas: không khả thi bằng cách bật cờ.** Ngân sách hardcode 25 vòng
  (`editor_agent.py:1810`), timeout một lượt 240s (`editor_turn_timeout_seconds`), trần trên là
  Caddy 330s. 25 vòng × per-call 120s vượt xa 240s ⇒ agent bị cắt giữa chừng, và với timeline bật
  người dùng sẽ **nhìn thấy** nó bị cắt. Đây là ràng buộc hạ tầng, không sửa bằng code ứng dụng.
- **Hệ quả nghịch lý cần biết trước:** timeline làm cho việc bị cắt trở nên *hiển nhiên*. Hôm nay
  người dùng chỉ thấy một câu xin lỗi; ngày mai họ thấy 18 bước rồi đứt. Đây là lý do mạnh nhất để
  giữ (b) ở vòng đầu.

---

## 8. Phần FE

### 8.1 Component dùng chung

Một component độc lập, nhận đúng một kiểu:

```ts
type TAgentStep = {
  id: string;
  seq: number;
  kind: "thinking" | "tool_call" | "note";
  label: string;
  detail?: string | null;
  tool?: string | null;
  status: "running" | "ok" | "failed";
  at?: string;
};

type TAgentTimeline = {
  v: number;
  steps: TAgentStep[];
  summary?: { retrieved?: number; read?: number; tools?: number; failed?: number; duration_ms?: number };
  truncated?: boolean;
};
```

Nó **không** biết gì về chat, canvas, session hay API. Vào là `TAgentTimeline`, ra là UI.
Đây là cách duy nhất để chi phí FE không nhân đôi thật sự — hai bộ **state** vẫn phải sửa riêng
(findings Q11: ba bộ render, `components/Chat/` là code chết với hai màn này), nhưng phần hiển thị
viết một lần.

### 8.2 Chat ngoài canvas — `use-chat-with-ai.ts`

Hai sửa đổi:

1. **Type** `TChatMessageItem` (`:27–38`) thêm `timeline?: TAgentTimeline | null`.
2. **Callback frame** (`:466–483`) — hiện là:
   ```ts
   if (frame.type === "ask_back") { lastAskBack = ...; return; }
   if (frame.type !== "token") return;     // ← chỗ vứt event
   ```
   Thêm nhánh `step` **trước** dòng `return`, upsert vào `timeline` của message đang `pending`
   (`localAssistantMessageId`), y hệt cách `token` đang nối `content`.
3. **Replay**: `toChatItem` (`:44–54`) đã map `metadata: message.metadata`. Chỉ cần đọc thêm
   `timeline` từ `message.metadata.timeline` — 🟡 hoặc để component tự đọc từ `metadata`, tuỳ
   Claude Code thấy cái nào ít đụng hơn.

Lưu ý một bug tiềm ẩn: sau khi stream xong, `setMessages` (`:497–513`) **thay** message lạc quan
bằng `toChatItem(response.assistant_message)`. Nếu timeline chỉ sống trong message lạc quan mà
không có trong `metadata` trả về, nó sẽ **biến mất ngay khi lượt kết thúc**. Đây chính là lý do
§3.4 (persist vào `metadata`) là bắt buộc chứ không phải "nice to have" — trừ khi quyết định #3
đổi thành "không cần replay", lúc đó FE phải chủ động bê `timeline` từ message lạc quan sang.

### 8.3 Canvas — `document-ai-chat-panel.tsx`

Ba sửa đổi, tất cả đều nhỏ:

1. **`:430`** — `APIStreamEditorAssistant(documentId, payload, () => {})`. Callback rỗng này đang
   vứt **100%** frame. Thay bằng handler xử lý `step` (và bỏ qua phần còn lại như hiện nay).
2. **`:184–200`** — mapping khi nạp phiên cũ hiện chỉ lấy `id, role, content, time, summary,
   content_html, change_set`. **`metadata` bị bỏ ngay tại đây.** Thêm nó vào.
3. 🟡 **`document-ai-chat-message.tsx:20–29`** — `TDocumentAiChatMessage` không có `metadata`,
   không có chỗ cho timeline. Thêm trường và render trong `ChatBubble`. (File chưa upload.)

### 8.4 Vấn đề UX phát sinh: editor bị khoá

`:409–410` gọi `editor.setEditable(false)` + `setEditorAiBusy(editor, true)` suốt lượt chạy.
Hôm nay người dùng chờ trong vô định nên không đo được thời gian. Với timeline bật, họ sẽ **thấy**
mình bị khoá 60–120 giây.

Ba lựa chọn, xếp theo chi phí:

| | Cách | Chi phí | Đánh đổi |
|---|---|---|---|
| a | Giữ khoá, thêm đồng hồ đếm + nút thu gọn | Rất rẻ | Không giải quyết gốc, nhưng biến "treo" thành "đang chạy, còn X giây" |
| b | Giữ khoá, thêm nút **Huỷ** | Trung bình | Đụng bất biến `do not cancel producer` (§5.2) — huỷ ở FE thì server vẫn ghi thay đổi vào tài liệu. Phải làm rõ "huỷ" nghĩa là gì trước khi làm |
| c | Bỏ khoá, cho gõ tiếp trong lúc AI chạy | Đắt | Xung đột `editor_version`: preflight đã chặn version cũ (`api/editor.py:1611–1616`). Đây là dự án riêng |

**Khuyến nghị (a)** ở vòng này. Ghi (b)/(c) vào việc sau.

### 8.5 Hai đường fallback

Cả hai màn đều có nhánh `shouldFallbackToJson` → gọi API non-stream. Component timeline phải coi
`timeline == null | undefined | { steps: [] }` là **không hiện gì**, tuyệt đối không hiện khung
rỗng hay spinner mắc kẹt.

---

## 9. Kế hoạch triển khai

### Pha 0 — Hai việc chặn, làm trước, mỗi việc dưới nửa ngày

| # | Việc | Ra quyết định gì |
|---|---|---|
| 0.1 | Log tạm trong `_aiter_agent_sse_events`: in `type(event)` + `type(event.part)` của **mọi** event trên môi trường thật, một lượt chat có tra cứu | (a) `FunctionToolCallEvent`/`FunctionToolResultEvent` có `tool_call_id` khớp nhau không → §3.2; (b) `ThinkingPart` có xuất hiện không → Pha 3 có tồn tại không |
| 0.2 | Đọc `api/chat.py` quanh `_stream_chat_events` (`:1397`) và `_persist_chat_turn` | Chỗ gom `step` và chỗ nhét vào `metadata` — §3.4 |

### Pha 1 — Chat ngoài canvas (BE + FE)

| Thứ tự | Việc | File |
|---|---|---|
| 1 | Định nghĩa hình dạng `step` + helper build/redact | `chat/` (module mới, dùng chung cho cả hai luồng) |
| 2 | Phát `step` cho tool call/result | `chat/adk_agent.py:1180–1206` |
| 3 | Gom `step` khi chuyển tiếp + ghi vào `metadata` lúc persist | 🟡 `api/chat.py` |
| 4 | Áp trần kích thước §4.5 | module ở bước 1 |
| 5 | Component `SummaryBar` + `ExecutionTimeline` | FE, thư mục mới |
| 6 | Nhánh `step` trong callback + `timeline` trong `TChatMessageItem` | `use-chat-with-ai.ts:27`, `:466` |
| 7 | Render + replay từ `metadata` | 🟡 `templates/HomePage/index.tsx:203–300` |

**Xong Pha 1 là đã có một tính năng dùng được**, không phụ thuộc Pha 2/3.

### Pha 2 — Canvas

| Thứ tự | Việc | File |
|---|---|---|
| 1 | Thêm `emit` (tuỳ chọn) vào chữ ký, truyền xuống | `chat/editor_agent.py:765`, `:1003` |
| 2 | Bọc cảm biến quanh các closure tool | `chat/editor_agent.py:1247–1700` |
| 3 | `step` cho vòng sửa lỗi hình học + `request_limit_hit`/`turn_timeout_hit` | `chat/editor_agent.py:1295–1414`, `:1600–1622`, `:1825–1838` |
| 4 | Cầu threadpool → queue bằng `call_soon_threadsafe` | `api/editor.py:1641–1668` |
| 5 | Nhét timeline vào **mọi** nhánh persist | 🟡 `api/editor.py`, `execute_editor_assistant` |
| 6 | Handler `step` thay callback rỗng; `metadata` khi nạp phiên cũ | `document-ai-chat-panel.tsx:430`, `:184–200` |
| 7 | `timeline` trong type + render | 🟡 `document-ai-chat-message.tsx:20` |
| 8 | Đồng hồ đếm thời gian (§8.4a) | `document-ai-chat-panel.tsx` |

### Pha 3 — Thinking steps (chỉ khi Pha 0.1 cho kết quả dương)

1. Nhánh `ThinkingPart`/`ThinkingPartDelta` trong `_aiter_agent_sse_events`, sau cờ riêng.
2. Gộp delta thành câu hoàn chỉnh trước khi phát (đừng phát từng token reasoning — nhiễu).
3. Quy tắc lọc nội dung reasoning trước khi hiện cho học sinh.
4. Canvas **không** có phần này trừ khi làm §5.2.

### Thứ tự kiểm thử

- Một lượt chat có tra cứu → timeline có step, F5 → vẫn còn.
- Một lượt chạm `UsageLimitExceeded` → có step `failed` cuối, không đứt lặng.
- Một lượt canvas dựng hình sai → thấy chuỗi thử–hỏng–thử lại.
- Ngắt mạng giữa chừng → FE không kẹt spinner; server vẫn ghi xong (bất biến §5.2).
- Ép nhánh fallback non-stream → không có khung timeline rỗng.
- Phiên 50 message → đo kích thước response `GET .../sessions/{id}` trước và sau.

---

## 10. Chỗ vẫn còn là giả định

Xếp theo mức ảnh hưởng tới thiết kế.

| # | Giả định | Sai thì đổi gì | Kiểm chứng bằng |
|---|---|---|---|
| 1 | `FunctionToolCallEvent`/`FunctionToolResultEvent` mang `tool_call_id` khớp nhau | Phải ghép cặp bằng FIFO theo tên tool, chấp nhận lệch khi gọi song song | Pha 0.1 |
| 2 | Provider thật có trả `ThinkingPart` | Pha 3 biến mất; timeline chỉ còn tool + status | Pha 0.1 |
| 3 | `_stream_chat_events` (`api/chat.py:1397`) là nơi chuyển tiếp tuple từ `_aiter_agent_sse_events` và `_persist_chat_turn` chạy sau đó trong cùng luồng | Đổi chỗ gom timeline; có thể phải đổi chữ ký `on_final` | Pha 0.2 — **file chưa upload** |
| 4 | `execute_editor_assistant` có đúng 3 nhánh gọi `_persist_canvas_chat_turn` | Thiếu nhánh ⇒ mất timeline ở đúng lượt lỗi | Đọc `api/editor.py` quanh `:1432–1560` — **đã upload, chưa đọc hết** |
| 5 | `read-sse-stream.ts` bỏ qua event lạ, không ném | Nếu ném ⇒ phải sửa FE trước khi BE phát `step` | findings Q10 đã trích code — **file chưa upload**, độ tin cậy cao |
| 6 | `HomePage/index.tsx:203–300` render inline và có chỗ cắm component | Có thể phải tách component trước | **File chưa upload** |
| 7 | `TDocumentAiChatMessage` cần thêm trường; `ChatBubble` có chỗ cắm | Như trên | **File chưa upload** |
| 8 | Gọi `loop.call_soon_threadsafe` từ threadpool của `run_in_threadpool` là an toàn ở đây | Phải dùng queue thread-safe (`queue.Queue`) + task drain riêng | Thử nghiệm nhỏ ở Pha 2.4 |
| 9 | Nhánh non-stream (`APISendChatMessage`, `/assistant`) không cần timeline | Nếu cần ⇒ phải gom step ở tầng thấp hơn, không phải ở tầng SSE | Quyết định #3 + đọc `api/chat.py` |
| 10 | 60 step / 32 KB là trần hợp lý | Đo p95 sau bản dựng đầu; > 8 KB ⇒ tính chuyện bảng riêng | Sau Pha 1 |

---

## Cần upload thêm

Để gỡ giả định #3, #4, #6, #7 và viết được task doc thi công:

| File | Vùng cần | Gỡ giả định |
|---|---|---|
| `services/api/src/bookforge_api/api/chat.py` | `:1360–1420` (`_stream_chat_events`, `_release_request_session`), `:1660–1700` (`citations`/`ask_back`/`event_log`), `_persist_chat_turn`, `:2640–2720` (`stream_chat_message`) | #3, #9 |
| `bookforge-fe/src/templates/HomePage/index.tsx` | `:180–320` | #6 |
| `bookforge-fe/src/components/TiptapEditor/partial/document-ai-chat-message.tsx` | cả file (ngắn) | #7 |
| `bookforge-fe/src/lib/read-sse-stream.ts` | cả file (ngắn) | #5 |

**Không cần:** `core/settings.py` (findings đã trích đủ), `llm/model_router.py` (findings đã trích
hai đoạn quyết định), `chat/retrieval.py` (đã loại ở §5.3).

**Không đọc được bằng cách upload — phải đo trên môi trường thật:** cặp provider/model của
`LLM_OP_CHAT` và `LLM_OP_EDITOR` (Pha 0.1).
