# 02 — Đánh giá khả thi các phương án

Ba trục quyết định độc lập nhau, đánh giá riêng từng trục:
**(A)** engine của editor · **(B)** chiến lược render ảnh · **(C)** chiến lược đồng bộ dữ liệu.

---

## A. Engine của mini-editor

### A1 — JSXGraph-native constraint editor (tái dùng stack sẵn có)

Dựng editor ngay trên board JSXGraph mà `geometry/board.ts` + `geometry/registry.ts` đã tạo.
Sửa = kéo điểm tự do (JSXGraph tự lan truyền ràng buộc) + panel thuộc tính bên cạnh
(màu, nhãn, ẩn/hiện, tham số vô hướng) + xoá có kiểm tra phụ thuộc.
Serialize ngược về GeometrySpec bằng cách đọc `X()`/`Y()` của các điểm tự do.

**Ưu**
- Không thêm dependency nào — JSXGraph 1.12.2 đã trong `package.json`.
- Là engine **duy nhất** bảo toàn được đồ thị ràng buộc: kéo A thì M (midpoint của AB)
  đi theo, đường tròn ngoại tiếp co giãn theo, giao điểm tính lại — tất cả miễn phí.
- Spec sau khi sửa **vẫn là GeometrySpec hợp lệ** → agent sửa tiếp được, BE verify được,
  export PDF/DOCX/thumbnail không đổi gì.
- Tái dùng luôn `registry.ts` (317 dòng, đã có test) làm bộ dựng board.
- Bề mặt bảo mật không đổi — làm việc trên JSON, không đụng `new Function`.

**Nhược**
- Không có sẵn UI editor — phải tự viết panel, hit-testing, undo stack (~600–900 dòng FE).
- UX bị giới hạn bởi bản chất toán học: không kéo/resize được object dẫn xuất. Cần
  giải thích trong UI, nếu không người dùng sẽ tưởng là lỗi.
- JSXGraph API cho việc *xoá/tạo lại* element khá thô — nhiều khả năng phải rebuild
  cả board sau mỗi thay đổi cấu trúc (chấp nhận được ở quy mô ≤ 60 object).

### A2 — Fabric.js hoặc Konva.js / react-konva

Chuyển GeometrySpec → danh sách shape phẳng (line, circle, polygon, text), cho người dùng
kéo/resize/xoay tự do, rồi export.

**Ưu**
- UX quen thuộc, có sẵn handle resize/rotate, hit-testing, selection.
- Nhiều tài liệu, cộng đồng lớn.

**Nhược — nghiêm trọng**
- **Phá huỷ đồ thị ràng buộc.** Sau khi flatten, midpoint không còn là midpoint. Kéo A
  thì M đứng yên → hình sai về mặt toán học. Với sản phẩm dạy Toán, đây là lỗi chết người.
- **Không round-trip được.** Không có đường nào từ "danh sách shape đã bị kéo lệch" ngược
  về GeometrySpec. Nghĩa là sau lần sửa đầu tiên, agent mất khả năng chỉnh hình đó mãi mãi
  (vi phạm Q5 ở `01-requirements.md`).
- Dependency mới ~300 KB (Fabric) hoặc ~150 KB (Konva) + `react-konva`.
- Phải tự viết lại toàn bộ renderer cho 26 primitive — trùng lặp với `registry.ts` và `svg.py`.

### A3 — tldraw SDK / Excalidraw SDK

**Ưu**: UI hoàn chỉnh nhất, đẹp, có sẵn undo/redo, multiplayer.

**Nhược**
- Mọi nhược điểm của A2 (flatten, mất round-trip) **cộng thêm**:
- Bundle rất lớn (tldraw ~1 MB+, Excalidraw ~800 KB) cho một mini-editor nhúng.
- Ngôn ngữ hình học của chúng (freehand, sticky note, arrow) lệch hẳn nhu cầu.
- **Giấy phép**: tldraw SDK dùng thương mại cần license trả phí để gỡ watermark —
  cần kiểm tra pháp lý trước khi cân nhắc.
- Design system riêng, khó hoà vào Tailwind theme hiện tại.

### A4 — Tự build trên SVG thuần

Tự viết renderer + interaction trực tiếp trên SVG, không dùng JSXGraph.

**Ưu**: kiểm soát hoàn toàn, bundle nhỏ nhất.
**Nhược**: phải tự cài đặt lại toàn bộ đại số hình học (giao điểm đường-đường tròn, tiếp tuyến,
đường tròn ngoại tiếp, lan truyền ràng buộc…) — chính là thứ `registry.py` mất 1130 dòng để làm
và JSXGraph cho không. Rủi ro sai số/suy biến rất cao. **Loại.**

### Bảng so sánh trục A

| Tiêu chí | A1 JSXGraph | A2 Fabric/Konva | A3 tldraw/Excalidraw | A4 SVG thuần |
|---|---|---|---|---|
| Bảo toàn ràng buộc | ✅ Đầy đủ | ❌ Mất | ❌ Mất | ⚠️ Tự làm |
| Round-trip về spec (agent sửa tiếp) | ✅ | ❌ | ❌ | ⚠️ |
| Dependency mới | Không | +150–300 KB | +800 KB–1 MB | Không |
| Tái dùng code sẵn có | Cao (`registry.ts`) | Không | Không | Không |
| Tương thích BE verifier | ✅ Nguyên vẹn | ❌ Phải bỏ | ❌ Phải bỏ | ⚠️ |
| Công sức UI | Trung bình–cao | Thấp | Rất thấp | Rất cao |
| Công sức tổng | **Trung bình** | Cao | Cao | Rất cao |
| Chi phí bảo trì | Thấp | Cao (2 mô hình dữ liệu) | Cao | Rất cao |
| Rủi ro pháp lý | Không | Không | ⚠️ Cần kiểm tra | Không |
| Hiệu năng @60 object | Tốt | Tốt | Tốt | — |

**Kết luận trục A: A1.** A2/A3 tiết kiệm công UI nhưng phải trả bằng chính thứ làm nên giá trị
của hệ thống — tính đúng đắn hình học và khả năng agent chỉnh sửa tiếp.

---

## B. Chiến lược render ảnh khi Save

### B1 — Render ở server từ spec (tái dùng `render_geometry_svg` / `render_jsxgraph_fallback`)

**Ưu**
- Deterministic: mọi client cho ra **cùng một** ảnh; không phụ thuộc font/trình duyệt.
- Tái dùng nguyên code đang chạy — `svg.py` đã cẩn thận về letterboxing, nhãn trùng, arc sweep.
- BE **verify trước khi render** → không bao giờ lưu được hình suy biến.
- Không nhận bitmap từ client → không có bề mặt upload tuỳ ý.
- `content_hash` tính ở server, dùng luôn làm token chống xung đột.

**Nhược**
- Thêm một round-trip mạng khi Save (chấp nhận được, mục tiêu < 1.5 s).
- SVG server render đơn giản hơn board JSXGraph (không vẽ nhãn cạnh, không tô nhiều màu)
  → **preview trong editor và ảnh đã lưu trông không giống hệt nhau**. Đây là chênh lệch
  *đã tồn tại từ trước*, không phải do phương án này gây ra, nhưng editor sẽ làm nó lộ rõ hơn.
  Cần xử lý: xem "Rủi ro R2" bên dưới.

### B2 — Export ở client (`canvas.toDataURL` / `toBlob` từ board JSXGraph)

**Ưu**: ảnh khớp 100% với cái người dùng vừa thấy; không cần round-trip.

**Nhược**
- Font/anti-aliasing khác nhau giữa các máy → cùng một hình, hai người export ra hai file khác nhau.
- Phải upload bitmap lên server → mở bề mặt nhận file tuỳ ý, cần validate.
- Bỏ qua verifier — client có thể lưu hình suy biến.
- Payload lớn hơn nhiều (PNG 640×420 ≈ 30–80 KB vs SVG ≈ 3–8 KB).
- Mất tính vector khi in/PDF.

### B3 — Headless browser ở server (Puppeteer/Playwright chạy JSXGraph thật)

**Ưu**: ảnh khớp chính xác board FE, vẫn deterministic.
**Nhược**: thêm Chromium vào hạ tầng (~400 MB image, RAM cao), thời gian khởi động lâu,
một dịch vụ nữa phải vận hành. **Quá nặng cho nhu cầu này** — chỉ đáng cân nhắc nếu sau
này chênh lệch preview/ảnh trở thành vấn đề thật sự.

**Kết luận trục B: B1**, và tách riêng việc thu hẹp chênh lệch preview↔SVG như một
cải tiến độc lập của `svg.py`.

---

## C. Chiến lược đồng bộ dữ liệu

| | C1 — Giữ spec + ảnh (hiện tại) | C2 — Chỉ lưu ảnh sau khi sửa |
|---|---|---|
| Agent sửa tiếp được | ✅ | ❌ Vĩnh viễn mất |
| Export PDF/DOCX | ✅ Không đổi | ✅ |
| Mở lại editor lần 2 | ✅ | ❌ |
| Dung lượng lưu | spec JSON ~2–6 KB thêm | Ít hơn chút |
| Thay đổi hạ tầng | Không | Phải gỡ figure node khỏi HTML |
| Phù hợp yêu cầu "chốt thành ảnh" | ✅ (ảnh SVG chính là bản chốt) | ✅ |

**Kết luận trục C: C1.** Chi phí thêm gần như bằng 0 vì hệ thống *đã* lưu cả hai; C2 chỉ có
ý nghĩa nếu anh chủ động muốn đóng băng hình (câu Q1(b) ở `01-requirements.md`).

---

## Rủi ro & giới hạn kỹ thuật của phương án được chọn (A1 + B1 + C1)

| # | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| R1 | Hai định dạng spec v1/v2 → editor phải viết 2 adapter | **Cao** | Một `TEditorSpec` trung gian trong editor; adapter v1↔ và v2↔ tách riêng, mỗi cái có test. Không hợp nhất format ở phase này |
| R2 | Preview (board JSXGraph) ≠ ảnh SVG đã lưu | Trung bình | Hiện rõ ảnh SVG thật sau khi Save; về lâu dài cải tiến `svg.py`. **Không** dùng đây làm lý do chuyển sang B2 |
| R3 | Figure `jsxgraph` cũ không có `math_figure_spec` | Trung bình | Mở chế độ chỉ-xem + thông báo rõ. Không parse ngược JS |
| R4 | Kéo điểm tạo ra hình suy biến (3 điểm thẳng hàng khi cần tam giác) | Trung bình | BE verify khi Save và **từ chối** kèm thông báo tiếng Việt; FE cảnh báo sớm bằng cách chạy verify nhẹ ở client trước |
| R5 | Người dùng kỳ vọng kéo được midpoint | Trung bình | UX: điểm dẫn xuất vẽ khác (rỗng/xám), click vào thì panel giải thích phụ thuộc |
| R6 | Xung đột khi hai tab/hai người cùng sửa | Thấp | Optimistic lock bằng `content_hash`, 409 khi lệch |
| R7 | Sửa tay xong agent ghi đè ở lượt sau | Thấp | Đúng như thiết kế — agent đọc spec mới từ metadata nên nó *biết* bản đã sửa |
| R8 | Chat chưa có chỗ lưu asset | **Cao** | Chặn P1 cho tới khi chốt Q3. P0 (tài liệu) không bị ảnh hưởng |
| R9 | Vượt giới hạn 300 dòng/file của CONVENTION | Thấp | Chia sẵn theo `partial/` ngay từ đầu — xem `03-recommended-architecture.md` |
