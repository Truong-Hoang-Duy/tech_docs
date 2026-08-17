# Xử lý tài liệu dài — mục lục và đọc theo phần

> **Trạng thái: chưa triển khai — bản đặc tả trước khi code.**
>
> **Cách đọc tài liệu này.** Các quyết định ở mục 5 **đã được chốt**: hãy làm đúng như vậy, đừng thiết kế lại.
> Nếu gặp một quyết định thực sự sai hoặc không làm được, **dừng lại và nêu ra trước khi code**, đừng tự đổi.
> Mục 8 là điều kiện hoàn thành, **bắt buộc**.
>
> Backend chạy được mà frontend **không cần đổi gì**. Việc của frontend nằm ở mục 10, làm ở đợt sau.

Tài liệu này tự đứng độc lập: không cần đọc thêm tài liệu nào khác để hiểu hoặc làm.
Mục 1–3 dành cho người muốn nắm vấn đề và hướng giải quyết; mục 4–11 dành cho người sửa code.

---

## 1. Vấn đề

Người dùng hỏi: *"trích xuất đề của Cụm 3 - Đề tham khảo 1"* trên một cuốn PDF hơn 100 trang.
Assistant trả về Bài 1, 2, 3 rồi dừng, và trình bày như thể đề đã đủ.
Đề thật trải **hai trang**: trang sau còn Bài 4, 5, 6, 7.
Đã thử nhiều đề khác, đều chỉ ra đúng một trang.

Đọc kỹ thì bug không phải "không đọc được hai trang".
Người dùng **không hỏi trang nào cả** — họ hỏi **một phần có tên**.
Agent tự dịch yêu cầu đó sang "trang 15", đọc đúng một trang, rồi dừng.

Trang là **tình cờ của cách trình bày**, không phải đơn vị ý nghĩa.
Nếu chỉ chữa bằng cách cho đọc được nhiều trang hơn thì một đề trải ba trang, hay một đề bắt đầu từ giữa trang, sẽ hỏng lại y như cũ.

**Bug thật: agent không có cách hỏi "cho tôi trọn phần tên là X".**

Bốn biểu hiện đang gặp:

- Một phần trải nhiều trang thì chỉ ra phần nằm ở trang đầu, và được trình bày như đã đủ.
- Cần trang 3 và trang 5 thì phải tốn hai lượt gọi công cụ, hoặc đọc thừa trang 4.
- Sửa tài liệu trong canvas xong hỏi lại thì nhận về nội dung trước khi sửa.
- Nói "sửa trang 12" trong canvas thì không có đường nào đi tới, vì không công cụ nào của editor nhận địa chỉ trang.

Không dùng tìm kiếm ngữ nghĩa để tra trang: thông tin trang trong kết quả tìm kiếm không đủ tin cậy để định vị, và văn bản đã lập chỉ mục không giữ nguyên dấu câu nên không phục vụ được yêu cầu trích nguyên văn.

## 2. Giải pháp — mục lục hai trục

| Phần | Trả lời câu hỏi | Nếu thiếu |
|---|---|---|
| **Mục lục hai trục** | Phần tôi cần nằm ở đâu, tên là gì | Agent dò mù, cạn số lượt gọi công cụ |
| **Đọc theo đơn vị hoặc theo trang** | Lấy trọn phần đó trong một lượt | Đọc thiếu, hoặc tốn lượt cho từng trang |
| **Đầu ra tự nói rõ phạm vi** | Tài liệu dài bao nhiêu, đã đọc tới đâu, còn gì | Trình bày phần thiếu như đã đủ |
| **Sinh Markdown thật lúc lưu** | Nội dung có khớp bản vừa sửa không | Đọc ra nội dung cũ, và tài liệu mất dần cấu trúc |

Điểm mấu chốt: một dòng mục lục mang **cả hai trục** cùng lúc.

```
Trang 15–16 — CỤM 3 - ĐỀ THAM KHẢO 1 — ~950 từ
```

Trục trang là **đơn vị**; trục cấu trúc là **nhãn**.
Các trang liền nhau thuộc cùng một nhãn được gộp thành **một** đơn vị — đây chính là cơ chế làm cho một đề hai trang trở thành một thứ đọc trọn được.
Nhờ vậy agent không cần nhớ đọc tiếp: nó xin một đơn vị và nhận về trọn vẹn.

### 2.1 Bốn hướng đã cân nhắc và không chọn

**Lấy trang làm đơn vị, rồi nhắc agent rằng còn trang phía sau.**
Khớp với lời người dùng khi họ nói "trang 15", và trang là thứ luôn có thật trên sách quét.
Nhưng đơn vị vẫn là trang, nên phần trải nhiều trang chỉ được *nhắc* chứ không được *đảm bảo* — model bỏ qua lời nhắc là bug quay lại.

**Lấy cấu trúc làm đơn vị: đưa nguyên bản đồ tài liệu của editor cho chat dùng.**
Đọc trọn một phần nên bug không thể xảy ra, và tái dùng được code y nguyên.
Nhưng tính đúng của đơn vị khi đó phụ thuộc vào chất lượng heading — xem mục 9, rủi ro đầu tiên.

**Chỉ sửa giá trị mặc định của `read_pages` và vài câu trong prompt.**
Đây là cách nhỏ nhất và dứt được đúng ca đã báo.
Không giải quyết được "phần X nằm ở đâu", không giải quyết được nội dung cũ, không giúp gì cho editor.
**Giữ lại làm bản vá gấp**: nó độc lập với phần còn lại, nên nếu cần chữa nóng trước khi đợt này xong thì đây là thứ nên làm.

**Đưa toàn bộ tài liệu vào ngữ cảnh mỗi lượt.**
Có một lý do từ chối cũ không còn đúng với chat: tài liệu trong chat không đổi giữa các lượt nên dùng lại được.
Nhưng ba lý do khác vẫn đứng: chat chọn được nhiều tài liệu cùng lúc nên đầu vào nhân lên theo số tài liệu; sách hơn 100 trang vẫn quá lớn; và phần giữa của ngữ cảnh dài bị mô hình ghi nhận kém hơn hai đầu.

### 2.2 Ba hướng cho việc nội dung cũ

Khi người dùng sửa tài liệu trong canvas, dữ liệu trang đã lưu không được cập nhật, nên chat đọc lại nội dung trước khi sửa.

| Hướng | Được | Mất |
|---|---|---|
| Ghi lại dữ liệu trang mỗi lần lưu | Đọc rẻ | Có đường ghi, nên ghi sai một lần là **hỏng dữ liệu vĩnh viễn**, phải nạp lại tài liệu mới cứu được |
| Không lưu, đọc thẳng từ bản đang hiển thị | **Không thể cũ được, do cách thiết kế** | Phải dựng lại mô hình khối mỗi lần đọc |
| **Lai: đọc từ bản đang hiển thị, lúc lưu thì sinh Markdown thật** | Đủ cả ba việc, và **bỏ hẳn nhóm rủi ro hỏng dữ liệu** | Vẫn dựng lại mô hình khối mỗi lần đọc |

**Chọn hướng lai.**
Chi phí chuyển HTML sang Markdown là như nhau ở cả ba hướng, chỉ khác **chạy lúc nào**.
Ghi lúc lưu mà sai thì hỏng dữ liệu thật của người dùng; đọc rồi mới chuyển mà sai thì chỉ hỏng một câu trả lời, sửa code là xong.
Với một tính năng chạm vào kho tài liệu đang có, đổi kiểu hỏng như vậy đáng giá.

## 3. Phạm vi

**Trong phạm vi**

- [document_map.py](../../services/api/src/bookforge_api/editor/document_map.py) — chỉ bổ sung, xem 4.2.
- Một module giải trang mới.
- [document_reader.py](../../services/api/src/bookforge_api/chat/document_reader.py), [adk_agent.py](../../services/api/src/bookforge_api/chat/adk_agent.py) — công cụ và prompt của chat.
- [editor_edit_tools.py](../../services/api/src/bookforge_api/chat/editor_edit_tools.py), [editor_agent.py](../../services/api/src/bookforge_api/chat/editor_agent.py) — công cụ và prompt của editor.
- [editor.py](../../services/api/src/bookforge_api/api/editor.py) — đường lưu.
- [settings.py](../../services/api/src/bookforge_api/core/settings.py), test.

**Ngoài phạm vi**

- Tìm kiếm ngữ nghĩa và mọi thứ trong `knowledge/`.
- Frontend — xem mục 10.
- **Nợ đã biết:** `GET /api/documents/{id}/pages` và `excerpt_for_node` vẫn đọc dữ liệu trang cũ. Đợt này không sửa, nhưng ghi ra đây để không ai tưởng đã xong.

---

## 4. Thiết kế

### 4.1 Cấu hình — [settings.py](../../services/api/src/bookforge_api/core/settings.py)

```
chat_read_pages_max_pages        int   15      số trang tối đa một lượt đọc
chat_derived_unit_max_words      int   1500    kích thước một đơn vị suy ra
```

Giá trị 15 lấy theo `chat_read_pages_max_span` sẵn có
([settings.py:187](../../services/api/src/bookforge_api/core/settings.py)) — thực chất là đổi tên nó, vì đơn vị đo đã đổi
từ "độ dài một dải" sang "tổng số trang một lượt", mà `"3,5,15-16"` thì hai thứ đó không còn là một.

**Một hàng rào phải vượt, đừng để bị bất ngờ.**
`test_settings_passthrough_ledger_is_exact` ([test_compose_env_passthrough.py](../../services/api/tests/test_compose_env_passthrough.py)) bắt **mọi** trường trong `Settings` phải chọn một trong hai:
có một dòng tương ứng trong `compose.common.yml`, hoặc được ghi vào danh sách `KNOWN_DEFAULT_ONLY` của chính test đó.
Không làm gì cả thì test đỏ. Với đợt này:

- `chat_read_pages_max_span` hiện nằm trong `KNOWN_DEFAULT_ONLY`; đổi tên nó thì **phải sửa dòng đó trong test**, nếu không cả hai phép kiểm của file đều đỏ (một bên thấy tên lạ, một bên thấy allowlist cũ đã hết đối tượng).
- `chat_derived_unit_max_words` là trường mới → xếp vào `KNOWN_DEFAULT_ONLY`, vì nó là con số tinh chỉnh nội bộ chứ không phải thứ đổi theo từng lần triển khai.

Đây là ngoại lệ duy nhất được phép sửa test cũ trong đợt này, và nó không mâu thuẫn với K4 — K4 nói về test của `document_map`.

### 4.2 Nền chung — phép giải trang

Chỗ dùng chung giữa chat và editor nằm ở **`_page_runs` và `_page_of`** ([document_map.py:146](../../services/api/src/bookforge_api/editor/document_map.py), [:70](../../services/api/src/bookforge_api/editor/document_map.py)), **không phải** ở `build_document_map`.

Hai lý do, phải nắm trước khi code kẻo đấu nhầm tầng:

| Vì sao không dùng `build_document_map` cho chat |
|---|
| **Thứ tự ưu tiên tầng.** Hàm này chọn theo `heading → trang → đoạn đều` ([document_map.py:235](../../services/api/src/bookforge_api/editor/document_map.py)). Tài liệu có heading thì tầng trang không bao giờ chạy, và bản đồ trả về không có số trang nào. Với editor như vậy là đúng — nó cần địa chỉ khối để sửa. Chat cần trang bất kể có heading hay không. |
| **Tầng trang cố ý gộp.** `_sections_by_page` gộp các trang liền nhau thành dải cho tới khi đạt kích thước ([document_map.py:164](../../services/api/src/bookforge_api/editor/document_map.py)), nên ra `Trang 12–18`. Chat cần từng trang để nói "trang 15 có, trang 16 có". |

**Ba thay đổi trong `document_map.py`, đều là bổ sung:**

1. `_page_runs` và `_page_of` chuyển thành hàm dùng chung được.
2. `MapSection` ([document_map.py:49](../../services/api/src/bookforge_api/editor/document_map.py)) thêm trường trang dạng số, không bắt buộc. Hiện số trang chỉ sống trong chuỗi nhãn `Trang 12–18`, nên không nơi gọi nào tách ra dùng được cho tử tế.
3. `build_document_map` báo ra nó đã chạy tầng nào. Hiện nó chọn ngầm, nên nơi gọi không biết mình đang cầm trang thật hay đoạn suy ra.

**Không được đụng:** thứ tự ưu tiên tầng · logic gộp và chia · `_MIN_MAP_SECTIONS` ([document_map.py:45](../../services/api/src/bookforge_api/editor/document_map.py)) · định dạng nhãn · và bốn trường mà gói ngữ cảnh đang đọc là `first_index`, `last_index`, `word_count`, `label` ([focus_envelope.py:113-127](../../services/api/src/bookforge_api/editor/focus_envelope.py)).

Điều kiện của bước này: **các test sẵn có của `document_map` phải xanh mà không sửa dòng nào.** Phải sửa test cũ nghĩa là đã đụng quá tay.

**Thứ tự nguồn dữ liệu khi đọc:**

1. Bản HTML đang hiển thị của tài liệu (`EditorDocument.content_html`).
2. Dữ liệu trang đã lưu (`pages.jsonl`).
3. Markdown của cả tài liệu (`document.md`).

Vì khâu nạp tài liệu cũng tạo ra bản HTML này ([pipeline.py:952](../../services/api/src/bookforge_api/ingest/pipeline.py), `:961`, `:1281`, `:1290`), đường số một là đường chính cho mọi loại tài liệu; hai đường sau chỉ là lưới an toàn cho ca G ở Bảng 2.

### 4.3 Mục lục hai trục

`get_document_map(document_id)` trả về danh sách đơn vị. Không chứa nội dung.

Mỗi đơn vị mang hai trục:

- **Trục trang** — số trang, lấy từ `_page_runs`. Đây là **đơn vị**, và nó đúng bất kể heading tốt hay xấu.
- **Trục cấu trúc** — nhãn, ghép từ các heading rơi vào khoảng trang đó. Nhãn xấu chỉ làm khó tra cứu, **không làm đọc sai**.

Kèm theo: loại đơn vị (`page` khi lấy từ trang thật, `section` khi suy ra), tổng số đơn vị, tổng số từ.

**Cách gộp:** các trang liền nhau thuộc cùng một nhãn gộp thành một đơn vị.
Đây là chỗ đề hai trang trở thành một đơn vị đọc trọn được, nên phải có test riêng (mục 8.3).

### 4.4 Đọc

Hai đường, phục vụ hai kiểu yêu cầu khác nhau:

- **Đọc theo đơn vị của mục lục** — đường chính. Trả trọn đơn vị, kể cả khi trải nhiều trang.
- **`read_pages(document_id, pages)`** — cho ca người dùng nói trang cụ thể. `pages` là chuỗi: `"15-16"`, `"3,5"`, `"3,5,15-16"`. Thay cho chữ ký cũ `(document_id, start_page, end_page)` ([document_reader.py:133](../../services/api/src/bookforge_api/chat/document_reader.py)).

Một tham số chuỗi thay vì hai tham số số, vì nó diễn đạt được cả trang rời lẫn dải trong một chỗ, và mô tả công cụ đưa cho mô hình phải ngắn.

Áp đủ Bảng 3.

### 4.5 Sinh Markdown thật lúc lưu

Hôm nay frontend gửi lên một chuỗi text phẳng ở trường Markdown, và server nhận sao lưu vậy ([editor.py:1108](../../services/api/src/bookforge_api/api/editor.py)).
Heading, danh sách, bảng, công thức mất hết.
Đường tạo tài liệu trong canvas thì làm đúng ([chat_document.py:186-212](../../services/api/src/bookforge_api/services/chat_document.py)) — đây là hình mẫu để tách ra dùng chung.

Gọi hàm dùng chung đó trong khối `try/except` sẵn có ở [editor.py:1112-1120](../../services/api/src/bookforge_api/api/editor.py), ghi `content_markdown` và `document.md`.

**Không đụng** `pages.jsonl`, `page_count`, `extracted_page_count`, `grounded_text_ready`, và các dòng tài sản hình ảnh.

Lưu ý quan trọng: đây là **bộ duyệt thứ năm** của cấu trúc tài liệu trong editor.
Bốn bộ trước là bản in PDF, bản dựng DOCX, bản chiếu Markdown cho agent, và bộ dựng ảnh thu nhỏ.
Mỗi bộ đều âm thầm bỏ qua loại nút nào nó không có luật xử lý, nên backend giữ một bộ kiểm bằng `tests/fixtures/full_schema_document.html` và `tests/test_editor_schema_roundtrip.py`.
Bộ mới phải vào cùng kỷ luật đó, và **fixture cần bổ sung ca nhiều trang** — hiện nó chỉ có một `data-page`.

### 4.6 Editor — địa chỉ trang trong công cụ

Hôm nay không công cụ nào của editor nhận địa chỉ trang: `get_outline`, `read_blocks`, `search_document` đều chỉ dùng địa chỉ khối ([editor_edit_tools.py:79](../../services/api/src/bookforge_api/chat/editor_edit_tools.py), `:103`, `:132`).
Người dùng nói "sửa trang 12" thì không có đường nào đi tới.

Dùng đúng nền ở 4.2 nên gần như không thêm logic mới:

- `get_outline` trả thêm khoảng trang cho mỗi đề mục.
- `read_blocks` nhận thêm cách chỉ định phạm vi theo trang.

**Địa chỉ khối vẫn là cách sửa duy nhất.**
Trang chỉ là cách **tìm tới** nội dung, không thay thế địa chỉ khối ở bất kỳ thao tác sửa nào.

### 4.7 Editor — hai lỗi trong gói ngữ cảnh

Hai lỗi này đang xảy ra thật ở môi trường dev, vì [`.env:78`](../../services/api/.env) có `BOOKFORGE_EDITOR_FOCUS_ENVELOPE_ENABLED=true`:

1. **Chỉ thị sửa toàn tài liệu đang vô điều kiện.** [editor_agent.py:885-888](../../services/api/src/bookforge_api/chat/editor_agent.py) bảo agent *"edit every block that needs it and finish the job"*, và câu này có mặt cả ở chế độ gói ngữ cảnh — nơi dòng SCOPE vừa nói với agent rằng nó chỉ thấy một phần tài liệu. Hai câu chống nhau. Phải cho câu này chỉ xuất hiện ở chế độ thấy toàn bộ.
2. **Số lần gọi công cụ đang không có giới hạn** cho lượt không phải vẽ hình — `tool_calls_limit = 4 if geometry_request else None` ([editor_agent.py:1690](../../services/api/src/bookforge_api/chat/editor_agent.py)). Mỗi lần `read_blocks` tốn tới 14.000 ký tự, nên một lượt lạc đường có thể đốt rất nhiều token trước khi `request_limit=25` chặn lại.

Ở nhánh còn lại, tài liệu trên khoảng 2.000 từ đi đường cũ, `read_blocks` cắt ở 14.000 ký tự, và **agent không nhận được nội dung nào cả** ([editor_agent.py:960-973](../../services/api/src/bookforge_api/chat/editor_agent.py)).
Cả hai nhánh đều hỏng, chỉ khác kiểu — đó là lý do 4.7 nằm trong phạm vi.

### 4.8 Đầu ra tự nói rõ phạm vi

Mỗi lần đọc trả kèm:

- Loại đơn vị đang dùng.
- Tổng số đơn vị của tài liệu.
- Đã trả về những đơn vị nào.
- Còn đơn vị ở phía trước hoặc phía sau không.
- Nếu đơn vị cuối trả về chưa hết một phần thì nói rõ phần đó còn tiếp.

### 4.9 Quy tắc an toàn

1. **Không gọi đơn vị suy ra là "trang".** Gán số thứ tự thành số trang chính là loại lỗi tài liệu này đang đi sửa.
2. **Nguồn dẫn ghi theo phần thực trả, không theo phần được yêu cầu.** Hiện `read_pages` ghi theo phần yêu cầu ([document_reader.py:169](../../services/api/src/bookforge_api/chat/document_reader.py)), và `read_document` cắt ở 6.000 từ nhưng vẫn ghi nguồn là toàn bộ số trang ([document_reader.py:179](../../services/api/src/bookforge_api/chat/document_reader.py)).
3. **Đọc một phần không được trình bày như toàn bộ.** Khi hết số lượt gọi công cụ, prompt tổng hợp hiện nói với mô hình rằng *"Bạn đã thu thập đủ thông tin"* ([adk_agent.py:498](../../services/api/src/bookforge_api/chat/adk_agent.py)) — tức là bảo nó tự tin đúng lúc nó vừa bị cắt ngang. Phải sửa.
4. **Ghi file lúc lưu luôn nằm trong `try/except`.** Hỏng thì ghi log, không bao giờ làm hỏng thao tác lưu của người dùng.
5. **Trang để tìm, khối để sửa.** Mọi thao tác sửa vẫn đi qua địa chỉ khối.

---

## 5. Các quyết định đã chốt

| | Quyết định | Lý do |
|---|---|---|
| K1 | **Mục lục hai trục**: trang làm đơn vị, cấu trúc làm nhãn | Đơn vị đúng bất kể heading tốt xấu; nhãn nhiễu không làm đọc sai |
| K2 | Đọc theo đơn vị là **đường chính**; đọc theo trang giữ cho ca người dùng nói trang cụ thể | Trả trọn phần thì bug không thể xảy ra, thay vì bị khuyên đừng xảy ra |
| K3 | Chỗ dùng chung là `_page_runs` và `_page_of`, **không phải** `build_document_map` | Bản đồ đó ưu tiên heading hơn trang và gộp trang thành dải — đúng cho editor, sai cho chat |
| K4 | Sửa `document_map.py` **chỉ bằng cách bổ sung**; test cũ phải xanh không sửa | Giữ hành vi gói ngữ cảnh không đổi một chút nào |
| K5 | Đọc từ bản HTML đang hiển thị; lúc lưu sinh Markdown thật; **không ghi lại `pages.jsonl`** | Đổi kiểu hỏng từ mất dữ liệu sang trả lời sai một lần |
| K6 | **Không đụng** `page_count`, `extracted_page_count`, `grounded_text_ready`, dòng tài sản hình ảnh | Bộ ảnh trang nối theo `page_count` và kiểm tra đủ file trước khi hiển thị; lệch một số là mất cả bộ ảnh ([document_runtime.py:53-69](../../services/api/src/bookforge_api/services/document_runtime.py)) |
| K7 | Một `<section data-page="1">` duy nhất mà tài liệu có nhiều hơn một trang thì **không** coi là trang thật | Frontend tự bọc như vậy cho tài liệu vốn không có phân trang — Bảng 2 ca B |
| K8 | Không khối nào mang thông tin trang thì dùng đơn vị suy ra, **không mặc định là trang 1** | Bịa trang là loại lỗi đang đi sửa |
| K9 | Trang không thay thế địa chỉ khối ở thao tác sửa | Địa chỉ khối là hợp đồng đã ổn định, không đụng vào |
| K10 | Sửa **cả hai nhánh** của gói ngữ cảnh ở 4.7 | Nhánh bật đang chạy ở dev và có hai câu chỉ thị chống nhau; nhánh còn lại thì agent không nhận được nội dung nào |
| K11 | Bộ sinh Markdown vào cùng kỷ luật fixture; fixture thêm ca nhiều trang | Bốn bộ duyệt trước đã từng âm thầm làm mất nút |
| K12 | Sinh Markdown chạy **đồng bộ ngay trong route lưu**, không đẩy sang hàng đợi | Đường hàng đợi bị tắt khi tính năng tri thức tắt, khi đó nội dung sẽ không bao giờ được làm mới |
| K13 | Server **bỏ qua** trường Markdown frontend gửi lên, và **không đổi schema** trong đợt này | Backend chạy được mà frontend không đổi gì; hai bên tách rời |
| K14 | **Không đụng đường tìm kiếm ngữ nghĩa** | `ScopedKnowledgeRetrievalTool` có bản giả ở **5 file test**; đụng vào là phải chạy toàn bộ bộ test |

---

## 6. Thứ tự làm

Bốn bước, mỗi bước có điều kiện riêng.
Dừng lại ở bước nào cũng không để hệ thống ở trạng thái dở dang.

**Mỗi bước một commit riêng, và không gộp** — ranh giới commit chính là đơn vị quay lui.

1. **Nền chung** (4.2) — không đổi hành vi nhìn thấy được từ bên ngoài. Điều kiện: test `document_map` xanh không sửa dòng nào.
2. **Chat** (4.3, 4.4, 4.5, 4.8) — **bước dứt bug đã báo**. Điều kiện: 8.6 chạy thật ra đủ Bài 1 đến 7.
3. **Editor: địa chỉ trang** (4.6) — điều kiện: "sửa trang 12" có đường đi.
4. **Editor: hai lỗi gói ngữ cảnh** (4.7) — điều kiện: hai câu chỉ thị không còn chống nhau, và lượt không vẽ hình có giới hạn số lần gọi công cụ.

## 7. Số lượt gọi công cụ

Chat có 7 lượt gọi mô hình và 5 lượt gọi công cụ mỗi tin nhắn ([settings.py:181-182](../../services/api/src/bookforge_api/core/settings.py)).
Mục lục tốn 1 lượt, đọc tốn 1 đến 2 lượt.

Thêm loại đơn vị và tổng số đơn vị vào danh sách tài liệu trong system prompt ([adk_agent.py:897](../../services/api/src/bookforge_api/chat/adk_agent.py) hiện đã in số trang) để những ca đơn giản bỏ được lượt gọi mục lục.

Nếu đo thấy vẫn hết lượt thì nâng số lượt chỉ là sửa một dòng — nhưng **đo trước đã**.

---

## 8. Nghiệm thu

### 8.1 Cổng tự động

- [ ] `uv run --directory services/api ruff check .` đạt.
- [ ] `uv run --directory services/api ruff format --check .` báo toàn bộ file đã format.
- [ ] `uv run --directory services/api pytest` đạt.
- [ ] Các test của `document_map` xanh **mà không sửa dòng nào**.
- [ ] 17 test trong `test_document_reader.py` đã cập nhật theo chữ ký mới của `read_pages`.
- [ ] `test_compose_env_passthrough.py` xanh: `KNOWN_DEFAULT_ONLY` đã theo kịp việc đổi tên `chat_read_pages_max_span` và trường mới `chat_derived_unit_max_words` (4.1).
- [ ] `grep` toàn kho không còn `chat_read_pages_max_span` sót lại — kể cả trong `compose.common.yml` và các file `.env`.

### 8.2 Nền chung

Đủ 7 ca ở Bảng 2 và 8 loại nguồn ở Bảng 1.

- [ ] Ca A — nhiều `<section data-page>`: nhóm đúng theo trang.
- [ ] **Ca B** — đúng một `<section data-page="1">` bọc cả tài liệu trong khi tài liệu nhiều trang: chuyển sang đơn vị suy ra, **không** nhận là trang thật. Đây là ca dễ sai nhất, phải có test riêng.
- [ ] Ca C — không có `<section>` nào: đơn vị suy ra.
- [ ] Ca D — đoạn trống cuối tài liệu nằm ngoài mọi `<section>`: bỏ qua, không tạo ra một trang rỗng.
- [ ] Ca E — khối có nội dung thật nằm ngoài mọi `<section>`: gán vào trang gần nhất phía trước.
- [ ] Ca F — một `<section>` rơi mất `data-page`: không đoán, lùi về dữ liệu trang đã lưu.
- [ ] Ca G — không có bản HTML đang hiển thị: lùi về dữ liệu trang đã lưu, rồi Markdown cả tài liệu.
- [ ] Tài liệu PPTX: không bị xử lý sai, và không có trường nào bị mất.

### 8.3 Mục lục hai trục

- [ ] Một nhãn trải hai trang liền nhau gộp thành **một** đơn vị. Đây là ca gốc.
- [ ] Tài liệu không có heading: vẫn ra đơn vị theo trang, nhãn để trống hoặc lấy dòng đầu.
- [ ] Tài liệu không có trang thật: ra đơn vị suy ra, và **nhãn không chứa chữ "trang"**.
- [ ] Mục lục không chứa nội dung tài liệu, chỉ chứa nhãn, khoảng trang và số từ.

### 8.4 Đọc

Đủ 8 ca ở Bảng 3.

- [ ] Đọc theo tên phần trong mục lục: trả **trọn** phần đó, kể cả trải nhiều trang.
- [ ] `"15-16"` trả đủ hai trang.
- [ ] `"3,5"` trả đúng trang 3 và 5, **không** có trang 4.
- [ ] Yêu cầu vượt quá trang cuối: trả phần có, và nói rõ trang cuối là bao nhiêu.
- [ ] Dải chỉ tồn tại một phần: trả phần có, nói rõ thiếu trang nào.
- [ ] Vượt số trang tối đa một lượt: cắt, và nói rõ đã cắt tới đâu.
- [ ] Trang tồn tại nhưng rỗng: trả rỗng kèm ghi chú, không im lặng.
- [ ] Nguồn dẫn khớp phần **thực trả**, kể cả khi yêu cầu vượt quá cuối tài liệu.
- [ ] `read_document` trên tài liệu lớn không ghi nguồn là toàn bộ số trang.
- [ ] Prompt tổng hợp không còn khẳng định đã thu thập đủ thông tin.

### 8.5 Sinh Markdown lúc lưu

- [ ] Sau khi lưu, `content_markdown` và `document.md` giữ được heading, danh sách, bảng và công thức.
- [ ] Fixture nhiều trang đi qua vòng tròn không mất loại nút nào.
- [ ] `pages.jsonl`, `page_count` và bộ ảnh trang **không đổi**.
- [ ] Ghi file hỏng: thao tác lưu vẫn thành công, và có dòng log.

### 8.6 Chạy thật

- [ ] **Ca gốc**: hỏi *"trích xuất đề của Cụm 3 - Đề tham khảo 1"* trả về **đủ Bài 1 đến 7**, dấu câu nguyên vẹn, đối chiếu trực tiếp với ảnh trang gốc.
- [ ] **In mục lục của cuốn sách ra xem nhãn có dùng được không.** Đây là phép đo cho rủi ro đầu tiên ở mục 9. Nhãn xấu vẫn đạt, miễn là đơn vị đúng — nhưng phải ghi lại kết quả.
- [ ] Một ca đọc trang rời.
- [ ] Một ca sửa tài liệu rồi hỏi lại, phải ra nội dung mới.
- [ ] Một ca trên tài liệu soạn trong canvas, dài.
- [ ] Một ca "sửa trang N" trong editor.
- [ ] Ghi lại: số lượt gọi công cụ, có hết lượt không, token vào và ra, thời gian đọc trên tài liệu khoảng 95 trang.

### 8.7 Còn lại, không thuộc đợt này

- [ ] Các nhóm nghiệm thu A–F cho gói ngữ cảnh của editor ([tài liệu 2026-08-03](2026-08-03-editor-focus-envelope.md) §7.5).

---

## 9. Rủi ro cần theo dõi

| Rủi ro | Mức | Xử lý |
|---|---|---|
| **Nhãn từ heading bị nhiễu trên sách quét** | Cao | Bộ dò heading theo quy tắc chuỗi ([markdown.py:16](../../services/api/src/bookforge_api/ingest/markdown.py)) coi mọi dòng chữ hoa ngắn là đề mục. Trên chính cuốn sách này, phần đầu mỗi trang có "HỘI ĐỒNG BỘ MÔN TOÁN TP. HỒ CHÍ MINH", "SỞ GIÁO DỤC VÀ ĐÀO TẠO", "MÔN THI: TOÁN" — đều thành đề mục, lặp lại hơn 100 lần. Ngược lại "Bài 1. Cho parabol…" **không** thành đề mục vì quá dài. Đây chính là lý do thiết kế đặt heading ở chỗ chỉ ảnh hưởng nhãn. Đo ở 8.6. Nếu hoá ra nhãn tốt thì nâng nó lên thành đơn vị là việc nhỏ về sau. |
| **Ca B ở Bảng 2 bị nhận nhầm** | Cao | Nhận nhầm một tài liệu nhiều trang thành một trang duy nhất sẽ làm hỏng toàn bộ việc điều hướng mà không báo lỗi. Phải có test riêng, 8.2. |
| Bổ sung `document_map` làm lệch gói ngữ cảnh | Trung bình | Chỉ bổ sung, không sửa. Test cũ phải xanh **không sửa dòng nào** — đó là hàng rào. |
| Bộ duyệt thứ năm bỏ sót loại nút mới | Trung bình | Vào cùng kỷ luật fixture, 8.5. |
| Mô hình không tuân thủ chỉ dẫn về phạm vi | Trung bình | Mô hình ngôn ngữ không đảm bảo tuân thủ chỉ dẫn dạng bắt buộc. Vì vậy 8.4 và 8.6 phải đo bằng chạy thật, không dựa vào prompt. |
| Sửa thẳng nên hỏng là chạm ngay người dùng | Trung bình | Bù bằng khuôn fail-safe sẵn có: không dựng được đơn vị thì trả rỗng và lùi về hành vi cũ, như `build_document_map` đang làm ([document_map.py:254-259](../../services/api/src/bookforge_api/editor/document_map.py)). Thang nguồn dữ liệu ở 4.2 cũng là đường lùi cho việc đọc. |
| Markdown sinh lại khác bản gốc lúc nạp | Trung bình | Khác về khoảng trắng và cấp đề mục kể cả khi người dùng không sửa gì, nên lần lưu đầu tiên luôn tạo ra thay đổi thật. Đúng như dự kiến, ghi vào mô tả commit. |
| Thời gian đọc tăng trên tài liệu rất dài | Trung bình | Đã đo trước đây: 3.846 khối và gần 50.000 từ dựng mô hình khối trong 85 ms. Đo lại ở 8.6. |
| Đổi chữ ký `read_pages` làm hỏng test sẵn có | Thấp | 17 test trong `test_document_reader.py`, đã tính vào 8.1. |
| Chi phí token tăng | Thấp | Tiếng Việt tốn token hơn tiếng Anh trên cùng số ký tự, nên phải **đo** chứ không suy từ số ký tự. Ghi ở 8.6. |

---

## 10. Việc cho frontend, làm sau

**Backend chạy được mà frontend không cần đổi gì** — server bỏ qua trường Markdown gửi lên và không đổi schema trong đợt này (K13).
Tài liệu báo cáo riêng cho frontend viết sau khi backend xong.

Ba việc dọn dẹp, không gấp:

- Bỏ trường Markdown khỏi dữ liệu gửi lên lúc lưu; hàm chuyển HTML sang text phẳng khi đó thành code chết.
- Tách một kiểu riêng cho dữ liệu gửi lên. Hiện kiểu dùng chung cho cả gửi lên và nhận về, nên bỏ trường sẽ làm bước kiểm kiểu đỏ.
- Cập nhật bản chụp OpenAPI bằng tay, không có công cụ sinh tự động.

**Một hợp đồng phải giữ.**
Đây là thứ backend **phụ thuộc vào**, không phải lời nhờ.
Backend xác định trang bằng `<section data-page="N">` trong HTML.
Hôm nay frontend giữ đúng nhờ có một loại nút riêng cho trang trong trình soạn thảo, và có bản chụp đối chiếu đã lưu chứng minh điều đó.
Nếu sau này thuộc tính này bị bỏ thì việc đọc theo trang hỏng âm thầm.
Ca F ở Bảng 2 là lưới an toàn phía backend cho tình huống đó.

---

## 11. Phụ lục — ba bảng trường hợp

Ba bảng này là phần nền để dựa vào lúc code. Mỗi ô có một hành vi xác định.

### Bảng 1 — nguồn gốc tài liệu

| Loại tài liệu | `data-page` trong HTML | `page_count` | Đơn vị |
|---|---|---|---|
| PDF tải lên, có sẵn text | nhiều `<section>` | đúng | Trang thật |
| PDF tải lên, qua nhận dạng ảnh | nhiều `<section>` | đúng | Trang thật |
| DOCX hoặc ảnh tải lên | nhiều `<section>` | đúng | Trang thật |
| PPTX tải lên | `class="pptx-slide" data-page` | số slide | Trang thật |
| Soạn trong canvas, dạng markdown | chỉ `data-page="1"` | 1 | Suy ra |
| Soạn trong canvas, dạng HTML | có thể không có | 1 | Suy ra |
| Hình vẽ hình học | không có | 1 | Suy ra |
| Nhập hàng loạt từ markdown | không có | theo nơi gọi | Suy ra |

### Bảng 2 — hình dạng HTML lúc đọc

| Ca | Mô tả | Xử lý |
|---|---|---|
| A | Nhiều `<section data-page="N">` | Nhóm theo `data-page`. Ca chuẩn. |
| B | Đúng một `<section data-page="1">` bọc cả tài liệu | **Ca dễ sai nhất.** Frontend tự bọc như vậy cho tài liệu vốn không có phân trang. Nếu tài liệu có nhiều hơn một trang thì đây **không** phải trang thật → chuyển sang đơn vị suy ra. |
| C | Không có `<section>` nào | Đơn vị suy ra. |
| D | Đoạn trống nằm ngoài mọi `<section>` | Bỏ qua. Đây là chỗ đặt con trỏ, không phải nội dung. |
| E | Khối có nội dung thật nằm ngoài mọi `<section>` | Gán vào trang gần nhất phía trước. |
| F | Một `<section>` rơi mất `data-page` | Không đoán. Trang đó lùi về dữ liệu trang đã lưu. |
| G | Không có bản HTML đang hiển thị | Lùi về dữ liệu trang đã lưu, rồi Markdown cả tài liệu. |

### Bảng 3 — yêu cầu đọc

| Ca | Xử lý |
|---|---|
| Đọc theo tên phần trong mục lục | Trả **trọn** phần đó, kể cả khi trải nhiều trang |
| Trang tồn tại | Trả nội dung |
| Trang vượt quá trang cuối | Trả phần có, và nói rõ trang cuối là bao nhiêu |
| Dải chỉ tồn tại một phần | Trả phần có, và nói rõ thiếu trang nào |
| Trang rời có khoảng trống, ví dụ `"3,5"` | Trả đúng trang 3 và 5, **không** trả trang 4 |
| Vượt số trang tối đa một lượt | Cắt, và nói rõ đã cắt tới đâu |
| Tài liệu không có trang thật | Trả đơn vị suy ra, và ghi rõ loại đơn vị |
| Trang tồn tại nhưng rỗng | Trả rỗng kèm ghi chú, không im lặng |

---

## 12. File

| File | Việc |
|---|---|
| [editor/document_map.py](../../services/api/src/bookforge_api/editor/document_map.py) | Sửa — chỉ bổ sung, xem 4.2 |
| `editor/page_units.py` | Thêm mới — phép giải trang và mục lục hai trục |
| [chat/document_reader.py](../../services/api/src/bookforge_api/chat/document_reader.py) | Sửa — `read_pages`, `read_document`, nguồn dẫn |
| [chat/adk_agent.py](../../services/api/src/bookforge_api/chat/adk_agent.py) | Sửa — đăng ký công cụ, prompt, prompt tổng hợp |
| [chat/editor_edit_tools.py](../../services/api/src/bookforge_api/chat/editor_edit_tools.py) | Sửa — `get_outline`, `read_blocks` nhận địa chỉ trang |
| [chat/editor_agent.py](../../services/api/src/bookforge_api/chat/editor_agent.py) | Sửa — chỉ thị sửa toàn tài liệu, giới hạn số lần gọi công cụ |
| [api/editor.py](../../services/api/src/bookforge_api/api/editor.py) | Sửa — sinh Markdown lúc lưu |
| [core/settings.py](../../services/api/src/bookforge_api/core/settings.py) | Sửa — hai con số ở 4.1, **không thêm cờ nào** |
| `tests/fixtures/full_schema_document.html` | Sửa — thêm ca nhiều trang |
| `tests/test_page_units.py` | Thêm mới — Bảng 1, Bảng 2, mục lục hai trục |
| `tests/test_document_reader.py` | Sửa — chữ ký mới, Bảng 3 |
| `tests/test_editor_schema_roundtrip.py` | Sửa — bộ duyệt thứ năm |
| `tests/test_editor_edit_tools.py` | Sửa — địa chỉ trang |
