# 00 — Phân tích hiện trạng: Canvas Agent & hình học 2D

> Phạm vi đọc: `backend/services/api/src/bookforge_api/{api,chat,services}` và
> `frontend/src/{components,templates,api}`. Trạng thái tại 2026-08-29.

## 1. Tóm tắt điều hành

Hệ thống **không có một** cơ chế vẽ hình 2D, mà có **hai stack song song** cùng tồn tại,
sinh ra hai định dạng dữ liệu khác nhau, hai node Tiptap khác nhau, và hai đường lưu trữ
khác nhau. Bất kỳ mini-editor nào cũng phải xử lý cả hai, hoặc phải chọn rõ một và có
fallback hợp lý cho cái còn lại.

Điểm mấu chốt về kiến trúc: **geometry ở đây là một đồ thị dựng hình có ràng buộc
(dependency-tracked construction graph), không phải danh sách shape phẳng.** Chỉ `point`
(tự do) và `glider` mang toạ độ của riêng chúng; mọi đối tượng khác là dẫn xuất
(midpoint, intersection, projection, circumcircle…). Điều này quyết định phạm vi khả thi
của việc "chỉnh sửa trực tiếp" — xem §6.

## 2. Hai stack geometry

| | **v1 — "geometry"** | **v2 — "jsxgraph"** |
|---|---|---|
| Module BE | `services/geometry/` | `services/jsxgraph/` |
| Tool của agent | `draw_geometry(description)` — LLM sinh cả spec | `apply_geometry_operations(operations, assertions)` — LLM phát ops tường minh |
| Vị thế | Đường cũ, vẫn hoạt động | **Đường chính** (system prompt ưu tiên) |
| Hình dạng spec | `objects[].args{}` lồng nhau | Trường phẳng ngay trên object |
| Tài liệu | `backend/docs/GEOMETRY_SPEC.md` | Không có doc riêng; đọc `geometry_spec.py` |
| `DocumentVisualAsset.source` | `'geometry'` | `'jsxgraph'` (hoặc `'math_svg'`) |
| Khoá metadata chứa spec | `metadata_json.geometry_spec` | `metadata_json.math_figure_spec` |
| HTML trong tài liệu | `<figure data-type="geometry" data-geometry-asset-id=…>` + `<img>` | `<figure data-type="jsxgraph" data-jsxgraph-source="…JS…">` + `<img>` |
| Node Tiptap | `GeometryFigure` (`geometry-figure-extension.ts`) | `JsxGraphNode` (`jsxgraph-extension.tsx`) |
| Cách render FE | Fetch spec qua API → dựng board bằng `geometry/registry.ts` | `new Function("board", source)` — **thực thi JS lấy từ HTML** |
| API đọc | `GET /editor/geometry/{asset_id}` | Không có (source nằm inline trong HTML) |
| API ghi | **Không có** | `PUT /editor/jsxgraph/{asset_id}` — **FE chưa từng gọi** |

### 2.1 Chi tiết v1 (`services/geometry/`)

- `registry.py` (1130 dòng) — nguồn sự thật duy nhất: mỗi primitive mang theo `evaluate`
  (bộ đánh giá số học) hoặc `expand` (khai triển composite phía server).
- `normalize.py` — validate id/args/style, khai triển composite, kiểm tra kiểu tham chiếu,
  **topological sort**, phát hiện chu trình.
- `verifier.py` — chạy `evaluate` theo thứ tự topo, thu `GeometryValues`
  (`points`/`lines`/`circles`), tự tính `boundingBox` nếu thiếu.
- `svg.py` — render SVG tĩnh từ giá trị đã verify. Chiếu **letterboxed uniform scale**
  (`min(width/…, height/…)`) để giữ đúng hình dạng, khớp `keepAspectRatio` của board FE.
- `assets.py` — `create_geometry_asset` / `update_geometry_asset`: ghi SVG vào
  `LocalStorage` tại key `{workspace_key}/editor/assets/geometry/{uuid}.svg`, tạo/cập nhật
  row `DocumentVisualAsset`, nhét spec đã chuẩn hoá vào `metadata_json`.
- Composite (`triangle`, `square`, `rectangle`, `triangle_sss`, `tangent_from_point`…)
  **được khai triển ở server** thành base primitive trước khi lưu → FE chỉ thấy 26 base type.

### 2.2 Chi tiết v2 (`services/jsxgraph/`)

- `geometry_spec.py` (975 dòng) — `normalize_geometry_spec_v2`, `_validate_concrete_geometry`
  (kiểm tra suy biến bằng số học), `compile_geometry_spec_v2` → **sinh chuỗi JS JSXGraph**.
- `geometry_pipeline.py` — `apply_geometry_operations(base_spec, operations)` với 3 op:
  `upsert_object`, `remove_object`, `set_view`; `plan_geometry_operations` (validate,
  read-only); `verify_rendered_geometry` (đối chiếu spec đã plan với spec renderer trả về,
  và kiểm tra mọi object đều có `const {id} =` trong source).
- `service.py` — `create_jsxgraph_asset` / `update_jsxgraph_asset` / `render_jsxgraph_fallback`,
  `editor_html_for_jsxgraph_asset`.
- 21 type được hỗ trợ (`_SUPPORTED_TYPES`), **không trùng khít** tập 26 type của v1
  (v2 có `point_on_circle`, `circumcenter`, `tangent_at_point`, `common_external_tangent`;
  v1 có `glider`, `rotate`, `reflect`, `translate`, `point_polar`, `bisector`, `incircle`,
  `center_of`, `arc`).
- `remove_object` **từ chối xoá** object còn có dependent — ràng buộc này sẽ áp thẳng vào editor.

## 3. Nơi kết quả được lưu

| Ngữ cảnh | Bảng / cột | Ảnh | Spec |
|---|---|---|---|
| Tài liệu (editor) | `document_visual_assets` (`asset_key`, `metadata_json`, `content_hash`, `bbox_json`) | file SVG trong `LocalStorage`, phục vụ qua `GET /editor/assets/{path}` | trong `metadata_json` |
| HTML tài liệu | `editor_documents.content_html` (versioned, append-only) | thẻ `<img src>` trỏ asset | v2: `data-jsxgraph-source` nằm **trong HTML**; v1: không |
| Chat | `chat_messages.metadata_json` | `preview_html` = SVG nhúng inline | `preview_spec` (v2) trong metadata |

`DocumentVisualAsset` có unique constraint `(document_id, editor_version, page_no, figure_index)`.
`LocalStorage` có sẵn `write_bytes` → lưu PNG là khả thi, không cần hạ tầng mới.

## 4. Các surface FE đang hiển thị hình do agent vẽ

| # | Đường dẫn | Cơ chế | Tương tác |
|---|---|---|---|
| 1 | `templates/HomePage/index.tsx:299` | `GeometryPreview` → iframe `sandbox=""` | Chỉ xem |
| 2 | `components/Chat/partial/message-item.tsx:23` | như trên | Chỉ xem |
| 3 | `templates/DocumentDetailPage/partial/ready-document-view.tsx:273` | như trên | Chỉ xem |
| 4 | `components/TiptapEditor` (canvas tài liệu) | `GeometryFigure` + `JsxGraphNode` node view | Board JSXGraph sống; kéo được điểm tự do |

Ba surface chat/document-detail dùng **cùng một component** `Chat/partial/geometry-preview.tsx`
— iframe `sandbox=""` (không cho phép script), nên SVG hoàn toàn tĩnh ở đó.

## 5. Khả năng chỉnh sửa đã có (và giới hạn của nó)

`jsxgraph-extension.tsx` **đã có một mini-editor sơ khai**:

- Nút "Chỉnh sửa" hiện khi node được chọn → `JsxGraphEditPanel` với 2 tab.
- Tab `length`: 3 ô nhập độ dài cạnh a/b/c — **chỉ chạy khi source khớp regex tam giác**
  (`parseTriangleModel`). Không khớp → panel gần như trống.
- Tab `source`: sửa JS thô, nhưng **đã bị tắt** (`JSXGRAPH_SOURCE_EDITING_ENABLED = false`).
- Lưu = `updateAttributes({ source })` → **chỉ đổi attribute trong ProseMirror**.

Hệ quả quan trọng — **hai lỗi hiện hữu**, cần ghi nhận trước khi xây tiếp:

1. **Ảnh SVG trên server không được render lại.** Sau khi người dùng sửa, `data-jsxgraph-source`
   đổi nhưng `<img src>` vẫn trỏ SVG cũ. Mọi consumer đọc ảnh — export PDF/DOCX, thumbnail,
   chế độ no-JS, và cả `GeometryPreview` ở chat — sẽ thấy hình **cũ**. `PUT /editor/jsxgraph/{asset_id}`
   đã tồn tại ở BE để làm đúng việc này nhưng FE không có API client tương ứng
   (`bookforge-api.ts` chỉ có `APIGetEditorGeometry`).
2. **`metadata_json.math_figure_spec` cũng lệch** — agent đọc spec từ metadata khi sửa figure,
   nên bản sửa tay của người dùng vô hình với agent ở lượt sau.

Node `GeometryFigure` (v1) **không có** UI chỉnh sửa nào — chỉ render board rồi thôi.

## 6. Ràng buộc cốt lõi: đây là đồ thị dựng hình, không phải danh sách shape

Đây là phát hiện quyết định phạm vi khả thi của mini-editor.

```
point A  (coords: [0,0])      ← tự do, có toạ độ riêng
point B  (coords: [4,0])      ← tự do
midpoint M (points: [A,B])    ← dẫn xuất, KHÔNG có toạ độ riêng
circle c (center: M, through: A)
projection H (point: C, line: AB)
```

- "Di chuyển M" là **vô nghĩa** — M được định nghĩa bởi A và B.
- "Resize đường tròn c" cũng vô nghĩa — bán kính do M và A quyết định.
- Cái người dùng thực sự có thể đổi: **toạ độ điểm tự do**, **style/label/visible**,
  **thêm/xoá object ở mức đồ thị**, **bounding box của view**, và các **tham số vô hướng**
  (`radius` của `circle_radius`, `ratio` của `point_on_segment`, `angle` của `rotate`…).
- JSXGraph đã tự lo phần lan truyền ràng buộc khi kéo điểm tự do — `registry.ts` dựng đúng
  các element phụ thuộc gốc để việc này hoạt động.

Một editor kiểu Fabric.js (kéo/resize/xoay shape rời rạc) **về bản chất không tương thích**
với mô hình dữ liệu này. Xem `02-feasibility-options.md`.

## 7. Ràng buộc kỹ thuật khác cần tôn trọng

- **Schema contract**: `frontend/src/components/TiptapEditor/editor-schema-contract.ts` —
  thêm node/mark vào `extensions.ts` sẽ làm fail contract test cho tới khi cập nhật cả
  contract doc lẫn fixture export phía backend. → **Ưu tiên không thêm node mới**; tái dùng
  `GeometryFigure` / `JsxGraphNode` đang có.
- **CONVENTION.md (FE)**: tối đa 300 dòng/file, 100 dòng/hàm, file kebab-case, type prefix `T`,
  hàm API prefix `API`, tách phần dư vào thư mục `partial/`.
- **Bảo mật**: `new Function(...)` ở `jsxgraph-extension.tsx:379` thực thi JS lấy từ
  `content_html`. `GEOMETRY_SPEC.md` khẳng định "document HTML never contains raw JSXGraph
  source or executable script" — điều đó **chỉ đúng với v1**. Nếu mini-editor ghi được vào
  document HTML, tuyệt đối không mở rộng bề mặt này.
- **Lưu tài liệu**: `PUT /editor` tạo `EditorDocument` version mới mỗi lần nội dung đổi
  (append-only, đã có sẵn lịch sử phiên bản ở mức tài liệu).
- **Chat không có document_id** — `_run_geometry_chat` không tạo `DocumentVisualAsset`.
  Đây là khoảng trống lớn nhất cho yêu cầu "lưu ảnh vào chat"; xem câu hỏi mở ở
  `01-requirements.md`.

## 8. Kiểm thử đang bảo vệ vùng này

BE: `test_geometry_{assets,normalize,parser,registry,svg_render,goldens,pipeline,generation,
operation_model,construction_fixes,frontend_contract,eval_oracle}.py`,
`test_editor_{jsxgraph,geometry_integration}.py`.

FE: `geometry/registry.test.ts`, `geometry/board.test.ts`, `geometry-figure-{extension,view}.test.tsx`,
`test/jsxgraph-render.test.ts`, `editor-schema-contract.test.ts`.

`test_geometry_frontend_contract.py` giữ đồng bộ registry BE ↔ FE — mọi thay đổi tập primitive
phải đi qua đây.
