# 04 — Kế hoạch triển khai

> Chưa code. Đây là danh sách task để anh duyệt / cắt bớt.
> Ước lượng độ phức tạp: **S** (< nửa ngày) · **M** (~1 ngày) · **L** (2–3 ngày).
> P0 = tài liệu (không chặn). P1 = chat (chặn bởi Q3). P2 = dọn dẹp.

## Giai đoạn 0 — Sửa lỗi hiện hữu (nền móng, làm trước)

Hai lỗi ở `00-current-state-analysis.md` §5 phải xử lý trước, nếu không mini-editor sẽ
kế thừa nguyên chúng.

| # | Task | Phía | Phức tạp | Rủi ro | Ghi chú |
|---|---|---|---|---|---|
| 0.1 | `APIUpdateEditorJsxGraph` — API client cho `PUT /editor/jsxgraph/{asset_id}` đã có sẵn | FE | S | Thấp | Chỉ là client, endpoint đã chạy |
| 0.2 | `JsxGraphNodeView` gọi 0.1 sau khi sửa (thay vì chỉ `updateAttributes`) | FE | S | **Trung bình** — đụng code đang chạy | Sửa được ngay bug ảnh SVG lệch |
| 0.3 | Bust cache `<img src>` bằng `?v={content_hash}` | FE | S | Thấp | Không có cái này thì 0.2 vô hình |

**Giá trị độc lập**: kể cả nếu dừng ở đây, tab "độ dài cạnh" hiện có đã hết lệch ảnh.

## Giai đoạn 1 — Backend (P0)

| # | Task | Phức tạp | Rủi ro | Ghi chú |
|---|---|---|---|---|
| 1.1 | Thêm `PUT /editor/geometry/{asset_id}` vào `api/editor.py` | M | Thấp | Sao chép cấu trúc của `update_editor_jsxgraph`; tái dùng `update_geometry_asset` đã có |
| 1.2 | Schema `EditorGeometryUpdateRequest` / mở rộng `EditorGeometrySpecResponse` (`content_hash`, `editor_html`) | S | Thấp | `schemas/documents.py` |
| 1.3 | Mã lỗi `editor_asset_conflict` (409) + optimistic lock theo `content_hash` | S | Thấp | `core/errors.py`; áp cho **cả** endpoint geometry và jsxgraph |
| 1.4 | `record_event('editor_geometry_updated')` | S | Thấp | Đối xứng với `editor_jsxgraph_updated` |
| 1.5 | Test: cập nhật hợp lệ, spec suy biến → 422, sai asset → 404, hash lệch → 409, view-only → 403 | M | Thấp | Nối vào `test_editor_geometry_integration.py` |

**Không có migration DB.** Không đụng `registry.py`, `verifier.py`, `svg.py`, `geometry_spec.py`.

## Giai đoạn 2 — Component editor độc lập (P0, phần lớn nhất)

Xây và test **hoàn toàn tách rời** khỏi Tiptap — có thể dựng một route demo tạm để thử tay.

| # | Task | Phức tạp | Rủi ro | Ghi chú |
|---|---|---|---|---|
| 2.1 | `types.ts` + `dependencies.ts` (đồ thị phụ thuộc: kéo được / xoá được) | M | Thấp | Thuần, test dễ. Phải khớp luật của `apply_geometry_operations` |
| 2.2 | `serialize.ts` — model ↔ GeometrySpec v1 | M | **Trung bình** | Round-trip phải bảo toàn; test golden với spec thật lấy từ `test_geometry_goldens.py` |
| 2.3 | `serialize-v2.ts` — model ↔ GeometrySpec v2 | M | **Trung bình** | Trường phẳng, khác v1; test riêng |
| 2.4 | `partial/editor-board.tsx` — board + drag điểm tự do + phân biệt điểm dẫn xuất | L | **Cao** | Phần khó nhất. Có thể phải rebuild board sau mỗi thay đổi cấu trúc |
| 2.5 | `use-geometry-editor.ts` — state, undo stack, dirty flag | M | Thấp | |
| 2.6 | `partial/object-list-panel.tsx` | M | Thấp | Chọn / ẩn-hiện / xoá có kiểm tra phụ thuộc |
| 2.7 | `partial/property-panel.tsx` | M | Thấp | Màu, nhãn, độ dày, nét đứt, tham số vô hướng |
| 2.8 | `partial/view-panel.tsx` + `partial/editor-toolbar.tsx` | S | Thấp | |
| 2.9 | `index.tsx` — shell, ghép các mảnh, banner chỉ-xem, hiện `serverIssues` | M | Thấp | Giữ ≤150 dòng |
| 2.10 | Test: serialize round-trip, luật phụ thuộc, undo/redo, chế độ chỉ-xem | M | Thấp | Vitest + Testing Library |

**Rủi ro chính là 2.4.** Nếu API xoá/tạo lại element của JSXGraph gây rắc rối, dự phòng là
rebuild toàn bộ board sau mỗi thay đổi cấu trúc (ở ≤60 object là chấp nhận được).
Nên thử nghiệm điểm này **trước tiên** trong giai đoạn 2 để lộ rủi ro sớm.

## Giai đoạn 3 — Nhúng vào canvas tài liệu (P0)

| # | Task | Phức tạp | Rủi ro | Ghi chú |
|---|---|---|---|---|
| 3.1 | `APIUpdateEditorGeometry` client | S | Thấp | |
| 3.2 | Nhúng vào `geometry-figure-view.tsx` (v1): nút + modal + adapter save | M | Thấp | Node này hiện chưa có UI sửa nào |
| 3.3 | **Thay** `JsxGraphEditPanel` bằng editor mới trong `jsxgraph-extension.tsx` (v2) | M | **Cao** | Đụng code đang chạy; `jsxgraph-extension.tsx` đang 803 dòng — **phải tách theo CONVENTION nhân dịp này** |
| 3.4 | Truyền `documentId` vào `JsxGraphNode` (v2 hiện chưa có) | S | Thấp | Bắt chước `GeometryFigure.configure({ documentId })` |
| 3.5 | Fallback chỉ-xem cho figure không có spec | S | Thấp | Rủi ro R3 |
| 3.6 | Chế độ chỉ-xem khi tài liệu view-only | S | Thấp | |
| 3.7 | Test node view: mở, sửa, lưu, lỗi, chỉ-xem | M | Thấp | |

**3.3 là task rủi ro nhất của cả dự án** — nó thay thế một tính năng người dùng đang dùng.
Cân nhắc giữ tab "độ dài cạnh" cũ song song một thời gian, hoặc chỉ chuyển sau khi 3.2 đã ổn.

## Giai đoạn 4 — Chat (P1, **chặn bởi Q3**)

Không lên lịch được cho tới khi chốt Q3.

| # | Task | Phức tạp | Ghi chú |
|---|---|---|---|
| 4.1 | Lộ `preview_spec` thành field trong `ChatMessageResponse` | S | Cần dù chọn phương án nào |
| 4.2 | Đường ghi cho geometry của chat | S → L | **Phụ thuộc hoàn toàn vào Q3** (b: S · c: M · d: L) |
| 4.3 | Nút chỉnh sửa trên `GeometryPreview` + modal | M | Dùng chung component với tài liệu |
| 4.4 | `DocumentDetailPage` — gần như free sau 4.3 | S | Cùng component |

## Giai đoạn 5 — Tài liệu & dọn dẹp (P2)

| # | Task | Phức tạp |
|---|---|---|
| 5.1 | `tech_docs/` — hướng dẫn dùng `<GeometryEditor>` (props, adapter, cách nhúng surface mới) | S |
| 5.2 | Cập nhật `backend/docs/GEOMETRY_SPEC.md`: thêm endpoint PUT, và **đính chính** khẳng định "no executable script" (chỉ đúng với v1) | S |
| 5.3 | Ghi chú vào `CANVAS_AGENT_ONBOARDING.md` §5 về component mới | S |

## Thứ tự triển khai đề xuất

```
G0 (sửa lỗi ảnh lệch)  ──► giá trị ngay, rủi ro thấp, làm quen vùng code
   │
   ├─► G1 (BE endpoint)      ──┐  chạy song song được
   └─► G2 (component độc lập) ──┤  ← làm 2.4 TRƯỚC để lộ rủi ro sớm
                                │
                                ▼
                          G3 (nhúng tài liệu)   ← 3.2 (v1, an toàn) trước 3.3 (v2, rủi ro)
                                │
                                ▼
                          [CHỐT Q3] ──► G4 (chat)
                                │
                                ▼
                              G5 (docs)
```

**Điểm dừng có ý nghĩa**: sau G3, tính năng đã dùng được đầy đủ trong tài liệu.
G4 có thể hoãn vô thời hạn mà không nợ kỹ thuật.

## Ước lượng tổng

| Giai đoạn | Ước lượng |
|---|---|
| G0 | ~0.5 ngày |
| G1 (BE) | ~1.5 ngày |
| G2 (component) | ~4–5 ngày |
| G3 (nhúng) | ~2 ngày |
| **Cộng P0** | **~8–9 ngày** |
| G4 (chat) | 1–4 ngày tuỳ Q3 |
| G5 | ~0.5 ngày |

## Việc **không** làm (ghi rõ để khỏi bị hiểu nhầm là bỏ sót)

- Hợp nhất GeometrySpec v1 và v2.
- Thêm primitive mới vào registry (ví dụ `text` cho annotation).
- Bật lại tab sửa source JS thô.
- Export PNG (trừ khi Q2 chốt là cần).
- Version history cho từng asset (trừ khi Q4 chốt là cần).
- Đồng sửa nhiều người (trừ khi Q7 chốt là cần).
