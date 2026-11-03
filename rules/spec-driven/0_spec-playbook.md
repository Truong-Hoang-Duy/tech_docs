# Sổ tay Thao tác Chat: Nghiệp vụ Spec ➔ Superpowers Plan ➔ Code

> **📌 Khi nào bật file này?**
> Bật cố định file này khi bạn triển khai các gói công việc **đã có sẵn tài liệu đặc tả (`specs/`)** trong `backend/docs/product/.../specs/` (ví dụ bộ **AI Governance MVP**: `pkg-01` đến `pkg-05`) và cần xuất kế hoạch thi công chuẩn vào `backend/docs/superpowers/plans/`.
> *(File này tách biệt hoàn toàn với `0_start-here.md` của luồng tính năng nhỏ lẻ thông thường).*

---

## 0. Bản đồ các Gói Spec (AI Governance MVP) & Gợi ý Phân vai

| Đợt / Gói | File Spec đầu vào (`backend/docs/product/ai-governance-mvp/specs/`) | Tên `<slug>` gợi ý | Gợi ý phân vai tối ưu |
|---|---|---|---|
| **Đợt A (Làm trước)** | `pkg-01-wave-a-identity-roles-and-file-governance.md` | `ai-governance-wave-a` | **Claude** quét & lập Plan ➔ **Gemini** duyệt Plan (vì Gemini rà 7 điểm upload FE rất mạnh) |
| **Đợt B** | `pkg-02-wave-b-command-guardrails-and-agent-policy.md` | `ai-governance-wave-b` | **Gemini** quét 25 điểm AI & lập Plan ➔ **Claude** duyệt sâu kiến trúc & chạy phần BE |
| **Đợt C** | `pkg-03-wave-c-output-provenance-and-traceability.md` | `ai-governance-wave-c` | **Claude** quét & lập Plan (nặng DB snapshot + đóng dấu file xuất) ➔ **Gemini** duyệt |
| **Release Gate** | `pkg-04-release-gate-humane-ux-and-acceptance.md` | `ai-governance-release-gate` | **Gemini** rà soát copy tiếng Việt & E2E ➔ **Claude** nghiệm thu 5 kịch bản `E2E-01..05` |

> **Hai tài liệu gốc luôn đi kèm mọi đợt:**
> - Quyết định kỹ thuật bắt buộc (`T1`–`T10`): `backend/docs/product/ai-governance-mvp/TECHNICAL_ALIGNMENT_DECISIONS.md`
> - Nguyên tắc nền tảng & Ranh giới Phase 2: `pkg-00-foundation-principles-and-decisions.md` và `pkg-05-phase2-horizon-and-architectural-invariants.md`

---

## 🔹 BƯỚC 1: Quét kiểm tra Spec đối chiếu với Code thật (`Spec-to-Code Audit`)

> **Mục đích:** Phát hiện mọi điểm lệch giữa tài liệu `specs/` và nhánh `dev` hiện tại (như trùng số thứ tự migration Alembic `0114`, thiếu đăng ký `ErrorCode` vào `catalog.py`, hàm đã đổi chữ ký, hoặc file FE sắp vượt 300 dòng) **trước khi** viết Plan.

**1. Mở khung chat của `Agent 1` (Gemini hoặc Claude), dán câu lệnh sau:**
*(Thay tên gói `pkg-01...` và `<slug>` tương ứng nếu làm đợt khác)*

```text
Đọc tech_docs/rules/spec-driven/1_audit-and-plan-rules.md (§1, §2) và tech_docs/rules/spec-driven/2_superpowers-templates.md (§1).
Hãy đọc kỹ:
1. backend/docs/product/ai-governance-mvp/TECHNICAL_ALIGNMENT_DECISIONS.md
2. backend/docs/product/ai-governance-mvp/specs/pkg-00-foundation-principles-and-decisions.md
3. backend/docs/product/ai-governance-mvp/specs/pkg-05-phase2-horizon-and-architectural-invariants.md
4. Gói mục tiêu: backend/docs/product/ai-governance-mvp/specs/<tên-file-pkg-XX.md>

Sau đó quét trực tiếp toàn bộ các file code thật liên quan trong backend/ và frontend/ để lập báo cáo kiểm tra độ lệch tại:
tech_docs/audits/<slug>-audit.md

Chưa tạo file superpowers plan và chưa sửa code. Hãy dừng lại và tóm tắt các điểm lệch quan trọng nhất phát hiện được.
```

**2. (Khuyên dùng) Nhờ `Agent 2` kiểm tra chéo bản Audit để không sót điểm chạm:**
Mở khung chat của `Agent 2` (người đối diện), dán:

```text
Đọc tech_docs/rules/spec-driven/1_audit-and-plan-rules.md (§2), file spec mục tiêu và báo cáo tại tech_docs/audits/<slug>-audit.md.
Hãy kiểm tra độc lập trên code thật (backend/ và frontend/) xem Agent 1 có bỏ sót file nào, điểm gọi nào, hoặc ràng buộc CI nào không.
Nếu phát hiện điểm thiếu, hãy bổ sung trực tiếp vào tech_docs/audits/<slug>-audit.md và tóm tắt ngắn gọn cho tôi.
```

---

## 🔹 BƯỚC 2: Tạo Kế hoạch Thi công chuẩn Superpowers (`backend/docs/superpowers/plans/`)

Khi bản quét `tech_docs/audits/<slug>-audit.md` đã chuẩn xác:

**Quay lại khung chat của `Agent 1`, dán câu lệnh sau:**

```text
Đọc tech_docs/rules/spec-driven/1_audit-and-plan-rules.md (§3) và tech_docs/rules/spec-driven/2_superpowers-templates.md (§2).
Dựa trên file Spec mục tiêu và kết quả quét thực tế tại tech_docs/audits/<slug>-audit.md, hãy tạo file Implementation Plan chuẩn Superpowers tại:
backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md

Lưu ý bắt buộc:
- Chia thành các Task 1..N theo đúng chu trình TDD 4 bước có checkbox (- [ ] Step 1..4).
- Áp dụng toàn bộ các hiệu chỉnh độ lệch đã phát hiện trong file audit (số migration, ErrorCode catalog, giới hạn 300 dòng FE...).
- Cập nhật bảng "4. Ma trận Ánh xạ Tiêu chí Nghiệm thu (AC -> Task)" trong tech_docs/audits/<slug>-audit.md.
- Tuyệt đối KHÔNG chứa chuỗi "tech_docs" trong file nằm ở backend/docs/superpowers/plans/.
Chưa viết code tính năng.
```

---

## 🔹 BƯỚC 3: Duyệt chéo Superpowers Plan (`Plan Cross-Review` — Gemini ⇄ Claude)

> Nếu **Claude** vừa tạo Plan ở Bước 2 ➔ Mở **Gemini** để duyệt.
> Nếu **Gemini** vừa tạo Plan ở Bước 2 ➔ Mở **Claude** để duyệt.

**Dán câu lệnh sau vào khung chat của `Agent 2`:**

```text
Đọc tech_docs/rules/spec-driven/1_audit-and-plan-rules.md (§3.2).
Hãy kiểm duyệt chéo kế hoạch tại backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md bằng cách đối chiếu 3 bên:
1. Tài liệu gốc trong backend/docs/product/ai-governance-mvp/specs/<tên-file-pkg-XX.md> và TECHNICAL_ALIGNMENT_DECISIONS.md
2. Báo cáo quét tại tech_docs/audits/<slug>-audit.md
3. Các file code thật trong backend/ và frontend/

Yêu cầu:
- Ghi toàn bộ nhận xét (🔴 Blocker / 🟡 Should-fix / 🟢 Nit) vào mục "## 5. Nhật ký Duyệt Superpowers Plan" bên trong file tech_docs/audits/<slug>-audit.md.
- Nếu có điểm 🔴 hoặc 🟡 cần sửa, hãy hiệu chỉnh trực tiếp vào các Task trong backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md (nhớ giữ quy tắc cấm nhắc chữ tech_docs trong file của backend) và chốt trạng thái APPROVED trong file audit. Chưa viết code tính năng.
```

---

## 🔹 BƯỚC 4: Chạy Plan theo từng Cụm Task (`Execute Tasks`)

Vì một gói `pkg-XX` thường có nhiều Task (cả BE lẫn FE), bạn có thể cho chạy toàn bộ hoặc chia theo từng cụm Task (ví dụ: *Chạy các Task Backend trước ➔ Chạy các Task Frontend sau*) để AI làm cực kỳ chắc chắn.

### Cách A: Chạy theo Cụm Task (Khuyên dùng cho các gói lớn như Đợt A, B, C)
Dán vào Agent bạn chọn để code (VD: **Claude** cho cụm Task BE, **Gemini** cho cụm Task FE):

```text
Đọc tech_docs/rules/spec-driven/1_audit-and-plan-rules.md (§4.1) và tech_docs/rules/3_git-and-conventions.md.
Hãy thực thi các Task từ Task <X> đến Task <Y> trong kế hoạch đã duyệt tại:
backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md
(tham chiếu thêm lưu ý tại tech_docs/audits/<slug>-audit.md).

Quy tắc bắt buộc:
- Đi đúng thứ tự từng Task (Step 1 viết test -> Step 2 chạy xác nhận fail -> Step 3 viết code -> Step 4 chạy test & lint pass).
- Hoàn thành Step nào thì tick [x] trực tiếp vào Step đó trong backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md.
- Ghi tóm tắt kết quả chạy test/lint vào mục "## 6. Nhật ký Thực thi" trong tech_docs/audits/<slug>-audit.md.
- Không tự ý git commit.
```

### Cách B: Chạy toàn bộ các Task còn lại trong Plan
```text
Đọc tech_docs/rules/spec-driven/1_audit-and-plan-rules.md (§4.1) và tech_docs/rules/3_git-and-conventions.md.
Hãy thực thi lần lượt toàn bộ các Task chưa hoàn thành (`- [ ]`) trong backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md.
Xong Step nào chạy test/lint xác nhận xanh rồi tick [x] vào file Plan, đồng thời ghi nhật ký vào mục "## 6. Nhật ký Thực thi" của tech_docs/audits/<slug>-audit.md. Không tự ý git commit.
```

---

## 🔹 BƯỚC 5: Nghiệm thu Code chéo (`Cross-Verify`) & Kiểm tra Tiêu chí `AC-XX-*`

Sau khi các Task đã được tick `[x]`, **chuyển sang khung chat của `Agent đối diện` (người không viết code ở Bước 4)** và dán:

```text
Đọc tech_docs/rules/spec-driven/1_audit-and-plan-rules.md (§4.2), file backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md và tech_docs/audits/<slug>-audit.md.
Hãy thực hiện nghiệm thu độc lập:
1. Chạy git status / git diff trên cả backend/ và frontend/ để đối chiếu với từng Task trong Plan và các tiêu chí AC trong Spec.
2. Kiểm tra chắc chắn không có bất kỳ chuỗi "tech_docs" nào lọt vào các file trong backend/ hoặc frontend/.
3. Chạy lại bộ lệnh kiểm tra (ruff, pytest, test_errors_catalog, build/typecheck FE, độ dài file FE <= 300 dòng).
4. Ghi kết luận nghiệm thu vào mục "## 7. Kết quả Nghiệm thu Code" trong tech_docs/audits/<slug>-audit.md và hướng dẫn tôi các bước kiểm tay trên giao diện (nếu có).
```

---

## 🔹 BƯỚC 6: Commit & Push

Khi kết luận nghiệm thu trong `tech_docs/audits/<slug>-audit.md` đã đạt `VERIFIED`:

**Chỉ Commit ở máy local:**
```text
Commit (chưa push) các thay đổi đã nghiệm thu của gói <slug> trên repo tương ứng (backend/ và/hoặc frontend/), tuân thủ nghiêm ngặt tech_docs/rules/3_git-and-conventions.md (§1).
```

**Commit và Push lên nhánh:**
```text
Commit và push các thay đổi đã nghiệm thu của gói <slug> trên repo tương ứng (backend/ và/hoặc frontend/), tuân thủ nghiêm ngặt tech_docs/rules/3_git-and-conventions.md (§1).
```

---

## 💡 Câu lệnh Cứu hộ nhanh (Khi đổi phiên chat giữa chừng)

Nếu đang chạy dở một gói `superpowers/plans/` mà bạn mở phiên chat mới hoặc đổi giữa Gemini và Claude, chỉ cần dán:

```text
Đọc backend/docs/superpowers/plans/YYYY-MM-DD-<slug>.md và tech_docs/audits/<slug>-audit.md, kiểm tra git status ở cả backend/ và frontend/, rồi tóm tắt trong 5 dòng:
1. Những Task nào đã hoàn thành ([x])?
2. Đang dừng ở Task/Step nào?
3. Bước tiếp theo cần chạy ngay là gì?
```
