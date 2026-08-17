# Chạy được RAG (ingest → chat theo tài liệu) trên local

> **Lỗi thời (2026-08-11):** cách dựng lại `infra/shared/compose.yml` từ git
> history ở dưới không còn cần thiết — repo đã có sẵn `infra/dev/compose.yml`
> tự tạo network + datastore đúng chuẩn. Dùng
> [2026-08-11-rag-local-checklist.md](2026-08-11-rag-local-checklist.md) thay
> thế. Phần phân tích nguyên nhân (mục "Vì sao xảy ra"/"Vì sao staging chạy
> được") vẫn còn giá trị tham khảo.

Status: hướng dẫn vận hành, viết 2026-08-08 sau khi tái hiện lỗi "tải tài liệu lên
được, nhưng tài liệu không hiện trong bộ chọn Thư mục ở Trò chuyện cùng AI" trên
máy dev (Docker Desktop không chạy, `services/api/.env` trỏ SQLite + loopback).

## Triệu chứng

1. Vào **Tài liệu** → **Tải lên tài liệu** → chọn PDF → tài liệu hiện ra trong
   danh sách, có tên/loại file/dung lượng.
2. Vào **Trò chuyện cùng AI** → panel **Công cụ** → tab **Thư mục** → danh sách
   trống, không thấy tài liệu vừa tải lên để chọn.
3. Trên staging, cùng thao tác đó hoạt động bình thường.

## Vì sao xảy ra: upload thành công không có nghĩa là đã "index" xong

Tài liệu bạn thấy ở trang **Tài liệu** và tài liệu hiện trong bộ chọn **Thư mục**
đến từ cùng một API danh sách, nhưng bộ chọn Thư mục lọc thêm điều kiện
`ai_ready !== false` ở phía frontend:

- [frontend/src/templates/DocumentDetailPage/partial/document-tools-folders.tsx:346](../../../frontend/src/templates/DocumentDetailPage/partial/document-tools-folders.tsx)
  ```ts
  documents.filter((document) => isDocumentReady(document) && document.ai_ready !== false)
  ```

`ai_ready` chỉ bật thành `true` sau khi tài liệu được đánh chỉ mục (embed +
lưu chunk) thành công trong dịch vụ tri thức dạng RAGFlow
(`knowledge-ingestion` + `knowledge-retrieval`). Luồng upload gọi bước index
này **đồng bộ, ngay trong request upload**, không phải qua hàng đợi nền
tùy theo `BOOKFORGE_QUEUE_INLINE`:

- `create_document_and_ingest_sync` → `ingest_document_workspace` →
  `index_document_for_knowledge(...)` —
  [services/api/src/bookforge_api/services/document_runtime.py:238-277](../../../services/api/src/bookforge_api/services/document_runtime.py)
  và [services/api/src/bookforge_api/ingest/pipeline.py:1016](../../../services/api/src/bookforge_api/ingest/pipeline.py)
- Bước index gọi `KnowledgeClient` tới `BOOKFORGE_KNOWLEDGE_INGESTION_URL`
  ([services/api/src/bookforge_api/knowledge/client.py:260-269](../../../services/api/src/bookforge_api/knowledge/client.py)).
  Nếu không có gì lắng nghe ở địa chỉ đó (`httpx.RequestError`), lỗi được bắt
  và nuốt lại trong `index_document_for_knowledge`, gọi `_mark_failed(...)`
  → `document.rag_status = 'failed'`, `document.ai_ready = False`
  ([services/api/src/bookforge_api/services/knowledge_indexing.py:239-250](../../../services/api/src/bookforge_api/services/knowledge_indexing.py)).
- Vì exception bị nuốt ở tầng index, request upload vẫn trả về **thành công**
  — tài liệu vẫn `status=ready` và hiện bình thường ở trang Tài liệu, chỉ có
  `ai_ready=false` nên biến mất khỏi bộ chọn Thư mục của chat.

`BOOKFORGE_QUEUE_INLINE` / `BOOKFORGE_KNOWLEDGE_REINDEX_DEBOUNCE_SECONDS`
(trong `infra/profiles/dev.env`) chỉ ảnh hưởng tới **reindex khi sửa tài
liệu sau này**, không phải bước index đầu tiên lúc upload — nên đừng mất
công chỉnh hai biến này để fix vấn đề trên.

## Vì sao staging chạy được mà local thì không

Staging không phải "code khác" — staging chỉ đơn giản là có **đầy đủ hạ
tầng RAG đang chạy thật** và local checkout thì không:

- Staging/prod chạy 5 compose project cùng lúc (`shared`, `api`, `gotenberg`,
  `knowledge-ingestion`, `knowledge-retrieval`) với Postgres/Valkey/MinIO/
  MySQL/Elasticsearch thật và `OPENAI_API_KEY` thật để tạo embedding —
  xem [docs/ops/staging-environment.md:19-49](staging-environment.md).
- Trên máy dev hiện tại, `services/api` chạy bare-metal bằng
  `uv run bookforge-api` (theo README), với `services/api/.env` trỏ
  `BOOKFORGE_DATABASE_URL=sqlite:///./storage/bookforge.db` và
  `BOOKFORGE_KNOWLEDGE_INGESTION_URL=http://127.0.0.1:9380` /
  `BOOKFORGE_KNOWLEDGE_RETRIEVAL_URL=http://127.0.0.1:9381` — nhưng **không
  có gì chạy ở hai cổng đó**, và Docker Desktop hiện đang tắt trên máy này.
  Không có MySQL/Elasticsearch/MinIO nào backing dịch vụ tri thức cả.

### Một điểm gây rối thêm: tài liệu README bị lệch so với repo hiện tại

`services/api/README.md:64-70` ghi "Start order: 1. Shared infra:
`infra/shared`" — ngụ ý `infra/shared` sẽ dựng luôn Postgres/Valkey/MinIO/
MySQL/Elasticsearch. Điều đó **từng đúng**, nhưng commit `dc03046`
("infra(shared): retire lawforge stack…", 2026-06-19) đã dọn các datastore
đó ra khỏi `infra/shared/compose.yml` vì chúng thuộc về stack "lawforge" đã
nghỉ hưu — file hiện tại **chỉ còn Caddy proxy dùng chung**, không có
datastore nào nữa:

```
# infra/shared/compose.yml (hiện tại)
# NOTE (2026-06-19): the lawforge app stack and its datastores (postgres/valkey/
# minio/knowledge-mysql/knowledge-elasticsearch) were retired...
```

Trên VPS, mỗi stack (prod/staging) giữ **bản compose.yml riêng, không commit
vào git** (`docs/ops/staging-environment.md:111`: "the tracked tree (minus
compose.yml/.env, which are VPS-local)"). Nói cách khác: **repo bạn đang có
trên local không chứa file compose để dựng Postgres/Valkey/MinIO/MySQL/
Elasticsearch cho BookForge nữa** — bản cũ có các service đó đã bị gỡ khỏi
`infra/shared/compose.yml`. Đây là lý do "làm theo README vẫn không chạy
được" chứ không phải do bạn làm sai bước nào.

## Cách chạy được ở local

### Điều kiện tiên quyết

- Docker Desktop phải đang chạy (`docker ps` phải trả về danh sách, không
  lỗi pipe). Trên máy này Docker Desktop hiện chưa mở — mở nó trước.
- Cần một OpenAI API key thật để tạo embedding
  (`BOOKFORGE_KNOWLEDGE_EMBEDDING_MODEL=text-embedding-3-small`). Không có
  key này thì bước index vẫn fail y như hiện tại, chỉ khác là lỗi sẽ đổi từ
  "connection refused" sang "401 unauthorized" từ OpenAI.

### Bước 1 — Tự dựng lại tầng datastore (Postgres/Valkey/MinIO/MySQL/ES)

File `infra/shared/compose.yml` hiện tại không còn các service này. Cách
nhanh nhất là lấy lại đúng định nghĩa cũ từ lịch sử git (commit trước khi bị
gỡ), lưu thành file riêng để không đụng vào `infra/shared/compose.yml` đang
dùng cho Caddy:

```powershell
cd d:\Project\bookforge\backend
git show dc03046~1:infra/shared/compose.yml > infra/shared/compose.datastores.yml
```

File này định nghĩa `bookforge-postgres`, `bookforge-valkey`,
`bookforge-minio` (+ `bookforge-minio-init` tạo sẵn 2 bucket), `bookforge-
knowledge-mysql`, `bookforge-knowledge-elasticsearch`, và **tạo luôn 2
network** `bookforge-internal` + `bookforge-knowledge` (alias mạng
`bookforge-knowledge-network`) mà `services/api/compose.yml` và
`services/knowledge-ingestion/compose.yml` đang khai báo là `external: true`
— tức là các compose file kia **cần** hai network này đã tồn tại sẵn.

Sửa file vừa tạo: bỏ phần `bookforge-proxy` (không cần Caddy ở local, chỉ
cần datastore) — hoặc để nguyên cũng được nếu bạn không set các biến bắt
buộc của Caddy (`BOOKFORGE_API_DOCS_BASIC_AUTH_HASH`, `CF_API_TOKEN`) thì nó
sẽ lỗi khi lên; đơn giản nhất là dùng `--profile` hoặc chỉ định thẳng tên
service khi `up` để bỏ qua proxy:

```powershell
cp infra/shared/.env.example infra/shared/.env
# Mở infra/shared/.env, điền các mật khẩu REQUIRED (Postgres/Valkey/MinIO/
# MySQL/Elasticsearch) và OPENAI_API_KEY thật.

docker compose --env-file infra/shared/.env -f infra/shared/compose.datastores.yml `
  up -d bookforge-postgres bookforge-valkey bookforge-minio bookforge-minio-init `
  bookforge-knowledge-mysql bookforge-knowledge-elasticsearch
```

### Bước 2 — Dựng dịch vụ tri thức (knowledge-ingestion + knowledge-retrieval)

```powershell
docker compose --env-file infra/shared/.env -f services/knowledge-ingestion/compose.yml up -d --build
docker compose --env-file infra/shared/.env -f services/knowledge-ingestion/compose.yml run --rm knowledge-ingestion-bootstrap
docker compose --env-file infra/shared/.env -f services/knowledge-retrieval/compose.yml up -d --build
```

Lệnh `run --rm knowledge-ingestion-bootstrap` tạo tenant/API token/dataset
nội bộ, mặc định dùng `BOOKFORGE_KNOWLEDGE_API_TOKEN` (đặt trong `.env`,
mặc định gợi ý `bookforge-dev-knowledge-token` theo
[services/knowledge-ingestion/README.md:25](../../services/knowledge-ingestion/README.md)).
Idempotent, chạy lại vô hại.

Kiểm tra:
```powershell
curl http://127.0.0.1:9380/v1/system/healthz
curl http://127.0.0.1:9381/v1/system/healthz
```

### Bước 3 — Trỏ `services/api` vào đúng hạ tầng vừa dựng

Nếu tiếp tục chạy API bare-metal (`uv run bookforge-api`), giữ nguyên
`services/api/.env` trỏ về `127.0.0.1` (các port đã map ra host ở bước 1-2
đúng như file `.env.example` gốc), chỉ cần điền:

```env
BOOKFORGE_KNOWLEDGE_API_TOKEN=<token đã bootstrap ở bước 2>
```

Nếu muốn full parity với staging (Postgres thật thay vì SQLite), đổi thêm:
```env
BOOKFORGE_DATABASE_URL=postgresql+psycopg://bookforge:<mật khẩu>@127.0.0.1:15432/bookforge
BOOKFORGE_REDIS_URL=redis://:<mật khẩu valkey>@127.0.0.1:6379/0
```
(không bắt buộc để fix riêng lỗi RAG — SQLite vẫn dùng được cho phần app
chính, chỉ knowledge stack mới liên quan tới lỗi này).

Khởi động lại API, rồi tải lại file PDF (hoặc trigger reprocess nếu có nút
đó trong UI). `index_document_for_knowledge` giờ gọi thành công tới
`knowledge-ingestion-api` thật → `ai_ready` chuyển `true` sau khi
`list_chunks` trả `total>0`
([knowledge_indexing.py:260-263](../../../services/api/src/bookforge_api/services/knowledge_indexing.py)) → tài liệu sẽ xuất hiện trong bộ chọn Thư mục của
chat.

### Lưu ý / gotcha

- `BOOKFORGE_KNOWLEDGE_EXECUTOR_COUNT` mặc định = 1
  ([infra/profiles/dev.env:12](../../infra/profiles/dev.env)) — theo
  [infra/profiles/README.md](../../infra/profiles/README.md), `task_executor.py`
  của RAGFlow đặt tên consumer theo `argv[1]` không phân biệt replica, nên
  không tăng số này lên khi chưa sửa code; ingest tuần tự là bình thường ở
  dev, không phải bug.
- Đừng nhầm `BOOKFORGE_QUEUE_INLINE`/debounce reindex với bước index-lúc-
  upload — hai cái không liên quan tới triệu chứng ở trên.
- MinIO console (http://127.0.0.1:9001) và Elasticsearch
  (http://127.0.0.1:19200, user `elastic`) hữu ích để xác nhận chunk/index
  thật sự đã được ghi, nếu vẫn nghi ngờ sau khi `ai_ready=true`.
