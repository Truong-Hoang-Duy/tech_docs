# Trạng thái: Ô nhập ngữ cảnh khi tạo câu hỏi trong thư mục câu hỏi

**Cập nhật:** 2026-09-14 · **Phía:** cả hai · **Giai đoạn:** thi công — BE đã push, chờ PR; BE + FE đã push, chờ tạo PR

## Mục tiêu
Thêm ô lời dặn tự do vào drawer "Tạo câu hỏi hàng loạt" (mở từ mọi nút "Tạo câu hỏi mới")
để giáo viên mô tả ý muốn; câu hỏi AI sinh ra bám theo lời dặn,
đồng thời các ô chọn (loại, số lượng, mức độ nhận thức) luôn thắng khi mâu thuẫn.

## Quyết định đã chốt
1. Phương án B — trường mới `instructions` (≤1000), không đụng `hint` (người dùng chốt 2026-09-14).
2. Không kiểm số câu / mức độ sau khi sinh — **mặc định Claude chọn**, người dùng chưa trả lời câu 2 của `03-design.md`.
3. Giới hạn 1000 ký tự, không đổi công thức ước lượng token — **mặc định Claude chọn**, chưa trả lời câu 3.
4. Lời dặn không lưu vào thẻ; ghi `AIAction.metadata_json['instructions']`.
5. FE: component `mass-generate/partial/mass-generate-instructions-field.tsx`, đặt sau "Mức độ nhận thức";
   reset trong `useEffect` mở drawer (`:499-527` — đã kiểm, drawer reset mọi state khi mở).
6. FE: nhãn ô là "Ngữ cảnh"; placeholder là câu người dùng chốt (2026-09-14, xem `qa.md`).

## Phương án đang theo
Xem 2 task doc. Câu chữ khối prompt đã chốt trong task doc BE (quyết định 4).

## File trong thư mục này
- `00-desc.md` — mô tả nghiệp vụ (người dùng đã sửa)
- `01-brief.md` — 7 câu hỏi khảo sát + 7 giả định
- `02-findings.md` — trả lời đủ 7 câu, 3/7 giả định sai hoặc sai một phần
- `03-design.md` — A (tái dùng hint) vs B (trường mới); đã chốt B
- `qa.md` — nhật ký quyết định lúc thi công

Task doc (repo `bookforge`):
- `backend/docs/tasks/2026-09-14-question-generation-context.md` — BE, 162 dòng
- `backend/docs/tasks/2026-09-14-question-generation-context-frontend.md` — FE, 155 dòng, phụ thuộc BE

## Tiến độ thi công
- BE (2026-09-14): nhánh `feat/question-generation-instructions` đã push lên origin — commit `71addc7` (docs: 2 task doc) + `3cee81a` (feat).
  7 file, +148 dòng, không xoá dòng nào. 8 test mới; full suite 3885 passed, 3 skipped; ruff sạch.
  DoD tick đủ, kể cả mục kiểm tay (người dùng chạy LLM thật: +331 prompt_tokens cho 984 ký tự).
  Lý do của quyết định 8 trong task doc đã sửa: +256 không phải phần dư; vô hại vì trần gói 80k ≫ budget 4096.
- FE (2026-09-14): nhánh `feat/question-generation-instructions` (tách từ `dev` @`a09c30d`) đã push — commit `b7f4ecd`.
  BE thêm commit `9d7f3f9` (task doc FE: đổi nhãn "Ngữ cảnh" + tick DoD) đã push.
  Trước đó: 4 file (2 sửa, 2 mới trong `mass-generate/partial/`).
  typecheck sạch, lint 0 lỗi, full suite 656 passed. 7 mục DoD tự động đã tick; 6 mục kiểm tay người dùng xác nhận đạt 2026-09-14 (mục 6: dặn 10 câu, chọn 3 → nhận 3 câu — ghi vào PR).
  Sau đó đổi nhãn → "Ngữ cảnh" + placeholder mới: doc sửa trước, code sau; test mass-generate + typecheck + lint chạy lại sạch.

## Câu hỏi mở
- Người dùng xác nhận hoặc đổi quyết định 2 và 3.
- `docs/QUESTION_BANK_API_GUIDE.md` §3.9 ghi trần số câu 20 / mặc định 5, code là trần 100 — lệch sẵn, ngoài phạm vi.

## Bước tiếp theo
BE: người dùng tạo PR → merge vào dev → deploy. Người dùng tạo 2 PR vào `dev` (BE merge + deploy trước FE); mô tả PR FE phải có kết quả mục 6.
