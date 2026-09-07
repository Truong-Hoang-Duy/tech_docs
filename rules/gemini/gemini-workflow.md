# Bắt đầu ở đây — Luồng làm việc với Gemini

> File này là **hướng dẫn sử dụng**, đọc để biết làm gì khi làm việc với Gemini Code Assist / CLI.
> Quy ước chung repo: [`../../docs-convention.md`](../../docs-convention.md).

---

## 1. Mô hình làm việc

Khác với Claude được chia thành 2 nhân vật (Web và Code), khi làm việc với **Gemini trong IDE**, chúng ta thường thực hiện cả việc "nghiên cứu, thiết kế" lẫn "đọc, viết code" trong cùng một phiên chat, vì Gemini có quyền truy cập trực tiếp vào codebase của bạn.

Dù vậy, nguyên lý cốt lõi vẫn không đổi: **Mọi thứ trao đổi phải là file trong repo, không phải tin nhắn trôi trong chat.**

Để Gemini không bị "ảo giác" (hallucination) hay mở rộng phạm vi (scope creep), mọi prompt giao việc đều phải tuân thủ **Khung cấu trúc 5 thành phần**:
1. **[Vị trí neo & Ngữ cảnh]:** File bản đồ, thư mục làm việc.
2. **[Ý đồ & Mục tiêu]:** Cần giải quyết bài toán gì.
3. **[Phạm vi & Không làm]:** Ranh giới công việc.
4. **[Dẫn chứng]:** Bắt buộc phải có `file:line` khi phân tích.
5. **[Đầu ra]:** Kết quả lưu vào file nào.

## 2. Các tình huống thường gặp

| Bạn đang cần | Đọc mục |
|---|---|
| Sáng mở máy, chuẩn bị làm | §3 |
| Bắt đầu một tính năng mới | §4 |
| Đang code, gặp câu hỏi hoặc lỗi | §5 |
| Xem thư mục làm việc có gì | §6 |
| Bảng kiểm tra chất lượng Prompt | §7 |

## 3. Mỗi sáng — Cập nhật bản đồ

Bản đồ dự án phải luôn mới thì Gemini mới biết code hiện tại đang thế nào. Hãy yêu cầu Gemini chạy cập nhật:

```text
[CẬP NHẬT BẢN ĐỒ]
Kiểm tra xem có router mới, bảng DB mới, job nền mới hoặc biến môi trường mới nào không.
Hãy cập nhật các mục tương ứng trong tech_docs/overview/repo-map.md từ nhánh hiện tại.
```

*(Nếu không có gì đổi, Gemini sẽ báo không đổi).*

## 4. Bắt đầu một tính năng mới (Workflow)

Quy trình này giúp tận dụng tối đa khả năng đọc codebase và phán đoán của mô hình, tránh việc prompt quá ngắn gọn làm giới hạn tư duy.

### Bước 1: Phân tích Ngữ cảnh & Đặt tên Slug (Chưa đụng tới code)
**Bạn làm:**
Viết mô tả yêu cầu bằng ngôn ngữ tự nhiên (Người dùng muốn gì, hiện trạng ra sao, chỗ nào chưa rõ). Bạn có thể viết nháp vào một file bất kỳ (ví dụ `tech_docs/research/draft.md`) hoặc chat trực tiếp. Bạn KHÔNG cần phải tự nghĩ tên thư mục vội.

**Prompt cho Gemini:**
Gửi mô tả cùng với yêu cầu dưới đây để Gemini phân tích và tạo cấu trúc thư mục.

```text
[PHÂN TÍCH NGỮ CẢNH & GỢI Ý SLUG]
Dưới đây là mô tả tính năng tôi muốn làm:
<Dán mô tả của bạn vào đây, hoặc chỉ định file nháp bạn vừa viết>

Nhiệm vụ của bạn ở bước này là:
1. Đọc kỹ để rút ra bối cảnh và hiểu rõ người dùng cuối thực sự muốn gì (User Intent).
2. Gợi ý 3-5 lựa chọn `<slug>` ngắn gọn, súc tích (tên tiếng Anh không dấu gạch ngang, VD: bloom-question-generate) để tôi chọn làm tên thư mục.
3. Đặt ra các câu hỏi khảo sát sâu sắc (nếu có) về những điểm chưa rõ.

*(Chờ tôi chọn slug và trả lời các câu hỏi)*
Sau khi tôi đã chọn và trả lời, hãy:
- Tổng hợp lại toàn bộ (mô tả ban đầu + câu trả lời của tôi) thành một bản mô tả chi tiết, rõ ràng và đầy đủ ngữ cảnh hơn.
- Tự động tạo thư mục `tech_docs/research/<slug>/` và lưu bản mô tả chi tiết đó vào `00-desc.md`.
- Xóa file nháp (ví dụ `draft.md`) nếu tôi có sử dụng.

TUYỆT ĐỐI CHÚ Ý:
- KHÔNG đi vào phân tích code hay đề xuất giải pháp kỹ thuật lúc này.
- KHÔNG viết bất kỳ đoạn code nào.
- Tên các file được tạo BẮT BUỘC phải dùng tiếng Anh ngắn gọn (VD: `00-desc.md`, `01-plan.md`, `status.md`).
Mục tiêu là chốt chặt nghiệp vụ và trả lời các thắc mắc của bạn trước khi sang bước lập kế hoạch.
```

### Bước 2: Khảo sát Codebase & Đề xuất Kế hoạch (Plan)
**Bạn làm:**
Sau khi giải đáp thắc mắc ở Bước 1, yêu cầu Gemini lặn sâu vào codebase để lập kế hoạch kỹ thuật.

**Prompt cho Gemini:**
Khuôn mẫu này kích hoạt tư duy phản biện và khả năng trinh sát codebase của Gemini:

```text
[KHẢO SÁT CODE & LẬP KẾ HOẠCH KỸ THUẬT]
Ngữ cảnh nghiệp vụ đã rõ ràng. Bây giờ hãy tiến hành khảo sát codebase thực tế và lập kế hoạch.
Bạn cần sử dụng các công cụ tìm kiếm và đối chiếu với bản đồ `tech_docs/overview/repo-map.md` để:
1. Lần theo luồng thực thi: Xác định chính xác các file, API router, model DB, và service liên quan hiện có (bắt buộc kèm dẫn chứng file:line).
2. Đưa ra Kế hoạch Kỹ thuật (Plan) chi tiết cho task lần này. Nêu rõ kiến trúc dự kiến, các bước thi công.
3. Đóng vai trò phản biện: Chỉ ra ít nhất 2 rủi ro hoặc điểm đánh đổi (trade-offs) của kế hoạch này (ví dụ: tác động hiệu năng, rủi ro concurrency).

Hãy lưu toàn bộ kế hoạch và phương án thiết kế này vào file mới:
`tech_docs/research/<slug>/01-plan.md`

Chúng ta có thể sẽ tranh luận và thay đổi phương án trong file này trước khi chốt.
```

### Bước 3: Đóng gói Task Doc chuẩn Hợp đồng
**Bạn làm:**
Khi kế hoạch thiết kế trong `01-plan.md` đã được chốt, yêu cầu Gemini sinh Task Doc giao việc.

**Prompt cho Gemini:**
Khuôn mẫu này đảm bảo Task Doc sinh ra đủ chặt chẽ, tách bạch và không bị rò rỉ ngữ cảnh nghiên cứu:

```text
[SINH TASK DOC GIAO VIỆC]
Phương án thiết kế trong `tech_docs/research/<slug>/01-plan.md` đã được duyệt.
Dựa trên đó, hãy tạo Task Doc thi công chuẩn. Vị trí lưu file trong `backend/docs/tasks/` tùy theo phạm vi:
- Nếu CHỈ Backend: Tạo một file `YYYY-MM-DD-<slug>.md`
- Nếu CHỈ Frontend: Tạo một file `YYYY-MM-DD-<slug>-frontend.md`
- Nếu CẢ HAI: Tạo HAI FILE độc lập (một file BE, một file FE như trên). Mỗi file phải TỰ ĐỨNG ĐƯỢC.

Ràng buộc tối thượng:
1. Tính tự đứng vững (Self-contained): Chép toàn bộ bối cảnh, hợp đồng dữ liệu, schema, và quyết định đã chốt vào Task Doc.
2. KHÔNG chứa chuỗi "tech_docs" hoặc bất kỳ link nào trỏ ngược về thư mục research/.
3. Mỗi file phải có danh sách DoD (Definition of Done) rõ ràng với các checkbox `[ ]`, có lệnh chạy test hoặc điều kiện nghiệm thu cụ thể.
4. (Nếu có FE): File Frontend phải chứa đủ hợp đồng API/mock data để thi công ngay mà không cần đọc file Backend.
```

### Bước 4: Giao việc & Thi công
*(Sau khi có Task Doc, bạn tiến hành giao việc thi công từng phần theo prompt)*

**Prompt cho Gemini:**
```text
[THI CÔNG CODE]
Bám sát Task Doc: `backend/docs/tasks/YYYY-MM-DD-<slug>.md`, hạng mục: <Tên hạng mục>.
Nhiệm vụ:
1. Đọc kỹ file đích trước khi sửa. Giữ nguyên toàn bộ cấu trúc, hàm phụ trợ không thuộc phạm vi thay đổi.
2. Triển khai logic theo đúng hợp đồng đã chốt.
3. Bổ sung xử lý lỗi phòng thủ và logging đầy đủ.
4. Viết unit test tương ứng và chạy kiểm thử ngay sau khi hoàn thành.
```

## 5. Đang code mà gặp lỗi hoặc cần gỡ rối (Debug)

Khi gặp lỗi runtime hoặc test không pass, đừng chỉ đưa log và bảo Gemini "sửa đi". Hãy buộc AI phải tuân thủ quy trình debug.

**Prompt Debug khi có lỗi:**
```text
[DEBUG LỖI]
Đang gặp lỗi sau khi chạy thao tác:
<Dán log lỗi hoặc traceback vào đây>

Hãy thực hiện quy trình debug:
1. Phân tích nguyên nhân gốc rễ (Root cause) dựa trên file:line trong traceback.
2. Đề xuất phương án sửa lỗi tối thiểu (Minimal invasive fix), không refactor lan man.
3. Chỉ ra tác động phụ có thể có của bản vá này.
Sau khi tôi đồng ý, hãy áp dụng bản sửa lỗi.
```

## 6. Sổ tay Git Workflow & Quản lý Thư mục

### Quy tắc Git Bất biến
1. **Không code trực tiếp trên `dev`:** Luôn tạo nhánh `feat/<slug>` hoặc `fix/<slug>`.
2. **Không tự commit/push:** AI chỉ làm khi có lệnh rõ ràng từ người dùng.
3. **Commit message chuẩn:** `<type>(<scope>): <mô tả>`.
4. **Kiểm tra rò rỉ:** File code ở Backend/Frontend không được trỏ link về `tech_docs/`.

### Một thư mục tính năng có gì?
Trong quá trình làm việc, thư mục `research` sẽ chứa các bản nháp, còn bản chốt thật sự nằm ở `docs/tasks`:
```text
tech_docs/research/<slug>/
├── 00-desc.md               ← BẠN viết bằng lời thường
├── 01-plan.md ← GEMINI viết, có thể sửa đổi nhiều lần
└── qa.md                     ← Nhật ký hỏi đáp lúc thi công (tùy chọn)

backend/docs/tasks/
└── YYYY-MM-DD-<slug>.md      ← Bản chốt cuối cùng (Task Doc)
```

## 7. Bảng Kiểm soát Chất lượng Prompt

Trước khi gửi một yêu cầu phức tạp cho Gemini, hãy tự rà soát:

| Tiêu chí | Đã đạt? | Mô tả kiểm tra |
|---|:---:|---|
| **Rõ ràng vị trí neo** | [ ] | Đã chỉ định file/module/bản đồ cụ thể chưa, hay đang hỏi chung chung? |
| **Bắt buộc dẫn chứng** | [ ] | Đã có câu lệnh ép dẫn chứng `file:line` thực tế chưa? |
| **Giới hạn phạm vi (Non-goals)** | [ ] | Đã ghi rõ những gì KHÔNG ĐƯỢC LÀM để tránh AI mở rộng tùy tiện chưa? |
| **Tách biệt pha** | [ ] | Có đang ép vừa nghiên cứu vừa viết code ngay trong 1 prompt không? (Nên tách riêng). |
| **Không rò rỉ tech_docs** | [ ] | Khi sinh Task Doc hay sửa code, đã nhấn mạnh cấm chuỗi `tech_docs` chưa? |
| **DoD đo lường được** | [ ] | Tiêu chuẩn nghiệm thu đã có lệnh test hoặc điều kiện kiểm tra rõ ràng chưa? |
