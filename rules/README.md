# Quy ước & Luồng làm việc AI (AI Rules & Workflows)

Thư mục này chứa quy chuẩn tài liệu và quy trình làm việc cùng AI trong hệ sinh thái BookForge.

**Một luồng duy nhất: Claude Code.** Nó đọc repo, viết tài liệu, viết code — và là nơi duy nhất được ghi.
**Gemini là trợ lý tra cứu read-only**, dùng để giữ hạn mức Claude cho việc ghi: đọc hộ, giảng lại, quét khoanh vùng, tra tài liệu ngoài. Không ghi file, không sửa code, không git.

---

## 1. Cấu trúc thư mục

```text
tech_docs/rules/
├── claude/                         # Luồng làm việc chính
│   ├── 1_start-here.md             # Sổ tay thao tác hằng ngày — đọc file này trước
│   ├── 2_workflow-rules.md         # Luật chi tiết + khuôn mẫu tài liệu (00-desc, 01-brief, 02-findings, 03-design, qa, status)
│   └── 3_git-workflow-rules.md     # Quy tắc thao tác Git
├── gemini-assist.md                # Vai trợ lý tra cứu read-only + prompt mẫu
└── docs-convention.md              # [DÙNG CHUNG] Quy ước tài liệu toàn dự án
```

---

## 2. Ai làm gì

| | Được làm | Không được làm |
|---|---|---|
| **Claude Code** | Khảo sát repo, viết `research/`, viết task doc, viết code, cập nhật bản đồ | Commit/push khi chưa được cho phép |
| **Gemini** | Đọc code, giải thích, khoanh vùng, tra tài liệu ngoài, phản biện — **trả lời trong chat** | Ghi/sửa bất kỳ file nào, sửa code, mọi thao tác git |

Mọi thứ Gemini nói là **giả thuyết** cho tới khi Claude Code mở file ra xác nhận bằng `file:line`. Bưng kết quả về bằng khối có nhãn `[TỪ GEMINI — CHƯA KIỂM CHỨNG]` — xem [`claude/2_workflow-rules.md`](claude/2_workflow-rules.md) §6.

---

## 3. Bắt đầu từ đâu

1. Làm việc hằng ngày → [`claude/1_start-here.md`](claude/1_start-here.md)
2. Cần tra khuôn mẫu (`00-desc` §8, `01-brief` §9, `02-findings` §10, `03-design` §17, `qa` §12, `status` §13) → [`claude/2_workflow-rules.md`](claude/2_workflow-rules.md)
3. Muốn nhờ Gemini đọc hộ → [`gemini-assist.md`](gemini-assist.md)

---

## 4. Quy chuẩn tài liệu chung

Mọi tài liệu tạo ra trong dự án phải tuân thủ nghiêm ngặt:
- [`docs-convention.md`](docs-convention.md): quy ước vị trí đặt file (`backend/docs/tasks/`, `api/`, `architecture/`), chuẩn định dạng (tiếng Việt, không YAML frontmatter, sơ đồ ASCII).
- **Ràng buộc cứng:** mọi task doc commit vào `bookforge` hoặc `bookforge-fe` tuyệt đối không chứa đường dẫn `tech_docs/` — người nhận task chỉ có repo code, không có repo tài liệu nghiên cứu.
