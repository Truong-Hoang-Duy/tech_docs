# 03 — Kiến trúc đề xuất

**Phương án chọn: A1 + B1 + C1** — editor dựa trên JSXGraph tôn trọng ràng buộc, render ảnh
ở server từ spec đã verify, lưu song song spec (editable) và ảnh (display).

> Kiến trúc này giả định các câu trả lời **mặc định** ở `01-requirements.md` §4.
> Q1(b) hoặc Q3(d) nếu được chọn sẽ làm thay đổi §3 và §5 bên dưới.

## 1. Nguyên tắc thiết kế

1. **Spec là nguồn sự thật; ảnh là sản phẩm phái sinh.** Không bao giờ có đường nào cho phép
   ảnh và spec lệch nhau — mọi lần ghi ảnh đều đi kèm ghi spec, trong cùng một transaction.
2. **Server verify, server render.** Client không bao giờ quyết định hình có hợp lệ hay không.
3. **Editor không biết gì về Tiptap, chat hay document.** Nó nhận `spec` vào, trả `spec` ra.
   Mọi thứ liên quan tới ngữ cảnh nằm ở lớp adapter.
4. **Không thêm node Tiptap mới** — tránh phải sửa `editor-schema-contract.ts` và fixture BE.

## 2. Luồng dữ liệu

```
                        ┌─────────────────────────────────────────┐
                        │  Host surface (một trong ba)            │
                        │  · GeometryFigure node view (v1)        │
                        │  · JsxGraphNode node view (v2)          │
                        │  · Chat message (P1, chờ Q3)            │
                        └───────────────┬─────────────────────────┘
                                        │ mở editor
                                        ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │  <GeometryEditor spec onSave onCancel readOnly />                  │
   │  ── thuần client, không biết host là ai ──                         │
   │                                                                    │
   │  spec ──► toEditorModel() ──► board JSXGraph (registry.ts)          │
   │              ▲                        │                            │
   │              │                 kéo điểm tự do / sửa panel           │
   │              │                        ▼                            │
   │              └──── serialize() ◄── undo stack (≤50 snapshot)       │
   └────────────────────────────────┬───────────────────────────────────┘
                                    │ onSave(nextSpec)
                                    ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │  Adapter theo ngữ cảnh (host tự chọn)                              │
   │  v1 → APIUpdateEditorGeometry(docId, assetId, spec, contentHash)   │
   │  v2 → APIUpdateEditorJsxGraph(docId, assetId, spec, contentHash)   │
   └────────────────────────────────┬───────────────────────────────────┘
                                    ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │  Backend                                                            │
   │  1. authz: DocumentAction.EDIT_CONTENT + _assert_document_editable  │
   │  2. optimistic lock: so contentHash gửi lên với asset.content_hash  │
   │  3. verify: normalize → verifier (v1) | normalize_v2 → concrete (v2)│
   │  4. render: render_geometry_svg | render_jsxgraph_fallback          │
   │  5. ghi: storage.write_text(asset_key) + cập nhật DocumentVisualAsset│
   │     (asset_key GIỮ NGUYÊN → URL ổn định)                            │
   │  6. record_event('editor_geometry_updated')                         │
   │  7. trả { asset_id, asset_url, spec, content_hash, editor_html }    │
   └────────────────────────────────┬───────────────────────────────────┘
                                    ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │  FE cập nhật node                                                   │
   │  updateAttributes({ src: `${asset_url}?v=${content_hash.slice(0,8)}`│
   │                     , source (chỉ v2) })                            │
   │  → người dùng bấm Lưu tài liệu → PUT /editor → version mới          │
   └────────────────────────────────────────────────────────────────────┘
```

**Ghi chú quan trọng về cache**: `asset_key` không đổi khi update (giống
`update_geometry_asset` hiện tại), nên URL giữ nguyên và trình duyệt sẽ cache ảnh cũ.
Bắt buộc phải bust bằng query `?v={content_hash}`.

## 3. Hợp đồng API backend

### 3.1 Endpoint mới — cập nhật hình v1

```http
PUT /api/documents/{document_id}/editor/geometry/{asset_id}
```

Đối xứng với `PUT /editor/jsxgraph/{asset_id}` đã có. Đặt ngay sau
`get_editor_geometry_spec` trong `api/editor.py`.

```ts
// Request
{
  spec: GeometrySpec,          // v1, đầy đủ (không phải patch)
  width?: number,              // mặc định giữ nguyên bbox_json.width
  height?: number,
  content_hash?: string        // optimistic lock; bỏ qua = ghi đè
}

// Response 200
{
  id: string,
  document_id: string,
  asset_url: string,
  spec: GeometrySpec,          // spec đã normalize + verify (có thể khác input)
  content_hash: string,
  editor_html: string
}
```

Mã lỗi tái dùng: `auth_required`, `access_denied`, `document_not_found`,
`document_not_editable`, `editor_asset_not_found`, `document_invalid_field`
(khi verify fail — kèm danh sách `ValidationIssue.message`).
Cần thêm **một** mã mới: `editor_asset_conflict` (409) cho trường hợp `content_hash` lệch.

### 3.2 Endpoint sẵn có — cập nhật hình v2

`PUT /api/documents/{document_id}/editor/jsxgraph/{asset_id}` **đã tồn tại và đã đúng**
(`api/editor.py:894`). Chỉ cần:
- Bổ sung tuỳ chọn `content_hash` để khoá lạc quan (thay đổi nhỏ, tương thích ngược).
- Viết API client ở FE (hiện chưa có).

Không cần đụng gì thêm vào `service.py`.

### 3.3 Mô hình dữ liệu

**Không thay đổi schema DB.** `DocumentVisualAsset` đã có đủ:
`metadata_json` (spec), `content_hash` (khoá lạc quan), `bbox_json` (kích thước),
`updated_at`. Không cần migration.

## 4. Thiết kế component FE

### 4.1 Cây thư mục (tuân thủ CONVENTION: ≤300 dòng/file, kebab-case, `partial/`)

```
frontend/src/components/GeometryEditor/
├── index.tsx                      # <GeometryEditor> — shell, ~150 dòng
├── types.ts                       # TGeometryEditorProps, TEditorModel, TEditorSelection
├── use-geometry-editor.ts         # hook: state + undo stack + dirty flag
├── serialize.ts                   # editorModel ↔ GeometrySpec (v1) — thuần, dễ test
├── serialize-v2.ts                # editorModel ↔ GeometrySpec v2
├── dependencies.ts                # đồ thị phụ thuộc: ai xoá được, ai kéo được
└── partial/
    ├── editor-board.tsx           # bọc board JSXGraph, gắn handler drag
    ├── object-list-panel.tsx      # danh sách object, chọn, ẩn/hiện, xoá
    ├── property-panel.tsx         # màu / nhãn / độ dày / nét đứt / tham số vô hướng
    ├── view-panel.tsx             # bounding box, hiện trục, tiêu đề
    └── editor-toolbar.tsx         # Hoàn tác / Làm lại / Huỷ / Lưu
```

### 4.2 Interface công khai

```ts
export type TGeometrySpecVersion = 1 | 2;

export type TGeometryEditorProps = {
  /** Spec ban đầu. Editor không tự fetch — host chịu trách nhiệm nạp. */
  spec: GeometrySpec | GeometrySpecV2;
  specVersion: TGeometrySpecVersion;
  /** Kích thước canvas mong muốn; mặc định 640×420 khớp backend. */
  width?: number;
  height?: number;
  /** Chỉ xem: tài liệu view-only, hoặc figure không có spec. */
  readOnly?: boolean;
  /** Lý do chỉ-xem, hiện trong banner (tiếng Việt). */
  readOnlyReason?: string;
  /** Trả spec đã sửa. Host tự gọi API tương ứng ngữ cảnh của mình. */
  onSave: (nextSpec: GeometrySpec | GeometrySpecV2) => Promise<void>;
  onCancel: () => void;
  /** Lỗi verify từ server, để hiện lên panel. */
  serverIssues?: string[];
};
```

**Editor không gọi API, không import `bookforge-api.ts`.** Đây là điều làm nó tái dùng được:
host quyết định lưu đi đâu.

### 4.3 Cách nhúng vào từng surface

| Host | Cách mở | Adapter Save |
|---|---|---|
| `geometry-figure-view.tsx` (v1) | Nút "Chỉnh sửa" khi node được chọn → modal | `APIUpdateEditorGeometry` → `updateAttributes({ src })` |
| `jsxgraph-extension.tsx` (v2) | **Thay** `JsxGraphEditPanel` hiện tại | `APIUpdateEditorJsxGraph` → `updateAttributes({ src, source })` |
| Chat (P1) | Nút trên `GeometryPreview` | Chờ chốt Q3 |

Cả hai node view đều đã có `documentId` (v1 qua `extension.options`, v2 cần bổ sung
tương tự `GeometryFigure.configure({ documentId })`) và `assetId` trong attrs.

### 4.4 Mô hình tương tác

- **Điểm tự do** (`point` có `coords`): chấm đặc, kéo được. Kéo xong → `board.on('up')`
  → đọc `X()`/`Y()` → cập nhật `coords` trong model → đẩy vào undo stack.
- **Điểm dẫn xuất**: chấm rỗng/xám, không kéo. Click → panel hiện "Phụ thuộc: A, B".
- **Object không phải điểm**: click để chọn → panel thuộc tính (màu, độ dày, nét đứt, ẩn/hiện).
- **Xoá**: chỉ bật khi `dependencies.ts` xác nhận không còn dependent; ngược lại nút bị
  disable kèm tooltip liệt kê object đang phụ thuộc (khớp đúng luật của
  `apply_geometry_operations`).
- **Undo/redo**: stack snapshot spec (JSON clone), giới hạn 50. Không dùng ProseMirror history.
- **Dirty guard**: đóng modal khi đang dirty → hỏi xác nhận.

### 4.5 Xử lý lỗi verify

Save → 422 `document_invalid_field` kèm danh sách issue → hiện tiếng Việt trên panel,
**giữ nguyên** trạng thái editor (không đóng, không mất bản sửa), để người dùng kéo lại.

## 5. Vấn đề chat (P1) — chưa khoá

Không thể thiết kế dứt điểm cho tới khi có Q3. Ba việc **chắc chắn** phải làm dù chọn
phương án nào:
1. `ChatMessageResponse` cần lộ `preview_spec` (hiện chỉ có trong `metadata` dict, chưa
   có field riêng — FE đọc được nhưng không có type).
2. Cần một endpoint ghi cho geometry của chat.
3. Cần quyết định về việc chỉnh sửa có làm thay đổi lịch sử hội thoại hay không.

Phần tài liệu (P0) **không phụ thuộc** vào việc này và có thể làm ngay.

## 6. Điều kiện chấp nhận (P0)

- [ ] Mở được hình v1 và v2 do agent vẽ; hình không có spec mở ở chế độ chỉ-xem có giải thích.
- [ ] Kéo điểm tự do → mọi object dẫn xuất cập nhật đúng theo ràng buộc.
- [ ] Đổi màu/nhãn/ẩn-hiện/tham số vô hướng → phản ánh ngay trên board.
- [ ] Xoá bị chặn đúng khi còn dependent, kèm lý do.
- [ ] Undo/redo hoạt động cho mọi thao tác trên.
- [ ] Save → ảnh SVG trên server đổi, `content_hash` đổi, `<img>` hiển thị ảnh mới (không bị cache).
- [ ] Sau Save, hỏi agent "sửa hình này" → agent đọc được spec đã sửa (không phải bản gốc).
- [ ] Hình suy biến bị BE từ chối kèm thông báo tiếng Việt; editor không mất dữ liệu.
- [ ] Tài liệu view-only → editor chỉ-xem, không có nút Lưu.
- [ ] Toàn bộ file ≤ 300 dòng, hàm ≤ 100 dòng; `npm run lint`, `typecheck`, `test` xanh.
