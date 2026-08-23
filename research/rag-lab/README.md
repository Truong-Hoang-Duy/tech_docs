# RAG Lab — Hướng dẫn RAG cho bookforge (miễn phí)

Tài liệu này giải thích RAG (Retrieval-Augmented Generation) bám theo đúng kiến trúc
đang có trong repo này (`backend/services/knowledge-ingestion` +
`backend/services/knowledge-retrieval`), sau đó có một bài tập thực hành chạy
**hoàn toàn miễn phí, offline, không cần API key** ở [`exercise.py`](exercise.py).

## 1. RAG là gì, và tại sao cần

RAG = cho LLM "mở sách" trước khi trả lời, thay vì bắt nó trả lời chỉ bằng kiến thức
đã học lúc train. Quy trình chuẩn có 2 pha:

**Pha Ingestion (nạp dữ liệu — chạy 1 lần, offline):**

```
tài liệu gốc (PDF/DOCX/MD) → parse → chunk (cắt nhỏ) → embed (vector hoá) → lưu vào vector store/doc store
```

**Pha Retrieval + Generation (chạy mỗi khi có câu hỏi — online):**

```
câu hỏi user → embed câu hỏi → tìm các chunk gần nhất trong store → nhét chunk vào prompt → LLM sinh câu trả lời
```

## 2. Map các khái niệm vào kiến trúc thật của bookforge

Repo này không phải RAG "toy" — nó đã tách RAG thành 2 microservice riêng, giống
kiến trúc RAGFlow:

| Khái niệm RAG | Ở đâu trong bookforge |
|---|---|
| **Parsing** (đọc PDF/DOCX/ảnh scan ra text có cấu trúc) | `backend/services/knowledge-ingestion/deepdoc/parser/*` — có parser riêng cho pdf, docx, ppt, excel, thậm chí OCR (`vision/ocr.py`, `paddleocr_parser.py`) |
| **Chunking** (cắt tài liệu thành đoạn nhỏ để embed) | nằm trong pipeline ingestion, điều phối bởi `rag/svr/task_executor.py` |
| **Embedding** (vector hoá text) | `rag/llm/embedding_model.py`. README của services nói rõ: mặc định dùng **OpenAI `text-embedding-3-small`** (dịch vụ trả phí, cần `OPENAI_API_KEY`) |
| **Vector store / doc store** | `knowledge-retrieval/common/doc_store/*` — hỗ trợ nhiều backend: Elasticsearch (`es_conn.py`), Infinity (`infinity_conn.py`), OceanBase (`ob_conn.py`) |
| **Retrieval** (tìm đoạn liên quan) | `knowledge-retrieval/rag/nlp/search.py` + `rag/nlp/query.py` — endpoint duy nhất expose ra ngoài là `POST /api/v1/retrieval` |
| **Hybrid search** (kết hợp tìm theo *nghĩa* + tìm theo *từ khoá*) | Đây là điểm quan trọng nhất cần hiểu — xem mục 3 |
| **Rerank** (chấm điểm lại top-k để sắp xếp chính xác hơn) | `rag/llm/rerank_model.py` |
| **Generation** (LLM sinh câu trả lời cuối) | Nằm ở service `api` (`bookforge_api`) — orchestrate chat, gọi sang `knowledge-retrieval` lấy context rồi mới gọi LLM |
| **Prompt construction** (ghép context + câu hỏi thành prompt) | `knowledge-retrieval/rag/prompts/generator.py` |

Điều đáng chú ý: **ingestion và retrieval là 2 service tách biệt, giao tiếp qua doc store**
(Elasticsearch/Infinity), không gọi hàm trực tiếp với nhau. Đây là thiết kế production
thật — cho phép scale ingestion và retrieval độc lập.

## 3. Hybrid search — khái niệm hay bị hiểu sai

Một hệ RAG "xịn" không chỉ tìm bằng vector (dense/semantic search). Nó kết hợp 2 loại:

- **Dense retrieval (semantic)**: câu hỏi và chunk được embed thành vector, so bằng
  cosine similarity. Ưu điểm: hiểu được đồng nghĩa, diễn đạt khác nhau. Nhược điểm:
  yếu với từ khoá hiếm/số liệu/tên riêng chính xác.
- **Sparse retrieval (keyword, kiểu BM25/TF-IDF)**: so khớp từ khoá thống kê tần suất.
  Ưu điểm: chính xác tuyệt đối với từ khoá/số liệu. Nhược điểm: không hiểu ngữ nghĩa.

`rag/nlp/search.py` trong `knowledge-retrieval` kết hợp cả hai rồi cộng điểm (weighted
fusion), sau đó `rerank_model.py` chấm điểm lại top-k bằng một model rerank chuyên dụng
(chính xác hơn nhưng chậm hơn nên chỉ áp dụng cho top-k, không áp dụng cho toàn bộ corpus).

Bài tập bên dưới sẽ cho bạn tự code phần **sparse retrieval (TF-IDF)** từ đầu bằng
Python thuần — đây chính là một nửa thuật toán hybrid search thật đang chạy trong repo.

## 4. Vì sao bài tập không dùng OpenAI/embedding thật

Project thật dùng `text-embedding-3-small` của OpenAI — **tốn phí**, cần API key.
Để bạn thực hành **miễn phí và chạy ngay không cần cài gì**, bài tập dùng TF-IDF tự
code bằng `stdlib` (module `math`, `collections`) — không cần internet, không cần
API key, không cần cài `pip install` gì cả.

TF-IDF không phải "giả", nó là baseline sparse retrieval thật sự — nhiều hệ RAG production
(kể cả bookforge) vẫn dùng loại retrieval này song song với dense embedding.

Nếu sau này muốn nâng cấp lên dense embedding thật mà vẫn miễn phí, có 2 lựa chọn không tốn
tiền (không cần làm ngay, chỉ để biết):

- **`sentence-transformers`** (thư viện mã nguồn mở, chạy embedding model local trên máy,
  không gọi API, không tốn phí — chỉ tốn dung lượng tải model lần đầu).
- **Ollama** chạy local LLM/embedding model miễn phí trên máy để thay thế bước generation.

## 5. Bài tập

Mở [`exercise.py`](exercise.py). File có các hàm để trống (`TODO`) bạn tự implement:

1. `tokenize` — tách câu thành từ (đã gợi ý sẵn cách xử lý tiếng Việt có dấu)
2. `build_tf_idf` — tính TF-IDF vector cho mỗi chunk trong corpus
3. `cosine_similarity` — đo độ giống nhau giữa 2 vector
4. `retrieve` — ghép tokenize + tf-idf + cosine để trả về top-k chunk liên quan nhất
5. `build_prompt` — ghép context lấy được + câu hỏi thành prompt hoàn chỉnh (đúng việc
   mà `rag/prompts/generator.py` làm trong service thật)

Corpus dùng để test chính là 3 file markdown trong `docs/` của project này
(`READING_GUIDE.md`, `features-cursor.md`, `BAO_CAO_SO_SANH_VIET_LAI.md`) — tự chunk theo
đoạn (paragraph). Chạy thử:

```bash
python3 docs/rag-lab/exercise.py "kiến trúc backend gồm những service nào?"
```

Nếu làm đúng, script sẽ in ra top-3 đoạn liên quan nhất trong docs + prompt hoàn chỉnh
sẵn sàng để dán vào bất kỳ LLM nào (kể cả bản miễn phí trên web) để lấy câu trả lời cuối.

File [`solution.py`](solution.py) có lời giải đầy đủ — cố làm trước rồi mới xem để so sánh.

## 6. Câu hỏi tự kiểm tra sau khi làm xong bài tập

- Nếu 2 chunk có cùng nội dung nhưng 1 chunk dài gấp đôi, TF-IDF cosine similarity có bị
  lệch không? Tại sao (gợi ý: cosine đã tự chuẩn hoá theo độ dài vector)?
- Vì sao dense embedding (semantic) tìm được "chi phí" khi hỏi "giá tiền" nhưng TF-IDF
  của bạn thì không? Thử sửa câu hỏi để thấy rõ giới hạn của sparse retrieval.
- Muốn thêm rerank (như `rerank_model.py` thật) vào bài tập này, bạn sẽ chèn bước đó ở
  đâu trong hàm `retrieve`?
