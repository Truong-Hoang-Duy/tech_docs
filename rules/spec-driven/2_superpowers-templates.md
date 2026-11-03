# Khuôn mẫu Chuẩn: Báo cáo Audit (`tech_docs/audits/`) & Kế hoạch Superpowers (`backend/docs/superpowers/plans/`)

---

## 1. Khuôn mẫu Báo cáo Quét & Điều phối: `tech_docs/audits/<slug>-audit.md`

Đặt tại: `tech_docs/audits/<slug>-audit.md` (Ví dụ: `tech_docs/audits/ai-governance-wave-a-audit.md`)

````markdown
# Báo cáo Quét Spec & Điều phối Thực thi: <Tên Gói Spec>

**Ngày khởi tạo:** YYYY-MM-DD · **Mã gói:** `<pkg-XX>` · **Phía tác động:** <BE | FE | Cả hai>
**File Spec gốc:** `backend/docs/product/ai-governance-mvp/specs/<tên-file-pkg-XX.md>`
**File Superpowers Plan:** `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`
**Người quét & lập Plan:** <Gemini | Claude> · **Người duyệt Plan:** <Claude | Gemini>
**Trạng thái:** <AUDITED | PLAN_DRAFTED | APPROVED | IN_PROGRESS | VERIFIED>

---

## 1. Tóm tắt Phạm vi & Ràng buộc Bất biến (`T1`–`T10`)
- **Mục tiêu cốt lõi của gói:** <2–3 gạch đầu dòng tóm tắt đầu ra bắt buộc của gói Spec này>
- **Các quyết định kỹ thuật (`T1`–`T10` / `D1`–`D6`) áp dụng trực tiếp:**
  - `<Mã T/D>`: <Nội dung ràng buộc không được vi phạm>

---

## 2. Phát hiện Độ lệch giữa Spec và Code thật (`Spec-to-Code Drift`)

> *(Bảng này ghi lại mọi điểm khác biệt giữa giả định trong file Spec và trạng thái thật của nhánh `dev` hiện tại để hiệu chỉnh khi viết Superpowers Plan).*

| # | Hạng mục kiểm tra | Trong Spec đang ghi | Thực tế trên Codebase (`file:line`) | Cách hiệu chỉnh vào Superpowers Plan |
|---|---|---|---|---|
| 1 | **Alembic Migration** | VD: `0114_ai_governance_wave_a.py` | `0114` đã dùng bởi `0114_notifications.py` (`head = 0114`) | Đổi thành `0115_ai_governance_wave_a.py`, `down_revision = "0114_notifications"` |
| 2 | **ErrorCode & Catalog** | Thêm mã lỗi `...` vào `codes.py` | `test_errors_catalog.py` bắt buộc đồng bộ 4 file | Đưa vào Task 1 việc cập nhật đủ `codes.py`, `catalog.py`, `render_errors_doc.py`, `docs/ERRORS.md` |
| 3 | **Chữ ký hàm / Schema** | ... | ... | ... |
| 4 | **Env / Docker Compose** | ... | ... | ... |
| 5 | **Giới hạn 300 dòng FE** | Sửa file `...` | File hiện tại đang có `N` dòng | Tách component con sang `partial/...` để giữ file ≤ 300 dòng |

---

## 3. Kiểm kê Điểm chạm Code thật (`backend/` & `frontend/`)

### 3.1 Backend (`backend/`)
| File (tính từ gốc `backend/`) | Thao tác (`Tạo` / `Sửa`) | Hiện trạng (`file:line`) & Nội dung cần can thiệp |
|---|---|---|
| `services/api/alembic/versions/...` | Tạo | ... |
| `services/api/src/bookforge_api/...` | Sửa | ... |

### 3.2 Frontend (`frontend/`)
| File (tính từ gốc `frontend/`) | Thao tác (`Tạo` / `Sửa`) | Số dòng hiện tại | Nội dung cần can thiệp & Phương án giữ ≤ 300 dòng |
|---|---|---|---|
| `src/...` | Sửa | `...` dòng | ... |

---

## 4. Ma trận Ánh xạ Tiêu chí Nghiệm thu (`AC-XX-*` ➔ `Task N`)

| Mã AC trong Spec | Nội dung yêu cầu nghiệm thu | Được xử lý tại Task nào trong Superpowers Plan? | File Test kiểm chứng |
|---|---|---|---|
| `AC-A-01` | ... | `Task 1`, `Task 3` | `services/api/tests/...` |
| `AC-A-02` | ... | `Task 2`, `Task 5` | `services/api/tests/...` |

---

## 5. Nhật ký Duyệt Superpowers Plan (`Cross-Review` bởi <Claude | Gemini>)
- **Ngày duyệt:** YYYY-MM-DD
- **Các file đã đối chiếu:** <Spec gốc + File Audit + Superpowers Plan + Code thật>
- **Phát hiện & Phản biện:**
  - 🔴 **[Blocker]** <Không có / Hoặc nêu rõ điểm sai và cách đã sửa vào Plan>
  - 🟡 **[Should-fix]** <Không có / Hoặc nêu điểm cải thiện>
  - 🟢 **[Nit]** <Không có / Hoặc góp ý nhỏ>
- **Kiểm tra cách ly `tech_docs`:** Đã xác nhận file `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md` không chứa chuỗi `tech_docs`.
- **Kết luận Duyệt Plan:** `APPROVED` | `CHANGES REQUESTED`

---

## 6. Nhật ký Thực thi (`Execution Log`)
- **Nhánh Git (`backend` / `frontend`):** `feat/<slug>`
- **Tiến độ từng Cụm Task:**
  - `Task 1..k`: <Người chạy> — <Tóm tắt kết quả chạy test & lint>
  - `Task k+1..n`: <Người chạy> — <Tóm tắt kết quả chạy test & lint>
- **Quyết định kỹ thuật phát sinh khi code (nếu có):**
  - <Ghi rõ nếu có điều chỉnh nhỏ so với Plan ban đầu>

---

## 7. Kết quả Nghiệm thu Code (`Cross-Verify` bởi <Gemini | Claude>)
- **Ngày nghiệm thu:** YYYY-MM-DD
- **Đối chiếu `git status` / `git diff`:** <Khớp 100% các Task và tiêu chí `AC-XX-*` hay còn thiếu?>
- **Kết quả chạy lại cổng kiểm tra độc lập:**
  - Backend (`ruff`, `pytest`, `test_errors_catalog`): <PASS / FAIL>
  - Frontend (`tsc`, `vitest`, `build`, giới hạn ≤ 300 dòng/file): <PASS / FAIL>
  - Kiểm tra không rò rỉ chuỗi `tech_docs` vào `backend/` và `frontend/`: <PASS>
- **Kết luận cuối cùng:** `VERIFIED (Sẵn sàng Commit)` | `NEEDS FIX`
````

---

## 2. Khuôn mẫu Kế hoạch Thi công Chuẩn Superpowers: `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`

Đặt tại: `backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`
> **⚠️ RÀNG BUỘC CỨNG:** File này nằm trong repo `backend`. **Tuyệt đối không** viết chữ `tech_docs` hoặc nhắc tên file `*-audit.md` ở bất kỳ đâu trong file này.

````markdown
# <Tên Gói / Tính năng> Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** <Mô tả ngắn gọn 1–2 câu về mục tiêu cần đạt của gói triển khai này>

**Architecture:** <Tóm tắt 3–5 dòng về kiến trúc giải pháp, các tầng thay đổi từ DB -> Service/Policy -> API -> Frontend UI, và các quyết định kỹ thuật T1..T10 được áp dụng>

**Tech Stack:** FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, pytest (Backend); React 18, TypeScript, TanStack Query, TailwindCSS, Vitest (Frontend).

**Spec:** `docs/product/ai-governance-mvp/specs/<tên-file-pkg-XX.md>` & `docs/product/ai-governance-mvp/TECHNICAL_ALIGNMENT_DECISIONS.md`

---

## Global Constraints

1. **SQLite & PostgreSQL Dual Compatibility:** Các bài test tích hợp chạy trên SQLite (`services/api/tests/conftest.py`), trong khi môi trường chạy thật dùng PostgreSQL. Migration Alembic và `db/models.py` phải tương thích cả hai; tránh dùng `batch_alter_table` gây khóa bảng hoặc cú pháp chỉ chạy được trên một hệ quản trị.
2. **Error Catalog Sync:** Mọi mã lỗi mới thêm vào `ErrorCode` (`errors/codes.py`) bắt buộc phải khai báo đầy đủ trong `errors/catalog.py`, `scripts/render_errors_doc.py`, và chạy cập nhật `docs/ERRORS.md` để vượt qua `tests/test_errors_catalog.py`. Luôn ném `AppError(ErrorCode.<code_name>, ...)` thay vì `HTTPException` thô.
3. **No DB Locks Across LLM / External I/O:** Không giữ transaction lock trên DB trong lúc chờ kết quả từ LLM, OCR, hoặc dịch vụ ngoài.
4. **Frontend File Size & Naming Convention (`CONVENTION.md`):** Mỗi file trong `frontend/src/` tối đa **300 dòng**, mỗi hàm tối đa **100 dòng**. Tách các phần phụ vào thư mục `partial/` cùng cấp nếu file vượt ngưỡng.

## Review Focus

1. <Điểm trọng tâm cần kiểm soát số 1 — VD: Đảm bảo `ai_allowed=false` chặn tuyệt đối trước `enqueue_ingest` ở mọi ngả>
2. <Điểm trọng tâm cần kiểm soát số 2 — VD: Đảm bảo Admin không đọc được nội dung tài liệu/prompt riêng tư của giáo viên>
3. <Điểm trọng tâm cần kiểm soát số 3 — VD: Đảm bảo đủ 100% các tiêu chí nghiệm thu `AC-XX-*` trong Spec>

---

## File Structure

### Backend (`bookforge`) — New Files
- `services/api/alembic/versions/<revision>_<slug>.py` — <Trách nhiệm 1 dòng>
- `services/api/src/bookforge_api/<path>.py` — <Trách nhiệm 1 dòng>
- `services/api/tests/<test_file>.py` — <Trách nhiệm 1 dòng>

### Backend (`bookforge`) — Modified Files
- `services/api/src/bookforge_api/db/models.py` — <Trách nhiệm 1 dòng>
- `services/api/src/bookforge_api/errors/codes.py` — <Trách nhiệm 1 dòng>
- `services/api/src/bookforge_api/errors/catalog.py` — <Trách nhiệm 1 dòng>

### Frontend (`bookforge-fe`) — New / Modified Files *(nếu gói có phần FE)*
- `src/<path>.tsx` — <Trách nhiệm 1 dòng>

---

### Task 1: <Tên Task 1 — VD: Database Migration, Models & Error Codes>

**Files:**
- Create: `services/api/alembic/versions/<revision>_<slug>.py`
- Modify: `services/api/src/bookforge_api/db/models.py`
- Modify: `services/api/src/bookforge_api/errors/codes.py`
- Modify: `services/api/src/bookforge_api/errors/catalog.py`
- Test: `services/api/tests/<test_file>.py`

**Interfaces:**
- Consumes: `<Các class/hàm/bảng hiện có>`
- Produces: `<Các cột/bảng/ErrorCode/hàm mới được tạo ra ở Task này>`

- [ ] **Step 1: Write failing test(s) in `services/api/tests/<test_file>.py`**

```python
# Đoạn code test cụ thể kiểm tra model / migration / mã lỗi mới
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run --directory services/api pytest tests/<test_file>.py -v
```
Expected: FAIL (vì chưa có cột / bảng / mã lỗi mới).

- [ ] **Step 3: Implement minimal code in models, migration, and error catalog**

1. Trong `services/api/src/bookforge_api/db/models.py`:
   - <Mô tả chính xác thay đổi và đoạn code>
2. Tạo `services/api/alembic/versions/<revision>_<slug>.py` (`down_revision = "<head_hiện_tại>"`):
   - <Mô tả chính xác `upgrade()` và `downgrade()`>
3. Cập nhật `codes.py`, `catalog.py`, `scripts/render_errors_doc.py` và chạy script cập nhật `docs/ERRORS.md`.

- [ ] **Step 4: Run test & linter to verify it passes**

Run:
```bash
uv run --directory services/api pytest tests/<test_file>.py tests/test_errors_catalog.py -v
uv run --directory services/api ruff check .
```
Expected: PASS.

---

### Task 2: <Tên Task 2 — ...>

*(Lặp lại cấu trúc `Files` -> `Interfaces` -> `Step 1..4` cho đến hết các Task của gói Spec)*
````
