# Bắt đầu ở đây — cách làm việc mỗi ngày

> File này là **hướng dẫn sử dụng**, đọc để biết làm gì.
> [`2_web-code-handoff.md`](2_web-code-handoff.md) là **luật chi tiết**, chỉ mở khi cần tra khuôn mẫu.
> Prompt dài dán vào web nằm ở file luật §6 — cố ý không chép lại ở đây để hai bản không lệch nhau.

---

## 1. Ba nhân vật

```text
BẠN            biết muốn gì               không cần biết code nằm đâu
CLAUDE WEB     nghĩ giỏi, giải thích, rẻ  không nhìn thấy code
CLAUDE CODE    nhìn thấy code, viết code  đắt — nên chỉ gọi khi cần đọc/sửa repo
```

Web và Code **không nói chuyện trực tiếp được**. Bạn là người bưng file qua lại.
Vì vậy mọi thứ trao đổi đều là **file trong repo**, không phải tin nhắn trôi trong chat.

Nguyên tắc chi phí: **việc nghĩ và việc giải thích đẩy sang web, việc đọc và sửa code mới gọi Claude Code.**

## 2. Bốn tình huống — mở đúng mục

| Bạn đang cần | Đọc mục |
|---|---|
| Sáng mở máy, chuẩn bị làm | §3 |
| Bắt đầu một tính năng mới | §4, bước 1–6 |
| Task doc đã có, muốn bắt tay làm | §4, **bước 7** |
| Đang code, gặp câu hỏi không hiểu | §5 |
| Web hết token, phải đổi tài khoản | §6 |

## 3. Mỗi sáng — 1 phút

Bản đồ dự án phải mới thì web mới hỏi trúng. Gõ vào Claude Code:

```text
Cập nhật bản đồ từ <ref> theo §3 của tech_docs/rules/claude/2_web-code-handoff.md.
```

Điền `<ref>` là nhánh bạn muốn bản đồ phản ánh:

| Điền | Khi nào dùng |
|---|---|
| `origin/dev` | Muốn bản đồ theo nhánh chung của team |
| `working` | Muốn bản đồ khớp đúng thứ bạn đang sửa dở, **kể cả chưa commit** |
| `feat/abc` | Theo một nhánh cụ thể |
| *(bỏ trống)* | Dùng lại ref của lần trước |

Kết quả: hai file [`overview/repo-map.md`](../../overview/repo-map.md) và [`overview/backend-features-all.md`](../../overview/backend-features-all.md) được cập nhật, và tôi in ra vài dòng **"hôm nay đổi gì"**.

- Không có gì đổi → tôi báo "không đổi" rồi dừng, gần như không tốn token.
- Có đổi → **copy mấy dòng đó dán vào chat web đang mở dở**, để web không dùng bản đồ cũ.

## 4. Bắt đầu một tính năng mới

Ví dụ chạy thật: *"Xuất đề thi ra Word kèm đáp án"*.

### Bước 1 — Bạn viết mô tả (5 phút)

Tạo `tech_docs/research/xuat-de-thi-word/00-mo-ta.md`. Viết bằng lời thường, **không cần biết tên hàm hay tên bảng nào**:

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

### Bước 2 — Mở chat web mới, dán 3 thứ

Theo thứ tự:

1. **Prompt giao thức** — copy nguyên khối ở [`2_web-code-handoff.md`](2_web-code-handoff.md) §6.
2. **Bản đồ**, dán theo phạm vi cho đỡ tốn:

| Phía | Dán gì |
|---|---|
| Chỉ BE | `repo-map.md` §1,2,3,5,6,7 + `backend-features-all.md` |
| Chỉ FE | `repo-map.md` §4 + `frontend/CONVENTION.md` |
| Cả hai / chưa rõ | Cả hai file, đầy đủ |

3. **Nội dung `00-mo-ta.md`** bạn vừa viết.

Web trả về **một khối markdown**: danh sách câu hỏi khảo sát. Nó sẽ hỏi kiểu:

```text
Q1 [ĐỊNH VỊ][BE] Luồng xuất PDF hiện tại đi qua những hàm nào,
   từ endpoint tới lúc sinh file?
Q2 [XÁC MINH][BE] Bảng `answer_cards` có phải nơi lưu đáp án của đề thi không,
   gắn với `test_papers` bằng cột nào?
Q3 [ĐỊNH VỊ][FE] Nút tải về ở màn hình đề thi gọi hàm nào trong src/api/?
```

`[XÁC MINH]` = tên đã có trong bản đồ. `[ĐỊNH VỊ]` = chưa ai biết tên, Claude Code phải đi tìm.

### Bước 3 — Lưu câu hỏi vào repo

Copy khối web vừa trả về, lưu **nguyên văn** thành `tech_docs/research/xuat-de-thi-word/01-brief.md`.

### Bước 4 — Gõ một câu trong Claude Code ← tốn token

```text
Đọc tech_docs/rules/claude/2_web-code-handoff.md và
tech_docs/research/xuat-de-thi-word/01-brief.md,
trả lời vào tech_docs/research/xuat-de-thi-word/02-findings.md.
```

Không cần mô tả lại tính năng — mô tả đã nằm trong file.

Tôi trả về `02-findings.md` gồm: **phía nào phải sửa**, tên thật của mọi thứ liên quan, trả lời từng câu kèm `file:line` và trích code, bảng **giả định của web đúng/sai**, và danh sách **file nên upload lên web**.

### Bước 5 — Bưng kết quả về web

Mở `02-findings.md`, copy **toàn bộ**, dán vào chat web đang mở. Không cần viết gì thêm.

Nếu findings có mục **"File nên upload lên web"** thì kéo thả những file đó từ VS Code vào chat web luôn — web đọc được cả file sẽ chính xác hơn nhiều.

> **Không bao giờ upload:** `.env`, `.env.local`, `*.key`, `*.pem`, dump database, log có dữ liệu người dùng thật.
> Cần cho web xem cấu hình thì upload `.env.example` hoặc `core/settings.py` — hai file này chỉ có tên biến, không có khoá.

Web viết `03-design.md`: phương án, đánh đổi, kế hoạch — lần này dựa trên tên thật của code.
**Đây là lúc tranh luận thoải mái**: hỏi tại sao, bắt so sánh hai cách, bắt viết lại. Phía web rẻ.

### Bước 6 — Lưu thiết kế, rồi chốt ← tốn token

Lưu `03-design.md` vào cùng thư mục, rồi gõ:

```text
Đọc tech_docs/research/xuat-de-thi-word/03-design.md, kiểm chứng lại trong repo,
rồi viết task doc theo docs-convention §1.2a.
```

Tôi kiểm lại phương án có khả thi không, rồi viết file giao việc trong `backend/docs/tasks/`:

- Chỉ BE → một file `YYYY-MM-DD-xuat-de-thi-word.md`
- Chỉ FE → một file `…-frontend.md`
- Cả hai → **hai file**, mỗi file tự đứng được

**Từ task doc đó mới bắt đầu code.**

> **Task doc không được nhắc tới `tech_docs/`.** `bookforge`, `bookforge-fe`, `tech_docs` là ba repo riêng — người nhận việc chỉ có repo triển khai, không có thư mục nghiên cứu của bạn.
> Nên task doc phải **chép nội dung cần thiết vào trong nó**, không link ngược về `research/`. Đây là ràng buộc cứng, xem [`docs-convention.md`](../docs-convention.md) §3.1.

### Bước 7 — Giao việc: bảo Claude Code làm theo task doc

Task doc viết xong **không tự chạy**. Bạn phải giao việc bằng một câu:

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md và triển khai đúng theo tài liệu đó.
```

Đụng cả hai phía thì **giao từng file một, không gộp**: làm BE trước cho có API thật, xong mới giao file `-frontend.md`.
Hai repo là hai thư mục làm việc khác nhau, nên mở phiên Claude Code riêng cho mỗi repo.

**Sáu luật tôi phải theo khi thi công** — bạn không cần nhắc lại, chúng nằm trong [`2_web-code-handoff.md`](2_web-code-handoff.md) §16; liệt kê ở đây để bạn biết đường soát:

1. **Task doc là hợp đồng.** Làm đúng phạm vi trong đó: không thêm tính năng, không refactor kèm, không "tiện tay sửa luôn".
2. **Bám "Quyết định đã chốt".** Đã chốt rồi thì không tự chọn cách khác, kể cả khi thấy cách khác hay hơn — muốn đổi thì hỏi trước.
3. **Task doc sai hoặc thiếu so với code thật → dừng, báo bạn, sửa task doc trước.** Không im lặng làm khác tài liệu; sai lệch giữa doc và code là thứ vài tuần sau không ai gỡ được.
4. **Xong hạng mục nào thì tick `- [x]` ngay trong DoD của chính file đó**, và sửa luôn nội dung nào đã không còn đúng. Không tạo file `.md` mới để báo cáo việc đã làm.
5. **Quyết định phát sinh giữa chừng** → ghi vào `qa.md` **và** chép về mục "Quyết định đã chốt" của task doc (§5).
6. **Không commit, không push khi bạn chưa cho phép.**

**Cách bạn kiểm tra đã xong hay chưa:** mở task doc, đọc mục **DoD**. Mục nào chưa `- [x]` là chưa xong — không cần đọc code.
Muốn tôi tự soát lại thì gõ:

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md, tự kiểm từng mục DoD trong repo,
tick mục đã đạt và nói rõ mục nào chưa.
```

## 5. Đang code mà gặp câu hỏi

Khi tôi đang viết code và gặp ràng buộc hoặc cần bạn quyết, tôi sẽ hỏi bạn bằng một khối **tự chứa** — đủ ngữ cảnh, có trích code, nói rõ đang bị chặn ở đâu.

Bạn làm 3 việc:

1. Copy nguyên khối đó, dán sang chat web, kèm 2 dòng này ở trên:

```text
Đây là câu hỏi/ràng buộc do agent đang viết code trong repo BookForge nêu ra.
Giải thích cho tôi bằng lời dễ hiểu, nêu 2 lựa chọn kèm đánh đổi, rồi khuyến nghị một cái.
```

2. Đọc, chọn, trả lời tôi.
3. Tôi ghi vào `qa.md` của tính năng đó **và** chép quyết định về mục "Quyết định đã chốt" của task doc.

Vòng này lặp bao nhiêu lần cũng được — nó rẻ, vì phần giảng giải nằm ở web.

> `qa.md` là **nhật ký**. Task doc là **nguồn sự thật**. Quyết định nào chỉ nằm ở qa.md mà không chép về task doc thì vài hôm sau sẽ không ai nhớ vì sao làm vậy.

## 6. Web hết token, đổi tài khoản

Mỗi thư mục tính năng có file `trang-thai.md` — **tôi tự cập nhật, bạn không phải viết**. Nó ghi: mục tiêu, phía, quyết định đã chốt, phương án đang theo, danh sách file, câu hỏi mở, bước tiếp theo.

Mở chat web mới bằng tài khoản khác, dán 3 thứ:

1. Khối hồi sức:

```text
Tôi đang tiếp tục một việc dở bằng tài khoản mới, bạn chưa có ngữ cảnh gì.
Dưới đây là prompt giao thức, rồi tới file trạng thái của việc đó.
Đọc xong, nói lại trong 5 dòng bạn hiểu đang ở đâu và bước tiếp theo là gì, rồi chờ tôi.
```

2. Prompt giao thức (§6 của file luật).
3. Nội dung `trang-thai.md`.

Xong. Không phải kể lại từ đầu.

**Mẹo:** hỏi câu nặng nhất ngay đầu phiên web, đừng để dồn tới lúc sắp hết token.

## 7. Tra nhanh — các câu gõ vào Claude Code

Sáu câu, sáu thời điểm. Giữa các câu đó Claude Code nằm im, không tốn gì.

**① Cập nhật bản đồ**
**Khi nào:** mỗi sáng, **trước khi mở chat web**. Gõ thêm giữa ngày nếu bạn vừa merge/pull nhiều thay đổi, hoặc thấy web bắt đầu bịa tên file.

```text
Cập nhật bản đồ từ <ref> theo §3 của tech_docs/rules/claude/2_web-code-handoff.md.
```

**② Khảo sát**
**Khi nào:** ngay sau khi web trả về brief và **bạn đã lưu nó thành `01-brief.md`**. Nếu có vòng bổ sung thì đổi số: `04-brief.md` → `05-findings.md`.

```text
Đọc tech_docs/rules/claude/2_web-code-handoff.md và tech_docs/research/<slug>/01-brief.md,
trả lời vào tech_docs/research/<slug>/02-findings.md.
```

**③ Chốt**
**Khi nào:** ngay sau khi web trả về thiết kế và **bạn đã lưu nó thành `03-design.md`**. Sau câu này mới bắt đầu code.

```text
Đọc tech_docs/research/<slug>/03-design.md, kiểm chứng lại trong repo,
rồi viết task doc theo docs-convention §1.2a.
```

**④ Thi công**
**Khi nào:** sau khi task doc đã có. Đụng cả hai phía thì giao từng file, BE trước rồi mới FE.

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md và triển khai đúng theo tài liệu đó.
```

**⑤ Tự soát DoD**
**Khi nào:** khi bạn muốn biết đã xong tới đâu mà không phải đọc code.

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md, tự kiểm từng mục DoD trong repo,
tick mục đã đạt và nói rõ mục nào chưa.
```

**⑥ Sinh lại bản đồ từ đầu**
**Khi nào:** hiếm — khi đổi sang nhánh rẽ khác hẳn, cấu trúc thư mục đổi lớn, bản đồ quá 14 ngày, hoặc lệch nhiều tới mức vá từng dòng không xuể.

```text
Sinh lại tech_docs/overview/repo-map.md từ <ref> theo §3.
```

> **Luật chung của ② và ③:** luôn gõ **sau khi đã lưu file**, không bao giờ dán nội dung web vào terminal.
> Dán vào terminal tốn đúng bằng lúc tôi tự đọc file, nhưng mất lịch sử và không sửa lại được.

## 8. Một thư mục tính năng có gì

```text
tech_docs/research/<slug>/
├── trang-thai.md     ← Claude Code viết, để hồi phục phiên web
├── 00-mo-ta.md       ← BẠN viết, bằng lời thường
├── 01-brief.md       ← Web viết, câu hỏi khảo sát
├── 02-findings.md    ← Claude Code viết, sự thật + bằng chứng
├── 03-design.md      ← Web viết, phương án
└── qa.md             ← nhật ký hỏi đáp lúc thi công
```

Bản chốt cuối cùng **không nằm ở đây** mà ở `backend/docs/tasks/`. Thư mục `research/` chỉ là nháp.

## 9. Sáu lỗi hay mắc

| Triệu chứng | Nguyên nhân | Sửa |
|---|---|---|
| Web bịa tên file, tên hàm không có thật | Chưa dán prompt giao thức, hoặc bản đồ đã cũ | Dán lại prompt §6; chạy cập nhật bản đồ (§3) |
| Phải hỏi tới vòng ba mới đủ thông tin | Brief thiếu mục "Cần trích nguyên văn" | Bảo web viết kỹ mục đó trước khi bạn lưu file |
| Claude Code đọc lan man, tốn token | Brief không đóng khung phạm vi | Thêm câu "chỉ đọc mảng X" vào brief |
| Không nhớ vì sao chọn cách này | Quyết định nằm trong chat, không nằm trong file | Mọi quyết định chép về "Quyết định đã chốt" của task doc |
| Code xong nhưng khác với task doc | Thi công không bám "Quyết định đã chốt", hoặc doc sai mà không sửa | Gõ câu ⑤ để tự soát DoD; doc sai thì sửa doc trước rồi mới sửa code (§4 bước 7) |
| Người khác mở task doc thấy link chết | Task doc trỏ về `tech_docs/research/…` — họ không có repo đó | Chép nội dung vào task doc, xoá mọi đường dẫn `tech_docs/` ([`docs-convention.md`](../docs-convention.md) §3.1) |

## 10. Khi nào mở file luật

[`2_web-code-handoff.md`](2_web-code-handoff.md) — mở khi cần:

| Cần gì | Mục |
|---|---|
| Prompt dài dán vào web | §6 |
| Bảng chọn ref cho bản đồ | §3 |
| Khuôn `00-mo-ta.md` | §8 |
| Quy tắc upload file lên web | §11 |
| Khuôn `qa.md` | §12 |
| Khuôn `trang-thai.md` | §13 |
| Luật thi công theo task doc | §16 |
| Checklist đầy đủ | §15 |
