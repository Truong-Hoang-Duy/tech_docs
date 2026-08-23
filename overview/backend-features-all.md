# BookForge Backend — Bản đồ chức năng

> Nguồn: `backend/services/api` (FastAPI + RQ worker + cron), cùng 3 dịch vụ phụ trợ: `knowledge-ingestion`, `knowledge-retrieval`, `gotenberg`.
> Tài liệu mô tả logic xử lý ở mức tổng quan, không đi sâu kỹ thuật.

---

## 1. Nền tảng tài khoản & tổ chức

**Xác thực và hồ sơ người dùng** — `backend/services/api/src/bookforge_api/api/auth.py`
+ Đăng nhập/đăng xuất bằng session cookie lưu trong bảng `sessions`; xem/sửa hồ sơ, đổi avatar (upload file hoặc chọn từ thư viện avatar dựng sẵn), quên mật khẩu qua token gửi email, và luồng "account setup" cho tài khoản do admin tạo (nhận link mời → tự đặt mật khẩu → chấp nhận điều khoản).

**Quản trị người dùng (Admin)** — `backend/services/api/src/bookforge_api/api/admin.py`
+ Admin tạo/sửa/xóa mềm người dùng trong tổ chức của mình, gửi lại thư mời, reset mật khẩu, và kích hoạt gói thuê bao. Có cơ chế chặn admin thao tác lên admin ngang cấp.

**Hồ sơ tổ chức** — `backend/services/api/src/bookforge_api/api/organizations.py`
+ Mỗi tổ chức có tên, logo riêng; toàn bộ dữ liệu (tài liệu, câu hỏi, quota) đều nằm trong "cây" của tổ chức đó — đây là ranh giới cách ly dữ liệu chính của hệ thống.

**Năm học & học kỳ** — `backend/services/api/src/bookforge_api/api/academic_years.py`
+ Khai báo năm học hiện hành và các học kỳ để làm khung phân loại cho tài liệu/ngân hàng câu hỏi.

---

## 2. Quản lý tài liệu

**Tải lên và quản lý tài liệu** — `backend/services/api/src/bookforge_api/api/documents.py`
+ Nhận PDF / DOCX / PPTX / ảnh, lưu file gốc vào storage, tạo bản ghi `documents`, rồi đẩy một job vào hàng đợi Redis (RQ) để worker xử lý nền. Hỗ trợ thư mục (`document_folders.py`), thùng rác (xóa mềm → khôi phục → xóa vĩnh viễn), phân trang và lọc theo loại file/trạng thái.

**Tạo tài liệu từ câu trả lời AI**
+ Endpoint `POST /api/documents/from-chat-message`: bấm "Chỉnh sửa" trên một câu trả lời trong chat → nội dung đó biến thành tài liệu **có thể sửa** và mở thẳng trong canvas. Đây là con đường chính để có tài liệu editable, vì file người dùng upload mặc định là **chỉ đọc**.

**Chia sẻ tài liệu** — `.../shares`
+ Chia sẻ cho từng người trong tổ chức với quyền `viewer` hoặc `editor`; ngoài ra có mức hiển thị private/public. Quyền hiệu lực được tính gộp ở `services/access.py` theo thứ tự: chủ sở hữu → được chia sẻ → công khai → admin.

**Xử lý tài liệu (ingest pipeline)** — `backend/services/api/src/bookforge_api/ingest/pipeline.py`
+ Chạy trong worker nền, gồm chuỗi bước: tách trang PDF → nhận diện văn bản (ưu tiên "born-digital" nếu PDF đã có text, ngược lại gọi OCR bằng Mistral/Gemini) → ghép thành Markdown theo trang → sửa cấp bậc tiêu đề → trích xuất hình ảnh/biểu đồ và nhờ LLM mô tả chúng → dựng cây mục lục → sinh HTML cho editor → tóm tắt tài liệu → đẩy Markdown sang dịch vụ knowledge để lập chỉ mục RAG. Tiến độ được ghi lại nên frontend hiển thị được thanh %.
+ Có endpoint `reprocess` (xử lý lại) và `knowledge/reindex` (lập chỉ mục lại) khi kết quả chưa tốt.

**Xem trước & tải về** — `preview`, `source-preview.pdf`, `export`, `download`
+ Ba nguồn byte khác nhau: file gốc, bản PDF dựng lại để xem, và bản render từ nội dung đã OCR. `services/download_options.py` là nơi duy nhất quyết định menu tải về hiển thị định dạng nào và định dạng nào bị khóa (kèm lý do). Chuyển đổi sang PDF đi qua sidecar **Gotenberg**; xuất DOCX dựng bằng `export/docx_builder.py` (giữ bảng, ảnh, công thức toán qua OMML).

---

## 3. Canvas (trình soạn thảo) và AI trong canvas

**Đọc/lưu nội dung canvas** — `backend/services/api/src/bookforge_api/api/editor.py`
+ `GET`/`PUT` nội dung tài liệu dạng HTML, có kiểm tra version để tránh hai người ghi đè nhau. Tài liệu upload bị khóa ở chế độ chỉ đọc theo thiết kế.

**Điều chỉnh nội dung canvas bằng AI (Canvas Agent)** — `backend/services/api/src/bookforge_api/chat/editor_agent.py`
+ Đây là chức năng trung tâm. Một lượt hỏi là một request JSON (không streaming), diễn ra như sau:
  1. Nhận yêu cầu + vị trí con trỏ / vùng đang bôi đen của người dùng.
  2. Cắt tài liệu thành các **block có ID** (`editor/block_document.py`) để agent thao tác chính xác từng khối thay vì viết lại cả bài.
  3. Dựng agent (PydanticAI) với bộ công cụ: `get_outline` (xem mục lục), `read_blocks`, `search_document`, `update_block`, `insert_blocks`, `delete_blocks`, `move_block`; thêm `retrieve_knowledge` khi tài liệu đã được lập chỉ mục RAG; thêm bộ công cụ hình học và công cụ định dạng văn bản pháp lý khi được bật.
  4. Agent lặp gọi công cụ cho tới khi xong, hệ thống so sánh trước/sau (`editor/block_diff.py`) và trả về một **change_set**.
  5. Frontend hiện lớp phủ "xem trước thay đổi"; người dùng bấm Đồng ý thì áp dụng trong một transaction duy nhất.
+ Lịch sử hội thoại được lưu server-side trong `canvas_chat_sessions` / `canvas_chat_messages`, nên các lượt sau có ngữ cảnh. Mỗi lượt đều bị đo quota và ghi nhận chi phí token.

**Mini-tools trên vùng bôi đen** — `backend/services/api/src/bookforge_api/api/assistant_tools.py`
+ 6 công cụ một-lượt, chỉ tác động lên đoạn đang chọn: Viết lại, Soát chính tả, Rút gọn, Đổi văn phong, Viết tiếp, Quét rủi ro. Không có bộ nhớ hội thoại, trả kết quả để người dùng xem trước rồi áp dụng.

**Hình học động (JSXGraph)** — `services/geometry/`, `services/jsxgraph/`
+ Người dùng mô tả bằng lời ("Vẽ tam giác ABC vuông tại A"), hệ thống chuyển thành đặc tả hình học, **giải bằng nhân toán học riêng** (`math_kernel`) chứ không để LLM tự bịa tọa độ, kiểm chứng lại các ràng buộc (`verifier`, `eval_oracle`), rồi sinh SVG + block JSXGraph nhúng vào tài liệu. Có endpoint xem trước, tạo, sửa, và phục vụ file hình.

---

## 4. Chat (ngoài canvas)

**Hội thoại có trích dẫn tài liệu (RAG)** — `api/chat.py`, `chat/adk_agent.py`
+ Người dùng chọn một số tài liệu làm phạm vi, đặt câu hỏi. Hệ thống viết lại câu hỏi cho rõ ngữ cảnh (xử lý câu hỏi kiểu "cái đó là gì?"), truy xuất đoạn liên quan bằng **kết hợp vector search (dịch vụ knowledge-retrieval) và BM25 + ưu tiên theo số trang** (`chat/retrieval.py`), rồi agent trả lời kèm **trích dẫn** trỏ về tên tài liệu / mục / trang.
+ Quản lý phiên chat: tạo, liệt kê (gộp cả phiên canvas), tự đặt tiêu đề từ câu hỏi đầu tiên, sửa tên, xóa.

**Các chế độ chat**
+ `general` (hỏi đáp trên tài liệu đã chọn), `legal` / `legal_search` / `legal_drafting` (tra cứu và soạn thảo văn bản pháp lý, gọi sang dịch vụ **LawForge/Pháp điển** qua `law/client.py`; bản nháp soạn ra có thể lưu thành tài liệu và tự lập chỉ mục), và `expert` (agent chuyên gia gắn với một bộ corpus riêng — `chat/expert_tools.py`).
+ Có nhánh riêng nhận diện yêu cầu vẽ hình để trả về hình học thay vì văn bản.

**Điều hướng trong tài liệu khi chat** — `/api/documents/{id}/tree`, `/pages`, `/search`
+ Cho phép panel chat nhảy tới mục/trang được trích dẫn.

**Lớp quy tắc chung cho mọi agent** — `chat/governance.py`
+ Một khối "hiến pháp" tiếng Việt được chèn đầu system prompt của mọi agent: lập trường chủ quyền biển đảo, cấm bịa nguồn/trích dẫn, giữ giọng sư phạm, không lộ ID nội bộ, và chống prompt-injection (bỏ qua yêu cầu ghi đè quy tắc).

---

## 5. Sinh trình chiếu (PPTX)

**Tạo slide từ tài liệu** — `backend/services/api/src/bookforge_api/api/presentations.py`
+ Từ một tài liệu đã xử lý: sinh **dàn ý** trước (có bản streaming để hiện dần), người dùng duyệt/sửa, rồi mới dựng file .pptx. Nội dung có trích dẫn về tài liệu nguồn. Xuất được sang Google Slides (`integrations/google.py`).

**Tạo slide độc lập (không cần tài liệu)** — `backend/services/api/src/bookforge_api/api/standalone_presentations.py`
+ Chọn theme/template → sinh dàn ý từ chủ đề → dựng deck → xem trước PDF → lưu vào thư viện. Hỗ trợ chèn hình học vào slide.

**Hai engine dựng file** — `pptx/`
+ *Canva engine*: đọc cấu trúc "slot" từ file template đã gắn nhãn, ép output của LLM khớp đúng khung đó rồi điền vào (`canva_generate` + `canva_fill`).
+ *Grid engine*: bố cục theo lưới có catalog kiểm chứng, tự chọn bảng màu, tự đo chữ để không tràn khung (`grid_plan`, `grid_metrics`, `grid_validate`).
+ Ảnh minh họa có thể sinh bằng Gemini. Deck sinh ra được lưu thành `documents` loại `generated_slide`, có job nền finalize + render thumbnail.

**Quản lý template** — `api/pptx_templates.py`
+ Admin tải lên, đặt template mặc định, và cấp quyền dùng template cho từng tổ chức.

---

## 6. Ngân hàng câu hỏi & đề thi

**Thẻ câu hỏi (question cards)** — `backend/services/api/src/bookforge_api/api/question_cards.py`
+ CRUD thẻ câu hỏi có phân loại theo taxonomy (môn/lớp/chủ đề/mức độ), hỗ trợ 9 dạng câu hỏi, đính kèm ảnh, thùng rác, nhân bản, lọc đa tiêu chí.
+ **Sinh câu hỏi bằng AI** (`/generate`) và **chuyển đổi dạng câu hỏi** (`/convert`) — có validator ép công thức toán phải ở dạng LaTeX hợp lệ.
+ **Phát hiện trùng lặp** (`/check-duplicates`) và **kiểm tra chất lượng** (`/quality-check`).

**Quy trình duyệt câu hỏi**
+ Vòng đời: nháp → gán người duyệt → đặt độ ưu tiên → duyệt / từ chối / yêu cầu sửa. Có **phiên duyệt** (review session) để duyệt hàng loạt theo lô, hàng đợi duyệt, dashboard thống kê cho người quản lý và bảng điều khiển riêng cho reviewer.

**Thư mục, giỏ và bộ sưu tập** — `question_folders.py`, `question_cart.py`, `question_collections.py`
+ Thư mục dạng cây (có màu, cấu hình riêng); "giỏ" để nhặt dần câu hỏi khi duyệt rồi kết tinh thành bộ sưu tập hoặc đề thi.

**Đề thi** — `test_papers.py`
+ Ghép câu hỏi thành đề có phân mục, sắp xếp lại thứ tự, **đối chiếu ma trận đề** (`matrix-check`), sinh **đề hoán vị** (variants), sinh **phiếu đáp án** tự động, đồng bộ hai chiều với canvas (`canvas/regenerate`, `canvas-sync-status`) và làm mới khi câu hỏi nguồn thay đổi.

---

## 7. Quota, chi phí và giám sát

**Gói thuê bao & hạn mức** — `models/quota.py`, `services/quota_gate.py`
+ Mỗi tổ chức có một `subscription` gắn với một `quota_plan` quy định ~20 trần khác nhau: số người dùng, dung lượng lưu trữ, số tài liệu AI-ready, số trang đã xử lý, tổng token, số lượt AI, kích thước file upload, số tài liệu chọn được trong chat, số slide tối đa, số từ tối đa cho một lượt sửa canvas…
+ `quota_snapshots` giữ mức tiêu thụ hiện tại. Trước mỗi hành động tốn tài nguyên, hệ thống gọi một "cổng" kiểm tra (`assert_can_*`); nếu chặn thì trả lỗi kèm header `X-Quota-*` để frontend hiển thị. Sau hành động thì cộng dồn mức dùng.

**Ghi nhận chi phí LLM** — `services/provider_cost.py`, `services/token_rates.py`
+ Mỗi lần gọi model ghi lại số token vào/ra và quy ra tiền theo bảng giá. **Model nào chưa có dòng giá thì API từ chối khởi động** — chốt chặn để không có chi phí "vô hình".

**Định tuyến model theo tác vụ** — `core/settings.py`, `llm/model_router.py`
+ Khoảng 15 "operation" (chat, editor, geometry, question_bank, outline, summarize…) mỗi cái cấu hình được một model riêng qua biến môi trường; không cấu hình thì rơi về model mặc định. Người dùng cũng có thể chọn model ngay trên giao diện (registry ở `llm/model_registry.py`).

**Dashboard & thống kê** — `api/dashboard.py`, `api/storage_usage.py`
+ Tổng quan hoạt động cho người dùng, dashboard riêng cho admin, thống kê theo từng tài liệu, và bảng phân bổ dung lượng lưu trữ.

**Nhật ký hành vi** — bảng `ai_actions`, `event_log`, `retrieval_traces`
+ Mọi lượt gọi AI, mọi sự kiện nghiệp vụ và mọi lần truy xuất RAG đều được ghi lại kèm request-id để truy vết.

---

## 8. Hạ tầng chạy nền

**Worker & hàng đợi** — `workers/`
+ Redis/Valkey + RQ. Các job: xử lý tài liệu (ingest), lập chỉ mục knowledge, finalize deck vừa sinh, render thumbnail. Job dài được đặt timeout và có cơ chế chống chồng job.

**Tác vụ định kỳ (cron)** — `cron/runner.py`
+ 6 job: hết hạn thuê bao, dọn thùng rác, giải cứu ingest/reindex bị treo, đối soát lại số liệu quota với thực tế, cảnh báo tổ chức sắp chạm hạn mức.

**Lưu trữ** — `storage/`
+ Lưu file trên đĩa cục bộ (hoặc MinIO) theo cây thư mục của tổ chức, có bảng `storage_objects` để kế toán dung lượng, có "guard" kiểm tra còn đủ chỗ trước khi ingest PDF và tự dọn thư mục staging bỏ quên.

**Xử lý lỗi & i18n** — `errors/`
+ Toàn bộ lỗi trả về theo một cấu trúc thống nhất (mã lỗi + chi tiết), có middleware gắn request-id và ngôn ngữ; danh mục mã lỗi được tài liệu hóa ở `backend/docs/ERRORS.md`.

**Kiến trúc dịch vụ**
+ `api` (FastAPI, nơi team làm việc chính) · `knowledge-ingestion` + `knowledge-retrieval` (RAGFlow rút gọn, chỉ giữ đường ingest và `POST /api/v1/retrieval`) · `gotenberg` (render PDF) · `lawforge-bundle/phapdien-service` (tra cứu pháp điển) · hạ tầng dùng chung: Postgres, Valkey, MinIO, MySQL, Elasticsearch, Caddy.

---

## Nhận xét thêm

- **Trục thiết kế rõ nhất** là tách "tài liệu upload = chỉ đọc" khỏi "tài liệu do AI sinh = sửa được". Điều này giải thích vì sao muốn dùng canvas agent thì phải đi qua đường chat → "Chỉnh sửa" chứ không sửa trực tiếp file đã tải lên.
- **AI không được tin tưởng tuyệt đối ở những chỗ dễ sai**: hình học có nhân toán học kiểm chứng lại; sinh slide bị ép về khung template; sinh câu hỏi bị validator kiểm LaTeX; trả lời RAG bắt buộc trích dẫn. Đây là mẫu lặp lại xuyên suốt.
- **Quota là hệ thống ngang** cắt qua gần như mọi tính năng, không phải một module đứng riêng.
- Có dấu hiệu **hai thế hệ code song song** ở vài chỗ (ví dụ `chat/adk_agent.py` mang tên ADK nhưng đã chuyển sang PydanticAI; nhiều migration `reserved_noop`), gợi ý dự án đã qua vài lần tái cấu trúc lớn.
