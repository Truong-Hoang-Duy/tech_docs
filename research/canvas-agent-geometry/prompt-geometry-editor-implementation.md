# PROMPT: Triển khai Mini-Editor cho Canvas Agent (Giai đoạn 2 — sau nghiên cứu)

## VAI TRÒ
Bạn là senior full-stack engineer, làm việc trên dự án gồm `backend/` và `frontend/`.
Nghiên cứu khả thi đã hoàn tất và được duyệt tại `tech_docs/research/canvas-agent-geometry/`
(5 file: `00-current-state-analysis.md` → `04-implementation-plan.md`). **Đọc kỹ cả 5 file này
trước khi viết bất kỳ dòng code nào** — chúng chứa toàn bộ phân tích kiến trúc, rủi ro, và lý do
tại sao các quyết định dưới đây được chọn.

## QUYẾT ĐỊNH ĐÃ CHỐT (áp dụng thay cho các câu hỏi mở ở `01-requirements.md` §4)

| # | Quyết định | Ghi chú triển khai |
|---|---|---|
| Q1 | Giữ song song **spec (editable) + ảnh (display)** sau Save | Không "đóng băng" — figure vẫn sửa tiếp được, kể cả bởi AI |
| Q2 | Ảnh lưu dạng **SVG** | Không thêm dependency raster (`resvg`/`cairosvg`) |
| Q3 | Chat: **ghi đè tại chỗ** `preview_html`/`preview_spec` trong `metadata_json` của tin nhắn đã tạo hình | Chấp nhận đánh đổi: lịch sử hội thoại hiển thị bản đã sửa, không giữ bản gốc AI vẽ |
| Q4 | **Không** cần version history cho từng asset | `update_geometry_asset`/`update_jsxgraph_asset` tiếp tục ghi đè tại chỗ như hiện tại |
| Q5 | **Có** — sau khi sửa tay, agent phải đọc được spec đã sửa ở lượt hỏi tiếp theo | Bắt buộc ghi spec mới vào đúng `metadata_json.geometry_spec` (v1) / `metadata_json.math_figure_spec` (v2), không chỉ đổi attribute Tiptap |
| Q6 | **Có** — MVP hỗ trợ **thêm object mới**, nhưng giới hạn ở primitive cơ bản đã có trong registry (point, midpoint, line qua 2 điểm, circle, intersection, perpendicular, parallel...). **Không** làm composite (triangle, square, rectangle...) trong editor | Composite vẫn nhờ AI — tránh trùng lặp logic khai triển ở `registry.py` |
| Q7 | **Không** hỗ trợ nhiều người sửa đồng thời | Dùng optimistic lock bằng `content_hash`, trả 409 khi lệch |

## PHẠM VI ĐỢT NÀY (đã gộp lại so với `04-implementation-plan.md` do Q3 rẻ hơn dự kiến)

Thực hiện gộp **G0 → G1 → G2(mở rộng) → G3 → G4a**, dừng trước phần chưa cần (xem "Ngoài phạm vi").

### Giai đoạn 0 — Sửa lỗi hiện hữu (làm trước, giá trị độc lập)
Theo đúng `00-current-state-analysis.md` §5 và `04-implementation-plan.md` G0:
- [ ] Viết `APIUpdateEditorJsxGraph` (client cho `PUT /editor/jsxgraph/{asset_id}` đã có sẵn ở BE).
- [ ] `JsxGraphNodeView` gọi API này sau khi sửa, thay vì chỉ `updateAttributes` cục bộ.
- [ ] Bust cache `<img src>` bằng query `?v={content_hash}`.

### Giai đoạn 1 — Backend
- [ ] `PUT /editor/geometry/{asset_id}` (endpoint mới, đối xứng với `update_editor_jsxgraph` đã có) — theo đúng contract ở `03-recommended-architecture.md` §3.1.
- [ ] Mở rộng `PUT /editor/jsxgraph/{asset_id}` để nhận `content_hash` tuỳ chọn (optimistic lock).
- [ ] Mã lỗi mới `editor_asset_conflict` (409), áp cho cả hai endpoint.
- [ ] `record_event('editor_geometry_updated')` đối xứng với `editor_jsxgraph_updated`.
- [ ] **Chat (Q3)**: endpoint hoặc mở rộng service để ghi đè `preview_html`/`preview_spec` trong `metadata_json` của `chat_messages` sau khi verify + render lại SVG. Tái dùng pipeline verify/render đã có, chỉ khác đích ghi (message thay vì `DocumentVisualAsset`).
- [ ] **Thêm object mới (Q6)**: đảm bảo BE verify chấp nhận spec có thêm object primitive cơ bản qua đúng đường `normalize`/`verifier` (v1) hoặc `apply_geometry_operations` với `upsert_object` (v2, đã hỗ trợ sẵn) — nhiều khả năng **không cần thêm gì ở BE cho v2**; v1 cần xác nhận `normalize.py` chấp nhận object mới trong spec đầy đủ (không phải patch).
- [ ] Test: cập nhật hợp lệ, spec suy biến → 422, sai asset → 404, hash lệch → 409, view-only → 403, thêm object mới hợp lệ/suy biến.

### Giai đoạn 2 — Component editor độc lập (trọng tâm, xây tách rời Tiptap trước)
Theo cấu trúc thư mục ở `03-recommended-architecture.md` §4.1, cộng thêm phần cho Q6:

```
frontend/src/components/GeometryEditor/
├── index.tsx
├── types.ts
├── use-geometry-editor.ts          # + "chế độ tạo mới" (creating mode) tách biệt "chế độ chọn/sửa"
├── serialize.ts
├── serialize-v2.ts
├── dependencies.ts                 # ai xoá được / ai kéo được
├── creation.ts                     # MỚI (Q6): định nghĩa arity + kiểu tham chiếu cho mỗi primitive
│                                    #   cơ bản được phép tạo trong editor; validate thứ tự chọn điểm cha
└── partial/
    ├── editor-board.tsx
    ├── object-list-panel.tsx
    ├── property-panel.tsx
    ├── view-panel.tsx
    ├── editor-toolbar.tsx
    └── add-object-toolbar.tsx      # MỚI (Q6): chọn loại primitive → hướng dẫn chọn điểm cha trên board
```

Việc cần làm:
- [ ] `types.ts` + `dependencies.ts` — đồ thị phụ thuộc, khớp luật `apply_geometry_operations`.
- [ ] `serialize.ts` / `serialize-v2.ts` — round-trip model ↔ spec, test golden lấy từ `test_geometry_goldens.py`.
- [ ] **`partial/editor-board.tsx`** — làm trước tiên để lộ rủi ro sớm (đúng khuyến nghị ở `04-implementation-plan.md`): kéo điểm tự do, phân biệt điểm dẫn xuất (chấm rỗng/xám, không kéo, click hiện "Phụ thuộc: A, B").
- [ ] `use-geometry-editor.ts` — state, undo stack (≤50 snapshot spec, không dùng ProseMirror history), dirty flag, chế độ tạo mới.
- [ ] `object-list-panel.tsx` — chọn/ẩn-hiện/xoá có kiểm tra phụ thuộc (nút disable + tooltip liệt kê dependent khi còn ràng buộc).
- [ ] `property-panel.tsx` — màu, nhãn, độ dày, nét đứt, tham số vô hướng (`radius`, `ratio`, `angle`...).
- [ ] `view-panel.tsx` + `editor-toolbar.tsx` (Hoàn tác/Làm lại/Huỷ/Lưu).
- [ ] **`add-object-toolbar.tsx` + `creation.ts` (Q6)**: danh sách primitive cơ bản được phép tạo (khác nhau giữa v1/v2 theo bảng `_SUPPORTED_TYPES` vs 26 type ở `00-current-state-analysis.md` §2); chọn công cụ → click các điểm cha theo đúng arity → xác nhận tên/nhãn → thêm vào model → đẩy vào undo stack. Nếu primitive cần tham số số học (vd bán kính), hỏi ngay sau khi chọn điểm cha.
- [ ] `index.tsx` — shell ghép các mảnh, banner chỉ-xem, hiện `serverIssues`. Giữ ≤150 dòng.
- [ ] Test: serialize round-trip, luật phụ thuộc, undo/redo, chế độ chỉ-xem, **tạo mới từng loại primitive cơ bản + trường hợp suy biến bị BE từ chối**.

Interface `<GeometryEditor>` giữ nguyên theo `03-recommended-architecture.md` §4.2 — **không gọi API trực tiếp, không biết Tiptap/chat/document**; host truyền `onSave` riêng.

### Giai đoạn 3 — Nhúng vào canvas tài liệu
- [ ] `APIUpdateEditorGeometry` client.
- [ ] Nhúng vào `geometry-figure-view.tsx` (v1): nút "Chỉnh sửa" + modal + adapter save.
- [ ] **Thay** `JsxGraphEditPanel` bằng editor mới trong `jsxgraph-extension.tsx` (v2) — **rủi ro cao nhất**, đụng code đang chạy. Tách file này theo CONVENTION (đang 803 dòng) nhân dịp này. Cân nhắc giữ tab "độ dài cạnh" cũ chạy song song một thời gian.
- [ ] Truyền `documentId` vào `JsxGraphNode` (bắt chước `GeometryFigure.configure({ documentId })`).
- [ ] Fallback chỉ-xem cho figure không có spec (`math_figure_spec` rỗng) kèm thông báo rõ.
- [ ] Chế độ chỉ-xem khi tài liệu view-only (không hiện nút Lưu).
- [ ] Test node view: mở, sửa, lưu, lỗi, chỉ-xem, thêm object mới.

### Giai đoạn 4a — Chat (Q3 đã chốt, đưa vào đợt này)
- [ ] Lộ `preview_spec` thành field riêng trong `ChatMessageResponse` (hiện chỉ có trong dict `metadata`).
- [ ] Nút chỉnh sửa trên `GeometryPreview` (component dùng chung ở `Chat/partial/geometry-preview.tsx`, đang phục vụ cả 3 surface chat/home/document-detail) → mở cùng `<GeometryEditor>`.
- [ ] Adapter save: gọi endpoint ghi đè `metadata_json` của tin nhắn (Giai đoạn 1) → re-render `preview_html` → cập nhật UI ngay không cần reload.
- [ ] `DocumentDetailPage` (`ready-document-view.tsx`) dùng chung component → gần như free sau bước trên.
- [ ] Test: sửa hình trong chat, hỏi AI "chỉnh hình này" ở lượt sau → xác nhận AI đọc được `preview_spec` đã sửa (đúng Q5).

### Giai đoạn 5 — Tài liệu & dọn dẹp
- [ ] `tech_docs/` — hướng dẫn dùng `<GeometryEditor>` (props, adapter, cách nhúng surface mới, cách thêm primitive được phép tạo).
- [ ] Cập nhật `backend/docs/GEOMETRY_SPEC.md`: thêm endpoint PUT mới, đính chính câu "document HTML never contains raw JSXGraph source" (chỉ đúng với v1).
- [ ] Ghi chú vào `CANVAS_AGENT_ONBOARDING.md` về component mới.

## NGOÀI PHẠM VI (giữ nguyên theo nghiên cứu, không tự ý mở rộng)
- Hợp nhất GeometrySpec v1 và v2.
- Thêm primitive hoàn toàn mới vào registry (vd `text` annotation).
- Composite (triangle, square...) trong add-object toolbar — vẫn nhờ AI.
- Bật lại tab sửa source JS thô.
- Export PNG.
- Version history cho từng asset.
- Hỗ trợ nhiều người sửa đồng thời.

## NGUYÊN TẮC BẮT BUỘC (nhắc lại từ `03-recommended-architecture.md` §1 và ràng buộc dự án)
1. Spec là nguồn sự thật; ảnh luôn là sản phẩm phái sinh — không bao giờ ghi ảnh mà không ghi spec cùng lúc.
2. Server verify, server render — client không tự quyết định hình hợp lệ.
3. Editor không phụ thuộc Tiptap/chat/document — chỉ nhận/trả `spec`.
4. Không thêm node Tiptap mới (tránh vỡ `editor-schema-contract.ts`).
5. Tuân thủ `CONVENTION.md`: ≤300 dòng/file, ≤100 dòng/hàm, kebab-case, type prefix `T`, hàm API prefix `API`, tách `partial/`.
6. Không mở rộng bề mặt `new Function` — mọi thao tác trong editor làm việc trên spec JSON.
7. `npm run lint`, `typecheck`, `test` và test suite BE liên quan (liệt kê ở `00-current-state-analysis.md` §8) phải xanh trước khi coi một giai đoạn là xong.

## QUY TRÌNH LÀM VIỆC
- Làm theo đúng thứ tự G0 → G1 → G2 → G3 → G4a → G5. Sau mỗi giai đoạn, dừng lại báo cáo tóm tắt (file đã đổi, test đã chạy, rủi ro phát sinh) trước khi sang giai đoạn kế tiếp.
- Riêng **Giai đoạn 3, task "thay `JsxGraphEditPanel`"**: bắt buộc dừng lại xin xác nhận trước khi xoá code cũ, vì đây là tính năng người dùng đang dùng.
- Nếu trong lúc code phát hiện giả định trong tài liệu nghiên cứu sai (ví dụ `normalize.py` không chấp nhận object mới như dự đoán ở G1), dừng lại báo cáo thay vì tự ý đổi hướng.

## ĐIỀU KIỆN CHẤP NHẬN CUỐI CÙNG
Toàn bộ checklist ở `03-recommended-architecture.md` §6, cộng thêm:
- [ ] Thêm được object primitive cơ bản mới trong editor (cả v1 và v2), object suy biến bị BE từ chối kèm thông báo tiếng Việt.
- [ ] Sửa hình trong chat → `preview_html` cập nhật ngay, không cần reload; hỏi AI sửa tiếp → AI dùng đúng spec đã sửa.
- [ ] Hai request Save đồng thời với cùng `content_hash` cũ → request thứ hai nhận 409, không mất dữ liệu của request thứ nhất.
