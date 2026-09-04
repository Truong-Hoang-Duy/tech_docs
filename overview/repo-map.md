# BookForge — Bản đồ tra cứu repo

> **Đây là MỤC LỤC, không phải tài liệu thiết kế.** Mỗi mục một dòng, đủ để hỏi cho trúng chỗ, không đủ để kết luận về cách code chạy.
> Dùng kèm [`backend-features-all.md`](backend-features-all.md) làm gói ngữ cảnh dán vào Claude Web — xem [`rules/2_web-code-handoff.md`](../rules/2_web-code-handoff.md) §3.
> Nguồn: `bookforge@e177816` (origin/dev) · `bookforge-fe@73812fd` (origin/dev) — **2026-09-04**.
> Đây là mốc để tính diff ở lần cập nhật sau; **ref quét do bạn chỉ định mỗi lần** — xem [`rules/2_web-code-handoff.md`](../rules/2_web-code-handoff.md) §3.
> Đường dẫn BE tính từ gốc repo `bookforge`, FE tính từ gốc repo `bookforge-fe`.

---

## 1. Tiến trình đang chạy

| Thành phần | Nơi khai báo | Vai trò |
|---|---|---|
| API (FastAPI) | `services/api/src/bookforge_api/main.py` | Toàn bộ HTTP endpoint ở §2 |
| RQ worker | `services/api/src/bookforge_api/workers/worker.py` | Chạy job nền ở §5 |
| Cron CLI | `services/api/src/bookforge_api/cron/runner.py` | 6 job định kỳ ở §5 |
| `knowledge-ingestion` | `services/knowledge-ingestion/` | Nạp & chunk tài liệu cho RAG (HTTP, mặc định `:9380`) |
| `knowledge-retrieval` | `services/knowledge-retrieval/` | Truy hồi hybrid cho chat (HTTP, mặc định `:9381`) |
| `gotenberg` | `services/gotenberg/` | Render DOCX/PPTX → PDF |
| Hạ tầng dev | `infra/dev/compose.yml` | valkey (Redis), minio, mysql + elasticsearch cho knowledge |

Middleware theo thứ tự vào: CORS → `RequestIdMiddleware` (`main.py:70-78`). Lỗi tập trung ở `register_error_handlers` (`errors/`).

---

## 2. Endpoint

234 endpoint, nhóm theo router trong `services/api/src/bookforge_api/api/`.
Router có ghi **[gate question_bank]** bị chặn bởi `Depends(require_feature('question_bank'))` (`main.py:87`) — xem §6.

**`auth.py`** — `/api/auth`

```text
POST   /login                          POST   /logout
GET    /session                        GET    /me
PATCH  /me                             POST   /me/avatar
DELETE /me/avatar                      POST   /me/avatar/library
GET    /me/avatar/file
POST   /password-reset/request         POST   /password-reset/confirm
GET    /account-setup/validate         POST   /account-setup/complete
```

**`admin.py`** — `/api/admin`

```text
GET    /users                          POST   /users
PATCH  /users/{user_id}                DELETE /users/{user_id}
POST   /users/{user_id}/resend-invitation
POST   /users/{user_id}/reset-password
POST   /subscriptions/activate
```

**`organizations.py`** — `/api/organizations`

```text
GET    /me            PATCH  /me
POST   /me/logo       DELETE /me/logo       GET /me/logo/file
```

**`academic_years.py`** — `/api/academic-years`

```text
GET    /current                        POST   /current/semesters
PATCH  /semesters/{semester_id}        DELETE /semesters/{semester_id}
```

**`asset_library.py`** — `/api/asset-library` · `GET /avatars`, `GET /avatars/{key}`

**`health.py`** · `GET /health`, `GET /health/ready`

**`quota.py`** · `GET /api/quota/summary` — **`storage_usage.py`** · `GET /api/storage/usage`

**`dashboard.py`** (không prefix)

```text
GET    /api/dashboard/quota            GET    /api/dashboard/overview
GET    /api/admin/dashboard            GET    /api/documents/{document_id}/dashboard
```

**`document_folders.py`** — `/api/document-folders`

```text
GET    ""  (danh sách)                 POST   ""  (tạo)
GET    /{folder_id}    PATCH  /{folder_id}    DELETE /{folder_id}
```

**`documents.py`** — `/api/documents`

```text
GET    ""  (danh sách)                 POST   /upload
POST   /from-chat-message              GET    /trash
GET    /{document_id}                  PATCH  /{document_id}
DELETE /{document_id}                  POST   /{document_id}/restore
POST   /{document_id}/purge            POST   /{document_id}/approval
POST   /{document_id}/reprocess        POST   /{document_id}/knowledge/reindex
GET    /{document_id}/source-file      GET    /{document_id}/preview
GET    /{document_id}/source-preview.pdf
GET    /{document_id}/export           GET    /{document_id}/download
GET    /{document_id}/share-targets    GET    /{document_id}/shares
POST   /{document_id}/shares           DELETE /{document_id}/shares/{user_id}
```

**`editor.py`** — `/api/documents/{document_id}/editor` (canvas)

```text
GET    ""   (nội dung)                 PUT    ""   (lưu)
GET    /session                        GET    /assets/{asset_path:path}
POST   /jsxgraph/preview               POST   /jsxgraph
PUT    /jsxgraph/{asset_id}            GET    /geometry/{asset_id}
GET    /chat/sessions                  POST   /chat/sessions
GET    /chat/sessions/{session_id}     DELETE /chat/sessions/{session_id}
POST   /assistant                      POST   /assistant/stream   (SSE)
```

**`chat.py`** (không prefix — chat ngoài canvas)

```text
GET    /api/chat/modes                 GET    /api/chat/models
GET    /api/chat/sessions              POST   /api/chat/sessions
GET    /api/chat/sessions/{session_id} PATCH  /api/chat/sessions/{session_id}
DELETE /api/chat/sessions/{session_id}
POST   /api/chat/sessions/{session_id}/ask-back
POST   /api/chat/sessions/{session_id}/ask-back/stream      (SSE)
POST   /api/chat/sessions/{session_id}/messages
POST   /api/chat/sessions/{session_id}/messages/stream      (SSE)
GET    /api/documents/{document_id}/tree
GET    /api/documents/{document_id}/pages
GET    /api/documents/{document_id}/search
```

**`assistant_tools.py`** — `/api/assistant-tools`

```text
POST   /spellcheck    /risk-scan    /summarize
POST   /style-rewrite /continue-writing /rewrite
```

**`standalone_presentations.py`** — `/api/documents/presentations` (đăng ký **trước** `presentations.py`, `main.py:102`)

```text
GET    /themes                         GET    /templates
POST   /outline                        POST   /outline/stream   (SSE)
POST   /build                          GET    /library
DELETE /library/remove
POST   /geometry-preview               GET    /geometry-previews/{preview_id}
GET    /decks/{deck_id}/state
GET    /files/{file_name}              GET    /files/{file_name}/preview.pdf
```

**`presentations.py`** — `/api/documents/{document_id}/presentations`

```text
GET    ""  (danh sách)                 POST   ""  (tạo)
GET    /outline-nodes                  POST   /outline    POST /outline/stream  (SSE)
GET    /{presentation_id}/download     GET    /{presentation_id}/preview.pdf
POST   /{presentation_id}/google-export
```

**`pptx_templates.py`** — `/api/admin/pptx-templates` · `GET ""`, `POST ""`, `PATCH /{template_id}`, `POST /{template_id}/default`

**`question_folders.py`** — `/api/question-folders` **[gate question_bank]**

```text
GET    ""   POST   ""                  GET /taxonomy    GET /tree
GET    /{folder_id}   PATCH /{folder_id}   DELETE /{folder_id}
```

**`question_knowledge_frameworks.py`** — `/api/question-knowledge-frameworks` **[gate]**
**`question_competency_frameworks.py`** — `/api/question-competency-frameworks` **[gate]**
Hai router cùng khuôn:

```text
GET    ""   POST   ""
GET    /{framework_id}   PATCH /{framework_id}   DELETE /{framework_id}
POST   /{framework_id}/clone
```

**`question_knowledge_nodes.py`** — `/api/question-knowledge-nodes` **[gate]**
**`question_competency_nodes.py`** — `/api/question-competency-nodes` **[gate]**
Hai router cùng khuôn:

```text
GET    ""   POST   ""
GET    /{node_id}   PATCH /{node_id}   DELETE /{node_id}
```

**`question_cards.py`** — `/api/question-cards` **[gate]** — router lớn nhất, 44 endpoint

```text
── CRUD ─────────────────────────────────────────────────────────────
GET    ""  (danh sách)                 POST   ""  (tạo)
GET    /{card_id}                      PATCH  /{card_id}
DELETE /{card_id}                      POST   /{card_id}/duplicate
GET    /trash    POST /{card_id}/restore    POST /{card_id}/purge
POST   /bulk     PATCH /bulk-update
── Bộ lọc & thống kê ────────────────────────────────────────────────
GET    /filter-options                 GET    /dashboard
GET    /review-dashboard               GET    /reviewers
── Duyệt (review) ───────────────────────────────────────────────────
GET    /review-queue                   GET    /review-queue/options
POST   /bulk/review                    POST   /bulk/approve
POST   /{card_id}/approve              POST   /{card_id}/reject
POST   /{card_id}/assign               POST   /{card_id}/priority
POST   /{card_id}/request-changes
POST   /review-sessions                GET    /review-sessions
GET    /review-sessions/{session_id}
POST   /review-sessions/{session_id}/items
POST   /review-sessions/{session_id}/items/details
GET    /review-sessions/{session_id}/items/{card_id}
POST   /review-sessions/{session_id}/items/{card_id}/decision
POST   /review-sessions/{session_id}/bulk-decision
POST   /review-sessions/{session_id}/complete
── Sinh / trích xuất bằng AI ────────────────────────────────────────
POST   /generate                       POST   /convert
POST   /extract                        GET    /extract/{job_id}   (job nền, §5)
POST   /quality-check                  POST   /check-duplicates
── Ảnh & tích hợp ngoài ─────────────────────────────────────────────
POST   /assets/images                  GET    /assets/images/file
GET    /cohota/question-banks          POST   /{card_id}/cohota   POST /bulk/cohota
```

**`question_cart.py`** — `/api/question-cart` **[gate]**

```text
GET    ""  (giỏ)    DELETE ""  (xoá sạch)
GET    /summary     POST   /items      DELETE /items/{card_id}
POST   /reorder     POST   /bulk       POST   /keep-approved
POST   /collections
```

**`question_collections.py`** — `/api/question-collections` **[gate]**

```text
GET    ""   POST   ""
GET    /{collection_id}   PATCH /{collection_id}   DELETE /{collection_id}
POST   /{collection_id}/items    DELETE /{collection_id}/items/{card_id}
POST   /{collection_id}/reorder  GET    /{collection_id}/summary
POST   /{collection_id}/cohota
```

**`test_papers.py`** — `/api/test-papers` **[gate]**

```text
GET    ""   POST   ""                  GET    /templates
GET    /{paper_id}   PATCH /{paper_id}   DELETE /{paper_id}
POST   /{paper_id}/items               DELETE /{paper_id}/items/{card_id}
POST   /{paper_id}/items/reorder       POST   /{paper_id}/items/section
GET    /{paper_id}/matrix-check        GET    /{paper_id}/canvas-sync-status
POST   /{paper_id}/canvas/regenerate   POST   /{paper_id}/refresh-from-source
GET    /{paper_id}/answer-card         POST   /{paper_id}/answer-card/refresh
POST   /{paper_id}/answer-card/sync
POST   /{paper_id}/variants            GET    /{paper_id}/variants
```

---

## 3. Bảng dữ liệu

Model SQLAlchemy ở `services/api/src/bookforge_api/models/`. Cột `FK` là khoá ngoại trỏ đi.

**`user.py` — tài khoản & tổ chức**

| Bảng | Class | FK |
|---|---|---|
| `organizations` | `Organization` | — (gốc cách ly dữ liệu) |
| `users` | `User` | `organizations.id` |
| `sessions` | `SessionRecord` | `users.id` |
| `password_reset_tokens` | `PasswordResetToken` | `users.id` |
| `account_setup_tokens` | `AccountSetupToken` | `users.id` |

**`document.py` — tài liệu, canvas, chat, trình chiếu**

| Bảng | Class | FK |
|---|---|---|
| `document_folders` | `DocumentFolder` | `organizations.id`, `users.id` |
| `documents` | `Document` | `document_folders.id`, `organizations.id`, `users.id` |
| `document_shares` | `DocumentShare` | `documents.id`, `users.id` |
| `knowledge_documents` | `KnowledgeDocument` | `documents.id`, `organizations.id` |
| `editor_documents` | `EditorDocument` | `documents.id` |
| `document_visual_assets` | `DocumentVisualAsset` | `documents.id`, `organizations.id` |
| `chat_sessions` | `ChatSession` | `organizations.id`, `users.id` |
| `chat_messages` | `ChatMessage` | `chat_sessions.id` |
| `canvas_chat_sessions` | `CanvasChatSession` | `documents.id`, `organizations.id`, `users.id` |
| `canvas_chat_messages` | `CanvasChatMessage` | `canvas_chat_sessions.id` |
| `presentations` | `Presentation` | `documents.id` |
| `pptx_templates` | `PptxTemplate` | `organizations.id`, `users.id` |
| `pptx_template_grants` | `PptxTemplateGrant` | `organizations.id` |
| `export_jobs` | `ExportJob` | `presentations.id` |
| `retrieval_traces` | `RetrievalTrace` | `documents.id` |
| `ai_actions` | `AIAction` | `organizations.id`, `users.id` |
| `event_log` | `EventLog` | `documents.id`, `organizations.id`, `users.id` |

**`question_bank.py` — ngân hàng câu hỏi & đề thi**

| Bảng | Class | FK |
|---|---|---|
| `question_folders` | `QuestionFolder` | `organizations.id`, `question_folders.id` (tự trỏ), `users.id` |
| `question_knowledge_frameworks` | `QuestionKnowledgeFramework` | `organizations.id`, `users.id` |
| `question_competency_frameworks` | `QuestionCompetencyFramework` | `organizations.id`, `users.id` |
| `question_knowledge_nodes` | `QuestionKnowledgeNode` | framework, tự trỏ, `organizations.id`, `users.id` |
| `question_competency_nodes` | `QuestionCompetencyNode` | framework, tự trỏ, `organizations.id`, `users.id` |
| `question_cards` | `QuestionCard` | `documents.id`, `organizations.id`, `question_cards.id` (tự trỏ), `question_folders.id`, `users.id` |
| `question_card_knowledge_nodes` | `QuestionCardKnowledgeNode` | `question_cards.id`, `question_knowledge_nodes.id` |
| `question_card_competency_nodes` | `QuestionCardCompetencyNode` | `question_cards.id`, `question_competency_nodes.id` |
| `question_review_sessions` | `QuestionReviewSession` | `organizations.id`, `users.id` |
| `question_review_session_items` | `QuestionReviewSessionItem` | `question_cards.id`, `question_review_sessions.id`, `users.id` |
| `question_cart_items` | `QuestionCartItem` | `organizations.id`, `question_cards.id`, `users.id` |
| `question_collections` | `QuestionCollection` | `organizations.id`, `users.id` |
| `question_collection_items` | `QuestionCollectionItem` | `question_cards.id`, `question_collections.id` |
| `test_papers` | `TestPaper` | `documents.id`, `organizations.id`, `question_collections.id`, `users.id` |
| `test_paper_items` | `TestPaperItem` | `question_cards.id`, `test_papers.id` |
| `test_paper_variants` | `TestPaperVariant` | `documents.id`, `test_papers.id` |
| `answer_cards` | `AnswerCard` | `documents.id`, `test_papers.id` |

**Còn lại**

| Bảng | Class | File | FK |
|---|---|---|---|
| `academic_years` | `AcademicYear` | `academic_year.py` | `organizations.id` |
| `semesters` | `Semester` | `academic_year.py` | `academic_years.id`, `organizations.id` |
| `quota_plans` | `QuotaPlan` | `quota.py` | — |
| `subscriptions` | `Subscription` | `quota.py` | `organizations.id`, `quota_plans.plan_key`, `users.id` |
| `quota_snapshots` | `QuotaSnapshot` | `quota.py` | `organizations.id`, `subscriptions.id` |
| `provider_cost_events` | `ProviderCostEvent` | `provider_cost.py` | `ai_actions.id`, `documents.id`, `organizations.id`, `users.id` |
| `storage_objects` | `StorageObject` | `storage_object.py` | `documents.id`, `organizations.id` |
| `organization_feature_flags` | `OrganizationFeatureFlag` | `features.py` | `organizations.id` |
| `expert_agents` | `ExpertAgent` | `expert.py` | — |
| `expert_agent_grants` | `ExpertAgentGrant` | `expert.py` | `expert_agents.id`, `organizations.id` |

---

## 4. Frontend

Route khai báo tập trung ở `src/App.tsx`. `protectedRoute` = bọc `RequireAuth`; `protectedFeatureRoute` = thêm `RequireFeature`.

| Route | Component | Thư mục |
|---|---|---|
| `/` | `HomePage` | `src/templates/HomePage/` |
| `/auth/sign-in`, `/auth/forgot-password`, `/auth/check-email` | `SignInPage`, `ForgotPasswordPage`, `CheckEmailPage` | `src/templates/Auth/` |
| `/reset-password` | `ResetPasswordPage` | `src/templates/ResetPasswordPage/` |
| `/account-setup` | `AccountSetupPage` | `src/templates/AccountSetupPage/` |
| `/documents` | `DocumentsPage` | `src/templates/DocumentsPage/` |
| `/documents/:documentId` | `DocumentDetailPage` | `src/templates/DocumentDetailPage/` |
| `/documents/:documentId/report` | `DocumentReportPage` | `src/templates/DocumentReportPage/` |
| `/history` | `HistoryPage` | `src/templates/HistoryPage/` |
| `/feedback-improvement/*` | `FeedbackImprovementPage` | `src/templates/FeedbackImprovementPage/` |
| `/create-ppt` | `CreatePowerPointPage` | `src/templates/CreatePowerPointPage/` |
| `/question-bank` | `QuestionBankPage` | `src/templates/QuestionBankPage/` — **[feature `question_bank`]** |
| `/question-bank/folders` | `QuestionBankPage folderListOnly` | ↑ |
| `/question-bank/curriculum` | `CurriculumPage` | ↑ |
| `/question-bank/editor/:cardId` | `QuestionCardEditorPage` | ↑ |
| `/question-bank/import` | `QuestionImportNotebookPage` | ↑ |
| `/question-bank/review` | `QuestionReviewSessionsPage` | ↑ |
| `/question-bank/review/sessions/:sessionId` | `QuestionReviewSessionPage` | ↑ |
| `/question-bank/sets` | `QuestionCollectionSetsPage` | ↑ |
| `/question-bank/exams` | `QuestionTestPapersPage` | ↑ |
| `/question-bank/trash` | `QuestionTrashPage` | ↑ |
| `/settings` | `AccountManagementPage` | `src/templates/AccountManagementPage/` |
| `/dashboard` | `DashboardPage`, hoặc `DocumentReportPage` khi có `?documentId` | `src/templates/DashboardPage/` |
| `/research`, `/templates` | redirect về `/` | — |

**Tầng gọi API — `src/api/`**

| File | Số export | Phủ endpoint |
|---|---|---|
| `question-bank-api.ts` | 216 | toàn bộ `/api/question-*`, `/api/test-papers` |
| `bookforge-api.ts` | 122 | auth, tổ chức, năm học, chat, trình chiếu, asset library |
| `document-api.ts` | 44 | `/api/documents`, `/api/document-folders` |
| `assistant-tools-api.ts` | 19 | `/api/assistant-tools/*` |
| `overview-dashboard-api.ts` | 16 | `/api/dashboard/*`, `/api/quota/summary` |
| `admin-users-api.ts` | 15 | `/api/admin/users*` |
| `api-request.ts` | 8 | lớp fetch chung (`credentials: 'include'`) |
| `api-error-format.ts`, `api-error-message.ts` | 1, 3 | chuẩn hoá lỗi từ BE |
| `pagination.ts`, `query-client.ts`, `upload-document-request.ts` | 1 mỗi file | phân trang, React Query, upload |

**Thư mục khác:** `src/components/` (42 thư mục dùng chung — `TiptapEditor`, `Chat`, `PresentationPreview`, `RequireAuth`, `RequireFeature`, `Toast`…), `src/hooks/` (`use-chat-modes`, `use-feature`, `use-paginated-query`, `use-infinite-scroll`, `use-share-targets-query`…), `src/contexts/auth-context.tsx`, `src/lib/` (`feature-flags`, `read-sse-stream`, `pdfjs`, `load-preview-pdf`, `extract-question-cards`).

---

## 5. Việc chạy nền

**Job RQ** — hàm ở `workers/jobs.py`, hàng đợi ở `workers/queue.py`:

| Job | Nơi gọi enqueue | Hàng đợi |
|---|---|---|
| `ingest_document_job` | `api/documents.py:606` (nạp tài liệu) | `BOOKFORGE_INGEST_RQ_QUEUE` (`ingest`) |
| `reindex_knowledge_job` | `api/documents.py:496,929` · `api/editor.py:1218` · `api/chat.py:1142` · `api/test_papers.py:70` · `workers/jobs.py:66` (nối sau ingest) · `cron/reap_stuck_reindex.py:127` · `services/knowledge_backfill.py:137` | `BOOKFORGE_INDEX_RQ_QUEUE` (`index`) |
| `run_exam_extract_job` | `api/question_cards.py:1055`, theo dõi qua `GET /extract/{job_id}` | `ingest` |
| `render_preview_pdf_job` | `services/preview_serve.py:71` | `ingest` |
| `finalize_generated_deck_job` | `api/presentations.py:451` · `api/standalone_presentations.py:871,988` | `ingest` |
| `render_inapp_thumbnail_job` | `api/documents.py:491` · `api/editor.py:1198` · `api/chat.py:1136` | `ingest` |

`BOOKFORGE_QUEUE_INLINE=true` (mặc định dev) chạy job **đồng bộ ngay trong request**, không qua Redis.

**Cron** — `bookforge-api-cron <job>`, đăng ký ở `cron/runner.py:21-28`; lịch chạy do scheduler của host quyết định, **không nằm trong repo**:

```text
expire-subscriptions   purge-trash            reap-stuck-ingests
reap-stuck-reindex     reconcile              warn-approaching-limits
```

---

## 6. Feature flag

Định nghĩa ở `services/features.py:44-55`. Một tính năng bật khi **env bật VÀ tổ chức được cấp** (bảng `organization_feature_flags`, riêng `expert_agents` đọc `expert_agent_grants`).

| Key | Env tương ứng | Nơi chặn |
|---|---|---|
| `question_bank` | `BOOKFORGE_QUESTION_BANK_ENABLED` | 9 router ở §2, và `RequireFeature` phía FE |
| `chat_workspace` | `BOOKFORGE_CHAT_WORKSPACE_ENABLED` | trong `chat/` |
| `chat_document_tools` | `BOOKFORGE_CHAT_DOCUMENT_TOOLS_ENABLED` | trong `chat/` |
| `editor_focus_envelope` | `BOOKFORGE_EDITOR_FOCUS_ENVELOPE_ENABLED` | trong `editor/` |
| `grid_deck` | `BOOKFORGE_GRID_DECK_ENABLED` | luồng PPTX |
| `legal_mode` | `BOOKFORGE_LAW_ENABLED` | `law/`, `chat/legal_tools.py` |
| `expert_agents` | `BOOKFORGE_EXPERT_AGENTS_ENABLED` | `chat/expert_*.py` |

Cờ chỉ bật bằng env, không có cấp theo tổ chức: `authorization_document_shadow`, `authorization_document_view_enforcement`, `chat_agent_expanded_budget`, `chat_inline_images`, `model_switcher`, `knowledge`, `knowledge_per_org_collections`, `law_drafting` (`services/features.py:24-34`).

---

## 7. Biến môi trường

**Backend** — `core/settings.py`, tiền tố **`BOOKFORGE_`** + tên trường viết hoa (VD trường `database_url` → `BOOKFORGE_DATABASE_URL`). Đọc từ `services/api/.env`. 183 trường, nhóm chính:

| Nhóm | Trường tiêu biểu |
|---|---|
| Chạy & mạng | `ENV`, `API_HOST`, `API_PORT`, `APP_ORIGIN`, `UVICORN_WORKERS`, `BUILD_COMMIT` |
| CSDL | `DATABASE_URL`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT_SECONDS`, `PG_MAX_CONNECTIONS` |
| Hàng đợi | `REDIS_URL`, `RQ_QUEUE`, `INGEST_RQ_QUEUE`, `INDEX_RQ_QUEUE`, `QUEUE_INLINE`, `WORKER_COUNT` |
| Lưu trữ | `STORAGE_ROOT`, `STORAGE_READY_MIN_FREE_BYTES`, `STORAGE_UPLOAD_MIN_FREE_BYTES`, `STORAGE_STAGING_MAX_AGE_HOURS` |
| Phiên & bảo mật | `SESSION_COOKIE_NAME`, `SESSION_COOKIE_SECURE`, `SESSION_TTL_HOURS`, `LOGIN_FAILURE_MAX_PER_IP`, `LOGIN_FAILURE_MAX_PER_ACCOUNT` |
| Email & mời | `EMAIL_PROVIDER`, `RESEND_API_KEY`, `EMAIL_FROM_ADDRESS`, `PASSWORD_RESET_TTL_MINUTES`, `ACCOUNT_SETUP_TTL_HOURS`, `TERMS_VERSION` |
| LLM — nhà cung cấp | `TEXT_LLM_PROVIDER/MODEL/API_KEY/BASE_URL`, `IMAGE_LLM_*`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY` |
| LLM — theo thao tác | `LLM_OP_*` (`ANSWER`, `OUTLINE`, `CHAT`, `EDITOR_*`, `GEOMETRY`, `QUESTION_BANK`, `QUESTION_EXAM_EXTRACT`…) + `*_REASONING_EFFORT` |
| Chống nghẽn Gemini | `GEMINI_RPM_LIMIT`, `GEMINI_BURST`, `GEMINI_MAX_IN_FLIGHT`, `GEMINI_429_FALLBACK_COOLDOWN_MS` |
| Chat & truy hồi | `CHAT_RETRIEVAL_*`, `CHAT_AGENT_REQUEST_LIMIT`, `CHAT_AGENT_TOOL_CALLS_LIMIT`, `CHAT_HISTORY_MAX_MESSAGES`, `CHAT_READ_*` |
| Canvas / editor | `EDITOR_MODEL_TIMEOUT_SECONDS`, `EDITOR_TURN_TIMEOUT_SECONDS`, `EDITOR_DOCUMENT_MAX_WORDS`, `EDITOR_ENVELOPE_*` |
| Trích đề thi | `EXAM_EXTRACT_PAGE_CEILING`, `EXAM_EXTRACT_WINDOW_PAGES`, `EXAM_EXTRACT_LLM_CONCURRENCY`, `EXAM_EXTRACT_JOB_TIMEOUT_SECONDS` |
| Trần cứng (hard limit) | `DEFAULT_MAX_UPLOAD_BYTES`, `UPLOAD_BYTES_CEILING`, `DOCUMENT_PAGES_CEILING`, `SLIDE_DECK_SLIDES_CEILING`, `QUESTION_SET_QUESTIONS_CEILING`, `SINGLE_TASK_TOKEN_CEILING_INFRA` |
| RAG / knowledge | `KNOWLEDGE_ENABLED`, `KNOWLEDGE_INGESTION_URL`, `KNOWLEDGE_RETRIEVAL_URL`, `KNOWLEDGE_API_TOKEN`, `KNOWLEDGE_CHUNK_TOKEN_NUM`, `KNOWLEDGE_REINDEX_DEBOUNCE_SECONDS` |
| Pháp lý | `LAW_ENABLED`, `LAW_SERVICE_URL`, `LAW_API_TOKEN`, `LAW_TOOL_TIMEOUT_SECONDS` |
| Tích hợp ngoài | `COHOTA_BASE_URL`, `COHOTA_API_TOKEN`, `COHOTA_COURSE_ID`, `COHOTA_QUESTION_BANK_ID`, `GOTENBERG_BASE_URL` |

**Frontend** — `frontend/.env.example`: `VITE_BOOKFORGE_BACKEND_TARGET` (proxy tới BE), `VITE_ENABLE_FEEDBACK_PROTOTYPE`, `VITE_DEV_EMAIL`, `VITE_DEV_PASSWORD`.

---

## 8. Vùng chưa lập bản đồ

Nói rõ để không tưởng là đã đủ — hỏi `[ĐỊNH VỊ]` cho những vùng này:

- **Bên trong `services/` của backend (86 module)**: chỉ có tên file, chưa có mô tả từng module. Các cụm lớn: `question_*` (15 file), `document_*`/`documents.py`, `quota_*` (6 file), `presentation*`, `geometry/` và `jsxgraph/` (hai stack hình học song song).
- **`chat/`**: `adk_agent.py`, `editor_agent.py`, `workspace_tools.py`, `legal_tools.py`, `expert_tools.py` — chưa liệt kê tool nào của agent.
- **Cột của bảng**: §3 chỉ có tên bảng + khoá ngoại, **không có danh sách cột**. Cần cột thì hỏi.
- **Shape request/response**: nằm ở `schemas/`, chưa liệt kê.
- **`authorization/`, `errors/`, `export/`, `ingest/`, `llm/`, `pptx/`, `storage/`, `law/`, `knowledge/`**: chưa mở.
- **Hai service RAG** (`knowledge-ingestion`, `knowledge-retrieval`): chưa liệt kê endpoint nội bộ.
- **Frontend**: mới có route và tầng API. Cấu trúc bên trong `components/` và `templates/` (đặc biệt `QuestionBankPage/`, `TiptapEditor/`) chưa mở.
- **Lịch cron thật** và cấu hình deploy: nằm ở host, xem `docs/ops/vps-deploy-runbook.md`.
- **Test**: chưa lập bản đồ `services/api/tests/`.
