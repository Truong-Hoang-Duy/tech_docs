# Setup RAG (Knowledge Chat) trên macOS

Nguồn đầy đủ: `backend/BACKEND_LOCAL_SETUP.md` (mục 4). File này chỉ tóm tắt phần cần cho macOS.

## Điều kiện trước

- Docker Desktop đang chạy, cấp ~8GB RAM (Docker Desktop → Settings → Resources)
- Có **OpenAI API key loại embeddings** (`text-embedding-3-small`) — không dùng chung key chat/LLM (`gpt-*`), sẽ fail muộn với lỗi `Fail to bind embedding model`
- Test key trước khi setup (key đúng in ra `1536`):
  ```bash
  curl -s https://api.openai.com/v1/embeddings \
    -H "Authorization: Bearer $OPENAI_API_KEY" -H 'Content-Type: application/json' \
    -d '{"model":"text-embedding-3-small","input":"probe"}' | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["data"][0]["embedding"]))'
  ```

## Bước 1 — Layer 1: RAG datastores (MySQL, Elasticsearch, MinIO, Valkey)

```bash
cp infra/dev/.env.example infra/dev/.env
```
- Sửa `infra/dev/.env`, set `OPENAI_API_KEY=<key embeddings của bạn>` (các giá trị khác giữ mặc định)
```bash
docker compose --env-file infra/dev/.env -f infra/dev/compose.yml up -d
docker compose --env-file infra/dev/.env -f infra/dev/compose.yml ps
```
- Chờ tới khi `bookforge-minio`, `bookforge-knowledge-mysql`, `bookforge-knowledge-elasticsearch` đều `healthy` (Elasticsearch có thể mất ~60s)
- Nếu port 9000/9001 (MinIO) bị chiếm, đổi `*_HOST_PORT` trong `infra/dev/.env`

## Bước 2 — Layer 2: 2 service RAG (ingestion + retrieval)

```bash
docker compose --env-file infra/dev/.env -f services/knowledge-ingestion/compose.yml up -d --build
```
- Build lần đầu nặng (~11GB image + tải NLTK corpus), cần internet, chỉ tốn 1 lần

Bootstrap (tạo tenant, API token, dataset — idempotent, an toàn chạy lại):
```bash
docker compose --env-file infra/dev/.env -f services/knowledge-ingestion/compose.yml run --rm knowledge-ingestion-bootstrap
```
- Lỗi `OPENAI_API_KEY is required` → quên sửa `infra/dev/.env` ở Bước 1

Khởi động retrieval:
```bash
docker compose --env-file infra/dev/.env -f services/knowledge-retrieval/compose.yml up -d --build
```

Kiểm tra:
```bash
curl http://127.0.0.1:9380/v1/system/healthz
curl http://127.0.0.1:9381/v1/system/healthz
```

## Bước 3 — Layer 3: bật cờ trong API (vẫn chạy `uv`, không cần Docker cho API)

Thêm vào `backend/services/api/.env`:
```env
BOOKFORGE_KNOWLEDGE_ENABLED=true
BOOKFORGE_KNOWLEDGE_INGESTION_URL=http://127.0.0.1:9380
BOOKFORGE_KNOWLEDGE_RETRIEVAL_URL=http://127.0.0.1:9381
BOOKFORGE_KNOWLEDGE_API_TOKEN=bookforge-dev-knowledge-token
```
- Restart `uv run bookforge-api`

## Test thử

- Chỉ upload được `.pdf`, `.docx`, `.pptx`, hoặc ảnh — `.md`/`.txt` bị từ chối (`file_unsupported_type`)
- `ai_ready: true` chưa chắc đã index xong, kiểm tra thật bằng:
  ```bash
  uv run --directory services/api python -c "import sqlite3;print(sqlite3.connect(r'storage/bookforge.db').execute('select status,chunk_count,embedding_token_count from knowledge_documents order by rowid desc limit 1').fetchall())"
  ```
  cần `status='ready'` và `chunk_count > 0`
- Câu trả lời có **citation** = retrieval thật sự hoạt động; không có citation = model tự trả lời, không dùng RAG

## Lưu ý / gotcha

- RAM khi idle: ~4.5–5GB cho cả stack RAG
- Nếu container knowledge crash-loop: kiểm tra nó có join đúng network `bookforge-knowledge-network` không (cần để resolve `bookforge-knowledge-mysql`, `bookforge-knowledge-elasticsearch`, `bookforge-minio`, `bookforge-valkey`)
- `401 Unauthorized` từ retrieval thường KHÔNG phải lỗi auth — xem traceback thật bằng `docker logs bookforge-knowledge-retrieval-api`
- Đừng set `DEVICE=gpu` — sẽ cài CUDA torch nhiều GB mỗi lần container khởi động lại

## Tắt RAG stack (khi không cần nữa)

```bash
docker compose --env-file infra/dev/.env -f services/knowledge-retrieval/compose.yml down
docker compose --env-file infra/dev/.env -f services/knowledge-ingestion/compose.yml down
docker compose --env-file infra/dev/.env -f infra/dev/compose.yml down
```
Thêm `-v` vào lệnh cuối để xóa luôn data volumes.
