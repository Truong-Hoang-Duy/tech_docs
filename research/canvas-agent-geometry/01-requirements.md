# 01 — Yêu cầu chức năng & phi chức năng

> Trạng thái: **có 7 câu hỏi mở cần chốt** (§4) trước khi khoá kiến trúc.
> Phần §1–§3 là đề xuất mặc định dựa trên hiện trạng; nếu không có phản hồi khác,
> đây là cái sẽ được triển khai.

## 1. Yêu cầu chức năng

### 1.1 Phạm vi chỉnh sửa — bị mô hình dữ liệu quy định

Như đã phân tích ở `00-current-state-analysis.md` §6, spec là **đồ thị dựng hình có ràng buộc**.
Phạm vi chỉnh sửa vì thế chia thành 3 nhóm rõ rệt:

| Nhóm | Thao tác | Khả thi? | Ghi chú |
|---|---|---|---|
| **A. An toàn ràng buộc** | Kéo điểm **tự do** (`point`) | ✅ Native | JSXGraph tự lan truyền sang mọi object dẫn xuất |
| | Kéo `glider` dọc theo vật chủ | ✅ Native | Bị ràng buộc sẵn |
| | Đổi màu stroke/fill, độ dày, nét đứt, kích thước điểm | ✅ Dễ | Đã có `style{}` trong cả v1 và v2 |
| | Đổi label, ẩn/hiện object (`visible`) | ✅ Dễ | |
| | Sửa tham số vô hướng: `radius`, `ratio`, `angle`, `distance` | ✅ Dễ | Nhập số, không kéo |
| | Đổi bounding box / bật-tắt trục | ✅ Dễ | `view.boundingBox`, `view.showAxes` |
| | Đổi tiêu đề hình | ✅ Dễ | |
| **B. Cần kiểm tra phụ thuộc** | Xoá object | ⚠️ Có điều kiện | Phải chặn nếu còn dependent (BE đã enforce) |
| | Thêm object mới | ⚠️ Cần UI dựng hình | Chọn công cụ → chọn điểm cha → tạo. Không tầm thường |
| **C. Không tương thích mô hình** | "Resize" một hình đa giác/đường tròn dẫn xuất | ❌ | Không có tham số nào để đổi; phải sửa điểm cha |
| | Xoay tự do một shape | ❌ | Không có phép biến đổi affine trên object dẫn xuất |
| | Kéo trực tiếp điểm dẫn xuất (midpoint, intersection…) | ❌ | Vô nghĩa về mặt toán học |
| | Thêm text/annotation tự do | ❌ hiện tại | Không có primitive `text` trong cả v1 lẫn v2 |

**Đề xuất MVP**: toàn bộ nhóm A + xoá có kiểm tra phụ thuộc ở nhóm B. Thêm object mới
đưa sang phase 2. Nhóm C **không làm** — thay vào đó UI phải *giải thích* tại sao
(ví dụ: click vào midpoint → panel hiện "Điểm này phụ thuộc A, B. Sửa A hoặc B để di chuyển.").

### 1.2 Undo/redo

Bắt buộc trong editor. Đề xuất: undo stack cục bộ trong editor (mảng snapshot spec,
giới hạn ~50 bước), **không** dùng ProseMirror history — vì editor chạy trong modal/overlay
riêng và chỉ commit một lần khi Save.

### 1.3 Nơi nhúng

| Surface | Ưu tiên | Ghi chú |
|---|---|---|
| Canvas tài liệu (TiptapEditor node view) | **P0** | Nơi duy nhất hiện có node có thể chỉnh |
| Chat (HomePage + message-item) | **P1** | Vướng câu hỏi mở Q3/Q4 — chat chưa có asset store |
| DocumentDetailPage (ready-document-view) | **P2** | Cùng component với chat, gần như free sau P1 |

### 1.4 Luồng Save

1. Người dùng sửa trong editor → spec mới (client-side).
2. Save → gửi **spec** lên BE.
3. BE **re-verify** (normalize + verifier + kiểm tra suy biến) → từ chối nếu hỏng.
4. BE **render lại ảnh** từ spec đã verify → ghi đè asset, cập nhật `content_hash`,
   `metadata_json`, `bbox_json`.
5. BE trả về `{ asset_url, spec, content_hash, editor_html }`.
6. FE cập nhật node attrs (bust cache của `<img src>` bằng `content_hash`) và đóng editor.

### 1.5 Tương thích ngược

- Hình v1 (`data-type="geometry"`) và v2 (`data-type="jsxgraph"`) **đều phải mở được**.
- Figure `jsxgraph` **không có** `math_figure_spec` trong metadata (tạo bởi đường
  `create_jsxgraph_figure` với source thô) → chỉ có source JS, không có spec.
  **Fallback**: mở ở chế độ chỉ-xem kèm thông báo "Hình này chưa hỗ trợ chỉnh sửa trực quan".
  Tuyệt đối không cố parse ngược JS thành spec.

## 2. Yêu cầu phi chức năng

| Hạng mục | Mục tiêu | Cơ sở |
|---|---|---|
| Số object tối đa | 60 object/hình | Hình hình học phổ thông hiếm khi quá 25; 60 là biên an toàn |
| Kích thước canvas | Mặc định 640×420 (khớp BE); cho phép 320–1280 × 240–960 | `create_geometry_asset(width=640, height=420)` |
| Thời gian mở editor | < 400 ms sau khi có spec | JSXGraph đã được lazy-import ở `board.ts` |
| Độ trễ Save | < 1.5 s p95 | BE chỉ verify + render SVG, không gọi LLM |
| Bundle | Không thêm thư viện canvas mới | JSXGraph 1.12.2 đã có sẵn |
| Không gọi LLM | Save là thao tác thuần deterministic | Không tốn token, không đụng quota |
| i18n | Toàn bộ UI tiếng Việt | Chuẩn chung của sản phẩm |
| Kích thước file | ≤ 300 dòng/file, ≤ 100 dòng/hàm | `frontend/CONVENTION.md` |

### 2.1 Quyền

- Sửa hình = sửa nội dung tài liệu → tái dùng nguyên `DocumentAction.EDIT_CONTENT` +
  `get_document_for_edit` + `_assert_document_editable`. **Không tạo mô hình quyền mới.**
- Tài liệu upload là view-only by design → editor phải ở chế độ chỉ-xem ở đó.
- **Không hỗ trợ multi-user đồng thời** ở phase này (xem Q7).

### 2.2 Bảo mật

- Không mở rộng bề mặt `new Function`. Editor làm việc trên **spec JSON**, không phải JS source.
- Ảnh render ở **server** từ spec đã verify → client không upload được bitmap tuỳ ý.
- Endpoint mới đi qua đúng `observe_document_authorization` như `PUT /editor/jsxgraph/{asset_id}`.

## 3. Định dạng lưu sau Save — đề xuất

**Giữ song song spec (editable) + ảnh render (display)** — đúng như hệ thống đang làm.

Lý do không chuyển sang "chỉ lưu ảnh":
- Agent sẽ **mất khả năng sửa tiếp** hình đó (`apply_geometry_operations` cần `base_spec`).
- Export PDF/DOCX và thumbnail đang đọc SVG asset — vẫn hoạt động bình thường.
- SVG vector giữ nét khi in; PNG sẽ vỡ.

Yêu cầu "chốt lại thành một bức ảnh" **đã được thoả mãn** bởi SVG asset hiện có: nó là ảnh
tĩnh, có URL riêng, được `<img>` tham chiếu, và là thứ mọi consumer không-JS nhìn thấy.
Nếu bắt buộc phải là raster (PNG), xem Q2.

## 4. Câu hỏi mở — cần anh chốt trước khi sang Giai đoạn 2

> Đây là những chỗ mà hai cách hiểu khác nhau sẽ dẫn tới hai khối lượng công việc rất khác nhau.
> Tôi có đề xuất mặc định cho từng câu; nếu anh đồng ý hết thì chỉ cần nói "theo mặc định".

**Q1 — Ý nghĩa của "chốt lại thành một bức ảnh".**
Hiện hình đã luôn có một file ảnh SVG trên server, và HTML tài liệu đã trỏ vào nó bằng `<img>`.
Vậy "Save thành ảnh" nghĩa là:
- (a) *Mặc định đề xuất*: cập nhật đúng file ảnh đó + spec — hình vẫn sửa được về sau; hay
- (b) **Đóng băng**: thay figure bằng một `<img>` trơn, vứt spec, từ đó không sửa được nữa
  (kể cả bằng AI)?

**Q2 — SVG hay PNG?**
Mặc định đề xuất: **giữ SVG** (vector, sắc nét khi in, BE đã render sẵn, không cần dep mới).
Nếu bắt buộc PNG thì cần thêm `resvg`/`cairosvg` ở BE (dep mới + rủi ro font) hoặc
`canvas.toBlob` ở client (mỗi máy render một kiểu, khó nhất quán). Anh có ràng buộc nào
bắt buộc phải là PNG không (ví dụ nơi tiêu thụ ảnh không đọc được SVG)?

**Q3 — Lưu ảnh "vào chat" nghĩa là gì?**
Hiện `chat_messages` **không có** bảng attachment và tin nhắn chat geometry **không gắn với
document nào**, nên không có `DocumentVisualAsset` để cập nhật. Anh muốn:
- (a) *Mặc định đề xuất*: **hoãn chat sang phase sau**, làm xong tài liệu trước; hay
- (b) Ghi đè `preview_html`/`preview_spec` trong `metadata_json` của chính message đó
  (rẻ, nhưng sửa lại lịch sử hội thoại — tin nhắn cũ của AI bị thay đổi); hay
- (c) Tạo **message mới** trong session chứa hình đã sửa (giữ nguyên lịch sử, tốn thêm
  contract cho message do người dùng tạo); hay
- (d) Xây một asset store độc lập với document (việc lớn nhất trong 4 lựa chọn).

**Q4 — Có cần version history cho từng hình không?**
Tài liệu đã có versioning ở mức `editor_documents` (append-only). Nhưng
`update_geometry_asset` **ghi đè tại chỗ** — bản SVG cũ mất vĩnh viễn.
Mặc định đề xuất: **không thêm version history cho asset** ở phase này; lịch sử ở mức
tài liệu là đủ. Anh có cần "khôi phục bản vẽ trước" không?

**Q5 — Sau khi người dùng sửa tay, agent có cần hiểu hình đã sửa không?**
Mặc định đề xuất: **có** — đây chính là lý do phải ghi spec về `metadata_json` chứ không chỉ
đổi attribute (lỗi hiện hữu đã nêu ở `00` §5). Xác nhận giúp tôi rằng "sửa tay rồi vẫn bảo
AI chỉnh tiếp được" là hành vi anh muốn.

**Q6 — Có cần thêm object mới trong editor không (MVP)?**
Thêm object đòi hỏi UI dựng hình (chọn công cụ → chọn các điểm cha → đặt tên), khối lượng
gấp ~2–3 lần so với chỉ sửa cái đang có. Mặc định đề xuất: **MVP không có**, chỉ sửa/xoá
object sẵn có; thêm mới thì bảo AI. Anh thấy MVP như vậy đủ dùng chưa?

**Q7 — Đồng thời nhiều người sửa?**
Mặc định đề xuất: **không**, dùng optimistic locking bằng `content_hash` — nếu ảnh đã bị
người khác đổi thì báo xung đột và bắt tải lại. Có ai đang thực sự dùng chung một tài liệu
cùng lúc không?

## 5. Ngoài phạm vi (đã chốt)

- Hợp nhất hai định dạng v1/v2 thành một — rủi ro cao, đụng agent đang chạy, cần đề án riêng.
- Sửa `data-jsxgraph-source` bằng tay trong UI (tab source đang bị tắt có chủ ý).
- Vẽ tự do / annotation ngoài mô hình hình học (mũi tên, ghi chú, tô highlight).
- Đồ thị hàm số, biểu đồ thống kê — khác nhánh, không dùng GeometrySpec.
