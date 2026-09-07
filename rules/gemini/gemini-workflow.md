# Sổ tay Kỹ thuật Prompting & Quy trình Làm việc với Gemini

> **📌 Định vị:** Đây là tài liệu hướng dẫn kỹ thuật tương tác và xử lý **Prompt Engineering** chuyên sâu với Gemini (Google Antigravity / Gemini Code Assist / Gemini CLI).
> **Trọng tâm:** Tối ưu hóa cấu trúc prompt để khai thác tối đa năng lực đọc hiểu codebase sâu rộng, nghiên cứu kiến trúc chính xác (zero-hallucination) và sinh mã nguồn chất lượng cao, bám sát nghiệp vụ hệ thống.
> Quy ước chung repo: [`../../docs-convention.md`](../../docs-convention.md).

---

## 1. Nguyên lý Prompting Dựa trên Sự thật Mã nguồn (Fact-Grounded Prompting)

Mô hình ngôn ngữ lớn khi làm việc trên codebase quy mô lớn rất dễ rơi vào hai bẫy:
1. **Suy diễn (Hallucination):** Tự bịa ra tên hàm, tên bảng, tham số API hoặc hành vi hệ thống dựa trên thói quen tổng quát thay vì code thực tế.
2. **Lạc đề / Mở rộng phạm vi (Scope Creep):** Tự ý refactor các đoạn code không liên quan, thay đổi kiến trúc hiện có mà không có chỉ thị.

Để đạt được chất lượng nghiên cứu và viết code tối đa, mọi prompt gửi tới Gemini cần tuân thủ **Khung cấu trúc 5 thành phần (5-Element Prompt Framework)**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      KHUNG CẤU TRÚC PROMPT CHUẨN                       │
├────────────────────────────────────────────────────────────────────────┤
│ 1. [VỊ TRÍ NEO & NGỮ CẢNH]   (Anchor Context & Maps)                   │
│    Chỉ định file bản đồ, module, commit SHA hoặc khu vực liên quan.    │
├────────────────────────────────────────────────────────────────────────┤
│ 2. [Ý ĐỒ NGHIỆP VỤ & MỤC TIÊU] (Business Goal & User Intent)          │
│    Mô tả từ góc nhìn người dùng/nghiệp vụ: Ai dùng? Ở đâu? Cần gì?   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. [PHẠM VI & NON-GOALS]     (Scope Boundaries)                        │
│    Nêu rõ cái LÀM và cái TUYỆT ĐỐI KHÔNG ĐƯỢC ĐỤNG TỚI lần này.        │
├────────────────────────────────────────────────────────────────────────┤
│ 4. [RÀNG BUỘC KỸ THUẬT & DẪN CHỨNG] (Constraints & Hard Proofs)       │
│    Ép buộc bằng chứng file:line, schema DB, cơ chế locking/trans.      │
├────────────────────────────────────────────────────────────────────────┤
│ 5. [ĐỊNH DẠNG ĐẦU RA MONG MUỐN] (Expected Output Format)              │
│    Chỉ định file kết quả, bảng so sánh, hợp đồng API, hay diff code.   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Kỹ thuật Prompting cho Giai đoạn 1: Nghiên cứu & Khảo sát (Research & Deep Recon)

Nghiên cứu chất lượng cao là điều kiện tiên quyết để code không phát sinh lỗi tiềm ẩn. Không bắt đầu viết code khi chưa nắm rõ hiện trạng và các tác động phụ (side-effects).

### 2.1. Kỹ thuật Prompt "Trinh sát Mã nguồn" (Code Reconnaissance Prompt)
Khi khảo sát một tính năng mới hoặc một bug phức tạp, prompt phải ép mô hình dùng các công cụ tìm kiếm (`grep_search`, `view_file`, `list_dir`) để lần theo luồng thực thi từ đầu đến cuối (End-to-End trace).

* **Công thức prompt:**
  1. Chỉ định điểm bắt đầu (Endpoint, UI Button, Event handler).
  2. Yêu cầu truy vết đường đi của dữ liệu: `Router -> Service -> Worker/Job -> Database/External API`.
  3. Bắt buộc mọi khẳng định phải có dẫn chứng `file:line`.

* **Prompt mẫu Khảo sát Hiện trạng:**
  ```text
  [KHẢO SÁT HIỆN TRẠNG]
  Tôi muốn tìm hiểu luồng xử lý của tính năng: <Mô tả tính năng, ví dụ: xuất tài liệu sang PDF và lưu thumbnail>.
  
  Hãy đối chiếu với tech_docs/overview/repo-map.md và thực hiện trinh sát codebase thực tế:
  1. Lần vết từ router tiếp nhận request đến service xử lý logic và worker chạy nền (nếu có).
  2. Liệt kê chính xác:
     - Các router và endpoint liên quan (kèm file:line).
     - Các bảng dữ liệu (model/schema) bị đọc hoặc ghi.
     - Các job nền hoặc queue liên quan.
  3. Trích dẫn đoạn mã then chốt (mỗi đoạn không quá 25 dòng).
  4. Nêu rõ các hạn chế hoặc điểm nghẽn hiện tại của luồng này.
  
  Yêu cầu bắt buộc: Mọi nhận định đều phải có bằng chứng file:line trong codebase hiện tại. Không suy đoán mò mẫm.
  ```

### 2.2. Kỹ thuật Prompt "Kiểm chứng Giả định" (Hypothesis-Testing Prompt)
Khi bắt đầu một bài toán kỹ thuật, chúng ta thường có sẵn một số giả định về cách hệ thống hoạt động. Hãy biến các giả định đó thành các bài kiểm tra nhị phân (Đúng/Sai) có chứng cứ.

* **Prompt mẫu Kiểm chứng Giả định:**
  ```text
  [KIỂM CHỨNG GIẢ ĐỊNH]
  Trước khi thiết kế phương án cho <tính năng/vấn đề>, hãy kiểm chứng các giả định sau trong codebase:
  - Giả định 1: <Ví dụ: Bảng document_versions đã có cột lưu metadata JSON của công thức toán>.
  - Giả định 2: <Ví dụ: Endpoint SSE chat hiện tại đã có cơ chế catch-up khi client rớt mạng>.
  - Giả định 3: <Ví dụ: Worker xử lý chuyển đổi file chạy đồng bộ hay bất đồng bộ qua Redis queue?>.
  
  Trả về bảng kết quả theo định dạng:
  | # | Giả định | Kết luận (Đúng / Sai / Một phần) | Bằng chứng thực tế (file:line) | Ghi chú kỹ thuật |
  ```

### 2.3. Kỹ thuật Prompt "Phản biện Kiến trúc & Đánh đổi" (Architectural Trade-offs Prompt)
Đừng yêu cầu Gemini đưa ra duy nhất một giải pháp. Hãy yêu cầu đưa ra ít nhất 2 phương án đối lập kèm theo phân tích đánh đổi (Trade-offs) và đóng vai trò người phản biện (Devil's Advocate).

* **Prompt mẫu Phản biện Kiến trúc:**
  ```text
  [THIẾT KẾ & ĐÁNH ĐỔI]
  Về bài toán <mô tả bài toán>, hãy đề xuất 2 phương án kiến trúc khả thi:
  - Phương án A: <Ý tưởng 1, ví dụ: Xử lý streaming trực tiếp từ worker qua SSE redis pub/sub>.
  - Phương án B: <Ý tưởng 2, ví dụ: Lưu trạng thái vào DB và client polling theo chu kỳ>.
  
  Phân tích chi tiết cho từng phương án:
  1. Ưu điểm & Nhược điểm kỹ thuật.
  2. Tác động tới tài nguyên hệ thống (DB connections, memory, CPU, latency).
  3. Độ phức tạp khi triển khai và rủi ro hồi quy (regression risk) trên code hiện tại.
  4. Các trường hợp biên (edge cases) có thể làm hỏng phương án: Mất mạng, timeout, dữ liệu siêu lớn, tranh chấp ghi (concurrency).
  5. Khuyến nghị phương án tối ưu cho hệ thống hiện tại kèm lý do xác đáng.
  ```

### 2.4. Kỹ thuật Prompt "Đóng gói Hồ sơ Nghiên cứu"
Sau khi thảo luận và chốt phương án, yêu cầu Gemini xuất toàn bộ kết quả vào một tài liệu nghiên cứu duy nhất: `tech_docs/research/<slug>/01-khao-sat-va-thiet-ke.md`.

* **Prompt mẫu Đóng gói Nghiên cứu:**
  ```text
  [XUẤT TÀI LIỆU NGHIÊN CỨU]
  Hãy tổng hợp toàn bộ hiện trạng, các giả định đã xác minh, và phương án thiết kế vừa thống nhất vào file:
  tech_docs/research/<slug>/01-khao-sat-va-thiet-ke.md
  
  Cấu trúc tài liệu phải tuân thủ chuẩn:
  1. Mục tiêu nghiệp vụ (Người dùng muốn gì, hiện trạng, non-goals).
  2. Khảo sát hiện trạng (Có trích dẫn file:line, schema, luồng dữ liệu).
  3. Bảng đối chiếu giả định & xác minh thực tế.
  4. Phương án thiết kế đã chọn (Kiến trúc, hợp đồng API request/response, luồng BE/FE).
  5. Đánh đổi & phương án thay thế.
  6. Quyết định đã chốt (Liệt kê rõ các ràng buộc kỹ thuật đã thống nhất).
  7. Bước tiếp theo (Chuẩn bị sinh Task Doc).
  ```

---

## 3. Kỹ thuật Prompting cho Giai đoạn 2: Lập Task Doc Chuẩn Giao Việc

Task Doc (`backend/docs/tasks/`) là tài liệu hợp đồng kỹ thuật kết nối giữa nghiên cứu và lập trình. Đây là nơi các quyết định được cố định hóa thành hướng dẫn thi công rõ ràng.

### 3.1. Ràng buộc Cốt lõi: Tính Độc Lập Tuyệt Đối (Self-Contained Rule)
> [!IMPORTANT]
> **RÀNG BUỘC CỨNG: TASK DOC TUYỆT ĐỐI KHÔNG CHỨA ĐƯỜNG DẪN `tech_docs/`**
> Repo code (`bookforge`, `bookforge-fe`) và repo tài liệu nghiên cứu (`tech_docs`) là các kho lưu trữ độc lập. Người nhận việc hoặc quy trình CI/CD chỉ mở thư mục repo code và **không có quyền truy cập vào `tech_docs/`**.
> Mọi đường dẫn trỏ tới `tech_docs/...` đều trở thành **link chết**.

### 3.2. Prompt Sinh Task Doc Chuẩn Hợp Đồng
Prompt phải yêu cầu Gemini chép đầy đủ toàn bộ bối cảnh, quyết định, hợp đồng API và tiêu chí nghiệm thu (DoD) vào thẳng Task Doc, không tham chiếu ngược.

* **Prompt mẫu Sinh Task Doc:**
  ```text
  [SINH TASK DOC GIAO VIỆC]
  Dựa trên phương án đã chốt trong tech_docs/research/<slug>/01-khao-sat-va-thiet-ke.md, hãy tạo Task Doc thi công chuẩn theo docs-convention:
  - Phía Backend:  backend/docs/tasks/YYYY-MM-DD-<slug>.md
  - Phía Frontend (nếu có): backend/docs/tasks/YYYY-MM-DD-<slug>-frontend.md
  
  Quy tắc bắt buộc:
  1. Tính tự đứng vững (Self-contained): Chép toàn bộ bối cảnh, hợp đồng dữ liệu, schema, và quyết định đã chốt vào file.
  2. RÀNG BUỘC CỨNG: Tuyệt đối KHÔNG chứa chuỗi "tech_docs" hoặc bất kỳ đường dẫn nào trỏ sang thư mục tech_docs.
  3. Mục "Hiện trạng đã kiểm chứng": Ghi rõ mốc ngày, các file và dòng code thực tế trong repo code.
  4. Mục "Phạm vi / Ngoài phạm vi": Ghi rõ ranh giới việc làm và việc KHÔNG làm.
  5. Mục "Việc cần làm": Chia thành các bước tuần tự rõ ràng (Schema -> Service -> API/Worker -> Tests).
  6. Mục "DoD — hoàn thành khi": Danh sách các checkbox [ ] kiểm thử cụ thể, có lệnh chạy test, điều kiện pass/fail đo lường được.
  7. Nếu có cả BE và FE: Tách làm 2 file riêng biệt. File FE phải chép trọn vẹn hợp đồng API/SSE/Types để người làm FE không cần đọc file BE.
  ```

---

## 4. Kỹ thuật Prompting cho Giai đoạn 3: Thi công Mã Nguồn (Implementation)

Để Gemini viết code chuẩn xác, không bị sót logic và không phá vỡ cấu trúc hiện tại, việc chia nhỏ bài toán (Task Chunking) và prompting phòng thủ là cực kỳ quan trọng.

### 4.1. Chiến thuật "Chia để trị" (Chunked Implementation Strategy)
Tuyệt đối không gửi prompt yêu cầu "viết toàn bộ tính năng này". Hãy chia việc thi công thành các lát cắt nhỏ (slices) có thể kiểm chứng độc lập:

```text
LÁT CẮT 1: Schema / Database Migration & Pydantic Models
    ▼ (Kiểm tra syntax, migration chạy thử)
LÁT CẮT 2: Business Logic / Service Layer
    ▼ (Viết unit test cô lập cho service)
LÁT CẮT 3: API Router / Worker Job / SSE Stream
    ▼ (Kiểm tra endpoint bằng curl/integration test)
LÁT CẮT 4: Frontend Integration & State Handling
    ▼ (Kiểm tra UI component, type-safety, render)
LÁT CẮT 5: End-to-End Verification & DoD Audit
```

### 4.2. Kỹ thuật Prompt "Lập trình Phòng thủ & Không Phá hủy" (Defensive Coding Prompt)
Khi yêu cầu Gemini sửa hoặc viết code, luôn đính kèm các ràng buộc về an toàn mã nguồn:
- Đọc kỹ toàn bộ file trước khi chỉnh sửa.
- Không xoá bỏ các hàm tiện ích hoặc comment hiện có không liên quan.
- Tuân thủ nghiêm ngặt type annotations và coding convention của repo.
- Xử lý đầy đủ các lỗi ngoại lệ (exception handling) và logging có cấu trúc.

* **Prompt mẫu Thi công từng Module:**
  ```text
  [THI CÔNG CODE — BƯỚC <X>]
  Bám sát Task Doc: backend/docs/tasks/YYYY-MM-DD-<slug>.md, hạng mục: <Tên hạng mục cụ thể>.
  
  Nhiệm vụ:
  1. Đọc kỹ file đích trước khi sửa: <Đường dẫn file>.
  2. Triển khai logic theo đúng hợp đồng và quyết định đã chốt trong Task Doc.
  3. Ràng buộc an toàn:
     - Giữ nguyên toàn bộ cấu trúc, hàm phụ trợ và comment hiện có không thuộc phạm vi sửa đổi.
     - Sử dụng đúng type hints chuẩn Python/TypeScript của dự án.
     - Bổ sung xử lý lỗi phòng thủ: Ghi log có context (request_id, org_id, v.v.), không nuốt lỗi (silent fail).
  4. Sau khi viết code, chạy linter hoặc cú pháp để đảm bảo không có lỗi runtime cơ bản.
  ```

### 4.3. Kỹ thuật Prompt "Kiểm thử đi trước một bước" (Test-Driven Prompting)
Để đảm bảo mã nguồn hoạt động chính xác, yêu cầu Gemini viết test hoặc chạy test case cụ thể ngay khi hoàn thành module.

* **Prompt mẫu Viết & Chạy Test:**
  ```text
  [VIẾT & CHẠY KIỂM THỬ]
  Viết unit test cho logic vừa triển khai tại: <Đường dẫn file test, ví dụ: tests/unit/test_thinking_agent.py>.
  
  Yêu cầu kiểm thử:
  1. Bao phủ luồng chuẩn (Happy path): Dữ liệu hợp lệ, kết quả trả về đúng định dạng mong đợi.
  2. Bao phủ ít nhất 3 trường hợp biên / lỗi (Edge cases / Error paths):
     - Dữ liệu đầu vào rỗng hoặc sai kiểu.
     - Dịch vụ phụ trợ / LLM timeout hoặc trả về mã lỗi.
     - Xử lý ngắt kết nối giữa chừng (Client disconnect).
  3. Chạy test bằng lệnh thích hợp (ví dụ: pytest <file_path>) và báo cáo kết quả chi tiết từng test case.
  ```

### 4.4. Kỹ thuật Prompt "Rà soát Tiêu chuẩn Hoàn thành (DoD Audit Prompt)"
Khi hoàn thành toàn bộ mã nguồn, dùng prompt đối chiếu để kiểm tra độc lập lại từng tiêu chí trong DoD.

* **Prompt mẫu Rà soát DoD:**
  ```text
  [RÀ SOÁT ĐỘC LẬP THEO DOD]
  Mở Task Doc backend/docs/tasks/YYYY-MM-DD-<slug>.md và rà soát mục "DoD — hoàn thành khi":
  
  1. Đi qua từng checkbox trong danh sách DoD.
  2. Với mỗi mục, chỉ ra bằng chứng cụ thể đã đạt được:
     - Lệnh kiểm thử đã chạy và output pass.
     - Đoạn code/file cụ thể đã hoàn thành.
  3. Quét toàn bộ các file mới và file sửa đổi xem có vi phạm:
     - Còn sót chuỗi "tech_docs" không?
     - Còn sót TODO/FIXME chưa giải quyết không?
     - Còn file tạm hay console.log / print debug không?
  4. Nếu tất cả đều đạt, cập nhật đánh dấu [x] vào các checkbox tương ứng trong Task Doc.
  ```

---

## 5. Kỹ thuật Prompting cho Git Workflow & Bản đồ Repo

Quy tắc Git trong dự án được kiểm soát nghiêm ngặt nhằm tránh làm hỏng nhánh chung hoặc rò rỉ dữ liệu nghiên cứu nội bộ.

### 5.1. Quy tắc Git Bất biến
1. **Không bao giờ code trực tiếp trên `dev`:** Luôn tạo nhánh `feat/<slug>` hoặc `fix/<slug>`.
2. **Không tự ý commit, không tự ý push:** Chỉ thực hiện khi có lệnh rõ ràng từ người dùng.
3. **Commit message chuẩn Conventional Commits tiếng Anh:** `<type>(<scope>): <mô tả>`.
4. **Không watermark AI:** Tuyệt đối không thêm `Co-Authored-By: ...` hay các dấu hiệu AI vào commit/code.
5. **Kiểm tra rò rỉ link:** Chạy kiểm tra không có file tài liệu trong `backend/` hay `frontend/` trỏ về `tech_docs/`.

### 5.2. Prompt mẫu Điều khiển Git Workflow
* **Prompt Tạo nhánh:**
  ```text
  Kiểm tra trạng thái git hiện tại. Nếu đang ở dev, hãy tạo nhánh mới feat/<slug> từ commit mới nhất và chuyển sang nhánh đó.
  ```

* **Prompt Yêu cầu Commit (Chờ lệnh người dùng):**
  ```text
  Hãy kiểm tra lại git status và git diff. Nếu mọi thứ đã sẵn sàng và test đã pass, hãy đề xuất commit message chuẩn theo định dạng <type>(<scope>): <desc> bằng tiếng Anh và hỏi xác nhận từ tôi trước khi thực hiện commit.
  ```

* **Prompt Cập nhật Bản đồ Repo (`repo-map.md`):**
  ```text
  [CẬP NHẬT BẢN ĐỒ REPO]
  Sau khi hoàn thành tính năng <tên tính năng>:
  1. Kiểm tra xem có router mới, bảng DB mới, job nền mới hoặc biến môi trường mới nào không.
  2. Nếu có, cập nhật mục tương ứng trong tech_docs/overview/repo-map.md.
  3. Cập nhật mốc SHA ở header của repo-map.md phản ánh đúng trạng thái commit hiện tại.
  ```

---

## 6. Sổ tay Prompt Mẫu Thực Chiến (Ready-to-Use Prompt Bank)

Dưới đây là các mẫu prompt hoàn chỉnh, bạn có thể sao chép, điền thông tin vào các dấu ngoặc `<...>` và gửi trực tiếp cho Gemini:

### 📋 Mẫu 1: Khởi động Nghiên cứu Tính năng Mới
```text
Tôi muốn nghiên cứu và triển khai tính năng: <Tên và mô tả tính năng>.

Bối cảnh & Nghiệp vụ:
- Mục tiêu người dùng: <Người dùng muốn làm gì và nhận được gì?>
- Màn hình / Điểm chạm: <Màn hình nào, nút bấm nào?>
- Phạm vi không làm: <Những gì KHÔNG thuộc phạm vi đợt này>

Hãy thực hiện:
1. Đọc tech_docs/overview/repo-map.md để định vị các module liên quan.
2. Dùng các công cụ tra cứu mã nguồn thực tế để vẽ lại luồng dữ liệu hiện tại (kèm dẫn chứng file:line).
3. Xác minh các điểm phụ thuộc (DB schema, API có sẵn, worker queues).
4. Tạo tài liệu nghiên cứu ban đầu tại tech_docs/research/<slug>/01-khao-sat-va-thiet-ke.md.
```

### 🔍 Mẫu 2: Phản biện Kỹ thuật & Edge Cases
```text
Xem xét phương án thiết kế hiện tại trong tech_docs/research/<slug>/01-khao-sat-va-thiet-ke.md.
Hãy đóng vai trò Kỹ sư Trưởng (Staff Engineer) cực kỳ khắt khe:
1. Chỉ ra ít nhất 3 điểm yếu lớn nhất của phương án này (về bảo mật, hiệu năng, hoặc tính toàn vẹn dữ liệu).
2. Điều gì sẽ xảy ra trong các kịch bản cực đoan:
   - Request bị gián đoạn giữa chừng khi đang ghi dữ liệu.
   - Kích thước payload vượt quá giới hạn thông thường (10x).
   - 2 người dùng cùng thao tác đồng thời trên cùng một tài nguyên (Race condition).
3. Đề xuất cách phòng thủ cụ thể cho từng kịch bản.
```

### 📝 Mẫu 3: Xuất Bộ Đôi Task Doc (Backend & Frontend)
```text
Phương án thiết kế trong tech_docs/research/<slug>/01-khao-sat-va-thiet-ke.md đã được duyệt.
Hãy tạo 2 file Task Doc độc lập trong backend/docs/tasks/:
1. backend/docs/tasks/YYYY-MM-DD-<slug>.md (Cho phần Backend)
2. backend/docs/tasks/YYYY-MM-DD-<slug>-frontend.md (Cho phần Frontend)

Ràng buộc tối thượng:
- Không chứa chuỗi "tech_docs" hay bất kỳ link nào trỏ ra ngoài repo code.
- File Frontend phải tự chứa toàn bộ hợp đồng API, sự kiện SSE (event names, payloads), mock data mẫu và mã lỗi để người làm FE thi công mà không cần mở file Backend.
- Mỗi file phải có danh sách DoD rõ ràng, kiểm chứng được bằng lệnh hoặc tiêu chí hiển thị cụ thể.
```

### 💻 Mẫu 4: Thi công Code từng Bước theo Task Doc
```text
Bắt đầu thi công Bước <Số bước, ví dụ: Bước 2: Thêm Worker Handler> trong Task Doc:
backend/docs/tasks/YYYY-MM-DD-<slug>.md.

Yêu cầu thi công:
1. Tạo hoặc sửa đúng các file được nêu trong mục này.
2. Đảm bảo code chặt chẽ: Có type hint đầy đủ, log thông tin lỗi rõ ràng.
3. Không tự ý sửa các file ngoài phạm vi bước này.
4. Viết ngay unit test tương ứng trong thư mục tests/.
5. Chạy test và đưa ra kết quả thực thi.
```

### 🛠️ Mẫu 5: Debug Lỗi Phát sinh Trong Quá trình Chạy
```text
Đang gặp lỗi sau khi chạy <lệnh test hoặc thao tác nghiệp vụ>:
<Dán log lỗi hoặc traceback vào đây>

Hãy thực hiện quy trình debug 3 bước:
1. Phân tích nguyên nhân gốc rễ (Root cause): Vì sao lỗi xảy ra dựa trên traceback và mã nguồn thực tế (nêu rõ file:line)?
2. Đề xuất phương án sửa lỗi tối thiểu (Minimal invasive fix): Chỉ sửa đúng chỗ hỏng, không refactor lan man.
3. Kiểm tra tác động phụ: Phương án sửa này có ảnh hưởng tới các luồng khác đang dùng chung hàm/bảng này không?
Sau khi tôi đồng ý, hãy áp dụng bản sửa lỗi và chạy lại test kiểm chứng.
```

---

## 7. Bảng Kiểm soát Chất lượng Prompt (Prompt Quality Checklist)

Trước khi gửi một yêu cầu phức tạp cho Gemini, hãy tự rà soát:

| Tiêu chí | Đã đạt? | Mô tả kiểm tra |
|---|:---:|---|
| **Rõ ràng vị trí neo** | [ ] | Đã chỉ định file/module/bản đồ cụ thể chưa, hay đang hỏi chung chung? |
| **Bắt buộc dẫn chứng** | [ ] | Đã có câu lệnh ép dẫn chứng `file:line` thực tế chưa? |
| **Giới hạn phạm vi (Non-goals)** | [ ] | Đã ghi rõ những gì KHÔNG ĐƯỢC LÀM để tránh AI mở rộng tùy tiện chưa? |
| **Tách biệt pha** | [ ] | Có đang ép vừa nghiên cứu vừa viết code ngay trong 1 prompt không? (Nên tách riêng). |
| **Không rò rỉ tech_docs** | [ ] | Khi sinh Task Doc hay sửa code, đã nhấn mạnh cấm chuỗi `tech_docs` chưa? |
| **DoD đo lường được** | [ ] | Tiêu chuẩn nghiệm thu đã có lệnh test hoặc điều kiện kiểm tra rõ ràng chưa? |
