# Báo cáo tiến độ & Handoff làm tiếp trên máy khác: AI Quick Edit (`canvas-quick-edit`)

**Ngày cập nhật:** 2026-11-08 · **Cách làm:** Cách 3: Việc thường · **Phía:** BE
**Trạng thái hồ sơ:** `IN_PROGRESS` (Đã code & pass test **Task 1**, đang chờ kiểm tay **Task 1** để sang **Task 2**)
**Mốc code gốc trên `dev`:**
- `backend`: `48a28e31` (nhánh đang làm: `feat/canvas-quick-edit`, đã commit & push Task 1 tại commit `74f74e2f` lên `origin/feat/canvas-quick-edit`)
- `frontend`: `fbd52874` (kéo từ `origin/dev` mới nhất, giữ nguyên 100% không sửa)

---

## I. Tóm tắt hiện trạng UI & Quyết định đã chốt

### 1. Kiểm tra UI hiện có trên `frontend` (`fbd52874`)
| Hạng mục | Đã có UI chưa? | Vị trí trong `frontend/` (`file:dòng`) | Cách kết hợp |
|---|---|---|---|
| **Menu chuột phải 5 công cụ AI** | **ĐÃ CÓ HOÀN CHỈNH** | `src/components/TiptapEditor/quick-edit/QuickEditContextMenu.tsx:338-429` | Giữ nguyên 100% thiết kế Figma (gồm `Sao chép`, `Cắt`, `Dán` và `Công cụ AI >` mở ra 5 công cụ). |
| **Bảng Xem trước & Áp dụng (Review Panel)** | **ĐÃ CÓ HOÀN CHỈNH** | `src/components/TiptapEditor/quick-edit/QuickEditPanel.tsx:314-689` | Đã có sẵn dòng hiển thị thuật ngữ bảo vệ `Đã giữ nguyên: ...` (`QuickEditPanel.tsx:600-602`) và khung cảnh báo vàng/đỏ (`QuickEditPanel.tsx:608-623`). Khi nối Backend vào kho Từ điển SGK, dữ liệu `preserved_terms` và `warnings` tự động hiển thị lên đúng 2 vùng UI này. |
| **Chân bảng Xem trước (3 nút chuẩn Figma)** | **ĐÃ KHÓA THEO FIGMA** | `src/components/TiptapEditor/quick-edit/QuickEditOverlay.test.tsx:209-226` | Commit `73fa2c49` đã cố định chân bảng 3 nút (`Thử lại`, `Bỏ qua`, `Thay thế` / `Chèn sau`) theo Figma. |

### 2. Quyết định đã chốt
- **Chỉ tập trung làm ở phía `backend/`**, phần giao diện (`frontend/`) kéo từ working tree `origin/dev` mới nhất về và **giữ nguyên không sửa**.

---

## II. Kết quả đã thực hiện xong ở Task 1

### 1. Các file đã sửa trong `backend/` (Lưu kèm bản vá tại `task1-backend.patch`)
1. `backend/services/api/src/bookforge_api/services/quick_edit_rails.py:165-455, 668-795`:
   - Xây dựng `SchoolGlossaryPedagogicalDictionary` kết nối trực tiếp với dữ liệu từ điển đã cache của `school_glossary._load_glossary_seed_rows()` (167 chương, 6.831 thuật ngữ gồm 10 môn THPT + bộ từ điển `chung`).
   - Tự động khóa bảo vệ thuật ngữ chuẩn xuất hiện trong đoạn văn (`protected_terms`) và trả về trong `preserved_terms` để UI hiển thị ở dòng **`Đã giữ nguyên: ...`**.
   - Tự động phát hiện từ đồng nghĩa/viết tắt (`aliases`) trong đoạn văn để bơm gợi ý chuẩn hóa (`normalization_hints`, ví dụ `“KHBD” -> “Kế hoạch bài dạy”`, `“YCCĐ” -> “Yêu cầu cần đạt”`) vào `_build_custom_query()`.
   - Giữ nguyên `DefaultPedagogicalDictionary` làm stub rỗng để tương thích ngược 100% với các unit test cũ.
2. `backend/services/api/src/bookforge_api/api/assistant_tools.py:671-750`:
   - Bổ sung `_enrich_quick_edit_payload(db, payload, document_ids)` tự động đọc `title`, `document_type`, `metadata_json` từ bản ghi `Document` trong DB (khi FE gửi `document_ids`) và suy luận `subject`, `grade`, `doc_type` cho `doc_metadata`.
3. `backend/services/api/tests/test_quick_edit_rails.py:121-145` & `backend/services/api/tests/test_assistant_quick_edit.py:381-423`:
   - Bổ sung unit test & integration test cho `SchoolGlossaryPedagogicalDictionary`, gợi ý chuẩn hóa từ đồng nghĩa, và làm giàu metadata từ bản ghi `Document` trong DB.

### 2. Kết quả chạy kiểm tra tự động & Gọi thật API OpenAI
- **Pytest Task 1:**
  ```bash
  cd backend/services/api && uv run pytest tests/test_quick_edit_rails.py tests/test_assistant_quick_edit.py -k "dictionary or glossary or metadata" -n 0 -q
  # Kết quả: 7 passed, 77 deselected, 8 warnings in 7.52s
  ```
- **Gọi thật `POST /api/assistant-tools/quick-edit` (`tool="refine"`):**
  - Đoạn 1 (Sinh học 10): trả về `status="ok"`, `preserved_terms=["quang hợp", "lục lạp", "tế bào", "năng lượng"]`.
  - Đoạn 2 (Từ đồng nghĩa + Sư phạm): tự động chuẩn hóa `KHBD` → `Kế hoạch bài dạy (KHBD)`, `PHT` → `Phiếu học tập (PHT)`, và trả về `preserved_terms=["KHBD", "PHT", "yêu cầu cần đạt", "năng lực đặc thù"]`.

---

## III. Hướng dẫn kiểm tay Task 1 (Checklist 4 mục)

1. **Dữ liệu & Mở màn hình:**
   - Đăng nhập tài khoản `owner@example.com` (mật khẩu `Supersafe123!`).
   - Mở tài liệu mẫu có tiêu đề **`Giáo án Sinh học 10 - Bài 12: Quang hợp ở thực vật`** trong mục **Tài liệu** (nếu sang máy mới chưa có bản ghi này trong SQLite local, chạy lệnh tạo nhanh ở **Mục IV.2** bên dưới).
2. **Thao tác:**
   - **Thử nghiệm A (Khóa bảo vệ thuật ngữ SGK):** Quét chọn đoạn văn dưới mục `2. Nội dung trọng tâm` (*"Quá trình quang hợp diễn ra ở lục lạp trong tế bào thực vât, giúp chuyển hóa năng lượng ánh sáng thành năng lượng hóa học tích lũy trong các hợp chất hữu cơ."*) → bấm chuột phải → di chuột vào **`Công cụ AI`** → bấm **`Chỉnh diễn đạt`**.
   - **Thử nghiệm B (Chuẩn hóa từ đồng nghĩa & thuật ngữ Sư phạm):** Quét chọn đoạn văn dưới mục `1. Mục tiêu bài học` (*"Giáo viên xây dựng KHBD và PHT nhằm làm rõ yêu cầu cần đạt và năng lực đặc thù cho học sinh khi tìm hiểu về quá trình trao đổi chất."*) → bấm chuột phải → **`Công cụ AI`** → bấm **`Chỉnh diễn đạt`**.
3. **✅ Đúng khi thấy:**
   - Ở **Thử nghiệm A**: Bảng xem trước hiện **`Đề xuất của AI`** giữ nguyên đúng các thuật ngữ chuyên môn, và dòng thông tin bên dưới hiện rõ: **`Đã giữ nguyên: quang hợp, lục lạp, tế bào, năng lượng...`**.
   - Ở **Thử nghiệm B**: **`Đề xuất của AI`** ưu tiên chuẩn hóa **`KHBD`** thành **`Kế hoạch bài dạy`** và **`PHT`** thành **`Phiếu học tập`**, đồng thời dòng thông tin bên dưới hiện **`Đã giữ nguyên: ... yêu cầu cần đạt, năng lực đặc thù`**.
4. **❌ Sai nếu thấy:**
   - Dòng **`Đã giữ nguyên:`** không hiện ra các thuật ngữ SGK/sư phạm (*quang hợp, lục lạp, yêu cầu cần đạt, năng lực đặc thù*), hoặc báo lỗi khi gọi công cụ.

---

## IV. Cách khôi phục và làm tiếp trên máy khác vào ngày mai

### 1. Khôi phục nhánh và code Task 1 ở `backend/` trên máy mới
Khi mở máy mới, kéo `tech_docs` về rồi chạy lệnh sau ở thư mục gốc `bookforge`:
```bash
cd backend
git fetch origin
git checkout dev && git pull --ff-only origin dev
git checkout -b feat/canvas-quick-edit
git apply ../tech_docs/tasks/canvas-quick-edit/task1-backend.patch
```

### 2. (Tùy chọn) Tạo tài liệu mẫu trong DB local trên máy mới để bấm kiểm tay
```bash
cd backend/services/api && uv run python -c "
from bookforge_api.core.db import session_scope
from bookforge_api.models.user import User, DEFAULT_ORGANIZATION_ID
from bookforge_api.models.document import Document
from bookforge_api.services.inapp_document import build_inapp_document, INDEX_ENQUEUE

sample_md = '''# Giáo án Sinh học 10 - Bài 12: Quang hợp ở thực vật

## 1. Mục tiêu bài học
Giáo viên xây dựng KHBD và PHT nhằm làm rõ yêu cầu cần đạt và năng lực đặc thù cho học sinh khi tìm hiểu về quá trình trao đổi chất.

## 2. Nội dung trọng tâm
Quá trình quang hợp diễn ra ở lục lạp trong tế bào thực vât, giúp chuyển hóa năng lượng ánh sáng thành năng lượng hóa học tích lũy trong các hợp chất hữu cơ.
'''

with session_scope() as db:
    user = db.query(User).filter(User.email == 'owner@example.com').first()
    doc = build_inapp_document(
        db,
        organization_id=user.organization_id or DEFAULT_ORGANIZATION_ID,
        owner_user_id=user.id,
        title='Giáo án Sinh học 10 - Bài 12: Quang hợp ở thực vật',
        content=sample_md,
        content_format='markdown',
        lane='general',
        editor_capability='editable',
        index_strategy=INDEX_ENQUEUE,
        metadata={'subject': 'Sinh học', 'grade': 'Lớp 10'},
    )
    print('Created sample document ID:', doc.id)
"
```

### 3. Câu lệnh dán vào khung chat cho AI trên máy mới
Khi mở phiên chat mới vào ngày mai, bạn chỉ cần dán câu lệnh Cứu hộ trong `tech_docs/prompts.md`:
```text
Đọc tech_docs/README.md và các file trong tech_docs/tasks/canvas-quick-edit/, kiểm tra git status và git log gần đây ở backend/ và frontend/, rồi tóm tắt trong 5 dòng: đang ở giai đoạn/Task nào, đã xong gì, việc tiếp theo cần làm ngay là gì.
```
Sau khi kiểm tay **Task 1** và nhắn **OK**, AI sẽ đánh dấu `[x]` cho **Task 1** trong `plan.md` và thực hiện nốt **Task 2** (*Đưa công cụ Sửa chính tả `spellcheck` vào hàng rào bảo vệ thuật ngữ & tách cảnh báo `terms_changed`*).

