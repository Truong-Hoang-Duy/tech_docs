# Debug: hình ảnh nhảy qua câu khác (exam PDF extract)

Công cụ độc lập để tái hiện và soi lỗi "upload PDF vào ngân hàng câu hỏi, hình ảnh
bị gán nhầm sang câu khác". Chạy tách biệt hoàn toàn với API/queue/DB — chỉ gọi
thẳng các hàm xử lý thật của backend trong một tiến trình Python, nên kết quả
phản ánh đúng những gì production sẽ làm với cùng file đó.

## Cách hoạt động (tóm tắt)

File PDF đi qua 2 tầng, độc lập với nhau:

1. **Hình học (không LLM)** — `pdf_figures.read_layout()`: với trang "born-digital"
   (có text layer thật), hệ thống đọc thẳng toạ độ hình + toạ độ chữ "Câu N" trên
   trang để biết hình nằm dưới câu nào. Đáng tin cậy gần như tuyệt đối vì là phép
   so sánh toạ độ, không phải suy đoán.
2. **LLM (`question_exam_extract`)** — với trang **scan** (không có text layer),
   không có toạ độ để so sánh, nên việc "hình này thuộc câu nào" phải hỏi mô hình
   qua 2 tín hiệu nó tự báo: `figure_ids` (câu tự nhận có hình) và `figure_anchors`
   (hình nằm ngay trước/sau câu nào). Code gốc (xem comment trong
   `question_exam_extract.py::match_figures_to_questions`) đã ghi nhận là **2 tín
   hiệu này không ổn định giữa các lần chạy** — đây gần như chắc chắn là nguồn gốc
   của lỗi "hình nhảy câu".

Script `debug_figure_matching.py` chạy nguyên luồng thật (`extract_exam()`), chỉ
gắn thêm 2 "móc" quan sát (không sửa code backend) để in ra: mỗi crop hình ở
trang scan, model tự nhận thuộc câu nào (`figure_ids`), model báo anchor gì
(`figure_anchors`), và **quyết định cuối cùng** — từ đó thấy ngay chỗ nào bị đổi
câu và do tín hiệu nào gây ra.

## Chạy ngay

**macOS / Linux** (dùng `run.sh`):
```bash
cd bookforge
./tech_docs/research/pdf-figure-debug/run.sh tech_docs/pdf/bo_de_1.pdf
```

**Windows** (dùng `run.ps1`, chạy trong PowerShell):
```powershell
cd bookforge
.\tech_docs\research\pdf-figure-debug\run.ps1 tech_docs\pdf\bo_de_1.pdf
```

- Repo có sẵn 7 đề mẫu ở [tech_docs/pdf/](../../pdf/) (`bo_de_1.pdf` → `bo_de_7.pdf`), dùng
  ngay để test thủ công mà không cần chuẩn bị file riêng.
- Nhiều file / cả thư mục: script nhận nhiều tham số hoặc một thư mục chứa `.pdf`:
  ```bash
  ./tech_docs/research/pdf-figure-debug/run.sh tech_docs/pdf/
  # hoặc chỉ định từng file
  ./tech_docs/research/pdf-figure-debug/run.sh tech_docs/pdf/bo_de_1.pdf tech_docs/pdf/bo_de_2.pdf
  ```
  (Windows: thay `run.sh` bằng `run.ps1` và dấu `\` cho đường dẫn như ví dụ trên.)
- Báo cáo ghi ra `tech_docs/research/pdf-figure-debug/out/<tên-file>__<thời-gian>.txt`
  (thư mục `out/` đã được `.gitignore`, không lo vô tình commit).
- Cả hai script tự dùng đúng venv của backend (`backend/services/api/.venv`) — cần venv
  này đã cài dependency như bình thường (`uv sync` trong `backend/services/api`
  nếu chưa có). `run.sh` tìm venv ở `.venv/bin/python` (macOS/Linux), `run.ps1` tìm ở
  `.venv\Scripts\python.exe` (Windows) — đúng theo cấu trúc venv của từng hệ điều hành.

Cờ tuỳ chọn:
- `--no-llm`: chỉ chạy tầng hình học (mục 1 ở trên) — **miễn phí, không gọi LLM**,
  chạy tức thì. Dùng để lọc nhanh: file/trang nào là "scan" (vùng rủi ro) trước
  khi tốn tiền gọi LLM.
- `--max-pages N`: chỉ xử lý N trang đầu — hữu ích để test nhanh/rẻ trên đề dài
  hàng chục trang trước khi chạy full.

Đã tự chạy thử với 1 file PDF mẫu tự sinh (2 trang, có hình vẽ) ở cả 2 chế độ —
xem `sample_test.pdf` trong thư mục này và 2 báo cáo mẫu trong `out/` để hình dung
định dạng output. Xoá `sample_test.pdf` bất cứ lúc nào, nó chỉ là dữ liệu demo.

## Cách nạp tài liệu để test

Không cần sửa gì cả — chỉ cần trỏ script vào file/thư mục PDF thật:

```bash
./tech_docs/research/pdf-figure-debug/run.sh /đường/dẫn/tới/lô/đề/thi/
```

Script tự lặp qua mọi `.pdf` trong thư mục đó, xử lý từng file độc lập, một file
lỗi không làm dừng cả lô (báo cáo file đó sẽ ghi lại traceback thay vì kết quả).

## Đọc báo cáo (.txt)

- **TÓM TẮT NHANH**: đếm số hình bị "ĐỔI CÂU" / "KHÔNG GÁN ĐƯỢC" / "giữ nguyên" —
  liếc mục này trước để biết file có vấn đề hay không.
- **Mục 1**: hình nào được gán bằng hình học (đáng tin) — nếu toàn bộ hình trong
  file đều nằm ở mục này thì bug không nằm ở luồng đang debug (khả năng cao là
  toàn bộ đề là born-digital, không qua nhánh LLM-đoán).
- **Mục 3** (chỉ khi không dùng `--no-llm`): với mỗi crop ở trang scan —
  `model tự nhận (figure_ids)` vs `figure_anchors` vs `KẾT QUẢ CUỐI`. Dòng có
  `⚠ ĐỔI CÂU` nghĩa là quyết định cuối khác với câu mà chính model tự gắn hình
  vào — đúng hiện tượng "hình nhảy câu". `⚠ KHÔNG GÁN ĐƯỢC` là hình bị rớt hẳn.
- **Mục 4**: danh sách câu hỏi + `figure_ids` cuối cùng, để đối chiếu trực quan
  với file PDF gốc.

## Giới hạn cần biết khi test cục bộ

- Setting dùng thẳng `backend/services/api/.env` (không tạo key/config mới) —
  đúng như production đang chạy, gồm cả model cho lời gọi LLM chính
  (`openai:gpt-5.4-nano` theo `.env` hiện tại).
- **OCR ảnh (`BOOKFORGE_IMAGE_LLM_API_KEY`, provider Mistral) đang để trống ở
  `.env` local** → trang scan sẽ KHÔNG có crop hình nào được cắt ra (mục 3 sẽ
  luôn rỗng dù đề có hình ở trang scan). Đây là giới hạn của môi trường local,
  không phải bug của script. Muốn tái hiện đúng lỗi trên trang scan, cần điền
  `BOOKFORGE_IMAGE_LLM_API_KEY` (Mistral) vào `backend/services/api/.env` trước
  khi chạy — production đang dùng Mistral thật nên mới thấy hiện tượng này.
- Mỗi lần chạy (không có `--no-llm`) là **lời gọi LLM thật, tốn phí thật** —
  dùng `--no-llm` hoặc `--max-pages` khi chỉ cần test nhanh trên nhiều file.

## Cấu trúc thư mục

```
debug_figure_matching.py   # script chính, tự chứa, không sửa code backend
run.sh                      # chạy bằng đúng venv backend (macOS / Linux)
run.ps1                     # chạy bằng đúng venv backend (Windows / PowerShell)
sample_test.pdf             # PDF mẫu tự sinh để smoke-test (xoá được)
out/                         # báo cáo .txt sinh ra (gitignore)
```
