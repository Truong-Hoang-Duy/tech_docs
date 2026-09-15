# Giao thức làm việc trong repo — Claude Code

> **📌 Cách dùng file này:** đây là **luật chi tiết** cho vòng lặp "mô tả → khảo sát → thiết kế → task doc → thi công".
> Mọi việc đọc repo, viết tài liệu và viết code đều do **một vai duy nhất: Claude Code**. Không còn vai "web", không còn bưng file qua lại.
> **Gemini là trợ lý tra cứu read-only**: đọc hộ, giải thích, quét rộng, tra tài liệu ngoài — **không ghi file, không sửa code, không git**. Ranh giới ở §6, prompt mẫu ở [`../gemini-assist.md`](../gemini-assist.md).
> Trong Claude Code chỉ gõ những câu ở §7. **Chỉ cần biết làm gì mỗi ngày thì đọc [`1_start-here.md`](1_start-here.md)** — file này mở khi cần tra khuôn mẫu.

---
## 1. Phân vai

| | **Bạn** | **Claude Code** (trong repo) | **Gemini** (trợ lý tra cứu) |
|---|---|---|---|
| Có gì | Ý đồ sản phẩm, quyền quyết định | **Sự thật của repo**: file, dòng, schema, test — và quyền ghi | Context lớn, hạn mức rẻ, tra được tài liệu ngoài repo |
| Không có gì | Không thuộc cấu trúc code — **không cần thuộc** | Token đắt; đọc lan man rất tốn | **Không ghi file, không sửa code, không git**; nói gì cũng chưa được kiểm chứng |
| Việc | Mô tả nghiệp vụ, chốt phương án | Khảo sát, thiết kế, viết task doc, viết code, cập nhật tài liệu | Đọc hộ, giảng lại, quét khoanh vùng, tra thư viện, phản biện |

Ba nguyên tắc, vi phạm cái nào cũng sinh ra một vòng lặp thừa:

> **Bạn không cần biết tên kỹ thuật.** Mô tả "chỗ hiện danh sách đề thi", đừng cố nhớ tên component.
> **Chỉ Claude Code được ghi.** Mọi file trong `research/`, `backend/docs/tasks/` và mọi dòng code đều do Claude Code viết — để chỉ có một nguồn sự thật và một lịch sử sửa.
> **Gemini nói gì cũng là giả thuyết.** Chưa có `file:line` do Claude Code tự mở ra đọc và xác nhận thì không được vào `02-findings.md`, `03-design.md` hay task doc (§6).
## 2. Ba giai đoạn và nhịp hằng ngày

```text
NHỊP HẰNG NGÀY — mỗi sáng, một câu gõ (§3)
[Code] ─► quét ref BẠN CHỈ ĐỊNH → cập nhật overview/1_repo-map.md + 2_backend-features-all.md
             └─► in ra 5–10 dòng "hôm nay đổi gì" để bạn nắm, và để dán cho Gemini khi cần

GIAI ĐOẠN 1 — KHẢO SÁT
[Bạn]  ─► tech_docs/research/00-desc.md      Mô tả nháp bằng lời thường (§8)
   │
[Code] ─► research/<slug>/00-desc.md         Chuẩn hoá lời văn, tự đặt slug, tạo thư mục,
   │                                         chuyển file vào — RỒI DỪNG cho bạn duyệt (§8)
   │         └─ bạn đọc, sửa hoặc bảo tôi sửa; ổn rồi mới sang bước sau
   │
[Code] ─► 01-brief.md       Câu hỏi khảo sát + giả định cần kiểm chứng — VẪN CHƯA đọc code (§9)
   │         └─ bạn duyệt: tôi sắp lục ở đâu, đang tin điều gì
   │         └─ không hiểu thuật ngữ → nhờ Gemini giải nghĩa (§6)
   │         └─ (tuỳ chọn) đưa brief cho Gemini quét khoanh vùng — dán về kèm nhãn (§6)
   │
[Code] ─► 02-findings.md    Hiện trạng có bằng chứng file:line, chốt phía nào phải sửa (§10)
   │         └─ bạn duyệt; khó nuốt thì nhờ Gemini tóm tắt và soi chỗ thiếu bằng chứng (§6)

GIAI ĐOẠN 2 — THIẾT KẾ & CHỐT
[Code] ─► 03-design.md      Hai phương án + đánh đổi + kế hoạch (§17)
   │         └─ BẠN tranh luận ngay tại đây; chỗ nào không hiểu thì nhờ Gemini giảng (§6)
   │
[Code] ─► backend/docs/tasks/YYYY-MM-DD-<slug>.md          (phần BE)
          backend/docs/tasks/YYYY-MM-DD-<slug>-frontend.md (phần FE, nếu có)

GIAI ĐOẠN 3 — THI CÔNG      vòng lặp ngắn, lặp nhiều lần (§12)
[Code] viết code ─► gặp ràng buộc / cần bạn quyết ─► viết câu hỏi TỰ CHỨA
   │                              └─ bạn tự chốt, hoặc dán sang Gemini cho nó giảng rồi chốt
   │
   └─► ghi vào qa.md  +  cập nhật "Quyết định đã chốt" của task doc

XUYÊN SUỐT: status.md giữ ngữ cảnh để hồi phục khi mất phiên hoặc hết hạn mức (§13)
```

Giai đoạn 1–2 giờ **đi thẳng một mạch**: cùng một agent vừa đọc repo vừa dựng phương án, không còn vòng bưng file qua lại. Chỗ tốn thời gian của bạn dồn vào đúng một việc — **đọc `03-design.md` và chốt**. Giai đoạn 3 lặp bao nhiêu lần cũng được.
## 3. Nhịp hằng ngày — cập nhật bản đồ từ nhánh bạn chỉ định

Code đổi liên tục, bản đồ cũ làm cả bạn lẫn Gemini hỏi trật chỗ. Mỗi sáng gõ **một câu** ở §7, **kèm nhánh muốn lấy**.

**Nguồn quét — bạn chọn, không mặc định `dev`:**

| Bạn ghi | Nghĩa |
|---|---|
| `origin/dev`, `origin/main`, `origin/<bất kỳ>` | Nhánh trên remote, đã `fetch` về |
| `feat/geometry-editor` (nhánh local) | Commit mới nhất của nhánh đó, kể cả chưa push |
| `working` | **Thư mục làm việc hiện tại**, tính cả thay đổi chưa commit |
| *(bỏ trống)* | Dùng lại đúng ref ghi ở header `1_repo-map.md` lần trước |

Hai repo có thể lấy từ hai nhánh khác nhau — ghi rõ khi cần:
`bookforge=origin/dev, bookforge-fe=feat/abc`. Ghi một ref duy nhất thì áp cho cả hai.

**Ràng buộc cứng khi tôi chạy việc này:** không `checkout`, không `pull`, không `stash`, không đụng nhánh bạn đang làm.
Với ref là nhánh, tôi chỉ `fetch` rồi đọc qua một **worktree tạm** trong scratchpad và xoá ngay sau khi quét.
Với `working`, tôi đọc thẳng thư mục làm việc, không tạo worktree.

Các bước:

0. **Kiểm migration DB local theo §18** — trước cả bước 1, kể cả khi diff rỗng.
1. `git -C <repo> fetch origin <nhánh>` — bỏ qua nếu ref là nhánh local hoặc `working`.
2. Đọc SHA cơ sở ở header hai file map, chạy `git diff --stat <sha cơ sở>..<ref>` cho từng repo.
3. **Diff rỗng cả hai repo** → chỉ sửa lại ngày trong header, báo "không đổi", dừng. Gần như 0 token.
4. **Diff nhỏ** → `git worktree add --detach <scratchpad>/map-<repo> <ref>`, quét **đúng vùng bị đụng**, sửa những dòng đã lệch trong map, rồi `git worktree remove`.
5. **Sinh lại toàn bộ** khi: diff đụng hơn 60 file, hoặc bản đồ quá 14 ngày, hoặc cấu trúc thư mục đổi, hoặc **ref lần này nằm khác nhánh với ref lần trước** (diff giữa hai nhánh rẽ nhau thường vô nghĩa để vá từng dòng).
6. In ra terminal **5–10 dòng "đổi gì từ lần trước"**, có ghi rõ **quét từ ref nào**, để bạn nắm và dán bổ sung khi đang hỏi Gemini dở. **Không lưu thành changelog trong file** — `docs-convention.md` §1.3 ghi rõ docs dự án không có mục changelog.

Hai lưu ý khi đổi ref:

- Quét từ `origin/dev` thì **những gì bạn vừa làm trên nhánh riêng chưa merge sẽ không có trong bản đồ**. Muốn thấy, quét từ chính nhánh đó hoặc từ `working`.
- Quét từ `working` cho bản đồ khớp nhất với cái bạn đang sửa, nhưng mốc SHA kèm hậu tố `+dirty` và **không dùng để tính diff lần sau được** — lần sau nên nêu lại ref rõ ràng.

Cập nhật file nào:

- `1_repo-map.md` — khi diff chạm `api/`, `models/`, `workers/`, `cron/`, `core/settings.py`, `services/features.py`, hoặc phía FE là `src/App.tsx`, `src/api/`.
- `2_backend-features-all.md` — **chỉ khi có tính năng mới hoặc luồng đổi bản chất**. Đổi tên biến, refactor nội bộ thì không đụng tới nó.

Header hai file map luôn ghi SHA nguồn, đây là mốc để tính diff lần sau:

```text
> Nguồn: bookforge@<sha> (<nhánh>) · bookforge-fe@<sha> (<nhánh>) — <YYYY-MM-DD>.
```

**`1_repo-map.md` chứa gì** (dùng khi sinh lại toàn bộ): bảng endpoint theo router · bảng dữ liệu (bảng → model → khoá ngoại) · route FE → component → tầng API · job nền và cron kèm nơi gọi · feature flag · biến môi trường theo nhóm · **mục "vùng chưa lập bản đồ"**.
Mỗi mục **một dòng** — đây là mục lục, không phải tài liệu thiết kế.

## 4. Gói ngữ cảnh — chỉ dùng khi hỏi Gemini

Claude Code **không cần** gói này: nó tự mở repo ra đọc. Gói này chỉ dùng khi bạn hỏi Gemini ở nơi không thấy repo (Gemini web / AI Studio), hoặc muốn khoanh vùng để Gemini khỏi quét lan man.

| Phía làm | Dán cho Gemini |
|---|---|
| Chỉ BE | `1_repo-map.md` §1,2,3,5,6,7 + `2_backend-features-all.md` |
| Chỉ FE | `1_repo-map.md` §4 + `frontend/CONVENTION.md` |
| Cả hai, hoặc chưa rõ | Cả hai file, đầy đủ |

| File | Trả lời câu hỏi |
|---|---|
| [`overview/2_backend-features-all.md`](../../overview/2_backend-features-all.md) | *Hệ thống làm được những gì, logic nằm ở module nào* |
| [`overview/1_repo-map.md`](../../overview/1_repo-map.md) | *Có những endpoint / bảng / màn hình / job / env nào* |
| [`frontend/CONVENTION.md`](../../frontend/CONVENTION.md) | *Quy ước đặt tên và giới hạn kích thước file FE* |

Cả hai bản đồ đều là **mục lục**: đủ để hỏi trúng chỗ, không đủ để kết luận code chạy thế nào. Gemini chạy thẳng trong IDE thì bỏ qua mục này — chỉ cần chỉ đúng thư mục cần đọc và cấm nó ghi (§6).
## 5. Nơi đặt file

Mỗi tính năng một thư mục `tech_docs/research/<feature-slug>/`, đánh số tăng dần như `research/canvas-agent-geometry/`.

**Trước khi có thư mục:** bạn để bản nháp ở `tech_docs/research/00-desc.md` (ngay gốc `research/`, không nằm trong thư mục con). Claude Code chuẩn hoá, đặt slug rồi chuyển nó vào `research/<slug>/00-desc.md` — xem §8. Gốc `research/` không bao giờ giữ lại file lẻ nào sau bước đó.

| File | Ai viết | Nội dung |
|---|---|---|
| `status.md` | **Claude Code** | Ngữ cảnh cô đọng để hồi phục khi mất phiên (§13) — không đánh số, luôn ở đầu |
| `00-desc.md` | **Bạn** viết nháp → **Claude Code** chuẩn hoá | Mô tả nghiệp vụ, phía, ràng buộc, cái không làm (§8) |
| `01-brief.md` | **Claude Code** | Câu hỏi khảo sát + giả định cần kiểm chứng — **bạn duyệt trước khi tôi đọc code** (§9) |
| `02-findings.md` | **Claude Code** | Hiện trạng có bằng chứng (§10) |
| `03-design.md` | **Claude Code** | Phương án, đánh đổi, kế hoạch (§17) — bạn tranh luận trực tiếp trên file này |
| `04-…`, `05-…` | **Claude Code** | Vòng khảo sát / thiết kế bổ sung nếu còn câu hỏi mở |
| `qa.md` | **Claude Code** + bạn | Nhật ký hỏi–đáp lúc thi công (§12) |

Quy ước áp dụng: tên file `kebab-case`, tiếng Việt, không frontmatter, sơ đồ ASCII — xem [`docs-convention.md`](../docs-convention.md).
`tech_docs/research/` là **nháp nghiên cứu**; bản chốt luôn kết thúc ở `backend/docs/tasks/`.

**Task doc — nơi đặt theo phía:**

| Phía | File |
|---|---|
| BE | `backend/docs/tasks/YYYY-MM-DD-<slug>.md` |
| FE | `backend/docs/tasks/YYYY-MM-DD-<slug>-frontend.md`, ghi `**Repo triển khai:** bookforge-fe` |
| Cả hai | **Hai file**, mỗi file tự đứng được; file FE nhắc lại hợp đồng API cần dùng, không bắt đọc file BE |

Tài liệu về FE vẫn nằm trong repo backend — repo `bookforge-fe` không có thư mục `docs/` (`docs-convention.md` §2.1).

**Ràng buộc cứng — task doc không được nhắc tới `tech_docs/`:**

`bookforge`, `bookforge-fe`, `tech_docs` là ba repo riêng; người nhận việc chỉ có repo triển khai, **không có** `tech_docs/`.
Vì vậy task doc sinh ra ở cuối quy trình này phải **cắt đứt hoàn toàn** với thư mục nghiên cứu đã dùng để tạo ra nó:

- Không có đường dẫn `tech_docs/…` hay `../tech_docs/…`, không nhắc tên `00-desc.md`, `01-brief.md`, `02-findings.md`, `03-design.md`, `qa.md`, `status.md`, `1_repo-map.md`.
- Trường `**Thiết kế gốc (đọc trước):**` chỉ trỏ file **trong cùng repo**; thiết kế chỉ có ở `research/` thì **bỏ trường đó** và viết thẳng vào "Quyết định đã chốt".
- Mọi thứ người làm cần biết — quyết định, ràng buộc, hợp đồng API, trích code — **chép vào task doc**, không link ra ngoài.

`tech_docs/research/` là nháp của bạn và tôi; task doc là thứ giao cho người khác. Xem [`docs-convention.md`](../docs-convention.md) §3.1.

**Không tự tạo file trong `backend/docs/superpowers/specs/` hay `backend/docs/audits/`** — hai loại đó do bạn (vai trò reviewer) viết.

## 6. Ranh giới khi dùng Gemini

Gemini có mặt trong quy trình này **chỉ để giữ hạn mức Claude cho việc ghi**. Prompt mẫu theo từng tình huống nằm ở [`../gemini-assist.md`](../gemini-assist.md); ở đây là phần luật.

**Bốn việc nên đẩy sang Gemini:**

| Việc | Vì sao đáng đẩy |
|---|---|
| Tra kiến thức ngoài repo (thư viện, API, chuẩn, cách người khác làm) | Không cần đọc repo — Claude Code làm cũng chẳng chính xác hơn, mà đắt hơn |
| Quét rộng để khoanh vùng ("mảng nào lo việc X") | Gemini đọc rộng rẻ; Claude Code chỉ cần đọc lại đúng vùng đã khoanh |
| Giảng lại cho bạn hiểu một đoạn code, một lỗi, một đánh đổi | Phần giảng giải dài dòng, không cần quyền ghi |
| Giải nghĩa `01-brief.md` / tóm tắt `02-findings.md` cho bạn duyệt | Bạn duyệt được mà không tốn thêm lượt của Claude |
| Đề xuất câu chữ khi tài liệu viết lủng củng | Gemini viết `<đoạn gốc> → <đoạn đề xuất>`; **Claude Code là người ghi vào file** |
| Phản biện `03-design.md` hoặc task doc Claude Code vừa viết | Con mắt thứ hai, không tốn lượt của Claude |

**Ba việc không giao cho Gemini:** ghi hay sửa bất kỳ file nào (kể cả trong `research/`), sửa code, và mọi thao tác git. Ghi là việc của Claude Code — một nguồn sự thật, một lịch sử sửa.

**Bưng kết quả về:** dán vào Claude Code trong một khối **có nhãn**, đừng dán trần:

```text
[TỪ GEMINI — CHƯA KIỂM CHỨNG]
<nội dung Gemini trả lời>
```

Thấy nhãn này, Claude Code **kiểm chứng trước khi dùng**: tên file/hàm/bảng nào không tự mở ra đọc được thì loại bỏ, và nói rõ chỗ nào Gemini nói sai. Dán trần không nhãn thì mặc định là lời của bạn — giả thuyết sẽ lọt vào tài liệu chốt mà không ai soát.

**Không đưa cho Gemini:** `.env`, `.env.local`, `*.key`, `*.pem`, dump cơ sở dữ liệu, log có dữ liệu người dùng thật. Cần bàn về cấu hình thì dùng `.env.example` hoặc `core/settings.py` — hai file này chỉ có tên biến và giá trị mặc định. Ràng buộc này áp cho cả Gemini trong IDE lẫn Gemini web.
## 7. Câu gõ vào Claude Code

**Mỗi sáng — cập nhật bản đồ** (điền ref bạn muốn lấy, xem bảng §3):

```text
Cập nhật bản đồ từ <ref> theo §3 của tech_docs/rules/claude/2_workflow-rules.md.
```

Ví dụ: `từ origin/dev` · `từ feat/geometry-editor` · `từ working`
· `từ bookforge=origin/dev, bookforge-fe=feat/abc`.
Bỏ trống ref thì tôi dùng lại đúng ref ghi ở header `1_repo-map.md` lần trước.

**Chuẩn hoá mô tả và tạo thư mục** (sau khi bạn đã viết nháp `tech_docs/research/00-desc.md`):

```text
Đọc tech_docs/research/00-desc.md, chuẩn hoá theo §8 của
tech_docs/rules/claude/2_workflow-rules.md, tự đặt slug rồi chuyển vào đúng thư mục.
```

Tôi viết lại cho chuẩn, tạo `research/<slug>/`, chuyển file vào, **rồi dừng** — chờ bạn duyệt xong mới sang khảo sát.

**Viết brief** (sau khi bạn duyệt `00-desc.md`):

```text
Đọc tech_docs/research/<slug>/00-desc.md, viết 01-brief.md theo §9 của
tech_docs/rules/claude/2_workflow-rules.md, rồi chờ tôi duyệt.
```

Tôi liệt kê câu hỏi khảo sát + giả định, **chưa đọc code**, rồi dừng.

**Khảo sát** (sau khi bạn duyệt `01-brief.md`):

```text
Đọc tech_docs/rules/claude/2_workflow-rules.md và tech_docs/research/<slug>/01-brief.md,
khảo sát repo rồi trả lời vào tech_docs/research/<slug>/02-findings.md theo §10.
```

**Thiết kế:**

```text
Đọc tech_docs/research/<slug>/02-findings.md, viết 03-design.md theo §17 của
tech_docs/rules/claude/2_workflow-rules.md, rồi chờ tôi chốt.
```

**Chốt thành task doc:**

```text
Đọc tech_docs/research/<slug>/03-design.md, kiểm chứng lại trong repo, rồi viết task doc
theo docs-convention §1.2a và §5 của tech_docs/rules/claude/2_workflow-rules.md.
```

**Thi công:**

```text
Đọc backend/docs/tasks/<ngày>-<slug>.md và triển khai đúng theo tài liệu đó,
theo §16 của tech_docs/rules/claude/2_workflow-rules.md.
```

**Sinh lại bản đồ từ đầu** (khi cấu trúc đổi lớn, hoặc đổi sang nhánh khác hẳn):

```text
Sinh lại tech_docs/overview/1_repo-map.md từ <ref> theo §3 của
tech_docs/rules/claude/2_workflow-rules.md.
```

Không cần mô tả lại tính năng ở bất kỳ câu nào — mô tả đã nằm trong file.
Muốn gọn hơn nữa thì đặt các câu này thành slash command trong `backend/.claude/commands/`.
## 8. `00-desc.md` — bạn viết nháp, Claude Code chuẩn hoá

**Bạn không tạo thư mục, không nghĩ slug.** Viết nháp thẳng vào `tech_docs/research/00-desc.md`, **hoàn toàn bằng ngôn ngữ nghiệp vụ** — không cần một tên kỹ thuật nào; chỗ nào không biết thì tả hiện tượng. Viết lủng củng, thiếu mục, gạch đầu dòng rời rạc đều được: dọn dẹp là việc của tôi.

Khuôn dưới đây là **đích đến sau khi chuẩn hoá**, không phải thứ bạn phải viết đủ ngay từ đầu.

```text
# 00 — Mô tả: <tên tính năng>

**Phía:** BE | FE | cả hai | chưa rõ      ← ghi "chưa rõ" cũng được, Claude Code sẽ chốt

## Người dùng muốn gì
<kể như kể chuyện: ai, đang ở màn hình nào, bấm gì, mong thấy gì>

## Hôm nay đang ra sao
<hiện trạng theo góc nhìn người dùng — cái gì thiếu, cái gì sai, cái gì đang làm thủ công>

## Ràng buộc
<thời hạn, chi phí, không được đụng vào phần nào, phải giữ tương thích với cái gì>

## Không làm lần này
<viết ra, nếu không phạm vi sẽ phình>

## Chỗ tôi không chắc
<liệt kê thoải mái — đây là đầu vào để Claude Code đi tìm, không phải điểm trừ>
```

### Luật chuẩn hoá — Claude Code phải theo

Câu gõ ở §7. Tôi làm đúng bảy việc sau, không hơn:

1. **Viết lại cho rõ, không phát minh nghiệp vụ.** Gom ý trùng, tách theo đúng các mục của khuôn, đổi lời kể lủng củng thành câu đọc được. Không thêm yêu cầu bạn chưa nói, không "đoán cho đủ ý".
2. **Không đọc code ở bước này.** Tối đa liếc `overview/1_repo-map.md` để đoán dòng **Phía** — khảo sát là việc của bước sau, làm sớm chỉ tốn token khi mô tả còn có thể đổi.
3. **Chỗ mơ hồ đẩy xuống "Chỗ tôi không chắc"**, không viết như thể đã biết. Mục này dài ra là tốt.
4. **Tối đa 3 câu hỏi nghiệp vụ**, hỏi một lượt, và chỉ khi thiếu tới mức không viết nổi. Thiếu ít thì cứ viết rồi ghi vào mục không chắc.
5. **Slug:** tiếng Anh, `kebab-case`, 2–4 từ, tả đúng việc (`export-exam-docx`), không trùng thư mục đã có trong `research/`.
6. **Chuyển file, không copy** — gốc `research/` phải sạch, không còn `00-desc.md` lẻ.
7. **Dừng lại.** In ra đường dẫn mới + 3 dòng "tôi đã đổi gì so với bản nháp", rồi chờ bạn duyệt. **Không tự chạy tiếp sang khảo sát**, kể cả khi thấy đã đủ thông tin.

Bạn duyệt: đọc `research/<slug>/00-desc.md`, sửa thẳng vào file hoặc bảo tôi sửa. Đúng ý rồi mới gõ câu khảo sát.

## 9. `01-brief.md` — Claude Code viết, bạn duyệt

Viết **trước khi đọc code**, chỉ dựa trên `00-desc.md`. Đây là bản kê khai *"tôi sắp lục ở đâu và đang tin điều gì"* — cửa duyệt rẻ nhất của cả quy trình: chặn một câu hỏi trật ở đây tốn một phút, để nó đi tiếp thì tốn cả lượt khảo sát.

Nó cũng là thứ đưa được cho Gemini: quét khoanh vùng trước cho rẻ (§2B của [`../gemini-assist.md`](../gemini-assist.md)), hoặc nhờ giải nghĩa từng câu hỏi khi bạn không rõ nó nhắm vào đâu. Kết quả mang về theo khối có nhãn ở §6.

```text
# 01 — Brief khảo sát: <tên tính năng>

## Mục tiêu tính năng
<3–5 gạch đầu dòng: làm được gì, cho ai, ràng buộc đã biết, cái KHÔNG làm>

## Phía dự đoán
<BE / FE / cả hai — và nói rõ đây mới là dự đoán, Claude Code sẽ chốt lại>

## Giả định cần kiểm chứng
<mỗi dòng: "Tôi đang giả định X" — cái nào sai sẽ đổi phương án>

## Câu hỏi khảo sát
<đánh số Q1..Qn, mỗi câu HỎI MỘT THỨ và trả lời được bằng cách đọc code.
Ghi rõ phía nào: [BE] / [FE] / [cả hai], và gắn nhãn chế độ cho từng câu:

  [ĐỊNH VỊ]  — chưa biết cái đó nằm đâu; mô tả bằng từ ngữ nghiệp vụ và yêu cầu
               Claude Code tự tìm rồi cho tên thật.
               VD: "[ĐỊNH VỊ][BE] Khi người dùng bấm xuất đề thi ra Word, luồng đi qua
                   những hàm nào, từ endpoint tới chỗ ghi file?"

  [XÁC MINH] — bản đồ đã có tên; hỏi để xác nhận chi tiết.
               VD: "[XÁC MINH][BE] `test_papers.py` có endpoint nào nhận tham số lọc
                   theo môn học không, tham số tên gì?"

Nếu tính năng đụng cả hai phía, xếp câu hỏi thành hai cụm [BE] và [FE] riêng.
Không hỏi "kiến trúc thế nào" — hỏi một luồng, một file, một quyết định cụ thể.
Tối đa 12 câu, xếp theo mức ảnh hưởng tới quyết định thiết kế.>

## Cần trích nguyên văn
<liệt kê thứ cần copy về: chữ ký hàm, model/TypedDict, cột của bảng, shape response,
tên biến môi trường. Mô tả bằng lời là đủ, không cần biết tên trước —
VD: "cột của bảng lưu đề thi", "kiểu dữ liệu response của API danh sách câu hỏi".>

## Ngưỡng dừng
<điều kiện để coi là đã đủ thông tin chốt thiết kế>
```

Bốn điều quyết định chất lượng vòng lặp:

- **Mỗi câu hỏi trả lời được bằng cách đọc code**, không phải bằng cách suy nghĩ.
- **Nhãn `[ĐỊNH VỊ]` / `[XÁC MINH]`** — `[XÁC MINH]` là tên đã có trong bản đồ, `[ĐỊNH VỊ]` là thứ chưa ai biết tên và phải đi tìm.
- **Mục "Cần trích nguyên văn"** — thứ giúp bạn đọc `02-findings.md` mà không phải mở repo.
- **Ngưỡng dừng**, nếu không sẽ khảo sát vô hạn.

### Luật viết brief — Claude Code phải theo

1. **Chưa đọc code.** Tối đa dùng `overview/1_repo-map.md` để biết thứ gì đã có tên. Đọc code ở bước này là làm trước việc của §10 mà chưa được duyệt.
2. **Giả định phải viết ra, không giấu trong đầu.** Mỗi giả định một dòng, kèm "nếu sai thì ảnh hưởng gì".
3. **Câu hỏi phải trả lời được bằng cách đọc code**, không phải bằng cách suy nghĩ hay hỏi người dùng.
4. **Tối đa 8 câu**, gộp câu cùng vùng lại. Brief dài là cách đốt token ở bước sau.
5. **Dừng lại chờ duyệt.** Không tự chạy tiếp sang khảo sát.
6. Bạn sửa brief bằng cách nói với tôi hoặc sửa thẳng file — sửa xong mới gõ câu khảo sát.

## 10. Khuôn `02-findings.md` — Claude Code viết

````text
# 02 — Kết quả khảo sát: <tên tính năng>

> Phạm vi đọc: <thư mục đã thực sự đọc>. Trạng thái tại <YYYY-MM-DD>.
> Mọi đường dẫn tính từ gốc repo tương ứng (`bookforge` / `bookforge-fe`).

## Tóm tắt cho người đọc không có repo
<5–10 dòng: điều gì làm thay đổi phương án so với giả định của brief>

## Phía nào phải sửa
<kết luận BE / FE / cả hai, kể cả khi 00-desc.md ghi "chưa rõ".
Liệt kê file phải đụng ở mỗi phía. Nếu cả hai: nói rõ hợp đồng giữa hai bên
(endpoint nào, shape gì) vì đó là chỗ hai task doc gặp nhau.>

## Bản đồ vùng liên quan
<tên thật của mọi thứ đụng tới — endpoint, hàm, bảng, component, job — mỗi dòng
một mục kèm đường dẫn. Đây là phần bù cho việc người hỏi không thuộc cấu trúc.>

## Tiền đề sai trong brief / mô tả
<câu hỏi nào hỏi về thứ không tồn tại, hoặc gọi sai tên → nêu cái THẬT SỰ có và
trả lời theo cái đó. Không được trả lời cụt "không tồn tại".>

## Trả lời câu hỏi
### Q1 — <nhắc lại câu hỏi>
**Trả lời:** …
**Bằng chứng:** `services/api/src/…/foo.py:120-138`
```python
<trích đúng đoạn, ≤ 25 dòng>
```

## Giả định của brief — đúng / sai
| # | Giả định | Kết luận | Bằng chứng |
|---|---|---|---|

## Trích nguyên văn theo yêu cầu
<chữ ký hàm, model, cột bảng, shape response — trích đủ để đọc được mà không cần repo>

## Vùng nên nhờ Gemini đọc thêm
| File / thư mục | Vì sao chưa đọc hết | Câu hỏi cần Gemini trả lời |
|---|---|---|
<chỉ ghi khi phạm vi rộng quá một lượt đọc; bỏ trống nếu đã đọc đủ — xem §11>
## Điều brief không hỏi nhưng ảnh hưởng tới thiết kế
<tối đa 5 mục — ràng buộc, va chạm, nợ kỹ thuật chắn đường>

## Chưa xác định được
<cái gì, vì sao, cần gì để xác định>
````

Ràng buộc khi viết file này:

- **Câu `[ĐỊNH VỊ]` là việc đi tìm, không phải việc đoán.** Tìm không ra thì nói rõ đã tìm ở đâu, bằng từ khoá gì.
- **Chỉ ghi cái đã đọc thấy.** Suy đoán phải gắn nhãn "giả thiết", đặt riêng, không trộn vào phần bằng chứng.
- **Tự chứa** — người mở lại file này sau vài tuần không có sẵn ngữ cảnh, nên trích đủ code để hiểu mà không phải dò repo.
- **Không thiết kế, không viết code tính năng** ở bước này.
- Trả lời hết mọi câu, kể cả khi câu trả lời là "chỗ này chưa có gì cả".
- Nếu phát hiện `1_repo-map.md` đã lệch thực tế, **sửa luôn dòng sai trong đó** và ghi một dòng vào mục tóm tắt.
- **Cập nhật `status.md`** (§13) trước khi kết thúc lượt.

## 11. File dài — tự đọc hay nhờ Gemini đọc hộ

Bản đồ trả lời "có cái gì"; file thật trả lời "chạy thế nào". Ngưỡng chọn:

| Tình huống | Cách làm |
|---|---|
| Hiểu được bằng ≤ 25 dòng | Claude Code đọc thẳng, trích vào `02-findings.md` |
| Một file, một luồng rõ ràng | Claude Code đọc cả file — đây đúng là việc của nó, đừng vòng qua Gemini |
| Phải lần qua nhiều file mới biết vùng nào liên quan | Nhờ Gemini quét khoanh vùng trước, Claude Code đọc lại đúng vùng đó (§6) |
| File rất dài mà chỉ cần một kết luận ("có chỗ nào gọi X không") | Gemini đọc hộ, trả lời trong chat; Claude Code mở đúng chỗ được chỉ để xác nhận |

**Luật không đổi:** kết luận của Gemini chỉ vào tài liệu sau khi Claude Code đã tự mở đúng file đó và xác nhận. `02-findings.md` chỉ chứa thứ Claude Code đã đọc thấy (§10).

**Tuyệt đối không đưa cho Gemini:** `.env`, `.env.local`, `*.key`, `*.pem`, dump cơ sở dữ liệu, log có dữ liệu người dùng thật, bất kỳ file nào chứa token hoặc khoá API thật (§6).
## 12. Hỏi nhanh lúc thi công — `qa.md`

Đây là vòng lặp bạn dùng nhiều nhất: tôi đang viết code, gặp ràng buộc hoặc cần bạn quyết. Tôi hỏi, bạn chốt; chỗ nào bạn không hiểu thì mang sang Gemini cho nó giảng rồi quay lại chốt.

**Nghĩa vụ của Claude Code khi hỏi:** viết câu hỏi ở dạng **tự chứa** — đủ ngữ cảnh, có trích đoạn code liên quan, nói rõ đang bị chặn ở đâu, và nêu sẵn các phương án kèm đánh đổi.
Bạn phải đọc là hiểu, hoặc dán thẳng sang Gemini mà không phải giải thích thêm câu nào.
Không dùng từ viết tắt nội bộ. Câu chỉ cần "có/không" thì hỏi thẳng bạn, đừng bắt bạn đi hỏi nơi khác.

**Prompt dán cho Gemini trước câu hỏi** (2 dòng cố định):

```text
Đây là câu hỏi/ràng buộc do agent đang viết code trong repo BookForge nêu ra.
Giải thích cho tôi bằng lời dễ hiểu, nêu 2 lựa chọn kèm đánh đổi, rồi khuyến nghị một cái.
```

**Khuôn một mục trong `qa.md`** (ghi nối tiếp, mới nhất xuống dưới):

```text
## <YYYY-MM-DD> — <câu hỏi tóm trong một dòng>

**Người hỏi:** Claude Code | Bạn
**Bối cảnh:** <file:line, hoặc đang ở bước nào của task doc>

**Câu hỏi:**
<khối tự chứa — ngữ cảnh + trích code + đang chặn cái gì + phương án nếu có>

**Tham khảo:** <nếu có hỏi Gemini: tóm 3–8 dòng, giữ phần đánh đổi, ghi rõ chỗ nào chưa kiểm chứng>
**Chốt:** <quyết định cuối + đã chép vào task doc nào>
```

**Luật chống mất mát:** `qa.md` là **nhật ký**, task doc mới là **nguồn sự thật**.
Mọi quyết định đã chốt phải được chép về mục "Quyết định đã chốt" của task doc, nếu không vài hôm sau không ai nhớ vì sao làm như vậy.
## 13. `status.md` — hồi phục khi mất ngữ cảnh

Đóng phiên, context bị nén, hết hạn mức, hoặc mai mở lại máy — ngữ cảnh mất sạch. File này để đọc một lần là chạy tiếp được.

**Claude Code tự cập nhật nó ở mọi lượt được gọi** — lúc đó ngữ cảnh đang sẵn nên gần như miễn phí. Bạn không phải viết.

```text
# Trạng thái: <tên tính năng>

**Cập nhật:** YYYY-MM-DD · **Phía:** BE | FE | cả hai · **Giai đoạn:** khảo sát | thiết kế | thi công | xong

## Mục tiêu
<3 dòng, đọc là hiểu đang làm gì cho ai>

## Quyết định đã chốt
1. <quyết định + lý do một dòng>
2. …

## Phương án đang theo
<5–10 dòng: cách làm đã chọn, và cách đã loại kèm lý do>

## File trong thư mục này
- `01-brief.md` — <một dòng>
- `02-findings.md` — <một dòng>
- …

## Câu hỏi mở
<cái gì chưa chốt, đang chờ ai>

## Bước tiếp theo
<việc kế tiếp, đủ cụ thể để bắt tay làm ngay>
```

Giữ **dưới 60 dòng** — nó là điểm khởi động lại, không phải bản sao của thiết kế.

**Câu hồi sức** — mở phiên Claude Code mới, gõ:

```text
Đọc tech_docs/research/<slug>/status.md và tech_docs/rules/claude/2_workflow-rules.md,
nói lại trong 5 dòng đang ở đâu và bước tiếp theo là gì, rồi chờ tôi.
```

Hết hạn mức Claude giữa chừng thì dán `status.md` cho Gemini để hiểu tiếp và bàn phương án — nhưng **không để Gemini sửa file**, chờ phiên Claude Code sau ghi lại (§6).

## 14. Quy tắc tiết kiệm token

- **Đẩy phần đọc rộng và phần giảng giải sang Gemini** (§6). Hạn mức Claude để dành cho việc đọc chính xác và việc ghi — hai thứ Gemini không được làm.
- **Đóng khung phạm vi đọc ngay trong câu giao việc** ("chỉ mảng quota", "chỉ `services/jsxgraph/`"). Đây là đòn tiết kiệm lớn nhất.
- **Lưu file, đừng dán vào terminal.** Dán 300 dòng vào Claude Code tốn đúng bằng lúc nó tự đọc file, nhưng mất lịch sử và không sửa lại được.
- **Cập nhật bản đồ theo diff, không sinh lại.** Diff rỗng thì dừng ngay (§3).
- **Duyệt `01-brief.md` cho kỹ** (§9) — chặn một câu hỏi trật ở đó rẻ hơn nhiều lần so với khảo sát lại cả lượt. Việc cực nhỏ (đổi một nhãn, sửa một chuỗi) thì đừng mở thư mục `research/` làm gì, gõ thẳng yêu cầu.
- **Gộp câu hỏi thành một lượt.** Hỏi lắt nhắt mỗi lần vài câu là cách đốt token nhanh nhất.
- **Một thư mục research cho một tính năng**; ngữ cảnh nằm ở file, không nằm ở chat.
- **Cập nhật `status.md` mỗi lượt** (§13) — mất phiên mà không có nó thì phải khảo sát lại từ đầu, đắt gấp nhiều lần.
## 15. Checklist

**Mỗi sáng**

- [ ] Đã gõ câu cập nhật bản đồ **kèm ref muốn lấy** (§3).
- [ ] Header hai file map ghi đúng SHA, **ref** và ngày — và ref đó đúng là nhánh bạn muốn bản đồ phản ánh.

**Mỗi tính năng**

- [ ] Đã tạo `tech_docs/research/<slug>/` và viết `00-desc.md`, có dòng **Phía**.
- [ ] `02-findings.md` có **"Phía nào phải sửa"**, **"Bản đồ vùng liên quan"**, câu nào cũng có `file:line`.
- [ ] Thứ lấy từ Gemini đã được Claude Code mở đúng file xác nhận lại; cái chưa xác nhận **không** nằm trong findings / design / task doc (§6).
- [ ] `03-design.md` nêu **hai phương án và đánh đổi**, không phải một phương án đã rồi.
- [ ] Chốt xong: task doc ở `backend/docs/tasks/` — **hai file nếu đụng cả hai phía** (§5), có "Quyết định đã chốt" + DoD.
- [ ] Task doc **không chứa chuỗi `tech_docs`** và đọc trọn vẹn được bởi người chỉ có repo triển khai (§5).

**Khi thi công**

- [ ] Câu hỏi của Claude Code **tự chứa**, dán sang Gemini được ngay.
- [ ] Đã ghi vào `qa.md`, và **quyết định đã chép về task doc**.
- [ ] `status.md` được cập nhật ở mọi lượt Claude Code chạy.
- [ ] Không đưa file chứa khoá/token cho Gemini (§6, §11).
- [ ] Không tự tạo file trong `specs/` hoặc `audits/`.
- [ ] Thi công **bám đúng task doc** (§16), DoD được tick ngay trong file đó.
- [ ] Đầu lượt đã kiểm migration DB local (§18): `alembic current` = head, hoặc đã sao lưu rồi chạy.
## 16. Thi công theo task doc

Task doc là **hợp đồng**, không phải gợi ý. Ba luật riêng cho giai đoạn này:

1. **Đúng phạm vi ghi trong doc.** Không thêm tính năng, không refactor kèm, không "tiện tay sửa luôn" chỗ khác.
2. **Bám mục "Quyết định đã chốt".** Đã chốt thì không tự chọn cách khác, kể cả khi thấy cách khác hay hơn — muốn đổi phải hỏi trước và sửa doc.
3. **Doc sai hoặc thiếu so với code thật → dừng, báo người dùng, sửa doc trước rồi mới code.** Không im lặng làm khác tài liệu: lệch giữa doc và code là thứ vài tuần sau không ai gỡ được.

Ba luật còn lại đã nằm ở chỗ khác, nhắc để không quên:

- **Đầu lượt thi công và lượt tự soát DoD: kiểm migration DB local theo §18** trước khi đọc task doc — DB lệch schema làm test/kiểm tay báo lỗi không liên quan tới task.

- **Tick `- [x]` từng mục DoD ngay trong task doc** khi đạt, và sửa nội dung đã không còn đúng — không tạo file `.md` mới để báo cáo (`docs-convention.md` §6).
- **Chỉ tick sau khi đã chạy và đọc kết quả thật**, không tick theo cảm giác. Mục mở đầu bằng `(kiểm tay)` thì để nguyên, nói rõ người dùng cần làm gì để nghiệm thu (`docs-convention.md` §1.2a).
- **Bỏ một mục DoD phải có lý do ghi lại trong chính task doc**, và phải được người dùng đồng ý trước.
- **Quyết định phát sinh** → `qa.md` + chép về "Quyết định đã chốt" (§12).
- **Không commit, không push khi chưa được cho phép** (`3_git-workflow-rules.md` §1).

Đụng cả hai phía thì thi công **từng task doc một**, BE trước cho có API thật, và mỗi repo một phiên Claude Code riêng.

## 17. `03-design.md` — Claude Code viết, bạn chốt

Viết sau khi bạn đã duyệt `02-findings.md`, và **chỉ dựa trên sự thật trong file đó**.

````text
# 03 — Thiết kế: <tên tính năng>

> Nguồn sự thật: `02-findings.md` (đọc tại `bookforge@<sha>`).
> Chỗ nào không có bằng chứng trực tiếp trong findings được đánh dấu **[giả định]**.

## Kết luận chốt
<3–5 dòng: làm theo cách nào, vì sao>

## Phương án A — <tên>
<cách làm, 5–10 dòng, có tên file/hàm thật lấy từ findings>
**Được:** … · **Mất:** … · **Hỏng ở đâu khi lỗi:** …

## Phương án B — <tên>
<như trên>

## Khuyến nghị
<chọn cái nào, vì sao, và điều kiện nào thì nên đổi sang cái kia>

## Không làm lần này
<cắt phạm vi ngay tại đây, đừng để phình ở task doc>

## Ảnh hưởng tới chỗ đang chạy
<những luồng/màn hình/job sẽ bị đụng, kèm `file:line`>

## Kế hoạch triển khai
<các bước theo thứ tự, mỗi bước một dòng, ghi rõ bước nào chặn bước nào>

## Chưa chốt — cần bạn quyết
<mỗi câu hỏi kèm đúng 2 lựa chọn và hệ quả của từng lựa chọn>
````

Sáu luật khi viết file này:

1. **Hai phương án phải khác nhau về cách làm**, không phải một phương án thật và một phương án dựng lên cho đủ số.
2. **Đánh đổi phải đo được** — thêm bao nhiêu lượt query, chậm thêm bao nhiêu, hỏng chỗ nào khi lỗi. Không viết "dễ bảo trì hơn" rồi thôi.
3. **Chỉ dựa trên `02-findings.md`.** Thứ chưa kiểm chứng phải gắn **[giả định]** kèm câu "cần kiểm gì để bỏ nhãn này".
4. **Không viết code tính năng** ở bước này; minh hoạ tối đa 10 dòng.
5. **Dừng chờ bạn chốt.** Không tự nhảy sang viết task doc, kể cả khi phương án đã rõ.
6. **Cập nhật `status.md`** (§13) trước khi kết thúc lượt.

## 18. Migration DB local — kiểm và chạy ngay trong phiên

**Vì sao có mục này.** Ngày 2026-09-14, sau khi kéo nhánh `feature/qb-khung-cap3-nl-rest` mà chưa migrate, mở drawer "Tạo câu hỏi hàng loạt" bật toast
"Có lỗi xảy ra — Đã xảy ra lỗi không mong muốn": model đã có cột `question_competency_frameworks.cap` (migration `0088_competency_cap`)
nhưng DB SQLite local chưa có, nên `GET /api/question-competency-frameworks` trả 500 `internal_error`.
Lỗi trông như do task đang làm, mất một lượt khảo sát mới ra.

**Khi nào chạy:** đầu lượt, **trước việc chính**, mỗi khi bạn gõ câu ① ⑦ ⑧ ⑨ ⑩ ở [`1_start-here.md`](1_start-here.md) §7
(cập nhật / sinh lại bản đồ, thi công, tự soát DoD, hồi phục phiên).
Câu ②–⑥ chỉ viết tài liệu nghiên cứu, không chạy BE hay test nên bỏ qua. Bạn nói "kiểm migration" ở bất kỳ lúc nào thì cũng chạy.

**Kiểm cái gì:** DB mà **thư mục làm việc** của repo backend đang dùng — thứ BE local của bạn thật sự chạy.
Không phải ref quét bản đồ (§3 đọc ref qua worktree tạm, không `pull`).

**Luôn chạy trong `backend/services/api`** — Alembic lấy địa chỉ DB từ `.env` ở đó, đường dẫn SQLite là tương đối.

### Bước 1 — Xác định DB (không in cả `.env`)

Chỉ đọc đúng hai dòng, che mật khẩu nếu có:

```bash
grep -hE "^(BOOKFORGE_ENV|BOOKFORGE_DATABASE_URL)=" .env | sed -E 's#(://[^:]+:)[^@]+@#\1***@#'
```

| `BOOKFORGE_DATABASE_URL` | Làm gì |
|---|---|
| `sqlite:///./…` (file local) | Theo bước 2–4, **tự chạy** |
| `postgresql…@localhost` / `127.0.0.1` | Kiểm bước 2, **hỏi bạn trước khi chạy** (không có bản sao để chạy thử) |
| Host khác (staging, prod, IP lạ) | **Không chạy gì**, chỉ báo |

### Bước 2 — So `current` với `heads`

```bash
uv run alembic current
uv run alembic heads
```

| Kết quả | Làm gì |
|---|---|
| `current` = head | Báo một dòng "migration: DB local đã ở `<revision>`", sang việc chính |
| `heads` ra **hơn một** revision | Dừng, báo bạn — hai nhánh cùng thêm migration, cần migration gộp, không phải việc của phiên này |
| `current` **rỗng** (DB không có bảng `alembic_version`) | Sang **bước 5**, không tự `stamp` |
| `current` cũ hơn head | Sang bước 3 |

### Bước 3 — Sao lưu, chạy thử trên bản sao, rồi chạy thật

```bash
uv run alembic history -r current:heads        # liệt kê migration sẽ chạy
cp storage/bookforge.db storage/bookforge.db.bak-<YYYY-MM-DD>   # trùng tên thì thêm -HHMM
cp storage/bookforge.db <scratchpad>/bookforge-copy.db
BOOKFORGE_DATABASE_URL="sqlite:///<scratchpad>/bookforge-copy.db" uv run alembic upgrade head
uv run alembic upgrade head                     # chỉ khi bản sao chạy sạch
```

- **Chạy thử trên bản sao lỗi** → dừng, **không** chạy thật, báo lỗi kèm tên migration hỏng.
Hay gặp: BE dev tự `create_all` lúc khởi động nên tạo sẵn bảng mới, rồi migration `create_table` báo "already exists".
- **`database is locked`** → nhờ bạn tắt BE (Ctrl+C) rồi tôi chạy lại lệnh cuối.

### Bước 4 — Xác nhận và báo

1. `uv run alembic current` phải in `(head)`.
2. Chạy đoạn so model với DB (dán nguyên vào `<scratchpad>/schema_drift.py`, chạy `uv run python <scratchpad>/schema_drift.py`), phải chỉ in `xong`:

```python
import sqlalchemy as sa

import bookforge_api.models  # noqa: F401
from bookforge_api.core.db import Base, get_engine

insp = sa.inspect(get_engine())
tables = set(insp.get_table_names())
for name, table in sorted(Base.metadata.tables.items()):
    if name not in tables:
        print('THIẾU BẢNG', name)
        continue
    cols = {c['name'] for c in insp.get_columns(name)}
    missing = [c.name for c in table.columns if c.name not in cols]
    if missing:
        print('THIẾU CỘT', name, missing)
print('xong')
```

3. Báo trong chat 3–5 dòng: đã chạy migration nào (`<từ>` → `<tới>`), file sao lưu nằm đâu, và **nhắc bật lại BE** nếu bạn đã tắt.

### Bước 5 — DB chưa từng chạy Alembic (`current` rỗng)

DB dev tạo bằng `create_all` không có `alembic_version`. `create_all` chỉ tạo **bảng mới**, không thêm **cột mới** vào bảng đã có — nên kéo code mới về là có thể lệch.
`alembic upgrade head` thẳng sẽ chạy lại từ migration đầu tiên và hỏng.

1. Chạy đoạn so model với DB ở bước 4.
2. Tìm migration đầu tiên tạo ra bảng/cột bị thiếu (`grep` tên cột trong `alembic/versions/`) → mốc `stamp` là revision **ngay trước** nó.
Không thiếu gì → mốc là head hiện tại.
3. Đọc các migration từ mốc tới head, xác nhận chúng tự kiểm tồn tại trước khi thêm (`if 'cap' not in columns`) hoặc chỉ gọi hàm seed chạy lại được.
4. Chạy thử trên bản sao: `stamp <mốc>` rồi `upgrade head`, kèm đoạn so model với DB.
5. **Hỏi bạn trước khi làm trên DB thật** — chọn mốc là phán đoán, không phải lệnh máy. Bạn đồng ý thì sao lưu, `stamp <mốc>`, `upgrade head`, xác nhận như bước 4.

Lần 2026-09-14: thiếu đúng cột `cap` → mốc `0087_reseed_khung_names` → `upgrade head` chạy 0088–0097; hai bảng khung được seed (27 khung năng lực, 92 khung kiến thức).

### Không bao giờ

- `alembic downgrade`, xoá DB, xoá file sao lưu.
- Chạy migration lên DB không phải local.
- Commit gì liên quan tới việc này — sao lưu và DB nằm trong `storage/`, không thuộc git.
- Sửa file migration để nó chạy qua. Migration hỏng là lỗi của nhánh đã kéo về → báo bạn.
