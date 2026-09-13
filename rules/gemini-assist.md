# Gemini — trợ lý tra cứu (read-only)

> Gemini **không phải** một luồng làm việc song song. Nó là chỗ bạn đẩy phần **đọc rộng và giảng giải** sang, để giữ hạn mức Claude cho việc quan trọng hơn: **đọc chính xác và ghi vào repo**.
> Luật ràng buộc nằm ở [`claude/2_workflow-rules.md`](claude/2_workflow-rules.md) §6; file này là phần thực hành.

---

## 1. Ba điều Gemini không được làm

| Cấm | Vì sao |
|---|---|
| **Ghi hoặc sửa bất kỳ file nào** — kể cả `tech_docs/research/` | Một nguồn sự thật, một lịch sử sửa. Mọi file do Claude Code viết. |
| **Sửa code** | Hai model cùng sửa thì không ai biết vì sao code thành ra như vậy. |
| **Mọi thao tác git** (add, commit, push, checkout, stash) | Xem [`claude/3_git-workflow-rules.md`](claude/3_git-workflow-rules.md). |

Gemini chỉ **đọc và trả lời trong chat**. Thứ đáng giữ lại thì bạn dán về Claude Code, Claude Code ghi (§3 bên dưới).

**Không đưa cho Gemini:** `.env`, `.env.local`, `*.key`, `*.pem`, dump cơ sở dữ liệu, log có dữ liệu người dùng thật. Cần bàn cấu hình thì dùng `.env.example` hoặc `core/settings.py` — chỉ có tên biến, không có khoá.

Dán khối này ở đầu mỗi phiên Gemini (IDE hoặc web):

```text
Bạn là trợ lý TRA CỨU cho dự án BookForge, chế độ CHỈ ĐỌC.
Tuyệt đối KHÔNG tạo/sửa/xoá file, KHÔNG sửa code, KHÔNG chạy lệnh git.
Mọi thay đổi trong repo do một agent khác (Claude Code) thực hiện.
Việc của bạn: đọc, giải thích, khoanh vùng, tra tài liệu ngoài, phản biện — và trả lời ngay trong chat.
Khi nói về code trong repo, luôn kèm đường dẫn file và số dòng để tôi kiểm chứng lại được.
Chỗ nào bạn suy đoán, ghi rõ "[suy đoán]"; đừng trình bày suy đoán như sự thật.
```

## 2. Bảy tình huống nên gọi Gemini

### A. Tra kiến thức ngoài repo
Thư viện, API bên thứ ba, chuẩn, cách người khác giải bài toán tương tự. Claude Code không nhanh hơn ở việc này, mà đắt hơn.

```text
[TRA CỨU NGOÀI]
Bối cảnh: <bài toán, 3–5 dòng — không cần dán code>
Cần biết: <câu hỏi cụ thể>
Yêu cầu trả lời:
1. Câu trả lời ngắn trước, giải thích sau.
2. Nêu 2 cách làm phổ biến kèm đánh đổi thật (hiệu năng, độ phức tạp, chi phí vận hành).
3. Ghi rõ phiên bản/thời điểm thông tin, và chỗ nào bạn không chắc.
```

### B. Quét rộng để khoanh vùng
Khi chưa biết mảng nào lo việc gì. Gemini đọc rộng rẻ; Claude Code chỉ cần đọc lại đúng vùng đã khoanh.

```text
[QUÉT KHOANH VÙNG — CHỈ ĐỌC]
Trong repo này, tìm xem chức năng "<mô tả bằng lời thường>" hiện đi qua những chỗ nào.
Trả về đúng một bảng: | file:line | vai trò của chỗ đó | mức chắc chắn (chắc/đoán) |
Không quá 15 dòng. KHÔNG đề xuất sửa gì, KHÔNG viết code.
Chỗ nào chỉ suy ra từ tên file/tên hàm thì ghi "đoán".
```

### C. Giảng lại cho bạn hiểu
Thay đúng vai "web" cũ: giải thích một đoạn code, một lỗi, một đánh đổi mà Claude Code vừa nêu.

```text
Đây là câu hỏi/ràng buộc do agent đang viết code trong repo BookForge nêu ra.
Giải thích cho tôi bằng lời dễ hiểu, nêu 2 lựa chọn kèm đánh đổi, rồi khuyến nghị một cái.

<dán nguyên khối câu hỏi tự chứa của Claude Code>
```

### D. Phản biện tài liệu Claude Code vừa viết
Con mắt thứ hai cho `03-design.md` hoặc task doc, trước khi bắt tay code.

```text
[PHẢN BIỆN — CHỈ ĐỌC]
Đọc <đường dẫn file>. Đóng vai người sẽ phải thi công tài liệu này.
1. Chỗ nào đọc xong vẫn không biết phải làm gì?
2. Quyết định nào chưa có lý do, hoặc mâu thuẫn với chỗ khác trong file?
3. Rủi ro nào chưa được nhắc tới (hiệu năng, đồng thời, dữ liệu cũ, rollback)?
Mỗi ý một dòng, trích chỗ có vấn đề. KHÔNG sửa file.
```

### E. Đọc hộ tài liệu để bạn duyệt
Quy trình có hai cửa duyệt mà bạn phải đọc tài liệu kỹ thuật: `01-brief.md` (tôi sắp đi tìm gì) và `02-findings.md` (tôi đã tìm thấy gì). Không nuốt nổi thì đẩy sang đây, đừng tốn lượt Claude để nghe giảng.

Với `01-brief.md`:

```text
[GIẢI NGHĨA — CHỈ ĐỌC]
Tôi là người ra yêu cầu, không rành kỹ thuật. Dưới đây là danh sách câu hỏi khảo sát
mà một agent sắp dùng để đọc code dự án BookForge.
Với mỗi câu: giải thích bằng lời thường nó đang muốn tìm gì và vì sao cần biết.
Cuối cùng nói câu nào theo bạn là thừa, và thiếu câu nào đáng hỏi.
Không viết code, không sửa file.

<dán nội dung 01-brief.md>
```

Với `02-findings.md`:

```text
[ĐỌC HỘ KẾT QUẢ KHẢO SÁT — CHỈ ĐỌC]
Đây là kết quả khảo sát code dự án BookForge do một agent khác viết.
1. Tóm tắt trong 5 dòng cho người không đọc code.
2. Giải nghĩa các thuật ngữ và tên kỹ thuật xuất hiện trong đó.
3. Chỉ ra chỗ nào kết luận mà không kèm bằng chứng file:line, hoặc mâu thuẫn nhau.
4. Nêu 3 câu tôi nên hỏi lại agent đó.
Không sửa file, không viết code.

<dán nội dung 02-findings.md — hoặc chỉ đường dẫn nếu Gemini chạy trong IDE>
```

### F. Đề xuất sửa câu chữ tài liệu
Tài liệu viết lủng củng, thiếu mạch, dùng từ khó hiểu — Gemini soạn bản sửa, **Claude Code là người ghi vào file**.

```text
[ĐỀ XUẤT SỬA TÀI LIỆU — CHỈ ĐỌC]
Đọc <đường dẫn file>. Chỗ nào khó hiểu, thiếu, hoặc sai mạch thì viết lại giúp tôi.
Trình bày dạng từng mục: <đoạn gốc> → <đoạn đề xuất> → <sửa vì sao>.
Chỉ sửa cách diễn đạt, KHÔNG đổi quyết định kỹ thuật đã chốt trong file.
TUYỆT ĐỐI không tự sửa file — tôi sẽ đưa đề xuất của bạn cho Claude Code ghi lại.
```

Mang về theo khối có nhãn (§3) rồi gõ: `Áp các đề xuất dưới đây vào <file>, cái nào không ổn thì nói rõ vì sao không áp.`

### G. Kiểm thử tay và soát danh sách DoD
Hai prompt dùng sau khi code xong — nội dung đầy đủ nằm ở [`claude/1_start-here.md`](claude/1_start-here.md) §4 bước 7, để bạn dùng ngay tại chỗ cần:

- `[HƯỚNG DẪN KIỂM THỬ TAY — CHỈ ĐỌC]` — biến mục DoD `(kiểm tay)` thành các bước bấm/chạy cụ thể cho người không rành kỹ thuật.
- `[SOÁT DANH SÁCH DoD — CHỈ ĐỌC]` — mỗi mục đang chặn rủi ro gì, tốn bao nhiêu công, **ĐÁNG GIỮ / CÓ THỂ BỎ / TÁCH SANG TASK SAU**; và rủi ro nào chưa mục nào phủ.

Kết quả mang về thì **Claude Code là người sửa task doc**. Bỏ một mục DoD phải ghi lý do lại trong chính file đó — vài tuần sau không ai nhớ vì sao mục đó biến mất.

## 3. Bưng kết quả về Claude Code

Thứ đáng giữ thì dán vào Claude Code **trong khối có nhãn**, đừng dán trần:

```text
[TỪ GEMINI — CHƯA KIỂM CHỨNG]
<nội dung Gemini trả lời>
```

Thấy nhãn này, Claude Code sẽ **tự mở file ra kiểm chứng trước khi dùng**, loại bỏ cái sai và nói rõ chỗ nào Gemini nói trật. Dán trần không nhãn thì mặc định là lời của bạn — giả thuyết sẽ lọt thẳng vào tài liệu chốt.

Gemini trả lời dài thì **đừng dán hết**: giữ lại bảng `file:line`, kết luận, và phần đánh đổi. Phần giảng giải là để bạn đọc, không phải để đưa vào repo.

## 4. Khi Claude hết hạn mức giữa chừng

Dán `tech_docs/research/<slug>/status.md` cho Gemini rồi hỏi tiếp — bàn phương án, hiểu chỗ đang vướng, chuẩn bị sẵn quyết định. Nhưng **không để Gemini ghi gì cả**: ghi lại những gì đã chốt là việc của phiên Claude Code kế tiếp.

## 5. Bảng tự kiểm trước khi hỏi

| Tiêu chí | Kiểm |
|---|---|
| **Đúng người** | Việc này có cần quyền ghi không? Có → Claude Code, không phải Gemini. |
| **Rõ vị trí neo** | Đã chỉ thư mục/file/bản đồ cụ thể chưa, hay đang hỏi chung chung? |
| **Ép dẫn chứng** | Đã yêu cầu `file:line` và nhãn "đoán" chưa? |
| **Đóng khung phạm vi** | Đã ghi rõ cái KHÔNG cần đọc chưa? |
| **Không rò rỉ bí mật** | Trong thứ sắp dán có khoá, token, dữ liệu người dùng thật không? |
