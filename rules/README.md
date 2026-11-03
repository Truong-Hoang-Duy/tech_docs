# Hệ thống Quy tắc & Luồng Phối hợp Song phương: Gemini ⇄ Claude

Thư mục này định nghĩa quy trình làm việc tối ưu giữa **Bạn**, **Gemini**, và **Claude** trong dự án BookForge theo mô hình **Đối xứng & Kiểm duyệt chéo (Maker – Reviewer)**.

> **Nguyên tắc cốt lõi:** Không một AI nào tự lập kế hoạch rồi tự duyệt, hoặc tự code rồi tự nghiệm thu.
> - Nếu **Gemini** phân tích & lập Plan → **Claude** đối chiếu code thật để phản biện & duyệt (và ngược lại).
> - Nếu **Claude** chạy Plan (viết code) → **Gemini** kiểm tra `git diff` & nghiệm thu DoD (và ngược lại).

---

## 1. Cấu trúc thư mục `tech_docs/`

```text
tech_docs/
├── plans/                              # Nơi lưu hồ sơ từng tính năng/bug theo <slug>/
│   └── <slug>/
│       ├── 01-analysis.md              # Bước 1: Phân tích hiện trạng, nguyên nhân gốc & hướng giải quyết
│       └── 02-plan.md                  # Bước 2 & 3: Kế hoạch chi tiết + Mục Duyệt chéo + Tiến độ chạy Plan
└── rules/
    ├── README.md                       # Tổng quan & Bảng câu lệnh nhanh (file này)
    ├── 1_workflow.md                   # Quy trình tối ưu 3 bước: Phân tích → Plan & Duyệt chéo → Chạy Plan
    ├── 2_templates.md                  # Khuôn mẫu gọn nhẹ cho 01-analysis.md, 02-plan.md và Task Doc
    ├── 3_git-and-conventions.md        # Quy tắc Git, chuẩn code BE/FE và ràng buộc cách ly tech_docs
    ├── gemini/
    │   └── rules.md                    # Vai trò, thế mạnh, luật vận hành & câu lệnh giao việc cho Gemini
    └── claude/
        └── rules.md                    # Vai trò, thế mạnh, luật vận hành & câu lệnh giao việc cho Claude
```

---

## 2. Phân vai & Thế mạnh giữa Gemini và Claude

Cả **Gemini** và **Claude** đều làm việc trực tiếp trên workspace (`backend/` và `frontend/`), có đầy đủ quyền đọc/ghi file và chạy lệnh kiểm tra. Tuỳ bài toán, bạn có thể chọn bất kỳ bên nào làm **Người lập (Maker)** và bên còn lại làm **Người duyệt (Reviewer)**:

| Đặc điểm | **Gemini** | **Claude** |
|---|---|---|
| **Thế mạnh chính** | Quét ngữ cảnh rộng toàn repo (BE + FE), truy vết luồng dữ liệu liên tầng, phát hiện lệch hợp đồng API / UI state, phân tích nhanh và tổng hợp kiến trúc. | Điều hướng biểu tượng chính xác (Serena MCP), soi kỹ từng nhánh logic, cạnh tranh dữ liệu (concurrency/DB lock), bám sát quy ước code cục bộ và thi công phẫu thuật (surgical edits). |
| **Khi đóng vai Người lập (Maker)** | Khảo sát diện rộng, gom đủ các điểm chạm BE/FE, viết `01-analysis.md` và `02-plan.md` rõ ràng. | Đào sâu vào hàm/class cụ thể, thiết kế các bước sửa code chi tiết và an toàn trong `01-analysis.md` và `02-plan.md`. |
| **Khi đóng vai Người duyệt (Reviewer)** | Kiểm tra xem Plan/Code của Claude có bỏ sót ảnh hưởng dây chuyền sang màn hình FE, trang khác, hoặc luồng phụ thuộc nào không. | Mở từng `file:line` kiểm chứng lại giả định của Gemini, bắt lỗi edge-case, chống over-engineering và kiểm tra an toàn DB/transaction. |

---

## 3. Ma trận Phối hợp 3 Giai đoạn

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 1: PHÂN TÍCH (01-analysis.md)                                           │
│   Bạn nêu yêu cầu ──► [Agent A] khảo sát code thật, tìm nguyên nhân gốc (file:line)│
│                       & đề xuất giải pháp vào tech_docs/plans/<slug>/01-analysis.md│
├───────────────────────────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 2: LẬP PLAN & DUYỆT CHÉO (02-plan.md)                                   │
│   2.1 Lập Plan:  [Agent A] viết các bước thực thi + DoD vào 02-plan.md            │
│   2.2 Duyệt Plan:[Agent B] mở code thật đối chiếu, ghi mục "## Review" (🔴/🟡/🟢) │
│   2.3 Chốt Plan: Cập nhật 02-plan.md tới khi không còn lỗi 🔴 Blocker             │
├───────────────────────────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 3: CHẠY PLAN & NGHIỆM THU                                               │
│   3.1 Chạy Plan: [Agent Thực thi] code theo từng Step, chạy test, tick [x] vào Plan│
│   3.2 Nghiệm thu:[Agent Duyệt] soát git diff + chạy lại test để xác nhận hoàn tất │
└───────────────────────────────────────────────────────────────────────────────────┘
```

> **💡 Chế độ Gọn (Fast-Track) cho bug nhỏ / chỉnh sửa ≤ 3 file:**
> Không cần tách `01-analysis.md`. Yêu cầu Agent A gộp phần Phân tích + Kế hoạch vào **một file duy nhất** `tech_docs/plans/<slug>/02-plan.md`, sau đó cho Agent B duyệt và chạy luôn.

---

## 4. Bảng Câu lệnh Nhanh (Cheat Sheet)

Chỉ cần copy câu lệnh tương ứng và thay `<slug>` (hoặc mô tả yêu cầu):

### Bước 1 — Phân tích (`01-analysis.md`)
```text
Đọc tech_docs/rules/1_workflow.md và tech_docs/rules/2_templates.md (§1).
Khảo sát code thực tế cho yêu cầu sau và tạo file tech_docs/plans/<slug>/01-analysis.md:
<mô tả yêu cầu hoặc lỗi cần xử lý>
```

### Bước 2A — Tạo Plan (`02-plan.md`)
```text
Đọc tech_docs/plans/<slug>/01-analysis.md và tech_docs/rules/2_templates.md (§2).
Hãy lập kế hoạch triển khai chi tiết vào tech_docs/plans/<slug>/02-plan.md.
```
*(Nếu dùng **Fast-Track** từ đầu: `"Đọc tech_docs/rules/1_workflow.md (§2.2). Phân tích code và lập thẳng tech_docs/plans/<slug>/02-plan.md cho yêu cầu: ..."`)*.

### Bước 2B — Duyệt Plan chéo (Gửi cho Agent đối diện)
```text
Đọc tech_docs/rules/1_workflow.md (§3.2) và kiểm duyệt kế hoạch tại tech_docs/plans/<slug>/02-plan.md.
Hãy mở code thật trong repo để đối chiếu từng file:line, đánh giá rủi ro/edge-case và ghi kết quả (🔴/🟡/🟢) vào mục Review trong 02-plan.md. Chưa viết code tính năng.
```

### Bước 3A — Chạy Plan (Thi công)
```text
Đọc tech_docs/rules/1_workflow.md (§4.1) và tech_docs/rules/3_git-and-conventions.md.
Hãy triển khai đúng theo kế hoạch đã chốt tại tech_docs/plans/<slug>/02-plan.md, chạy kiểm tra tự động và cập nhật tiến độ [x] trực tiếp vào file đó.
```

### Bước 3B — Nghiệm thu Code chéo (Gửi cho Agent đối diện sau khi code xong)
```text
Đọc tech_docs/rules/1_workflow.md (§4.2) và tech_docs/plans/<slug>/02-plan.md.
Hãy đối chiếu với git status / git diff thực tế, chạy lại các lệnh test/lint và ghi kết luận nghiệm thu vào cuối file 02-plan.md.
```

### Bước 4 — Commit / Push (Chỉ khi bạn xác nhận)
```text
Commit (chưa push) các thay đổi của kế hoạch tech_docs/plans/<slug>/02-plan.md, tuân thủ nghiêm ngặt tech_docs/rules/3_git-and-conventions.md (§1).
```

