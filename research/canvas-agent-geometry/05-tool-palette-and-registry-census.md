# 06 — Bộ công cụ dạng lưới-icon cho `<GeometryEditor>` + kiểm kê registry thực chứng

**Ngày:** 2026-09-01
**Loại:** tài liệu nghiên cứu. **Không phải forward spec — không code theo tài liệu này.** Mọi mục ở §A.7 và §B.5 cần người sở hữu Q1–Q7 duyệt trước khi thành đặc tả.
**Trả lời:** research prompt "Bộ công cụ tạo dựng dạng lưới-icon phân nhóm cho `<GeometryEditor>` (Frontend + Backend)".
**Nối tiếp:** [`05-geogebra-parity-gap-analysis.md`](05-geogebra-parity-gap-analysis.md) — tài liệu này **đóng lỗ hổng §0/§A.2 của 05** (05 tự ghi nhận chỉ map được 22 nút mà prompt gọi tên, thiếu ảnh tham chiếu). Prompt lần này cung cấp **danh sách nút đầy đủ theo nhóm**, nên §A dưới đây là bản map hoàn chỉnh. Phần B là phần **hoàn toàn mới**: kiểm kê ba tầng (registry / verify / render) mà 05 không làm có hệ thống.

## 0. Nguồn dữ liệu

Toàn bộ tài liệu đọc trực tiếp từ code, không suy đoán từ hai đặc tả nền. File đã đọc **toàn bộ**:

| File | Dòng | Dùng cho |
|---|---|---|
| `backend/.../services/geometry/registry.py` | 1130 | §B.1 (v1), §B.2 |
| `backend/.../services/geometry/types.py` | 87 | định nghĩa `RefSpec`/`NumberSpec`/`Primitive` |
| `backend/.../services/geometry/normalize.py` | 234 | §B.3 |
| `backend/.../services/geometry/verifier.py` | 66 | §B.2 |
| `backend/.../services/geometry/svg.py` | 170 | §B.4 |
| `backend/.../services/geometry/README.md` | 7 | §B.6 |
| `backend/.../services/jsxgraph/geometry_spec.py` | 975 | §B.1 (v2), §B.5 |
| `backend/.../services/jsxgraph/geometry_pipeline.py` | 434 | `apply_geometry_operations` (:198) |
| `backend/.../services/jsxgraph/catalog.py` | 102 | §A.4 (nhóm `interactive_controls`) |
| `frontend/src/components/GeometryEditor/creation.ts` | 212 | §A.3 |
| `frontend/src/components/GeometryEditor/index.tsx` | 168 | §A.5 |
| `frontend/src/components/GeometryEditor/partial/add-object-toolbar.tsx` | 109 | §A.5 |
| `frontend/src/components/GeometryEditor/geometry-editor.css` | — | §A.5 |
| `frontend/src/components/TiptapEditor/geometry/{registry,types}.ts` | 317 / 72 | §A.3, §A.6 |
| `frontend/src/components/{Icon/index.tsx, TiptapEditor/partial/editor-toolbar-icons.tsx}` | — / 325 | §A.6 |
| `frontend/CONVENTION.md` | — | §A.5 |

**Test đã chạy (không sửa):**

```
uv run --directory services/api pytest tests/test_geometry_goldens.py tests/test_geometry_frontend_contract.py -q
→ 12 passed in 8.33s
```

Cả hai xanh. Không có drift nào giữa registry BE và hợp đồng FE **tại thời điểm này** — nhưng xem §B.7 về việc cơ chế test đó bảo vệ cái gì (và **không** bảo vệ cái gì).

---

# Phần A — Frontend

## A.1 Đính chính hai tiền đề của research prompt

Cần nói trước, vì hai tiền đề này ảnh hưởng tới kết luận §A.5.

**(1) `index.tsx` hiện KHÔNG phải "một cột dọc dùng chung một vùng cuộn".**
Đọc `geometry-editor.css`: `.geometry-editor-body` là `display:flex; flex-wrap:wrap` (board và sidebar **cạnh nhau**, wrap khi hẹp); `.geometry-editor-board` là `flex:0 0 auto`; `.geometry-editor-side` **đã có vùng cuộn riêng** — `max-height: 420px; overflow-y: auto`. Tức bố cục 2 cột + sidebar cuộn độc lập **đã tồn tại**. Cái thực sự thiếu so với mục tiêu là: (a) board không co giãn theo viewport (`width`/`height` là prop số cố định, mặc định 640×420 để khớp backend — xem §A.5), (b) `EditorToolbar` (Hoàn tác/Làm lại/Huỷ/Lưu) nằm **dưới** body chứ không nổi trên board, (c) công cụ là nút chữ chứ không phải icon. Đây là ba thay đổi nhỏ hơn nhiều so với "viết lại bố cục".

**(2) `add-object-toolbar.tsx` hiện là nút chữ — đúng như prompt mô tả** (`:52–64`, render `{primitive.label}` trong `<button>`), và grid của nó là `.geometry-editor-tool-grid` = `display:flex; flex-wrap:wrap` (`:137`). Phần này prompt mô tả chính xác.

## A.2 Bảng map đầy đủ: 48 công cụ → registry

Cột **Trong registry** đọc từ code thật (§B.1), không từ hai đặc tả nền.
Cột **Trong phạm vi?** = có làm được trong task F2 hiện tại **mà không** thêm primitive vào registry và **không** vi phạm Q1–Q7 / 7 nguyên tắc.

### Nhóm Công cụ cơ bản

| Công cụ | Trong registry | Việc cần làm cho `creation.ts` | Trong phạm vi? | Căn cứ |
|---|---|---|---|---|
| Di chuyển (chọn/kéo) | — (không phải object) | Không. Là **chế độ con trỏ**, đã có: `index.tsx:37 handleSelect` + `editor.creation === null` | ✅ Có | Mô hình tương tác §F2 FE |
| Điểm tự do | `point` — cả hai | Đã có (`add-object-toolbar.tsx:45` nút riêng, không qua `creation.ts`) | ✅ Có | `registry.py:704`; `geometry_spec.py:17` |
| **Thanh trượt tham số (Slider)** | **Không có ở đâu** | — | ❌ **Không** | Xem §A.4-(a). Chuỗi `slider` chỉ tồn tại ở `catalog.py:39` (nhánh JS thô) |
| Giao điểm | `intersection` — cả hai | Đã có (`creation.ts:100`) | ✅ Có | `registry.py:776`; `geometry_spec.py:24` |
| **Cực trị của hàm số** | Không có | — | ❌ **Không** | FE "Ngoài phạm vi": *"Đồ thị hàm số, biểu đồ thống kê — khác nhánh, không dùng `GeometrySpec`"* |
| **Nghiệm của hàm số** | Không có | — | ❌ **Không** | như trên |
| **Đường khớp tốt nhất** | Không có | — | ❌ **Không** | như trên + không có kind "tập dữ liệu" (`types.py:11` chỉ có 4 kind) |

### Nhóm Chỉnh sửa — không có cái nào là primitive

| Công cụ | Trong registry | Việc cần làm | Trong phạm vi? | Căn cứ |
|---|---|---|---|---|
| Chọn nhiều đối tượng | — | Mở rộng `TEditorSelection` (`types.ts:43`) từ `string \| null` thành mảng | ⚠️ Có, **nhưng là thay đổi state model**, lan sang `property-panel` / `object-list-panel` / `dependencies.ts` | Ngoài §F2 đã mô tả; nên tách task riêng |
| Di chuyển khung nhìn (pan) | — | Thuộc `view.boundingBox`; `view-panel.tsx` đã sửa bbox bằng số. Pan-bằng-chuột cần handler trên board | ✅ Có (UI thuần) | `types.ts:30 TEditorView` |
| Xoá | — | **Đã có** — `object-list-panel.tsx` + `dependencies.ts` (disable kèm tooltip khi còn dependent) | ✅ Có | DoD FE đã tick |
| Hiện/ẩn nhãn | — | `label` đã sửa được ở `property-panel`. "Ẩn nhãn" = đặt `label: ''` | ✅ Có | `normalize.py:102`; `svg.py:56 _point_labels` chỉ vẽ text khi có label |
| Hiện/ẩn đối tượng | — | **Đã có** — `style.visible` (`index.tsx:122`) | ✅ Có | `normalize.py:10 _STYLE_FIELDS`; `svg.py:81 hidden` |

### Nhóm Media

| Công cụ | Trong registry | Trong phạm vi? | Căn cứ (trích nguyên văn) |
|---|---|---|---|
| **Chèn ảnh** | Không có | ❌ **Không** | BE nguyên tắc 3: *"**Không nhận bitmap từ client** — payload luôn là spec JSON."* + Q2 *"Ảnh lưu dạng **SVG**"*; ảnh là **sản phẩm phái sinh** (nguyên tắc 1), không phải input |
| **Chèn văn bản / chú thích** | Không có | ❌ **Không** | Cả hai đặc tả, "Ngoài phạm vi": *"Thêm primitive hoàn toàn mới vào registry (ví dụ `text` cho annotation)."* + FE: *"Vẽ tự do / annotation ngoài mô hình hình học (mũi tên, ghi chú, highlight)."* |

### Nhóm Đo lường — cả ba chặn bởi cùng một lý do

| Công cụ | Trong registry | Trong phạm vi? | Căn cứ |
|---|---|---|---|
| Góc (**số đo**) | `angle` có, **nhưng chỉ là marker** | ❌ Không (ở nghĩa "đo") | `registry.py:900` dùng `_eval_marker_noop` (`:413`) — *"angle/arc are visual markers on already-validated points; no numeric constraint in v1"*. `svg.py:124` vẽ cung `<polyline>` cam, **không có `<text>` số đo**. Vẽ **cung góc** thì đã có (`creation.ts:114`) |
| Khoảng cách / độ dài | Không có | ❌ Không | Cần object mang **giá trị số hiển thị dạng chữ**. `svg.py` chỉ sinh `<text>` cho nhãn điểm (`:147`, `:157`). = primitive `text` mới → ngoài phạm vi |
| Diện tích | Không có | ❌ Không | như trên |

### Nhóm Biến đổi

| Công cụ | Trong registry | Việc cần làm cho `creation.ts` | Trong phạm vi? | Căn cứ |
|---|---|---|---|---|
| Đối xứng qua đường thẳng | `reflect` — **chỉ v1** | **Thêm entry mới** (chưa có trong `V1_ONLY`) | ⚠️ **Mơ hồ** — §A.3-(2) | `registry.py:747`, `over: RefSpec(1, {POINT, LINE})` |
| Đối xứng qua điểm | `reflect` — chỉ v1 | Cùng entry, `over` trỏ point | ⚠️ **Mơ hồ** — §A.3-(2) | `registry.py:747`; `_eval_reflect:203` phân nhánh theo `over ∈ points/lines` |
| Tịnh tiến theo vector | `translate` — chỉ v1 | **Thêm entry mới** | ⚠️ **Mơ hồ** — §A.3-(3) | `registry.py:755`; `vector: NumberSpec(2)` là **2 số literal**, không phải object vector |
| Quay quanh một điểm | `rotate` — chỉ v1 | **Thêm entry mới** | ⚠️ **Mơ hồ** — §A.3-(2) | `registry.py:739` |
| **Vị tự (scale) từ một điểm** | **Không có** | — | ❌ Không | Grep toàn `services/`: không có `dilate`/`scale`/`homothety`. Cần primitive mới |
| **Đối xứng qua đường tròn (nghịch đảo)** | **Không có** | — | ❌ Không | như trên |

### Nhóm Dựng hình

| Công cụ | Trong registry | Việc cần làm | Trong phạm vi? | Căn cứ |
|---|---|---|---|---|
| Trung điểm | `midpoint` — cả hai | Đã có (`creation.ts:36`) | ✅ Có | `registry.py:715` |
| Tâm (của đường tròn) | `center_of` — **chỉ v1** | Đã có (`creation.ts:145`) | ✅ Có (v1) | `registry.py:884`. v2 **không có** → §A.3-(6) |
| Đường vuông góc | `perpendicular` — cả hai | Đã có | ✅ Có | `registry.py:812` |
| **Đường trung trực** | `perpendicular_bisector` là **COMPOSITE** (`registry.py:1021`) | — | ⚠️ **Mơ hồ — cần quyết định** | Q6: *"chỉ primitive cơ bản trong registry; **không** composite"*. Xem §A.3-(4) |
| Đường song song | `parallel` — cả hai | Đã có | ✅ Có | `registry.py:820` |
| Đường phân giác góc | `bisector` — **chỉ v1** | Đã có (`creation.ts:131`) | ✅ Có (v1) | `registry.py:828`. **Kết luận dứt điểm ở §A.3-(4)** |
| Tiếp tuyến | `tangent` — cả hai | **Thêm entry mới** (thiếu ở `creation.ts`) | ✅ Có (chế độ "tại điểm trên đường tròn") | `registry.py:836`; `geometry_spec.py:27`. Chế độ khác: §A.3-(5) |

### Nhóm Đường

| Công cụ | Trong registry | Việc cần làm | Trong phạm vi? | Căn cứ |
|---|---|---|---|---|
| Đoạn thẳng | `segment` — cả hai | Đã có | ✅ Có | `registry.py:788` |
| Đường thẳng | `line` — cả hai | Đã có | ✅ Có | `registry.py:796` |
| Tia | `ray` — cả hai | Đã có | ✅ Có | `registry.py:804` |
| **Vector** | **Không có** | — | ❌ Không | Grep xác nhận `'vector'` chỉ là tên arg của `translate`. Ngoài entry registry còn cần **nhánh vẽ đầu mũi tên** trong `svg.py` (hiện mọi kind `line` vẽ `<line>` trơn, `svg.py:96`) |

### Nhóm Đường tròn

| Công cụ | Trong registry | Việc cần làm | Trong phạm vi? | Căn cứ |
|---|---|---|---|---|
| Đường tròn theo tâm (qua điểm) | `circle` — cả hai | Đã có | ✅ Có | `registry.py:844` |
| Đường tròn: tâm & bán kính | `circle_radius` — cả hai | Đã có | ✅ Có | `registry.py:852` |
| **Đường tròn qua 3 điểm** | `circumcircle` — **cả hai** | **Thêm entry mới** — khoảng trống rõ ràng nhất | ✅ **Có** | `registry.py:868`; `geometry_spec.py:19` |
| **Compa** (bán kính = một đoạn đo trước) | **Không có** | — | ❌ Không | `circle` lấy bán kính = dist(tâm, chính điểm đó); `circle_radius.radius` là **số literal**. Không entry nào biểu diễn "bán kính = dist(P,Q)" như một **quan hệ**. Cần primitive mới |
| **Nửa đường tròn** | `arc` (chỉ v1) làm được, **nhưng cần 2 object** | — | ⚠️ **Mơ hồ** — §A.3-(6) | `midpoint(A,B)` + `arc([M,A,B])`. `svg.py:141` xác nhận `arc` quét CCW từ A→B |
| Cung tròn | `arc` — **chỉ v1** | Đã có (`creation.ts:152`) | ✅ Có (v1) | `registry.py:908` |
| **Cung ngoại tiếp** (qua 3 điểm) | **Không có** | — | ❌ Không | `arc` nhận `[O, A, B]` (tâm, đầu, cuối), không phải 3 điểm trên cung. Cần primitive mới |
| **Hình quạt tròn** | **Không có** | — | ❌ Không | Cần marker mới **và** nhánh vẽ mới trong `svg.py` (hiện chỉ 3 nhánh marker, `svg.py:114`) |
| **Hình quạt ngoại tiếp** | **Không có** | — | ❌ Không | như trên |

### Nhóm Conic — cả bốn loại bỏ

| Công cụ | Trong registry | Trong phạm vi? | Căn cứ |
|---|---|---|---|
| Elip / Conic qua 5 điểm / Parabol / Hyperbol | Không có | ❌ **Không** | Lý do **kiến trúc, không chỉ phạm vi**: `types.py:11` khai báo `GeometryKind = Literal['point','line','circle','marker']` — **không có kind conic**. `GeometryValues` (`types.py:38`) chỉ có 3 bảng `points`/`lines`/`circles`; `svg.py` chỉ biết vẽ `<line>`, `<circle>`, 3 marker. Thêm conic = thêm kind thứ 5 → chạm `types.py` + `normalize.py` + `verifier.py` + `svg.py` + `registry.ts` FE, tức đúng mục *"Sửa thuật toán trong `registry.py`, `normalize.py`, `verifier.py`, `svg.py`"* trong "Ngoài phạm vi" BE |

### Nhóm Khác

| Công cụ | Trong registry | Trong phạm vi? | Căn cứ |
|---|---|---|---|
| Bút vẽ tự do | Không có | ❌ Không | FE "Ngoài phạm vi": *"Vẽ tự do / annotation ngoài mô hình hình học"* |
| Hình vẽ tay tự do | Không có | ❌ Không | như trên |
| Quan hệ (hiện quan hệ đại số) | Không có | ❌ Không | Đầu ra là **văn bản** → cùng rào cản với nhóm Đo lường |
| **Nút bấm (button script)** | Không có | 🛑 **DỪNG — §A.4** | Nguyên tắc 4 BE / 5 FE |
| **Ô checkbox** | Không có | 🛑 **DỪNG — §A.4** | như trên |
| **Ô nhập liệu (input box)** | Không có | 🛑 **DỪNG — §A.4** | như trên |

## A.3 Sáu điểm mơ hồ cần người ra quyết định chốt trước khi code

### (1) `creation.ts` đang thiếu 4 primitive **đã có sẵn ở cả hai stack**

Đây là phát hiện đáng giá nhất của Phần A. Giao của v1 và v2 có **17 type**; `creation.ts` mới lộ ra **12**. Bốn cái thiếu (không tính `point` vốn có nút riêng), **không cần đụng BE**:

| Type | v1 | v2 | Vì sao đáng thêm |
|---|---|---|---|
| `circumcircle` | `registry.py:868` | `geometry_spec.py:19` | Đúng nút GeoGebra "Đường tròn qua 3 điểm" |
| `tangent` | `registry.py:836` | `geometry_spec.py:27` | Đúng nút GeoGebra "Tiếp tuyến" (chế độ điểm-trên-đường-tròn) |
| `circle_by_diameter` | `registry.py:860` | `geometry_spec.py:18` | Không có nút GeoGebra tương ứng trực tiếp, nhưng là dựng hình phổ thông rất hay dùng |
| `point_on_segment` | `registry.py:723` | `geometry_spec.py:9` | Điểm chia đoạn theo tỉ lệ; cần 1 scalar `ratio` |

⚠️ **Cảnh báo về `polygon` (đã lộ ra rồi, `creation.ts:106`):** `svg.py:119–123` vẽ polygon thành `<polygon … fill-opacity="0.08" **stroke="none"**/>` — **tô nền, không có cạnh**. Đây chính là lý do composite `triangle` phải khai triển thành `polygon` + 3 `segment` (`_expand_triangle`, `registry.py:445`). Người dùng bấm nút "Đa giác" hiện tại nhận một mảng màu mờ không viền — **không giống kỳ vọng**. Không phải bug mới do task này gây ra, nhưng lên lưới icon thì nó nổi bật hơn nhiều so với một nút chữ.

Ngoài ra `creation.ts` cũng thiếu **3 primitive chỉ-v1**: `rotate` (`:739`), `reflect` (`:747`), `translate` (`:755`) — tức **toàn bộ nhóm Biến đổi**. Xem (2)/(3).

### (2) `reflect` / `rotate` là gì — kết luận dứt điểm

**Kết luận (đọc chữ ký, không suy đoán):**

- `reflect` (`registry.py:747`): `{'point': RefSpec(1, POINT_REF), 'over': RefSpec(1, frozenset({POINT, LINE}))}`, `produces = POINT`. → **Một primitive tổng quát** cho cả đối xứng-trục và đối xứng-tâm, phân biệt **theo kind của đối tượng được trỏ tới** ở `over`, không phải theo tên type. `_eval_reflect` (`:203`) phân nhánh `over ∈ values.points` → `reflect_point_over_point`, `over ∈ values.lines` → `reflect_point_over_line`, còn lại → issue `"is not a point or line"` (`:218`).
- `rotate` (`registry.py:739`): `{'point', 'center', 'angle': float}`, `produces = POINT`. Không có biến thể.
- `translate` (`registry.py:755`): `{'point', 'vector': NumberSpec(2), 'from': RefSpec(1,POINT), 'to': RefSpec(1,POINT)}`. `vector`/`from`/`to` đều **tuỳ chọn** (`normalize.py:14–17 _OPTIONAL_ARGS`), và `_eval_translate:227` từ chối nếu **dùng cả hai** cách.

**Điểm mơ hồ thật sự — không phải tên, mà là miền tác động:** cả ba đều `produces = POINT` và nhận `point: RefSpec(1, POINT_REF)`. Chúng biến đổi **một điểm**. GeoGebra biến đổi **bất kỳ object nào** (tam giác, đường tròn, đường thẳng). Muốn lật một tam giác ở đây, người dùng phải bấm nút 3 lần rồi tự tạo `polygon` mới.

**Câu hỏi cho người ra quyết định:** đưa 3 nút này lên lưới icon với nhãn nói rõ "đối xứng **một điểm**", hay giấu đi vì sẽ gây kỳ vọng sai? *(Tài liệu này không tự quyết.)*

### (3) `translate` — cách nhập vector nào cho UI?

Hai cách loại trừ nhau. `vector: [dx, dy]` cần 2 ô số (arity 1 point + 2 scalar). `from`/`to` cần bấm 2 điểm (arity 3 point). **Không được gửi cả hai** (`registry.py:227`). Cần chốt một, hoặc làm hai nút riêng.

### (4) `bisector` — trung trực hay phân giác? **Kết luận: PHÂN GIÁC GÓC.**

Tra thẳng chữ ký như prompt §B.2 yêu cầu:

```python
# registry.py:828
'bisector': Primitive(
    'bisector', LINE, {'points': RefSpec(3, POINT_REF)}, 'bisector',
    'angle bisector for angle AOB; args.points=[A,O,B]', evaluate=_eval_bisector),
```

`args` nhận **3 điểm**, doc ghi rõ *"angle bisector for angle AOB"*, và `_eval_bisector` (`:297`) chuẩn hoá hai vector `OA`, `OB` rồi lấy tổng — công thức phân giác trong. → **Phân giác góc.** `creation.ts:131` gán nhãn "Phân giác" — **đúng**, không cần sửa.

**Trung trực là một type khác, và nó là COMPOSITE:**

```python
# registry.py:1021
'perpendicular_bisector': Primitive(
    'perpendicular_bisector', LINE, {'points': RefSpec(2, POINT_REF)}, 'composite',
    'duong trung truc of segment AB; expands to midpoint + perpendicular',
    composite=True, expand=_expand_perpendicular_bisector),
```

→ **Xung đột trực tiếp với Q6**: *"chỉ primitive cơ bản trong registry; **không** composite"*. Và FE không bao giờ thấy nó — `normalize.py:106` khai triển composite **trước** khi build `object_types`, nên spec đi tới FE chỉ còn `midpoint` + `perpendicular`.

**Ba lựa chọn cho người ra quyết định (tài liệu này không tự chọn):**
1. Không có nút trung trực. Người dùng bấm "Trung điểm" rồi "Đường vuông góc" — 2 thao tác, đúng tinh thần Q6.
2. Một nút "Trung trực" tạo **2 object** (`midpoint` + `perpendicular`) trong một lần bấm. Không đụng BE, không dùng composite — nhưng phá vỡ giả định "1 công cụ = 1 object" của `buildCreatedObject` (`creation.ts:203`) và làm undo stack ghi 1 bước cho 2 object.
3. Nới Q6 để cho phép composite. **Cần duyệt lại Q6.**

### (5) `tangent` — ba chế độ GeoGebra, phủ không đều

| Chế độ | v1 | v2 |
|---|---|---|
| Tại một điểm **trên** đường tròn | ✅ `tangent` (`registry.py:836`) | ✅ `tangent` **và** `tangent_at_point` (`geometry_spec.py:22,27` — hai tên, cùng một nhánh xử lý tại `geometry_spec.py:482–491`) |
| Từ một điểm **ngoài** → 2 tiếp tuyến | ⚠️ chỉ qua **composite** `tangent_from_point` (`registry.py:1030`) → Q6 cấm | ❌ **không có** |
| Chung của **hai đường tròn** | ❌ không có | ✅ `common_external_tangent` (`geometry_spec.py:23`), chỉ nhánh **ngoài**, `side: upper/lower` |

→ Nút "Tiếp tuyến" trên lưới icon chỉ nên phủ **chế độ 1**. Đây là bất đối xứng v1↔v2 lớn nhất tìm được (xem thêm §B.5).

### (6) "Nửa đường tròn" và "Trung điểm/tâm" — gộp hay tách nút?

- **Nửa đường tròn**: làm được bằng `midpoint` + `arc` — nhưng lại là "1 nút → 2 object", cùng vấn đề với (4). Và **v2 không có `arc`** nên nút này chỉ sống ở v1.
- **Trung điểm/tâm**: GeoGebra gộp một nút. Ở đây là 2 type khác nhau — `midpoint` (2 điểm, cả hai stack) và `center_of` (1 đường tròn, **chỉ v1**). Gộp thành một nút "thông minh" theo kind của đối tượng được bấm là làm được, nhưng `TCreatablePrimitive` hiện có `type` **cố định** (`creation.ts:15`) → cần đổi shape của type đó. Tách 2 nút thì không cần đụng gì.

## A.4 🛑 Điểm phải dừng và báo cáo: Nút bấm / Checkbox / Ô nhập liệu

Prompt §3.3 yêu cầu xác nhận rõ ràng. **Xác nhận: có, ba công cụ này bắt buộc mở rộng bề mặt thực thi JS phía client** — trừ khi định nghĩa lại chúng thành thứ khác hẳn. Ba bằng chứng độc lập:

**(a) Trong codebase này, `button`/`checkbox`/`input` chỉ tồn tại ở đúng một chỗ, và chỗ đó là nhánh JS thô.**

```python
# services/jsxgraph/catalog.py:37–40
'group': 'interactive_controls',
'objects': ('slider', 'checkbox', 'button', 'input'),
'examples': ('parameter slider', 'dynamic triangle side length', 'movable construction'),
```

Đây là catalog **quảng cáo cho LLM** thuộc nhánh `MathFigureSpec` sinh **JSXGraph source dạng chuỗi JS**. Không có type nào trong `PRIMITIVES` (26) hay `_SUPPORTED_TYPES` (21) tương ứng.

**(b) Đường duy nhất để chuỗi JS đó chạy là `new Function`, đúng chỗ nguyên tắc cấm mở rộng.**

```ts
// frontend/src/components/TiptapEditor/partial/jsxgraph-source.ts:231
const execute = new Function("board", `"use strict";\n${executableSource}${returns}`);
```

Nguyên tắc 5 FE: *"**Không mở rộng bề mặt `new Function`** … Tab sửa source thô đang tắt có chủ ý (`JSXGRAPH_SOURCE_EDITING_ENABLED = false`) — **không bật lại**."* Nguyên tắc 4 BE: *"**Không mở rộng bề mặt `new Function`** — không thêm đường nào cho phép client ghi JS thô vào document HTML."* Có test khoá: `extensions.test.ts:120` — *"principle 5 — the `new Function` surface must not grow a user-facing editor again."*

**(c) Kể cả bỏ script đi thì vẫn chặn, chỉ là chặn ở chỗ khác.** Một checkbox "chỉ bật/tắt `style.visible` của object khác", không script, vẫn cần **lưu được** trong spec. `normalize.py:123–126` từ chối mọi `type` ngoài `PRIMITIVES` (issue `primitive`); `geometry_spec.py:604` ném `GeometrySpecError`. → cần primitive mới → *"Thêm primitive hoàn toàn mới vào registry"* đã ở "Ngoài phạm vi" của cả hai đặc tả.

**Kết luận:** không tự "diễn giải lại cho an toàn". Ba công cụ này cần một quyết định riêng ở cấp Q1–Q7 trước khi bất kỳ ai viết dòng code nào. **Slider rơi vào cùng nhóm này** vì cùng ba lý do, cộng thêm lý do thứ tư đã phân tích ở `05-…:§A.4` (lưu "giá trị tại lúc Save" thì slider không còn là slider — spec chỉ còn `radius: 3.5`, không trường nào giữ `min`/`max`/`step`).

## A.5 Bố cục — có vượt giới hạn không?

**Tình trạng hiện tại so với ngân sách:**

| File | Dòng | Ngân sách | Trạng thái |
|---|---|---|---|
| `index.tsx` | **168** | ≤150 (§F2) / ≤300 (`CONVENTION.md`) | ⚠️ **đã vượt ngân sách F2 trước khi thêm gì** |
| `add-object-toolbar.tsx` | 109 | ≤300 | ✅ |
| `creation.ts` | 212 | ≤300 | ⚠️ còn ~88 dòng dư; thêm 5–8 entry (~10 dòng/entry) là **chạm trần** |

**Ước lượng phần thêm vào.** Sau khi trừ hết mục ❌/🛑 ở §A.2, số công cụ khả thi là **~20** (12 đã có + 4 shared thiếu + 3 transform v1 + free point). Với pattern icon hiện có (~8–14 dòng SVG/icon, §A.6), tập icon là **~200–260 dòng**.

**Khuyến nghị (khả thi về kiến trúc, không vi phạm nguyên tắc nào):**

```text
src/components/GeometryEditor/
├── index.tsx                    # shell, cắt xuống ≤150 bằng cách đẩy layout xuống board-frame
├── creation.ts                  # ⚠️ 212 → tách nhóm ra creation-groups.ts nếu vượt 300
├── creation-groups.ts           # (mới) khai báo nhóm: id nhóm, nhãn tiếng Việt, thứ tự type
└── partial/
    ├── board-frame.tsx          # (mới) board + điều khiển nổi (zoom/fullscreen/undo/redo)
    ├── tool-palette.tsx         # (mới) thay add-object-toolbar: lưới icon phân nhóm
    ├── tool-icons.tsx           # (mới) ~20 component SVG tĩnh — §A.6
    └── … (6 file hiện có giữ nguyên)
```

**Không có nguyên tắc nào bị phá:** không thêm node Tiptap (ng.tắc 4), không đụng `new Function` (ng.tắc 5), không thêm thư viện (ng.tắc 6, §A.6), không parse ngược JS (ng.tắc 7), editor vẫn không import `bookforge-api.ts` (§F2). Interface công khai `TGeometryEditorProps` **giữ nguyên**.

**Một ràng buộc cần biết trước khi làm board co giãn theo viewport:** `width`/`height` mặc định **640×420 để khớp backend** (`index.tsx:14–15`, và `render_geometry_svg(spec, *, width=640, height=420)` ở `svg.py:74`). `svg.py:27` dùng scale **đồng nhất (letterbox)** — `min(width/…, height/…)`. Nếu board FE đổi tỉ lệ khung theo viewport mà `onSave` vẫn gửi 640×420, ảnh SVG server render sẽ **letterbox khác** với những gì người dùng vừa thấy. Đây là chênh lệch preview↔SVG mà **cả hai đặc tả đã ghi là ngoài phạm vi**, nhưng một board full-viewport sẽ làm nó lộ rõ hơn đáng kể. Cần chốt: board co giãn nhưng **khoá tỉ lệ 640:420**, hay cho `onSave` gửi kèm `width`/`height` thật (endpoint B1 **đã nhận** hai field này).

## A.6 Icon — dùng lại pattern nào

**`package.json` không có thư viện icon nào.** Không `lucide`, không `react-icons`, không `@heroicons`. Icon trong repo được **tự vẽ**, theo đúng hai pattern:

| Pattern | Vị trí | Hình thức | Hợp cho công cụ hình học? |
|---|---|---|---|
| Registry path tập trung | `src/components/Icon/index.tsx` | `{ "tên-icon": "M7.08 2.71c1.95…" }` — **một chuỗi `d` duy nhất** mỗi icon | ❌ **Không.** Icon công cụ hình học cần nhiều phần tử (chấm điểm + đoạn + cung + nét đứt) — một `d` không diễn đạt được, và không có chỗ cho `fill`/`stroke` khác nhau giữa các phần |
| Component SVG cục bộ | `src/components/TiptapEditor/partial/editor-toolbar-icons.tsx` (325 dòng) | `export const BulletListIcon = () => (<svg className="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line …/><circle …/></svg>)` | ✅ **Đúng cái cần** — đa phần tử, `currentColor` theo trạng thái nút |

**→ Khuyến nghị: theo pattern thứ hai.** Đây **không phải nguồn icon mới** — nó là pattern đã dùng cho chính thanh công cụ Tiptap.

⚠️ **Nhưng đừng lặp lại lỗi của nó:** `editor-toolbar-icons.tsx` **đang 325 dòng, vượt giới hạn 300 của `CONVENTION.md`**. Với ~20 icon (~200–260 dòng) thì một file `tool-icons.tsx` vẫn dưới trần — nhưng nếu danh sách công cụ phình lên thì phải tách theo nhóm ngay, đừng đợi.

**Xác nhận cách hiểu nguyên tắc 6** (prompt §3.5 yêu cầu xác nhận, không suy diễn). Nguyên văn: *"**Không thêm thư viện canvas mới** — `jsxgraph@^1.12.2` đã có trong `package.json`."* Ba căn cứ cho thấy nó nói về **dependency**, không về hình vẽ tĩnh:

1. Câu giải thích trỏ thẳng vào `package.json` — đơn vị đo là **gói phụ thuộc**.
2. Bối cảnh ở §"Ràng buộc quyết định phạm vi" nói rõ đối tượng: *"Một editor kiểu Fabric.js/tldraw (kéo–resize–xoay shape rời rạc) **về bản chất không tương thích** với mô hình này"* — tức lo về **mô hình tương tác của thư viện canvas**, không về SVG tĩnh.
3. SVG tĩnh viết tay không thêm dòng nào vào `package.json`, không dựng canvas, không nhận sự kiện chuột.

→ **Icon SVG tĩnh tự vẽ không chạm nguyên tắc 6.** Cách hiểu này khớp với việc `editor-toolbar-icons.tsx` đã tồn tại và không bị coi là vi phạm.

## A.7 Bảng arity cho các công cụ **đã xác nhận khả thi** — bổ sung vào `creation.ts`

Theo đúng khuôn `TCreatablePrimitive` (`creation.ts:14–25`). Chỉ liệt kê phần **chưa có**; 12 entry hiện có giữ nguyên.

**Nhóm SHARED (v1 + v2) — thêm 4, không cần duyệt gì thêm:**

| type | Nhãn | arity | Kiểu tham chiếu (theo thứ tự bấm) | scalars | `toArgs` |
|---|---|---|---|---|---|
| `circumcircle` | Đường tròn qua 3 điểm | 3 | point, point, point | — | `{ points: picked }` |
| `tangent` | Tiếp tuyến tại điểm | 2 | **circle**, point *(điểm phải nằm trên đường tròn)* | — | `([circle, point]) => ({ circle, point })` |
| `circle_by_diameter` | Đường tròn đường kính | 2 | point, point | — | `{ points: picked }` |
| `point_on_segment` | Điểm chia đoạn | 2 | point, point | `ratio` (0–1, mặc định 0.5) | `([a,b], s) => ({ points:[a,b], ratio: s.ratio })` |

**Nhóm V1_ONLY — thêm 3, nhưng chờ chốt §A.3-(2)/(3):**

| type | Nhãn | arity | Kiểu tham chiếu | scalars | `toArgs` |
|---|---|---|---|---|---|
| `reflect` | Đối xứng (điểm) qua trục/tâm | 2 | point, **point hoặc line** | — | `([point, over]) => ({ point, over })` |
| `rotate` | Quay điểm quanh tâm | 2 | point, point *(tâm)* | `angle` (độ, mặc định 90) | `([point, center], s) => ({ point, center, angle: s.angle })` |
| `translate` | Tịnh tiến điểm | 1 **hoặc** 3 | point *(+ point, point nếu dùng from/to)* | `dx`, `dy` *(nếu dùng vector)* | ⚠️ hai biến thể loại trừ nhau — §A.3-(3) |

**Ràng buộc nên kiểm trước khi bấm (client-side, không thay server verify):**
- `tangent`: đối tượng thứ nhất phải là kind `circle`, thứ hai là `point` **và** `|dist(P, tâm) − r| ≤ 1e-5` (`registry.py:320`). Client cảnh báo sớm; **server vẫn là bên quyết định** (F5).
- `circumcircle`: 3 điểm không thẳng hàng (`registry.py:366`).
- `reflect`: `over` phải là point hoặc line, không được là circle (`registry.py:218`).

**🚫 KHÔNG thêm được (dù BE có hỗ trợ) — 4 primitive riêng của v2.** Đây là nguyên nhân gốc của mục DoD FE còn để trống (*"`creation.ts:178` mới trả `SHARED` cho v2, còn thiếu bốn primitive riêng của v2"*):

`creation.ts:15` khai báo `type: GeometryObjectType`, import từ `@/components/TiptapEditor/geometry/types` (`GeometryEditor/types.ts:3`). Union đó (`TiptapEditor/geometry/types.ts:6–32`) liệt kê **đúng 26 type của v1** — **không có** `point_on_circle`, `circumcenter`, `tangent_at_point`, `common_external_tangent`. Thêm 4 entry v2 vào `creation.ts` sẽ **không compile**, trừ khi nới union đó — mà file ấy nằm trong danh sách *"Đọc để hiểu, không sửa"* của đặc tả FE và có comment đầu file tự mô tả là mirror của v1. **Cần quyết định riêng**: tạo một union `TGeometryObjectTypeV2` riêng trong `GeometryEditor/types.ts`, hay nới union chung. Tài liệu này chỉ ghi nhận.

---

# Phần B — Backend: kiểm kê ba tầng

## B.1 Bảng kiểm kê đầy đủ

Ba tầng độc lập như prompt §B.1 yêu cầu. **Cột "nhánh vẽ SVG" cần đọc kèm §B.4** — `svg.py` không dispatch theo type.

### v1 — `PRIMITIVES` (26 base, `registry.py:703–921`)

| Object type | v1/v2 | Args + kiểu | Rule verify suy biến | Nhánh vẽ SVG | Dòng (def / eval) |
|---|---|---|---|---|---|
| `point` | cả hai | `coords: NumberSpec(2)` | coords phải hữu hạn | ✅ qua `values.points` | 704 / 133 |
| `glider` | **v1** | `on: Ref(1,{point,line,circle})`, `coords: NumberSpec(2)` | coords hữu hạn; parent không drawable; parent suy biến | ✅ points | 707 / 142 |
| `midpoint` | cả hai | `points: Ref(2, point)` | **không có** *(không thể suy biến)* | ✅ points | 715 / 166 |
| `point_on_segment` | cả hai | `points: Ref(2, point)`, `ratio: float` | `ratio ∉ [0,1]` | ✅ points | 723 / 172 |
| `projection` | cả hai | `point: Ref(1,point)`, `line: Ref(1,line)` | đường suy biến | ✅ points | 731 / 185 |
| `rotate` | **v1** | `point`, `center: Ref(1,point)`, `angle: float` | **không có** | ✅ points | 739 / 194 |
| `reflect` | **v1** | `point: Ref(1,point)`, `over: Ref(1,{point,line})` | đường đối xứng suy biến; `over` sai kind | ✅ points | 747 / 203 |
| `translate` | **v1** | `point`, `vector: NumberSpec(2)`*, `from`*, `to`* | dùng cả hai cách; vector không hữu hạn | ✅ points | 755 / 221 |
| `point_polar` | **v1** | `from: Ref(1,point)`, `distance: float`, `angle: float`, `ref`* | `distance ≤ 0`; `ref` trùng `from` | ✅ points | 768 / 243 |
| `intersection` | cả hai | `objects: Ref(2, any)`, `select`*, `exclude`* | không có giao điểm | ✅ points | 776 / 259 |
| `segment` | cả hai | `points: Ref(2, point)` | hai điểm trùng nhau | ✅ lines | 788 / 273 |
| `line` | cả hai | `points: Ref(2, point)` | hai điểm trùng nhau | ⚠️ lines — **vẽ như đoạn**, §B.4 | 796 / 273 |
| `ray` | cả hai | `points: Ref(2, point)` | hai điểm trùng nhau | ⚠️ lines — **vẽ như đoạn**, §B.4 | 804 / 273 |
| `perpendicular` | cả hai | `line: Ref(1,line)`, `through: Ref(1,point)` | đường gốc suy biến | ⚠️ lines — **vẽ như đoạn cụt**, §B.4 | 812 / 283 |
| `parallel` | cả hai | `line`, `through` | đường gốc suy biến | ⚠️ như trên | 820 / 283 |
| `bisector` | **v1** | `points: Ref(3, point)` | cạnh dài 0; hai cạnh là tia đối | ⚠️ như trên | 828 / 297 |
| `tangent` | cả hai | `circle: Ref(1,circle)`, `point: Ref(1,point)` | điểm không nằm trên đường tròn; bán kính suy biến | ⚠️ như trên | 836 / 315 |
| `circle` | cả hai | `center`, `through: Ref(1,point)` | bán kính ≤ EPS | ✅ circles | 844 / 330 |
| `circle_radius` | cả hai | `center: Ref(1,point)`, `radius: float` | bán kính ≤ EPS | ✅ circles | 852 / 339 |
| `circle_by_diameter` | cả hai | `points: Ref(2, point)` | hai đầu trùng nhau | ✅ circles | 860 / 351 |
| `circumcircle` | cả hai | `points: Ref(3, point)` | 3 điểm thẳng hàng; bán kính ≤ EPS | ✅ circles | 868 / 361 |
| `incircle` | **v1** | `points: Ref(3, point)` | 3 điểm thẳng hàng; bán kính ≤ EPS | ✅ circles | 876 / 378 |
| `center_of` | **v1** | `circle: Ref(1, circle)` | **không có** | ✅ points | 884 / 397 |
| `polygon` | cả hai | `points: Ref(≥3, point)` | các điểm thẳng hàng | ⚠️ `svg.py:119` — **`stroke="none"`, chỉ tô nền** | 892 / 401 |
| `angle` | cả hai | `points: Ref(3, point)` | **không có** (`_eval_marker_noop`) | ✅ `svg.py:124` — cung cam, **không có số đo** | 900 / 413 |
| `arc` | **v1** | `points: Ref(3, point)` = `[O, A, B]` | **không có** (`_eval_marker_noop`) | ✅ `svg.py:135` — quét CCW A→B | 908 / 413 |

`*` = arg tuỳ chọn, theo `normalize.py:11–18 _OPTIONAL_ARGS` (6 mục — đây là **ngoại lệ duy nhất** của luật validate đồng nhất).

### v1 — `COMPOSITES` (13, `registry.py:924–1046`) — **FE không bao giờ thấy**

`equilateral_triangle` (919) · `square` (928) · `rectangle` (937) · `rhombus` (946) · `parallelogram` (955) · `regular_polygon` (964) · `triangle_sss` (973) · `triangle_sas` (988) · `right_triangle` (1003) · `isosceles_triangle` (1012) · **`perpendicular_bisector` (1021)** · **`tangent_from_point` (1030)** · `triangle` (1039).

`normalize.py:106` khai triển chúng **trước** khi build `object_types` và trước mọi validate arg → spec tới FE chỉ còn base primitive. Q6 loại chúng khỏi editor.

### v2 — `_SUPPORTED_TYPES` (21, `geometry_spec.py:16–38`)

| Object type | Có ở v1? | Args (trường **phẳng**, không có `args`) | Rule verify | Dòng |
|---|---|---|---|---|
| `point` | ✅ | `coords: [x,y]` | coords hữu hạn (`:583` `_coord`) | 17 |
| `midpoint` | ✅ | `points: [2]` | không có | 18 |
| `point_on_segment` | ✅ | `points: [2]`, `ratio` | `ratio ∉ [0,1]` (`:634`) | 19 |
| **`point_on_circle`** | ❌ **v2-only** | `circle`, `angle` (độ) | `angle` phải hữu hạn (`:642`) | 20 |
| `projection` | ✅ | `point`, `line` | đường suy biến (`:451`) | 21 |
| **`circumcenter`** | ❌ **v2-only** | `points: [3]` | 3 điểm thẳng hàng (`:457`) | 22 |
| `segment` / `line` / `ray` | ✅ | `points: [2]` (+ alias `a`/`b`, `p1`/`p2`, `from`/`to` — `:617`) | **không có** ⚠️ | 23–25 |
| `circle` | ✅ | `center`, `through` | **không có** ⚠️ | 26 |
| `circle_radius` | ✅ | `center`, `radius` | `radius ≤ 0` (`:507`, `:650`) | 27 |
| `circle_by_diameter` | ✅ | `points: [2]` | **không có** ⚠️ | 28 |
| `circumcircle` | ✅ | `points: [3]` (+ alias `a`/`b`/`c` — `:623`) | 3 điểm thẳng hàng (`:517`) | 29 |
| `perpendicular` / `parallel` | ✅ | `line`, `through` | đường gốc suy biến (`:477`) | 30–31 |
| **`tangent_at_point`** | ❌ **v2-only** *(cùng nhánh với `tangent`)* | `circle`, `point` | điểm không trên đường tròn (`:484`); bán kính suy biến (`:488`) | 32 |
| **`common_external_tangent`** | ❌ **v2-only** | `circles: [2]`, `side: upper\|lower` | không dựng được (`:498`); `side` sai (`:655`) | 33 |
| `intersection` | ✅ | `objects: [2]`, `select`/`index`, `exclude` | không có giao (`:523`); quá gần điểm loại trừ (`:529`); hai nghiệm quá gần (`:533`) | 34 |
| `polygon` | ✅ | `points: [≥3]` | **không có** ⚠️ | 35 |
| `angle` | ✅ | `points: [3]` | không reject, **nhưng tự sửa**: hoán vị đỉnh để tìm góc vuông, đảo chiều nếu cross<0, đặt `style.type='square'` cho góc vuông (`:693–736`) | 36 |
| `tangent` | ✅ | `circle`, `point` | như `tangent_at_point` | 37 |

## B.2 Object type **không có rule verify suy biến nào** — rủi ro cần cảnh báo

Prompt §B.3 yêu cầu liệt kê riêng. **Không tự thêm rule** — `README.md:7` chốt: *"The verifier must stay semantic-intent agnostic. It checks object validity and degeneracy, not whether a user meant 'regular', 'square', or 'isosceles'."*

**v1 — 4 type:**

| Type | Vì sao không có rule | Đánh giá rủi ro |
|---|---|---|
| `midpoint` | Trung điểm hai điểm trùng nhau **vẫn hợp lệ** về mặt toán | 🟢 Thấp — không có trạng thái suy biến thật |
| `rotate` | Quay quanh chính nó (point ≡ center) cho ra chính nó | 🟡 Trung bình — chọn nhầm tâm ≡ điểm thì được một điểm chồng lên, không có cảnh báo |
| `center_of` | Đường tròn cha **đã** được `_add_circle` (`:114`) kiểm bán kính > EPS | 🟢 Thấp — cha đã bảo vệ |
| `angle`, `arc` | `_eval_marker_noop` (`:413`) — chú thích ghi rõ: *"visual markers on already-validated points; no numeric constraint in v1"* | 🟡 Trung bình — `arc` với O ≡ A cho bán kính 0; `svg.py:138` chặn `radius > 0` nên **không vỡ render**, chỉ không vẽ gì |

**v2 — 6 type (nghiêm trọng hơn, §B.5):** `segment`, `line`, `ray`, `circle`, `circle_by_diameter`, `polygon`.

## B.3 `normalize.py` — luật có đồng nhất không?

**Có, gần như hoàn toàn đồng nhất.** `normalize_geometry_spec` (`:64`) áp một đường cho **mọi** type:

1. Validate `id` theo `_ID_RE` (`:9`, `:88`).
2. Lọc `style` theo `_STYLE_FIELDS` (`:10`, `:95`).
3. `draggable` mặc định = `type ∈ {point, glider}` (`:103`).
4. **Khai triển composite** (`:106`) — trước mọi validate arg.
5. Bắt trùng id (`:112`).
6. Validate arg: thừa (`:129`), thiếu (`:137`), sai arity ref (`:155/166`), ref không tồn tại (`:180`), **sai kind** (`:189`).
7. Topological sort, bắt chu trình (`:207–221`).

**Ba ngoại lệ duy nhất**, tất cả đều khai báo tường minh:
- `_OPTIONAL_ARGS` (`:11–18`) — 6 cặp `(type, arg)` được phép thiếu.
- Composite được khai triển thay vì validate trực tiếp (`:106`).
- Object có type ngoài `PRIMITIVES` bị `continue` sau khi ghi issue `primitive` (`:127`) — không validate tiếp.

→ **Xác nhận B5 của đặc tả BE:** một object primitive mới trong spec **đầy đủ** đi qua đúng đường validate id/args/style → khai triển composite → topo sort, không có nhánh đặc biệt nào. Đúng như dự đoán; không cần sửa `normalize.py`.

## B.4 `svg.py` — object nào **không** vẽ được?

**Câu trả lời ngắn: không có object type nào thiếu nhánh vẽ.** Nhưng lý do quan trọng hơn con số.

`svg.py` **không dispatch theo `type`.** Nó vẽ theo **kind**, đọc từ `verified.values` mà verifier đã tính:

| Vòng lặp | Nguồn | Vẽ ra | Dòng |
|---|---|---|---|
| lines | `values.lines` (mọi type `produces=LINE`) | `<line>` | 91–99 |
| circles | `values.circles` (mọi `produces=CIRCLE`) | `<circle fill="none">` | 100–109 |
| markers | duyệt `spec['objects']`, **chỉ 3 type**: `polygon`/`angle`/`arc` | `<polygon>` / `<polyline>` | 110–145 |
| points | `values.points` (mọi `produces=POINT`) | `<circle class="point" r="4">` + `<text>` nhãn | 147–160 |

→ **Hệ quả kiến trúc quan trọng cho bất kỳ primitive mới nào sau này:** một primitive mới sinh ra point/line/circle **được vẽ miễn phí**, không cần đụng `svg.py`. Một primitive **marker** mới (hình quạt, vector có mũi tên, nhãn số đo) **bắt buộc** phải thêm nhánh vào `svg.py:110–145`, vì `object_type not in {'polygon','angle','arc'}` sẽ `continue` (`:114`) — **im lặng, không lỗi, không vẽ gì**.

**Ba khoảng trống render thật (không phải "thiếu nhánh", mà là "nhánh vẽ sai kỳ vọng"):**

1. **`line` và `ray` vẽ như `segment`.** `_eval_two_point_line` (`:273`) lưu đúng hai điểm định nghĩa; `svg.py:96` vẽ `<line>` giữa hai điểm đó. Đường thẳng vô hạn và tia đều thành đoạn.
2. **`perpendicular` / `parallel` / `bisector` / `tangent` vẽ thành đoạn cụt độ dài tuỳ tiện.** Điểm thứ hai được lưu là `through + direction` với `direction` có độ lớn **bất kỳ**: bằng vector chỉ phương của đường gốc (`:294`), tổng hai vector đơn vị nên ≤ 2 (`:311`), hoặc đúng bằng bán kính (`:327`). Không có bước clip theo `boundingBox`.
3. **`polygon` không có cạnh** — `stroke="none"` (`svg.py:122`).

Cả ba đều là biểu hiện của *"chênh lệch giữa preview board JSXGraph và ảnh SVG server render"* mà **cả hai đặc tả đã ghi rõ là ngoài phạm vi** (BE: *"cải tiến độc lập của `svg.py`"*; FE: *"Chênh lệch này **đã tồn tại từ trước**"*). Ghi nhận, **không đề xuất giải pháp** theo §B.4 của prompt. Nhưng cần biết: đưa `tangent` lên lưới icon (§A.7) sẽ khiến người dùng tạo nhiều `tangent` hơn, và mỗi cái ra một gạch ngắn trong ảnh xuất.

## B.5 Bất đối xứng v1 ↔ v2 — **ngoài 3 case đã biết trong DoD**

DoD của đặc tả BE ghi nhận v2 chỉ từ chối `circle_radius<=0`, circumcenter/circumcircle thẳng hàng, tangent lệch đường tròn. **Đọc `_validate_concrete_geometry` (`geometry_spec.py:399–547`) cho thấy v2 phủ rộng hơn thế**, nhưng vẫn hụt so với v1 ở 5 chỗ.

**v2 phủ nhiều hơn DoD mô tả — 6 rule nữa:**

| Rule | Dòng |
|---|---|
| `projection` dùng đường suy biến | 451 |
| `perpendicular`/`parallel` có đường gốc suy biến | 477 |
| `tangent` bán kính suy biến (điểm ≡ tâm) | 488 |
| `common_external_tangent` không dựng được | 498 |
| `intersection` không có giao điểm | 523 |
| `intersection` nghiệm quá gần điểm loại trừ / hai nghiệm quá gần (ngưỡng 0.45) | 529, 533 |

**v1 chặt hơn v2 — 5 trường hợp v2 KHÔNG phủ (phần bổ sung mới):**

| Trường hợp suy biến | v1 reject tại | v2 |
|---|---|---|
| `segment`/`line`/`ray` có **hai điểm trùng nhau** | `registry.py:278` `"line points coincide"` | ❌ `geometry_spec.py:470` gán thẳng `lines[id] = (P, P)` — **không kiểm** |
| `circle` có **center ≡ through** (bán kính 0) | `registry.py:122` qua `_add_circle` (`radius ≤ EPS`) | ❌ `:503` gán `circles[id] = (center, 0.0)` — **không kiểm** |
| `circle_by_diameter` có **hai đầu trùng nhau** | `registry.py:355` qua `_add_circle` | ❌ `:512` bán kính 0.0 — **không kiểm** |
| `circumcircle` có **bán kính ≤ 0** | `registry.py:371` qua `_add_circle` | ❌ chỉ kiểm thẳng hàng (`:517`), không kiểm bán kính |
| `polygon` có **các điểm thẳng hàng** | `registry.py:410` (shoelace ≤ EPS) | ❌ `_validate_concrete_geometry` **không có nhánh `polygon`** |

*(Các type `point_polar`, `glider`, `incircle`, `reflect`, `rotate`, `translate`, `bisector`, `center_of`, `arc` không so được — chúng không tồn tại ở v2.)*

**Bất đối xứng theo chiều ngược lại (v2 khác hẳn v1):**

- v2 **tự sửa** `angle`: hoán vị 3 điểm để tìm góc vuông, đảo chiều nếu `cross < 0`, ép `style.type='square'` và `withLabel=False` (`:693–736`). v1 để nguyên (`_eval_marker_noop`). → **cùng một spec `angle` cho ra hai kết quả khác nhau ở hai stack.**
- v2 **ép ẩn mặc định** `line`/`ray`/`perpendicular`/`parallel` khi không khai báo `visible` (`:608–614`). v1 không.
- v2 **tự đổi tên id trùng** thành `id_2`, `id_3`… (`:591–597`) và rewrite mọi ref theo `id_map` (`:659–672`). v1 **báo lỗi** `duplicate_id` (`:112`).
- v2 chấp nhận **alias tên trường** (`a`/`b`, `p1`/`p2`, `from`/`to`, `point1`/`point2`) cho `segment`/`line`/`ray`/`circumcircle` (`:617–632`). v1 không.
- v2 ném **exception dừng ngay ở lỗi đầu tiên** (`GeometrySpecError`); v1 **gom toàn bộ issue** rồi trả danh sách (`NormalizedGeometry.issues`). → thông báo lỗi tiếng Việt hiện lên panel FE (F5) sẽ **đầy đủ ở v1, chỉ có một dòng ở v2**.

**Ghi nhận, không tự làm:** nếu sau này thêm công cụ mới ở v2, ba trường hợp `segment`/`circle`/`circle_by_diameter` trùng điểm là lỗ hổng verify **đã tồn tại**, không do công cụ mới gây ra — nhưng lưới icon làm việc "bấm nhầm hai lần vào cùng một điểm" dễ xảy ra hơn hẳn so với nút chữ.

## B.6 Xác nhận "verifier trung lập với ý định ngữ nghĩa"

`services/geometry/README.md:7` (nguyên văn):

> *"The verifier must stay semantic-intent agnostic. It checks object validity and degeneracy, not whether a user meant 'regular', 'square', or 'isosceles'. Intent-aware checks belong only in the eval oracle and live harness."*

**Cách đọc đúng, cho các mục ở §B.2:** "không có rule reject" ở đây là **cố tình cho phép** khi trạng thái đó vẫn là một object hợp lệ về mặt toán (`midpoint` của hai điểm trùng nhau), và là **khoảng trống thật** khi trạng thái đó làm object mất định nghĩa (`segment` hai điểm trùng nhau ở v2 → không có phương). Phân biệt: rule *degeneracy* (được phép có) khác rule *intent* (bị cấm). Năm mục ở §B.5 đều thuộc loại **degeneracy**, tức việc v1 có mà v2 không **không** mâu thuẫn với nguyên tắc này — nó chỉ là v2 kiểm ít hơn.

## B.7 Cơ chế test đồng bộ BE ↔ FE bảo vệ cái gì (và không bảo vệ cái gì)

Prompt §B.2 yêu cầu dùng hai test này để đối chiếu chéo. Kết quả đọc code:

```python
# tests/test_geometry_frontend_contract.py — toàn bộ file, 16 dòng
_DOC = Path(__file__).resolve().parents[3] / 'docs' / 'GEOMETRY_SPEC.md'

def test_frontend_contract_documents_every_primitive_and_arg():
    text = _DOC.read_text(encoding='utf-8')
    for name, primitive in {**PRIMITIVES, **COMPOSITES}.items():
        assert name in text
        for arg_name in primitive.args:
            assert arg_name in text
```

**Nó kiểm `docs/GEOMETRY_SPEC.md`, KHÔNG kiểm `registry.ts` của FE.** Đây là test **substring trên một file markdown**, cùng repo backend. Ba hệ quả:

1. Nếu thêm primitive vào `registry.py` mà quên cập nhật `GEOMETRY_SPEC.md` → **đỏ**. Tốt.
2. Nếu `frontend/.../geometry/registry.ts` hoặc `types.ts` lệch khỏi `registry.py` → **vẫn xanh**. Không có test nào bắc cầu hai repo.
3. Vì là `assert name in text` (substring), một arg tên `points` sẽ pass nhờ **bất kỳ** chỗ nào trong file có chuỗi `points` — độ nhạy thấp.

**Đối chiếu chéo thủ công đã làm trong nghiên cứu này:** `frontend/.../geometry/registry.ts` có nhánh `case` cho **đủ 26** type v1 (`:127–306`), `types.ts:6–32` liệt kê **đủ 26**. → **hiện tại không lệch.** Nhưng nó không lệch nhờ con người, không nhờ test. Và nó **thiếu 4 type v2** (§A.7) — đây không phải "lệch" theo nghĩa hồi quy, vì `registry.ts` tự mô tả là mirror của **v1**; nhưng nó là lý do kỹ thuật khiến mục DoD FE không tick được.

**Chỉ ghi nhận, không sửa** theo §B.4 của prompt.

---

# Tổng kết cho người ra quyết định

**Làm được ngay, không cần duyệt gì thêm (§A.7):**
- Chuyển `add-object-toolbar.tsx` sang lưới icon phân nhóm — pattern icon đã có sẵn trong repo (`editor-toolbar-icons.tsx`), không thêm dependency, không chạm nguyên tắc 6 (§A.6).
- Thêm **4 entry** vào `creation.ts`: `circumcircle`, `tangent`, `circle_by_diameter`, `point_on_segment` — có ở **cả hai** stack, verify đầy đủ, render đúng.
- Tách `partial/board-frame.tsx` + `partial/tool-palette.tsx` + `partial/tool-icons.tsx`; `index.tsx` (đang **168 dòng, vượt ngân sách ≤150**) co lại dưới trần.

**Cần chốt trước khi code (§A.3):** ① có đưa `reflect`/`rotate`/`translate` lên không, dù chúng chỉ biến đổi **một điểm** — ② `translate` nhập vector kiểu nào — ③ "Đường trung trực" xử lý ra sao khi `perpendicular_bisector` là **composite** mà Q6 cấm — ④ "Nửa đường tròn" và "Trung điểm/tâm" gộp hay tách — ⑤ có nới `GeometryObjectType` để thêm 4 primitive v2 không (đây là thứ đang chặn mục DoD FE còn trống).

**🛑 Dừng, cần quyết định cấp Q1–Q7 (§A.4):** Slider · Nút bấm · Checkbox · Ô nhập liệu. Bốn công cụ này đụng nguyên tắc 4 BE / 5 FE về `new Function`, có test khoá (`extensions.test.ts:120`).

**Loại khỏi phạm vi ngay, không cần cân nhắc lại (§A.2) — 20 công cụ:** toàn bộ nhóm Conic (4) · Cực trị/Nghiệm/Đường khớp (3) · Chèn ảnh · Chèn văn bản · Bút vẽ + Hình vẽ tay (2) · Quan hệ · nhóm Đo lường ở nghĩa "hiện số đo" (3) · Vector · Compa · Vị tự · Nghịch đảo qua đường tròn · Cung ngoại tiếp · Hình quạt (2). Mỗi cái đã có câu trích dẫn căn cứ trong bảng §A.2.

**Phát hiện cần task riêng (§B.4, §B.5, không phải việc của F2):**
- `polygon` render **không có cạnh** (`svg.py:122 stroke="none"`) — nút "Đa giác" đang lộ ra sẽ nổi bật hơn khi lên lưới icon.
- `line`/`ray`/`perpendicular`/`parallel`/`bisector`/`tangent` render thành **đoạn hữu hạn / đoạn cụt** trong SVG, không clip theo bbox.
- **5 trường hợp suy biến v1 chặn mà v2 không chặn** (`segment`/`line`/`ray` trùng điểm, `circle` bán kính 0, `circle_by_diameter` trùng điểm, `circumcircle` bán kính 0, `polygon` thẳng hàng) — ngoài 3 case DoD đã biết. Kèm 5 bất đối xứng hành vi khác (angle tự sửa, ẩn mặc định, đổi tên id trùng, alias trường, gom lỗi vs dừng ở lỗi đầu).
- `test_geometry_frontend_contract.py` kiểm **file markdown**, không kiểm `registry.ts` — không có lưới an toàn nào bắc cầu hai repo.

**Không có mục nào trong nghiên cứu này đề xuất sửa `registry.py` / `normalize.py` / `verifier.py` / `svg.py`.** Nơi nào một công cụ đòi primitive mới, tài liệu dừng lại và ghi nhận, đúng theo §5 và §B.4 của research prompt.
