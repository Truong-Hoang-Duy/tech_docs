# Sổ tay Thao tác Chat Hằng ngày (Bật file này khi làm việc)

> **📌 Cách dùng:** Mở cố định file này ở một tab trong IDE. Khi bắt đầu tìm hiểu hoặc làm bất kỳ chức năng nào, chỉ cần đi từ trên xuống dưới, copy khối lệnh tương ứng dán vào khung chat của **Gemini** hoặc **Claude**.
> *(File này dành riêng cho bạn thao tác chat, không liệt kê trong `README.md`).*

---

## 0. Chọn kịch bản nào trước khi bắt đầu?

| Bạn đang muốn làm gì? | Đi tới mục | Nên chọn ai khởi đầu (Agent 1)? |
|---|---|---|
| **Chỉ mới tìm hiểu / khám phá** xem một chức năng trong hệ thống đang chạy ra sao (chưa sửa gì) | **Mục I** | **Gemini** (đọc rộng cả FE + BE nhanh, giải thích dễ hiểu) |
| **Làm tính năng mới / Sửa lỗi lớn** (đụng nhiều file, đổi logic phức tạp, hoặc chạm cả BE + FE) | **Mục II** *(Quy trình Chuẩn)* | - Đụng rộng BE + FE / UI: **Gemini lập ➔ Claude duyệt**<br>- Đụng sâu logic BE / DB: **Claude lập ➔ Gemini duyệt** |
| **Sửa bug nhỏ / Chỉnh sửa nhanh** (≤ 3 file, đã rõ triệu chứng) | **Mục III** *(Fast-Track)* | Ai đang rảnh hạn mức hơn làm **Agent 1**, người kia duyệt & chạy luôn |

---

## I. Khi bắt đầu TÌM HIỂU một chức năng có sẵn (Chưa biết nằm đâu)

Khi bạn muốn nắm một chức năng trong dự án đang hoạt động thế nào, có lỗi ngầm gì không trước khi quyết định làm:

### Bước 1: Nhờ Agent 1 (nên dùng Gemini) kéo code mới nhất và khảo sát trong chat
Copy dán vào **Gemini** (hoặc **Claude**):

```text
Tôi đang muốn tìm hiểu chức năng: "<mô tả chức năng bằng lời thường, VD: tạo câu hỏi từ file PDF / xuất giáo án / gợi ý sửa trên Canvas>".
Trước tiên, hãy kéo mã nguồn mới nhất từ nhánh chính (main / dev) của backend/, frontend/ và tech_docs/ về máy.
Chưa tạo hay sửa file nào cả. Sau khi đã cập nhật code mới nhất, hãy khảo sát code thực tế ở cả frontend/ và backend/ rồi trả lời trực tiếp trong chat:
1. Luồng hoạt động từ lúc người dùng bấm trên giao diện (FE) -> gọi API nào -> xử lý ở hàm nào dưới BE -> lưu vào bảng DB nào (kèm file:line cụ thể).
2. Có cờ (feature flag) hay điều kiện phân quyền nào đang khoá chức năng này không?
3. Những giới hạn hiện tại hoặc điểm dễ gây lỗi của luồng này là gì?
Giải thích ngắn gọn, rõ ràng, dễ hiểu.
```

### Bước 2 (Tuỳ chọn): Nhờ Agent 2 kiểm chứng lại nếu muốn đào sâu
Nếu đọc xong Bước 1 bạn muốn bắt tay vào nâng cấp hoặc sửa lỗi cho chức năng đó, chuyển thẳng xuống **Mục II (Bước 1)** bên dưới.

---

## II. Quy trình Chuẩn: Làm Tính năng mới / Sửa lỗi lớn (6 Bước từ A → Z)

> **Quy ước gọi tên dưới đây:**
> - **Agent 1 (Người lập):** AI bạn chọn để Phân tích & viết Plan (VD: **Gemini**).
> - **Agent 2 (Người duyệt):** AI đối diện sẽ Duyệt Plan đó (VD: **Claude**).
> *(Bạn hoàn toàn có thể đảo ngược: **Agent 1 = Claude**, **Agent 2 = Gemini** — câu lệnh giữ nguyên).*

---

### 🔹 BƯỚC 1: Kéo code mới nhất & Phân tích hiện trạng (`01-analysis.md`)

**1. Mở khung chat của `Agent 1`, dán câu này:**
*(Bạn có thể tự đặt `<slug>` chỉ 2–3 từ tiếng Anh như `canvas-page-scroll`, hoặc để AI tự đặt — quy tắc tại `3_git-and-conventions.md` §4)*

```text
Đọc tech_docs/rules/1_workflow.md (§2.1) và tech_docs/rules/2_templates.md (§1).
Bước đầu tiên bắt buộc: Hãy kéo mã nguồn mới nhất từ nhánh chính (main / dev) của backend/, frontend/ và tech_docs/ về local.
Sau khi code đã mới nhất, hãy khảo sát code thực tế trong repo và tạo file phân tích tại tech_docs/plans/<slug>/01-analysis.md cho yêu cầu sau:

<Gõ mô tả yêu cầu hoặc triệu chứng lỗi của bạn vào đây bằng lời thường>
```

**2. Sau khi `Agent 1` tạo xong `01-analysis.md`, bạn chỉ cần mở file đó xem 2 mục:**
- **Mục 1 (Mục tiêu & Phạm vi)** và **Mục 4 (Phương án Đề xuất)**: Xem hướng giải quyết đã đúng ý bạn chưa.
- **Mục 5 (Câu hỏi cần chốt)**: Nếu AI có hỏi lại, bạn trả lời thẳng trong chat:
  ```text
  Chốt theo phương án <A/B>. Về câu hỏi ở mục 5: <câu trả lời của bạn>.
  Hãy cập nhật lại 01-analysis.md cho khớp.
  ```
- *(Mẹo: Nếu đọc `01-analysis.md` thấy khó hiểu thuật ngữ, mở `Agent 2` gõ: `"Đọc tech_docs/plans/<slug>/01-analysis.md và giải thích lại bằng lời đời thường cho tôi hiểu 2 phương án trong đó khác nhau thế nào"`).*

---

### 🔹 BƯỚC 2: Lập Kế hoạch chi tiết (`02-plan.md`)

Khi đã ưng ý với `01-analysis.md`, **gõ tiếp vào khung chat của `Agent 1`:**

```text
Đọc tech_docs/plans/<slug>/01-analysis.md và tech_docs/rules/2_templates.md (§2).
Hãy lập kế hoạch triển khai chi tiết từng bước vào file tech_docs/plans/<slug>/02-plan.md.
Chưa viết code tính năng, dừng lại để chuyển sang bước duyệt Plan.
```

---

### 🔹 BƯỚC 3: Duyệt Plan chéo (`Cross-Review` — Bước chặn lỗi quan trọng nhất)

Bây giờ **chuyển sang khung chat của `Agent 2`** (Nếu Gemini vừa lập Plan thì mở Claude; nếu Claude vừa lập Plan thì mở Gemini).

**1. Dán câu này vào `Agent 2`:**

```text
Đọc tech_docs/rules/1_workflow.md (§3.2) và kiểm duyệt chéo kế hoạch tại tech_docs/plans/<slug>/02-plan.md (kèm 01-analysis.md).
Bắt buộc mở các file code thật trong backend/ và frontend/ để đối chiếu từng file:line, kiểm tra rủi ro, edge-case, tác động dây chuyền và độ phủ test.
Ghi kết quả (🔴 Blocker / 🟡 Should-fix / 🟢 Nit) vào mục "## 5. Nhật ký Duyệt Plan" trong 02-plan.md.
Nếu phát hiện điểm 🔴 hoặc 🟡 cần chỉnh, hãy cập nhật trực tiếp vào các Step của 02-plan.md và đổi trạng thái thành APPROVED. Chưa viết code tính năng.
```

**2. Xem kết quả:**
- `Agent 2` sẽ tự động vừa bắt lỗi, vừa vá luôn những chỗ thiếu sót trong `02-plan.md` và chốt trạng thái `APPROVED`.
- Nếu `Agent 2` phát hiện mâu thuẫn lớn về nghiệp vụ cần hỏi ý bạn, bạn chỉ cần chốt trong chat để nó cập nhật nốt `02-plan.md`.

---

### 🔹 BƯỚC 4: Chạy Plan (Viết code & Chạy test tự động)

Khi `02-plan.md` đã ở trạng thái `APPROVED`, bạn có thể giao việc viết code cho **Claude** (nếu thiên về sửa phẫu thuật chính xác) hoặc **Gemini** (nếu thiên về sửa đồng bộ nhiều file/UI).

**Dán câu này vào khung chat của Agent bạn chọn để Chạy Plan:**

```text
Đọc tech_docs/rules/1_workflow.md (§4.1) và tech_docs/rules/3_git-and-conventions.md.
Hãy triển khai code đúng theo kế hoạch đã chốt tại tech_docs/plans/<slug>/02-plan.md.
Làm xong Step nào thì chạy lệnh kiểm tra (ruff / pytest / build) và tick [x] trực tiếp vào 02-plan.md, đồng thời ghi tóm tắt kết quả vào mục "## 6. Nhật ký Thực thi". Không tự ý commit.
```

> **Tình huống phát sinh khi đang chạy Plan:**
> Nếu Agent đang code mà dừng lại hỏi bạn vì gặp ràng buộc mới, chỉ cần trả lời lựa chọn của bạn và dặn:
> `"Làm theo hướng <X>, nhớ ghi lại vào mục Quyết định phát sinh trong 02-plan.md rồi chạy tiếp các Step còn lại."`

---

### 🔹 BƯỚC 5: Nghiệm thu Code chéo (`Cross-Verify`) & Kiểm tay

Sau khi Agent ở Bước 4 báo đã chạy xong hết các Step:

**1. Chuyển sang khung chat của `Agent đối diện` (người KHÔNG viết code ở Bước 4), dán câu này:**

```text
Đọc tech_docs/rules/1_workflow.md (§4.2) và tech_docs/plans/<slug>/02-plan.md.
Hãy kiểm tra độc lập bằng cách chạy git status / git diff, đối chiếu từng thay đổi với 02-plan.md, chạy lại các lệnh test/lint và ghi kết luận vào mục "## 7. Kết quả Nghiệm thu Code" của 02-plan.md.
Nếu có mục (kiểm tay) cho người dùng, hãy hướng dẫn ngắn gọn các bước để tôi bấm thử trên màn hình.
```

**2. Bạn bấm thử trên màn hình (nếu có mục `kiểm tay`):**
- **Nếu chạy mượt hết:** Báo `"Các mục kiểm tay đã ĐẠT, hãy tick [x] nốt vào 02-plan.md"` rồi chuyển sang Bước 6.
- **Nếu bấm thử thấy lỗi:** Mô tả hiện tượng mắt thấy (kèm lỗi trong tab Network/Console nếu có) vào khung chat:
  ```text
  Khi tôi kiểm tay thì gặp lỗi sau:
  - Thao tác: <bấm vào đâu>
  - Thực tế thấy: <hiện tượng lỗi / mã lỗi>
  Hãy kiểm tra nguyên nhân, cập nhật vào 02-plan.md và sửa dứt điểm.
  ```

---

### 🔹 BƯỚC 6: Commit & Push (Hoàn tất)

Khi mọi mục trong `02-plan.md` đã `[x]` và kết luận là `VERIFIED`, dán một trong hai câu sau:

**Chỉ Commit ở máy local (chưa đẩy lên remote):**
```text
Commit (chưa push) các thay đổi của task trong tech_docs/plans/<slug>/02-plan.md, tuân thủ nghiêm ngặt tech_docs/rules/3_git-and-conventions.md (§1).
```

**Commit và Push luôn lên nhánh:**
```text
Commit và push các thay đổi của task trong tech_docs/plans/<slug>/02-plan.md, tuân thủ nghiêm ngặt tech_docs/rules/3_git-and-conventions.md (§1).
```

---

## III. Chế độ Gọn (Fast-Track): Dành cho Bug nhỏ / Sửa nhanh (≤ 3 file)

Khi gặp lỗi nhỏ, rõ ràng (VD: sửa lỗi hiển thị, thêm 1 trường nhỏ, sửa điều kiện lọc), dùng **3 câu lệnh rút gọn** này (chỉ tạo duy nhất file `02-plan.md`):

### 1. Gõ vào `Agent 1` (Kéo code mới nhất + Phân tích + Lập thẳng `02-plan.md`):
```text
Đọc tech_docs/rules/1_workflow.md (§2.2) và tech_docs/rules/2_templates.md (§2).
Trước tiên, hãy kéo mã nguồn mới nhất từ nhánh chính (main / dev) của backend/, frontend/ và tech_docs/ về local.
Sau đó khảo sát code thật và lập thẳng kế hoạch (gộp nguyên nhân gốc file:line vào mục 1) tại tech_docs/plans/<slug>/02-plan.md cho việc sau:

<Mô tả lỗi / yêu cầu nhỏ>
```

### 2. Gõ vào `Agent 2` (Duyệt Plan + Nếu ổn thì Chạy Plan luôn trong 1 lượt!):
```text
Đọc tech_docs/rules/1_workflow.md (§3.2 và §4.1) cùng tech_docs/rules/3_git-and-conventions.md.
1. Kiểm duyệt kế hoạch tại tech_docs/plans/<slug>/02-plan.md đối chiếu với code thật và ghi vào mục 5 (Nhật ký Duyệt Plan).
2. Nếu không có lỗi thiết kế lớn (hoặc sau khi bạn tự hiệu chỉnh các chi tiết nhỏ trong Plan), hãy chuyển trạng thái sang APPROVED và THỰC THI LUÔN toàn bộ các Step trong 02-plan.md, chạy test/lint và tick [x] hoàn tất. Không tự commit.
```

### 3. Quay lại `Agent 1` (Nghiệm thu `git diff` độc lập):
```text
Đọc tech_docs/rules/1_workflow.md (§4.2) và tech_docs/plans/<slug>/02-plan.md.
Hãy kiểm tra git diff và chạy lại test để nghiệm thu code do agent kia vừa thực hiện, ghi kết luận vào mục 7 của 02-plan.md.
```
*(Sau khi `VERIFIED`, dùng lệnh Commit ở Bước 6 Mục II).*

---

## IV. Câu lệnh Cứu hộ nhanh (Khi mất phiên chat hoặc đổi máy)

Nếu đang làm dở mà đóng cửa sổ chat, hết hạn mức, hoặc hôm sau mới mở máy làm tiếp, bạn chỉ cần mở **bất kỳ Agent nào (Gemini hoặc Claude)** và dán đúng 1 câu:

```text
Đọc file tech_docs/plans/<slug>/02-plan.md (và 01-analysis.md nếu có), kiểm tra git status hiện tại, rồi tóm tắt trong 5 dòng: task này đang dừng ở bước nào và việc tiếp theo cần làm ngay là gì.
```

