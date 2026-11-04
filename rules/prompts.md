# Câu lệnh mẫu

Copy câu lệnh, thay `<slug>` và các chỗ `<...>`, rồi dán vào khung chat của AI tương ứng.
Cách làm chung xem [`README.md`](README.md), khung tài liệu xem [`templates.md`](templates.md).

---

## 0. Chỉ tìm hiểu một chức năng (chưa làm gì)

```text
Đọc tech_docs/rules/README.md. Lấy code mới nhất (theo mục Git), chưa tạo hay sửa file nào.
Tìm hiểu chức năng: "<mô tả bằng lời thường>" rồi trả lời ngay trong chat:
1. Luồng từ lúc người dùng bấm trên giao diện → gọi tới đâu ở backend → lưu vào đâu (kèm file:dòng).
2. Có điều kiện phân quyền hay cờ bật/tắt nào đang khoá chức năng này không?
3. Giới hạn hiện tại hoặc chỗ dễ lỗi là gì?
Giải thích ngắn gọn, dễ hiểu.
```

---

## 1. Tìm hiểu (AI A)

**Việc thường:**
```text
Đọc tech_docs/rules/README.md và mẫu 01-analysis trong tech_docs/rules/templates.md.
Lấy code mới nhất (theo mục Git), tìm hiểu code thật và tạo tech_docs/plans/<slug>/01-analysis.md. Chưa sửa code.
Slug: <tên bạn chọn | để trống — AI tự đặt 2–3 chữ tiếng Anh theo mục 9 README và báo lại>
Yêu cầu:
- Lỗi: <ở màn hình nào, vai trò gì · bấm gì · thấy gì · mong đợi gì>
- Hoặc tính năng: <ai dùng · muốn làm được gì · kết quả mong muốn · phần không làm>
```

**Việc có spec:**
```text
Đọc tech_docs/rules/README.md (mục 3.1) và mẫu 01-analysis trong tech_docs/rules/templates.md.
Lấy code mới nhất (theo mục Git), kiểm tra spec với code thật và tạo tech_docs/plans/<slug>/01-analysis.md. Chưa sửa code.
Kiểm tra cả spec có làm được không; chỗ nghi sai ghi lại để tôi chốt, không tự sửa spec.
Slug: <tên bạn chọn | để trống — AI tự đặt 2–3 chữ tiếng Anh theo mục 9 README và báo lại>
Spec: <đường dẫn tới spec>
Phạm vi lần này: <cả gói | chỉ phần … | "Làm theo đúng spec">
Lưu ý thêm (nếu có): <thứ tự ưu tiên, phần tạm chưa làm…>
```

**Việc nhỏ (gộp bước 1 và 2):**
```text
Đọc tech_docs/rules/README.md và mẫu 02-plan trong tech_docs/rules/templates.md.
Lấy code mới nhất (theo mục Git), tìm hiểu code thật và lập thẳng tech_docs/plans/<slug>/02-plan.md (ghi hiện trạng vào mục 1). Chưa sửa code.
Slug: <tên bạn chọn | để trống — AI tự đặt 2–3 chữ tiếng Anh theo mục 9 README và báo lại>
Yêu cầu: <mô tả lỗi / yêu cầu nhỏ>
```

**Chốt sau khi đọc `01-analysis.md`:**
```text
Chốt theo phương án <A / B>. Trả lời câu hỏi cần chốt: <câu trả lời>.
Cập nhật lại tech_docs/plans/<slug>/01-analysis.md cho khớp.
```

---

## 2. Lập kế hoạch (AI A)

```text
Đọc tech_docs/rules/README.md, mẫu 02-plan trong tech_docs/rules/templates.md và tech_docs/plans/<slug>/01-analysis.md.
Lập kế hoạch vào tech_docs/plans/<slug>/02-plan.md (việc có spec: Phần A viết theo dạng superpowers). Chưa sửa code.
```

---

## 3. Duyệt chéo (gửi AI B — AI không lập kế hoạch)

```text
Đọc tech_docs/rules/README.md (mục 5 — quy tắc duyệt chéo) và các file trong tech_docs/plans/<slug>/ (kèm spec nếu có).
Mở code thật đối chiếu từng chỗ kế hoạch nhắc tới, ghi nhận xét 🔴 / 🟡 / 🟢 vào mục Duyệt chéo của 02-plan.md và chốt trạng thái. Chưa sửa code.
```

---

## 4. Làm (AI bạn chọn)

```text
Đọc tech_docs/rules/README.md (mục Git và Những chỗ hay vấp) và tech_docs/plans/<slug>/02-plan.md đã duyệt.
Làm theo kế hoạch <toàn bộ | từ bước X đến bước Y>. Xong bước nào đánh dấu [x] và ghi kết quả vào mục Nhật ký. Không commit.
```

**Khi AI dừng lại hỏi giữa chừng:**
```text
Làm theo hướng <X>. Ghi vào mục Quyết định phát sinh trong 02-plan.md rồi làm tiếp.
```

---

## 5. Nghiệm thu chéo (gửi AI không viết code ở bước 4)

```text
Đọc tech_docs/rules/README.md và tech_docs/plans/<slug>/02-plan.md.
Cập nhật nhánh theo bản mới nhất, đối chiếu từng thay đổi với kế hoạch, chạy lại toàn bộ kiểm tra như CI
và ghi kết luận vào mục Nghiệm thu của 02-plan.md.
```

---

## 6. Kiểm tay (mở một hội thoại mới với AI không viết code ở bước 4 — Gemini hoặc Claude)

```text
Đọc tech_docs/rules/README.md (mục Kiểm tay) và mẫu 03-manual-test trong tech_docs/rules/templates.md.
Viết hướng dẫn kiểm tay cho việc ở tech_docs/plans/<slug>/ vào 03-manual-test.md.
Tự bấm thử trước bằng công cụ điều khiển trình duyệt bạn đang có (nếu không có thì báo tôi),
sau đó hướng dẫn tôi từng kịch bản một. Chưa sửa code khi tôi chưa cho phép.
```

**Báo lỗi khi kiểm tay:**
```text
Kịch bản <số>, bước <số>: <thấy gì>. (Kèm ảnh nếu có.)
Tìm nguyên nhân, ghi vào 03-manual-test.md. <Được phép sửa | Chưa sửa, báo tôi trước>.
```

**Kiểm xong:**
```text
Tôi đã kiểm xong, các kịch bản đều Đạt. Ghi kết quả vào 03-manual-test.md và đổi trạng thái 02-plan.md sang VERIFIED.
```

---

## 7. Chép kế hoạch sang backend và commit

```text
Đọc tech_docs/rules/README.md (mục 7 Chép kế hoạch và mục 8 Git).
Chép Phần A của tech_docs/plans/<slug>/02-plan.md sang backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md,
rồi commit <(chưa push) | và push> các thay đổi của việc này. Ghi đường dẫn và mã commit vào mục Commit của 02-plan.md.
```

---

## Cứu hộ (mất phiên chat, đổi máy, hôm sau làm tiếp)

```text
Đọc các file trong tech_docs/plans/<slug>/, kiểm tra git status ở backend/ và frontend/,
rồi tóm tắt trong 5 dòng: đang ở bước nào, đã xong gì, việc tiếp theo cần làm ngay là gì.
```
