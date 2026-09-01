# Quy ước Docs của dự án BookForge

Tài liệu này **đúc kết** quy ước viết docs đang thực sự tồn tại trong dự án — không phát minh quy ước mới.
Mọi mục đều dẫn chứng file thật; chỗ nào dự án đang không nhất quán thì ghi vào §5 thay vì tự chọn một cách rồi coi là chuẩn.

Phạm vi khảo sát: toàn bộ `.md` trong `backend/` và `frontend/` (≈330 file), trừ `tech_docs/research/` (docs nghiên cứu tạm) và `services/*/rag/prompts/` (file prompt, không phải tài liệu).

Hai văn bản dưới đây là **nguồn quy ước gốc của dự án**, tài liệu này chỉ tổng hợp lại và bổ sung phần chưa được viết ra:

- [`backend/docs/TASK_HANDOFF.md`](../../backend/docs/TASK_HANDOFF.md) — §"The task spec": quy định file giao việc.
- [`backend/docs/REVIEW_STANDARDS.md`](../../backend/docs/REVIEW_STANDARDS.md) — §"Handing findings to the author": quy định ngôn ngữ, link, cấu trúc khối, DoD.

Backend và frontend là **hai repo riêng, hai quy ước riêng** — §1 và §2 ghi tách bạch, không gộp.

---

## 1. Backend (`backend/`, repo `bookforge`)

### 1.1 Bảng phân loại docs

| Loại nội dung | Thư mục đặt | File tham chiếu thật |
|---|---|---|
| Chỉ mục docs | `docs/README.md` | [`docs/README.md`](../../backend/docs/README.md) — mục lục có mô tả một dòng cho mỗi doc |
| Hợp đồng API cho FE | `docs/api/<kebab>.md` | [`api/quota-handoff.md`](../../backend/docs/api/quota-handoff.md), [`api/sse-events.md`](../../backend/docs/api/sse-events.md), [`api/pptx-slide-contract.md`](../../backend/docs/api/pptx-slide-contract.md) |
| Hợp đồng/tham chiếu xuyên suốt | `docs/<UPPER_SNAKE>.md` | [`GEOMETRY_SPEC.md`](../../backend/docs/GEOMETRY_SPEC.md), [`ERRORS.md`](../../backend/docs/ERRORS.md), [`QUESTION_BANK_API_GUIDE.md`](../../backend/docs/QUESTION_BANK_API_GUIDE.md) |
| Quy trình nội bộ (meta-docs) | `docs/<UPPER_SNAKE>.md` | [`TASK_HANDOFF.md`](../../backend/docs/TASK_HANDOFF.md), [`REVIEW_STANDARDS.md`](../../backend/docs/REVIEW_STANDARDS.md), [`REPO_STATUS.md`](../../backend/docs/REPO_STATUS.md) |
| Kiến trúc hệ thống | `docs/architecture/NN-<kebab>.md` (chuỗi đánh số) | [`architecture/01-system-overview.md`](../../backend/docs/architecture/01-system-overview.md) → `07-…` |
| Kiến trúc một mảng lớn | `docs/architecture/bookforge-<chủ-đề>.md` | `bookforge-database-authorization-architecture.md` |
| Thiết kế backend | `docs/backend/<kebab>.md` | [`backend/data-model.md`](../../backend/docs/backend/data-model.md), `backend/document-access-model.md` |
| Sản phẩm / nghiệp vụ | `docs/product/<kebab>.md` | [`product/quota-rules.md`](../../backend/docs/product/quota-rules.md), `product/hitl-tong-quan.md` |
| Vận hành, runbook | `docs/ops/<kebab>.md` | [`ops/vps-deploy-runbook.md`](../../backend/docs/ops/vps-deploy-runbook.md), `ops/staging-environment.md` |
| Vận hành theo sự kiện/ngày | `docs/ops/YYYY-MM-DD-<kebab>.md` | `ops/2026-06-27-ci-actions-minute-optimization.md` |
| Chính sách AI | `docs/governance/<kebab>.md` | `governance/ai-governance-vn.md` |
| Thiết kế đã chốt (spec) | `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md` | [`specs/2026-07-06-geometry-operation-model-design.md`](../../backend/docs/superpowers/specs/2026-07-06-geometry-operation-model-design.md) |
| Kế hoạch triển khai chi tiết | `docs/superpowers/plans/YYYY-MM-DD-<slug>.md` | [`plans/2026-07-04-agent-geometry-jsxgraph.md`](../../backend/docs/superpowers/plans/2026-07-04-agent-geometry-jsxgraph.md) |
| Kế hoạch triển khai phần FE | `docs/superpowers/plans/YYYY-MM-DD-<slug>-fe.md` hoặc `-frontend.md` | [`plans/2026-07-04-geometry-jsxgraph-fe.md`](../../backend/docs/superpowers/plans/2026-07-04-geometry-jsxgraph-fe.md) |
| **File giao việc (task spec)** | `docs/tasks/YYYY-MM-DD-<slug>.md` | [`tasks/2026-06-19-reindex-tier1-debounce.md`](../../backend/docs/tasks/2026-06-19-reindex-tier1-debounce.md) |
| **File giao việc cho FE** | `docs/tasks/YYYY-MM-DD-<slug>-frontend.md` (vẫn nằm trong repo backend) | [`tasks/2026-06-24-phase2-unbounded-chat-scope-frontend.md`](../../backend/docs/tasks/2026-06-24-phase2-unbounded-chat-scope-frontend.md) |
| Bàn giao hợp đồng BE → FE | `handoff/frontend/<UPPER_SNAKE>.md` | [`handoff/frontend/CHAT_INLINE_IMAGES.md`](../../backend/handoff/frontend/CHAT_INLINE_IMAGES.md), `EDITOR_CURSOR_CONTEXT.md` |
| Rà soát chất lượng | `docs/audits/YYYY-MM-DD-<slug>.md` | `audits/2026-06-12-system-quality-audit.md` |
| Ghi chú cạnh code | `services/**/README.md` | [`services/api/src/bookforge_api/services/geometry/README.md`](../../backend/services/api/src/bookforge_api/services/geometry/README.md) — 7 dòng, chỉ ghi cái không đọc ra được từ code |
| Onboarding / setup | root repo, `UPPER_SNAKE.md` | [`CANVAS_AGENT_ONBOARDING.md`](../../backend/CANVAS_AGENT_ONBOARDING.md), `LOCAL_QUICKSTART.md` |

Quy tắc rút ra: **`docs/` root dùng `UPPER_SNAKE`, mọi thư mục con dùng `kebab-case`.**
Thư mục có vòng đời theo thời gian (`tasks/`, `specs/`, `plans/`, `audits/`) tiền tố `YYYY-MM-DD-`; thư mục mô tả trạng thái hiện tại (`backend/`, `product/`, `api/`, `architecture/`) không có ngày.

**Slug ngắn gọn (quy định, áp dụng cho file tạo mới):** phần `<slug>` chỉ nêu đúng chủ đề chính bằng 2–4 từ khoá nối gạch ngang, không nhồi thêm phạm vi/ngữ cảnh phụ vào tên file — những chi tiết đó thuộc nội dung bên trong file (banner, mục Bối cảnh/Phạm vi), không thuộc tên file. Tên file kể cả ngày và hậu tố (`-frontend`/`-fe`/`-design`) phải đọc gọn trong một dòng, không phải bản tóm tắt lại toàn bộ tiêu đề.

### 1.2 Khung heading theo từng loại

**a) File giao việc — `docs/tasks/`** (khuôn mẫu bắt buộc, do `TASK_HANDOFF.md` §"The task spec" quy định)

```text
# Task — <mô tả việc, tiếng Việt>

**Ngày:** YYYY-MM-DD
**Loại:** forward spec (giao việc trước khi code) | follow-up spec (sau review)
**Repo triển khai:** <bookforge | bookforge-fe>
**Thiết kế gốc (đọc trước):** <đường dẫn spec>
**Phụ thuộc:** <task/PR chặn>

## Cách đọc tài liệu này      ← banner bắt buộc, xem §1.3
## Bối cảnh
## Hiện trạng đã kiểm chứng (ngày, nơi kiểm)     ← tuỳ chọn
## Phạm vi / Ngoài phạm vi
## Quyết định đã chốt         ← bắt buộc, TASK_HANDOFF.md step 1
## Việc cần làm               ← một khối cho mỗi hạng mục
## Ai sở hữu test nào         ← tuỳ chọn, theo TASK_HANDOFF.md §3
## DoD — hoàn thành khi       ← bắt buộc, checkbox `- [ ]`
## Tham chiếu nhanh các file
```

Mẫu đối chiếu: [`2026-06-24-phase2-unbounded-chat-scope-frontend.md`](../../backend/docs/tasks/2026-06-24-phase2-unbounded-chat-scope-frontend.md) (đầy đủ nhất), [`2026-06-19-reindex-tier1-debounce.md`](../../backend/docs/tasks/2026-06-19-reindex-tier1-debounce.md) (bản rút gọn, 54 dòng).

Ba ràng buộc nội dung mà `TASK_HANDOFF.md` và `REVIEW_STANDARDS.md` nói rõ:

- **Không có trường người được giao** — "a task spec is not pre-assigned to a person".
- **Mỗi khối việc theo mạch**: *khi nào xảy ra* → *nguyên nhân gốc* (`file:line`) → *bằng chứng* → *hành vi mong muốn* → *hướng đề xuất* (ghi rõ là gợi ý).
- **DoD phải kiểm chứng được**: mỗi checkbox là một khẳng định cụ thể (lệnh + trạng thái mong đợi), và **gộp "test cái gì" vào DoD**, không để mục test rời.

**b) Kế hoạch triển khai — `docs/superpowers/plans/`** (143/143 file theo đúng khung này)

```text
# <Feature> Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development …

**Goal:** …          ← 141/143 file có bộ ba Goal/Architecture/Tech Stack
**Architecture:** …
**Tech Stack:** …

## Global Constraints        ← gạch đầu dòng in đậm, mỗi dòng một ràng buộc cứng
## File Structure            ← bảng Create / Modify + trách nhiệm từng file
## Task N: <tên>             ← Files / Interfaces / `- [ ] **Step N:**`
## Self-Review               ← 91/143 file
```

**c) Thiết kế — `docs/superpowers/specs/`**: H1 dạng `# <Chủ đề> — Design`, sau đó khối metadata gạch đầu dòng (`- **Date:** / - **Status:** / - **Builds on:** / - **Scope:**`), rồi các mục đánh số `## 1. …`.
Chỉ 24/132 file có khối metadata này — xem §5.2.

**d) Hợp đồng cho FE — `docs/api/` và `docs/<UPPER_SNAKE>.md`**: H1 tên hợp đồng, ngay dưới là dòng `**Source of truth:**` trỏ tới file code sinh ra nó, rồi `## Where it surfaces` (bảng endpoint → shape), rồi các mục đánh số.
Xem [`api/pptx-slide-contract.md`](../../backend/docs/api/pptx-slide-contract.md).

**e) Bàn giao FE — `handoff/frontend/`**: H1 dạng `# Hướng Dẫn FE: <Tiêu Đề Viết Hoa Từng Chữ>`, khối endpoint + `credentials: 'include'` đặt ngay đầu, `## Mục Tiêu UX`, rồi `## 1. …` → `## N. …`, kết bằng `## Checklist Triển Khai FE` / `## Acceptance Test Cho FE` / `## Lỗi Và Cách Xử Lý`.
Xem [`CANVAS_CHAT_HISTORY_INSTRUCTIONS.md`](../../backend/handoff/frontend/CANVAS_CHAT_HISTORY_INSTRUCTIONS.md).

### 1.3 Văn phong & định dạng

| Điểm | Quy ước | Bằng chứng |
|---|---|---|
| Ngôn ngữ theo thư mục | `docs/tasks/` **13/13 tiếng Việt**; `handoff/frontend/` **5/5 tiếng Việt**; `docs/architecture/` **0/12** và `docs/backend/` **0/7** tiếng Việt (thuần Anh); `docs/product/` 19/25 Việt; `plans`/`specs` phần lớn Anh | đếm ký tự có dấu trên toàn bộ file |
| Quy tắc chọn ngôn ngữ | "If the author works in Vietnamese, write Vietnamese — professional, concise, direct (no casual filler)" | `REVIEW_STANDARDS.md` §Handing findings |
| Trộn ngôn ngữ | Định danh code, đường dẫn, endpoint, tên env, mã lỗi, lệnh chạy **luôn giữ nguyên tiếng Anh trong backtick**, kể cả giữa câu tiếng Việt | mọi file `docs/tasks/` |
| Xuống dòng | **Một câu một dòng** trong task doc và follow-up doc | `REVIEW_STANDARDS.md`: "One sentence per line (word-wrap handles width)" |
| Link file | **Tương đối so với chính file doc** để bấm được — từ `docs/tasks/` là `../../services/api/src/...`, không phải đường dẫn từ gốc repo | `REVIEW_STANDARDS.md`; xem `tasks/2026-08-03-editor-focus-envelope.md` |
| Trỏ tới dòng code | `file.py:123` trong văn xuôi, `#L93` khi cần link neo | `tasks/2026-06-24-…-frontend.md` |
| Code block | Luôn gắn ngôn ngữ: `http` cho endpoint, `ts` cho type FE, `json`, `python`, `bash`, `text` cho cây thư mục / sơ đồ | `GEOMETRY_SPEC.md`, `api/sse-events.md` |
| Sơ đồ | **ASCII** (32 file dùng `│ ├ └`); mermaid chỉ xuất hiện đúng **1 file** trên toàn repo → mặc định là ASCII | `tasks/2026-08-12-chat-inline-images.md` §2.1 |
| Bảng | GFM; dùng cho ma trận endpoint→shape, so sánh phương án, "ai sở hữu test nào" | khắp nơi |
| Checkbox | `- [ ]` cho DoD và cho từng Step trong plan | `TASK_HANDOFF.md` §2 |
| Emoji | Chỉ dùng có nghĩa: 🔴🟡🟢 = **thứ tự ưu tiên, không phải mức tuỳ chọn**; ✅ = đã xong | `REVIEW_STANDARDS.md` quy định rõ nghĩa màu |
| Banner sau H1 | Khối `> …` nêu trạng thái / cách đọc / cảnh báo phạm vi | `tasks/2026-08-03-editor-focus-envelope.md`, `plans/*` |
| Frontmatter | **Không dùng.** 0/330 file có YAML frontmatter | quét toàn bộ |
| Changelog | **Không có** mục changelog trong file docs; lịch sử nằm ở git và ở việc tạo file mới theo ngày | quét toàn bộ |
| Người viết | `**Tác giả:**` chỉ có ở 5 file; task doc **cấm** trường người được giao | `TASK_HANDOFF.md` |
| Cập nhật chỉ mục | Doc mới đáng chú ý thì thêm một dòng mô tả vào `docs/README.md` | `docs/README.md` |

### 1.4 Độ dài tham chiếu (số dòng)

| Thư mục | n | Trung vị | Khoảng |
|---|---|---|---|
| `docs/api/` | 3 | 79 | 39–333 |
| `docs/backend/` | 7 | 190 | 36–273 |
| `docs/ops/` | 9 | 111 | 38–522 |
| `docs/tasks/` | 13 | **136** | 50–959 |
| `docs/superpowers/specs/` | 132 | 204 | 45–1343 |
| `docs/superpowers/plans/` | 143 | **953** | 82–3121 |
| `handoff/frontend/` | 5 | 181 | 111–1951 |
| `docs/architecture/` | 12 | 325 | 129–769 |

Đọc bảng này: một file giao việc bình thường **~100–200 dòng**; vượt 300 dòng là dấu hiệu nó đang gánh cả phần thiết kế, nên tách spec ra riêng.
Plan trong `superpowers/plans/` dài là do có code mẫu đầy đủ cho từng Step — đó là loại doc để agent thi hành từng bước, khác với task doc.

---

## 2. Frontend (`frontend/`, repo `bookforge-fe`)

### 2.1 Phát hiện quan trọng: repo FE gần như không chứa docs

Toàn bộ `.md` trong repo FE (ngoài `node_modules`) chỉ có 4 file:

| File | Dòng | Nội dung |
|---|---|---|
| [`CONVENTION.md`](../../frontend/CONVENTION.md) | 39 | Quy ước code FE — không phải quy ước docs |
| [`README.md`](../../frontend/README.md) | 57 | Cách chạy dev, proxy backend, deploy |
| [`openapi/question-bank-question-types.md`](../../frontend/openapi/question-bank-question-types.md) | 228 | Bản sao hợp đồng 9 loại câu hỏi, tiếng Việt |
| `.github/pull_request_template.md` | 17 | Template PR |

**Không có thư mục `frontend/docs/`.** Vì vậy:

> **Tài liệu công việc của FE được viết trong repo backend, không viết trong repo FE.**

Bằng chứng trực tiếp:

- [`backend/docs/tasks/2026-06-24-phase2-unbounded-chat-scope-frontend.md`](../../backend/docs/tasks/2026-06-24-phase2-unbounded-chat-scope-frontend.md) ghi ngay đầu file: *"**Repo triển khai:** `bookforge-fe` (KHÔNG phải repo backend này)"*.
- [`backend/docs/superpowers/plans/2026-07-04-geometry-jsxgraph-fe.md`](../../backend/docs/superpowers/plans/2026-07-04-geometry-jsxgraph-fe.md) — kế hoạch FE 1178 dòng, nằm trong repo backend.
- Cùng dạng: `2026-05-31-list-pagination-filtering-frontend.md`, `2026-06-03-document-export-frontend.md`, `2026-07-15-unified-pptx-generation-fe.md`, `2026-07-21-deck-draft-lifecycle-v2-fe.md`, `2026-07-29-editor-caret-context-fe-wiring.md`.
- `backend/handoff/frontend/` — nơi backend bàn giao hợp đồng cho FE.

### 2.2 Quy ước cho docs viết về FE

Vì file nằm trong repo backend nhưng mô tả code FE, các doc trên thống nhất bốn điểm:

1. **Nêu rõ repo triển khai ngay đầu file** — bằng dòng `**Repo triển khai:**` (task doc) hoặc trong `## Global Constraints` (plan).
2. **Mọi đường dẫn file là tương đối với gốc repo `bookforge-fe`** (`src/components/TiptapEditor/...`), và nói thẳng điều đó: *"Mọi đường dẫn file dưới đây là **trong repo `bookforge-fe`**"* (`2026-06-24-…-frontend.md` §Quyết định đã chốt).
3. **Nhắc lại ràng buộc của `frontend/CONVENTION.md`** khi đặc tả file mới: tối đa 300 dòng/file, 100 dòng/function, tách phần dôi ra vào thư mục `partial/`, `kebab-case` cho tên file, `PascalCase` cho component, tiền tố `T` cho type, `API` cho hàm gọi API, `useQuery` cho hook query.
4. **Đặc tả bằng cây thư mục + interface công khai**, không mô tả suông — xem `File Structure` của `2026-07-04-geometry-jsxgraph-fe.md`.

Ngôn ngữ: task doc FE viết **tiếng Việt** (`2026-06-24-…-frontend.md`), plan FE viết **tiếng Anh** (`2026-07-04-geometry-jsxgraph-fe.md`) — dự án không có quy tắc thống nhất, xem §5.3.

---

## 3. Quy ước áp cho cả hai bên

- **Git**: [`tech_docs/rules/2_git-workflow-rules.md`](../rules/2_git-workflow-rules.md) — commit tài liệu dùng `docs(<scope>): …`, không tự commit/push, không thêm attribution AI. Áp cho cả hai repo.
- **Không tự sinh file .md** ghi lại việc đã làm nếu người dùng không yêu cầu (cùng file trên, §1).
- **Không tự tạo file trong `docs/superpowers/specs/` và `docs/audits/`** — hai loại này do người dùng (vai trò reviewer/kiểm duyệt) tự viết, trừ khi được yêu cầu rõ ràng. Khi cần mô tả việc cần làm, viết vào `docs/tasks/` (task spec, §1.2a) thay vì tự soạn spec hoặc audit.
- **Khung báo cáo kỹ thuật**: [`tech_docs/rules/1_technical-spec-template.md`](../rules/1_technical-spec-template.md) — 10 mục tiếng Việt (Tổng quan → Câu hỏi mở), tự khai là "khung tham khảo, không phải form bắt buộc điền đủ 100%". Một số doc dài trong `docs/tasks/` và `docs/product/` theo khung này.
- **Nhánh**: [`backend/CLAUDE.md`](../../backend/CLAUDE.md) — giữ nhánh sau khi merge, ưu tiên `git merge --no-ff`, áp cho cả repo API lẫn `bookforge-fe`.

---

## 4. Sơ đồ chọn nơi đặt file

```text
Nội dung là gì?
│
├─ Giao việc để ai đó code theo  ──────────────► backend/docs/tasks/YYYY-MM-DD-<slug>[-frontend].md
│                                                (tiếng Việt, ~100–200 dòng, có Quyết định đã chốt + DoD)
│
├─ Kế hoạch thi hành từng bước cho agent ──────► backend/docs/superpowers/plans/YYYY-MM-DD-<slug>[-fe].md
│                                                (Goal/Architecture/Tech Stack + Task N + Step checkbox)
│
├─ Chốt thiết kế trước khi code ───────────────► KHÔNG tự tạo — specs/ do người dùng (reviewer) viết (§3);
│                                                nếu cần mô tả việc cần làm thì viết task doc ở docs/tasks/
│
├─ Hợp đồng API để FE tích hợp ────────────────► backend/docs/api/<kebab>.md
│                                                hoặc backend/handoff/frontend/<UPPER_SNAKE>.md
│
├─ Mô tả hệ thống ở trạng thái hiện tại ───────► backend/docs/{architecture,backend}/<kebab>.md  (tiếng Anh)
│
├─ Nghiệp vụ / sản phẩm ───────────────────────► backend/docs/product/<kebab>.md
│
├─ Vận hành, deploy, sự cố ────────────────────► backend/docs/ops/[YYYY-MM-DD-]<kebab>.md
│
├─ Rà soát chất lượng (audit) ──────────────────► KHÔNG tự tạo — audits/ do người dùng (reviewer) viết (§3)
│
└─ Ghi chú chỉ có ý nghĩa cạnh code ───────────► services/**/README.md  (ngắn, ≤ 20 dòng)
```

---

## 5. Ngoại lệ & điểm không nhất quán (ghi nhận, không tự sửa)

**5.1 `docs/tasks/` có hai khuôn mẫu không tương thích nhau.**
Bản ngắn theo `TASK_HANDOFF.md` (`## Bối cảnh` → `## Việc cần làm` → `## DoD`, 50–140 dòng, ví dụ `2026-06-19-reindex-tier1-debounce.md`) và bản dài theo `tech_docs/rules/1_technical-spec-template.md` (`## 1. Tổng quan` → `## 13.`, 300–959 dòng, ví dụ `2026-08-12-chat-inline-images.md`).
Ngoài ra `REVIEW_STANDARDS.md` yêu cầu **gộp "test cái gì" vào DoD**, nhưng `2026-06-19-reindex-tier1-debounce.md` vẫn để mục `## Cần test gì` rời — quy ước viết ra sau, file cũ chưa cập nhật.

**5.2 Khối metadata đầu file có ít nhất bốn biến thể.**
`- **Date:** / - **Status:**` (24/132 spec) · `**Ngày:**` in đậm không gạch đầu dòng (`tasks/2026-06-24-…`) · `- **Trạng thái:** / - **Tác giả:** / - **Ngày cập nhật:**` (5 file, theo template `tech_docs/rules/1`) · `_Last updated: …_` in nghiêng (`REPO_STATUS.md`).
108/132 spec **không có** ngày trong nội dung file, chỉ có trong tên file.

**5.3 Ngôn ngữ của `plans/` và `specs/` không có quy tắc.**
Plans: 45 Việt / 98 Anh. Specs: 21 Việt / 111 Anh. Cùng một tính năng có thể spec tiếng Anh còn task doc tiếng Việt.
Riêng `docs/tasks/` (13/13 Việt), `handoff/frontend/` (5/5 Việt), `docs/architecture/` + `docs/backend/` (19/19 Anh) thì nhất quán tuyệt đối.

**5.4 Hợp đồng FE nằm ở hai nơi, và có bản trùng đã lệch nhau.**
`docs/QUESTION_BANK_API_GUIDE.md` (46.873 byte) và `handoff/frontend/QUESTION_BANK_API_GUIDE.md` (49.852 byte) là hai bản **khác nội dung** của cùng một tài liệu.
Tương tự, `plans/2026-07-04-agent-geometry-jsxgraph.md` Task 9 yêu cầu tạo `handoff/frontend/GEOMETRY_SPEC.md`, nhưng file thực tế nằm ở `docs/GEOMETRY_SPEC.md`.
→ Ranh giới giữa `docs/api/`, `docs/<UPPER_SNAKE>.md` và `handoff/frontend/` chưa được định nghĩa ở đâu cả.

**5.5 `docs/README.md` không phải chỉ mục đầy đủ.**
Nó liệt kê ~20 file trong khi `docs/` có hơn 300. Các thư mục `tasks/`, `api/`, `architecture/`, `audits/` **không được nhắc tới**. Không rõ tiêu chí nào quyết định một doc có được đưa vào chỉ mục hay không.

**5.6 Tên file `docs/product/` trộn tiếng Anh và tiếng Việt không dấu.**
`quota-rules.md`, `cost-model.md` cạnh `chi-phi-3-goi-dich-vu.md`, `quan-tri-tai-khoan-quyen-va-token.md`, `phan-anh-va-cai-thien.md`. Không có quy tắc phân biệt.

**5.7 Kiểu bảng markdown 50/50.**
410 dòng phân cách kiểu gọn `|---|---|` so với 415 dòng kiểu có khoảng trắng `| --- | --- |`. Không có chuẩn; giữ nhất quán trong phạm vi một file là đủ.

**5.8 `docs/ops/` trộn ba kiểu đặt tên.**
Không ngày (`vps-deploy-runbook.md`), có ngày đầu (`2026-06-27-ci-actions-…`), ngày ở giữa (`incident-2026-07-16-staging-chat-503-…`).

**5.9 Frontend không có nơi cho docs của chính nó.**
Repo `bookforge-fe` không có `docs/`. Mọi tài liệu về FE phải đặt nhờ trong repo backend (§2.1). Đây là hiện trạng, không phải quyết định được ghi ở đâu — nếu muốn đổi thì cần chốt riêng.

---

## 6. Checklist tự kiểm khi viết một file docs mới

- [ ] Đặt đúng thư mục theo §1.1/§4, tên file đúng kiểu chữ của thư mục đó (`UPPER_SNAKE` ở `docs/` root, `kebab-case` ở thư mục con) và có `YYYY-MM-DD-` nếu là `tasks`/`specs`/`plans`/`audits`.
- [ ] Slug ngắn gọn: 2–4 từ khoá nêu đúng chủ đề chính, không nhồi thêm phạm vi/chi tiết phụ vào tên file (chi tiết đó để trong nội dung file).
- [ ] Không tự tạo file trong `docs/superpowers/specs/` hoặc `docs/audits/` trừ khi được yêu cầu rõ ràng (§3) — cần mô tả việc cần làm thì viết task doc ở `docs/tasks/` thay vào đó.
- [ ] Dùng đúng khung heading của loại doc đó (§1.2), không tự chế mục mới khi khuôn mẫu đã có.
- [ ] Ngôn ngữ khớp thư mục: `tasks/` và `handoff/frontend/` viết tiếng Việt; `architecture/` và `backend/` viết tiếng Anh; định danh code luôn để nguyên trong backtick.
- [ ] Mọi link file là **đường dẫn tương đối tính từ chính file doc** và bấm được; trỏ code kèm `file:line`.
- [ ] Không frontmatter, không mục changelog, không trường người được giao; code block nào cũng gắn ngôn ngữ; sơ đồ vẽ bằng ASCII.
- [ ] Nếu là file giao việc: có banner "Cách đọc tài liệu này", mục "Quyết định đã chốt", và **DoD dạng checkbox kiểm chứng được đã gộp phần test vào**.
- [ ] Sau khi tự kiểm DoD (đạt, thiếu, hay có thay đổi so với lúc viết): **sửa ngay trong chính file đó** — tick `- [x]` cho mục đã đạt, cập nhật lại nội dung/trạng thái không còn đúng. Không tạo file `.md` mới hay báo cáo riêng chỉ để ghi lại kết quả kiểm tra (xem §3 — không tự sinh file ghi lại việc đã làm nếu không được yêu cầu).
- [ ] Độ dài nằm trong khoảng của loại đó (§1.4); file giao việc vượt ~300 dòng thì tách phần thiết kế ra `specs/`.
- [ ] Nếu doc đáng để người khác tìm thấy: thêm một dòng mô tả vào [`backend/docs/README.md`](../../backend/docs/README.md).
