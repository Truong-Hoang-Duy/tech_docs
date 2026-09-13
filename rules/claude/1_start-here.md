# Bắt đầu ở đây — cách làm việc mỗi ngày

> File này là **hướng dẫn sử dụng**, đọc để biết làm gì.
> [`2_workflow-rules.md`](2_workflow-rules.md) là **luật chi tiết**, chỉ mở khi cần tra khuôn mẫu.
> [`../gemini-assist.md`](../gemini-assist.md) là chỗ tra prompt khi muốn nhờ Gemini đọc hộ cho đỡ tốn hạn mức Claude.

---

## 1. Hai nhân vật rưỡi

```text
BẠN            biết muốn gì                     không cần biết code nằm đâu
CLAUDE CODE    đọc repo, viết tài liệu, viết code — người duy nhất được GHI
GEMINI         đọc hộ, giảng lại, tra tài liệu ngoài — CHỈ ĐỌC, không ghi gì
```

Claude Code làm trọn một mạch: khảo sát → thiết kế → task doc → code. Bạn **không phải bưng file qua lại** như trước nữa.

Gemini là "nửa nhân vật": nó không tạo ra thứ gì trong repo, chỉ giúp **bạn** hiểu nhanh và giúp Claude Code khỏi phải đọc lan man. Mọi thứ Gemini nói đều là **giả thuyết cho tới khi Claude Code mở file ra xác nhận**.

Nguyên tắc chi phí: **việc đọc rộng và việc giảng giải đẩy sang Gemini; hạn mức Claude để dành cho đọc chính xác và ghi.**

## 2. Bạn đang ở tình huống nào

| Bạn đang cần | Đọc mục |
|---|---|
| Sáng mở máy, chuẩn bị làm | §3 |
| Bắt đầu một tính năng mới | §4, bước 1–6 |
| Task doc đã có, muốn bắt tay làm | §4, **bước 7** |
| Đang code, gặp câu hỏi không hiểu | §5 |
| Muốn đỡ tốn hạn mức Claude | §6 |

## 3. Mỗi sáng — 1 phút

Bản đồ dự án phải mới thì cả bạn lẫn Gemini mới hỏi trúng chỗ. Gõ vào Claude Code:

```text
Cập nhật bản đồ từ <ref> theo §3 của tech_docs/rules/claude/2_workflow-rules.md.
```

Điền `<ref>` là nhánh bạn muốn bản đồ phản ánh:

| Điền | Khi nào dùng |
|---|---|
| `origin/dev` | Muốn bản đồ theo nhánh chung của team |
| `working` | Muốn bản đồ khớp đúng thứ bạn đang sửa dở, **kể cả chưa commit** |
| `feat/abc` | Theo một nhánh cụ thể |
| *(bỏ trống)* | Dùng lại ref của lần trước |

Kết quả: hai file [`overview/1_repo-map.md`](../../overview/1_repo-map.md) và [`overview/2_backend-features-all.md`](../../overview/2_backend-features-all.md) được cập nhật, kèm vài dòng **"hôm nay đổi gì"** in ra terminal.

- Không có gì đổi → báo "không đổi" rồi dừng, gần như không tốn token.
- Có đổi → liếc qua để biết ai vừa đụng vào đâu; khi hỏi Gemini thì dán mấy dòng đó kèm theo.

## 4. Bắt đầu một tính năng mới

Ví dụ chạy thật: *"Xuất đề thi ra Word kèm đáp án"*.

### Bước 1 — Bạn viết nháp mô tả (5 phút)

Tạo **một file duy nhất**: `tech_docs/research/00-desc.md` (ngay gốc `research/`, chưa cần thư mục, chưa cần nghĩ tên tính năng).

Viết bằng lời thường, **không cần biết tên hàm hay tên bảng nào**. Lủng củng, thiếu mục, gạch đầu dòng rời rạc cũng được — bước 2 tôi dọn. Khuôn dưới đây là đích đến, không phải bài tập bắt bạn điền đủ:

```text
# 00 — Mô tả: Xuất đề thi ra Word kèm đáp án

**Phía:** chưa rõ

## Người dùng muốn gì
Giáo viên ở màn hình danh sách đề thi, bấm "Xuất Word",
tải về file .docx có đề và đáp án ở trang cuối.

## Hôm nay đang ra sao
Chỉ xuất được PDF. Muốn có Word thì phải copy thủ công.

## Không làm lần này
Không làm bản trộn nhiều mã đề.

## Chỗ tôi không chắc
Không biết xuất PDF hiện chạy bằng gì, và đáp án lưu ở đâu.
```

Dòng **Phía** ghi `chưa rõ` cũng được — Claude Code sẽ chốt là sửa BE, FE hay cả hai.
Mục **"Chỗ tôi không chắc"** không phải điểm trừ, nó là đầu vào để Claude Code đi tìm.

### Bước 2 — Tôi chuẩn hoá mô tả và đặt tên thư mục ← rẻ

```text
Đọc tech_docs/research/00-desc.md, chuẩn hoá theo §8 của
tech_docs/rules/claude/2_workflow-rules.md, tự đặt slug rồi chuyển vào đúng thư mục.
```

Tôi viết lại cho chuẩn chỉnh theo khuôn, tự đặt slug, tạo `tech_docs/research/<slug>/`, chuyển file vào — **rồi dừng**, in ra đường dẫn mới kèm 3 dòng "đã đổi gì so với bản nháp".

Ở bước này tôi **không đọc code**: chỉ diễn đạt lại cho rõ, không thêm yêu cầu bạn chưa nói, chỗ nào mơ hồ thì đẩy xuống mục **"Chỗ tôi không chắc"** chứ không tự đoán. Thiếu tới mức không viết nổi thì tôi hỏi tối đa 3 câu nghiệp vụ, hỏi một lượt.

**Bạn rà soát:** mở `tech_docs/research/<slug>/00-desc.md`, đọc kỹ. Sai ý thì sửa thẳng vào file hoặc bảo tôi sửa — rẻ nhất là sửa ở đây, trước khi có ai đi đọc repo. Đúng ý rồi mới sang bước 3.

### Bước 3 — Tôi viết `01-brief.md`: sắp đi tìm gì, đang tin gì ← rẻ

```text
Đọc tech_docs/research/<slug>/00-desc.md, viết 01-brief.md theo §9 của
tech_docs/rules/claude/2_workflow-rules.md, rồi chờ tôi duyệt.
```

Ở bước này tôi **vẫn chưa đọc code**. Tôi chỉ dựa trên mô tả của bạn để viết ra hai thứ:

- **Câu hỏi khảo sát** — danh sách những gì tôi sẽ đi tìm trong repo. Mỗi câu có nhãn: `[XÁC MINH]` là thứ đã có tên trong bản đồ, chỉ cần kiểm lại; `[ĐỊNH VỊ]` là thứ chưa ai biết tên, tôi phải lần ra.
- **Giả định cần kiểm chứng** — những điều tôi đang *đoán* là đúng. Đoán sai một cái ở đây thì thiết kế phía sau sai theo, nên nó được viết ra để bạn nhìn thấy.

**Vì sao có bước này:** đây là chỗ rẻ nhất để chặn việc tôi đi sai hướng. Bạn đọc xong là biết tôi sắp lục ở đâu và đang tin gì — thấy thừa, thiếu, hoặc trật thì sửa thẳng vào file hoặc bảo tôi sửa. Sai ở đây sửa mất một phút; sai sau khi khảo sát xong thì mất cả một lượt token.

**Không hiểu thuật ngữ hay không biết câu hỏi đó nhắm vào gì?** Đừng tốn lượt hỏi tôi — dán sang Gemini:

```text
[GIẢI NGHĨA — CHỈ ĐỌC]
Tôi là người ra yêu cầu, không rành kỹ thuật. Dưới đây là danh sách câu hỏi khảo sát
mà một agent sắp dùng để đọc code dự án BookForge.
Với mỗi câu: giải thích bằng lời thường nó đang muốn tìm gì và vì sao cần biết.
Cuối cùng nói câu nào theo bạn là thừa, và thiếu câu nào đáng hỏi.
Không viết code, không sửa file.

<dán nội dung 01-brief.md>
```

Gemini chỉ ra chỗ thừa/thiếu hợp lý → bảo tôi sửa `01-brief.md`, đừng tự sửa tay rồi quên mất vì sao.

### Bước 4 — Khảo sát và đọc kết quả ← tốn token nhất

```text
Đọc tech_docs/rules/claude/2_workflow-rules.md và tech_docs/research/<slug>/01-brief.md,
khảo sát repo rồi trả lời vào tech_docs/research/<slug>/02-findings.md theo §10.
```

Giờ tôi mới thật sự mở repo ra đọc. Tôi trả về `02-findings.md` gồm: **phía nào phải sửa**, tên thật của mọi thứ liên quan kèm `file:line` và trích code, **giả định nào trong brief đúng / sai**, và cái gì tôi chưa xác định được.

> **Muốn rẻ hơn:** trước khi gõ câu trên, đưa `01-brief.md` cho Gemini quét khoanh vùng (prompt ở [`../gemini-assist.md`](../gemini-assist.md) §2B), rồi dán kết quả về cho tôi kèm nhãn `[TỪ GEMINI — CHƯA KIỂM CHỨNG]`. Tôi đọc thẳng vào vùng đó thay vì mò cả repo — vẫn kiểm chứng lại từng chỗ trước khi ghi.

**Bạn rà soát findings** — đây là cửa duyệt quan trọng nhất, vì mọi thứ sau đây đều dựng trên nó. Không đọc nổi thì nhờ Gemini đọc hộ:

```text
[ĐỌC HỘ KẾT QUẢ KHẢO SÁT — CHỈ ĐỌC]
Đây là kết quả khảo sát code dự án BookForge do một agent khác viết.
1. Tóm tắt trong 5 dòng cho người không đọc code.
2. Giải nghĩa các thuật ngữ và tên kỹ thuật xuất hiện trong đó.
3. Chỉ ra chỗ nào kết luận mà không kèm bằng chứng, hoặc mâu thuẫn nhau.
4. Nêu 3 câu tôi nên hỏi lại agent đó.
Không sửa file, không viết code.

<dán nội dung 02-findings.md — hoặc chỉ đường dẫn file nếu Gemini chạy trong IDE>
```

Thấy tôi hiểu sai ý, hoặc tài liệu viết khó hiểu → nói ngay, tôi khảo sát bổ sung hoặc viết lại file. Muốn Gemini đề xuất câu chữ cụ thể thì dùng prompt §2F ở [`../gemini-assist.md`](../gemini-assist.md) — nó viết ra `<đoạn gốc> → <đoạn đề xuất>`, bạn dán về, **tôi là người ghi vào file**.

### Bước 5 — Thiết kế và tranh luận ← tốn token

```text
Đọc tech_docs/research/<slug>/02-findings.md, viết 03-design.md theo §17 của
tech_docs/rules/claude/2_workflow-rules.md, rồi chờ tôi chốt.
```

**Đây là lúc tranh luận.** Hỏi tại sao, bắt so sánh, bắt viết lại. Chỗ nào đọc không hiểu thì copy đoạn đó sang Gemini nhờ giảng (§6) — phần giảng giải để Gemini làm, đừng bắt Claude Code viết dài.

### Bước 6 — Chốt thành task doc ← tốn token

```text
Đọc tech_docs/research/<slug>/03-design.md, kiểm chứng lại trong repo, rồi viết task doc
theo docs-convention §1.2a và §5 của tech_docs/rules/claude/2_workflow-rules.md.
```

Tôi kiểm lại phương án có khả thi không, rồi viết file giao việc trong `backend/docs/tasks/`:

- Chỉ BE → một file `YYYY-MM-DD-<slug>.md`
- Chỉ FE → một file `…-frontend.md`
- Cả hai → **hai file**, mỗi file tự đứng được

**Từ task doc đó mới bắt đầu code.**

> **Task doc không được nhắc tới `tech_docs/`.** `bookforge`, `bookforge-fe`, `tech_docs` là ba repo riêng — người nhận việc chỉ có repo triển khai, không có thư mục nghiên cứu của bạn.
> Nên task doc phải **chép nội dung cần thiết vào trong nó**, không link ngược về `research/`. Đây là ràng buộc cứng, xem [`docs-convention.md`](../docs-convention.md) §3.1.

Trong task doc có mục **DoD** — danh sách điều kiện nghiệm thu. Tôi viết nó thành hai loại: mục **tự kiểm được** (có lệnh chạy + kết quả mong đợi) và mục **`(kiểm tay)`** (thứ máy không tự khẳng định được). Cách dùng nằm ở bước 7, sau khi code xong.

### Bước 7 — Giao việc: bảo Claude Code làm theo task doc

Task doc viết xong **không tự chạy**. Bạn phải giao việc bằng một câu:

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md và triển khai đúng theo tài liệu đó,
theo §16 của tech_docs/rules/claude/2_workflow-rules.md.
```

Vế `theo §16` là bắt buộc: phiên Claude Code mới tinh chỉ đọc task doc thì **không tự biết sáu luật thi công** bên dưới. Ngoài vế đó ra bạn không phải dán gì thêm — tài liệu nằm trong repo, tôi tự mở ra đọc.

Đụng cả hai phía thì **giao từng file một, không gộp**: làm BE trước cho có API thật, xong mới giao file `-frontend.md`.
Hai repo là hai thư mục làm việc khác nhau, nên mở phiên Claude Code riêng cho mỗi repo.

**Sáu luật tôi phải theo khi thi công** — bạn không cần nhắc lại, chúng nằm trong [`2_workflow-rules.md`](2_workflow-rules.md) §16; liệt kê ở đây để bạn biết đường soát:

1. **Task doc là hợp đồng.** Làm đúng phạm vi trong đó: không thêm tính năng, không refactor kèm, không "tiện tay sửa luôn".
2. **Bám "Quyết định đã chốt".** Đã chốt rồi thì không tự chọn cách khác, kể cả khi thấy cách khác hay hơn — muốn đổi thì hỏi trước.
3. **Task doc sai hoặc thiếu so với code thật → dừng, báo bạn, sửa task doc trước.** Không im lặng làm khác tài liệu.
4. **Xong hạng mục nào thì tick `- [x]` ngay trong DoD của chính file đó**, và sửa luôn nội dung nào đã không còn đúng. Không tạo file `.md` mới để báo cáo việc đã làm.
5. **Quyết định phát sinh giữa chừng** → ghi vào `qa.md` **và** chép về mục "Quyết định đã chốt" của task doc.
6. **Không commit, không push khi bạn chưa cho phép.**

#### Code xong rồi — soát DoD

**Cách bạn kiểm tra đã xong hay chưa:** mở task doc, đọc mục **DoD**. Mục nào chưa `- [x]` là chưa xong — không cần đọc code.

Hai loại mục trong đó:

| Loại | Trông như thế nào | Ai tick |
|---|---|---|
| **Tự kiểm được** | Có lệnh chạy + kết quả mong đợi: `pytest tests/api/test_export.py` xanh, `curl …` trả 200 kèm đúng shape | Tôi chạy, đọc kết quả, tự tick `- [x]` |
| **`(kiểm tay)`** | Thứ máy không tự khẳng định được: mở màn hình xem bố cục, mở file `.docx` xem có đúng đáp án ở trang cuối, thử trên dữ liệu thật, kiểm trên thiết bị/tài khoản cụ thể | **Bạn** làm rồi báo tôi tick |

Tôi tự soát bất cứ lúc nào bạn muốn:

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md, tự kiểm từng mục DoD trong repo theo §16 của
tech_docs/rules/claude/2_workflow-rules.md, tick mục đã đạt và nói rõ mục nào chưa,
mục nào phải bạn kiểm tay.
```

Tôi chạy test, đọc kết quả thật rồi mới tick — **không tick theo cảm giác**. Mục `(kiểm tay)` tôi để nguyên và nói rõ bạn cần làm gì.

**Không biết kiểm tay thế nào?** Hỏi Gemini, đừng tốn lượt của tôi:

```text
[HƯỚNG DẪN KIỂM THỬ TAY — CHỈ ĐỌC]
Dưới đây là các mục nghiệm thu (DoD) mà tôi phải tự kiểm bằng tay trong dự án BookForge.
Với mỗi mục, viết cho tôi các bước bấm/chạy theo thứ tự: chuẩn bị dữ liệu gì,
thao tác ở đâu, nhìn vào đâu để biết đạt, dấu hiệu nào là chưa đạt.
Viết cho người không rành kỹ thuật. Không sửa file, không viết code.

<dán các mục (kiểm tay)>
```

**Nghi ngờ một mục DoD có đáng làm không?** Cũng hỏi Gemini trước khi bỏ:

```text
[SOÁT DANH SÁCH DoD — CHỈ ĐỌC]
Đây là mục DoD của một task trong dự án BookForge.
Với mỗi mục: nó đang bảo vệ mình khỏi rủi ro gì, chi phí kiểm tốn bao nhiêu công,
và theo bạn là ĐÁNG GIỮ / CÓ THỂ BỎ / NÊN TÁCH SANG TASK SAU — nói rõ lý do.
Chỉ ra luôn rủi ro nào chưa có mục DoD nào phủ.
Không sửa file, không viết code.

<dán mục DoD của task doc>
```

Gemini trả lời trong chat; thấy hợp lý thì bảo tôi: `Bỏ mục DoD số 3 trong <file> vì <lý do>, ghi lý do vào ngay dưới mục DoD.` — **tôi là người sửa file**, và lý do bỏ phải nằm lại trong task doc để sau này còn biết vì sao.

**Chỉ khi mọi mục đều `- [x]` thì task mới coi là đạt.** Mục bỏ đi phải được xoá kèm ghi lý do, không để lửng `- [ ]` mãi.

## 5. Đang code mà gặp câu hỏi

Khi tôi đang viết code và gặp ràng buộc hoặc cần bạn quyết, tôi sẽ hỏi bằng một khối **tự chứa** — đủ ngữ cảnh, có trích code, nói rõ đang bị chặn ở đâu, kèm phương án và đánh đổi.

- Hiểu rồi → trả lời thẳng, tôi làm tiếp.
- Không hiểu → copy nguyên khối đó sang Gemini, kèm 2 dòng ở [`../gemini-assist.md`](../gemini-assist.md) §2C, đọc xong quay lại chốt với tôi.

Chốt xong tôi ghi vào `qa.md` của tính năng đó **và** chép quyết định về mục "Quyết định đã chốt" của task doc.

> `qa.md` là **nhật ký**. Task doc là **nguồn sự thật**. Quyết định nào chỉ nằm ở qa.md mà không chép về task doc thì vài hôm sau sẽ không ai nhớ vì sao làm vậy.

## 6. Nhờ Gemini cho đỡ tốn hạn mức

Gemini **chỉ đọc và trả lời trong chat** — không ghi file, không sửa code, không git. Bốn lúc nên gọi nó:

| Lúc nào | Nhờ gì |
|---|---|
| Đọc `01-brief.md` mà không hiểu câu hỏi nhắm vào đâu | Giải nghĩa từng câu bằng lời thường, chỉ ra câu thừa/thiếu (§4 bước 3) |
| Trước khi khảo sát, phạm vi còn rộng | Quét khoanh vùng: "chức năng X đi qua những file nào" → dán danh sách về cho Claude Code đọc đúng chỗ |
| Đọc `02-findings.md` mà thấy khó nuốt | Tóm tắt cho người không đọc code, giải nghĩa thuật ngữ, chỉ chỗ thiếu bằng chứng (§4 bước 4) |
| Tài liệu viết lủng củng, muốn sửa | Gemini đề xuất `<đoạn gốc> → <đoạn đề xuất>`; **Claude Code là người ghi vào file** |
| Mục DoD `(kiểm tay)` mà không biết kiểm thế nào | Viết các bước bấm/chạy cụ thể cho người không rành kỹ thuật (§4 bước 7) |
| Nghi một mục DoD thừa | Đánh giá ĐÁNG GIỮ / CÓ THỂ BỎ / TÁCH SANG TASK SAU kèm lý do (§4 bước 7) |
| Cần kiến thức ngoài repo | Tra thư viện, API, chuẩn, cách người khác làm |
| Đọc `03-design.md` hoặc câu hỏi của Claude Code mà không hiểu | Nhờ giảng lại bằng lời dễ hiểu, nêu 2 lựa chọn |
| Task doc / design vừa viết xong | Nhờ phản biện trước khi bắt tay code |

**Bưng kết quả về đúng cách:** dán vào Claude Code trong khối có nhãn, đừng dán trần.

```text
[TỪ GEMINI — CHƯA KIỂM CHỨNG]
<nội dung Gemini trả lời>
```

Thấy nhãn này tôi sẽ tự mở file ra kiểm chứng trước khi dùng, và nói rõ chỗ nào Gemini nói trật. Không có nhãn thì tôi coi đó là lời bạn và tin luôn — dễ lọt giả thuyết vào tài liệu chốt.

> **Không đưa cho Gemini:** `.env`, `.env.local`, `*.key`, `*.pem`, dump database, log có dữ liệu người dùng thật.

Prompt mẫu cho từng tình huống: [`../gemini-assist.md`](../gemini-assist.md).

## 7. Tra nhanh — các câu gõ vào Claude Code

**① Cập nhật bản đồ** — mỗi sáng, hoặc sau khi vừa merge/pull nhiều thay đổi.

```text
Cập nhật bản đồ từ <ref> theo §3 của tech_docs/rules/claude/2_workflow-rules.md.
```

**② Chuẩn hoá mô tả & tạo thư mục** — sau khi bạn viết nháp `tech_docs/research/00-desc.md`. Tôi làm xong thì dừng cho bạn duyệt.

```text
Đọc tech_docs/research/00-desc.md, chuẩn hoá theo §8 của
tech_docs/rules/claude/2_workflow-rules.md, tự đặt slug rồi chuyển vào đúng thư mục.
```

**③ Viết brief** — sau khi bạn đã duyệt `research/<slug>/00-desc.md`. Tôi liệt kê câu hỏi khảo sát + giả định rồi dừng cho bạn duyệt.

```text
Đọc tech_docs/research/<slug>/00-desc.md, viết 01-brief.md theo §9 của
tech_docs/rules/claude/2_workflow-rules.md, rồi chờ tôi duyệt.
```

**④ Khảo sát** — sau khi bạn đã duyệt `01-brief.md`.

```text
Đọc tech_docs/rules/claude/2_workflow-rules.md và tech_docs/research/<slug>/01-brief.md,
khảo sát repo rồi trả lời vào tech_docs/research/<slug>/02-findings.md theo §10.
```

**⑤ Thiết kế** — sau khi đã đọc và đồng ý với findings.

```text
Đọc tech_docs/research/<slug>/02-findings.md, viết 03-design.md theo §17 của
tech_docs/rules/claude/2_workflow-rules.md, rồi chờ tôi chốt.
```

**⑥ Chốt thành task doc** — sau khi bạn đã chốt phương án trong `03-design.md`.

```text
Đọc tech_docs/research/<slug>/03-design.md, kiểm chứng lại trong repo, rồi viết task doc
theo docs-convention §1.2a và §5 của tech_docs/rules/claude/2_workflow-rules.md.
```

**⑦ Thi công** — giao từng file, BE trước rồi mới FE.

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md và triển khai đúng theo tài liệu đó,
theo §16 của tech_docs/rules/claude/2_workflow-rules.md.
```

**⑧ Tự soát DoD** — khi muốn biết đã xong tới đâu mà không phải đọc code (xem §4 bước 7).

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md, tự kiểm từng mục DoD trong repo theo §16 của
tech_docs/rules/claude/2_workflow-rules.md, tick mục đã đạt và nói rõ mục nào chưa,
mục nào phải bạn kiểm tay.
```

**⑨ Hồi phục sau khi mất phiên**

```text
Đọc tech_docs/research/<slug>/status.md và tech_docs/rules/claude/2_workflow-rules.md,
nói lại trong 5 dòng đang ở đâu và bước tiếp theo là gì, rồi chờ tôi.
```

**⑩ Sinh lại bản đồ từ đầu** — hiếm: đổi sang nhánh rẽ khác hẳn, cấu trúc thư mục đổi lớn, hoặc bản đồ quá 14 ngày.

```text
Sinh lại tech_docs/overview/1_repo-map.md từ <ref> theo §3 của
tech_docs/rules/claude/2_workflow-rules.md.
```

> **Luật chung:** thứ gì đã nằm trong file thì **gõ đường dẫn, đừng dán nội dung vào terminal**. Dán tốn đúng bằng lúc tôi tự đọc file, nhưng mất lịch sử và không sửa lại được.

## 8. Một thư mục tính năng có gì

```text
tech_docs/research/
├── 00-desc.md        ← BẠN viết nháp ở đây, chỉ tồn tại tới khi tôi dọn vào <slug>/
└── <slug>/
    ├── status.md      ← Claude Code viết, để hồi phục khi mất phiên
    ├── 00-desc.md     ← bản đã chuẩn hoá, bạn duyệt trước khi khảo sát
    ├── 01-brief.md    ← Claude Code viết, bạn duyệt: sắp đi tìm gì, đang tin gì
    ├── 02-findings.md ← Claude Code viết, sự thật + bằng chứng file:line
    ├── 03-design.md   ← Claude Code viết, phương án + đánh đổi; bạn tranh luận tại đây
    └── qa.md          ← nhật ký hỏi đáp lúc thi công
```

Bản chốt cuối cùng **không nằm ở đây** mà ở `backend/docs/tasks/`. Thư mục `research/` chỉ là nháp.

## 9. Sáu lỗi hay mắc

| Triệu chứng | Nguyên nhân | Sửa |
|---|---|---|
| Tài liệu nhắc tên file không có thật | Thứ Gemini nói được dán trần vào, không ai kiểm chứng | Luôn dán kèm nhãn `[TỪ GEMINI — CHƯA KIỂM CHỨNG]` (§6) |
| Khảo sát đọc lan man, tốn token | Không đóng khung phạm vi | Thêm "chỉ đọc mảng X" vào câu giao việc, hoặc duyệt `01-brief.md` trước |
| Hết hạn mức Claude giữa chừng | Dồn cả việc giảng giải lẫn việc đọc rộng vào Claude Code | Đẩy hai việc đó sang Gemini (§6) |
| Không nhớ vì sao chọn cách này | Quyết định nằm trong chat, không nằm trong file | Mọi quyết định chép về "Quyết định đã chốt" của task doc |
| Code xong nhưng khác với task doc | Thi công không bám "Quyết định đã chốt", hoặc doc sai mà không sửa | Gõ câu ⑧ để tự soát DoD; doc sai thì sửa doc trước rồi mới sửa code |
| Người khác mở task doc thấy link chết | Task doc trỏ về `tech_docs/research/…` — họ không có repo đó | Chép nội dung vào task doc, xoá mọi đường dẫn `tech_docs/` ([`docs-convention.md`](../docs-convention.md) §3.1) |

## 10. Khi nào mở file luật

[`2_workflow-rules.md`](2_workflow-rules.md) — mở khi cần:

| Cần gì | Mục |
|---|---|
| Bảng chọn ref cho bản đồ | §3 |
| Ranh giới dùng Gemini | §6 |
| Khuôn `00-desc.md` | §8 |
| Khuôn `01-brief.md` | §9 |
| Khuôn `02-findings.md` | §10 |
| Khuôn `03-design.md` | §17 |
| Khuôn `qa.md` | §12 |
| Khuôn `status.md` | §13 |
| Luật thi công theo task doc | §16 |
| Checklist đầy đủ | §15 |
