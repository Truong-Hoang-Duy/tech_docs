# Câu lệnh mẫu

Copy câu lệnh, thay `<slug>` và các chỗ `<...>`, rồi dán vào khung chat của agent đã chọn cho việc này. Mọi bước của một việc đều gửi cho cùng một agent.

---

## 0. Chỉ tìm hiểu một chức năng (chưa làm gì)

```text
Lấy code mới nhất theo tech_docs/README.md mục 8, chưa tạo hay sửa file nào.
Tìm hiểu chức năng: "<mô tả bằng lời thường>" rồi trả lời ngay trong chat:
1. Luồng từ lúc người dùng bấm trên giao diện → gọi tới đâu ở backend → lưu vào đâu (kèm file:dòng).
2. Có điều kiện phân quyền hay cờ bật/tắt nào đang khoá chức năng này không?
3. Giới hạn hiện tại hoặc chỗ dễ lỗi là gì?
Giải thích ngắn gọn, dễ hiểu.
```

---

## 1. Tìm hiểu

**Việc thường:**
```text
Đọc tech_docs/README.md và tech_docs/templates.md. Lấy code mới nhất (mục 8). Chưa sửa code.
Trước khi tạo file, hỏi tôi: chỉ plan hay plan + spec, kèm một câu lời khuyên, rồi chờ tôi trả lời.
- Chỉ plan: lập thẳng tech_docs/tasks/<slug>/plan.md (ghi hiện trạng vào mục 1), kiểm kế hoạch theo README mục 5 rồi báo tôi và dừng.
- Plan + spec: tạo tech_docs/tasks/<slug>/analysis.md, viết mục 0 cho người không đọc code. Mở lại code và yêu cầu gốc để kiểm, rồi báo tôi ngắn gọn bằng lời thường và các điều cần tôi quyết.
Slug: <tên bạn chọn | để trống: AI tự đặt theo README mục 9 và báo lại>
Yêu cầu:
- Lỗi: <ở màn hình nào, vai trò gì · bấm gì · thấy gì · mong đợi gì>
- Hoặc tính năng: <ai dùng · muốn làm được gì · kết quả mong muốn · phần không làm>
```

**Việc có spec:**
```text
Đọc tech_docs/README.md, tech_docs/spec-check.md và mẫu analysis trong tech_docs/templates.md. Lấy code mới nhất (mục 8) và tạo tech_docs/tasks/<slug>/analysis.md. Chưa sửa code.
Kiểm spec theo 3 lớp của spec-check.md, nghiệp vụ trước. Chỗ nghi sai ghi lại để tôi chốt, không tự sửa spec.
Viết mục 0 cho người không đọc code: spec này sẽ làm gì. Mở lại code và spec để kiểm, rồi báo tôi ngắn gọn bằng lời thường và các điều cần tôi quyết.
Slug: <tên bạn chọn | để trống: AI tự đặt theo README mục 9 và báo lại>
Spec: <đường dẫn tới spec>
Tài liệu gốc (nếu có): <đường dẫn | để trống: chỉ dùng spec>
Phạm vi lần này: <cả gói | chỉ phần … | "Làm theo đúng spec">
Lưu ý thêm (nếu có): <thứ tự ưu tiên, phần tạm chưa làm…>
```

**Chốt sau khi đọc mục 0 của `analysis.md`:**
```text
Chốt các điều trong mục "Bạn cần quyết" của tech_docs/tasks/<slug>/analysis.md:
- <điều 1>: <a | b | theo lời khuyên của bạn | cách khác: …>
- <điều 2>: <…>
Điều nào tôi không nêu: làm theo lời khuyên của bạn.
Ghi vào "Bạn chốt" và cập nhật analysis.md. Chưa lập kế hoạch.
```

---

## 2–3. Lập kế hoạch và kiểm kế hoạch

```text
Đọc tech_docs/README.md (mục 4, 5), mẫu plan trong tech_docs/templates.md và tech_docs/tasks/<slug>/analysis.md.
Lập kế hoạch vào tech_docs/tasks/<slug>/plan.md. Chưa sửa code.
Chia Task theo phần tôi bấm thử được, mỗi Task có tiêu chí đạt. Không viết sẵn code trong kế hoạch.
Đưa mọi điều tôi đã chốt vào "Quyết định đã chốt". Việc có spec: làm thêm theo spec-check.md mục 3.
Xong thì kiểm 4 điều ở README mục 5 bằng cách mở code và chạy lệnh thật, sửa chỗ sai.
Hết chỗ sai và hết việc cần tôi quyết thì chốt APPROVED; ngược lại giữ DRAFT.
Báo tôi bằng lời thường: đã sửa gì, còn bao nhiêu việc cần tôi quyết. Dừng ở đây.
```

**Sau khi bạn quyết các việc còn lại:**
```text
Tôi chốt: <điều 1: …> · <điều 2: …>.
Cập nhật tech_docs/tasks/<slug>/plan.md theo các điều này, mở lại code kiểm phần vừa sửa.
Hết chỗ sai và hết việc cần tôi quyết thì chốt APPROVED. Báo tôi và dừng, chưa sửa code.
```

---

## 4. Làm (mở phiên mới)

```text
Đọc tech_docs/README.md (mục 4, 6, 8, 11) và tech_docs/tasks/<slug>/plan.md đã APPROVED.
Trước khi sửa code, làm đúng các bước ở README mục 8. Có thay đổi dở dang thì dừng, báo tôi.
Làm lần lượt từng Task, bắt đầu từ <Task 1 | Task X>. Mỗi Task: code, chạy kiểm tra, tự bấm thử theo tiêu chí, ghi kết quả vào manual-test.md và Nhật ký, rồi dừng và hướng dẫn tôi kiểm.
Chỉ sang Task sau khi tôi báo đạt. Không tự sửa tiêu chí hay xóa test. Không commit.
```

**Task đạt:**
```text
Task <số> đạt. Đánh dấu [x] và làm Task tiếp theo.
```

**Task không đạt:**
```text
Task <số>, bước <số>: <thấy gì>. (Kèm ảnh nếu có.)
Tìm nguyên nhân, ghi vào manual-test.md. <Được phép sửa | Chưa sửa, báo tôi trước>.
```

**Khi AI dừng lại hỏi giữa chừng:**
```text
Làm theo hướng <X>. Ghi vào mục Quyết định phát sinh trong plan.md rồi làm tiếp.
```

---

## 5. Nghiệm thu

```text
Cập nhật nhánh theo origin/dev mới nhất. Đọc lại toàn bộ diff, đối chiếu từng thay đổi với tech_docs/tasks/<slug>/plan.md và từng nghiệp vụ ở mục 3.0 của analysis.md (nếu có).
Chạy lại toàn bộ kiểm tra như CI và ghi kết luận vào mục Nghiệm thu của plan.md, dán lệnh và dòng kết quả cuối.
```

---

## 6. Kiểm tay toàn bộ

```text
Đọc tech_docs/README.md mục 6. Thêm vào manual-test.md các kịch bản chung liên quan (kịch bản của Task giữ nguyên). Việc có spec: phủ các nghiệp vụ ở mục 3.0 của analysis.md.
Tự bấm thử mọi kịch bản trước (không có công cụ điều khiển trình duyệt thì báo tôi), rồi hướng dẫn tôi từng kịch bản một. Chưa sửa code khi tôi chưa cho phép.
```

**Kiểm xong:**
```text
Tôi đã kiểm xong, các kịch bản đều Đạt. Ghi kết quả và Số đo, đổi trạng thái plan.md sang VERIFIED.
```

---

## 7. Lưu spec và commit

**Việc thường, chỉ plan:**
```text
Đọc tech_docs/README.md mục 7, 8. Commit <(chưa push) | và push> các thay đổi của việc này, message ghi rõ lý do. Ghi mã commit vào mục Commit của tech_docs/tasks/<slug>/plan.md.
```

**Việc thường, plan + spec:**
```text
Đọc tech_docs/README.md mục 7, 8 và mẫu spec ngắn trong tech_docs/templates.md.
Tạo spec backend/docs/superpowers/specs/YYYY-MM-DD-<slug>.md, ghi đúng những gì đã làm thật.
Báo tôi spec vừa tạo và chờ tôi đồng ý, rồi mới commit <(chưa push) | và push>. Ghi đường dẫn spec và mã commit vào mục Commit của plan.md.
```

**Việc có spec:**
```text
Đọc tech_docs/README.md mục 8 và tech_docs/spec-check.md mục 4. Cập nhật spec <đường dẫn spec> theo đúng mục đó.
Báo tôi danh sách chỗ đã sửa và chờ tôi đồng ý, rồi mới commit <(chưa push) | và push>. Ghi các chỗ sửa spec và mã commit vào mục Commit của plan.md.
```

---

## Cứu hộ (mất phiên chat, đổi máy, hôm sau làm tiếp)

```text
Đọc các file trong tech_docs/tasks/<slug>/, kiểm tra git status và git log gần đây ở backend/ và frontend/,
rồi tóm tắt trong 5 dòng: đang ở bước nào, đã xong gì, việc tiếp theo cần làm ngay là gì.
```

---

## Xem lại luật (sau khoảng 10 việc)

```text
Đọc tech_docs/README.md và mục Số đo trong các plan.md ở tech_docs/tasks/. Điền số lần phải sửa sau merge từ git log.
Tóm tắt các số đo, chỉ ra bước nào tốn thời gian mà không bắt được lỗi, và đề xuất bỏ hoặc sửa gì. Chưa sửa luật khi tôi chưa đồng ý.
```
