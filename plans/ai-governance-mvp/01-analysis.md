# 01 — Phân tích MVP Quản trị & Giải trình Hoạt động AI (M01 → M08)

**Ngày:** 2026-11-03 · **Người phân tích:** Gemini · **Phía tác động:** Cả hai (`backend` + `frontend`)
**Nguồn đối chiếu:** [`BookForge_AI_Governance_MVP_Phase2_Scope_2026-11-02.md`](../../research/BookForge_AI_Governance_MVP_Phase2_Scope_2026-11-02.md) (Mục 4: MVP 1 — `M01` đến `M08`)
**Mốc code:** `backend@1727af5a` (`origin/dev`) · `frontend@bba2967a` (`origin/dev`)

---

## 1. Mục tiêu & Phạm vi MVP 1

- **Yêu cầu cốt lõi của MVP 1:** Thiết lập một vòng kiểm soát và giải trình thống nhất cho toàn bộ tác vụ AI theo mạch:
  `Nhận diện vai trò (M01) → Cam kết khi upload file (M02) → Kiểm soát quyền dùng file với AI (M03) → Kiểm soát câu lệnh & Agent (M04, M05) → Gắn nhãn nguồn gốc đầu ra (M06) → Truy vết lịch sử giải trình 2 chiều (M07) → Thông điệp sư phạm & Kiểm thử 12 ca nghiệm thu (M08)`.
- **Ngoài phạm vi MVP 1 (Mục 4.6):** Không quét nội dung file tự động để phán xét bản quyền lúc upload; không làm DLP sâu; không làm workflow duyệt nhiều cấp; không tự động chấm điểm/xếp loại/kỷ luật học sinh.

---

## 2. Đối chiếu Hiện trạng Code (`file:line`) với 8 Gói việc MVP (`M01` → `M08`)

Qua khảo sát mã nguồn hiện tại, **hệ thống đã có sẵn khoảng 60% nền tảng Database và Authorization**. Dưới đây là trạng thái từng gói việc:

### 2.1. Gói `M01` — Danh tính, Trường/Workspace & 3 Vai trò (Học sinh – Giáo viên – Quản trị AI trường)
- **Hiện trạng đã có:**
  - `backend/services/api/src/bookforge_api/models/user.py:26-29`: Hệ thống có `ROLE_ADMIN = 'admin'`, `ROLE_USER = 'user'` gắn theo từng `Membership` của `Organization` (Trường/Workspace).
  - `backend/services/api/src/bookforge_api/models/rbac.py:13-91`: Đã có hệ thống Dynamic RBAC (`Role`, `Permission`, `RolePermission`, `RoleAssignment`) và catalog quyền tại `services/user_permission_catalog.py:12-100` (bao gồm quyền `'use_ai': 'Sử dụng AI'`, `'approve': 'Phê duyệt'`).
- **Khoảng trống cần bổ sung cho MVP:**
  - Hiện tại chỉ mới có 2 role hệ thống (`admin` và `user` — mặc định đóng vai trò Giáo viên), chưa định nghĩa rõ vai trò/nhãn `student` (Học sinh) hoặc cờ phân biệt `school_ai_admin` / `teacher` / `student` trong ngữ cảnh gọi AI để giới hạn hành vi (VD: Học sinh không được nhờ làm bài kiểm tra hộ, không dùng tài liệu nội bộ của giáo viên).

### 2.2. Gói `M02` — Cam kết của người Upload & Hồ sơ File
- **Hiện trạng đã có:**
  - `backend/services/api/src/bookforge_api/models/document.py:108-163`: Bảng `documents` đã lưu `owner_user_id`, `organization_id`, `created_at`, `original_filename`, `content_hash`, và cột `metadata_json` (kiểu `JSON`).
  - `backend/services/api/src/bookforge_api/services/documents.py:150-237`: Hàm `create_document_from_upload()` khởi tạo `Document` và ghi `metadata_json`.
  - `backend/services/api/src/bookforge_api/models/document.py:528-547`: Bảng `event_log` (`EventLog`) ghi nhận sự kiện theo `actor_user_id`, `document_id`, `ip_address`, `metadata_json`.
  - `frontend/src/api/document-api.ts:228-235` & `upload-document-request.ts:38`: API upload file qua `POST /api/documents/upload`.
- **Khoảng trống cần bổ sung cho MVP:**
  - Lúc upload chưa bắt buộc truyền cờ xác nhận cam kết (`upload_consent_accepted: bool`) và loại khai báo dữ liệu (`ai_usage_declaration`).
  - Cần chặn ở cả FE (disable nút Upload khi chưa tick) và BE (`POST /api/documents/upload` trả lỗi 400 nếu thiếu xác nhận), đồng thời ghi hồ sơ cam kết (`consent_accepted_at`, `consent_user_id`, `consent_policy_version`, `ai_allowed_by_uploader`) vào `Document.metadata_json` + `EventLog`.

### 2.3. Gói `M03` — Kiểm soát Quyền dùng File làm nguồn cho AI
- **Hiện trạng đã có:**
  - `backend/services/api/src/bookforge_api/models/document.py:134-140`: Đã có cột `approval_status` (`pending` / `approved` / `rejected`).
  - `backend/services/api/src/bookforge_api/services/access.py:87-105`: Đã có hàm `ai_usable(document)` và `assert_ai_usable(document)` kiểm tra quyền đưa tài liệu vào AI.
  - `backend/services/api/src/bookforge_api/authorization/policies/documents.py:55-91`: Đã kiểm tra chặt quyền truy cập tài liệu (`owner`, `DocumentShare`, `GroupGrant`, `public`).
- **Khoảng trống cần bổ sung cho MVP:**
  - Cho phép người upload (hoặc Admin) đánh dấu file thuộc diện **"Không được đưa vào AI"** (ví dụ: đề thi chưa công bố, hồ sơ cá nhân, tài liệu hạn chế — lưu trong `metadata_json['ai_allowed_by_uploader'] = False` hoặc `ai_policy_status`).
  - Cập nhật `ai_usable()` và `assert_ai_usable()` tại `services/access.py:87-105` cùng các điểm nhận file đính kèm (`purpose='chat'`, tạo câu hỏi, tạo slide, Canvas) để **chặn tuyệt đối** việc đưa file đã khai báo hạn chế vào bất kỳ tác vụ AI nào.

### 2.4. Gói `M04` & `M05` — Kiểm soát Ngữ cảnh Command/Prompt (3 trạng thái) & Ràng buộc xuyên suốt mọi Agent
- **Hiện trạng đã có:**
  - `backend/services/api/src/bookforge_api/chat/governance.py:18-55`: Đã có `GOVERNANCE_INSTRUCTION` (`v2`) và hàm `detect_governance_topics(query)`.
- **Khoảng trống cần bổ sung cho MVP:**
  - `GOVERNANCE_INSTRUCTION` hiện tại mới tập trung vào chủ quyền, chống bịa nguồn, ẩn ID nội bộ; **chưa có các quy tắc đặc thù của THPT Long Trường (QĐ 705)**:
    1. Không làm thay toàn bộ bài kiểm tra/bài thi cá nhân của học sinh (chuyển sang gợi mở/hướng dẫn).
    2. Không tự quyết định kết quả đánh giá chính thức, xếp loại học lực/hạnh kiểm hoặc kỷ luật học sinh thay giáo viên/nhà trường.
    3. Phản hồi theo 3 trạng thái: **Phù hợp** (hỗ trợ) / **Cần làm rõ hoặc điều chỉnh** (hướng dẫn thu hẹp phạm vi) / **Không thể hỗ trợ** (từ chối lịch sự, trung tính, viện dẫn đúng mục quy tắc QĐ 705).
  - Cần rà soát đảm bảo **mọi điểm gọi LLM** (Chat chính, Canvas Editor Agent, Question Bank AI generation `llm/question_bank_prompts.py`, Slide generation, Flow Artifact AI, Infographic Agent) đều đi qua lớp kiểm tra & gắn quy tắc chung này, và truyền vai trò người gọi (`user_role`) vào ngữ cảnh.

### 2.5. Gói `M06` — Nhãn Nguồn gốc Tạo sinh (4 mức) trên mọi Đầu ra & Từng Câu hỏi
- **Hiện trạng đã có:**
  - `ChatMessage` (`models/document.py:318-320`) và `CanvasChatMessage` (`models/document.py:366-368`) đã lưu `citations_json`, `retrieved_nodes_json`, `metadata_json`.
  - `QuestionCard` (`models/question_bank.py:198-206`) đã có `status` (`new` = chờ duyệt, `approved` = đã duyệt), `source_document_id`, và `metadata_json`.
- **Khoảng trống cần bổ sung cho MVP:**
  - Chuẩn hóa trường `ai_origin_label` trong `metadata_json` của `ChatMessage`, `CanvasChatMessage`, `QuestionCard`, `Document` (Canvas/Slide/Flow) theo đúng **4 nhãn bắt buộc của Mục 4.3.C**:
    1. `ai_no_reference`: *AI — Không dùng tài liệu tham chiếu* (đảm bảo không gắn trích dẫn giả).
    2. `ai_with_reference`: *AI — Có tài liệu tham chiếu* (kèm danh sách `document_id` + tên file thật).
    3. `ai_mixed_source`: *AI — Nguồn hỗn hợp* (kết hợp tài liệu tham chiếu và suy luận mô hình).
    4. `ai_edited`: *AI — Đã tiếp tục chỉnh sửa* (áp dụng khi nội dung AI tạo ra được sửa tiếp trên Canvas hoặc sửa câu hỏi).
  - Hiển thị rõ nhãn này trên UI (Chat bubble, Canvas header/history, từng thẻ câu hỏi trong Ngân hàng đề kèm nhãn *"Chờ chuyên môn duyệt"* khi `status != 'approved'`, và giữ nhãn khi xuất DOCX/PPTX).

### 2.6. Gói `M07` — Bằng chứng Lịch sử & Truy vết Giải trình 2 chiều
- **Hiện trạng đã có:**
  - Bảng `ai_actions` (`models/document.py:501-526`) đã ghi `user_id`, `organization_id`, `action_type`, `document_ids_json`, `status`, `metadata_json`, `created_at`!
  - Bảng `event_log` (`models/document.py:528-547`) và `retrieval_traces` (`models/document.py:487-499`) đã có sẵn.
- **Khoảng trống cần bổ sung cho MVP:**
  - Ghi bổ sung vào `AIAction.metadata_json`: vai trò người gọi tại thời điểm thực hiện (`actor_role`), trạng thái quyết định chính sách (`policy_decision`: `allowed` / `guided` / `refused`), phiên bản quy tắc (`policy_version`), và ID sản phẩm đầu ra (`output_type`, `output_id` như `message_id`, `question_card_ids`, `document_id`).
  - Cung cấp API & Giao diện tra cứu giải trình (dành cho chủ sở hữu / Quản trị AI trường theo phân quyền):
    - **Chiều 1 (Theo File):** Xem 1 file do ai upload, cam kết lúc nào, và danh sách các tác vụ AI (`ai_actions`) + sản phẩm đã dùng file đó.
    - **Chiều 2 (Theo Sản phẩm AI / Câu hỏi / Tài liệu):** Xem sản phẩm đó sinh ra từ `ai_action` nào, bởi ai, lúc nào, dùng những file gốc nào.

### 2.7. Gói `M08` — Văn phong Sư phạm Nhân văn & Bộ Test 12 Ca Nghiệm thu (Mục 4.5)
- Chuẩn hóa bộ thông điệp cảnh báo/hướng dẫn/từ chối (không quy chụp, không dùng chữ *"BookForge đã xác minh bản quyền"* hay *"100% tuân thủ pháp luật"*).
- Viết bộ test tự động kiểm chứng đủ **12 ca nghiệm thu bắt buộc** tại Mục 4.5 của tài liệu phạm vi.

---

## 3. Lộ trình Triển khai MVP 1 (Chia thành 3 Đợt gọn theo đúng Mục 6.1)

Để kiểm soát chất lượng và có sản phẩm chạy được ngay ở từng chặng, toàn bộ MVP (`M01` → `M08`) nên được chia thành **3 Plan nối tiếp nhau**:

```text
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ ĐỢT 1 (Làm ngay trước Thứ 7): CAM KẾT UPLOAD, QUYỀN FILE AI & QUY TẮC QĐ 705        │
│   Bao phủ: M02 + M03 + M04 + M08 (phần thông điệp)                                  │
│   - Checkbox cam kết & khai báo "Cho phép dùng với AI / Không đưa vào AI" lúc upload│
│   - Lưu hồ sơ cam kết vào Document.metadata_json + EventLog                         │
│   - Chặn cứng file "Không đưa vào AI" tại ai_usable() trên mọi điểm gọi AI          │
│   - Cập nhật GOVERNANCE_INSTRUCTION theo QĐ 705 Long Trường + UI xem Quy tắc AI     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ĐỢT 2: NHÃN NGUỒN GỐC AI (4 MỨC) & PHÂN BIỆT VAI TRÒ TRÊN MỌI AGENT                │
│   Bao phủ: M06 + M01 + M05                                                          │
│   - Chuẩn hóa 4 nhãn nguồn gốc AI trên Chat, Canvas, Ngân hàng câu hỏi & File xuất  │
│   - Nhãn "Tham khảo / Chờ duyệt chuyên môn" cho câu hỏi & đề thi AI tạo             │
│   - Áp dụng ngữ cảnh 3 vai trò (Học sinh / Giáo viên / Quản trị trường) vào các Agent│
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ĐỢT 3: TRUY VẾT GIẢI TRÌNH 2 CHIỀU & BỘ TEST 12 CA NGHIỆM THU                       │
│   Bao phủ: M07 + M08 (kiểm thử toàn diện 12 ca mục 4.5)                             │
│   - Liên kết AIAction ↔ File nguồn ↔ Sản phẩm đầu ra (QuestionCard, Document, Chat) │
│   - API & Drawer/Tab "Lịch sử & Giải trình AI" trên từng File và Sản phẩm           │
│   - Bộ test tự động phủ trọn 12 ca nghiệm thu mục 4.5                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Câu hỏi cần bạn chốt để lập `02-plan.md`

1. Bạn có đồng ý chia MVP thành **3 đợt cuốn chiếu** như Mục 3, và bắt đầu lập **`02-plan.md` cho Đợt 1 (`M02 + M03 + M04`)** ngay bây giờ để kịp hoàn thành trước Thứ 7 tuần này không?
2. Về vai trò **Học sinh (`M01`)**: Hiện tại trên hệ thống đang có tài khoản Học sinh đăng nhập trực tiếp, hay giai đoạn đầu ở THPT Long Trường mới chỉ có **Giáo viên & Quản trị viên trường** đăng nhập?

