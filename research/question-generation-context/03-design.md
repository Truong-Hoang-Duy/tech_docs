# 03 — Thiết kế: Ô nhập ngữ cảnh khi tạo câu hỏi trong thư mục câu hỏi

> Nguồn sự thật: `02-findings.md` (đọc tại `bookforge@ebd0693a`, `bookforge-fe@a09c30d`).
> Chỗ nào không có bằng chứng trực tiếp trong findings được đánh dấu **[giả định]**.
> Đường dẫn BE tính từ `backend/services/api/src/bookforge_api/`, FE tính từ `frontend/src/`.

## Kết luận chốt

**Đề xuất — chờ bạn chốt:** làm theo **Phương án B**.
- Thêm **một trường mới, riêng cho lời dặn của giáo viên**, vào `POST /api/question-cards/generate`. Không đụng `hint`.
- Thêm **một ô nhập không bắt buộc** vào drawer dùng chung `MassQuestionGenerateDrawer`, nên ô có ở cả 4 nơi đang mở drawer.
- **Các ô chọn luôn thắng lời dặn.** Loại câu hỏi đã được schema ép cứng; mức nhận thức và số câu được dặn bằng prompt.
- Lời dặn **không lưu vào thẻ câu hỏi**, chỉ ghi vào nhật ký lượt AI.

Lý do chọn B thay vì tái dùng `hint`: `hint` đang mang một nghĩa khác, đã có test khoá hành vi, và được ghi vào `content_json` của từng thẻ. Trộn hai nghĩa vào một trường thì lỗi xảy ra **im lặng**; tách trường thì lỗi xảy ra **ồn ào** (422). Chi tiết ở phần Khuyến nghị.

## Phương án A — Tái dùng `hint`, đổi nghĩa thành "yêu cầu thêm"

Hợp đồng API giữ nguyên: FE chỉ đổi `hint: null` thành giá trị người dùng gõ. BE đổi nghĩa `hint`:
- `llm/question_bank_prompts.py:86-88` — bỏ điều kiện `not knowledge_lines and not competency_lines`, đổi nhãn "Mục tiêu liên quan" thành nhãn lời dặn, thêm câu ưu tiên ô chọn.
- `api/question_cards.py:680-687` và `:818-822` — **thôi ghi `hint` vào `content_json`**. Nếu không, câu kiểu "Bạn là giáo viên dạy toán lớp 10…" sẽ nằm trong mọi thẻ sinh ra.
- Viết lại các test đang khoá nghĩa cũ:
  - `tests/test_question_cards_generate_api.py:118-130` (`test_generate_stores_related_goal_hint`)
  - `tests/test_question_curriculum_api.py:412` (`…uses_paths_not_hint_when_ids_present`)
  - `:474-509` (`…persists_node_ids_and_skips_hint`)
  - `:512-532` (`…hint_only_still_writes_hint`)
- FE: thêm ô vào drawer, gán vào `hint` trong `buildPayload` (`MassQuestionGenerateDrawer.tsx:846`).

**Được:** không đổi hợp đồng API, không đổi kiểu `TGenerateQuestionCardsRequest`. BE đụng 2 file nguồn.
**Mất:** xoá hẳn khái niệm "mục tiêu liên quan" mà BE đang có (FE chưa từng dùng — findings Q7). Phải viết lại 4 test đang khoá hành vi cũ.
**Hỏng ở đâu khi lỗi:** nếu FE lên production trước BE, API vẫn nhận `hint` mà không báo lỗi, nhưng:
- (1) lời dặn **bị bỏ im lặng** khi người dùng chọn Kiến thức/Năng lực;
- (2) lời dặn **bị ghi vào `content_json.hint`** của mọi thẻ — dữ liệu bẩn, sau này phải dọn.

Không có tín hiệu nào cho người dùng hay log biết đã sai.

## Phương án B — Trường mới riêng cho lời dặn

Thêm một trường mới, tên tạm là `instructions` (chốt tên ở task doc), chạy song song với `hint`:
- `schemas/question_bank.py:585-611` — `instructions: str | None = Field(default=None, max_length=1000)`.
- `services/question_cards_ai.py:89-143` — `generate_question_cards` nhận thêm tham số và chuyển tiếp xuống prompt.
- `llm/question_bank_prompts.py:51-96` — `question_generation_user_prompt` thêm một khối lời dặn:
  - khối này **không phụ thuộc** Kiến thức/Năng lực;
  - đặt **sau** các dòng thông số, **trước** khối ngữ liệu.
- `api/question_cards.py:696-845` — `strip()`, chuỗi rỗng thành `None`, truyền xuống service, thêm khoá vào `action_metadata` (`:740-749`). **Không** ghi vào `content_json`.
- FE:
  - `api/question-bank-api.ts:767-782` — thêm field optional.
  - Drawer — thêm state, thêm ô nhập, thêm một dòng trong `buildPayload`.

Minh hoạ khối prompt (không phải code chốt):
```python
if instructions:
    lines.append('')
    lines.append('Yêu cầu thêm của giáo viên (chỉ dùng để điều chỉnh cách ra câu hỏi):')
    lines.append(instructions)
    lines.append('Nếu yêu cầu trên mâu thuẫn với số câu, dạng câu hỏi, mức độ nhận thức '
                 'đã nêu ở trên, luôn theo các thông số ở trên.')
```

**Được:** `hint` và 4 test hiện có giữ nguyên. Lời dặn có hiệu lực cả khi chọn Kiến thức/Năng lực. Thẻ câu hỏi không bị ghi thêm dữ liệu.
**Mất:** đổi hợp đồng API (+1 field optional). BE đụng 4 file nguồn thay vì 2; FE đụng thêm 1 file kiểu. `hint` tiếp tục là trường "chết" phía FE.
**Hỏng ở đâu khi lỗi:** nếu FE lên trước BE, request có field lạ bị **422** (`extra='forbid'`, findings Q1). **Toàn bộ nút tạo câu hỏi bằng AI hỏng ở cả 4 nơi**, nhưng hỏng rõ ràng: người dùng thấy toast lỗi, log có 422. Chặn được bằng thứ tự triển khai BE trước (§16 đã quy định).

**Chi phí token (chung cho cả hai phương án):** 1000 ký tự ≈ 250 token theo chính công thức `(len + 3) // 4` của handler. Mức này nằm trong phần dư +256 của ước lượng đầu vào (`api/question_cards.py:732`), nên **không phải sửa công thức** khi giữ giới hạn 1000. Tiếng Việt có dấu có thể tốn hơn 4 ký tự/token **[giả định]** — cần kiểm bằng cách so `usage.prompt_tokens` trong `record_ai_action` của một request có và không có lời dặn.

## Khuyến nghị

**Chọn B.** Ba lý do đo được:
1. **Chế độ hỏng:** A hỏng im lặng và để lại dữ liệu bẩn trong `content_json` của thẻ; B hỏng bằng 422 thấy ngay và không ghi dữ liệu sai.
2. **Không phá hành vi đã khoá:** B giữ nguyên 4 test của `hint`; A phải viết lại cả 4, tức là xoá một ý đồ thiết kế ai đó đã cố ý test.
3. **Chênh lệch khối lượng nhỏ:** B hơn A 2 file BE (schema, service) và 1 file kiểu FE, mỗi file vài dòng.

**Nên đổi sang A khi:** bạn xác nhận `hint` ("mục tiêu liên quan") là tàn dư không ai định dùng nữa, **hoặc** có client ngoài drawer (tích hợp, script) đang gọi `/generate` mà không muốn đổi hợp đồng. Findings không thấy client nào như vậy trong `bookforge-fe`.

**Loại ngay — chỉ sửa FE, gửi `hint` nguyên nghĩa cũ:** không cần sửa BE, nhưng lời dặn **bị bỏ mỗi khi chọn Kiến thức/Năng lực** (findings Q2) và bị ghi vào mọi thẻ (Q7). Làm vậy là sai đúng yêu cầu gốc.

## Không làm lần này

1. **Tự bóc thông số từ lời dặn để điền ô** (ví dụ đọc "10 câu", "lớp 10" rồi tự đặt ô Số lượng, Khối/lớp). Ô Chủ đề vẫn bắt buộc như hôm nay.
2. **Kiểm tra sau khi sinh** xem mức nhận thức của câu có khớp ô chọn không — không có cách kiểm cứng, chỉ có prompt (findings Q4).
3. **Luồng notebook nhập câu hỏi** (`QuestionImportNotebookPage.tsx:703-780`) — không thêm ô; nó không gửi field mới nên hành vi giữ nguyên.
4. **Lưu lời dặn vào thẻ** hoặc hiển thị lại lời dặn đã dùng cho thẻ nào — chỉ ghi vào nhật ký lượt AI.
5. **Dọn `mass-generate-payload.ts`** (hàm dựng payload không được dùng) và **tách nhỏ drawer 1961 dòng** — chỉ ghi cảnh báo vào task doc, không refactor kèm (§16).
6. **Lưu mẫu lời dặn / gợi ý lời dặn sẵn** cho giáo viên chọn.
7. **Nới giới hạn độ dài quá 1000 ký tự** — trừ khi bạn chốt khác ở câu hỏi 3 bên dưới.

## Ảnh hưởng tới chỗ đang chạy

**BE** (phương án B)
- `POST /api/question-cards/generate` — `api/question_cards.py:690-845`. Request cũ không có field mới: prompt **giống hệt hôm nay**.
- Prompt sinh câu hỏi — `llm/question_bank_prompts.py:51-96`. Test gọi thẳng hàm này: `tests/test_question_cards_ai.py:336`, `tests/test_question_curriculum_api.py:412`. Phải giữ nguyên chữ ký cũ (tham số mới là keyword có mặc định).
- Nhật ký AI — `record_ai_action(action_type='question_set_generation')` tại `api/question_cards.py:768-777` (thất bại) và `:827-842` (thành công). Metadata có thêm một khoá.

**FE** — drawer dùng chung nên ô mới xuất hiện ở cả 4 nơi:
- `…/folder-list/FolderListScreen.tsx:2217` (nút "Tạo câu hỏi mới" `:1633`)
- `…/cards/CardsPage.tsx:1271` (nút `:1063`, `onBulkCreate` `:1203`)
- `…/sets/QuestionCollectionSetsPage.tsx:2287` (nút `:3424`)
- `templates/DocumentsPage/index.tsx:123` — chỗ này **luôn** có ngữ liệu từ mục lục tài liệu. Prompt đang ép "Chỉ dùng thông tin có trong ngữ liệu" (findings Q2), nên khối lời dặn phải nói rõ nó là cách ra câu hỏi, không phải nguồn kiến thức (đã có trong minh hoạ ở B).

Thay đổi trong drawer và các file liên quan:
- `MassQuestionGenerateDrawer.tsx` — thêm state cạnh `:339-391`; thêm ô trong khối "B. Cấu hình chung" `:1037-1194`; sửa `buildPayload` `:828-863`.
- Ô nhập đặt trong **file partial riêng** cạnh drawer, để không làm file 1961 dòng dài thêm quá mức cần (`frontend/CONVENTION.md:3-5`). Tên file chốt ở task doc.
- **Không** sửa `mass-generate-payload.ts`: drawer không gọi file đó (findings, mục "Điều brief không hỏi" 1).

Drawer có reset state khi đóng rồi mở lại hay không: **[giả định]** là không reset, vì các state khác (`topicValue`, `sourceText`) khởi tạo bằng `useState` một lần. Cần kiểm drawer có bị unmount khi `isOpen=false` không, để quyết lời dặn có còn giữ khi mở lại.

## Kế hoạch triển khai

Hai task doc: BE trước, FE sau (§5, §16). Bước BE chặn toàn bộ bước FE.

**BE — `backend/docs/tasks/YYYY-MM-DD-question-generation-context.md`**
1. Thêm trường vào `QuestionCardGenerateRequest`, giới hạn 1000 ký tự.
2. Thêm tham số vào `question_generation_user_prompt`, chèn khối lời dặn và câu ưu tiên ô chọn (cần bước 1 để có tên trường).
3. Chuyển tiếp tham số qua `generate_question_cards` (cần bước 2).
4. Handler: `strip`, rỗng thành `None`, truyền xuống, thêm vào `action_metadata`, không ghi `content_json` (cần bước 3).
5. Test:
   - khối lời dặn có mặt khi có/không có Kiến thức/Năng lực và khi có `source_text`;
   - vắng field thì prompt không đổi;
   - quá 1000 ký tự thì 422;
   - `content_json` không có lời dặn;
   - 4 test `hint` cũ vẫn xanh.

**FE — `backend/docs/tasks/YYYY-MM-DD-question-generation-context-frontend.md`** (chỉ bắt đầu khi BE đã có trên môi trường FE gọi tới)

6. Thêm field optional vào `TGenerateQuestionCardsRequest`.
7. Tạo component partial cho ô nhập:
   - nhãn và placeholder theo ví dụ trong `00-desc.md`;
   - đếm ký tự x/1000, chặn nhập quá giới hạn.
8. Gắn vào drawer: state, đặt ô trong khối B, thêm vào `buildPayload`, gửi rỗng thành `null` (cần 6, 7).
9. (kiểm tay) Chạy ở cả 4 nơi mount; thử lời dặn mâu thuẫn ô chọn (ví dụ gõ "10 câu" nhưng chọn 5) và ghi lại kết quả.

## Chưa chốt — cần bạn quyết

1. **Phương án A hay B?**
   - **B (khuyến nghị):** đổi hợp đồng API (+1 field), `hint` giữ nguyên; triển khai sai thứ tự thì hỏng rõ bằng 422.
   - **A:** hợp đồng giữ nguyên, xoá nghĩa "mục tiêu liên quan" và viết lại 4 test; triển khai sai thứ tự thì lời dặn bị bỏ im lặng và ghi bẩn vào thẻ.

2. **Có kiểm số câu sau khi sinh không?** Hôm nay prompt nói "đúng N câu" nhưng không ai kiểm (findings Q4); lời dặn kiểu "tạo 10 câu" làm tăng khả năng lệch.
   - **Không kiểm (giữ như hôm nay):** không tốn thêm token; người dùng có thể nhận ít hoặc nhiều câu hơn số đã chọn, toast vẫn báo đúng số thực tế.
   - **Có kiểm:** sai số câu thì cho model sửa, dùng cơ chế sửa output sẵn có (tối đa 2 lượt, `OUTPUT_REPAIR_PASSES`). Mỗi lượt sửa tốn thêm ≈ một lần output (tới 4096 token); vẫn sai thì 502, không tạo câu nào. Việc này đổi hành vi cho **mọi** request `/generate`, kể cả khi không có lời dặn.

3. **Giới hạn độ dài lời dặn?**
   - **1000 ký tự:** vừa ví dụ trong `00-desc.md` (~200 ký tự) với dư nhiều; không phải sửa công thức ước lượng token.
   - **Tới 4000 ký tự:** giáo viên dán được yêu cầu dài, nhưng phải cộng độ dài lời dặn vào `estimated_input_tokens` (`api/question_cards.py:732`), nếu không phần output có thể bị ăn mất khi gói có trần token thấp.
