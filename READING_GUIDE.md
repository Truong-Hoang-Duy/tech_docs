# Hướng dẫn đọc source `backend/` — BookForge

> Tài liệu onboarding: kiến trúc, bản đồ thư mục, lộ trình đọc và các bẫy thường gặp.
> Link trong file là **đường dẫn tương đối** — mở bằng VSCode (Markdown Preview hoặc Ctrl/Cmd+Click) trên bất kỳ máy nào có repo này là bấm mở được file. Cập nhật: 2026-07-18.

## 1. BookForge là gì?

Đây là **monorepo backend** cho một sản phẩm giáo dục tiếng Việt. Luồng giá trị chính: người dùng **upload tài liệu** (PDF/DOCX/PPTX/ảnh) → hệ thống xử lý song song thành **hai thứ**: (a) bản **"canvas" chỉnh sửa được** (OCR → HTML/Markdown cho editor) và (b) **tri thức tìm kiếm được** (RAG index). Trên nền đó có: **chat hỏi đáp có trích dẫn**, **sinh slide PPTX**, mini-tools AI (viết lại, tóm tắt…), cùng nền tảng auth/tổ chức/chia sẻ/quota/dashboard.

Ba điều định hình cách đọc repo này:

- **Hai sản phẩm, một codebase**: bản thường + bản luật (law), khác nhau bằng **config chứ không fork**. Code luật phát triển trên nhánh `feat/legal-mode`.
- **Không có frontend ở đây** — FE React/Vite nằm ở repo riêng `bookforge-fe`. Repo này chỉ expose API.
- **Git history rất ngắn là cố ý**: repo là baseline 1 commit từ 2026-06-09, ~1090 commit cũ được bỏ lại — xem [REPO_STATUS.md](REPO_STATUS.md). Đừng dùng `git log` để hiểu lịch sử.

## 2. Tech stack

| Mảng | Công nghệ |
|---|---|
| Ngôn ngữ / tooling | Python 3.13, **uv** (package manager, cũng tải luôn Python), Ruff, pre-commit |
| Web | **FastAPI** + uvicorn, Pydantic v2 |
| Data | SQLAlchemy 2.0 + Alembic; **Postgres 17** (prod) / **SQLite** (dev) |
| Queue | **RQ** trên **Valkey 8** (Redis-compatible); dev chạy inline không cần worker |
| RAG backend | MySQL 8 + Elasticsearch 8.11 + MinIO (thuộc 2 service knowledge) |
| LLM | **PydanticAI** đa provider — **Gemini** là chính (OCR/chat/PPTX), OpenAI (embeddings + agent luật), Mistral OCR tùy chọn; routing theo từng operation qua env `BOOKFORGE_LLM_OP_*`. Không GPU — toàn hosted API |
| Khác | Caddy (reverse proxy), **Gotenberg** (render PDF/PPTX qua LibreOffice), Resend (email), Pexels (ảnh cho slide) |

## 3. Bản đồ thư mục top-level

| Thư mục | Là gì | Đọc khi nào |
|---|---|---|
| [services/](../services/) | 4 đơn vị deploy — trong đó `api/` là toàn bộ code chính | **Ngay** — 80% thời gian ở `services/api` |
| [docs/](./) | Docs thiết kế: architecture, backend alignment, product, ops | Ngay sau README |
| [lawforge-bundle/](../lawforge-bundle/) | Service pháp điển (luật VN) **đang chạy thật** + bundle deploy — không phải đồ lưu trữ | Khi làm legal mode |
| [infra/](../infra/) | Docker Compose + Caddy (không k8s/Terraform); `profiles/` = preset hiệu năng | Khi cần chạy full stack |
| [scripts/](../scripts/) | Tooling deploy/bench/codegen — quan trọng nhất: [vps-deploy-be.sh](../scripts/deploy/vps-deploy-be.sh) | Khi đụng deploy |
| [benchmarks/](../benchmarks/) | Calibrate throughput Gemini cho `infra/profiles/*.env` | Hiếm khi |
| [handoff/](../handoff/) | Docs hợp đồng API bàn giao cho team FE — không service nào import | Bỏ qua khi onboard |
| [tools/](../tools/) | Tiện ích lẻ (md→html, rotate PEM cho RAGFlow) | Hiếm khi |
| [.github/](../.github/) | 1 workflow CI: ruff + pytest (có Postgres container) + tests phapdien; push `dev`→staging, `main`→prod | Khi đụng CI |
| [.claude/](../.claude/) | Skill review nội bộ `bookforge-review`, chuẩn ở [REVIEW_STANDARDS.md](REVIEW_STANDARDS.md) | Khi review PR |

**Rác ở root — bỏ qua, đừng tưởng là code thật**: `create_test_doc.py`, `fix_test_doc.py` (script debug 1 lần, hardcode path Windows), `normal_write_probe.txt`, `sqlite_write_probe_root.db(-journal)` (file probe quyền ghi), `test_tmp/`, `package-lock.json` (stub rỗng — backend này không có Node).

## 4. Chi tiết từng service

### 4.1. `services/api` — trái tim của repo

**Một codebase, ba process** (console scripts trong [pyproject.toml](../services/api/pyproject.toml)):

- `bookforge-api` → [main.py](../services/api/src/bookforge_api/main.py) — dựng FastAPI app, đăng ký middleware, error handlers và ~24 routers. **Đọc file này đầu tiên: danh sách router chính là bản đồ tính năng.**
- `bookforge-api-worker` → [workers/worker.py](../services/api/src/bookforge_api/workers/worker.py) — RQ worker, 2 lane queue `ingest` và `index`.
- `bookforge-api-cron` → [cron/runner.py](../services/api/src/bookforge_api/cron/runner.py) — job định kỳ (reconcile storage, hết hạn subscription, cảnh báo quota, dọn thùng rác); trên compose do container `ofelia` kích hoạt.

**Layout phân lớp trong [src/bookforge_api/](../services/api/src/bookforge_api/)** — mọi feature đều đọc theo cùng một công thức *router → service → model/schema*:

| Lớp | Vị trí | Ghi chú |
|---|---|---|
| Routers | [api/](../services/api/src/bookforge_api/api/) | 1 file / resource: `auth`, `documents`, `chat`, `editor`, `presentations`, `question_cards/cart/collections/folders`, `quota`, `admin`, `dashboard`, `test_papers`, `health`… Lưu ý: route ở đây làm orchestration **nặng**, không phải thin controller |
| Business logic | [services/](../services/api/src/bookforge_api/services/) | ~70 module — nơi có nhiều việc nhất: `documents.py`, `quota_enforce.py`, `hard_limits.py`, `knowledge_indexing.py`, `ai_actions.py`, `subscriptions.py`, `gotenberg.py`… |
| ORM models | [models/](../services/api/src/bookforge_api/models/) | SQLAlchemy 2.0; [document.py](../services/api/src/bookforge_api/models/document.py) lớn nhất (Document, ChatSession, ChatMessage); ngoài ra `user`, `quota`, `question_bank`, `expert`, `provider_cost` |
| DTO | [schemas/](../services/api/src/bookforge_api/schemas/) | Pydantic request/response, soi gương theo routers |
| Cross-cutting | [core/](../services/api/src/bookforge_api/core/) | Xem ngay bên dưới |
| Nền | [errors/](../services/api/src/bookforge_api/errors/), [storage/](../services/api/src/bookforge_api/storage/) | `ApiException` + `ErrorCode` + handlers chuẩn hóa mọi lỗi; storage = filesystem local có guard |
| Migrations | [alembic/versions/](../services/api/src/bookforge_api/alembic/versions/) | 77 bản, từ `0001_initial` |

**`core/` — đọc kỹ 3 file này trước khi đọc bất kỳ feature nào:**

- [settings.py](../services/api/src/bookforge_api/core/settings.py) — một class `Settings(BaseSettings)` duy nhất, ~230 field, prefix `BOOKFORGE_`, singleton qua `get_settings()`. Chứa cả feature flags (`knowledge_enabled`, `law_enabled`…), routing LLM, và validator chặn boot nếu config sai.
- [db.py](../services/api/src/bookforge_api/core/db.py) — engine/session factory, `session_scope()`; dev mode tự tạo schema + seed org mặc định (nên local không cần Alembic).
- [deps.py](../services/api/src/bookforge_api/core/deps.py) — các FastAPI dependency: `get_db`, `get_current_user` (cookie `bookforge_session`), quota context. Mọi request đi qua đây.

**Các subsystem lớn:**

- [llm/](../services/api/src/bookforge_api/llm/) — tầng AI. Điểm mấu chốt: [model_router.py](../services/api/src/bookforge_api/llm/model_router.py) với `resolve_text_model()` là **seam duy nhất** biến tên operation thành model PydanticAI cụ thể (Gemini/OpenAI-compatible), bọc rate-limit. Tests monkeypatch đúng chỗ này để không gọi LLM thật. Kèm [providers.py](../services/api/src/bookforge_api/llm/providers.py) (OCR ảnh Gemini), `model_registry.py` (model switcher cho user), `mistral_ocr.py`.
- [chat/](../services/api/src/bookforge_api/chat/) — 2 agent: [adk_agent.py](../services/api/src/bookforge_api/chat/adk_agent.py) (chat Q&A trên tài liệu — **tên "ADK" là legacy, bên trong là PydanticAI**) và [editor_agent.py](../services/api/src/bookforge_api/chat/editor_agent.py) (trợ lý canvas, có tool đọc/ghi document, geometry JSXGraph, trả về `change_set` để FE apply 1 transaction). Toolsets đi kèm: `document_reader.py`, `knowledge_retrieval.py`, `legal_tools.py`, `expert_tools.py`; system instructions trong `governance.py`.
- [ingest/](../services/api/src/bookforge_api/ingest/) — [pipeline.py](../services/api/src/bookforge_api/ingest/pipeline.py) (~57KB, file dày đặc nhất repo): extract trang/asset → OCR → vision từng hình → build artifacts cho editor/markdown/tree → index knowledge → ghi event.
- [pptx/](../services/api/src/bookforge_api/pptx/) — sinh slide: `engine_service.py` + `presentation_builder.py`; deck sinh ra được lưu như một `Document` loại `generated_slide`.
- [workers/](../services/api/src/bookforge_api/workers/) — [queue.py](../services/api/src/bookforge_api/workers/queue.py) (`enqueue_ingest`…; flag `queue_inline` cho dev chạy đồng bộ, không cần Redis) và [jobs.py](../services/api/src/bookforge_api/workers/jobs.py) (thân job).
- Clients ra ngoài: [knowledge/client.py](../services/api/src/bookforge_api/knowledge/client.py), [law/client.py](../services/api/src/bookforge_api/law/client.py), [services/gotenberg.py](../services/api/src/bookforge_api/services/gotenberg.py) — tất cả đều httpx.
- Kế toán AI: [services/ai_actions.py](../services/api/src/bookforge_api/services/ai_actions.py) (`record_ai_action`), `token_usage.py`, `token_rates.py`, `provider_cost.py` — mọi lần gọi LLM đều bị ghi sổ và trừ quota.

**Tests**: [tests/](../services/api/tests/) — 259 file phẳng, 1 file / feature, chạy song song (pytest-xdist), async auto. Không có test nào gọi LLM thật.

### 4.2. `services/knowledge-ingestion` + `services/knowledge-retrieval` — RAG, vendored từ RAGFlow

Hai service này **copy từ RAGFlow v0.24.0 rồi cắt gọt**, không phải code tự viết: framework là **Quart** (không phải FastAPI), pattern hoàn toàn khác (blueprints động trong [api/apps/__init__.py](../services/knowledge-ingestion/api/apps/__init__.py), kèm `rag/`, `deepdoc/`, `common/`). Chạy Docker-only, ports 9380/9381, giữ datastore riêng (MySQL + Elasticsearch + MinIO).

Cách đọc đúng: **coi chúng là external HTTP service** — ingestion nhận Markdown để chunk + embed (OpenAI `text-embedding-3-small`), retrieval trả chunks qua `POST /api/v1/retrieval`. Chúng **không có khái niệm user** — `services/api` giữ toàn bộ auth/phân quyền và chỉ truyền sang danh sách document ID được phép. Đừng sửa trực tiếp trừ khi thật cần.

### 4.3. `services/gotenberg` — sidecar render

Chỉ có Dockerfile + compose bọc Gotenberg (LibreOffice) để convert Office/HTML → PDF, dùng cho export và preview slide. Không có gì để đọc ngoài config.

### 4.4. `lawforge-bundle/phapdien-service` — service pháp điển

FastAPI riêng (uv project riêng, port 9382) bọc một agent OpenAI với các tool `law_browse` / `law_search` / `law_lookup` / `law_get` (+ chế độ soạn thảo `law_drafting_guide`, `law_draft_submit`). Search là hybrid: BM25 tách từ tiếng Việt + dense embeddings, fuse bằng RRF; câu trả lời **bắt buộc có trích dẫn**. Corpus = Bộ Pháp điển; index SQLite ~1GB không commit (xem [RUN.md](../lawforge-bundle/RUN.md) để lấy). API chính nối vào qua [law/client.py](../services/api/src/bookforge_api/law/client.py) + [chat/legal_tools.py](../services/api/src/bookforge_api/chat/legal_tools.py), bật bằng `BOOKFORGE_LAW_ENABLED` + `BOOKFORGE_LAW_SERVICE_URL`. CI có chạy test của service này.

## 5. Các service nói chuyện với nhau thế nào

```
FE (repo bookforge-fe)
   │ HTTP + cookie session
   ▼
Caddy ──► bookforge-api :8000 ──┬── RQ / Valkey ──► worker (lane: ingest, index)
                                 │                    │
                                 │            Postgres/SQLite (chung api+worker+cron)
                                 │
                                 ├── httpx ──► knowledge-ingestion :9380 ─┐
                                 ├── httpx ──► knowledge-retrieval :9381 ─┤→ MySQL+ES+MinIO (riêng)
                                 ├── httpx ──► gotenberg :3000
                                 └── httpx ──► phapdien :9382 (chỉ khi legal mode)
```

Nguyên tắc: **không có shared Python package** giữa các service — mỗi cái là một uv project độc lập; hợp đồng chia sẻ duy nhất là HTTP client + env config. Docker network `bookforge-internal` và `bookforge-knowledge-network` nối tất cả lại.

## 6. Trace một request end-to-end (nên tự đi một lần với file mở sẵn)

`POST /api/chat/sessions/{id}/messages` — gửi một tin nhắn chat:

1. Route `create_chat_message()` trong [api/chat.py](../services/api/src/bookforge_api/api/chat.py).
2. Auth: `get_current_user` trong [core/deps.py](../services/api/src/bookforge_api/core/deps.py) — cookie → session record → `User`.
3. Chặn quota: [services/quota_enforce.py](../services/api/src/bookforge_api/services/quota_enforce.py) (`require_ai_action`) + [services/hard_limits.py](../services/api/src/bookforge_api/services/hard_limits.py).
4. Chọn phạm vi: `_documents_for_session()` lọc các document đã `ai_ready`.
5. Agent: `run_adk_chat` trong [chat/adk_agent.py](../services/api/src/bookforge_api/chat/adk_agent.py) dựng PydanticAI `Agent` + toolsets.
6. Tool retrieval: [chat/knowledge_retrieval.py](../services/api/src/bookforge_api/chat/knowledge_retrieval.py) → `KnowledgeClient.retrieve()` trong [knowledge/client.py](../services/api/src/bookforge_api/knowledge/client.py) → HTTP sang knowledge-retrieval.
7. Gọi LLM: model từ [llm/model_router.py](../services/api/src/bookforge_api/llm/model_router.py), throttle bởi [core/gemini_limiter.py](../services/api/src/bookforge_api/core/gemini_limiter.py).
8. Ghi sổ: `record_ai_action` + token usage → trừ quota, đóng dấu header quota vào response.
9. Lưu `ChatMessage` ([models/document.py](../services/api/src/bookforge_api/models/document.py)) → trả response theo [schemas/chat.py](../services/api/src/bookforge_api/schemas/chat.py).

Ví dụ thứ hai đáng tự trace: **upload → ingest** — [api/documents.py](../services/api/src/bookforge_api/api/documents.py) → `enqueue_ingest` → `ingest_document_job` trong [workers/jobs.py](../services/api/src/bookforge_api/workers/jobs.py) → [ingest/pipeline.py](../services/api/src/bookforge_api/ingest/pipeline.py) → [services/knowledge_indexing.py](../services/api/src/bookforge_api/services/knowledge_indexing.py).

## 7. Lộ trình đọc đề xuất

**Giai đoạn 1 — docs (nửa ngày):** [README.md](../README.md) → [LOCAL_QUICKSTART.md](../LOCAL_QUICKSTART.md) → [ONBOARDING.md](../ONBOARDING.md) → [BACKEND_LOCAL_SETUP.md](../BACKEND_LOCAL_SETUP.md) → [REPO_STATUS.md](REPO_STATUS.md) → **[architecture/01-system-overview.md](architecture/01-system-overview.md)** (doc kiến trúc tốt nhất, có dẫn chứng tới từng file) → [architecture/03-dependency-and-data-flow.md](architecture/03-dependency-and-data-flow.md) → [backend/alignment.md](backend/alignment.md) (source of truth về hướng đi) → [backend/data-model.md](backend/data-model.md).

**Giai đoạn 2 — xương sống code:** [services/README.md](../services/README.md) → [pyproject.toml](../services/api/pyproject.toml) + [Dockerfile](../services/api/Dockerfile) → [main.py](../services/api/src/bookforge_api/main.py) → `core/settings.py` → `core/db.py` → `core/deps.py`.

**Giai đoạn 3 — một lát cắt dọc:** chọn 1 feature (documents hoặc chat) và đọc trọn router → service → model → schema.

**Giai đoạn 4 — async + AI:** `workers/queue.py` + `workers/jobs.py` + `ingest/pipeline.py`, rồi `llm/model_router.py` + `chat/adk_agent.py`, rồi tự đi trace ở mục 6.

**Giai đoạn 5 — biên giới ngoài:** `knowledge/client.py`, `law/client.py`, `services/gotenberg.py`; liếc qua pattern RAGFlow ở knowledge-ingestion để biết vì sao không nên sửa nó. Nếu làm editor agent: đọc thêm [CANVAS_AGENT_ONBOARDING.md](../CANVAS_AGENT_ONBOARDING.md).

## 8. Chạy local để vừa đọc vừa thử

Đường nhanh nhất (không Docker, SQLite, queue inline, RAG tắt) — chạy từ root của `backend/`:

```bash
cd services/api
cp .env.example .env
uv sync
uv run bookforge-api          # → http://localhost:8000/docs
```

Tạo user đầu tiên (terminal khác, trong `services/api`):

```bash
uv run python scripts/create_user.py --email owner@example.com --password "Supersafe123!" --full-name "Book Owner" --role admin
```

Kiểm tra: `curl localhost:8000/health` và `/health/ready`. Dev mode tự tạo schema + seed org, không cần Alembic; muốn dùng tính năng AI thì cần thêm Gemini key (server vẫn boot được khi thiếu). Test/lint: `uv run pytest`, `uv run ruff check`. Full stack prod-like (Path B, 3 lớp compose theo thứ tự) xem [BACKEND_LOCAL_SETUP.md](../BACKEND_LOCAL_SETUP.md) §4.

Hai gotcha khi boot: API **fail sớm có chủ đích** nếu model LLM cấu hình không có rate-card trong catalog, và nếu budget kết nối Postgres `(uvicorn_workers + worker_count) × (pool_size + max_overflow)` vượt `max_connections - 3`.

## 9. Những điểm dễ nhầm — biết trước đỡ mất thời gian

- **`chat/adk_agent.py` không dùng Google ADK** — tên là di sản, implementation hiện tại là PydanticAI.
- **Branch model**: `dev` = integration (cắt feature branch từ đây), `main` = production (CI tự deploy, đừng push thẳng), `feat/legal-mode` = mảng luật.
- `services/api/services/api/storage/workspaces/` (đường dẫn lồng kỳ lạ) là **output runtime lúc dev**, không phải source.
- Root [pyproject.toml](../pyproject.toml) khai báo workspace member `phapdien` trông lệch với layout `services/` — docs cũng ghi nhận nó hơi stale; đừng để nó dẫn bạn đi lạc.
- [ERRORS.md](ERRORS.md) là file **generated** từ `errors/catalog.py` (qua [scripts/render_errors_doc.py](../scripts/render_errors_doc.py), có CI test giữ sync) — sửa catalog, đừng sửa tay file này.
- `handoff/` là docs bàn giao cho FE, đọc backend thì bỏ qua.
