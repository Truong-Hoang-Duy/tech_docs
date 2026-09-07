# Quy ước & Luồng làm việc AI (AI Rules & Workflows)

Thư mục này chứa các tài liệu quy chuẩn, quy trình phối hợp và hướng dẫn hành động khi làm việc cùng các trợ lý AI (Gemini, Claude) trong hệ sinh thái BookForge.

---

## 1. Cấu trúc thư mục

```text
tech_docs/rules/
├── gemini/                         # Quy trình dành riêng cho Gemini (Google Antigravity / Gemini CLI)
│   └── gemini-workflow.md          # Quy trình hợp nhất (Nghiên cứu + Thiết kế + Task Spec + Thi công + Git)
├── claude/                         # Quy trình dành riêng cho Claude (Claude Web ↔ Claude Code)
│   ├── 1_start-here.md             # Sổ tay thao tác hằng ngày của Claude
│   ├── 2_web-code-handoff.md        # Giao thức bưng file qua lại giữa Web và Code
│   └── 3_git-workflow-rules.md     # Quy tắc thao tác Git của Claude
├── docs-convention.md              # [DÙNG CHUNG] Quy ước tài liệu toàn dự án (áp dụng cho mọi AI & Developer)
└── technical-spec-template.md      # [DÙNG CHUNG] Mẫu khung soạn thảo đặc tả kỹ thuật (Technical Spec)
```

---

## 2. Chọn luồng làm việc

| Bạn đang dùng | Đọc tài liệu nào | Đặc điểm mô hình |
|---|---|---|
| **Gemini** (Google Antigravity, Gemini CLI / IDE) | [`gemini/gemini-workflow.md`](gemini/gemini-workflow.md) | **Hợp nhất 1 luồng (All-in-one)**: Context lớn (1M+ tokens), đọc repo trực tiếp, kiêm nhiệm cả nghiên cứu, thiết kế, lập task và code trong cùng 1 phiên. |
| **Claude** (Claude Web + Claude Code) | [`claude/1_start-here.md`](claude/1_start-here.md) | **Chia 2 vai (Web ↔ Code)**: Web nghĩ/giải thích rẻ nhưng không thấy code; Code đọc/viết repo nhưng token đắt. Người dùng chuyển file qua lại. |

---

## 3. Quy chuẩn tài liệu chung

Dù dùng Gemini hay Claude, mọi tài liệu tạo ra trong dự án phải tuân thủ nghiêm ngặt:
- [`docs-convention.md`](docs-convention.md): Quy ước vị trí đặt file (`backend/docs/tasks/`, `api/`, `architecture/`), chuẩn định dạng (tiếng Việt, không YAML frontmatter, sơ đồ ASCII).
- **Ràng buộc cứng:** Mọi task doc commit vào `bookforge` hoặc `bookforge-fe` tuyệt đối không chứa đường dẫn `tech_docs/` vì người nhận task chỉ có repo code, không có repo tài liệu nghiên cứu.
