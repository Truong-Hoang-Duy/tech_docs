# Kế hoạch Kỹ thuật: Tạo sinh câu hỏi theo thang Bloom

## 1. Lần theo luồng thực thi (Codebase Trace)

Dựa trên bản đồ `1_repo-map.md` và mã nguồn thực tế, luồng tạo sinh câu hỏi (Question Generation) hiện tại đang chạy qua các thành phần sau:

- **API Router (`services/api/src/bookforge_api/api/question_cards.py:687`)**:
  - Endpoint `POST /generate` được định nghĩa thông qua hàm `def generate(..., payload: QuestionCardGenerateRequest, ...)`.
- **Payload Schema (`schemas/question_bank.py:571`)**:
  - `QuestionCardGenerateRequest` chứa các tham số: `subject`, `grade`, `topic`, `question_type`, `num_questions`, và đặc biệt là `cognitive_level: CognitiveLevel | None`.
- **AI Service (`services/api/src/bookforge_api/services/question_cards_ai.py:150`)**:
  - Hàm `generate_question_cards` gọi Pydantic AI Agent để sinh dữ liệu dựa trên prompt và trả về danh sách `result.payloads`.
- **DB Model & Lưu trữ (`services/api/src/bookforge_api/api/question_cards.py:793`)**:
  - Router loop qua kết quả AI và gọi `create_card` thông qua schema `QuestionCardCreateRequest` để ghi vào DB (`QuestionCard`).
  - **Điểm yếu hiện tại**: Thuộc tính `score` của thẻ câu hỏi không được truyền vào lúc tạo (`create_card` đang bỏ qua `score`, dẫn đến câu hỏi sinh ra có `score=None`).

## 2. Kế hoạch Kỹ thuật (Technical Plan)

Để đáp ứng yêu cầu cấu hình barem điểm linh hoạt theo thang Bloom và đảm bảo sinh câu hỏi chuẩn chỉ, kế hoạch thi công được đề xuất như sau:

### Bước 2.1: Cập nhật Schema cho Config Điểm
- Mở rộng `QuestionCardGenerateRequest` (`schemas/question_bank.py`) để FE có thể gửi cấu hình điểm linh hoạt cho từng đợt sinh:
  - Thêm trường: `cognitive_level_scores: dict[CognitiveLevel, float] | None = Field(default=None, description="Barem điểm ánh xạ theo thang Bloom")`.
  - *(Lý do: Đảm bảo BE không fix cứng cấu hình điểm số, cho phép FE truyền map cấu hình tương ứng lúc generate).*

### Bước 2.2: Sửa đổi AI Prompt (Hỗ trợ định dạng phức tạp)
- Kiểm tra system prompt của Agent trong `services/question_cards_ai.py`.
- Đảm bảo AI được gò constraint rõ ràng về cách sinh định dạng công thức chuẩn (ví dụ chuẩn LaTeX `$$` cho block và `$` cho inline) để cover bài toán các môn học tự nhiên (Toán/Lý) mà không bị lỗi giao diện.

### Bước 2.3: Mapping Điểm (Score) khi lưu DB
- Tại `api/question_cards.py` (hàm `generate`), khi build đối tượng `QuestionCardCreateRequest`:
  - Trích xuất `score` từ `payload.cognitive_level_scores` dựa trên khóa `payload.cognitive_level` (hoặc level do AI sinh ra đối với từng thẻ nếu sinh hỗn hợp).
  - Truyền giá trị `score` vào `QuestionCardCreateRequest(..., score=mapped_score, ...)`.

---

> [!WARNING]
> ## 3. Đóng vai trò phản biện: Rủi ro & Đánh đổi (Trade-offs)
> 
> Trước khi đi đến bước tạo Task Doc, cần lưu ý 2 rủi ro kiến trúc sau:
> 
> **Rủi ro 1: Phân mảnh dữ liệu điểm (Data Consistency)**
> Việc truyền barem điểm "linh hoạt" per-request từ FE sẽ dẫn đến tình trạng: Hai câu hỏi sinh ra ở 2 thời điểm khác nhau, cùng mức "Nhận biết", nhưng có điểm khác nhau (VD: 1 điểm và 2 điểm) do config thay đổi. Khi ráp hai câu này vào chung một đề thi (Test Paper), điểm số sẽ bị lệch chuẩn. 
> *Đề xuất:* Cần xác định rõ barem điểm này sẽ được quản lý ở đâu về mặt lâu dài. Liệu có nên lưu cấu hình này thành một Entity tĩnh ở cấp độ `Organization` trong DB không, hay hoàn toàn giao cho FE tự do truyền?
> 
> **Rủi ro 2: Ảo giác đánh giá của LLM (Hallucination in Mixed Generation)**
> Nếu người dùng để `cognitive_level = None` (AI tự sinh trộn lẫn nhiều cấp độ), ta sẽ phải dựa vào AI để tự định danh `cognitive_level` cho mỗi câu hỏi, rồi BE mới mapping ra `score`. Vấn đề là LLM thường đánh giá mức thang Bloom sai lệch (hay nhầm "Thông hiểu" thành "Vận dụng"), dẫn đến việc gán điểm cao/thấp hơn năng lực thực tế của câu hỏi đó.
> *Đề xuất:* Ở giai đoạn đầu, có nên bắt buộc FE truyền tường minh `cognitive_level` khi gọi API generate (không cho phép sinh hỗn hợp)?

## 4. Open Questions
1. Bạn muốn giải quyết rủi ro số 1 như thế nào? Để FE truyền map `cognitive_level_scores` linh hoạt per-request, hay lưu cấu hình điểm mặc định vào database?
2. Bạn có đồng ý giới hạn AI chỉ sinh đúng 1 mức độ Bloom trong mỗi request (bắt buộc truyền `cognitive_level`) để tránh rủi ro số 2 không?
