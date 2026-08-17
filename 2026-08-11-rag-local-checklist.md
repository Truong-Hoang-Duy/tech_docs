# Checklist: bật RAG (chat with documents) ở local — chạy tuần tự

Status: checklist vận hành, viết 2026-08-11 sau khi chạy thành công Path B theo
[BACKEND_LOCAL_SETUP.md §4](../backend/BACKEND_LOCAL_SETUP.md). Dùng
`infra/dev/compose.yml` (KHÔNG dùng cách tái tạo `infra/shared/compose.yml` cũ
từ git history nữa — xem [local-dev-knowledge-stack.md](local-dev-knowledge-stack.md),
doc đó đã lỗi thời từ khi `infra/dev/` được thêm vào để tự tạo 2 network
`bookforge-internal` + `bookforge-knowledge-network`).

Tất cả lệnh chạy từ `backend/` (repo root theo nghĩa của guide).

## 0. Điều kiện tiên quyết

- Docker Desktop đang chạy (`docker info` không lỗi).
- Có **OpenAI embeddings key** thật (`text-embedding-3-small`) — khác với key
  LLM chat. Verify trước khi làm gì khác, kết quả đúng phải in `1536`:
  ```powershell
  curl -s https://api.openai.com/v1/embeddings -H "Authorization: Bearer YOUR_KEY" -H "Content-Type: application/json" -d '{"model":"text-embedding-3-small","input":"probe"}' | python -c "import json,sys;print(len(json.load(sys.stdin)['data'][0]['embedding']))"
  ```

## 1. Cấu hình `infra/dev/.env`

```powershell
Copy-Item infra\dev\.env.example infra\dev\.env
```

Điền **giống hệt nhau** vào cả hai biến:
```env
BOOKFORGE_KNOWLEDGE_EMBEDDING_API_KEY=<key>
OPENAI_API_KEY=<key>
```

> **Gotcha đã gặp thật:** nếu bộ gõ tiếng Việt (Unikey/Vietkey…) đang bật khi
> dán/gõ key, nó có thể **âm thầm chèn 1 ký tự dấu** (vd. `ị`) vào giữa
> chuỗi key. Key vẫn "trông" đúng độ dài nhưng bootstrap lưu key hỏng vào
> MySQL, và lúc index sẽ fail với
> `UnicodeEncodeError: 'ascii' codec can't encode character 'ịxxx'`
> trong log `knowledge-ingestion-executor` — rất khó đoán ra nguyên nhân nếu
> không biết trước. **Tắt bộ gõ tiếng Việt trước khi điền key.**

## 2. Layer 1 — datastores

```powershell
docker compose --env-file infra/dev/.env -f infra/dev/compose.yml up -d
docker compose --env-file infra/dev/.env -f infra/dev/compose.yml ps
```
Kỳ vọng: `bookforge-minio`, `bookforge-knowledge-mysql`,
`bookforge-knowledge-elasticsearch`, `bookforge-valkey` đều `healthy`;
`bookforge-minio-init` là job một lần, xem bằng `ps -a` → phải `Exited (0)`.

## 3. Layer 2 — knowledge services

```powershell
docker compose --env-file infra/dev/.env -f services/knowledge-ingestion/compose.yml up -d --build
docker compose --env-file infra/dev/.env -f services/knowledge-ingestion/compose.yml run --rm knowledge-ingestion-bootstrap
docker compose --env-file infra/dev/.env -f services/knowledge-retrieval/compose.yml up -d --build
curl http://127.0.0.1:9380/v1/system/healthz
curl http://127.0.0.1:9381/v1/system/healthz
```
Cả hai phải trả `{"status":"ok"}`. Nếu bootstrap báo
`OPENAI_API_KEY is required` → chưa điền đúng bước 1.

Nếu sau này phải sửa lại key (kể cả do gotcha ở bước 1), key cũ đã bị lưu
vào MySQL rồi — phải recreate + bootstrap lại, sửa `.env` không đủ:
```powershell
docker compose --env-file infra/dev/.env -f services/knowledge-ingestion/compose.yml up -d --force-recreate
docker compose --env-file infra/dev/.env -f services/knowledge-ingestion/compose.yml run --rm knowledge-ingestion-bootstrap
```

## 4. Layer 3 — nối API host vào RAG

Thêm vào `services/api/.env` (token phải khớp `BOOKFORGE_KNOWLEDGE_API_TOKEN`
trong `infra/dev/.env`):
```env
BOOKFORGE_KNOWLEDGE_ENABLED=true
BOOKFORGE_KNOWLEDGE_INGESTION_URL=http://127.0.0.1:9380
BOOKFORGE_KNOWLEDGE_RETRIEVAL_URL=http://127.0.0.1:9381
BOOKFORGE_KNOWLEDGE_API_TOKEN=bookforge-dev-knowledge-token
```
Restart `uv run bookforge-api`.

## 5. Test

- Upload `.pdf` / `.docx` / `.pptx` / ảnh (`.md`/`.txt` bị từ chối:
  `file_unsupported_type`).
- Đừng tin `ai_ready: true` — check chunk thật:
  ```powershell
  uv run --directory services/api python -c "import sqlite3;print(sqlite3.connect(r'storage/bookforge.db').execute('select status,chunk_count,embedding_token_count from knowledge_documents order by rowid desc limit 1').fetchall())"
  ```
  Kỳ vọng `status='ready'`, `chunk_count > 0`.
- Tín hiệu thật: câu trả lời chat có **citation**. Không có citation =
  retrieval rỗng, model tự bịa bằng kiến thức nền.

## 6. Debug khi `status='processing'` mãi không xong

```powershell
docker logs bookforge-knowledge-ingestion-knowledge-ingestion-executor-1 --tail 80
docker logs bookforge-knowledge-ingestion-broker --tail 40
```
`UnicodeEncodeError` trong executor log → quay lại gotcha ở bước 1.

## 7. Tắt stack

```powershell
docker compose --env-file infra/dev/.env -f services/knowledge-retrieval/compose.yml down
docker compose --env-file infra/dev/.env -f services/knowledge-ingestion/compose.yml down
docker compose --env-file infra/dev/.env -f infra/dev/compose.yml down
```
Thêm `-v` vào lệnh cuối nếu muốn xoá luôn data volume.
