# Quy ước trao đổi Claude Web ↔ Claude Code

> **📌 Cách dùng file này:** đây là **giao thức cố định** cho vòng lặp "soạn mô tả trên web → phân tích trong repo → quay lại web → thi công".
> Mục tiêu: không phải soạn prompt mới mỗi lần, và **không ai trong chuỗi cần thuộc tên hàm, tên bảng, tên endpoint** — việc định vị đó là của Claude Code.
> Dán §6 vào đầu mỗi chat web; trong Claude Code chỉ gõ những câu ở §7.
> **Chỉ cần biết làm gì mỗi ngày thì đọc [`1_start-here.md`](1_start-here.md)** — file này là luật chi tiết, mở khi cần tra khuôn mẫu.

---

## 1. Phân vai

| | **Bạn** | **Claude Web** | **Claude Code** (trong repo) |
|---|---|---|---|
| Có gì | Ý đồ sản phẩm, quyền quyết định | Suy luận rộng, viết dài rẻ | **Sự thật của repo**: file, dòng, schema, test |
| Không có gì | Không thuộc cấu trúc code — **không cần thuộc** | Không thấy code (trừ file bạn upload, §11) | Token đắt; đọc lan man rất tốn |
| Việc | Mô tả nghiệp vụ, chốt phương án, bưng file qua lại | Đặt câu hỏi, dựng phương án, **giải thích cho bạn hiểu** | **Định vị, trả lời bằng bằng chứng `file:line`, và viết code** |

Ba nguyên tắc, vi phạm cái nào cũng sinh ra một vòng lặp thừa:

> **Bạn không cần biết tên kỹ thuật.** Mô tả "chỗ hiện danh sách đề thi", đừng cố nhớ tên component.
> **Web không đoán code.** Không được viết tên file/hàm/bảng như thể đã biết — thứ cần biết thì đưa vào câu hỏi, hoặc yêu cầu upload file.
> **Code không nghiên cứu rộng, và không giải thích dài.** Trả lời đúng câu được hỏi kèm bằng chứng; phần giảng giải đẩy sang web (§12).

## 2. Ba giai đoạn và nhịp hằng ngày

```text
NHỊP HẰNG NGÀY — mỗi sáng, một câu gõ (§3)
[Code] ─► quét ref BẠN CHỈ ĐỊNH → cập nhật overview/repo-map.md + backend-features-all.md
             └─► in ra "hôm nay đổi gì" để bạn dán vào chat web đang mở

GIAI ĐOẠN 1 — KHẢO SÁT      thư mục tech_docs/research/<slug>/
[Bạn]  ─► 00-mo-ta.md       Mô tả nghiệp vụ + dòng "Phía: BE|FE|cả hai" (§8)
   │
[Web]  ─► 01-brief.md       Câu hỏi khảo sát + giả định cần kiểm chứng (§9)
   │
[Code] ─► 02-findings.md    Định vị, trả lời kèm file:line, chốt phía nào phải sửa,
   │                        liệt kê file nên upload lên web (§10)

GIAI ĐOẠN 2 — CHỐT
[Web]  ─► 03-design.md      Phương án + đánh đổi + kế hoạch
   │
[Code] ─► backend/docs/tasks/YYYY-MM-DD-<slug>.md          (phần BE)
          backend/docs/tasks/YYYY-MM-DD-<slug>-frontend.md (phần FE, nếu có)

GIAI ĐOẠN 3 — THI CÔNG      vòng lặp ngắn, lặp nhiều lần (§12)
[Code] viết code ─► gặp ràng buộc / cần quyết định
   │                 viết câu hỏi TỰ CHỨA
   ▼
[Bạn] dán sang web ─► [Web] giải thích + khuyến nghị ─► bạn chốt
   │
   └─► ghi vào qa.md  +  cập nhật "Quyết định đã chốt" của task doc

XUYÊN SUỐT: trang-thai.md giữ ngữ cảnh để hồi phục khi đổi tài khoản web (§13)
```

Giai đoạn 1–2 bình thường **đúng hai lượt qua lại**. Giai đoạn 3 lặp bao nhiêu lần cũng được — nó rẻ, vì phần nặng nằm ở web.

## 3. Nhịp hằng ngày — cập nhật bản đồ từ nhánh bạn chỉ định

Code đổi liên tục, bản đồ cũ làm web hỏi trật. Mỗi sáng gõ **một câu** ở §7, **kèm nhánh muốn lấy**.

**Nguồn quét — bạn chọn, không mặc định `dev`:**

| Bạn ghi | Nghĩa |
|---|---|
| `origin/dev`, `origin/main`, `origin/<bất kỳ>` | Nhánh trên remote, đã `fetch` về |
| `feat/geometry-editor` (nhánh local) | Commit mới nhất của nhánh đó, kể cả chưa push |
| `working` | **Thư mục làm việc hiện tại**, tính cả thay đổi chưa commit |
| *(bỏ trống)* | Dùng lại đúng ref ghi ở header `repo-map.md` lần trước |

Hai repo có thể lấy từ hai nhánh khác nhau — ghi rõ khi cần:
`bookforge=origin/dev, bookforge-fe=feat/abc`. Ghi một ref duy nhất thì áp cho cả hai.

**Ràng buộc cứng khi tôi chạy việc này:** không `checkout`, không `pull`, không `stash`, không đụng nhánh bạn đang làm.
Với ref là nhánh, tôi chỉ `fetch` rồi đọc qua một **worktree tạm** trong scratchpad và xoá ngay sau khi quét.
Với `working`, tôi đọc thẳng thư mục làm việc, không tạo worktree.

Các bước:

1. `git -C <repo> fetch origin <nhánh>` — bỏ qua nếu ref là nhánh local hoặc `working`.
2. Đọc SHA cơ sở ở header hai file map, chạy `git diff --stat <sha cơ sở>..<ref>` cho từng repo.
3. **Diff rỗng cả hai repo** → chỉ sửa lại ngày trong header, báo "không đổi", dừng. Gần như 0 token.
4. **Diff nhỏ** → `git worktree add --detach <scratchpad>/map-<repo> <ref>`, quét **đúng vùng bị đụng**, sửa những dòng đã lệch trong map, rồi `git worktree remove`.
5. **Sinh lại toàn bộ** khi: diff đụng hơn 60 file, hoặc bản đồ quá 14 ngày, hoặc cấu trúc thư mục đổi, hoặc **ref lần này nằm khác nhánh với ref lần trước** (diff giữa hai nhánh rẽ nhau thường vô nghĩa để vá từng dòng).
6. In ra terminal **5–10 dòng "đổi gì từ lần trước"**, có ghi rõ **quét từ ref nào**, để bạn dán bổ sung vào chat web đang mở dở. **Không lưu thành changelog trong file** — `docs-convention.md` §1.3 ghi rõ docs dự án không có mục changelog.

Hai lưu ý khi đổi ref:

- Quét từ `origin/dev` thì **những gì bạn vừa làm trên nhánh riêng chưa merge sẽ không có trong bản đồ**. Muốn thấy, quét từ chính nhánh đó hoặc từ `working`.
- Quét từ `working` cho bản đồ khớp nhất với cái bạn đang sửa, nhưng mốc SHA kèm hậu tố `+dirty` và **không dùng để tính diff lần sau được** — lần sau nên nêu lại ref rõ ràng.

Cập nhật file nào:

- `repo-map.md` — khi diff chạm `api/`, `models/`, `workers/`, `cron/`, `core/settings.py`, `services/features.py`, hoặc phía FE là `src/App.tsx`, `src/api/`.
- `backend-features-all.md` — **chỉ khi có tính năng mới hoặc luồng đổi bản chất**. Đổi tên biến, refactor nội bộ thì không đụng tới nó.

Header hai file map luôn ghi SHA nguồn, đây là mốc để tính diff lần sau:

```text
> Nguồn: bookforge@<sha> (<nhánh>) · bookforge-fe@<sha> (<nhánh>) — <YYYY-MM-DD>.
```

**`repo-map.md` chứa gì** (dùng khi sinh lại toàn bộ): bảng endpoint theo router · bảng dữ liệu (bảng → model → khoá ngoại) · route FE → component → tầng API · job nền và cron kèm nơi gọi · feature flag · biến môi trường theo nhóm · **mục "vùng chưa lập bản đồ"**.
Mỗi mục **một dòng** — đây là mục lục, không phải tài liệu thiết kế.

## 4. Gói ngữ cảnh dán vào web

Web chỉ hỏi trúng khi có bản đồ trong tay. Dán theo **phạm vi**, không dán thừa:

| Phía làm | Dán vào đầu chat web |
|---|---|
| Chỉ BE | `repo-map.md` §1,2,3,5,6,7 + `backend-features-all.md` |
| Chỉ FE | `repo-map.md` §4 + `frontend/CONVENTION.md` |
| Cả hai, hoặc chưa rõ | Cả hai file, đầy đủ |

| File | Trả lời câu hỏi |
|---|---|
| [`overview/backend-features-all.md`](../overview/backend-features-all.md) | *Hệ thống làm được những gì, logic nằm ở module nào* |
| [`overview/repo-map.md`](../overview/repo-map.md) | *Có những endpoint / bảng / màn hình / job / env nào* |
| [`frontend/CONVENTION.md`](../../frontend/CONVENTION.md) | *Quy ước đặt tên và giới hạn kích thước file FE* |

Cả hai bản đồ đều là **mục lục**: đủ để hỏi trúng chỗ, không đủ để kết luận code chạy thế nào. Cần sâu hơn thì hỏi ở `01-brief.md`, hoặc upload file thật (§11).

## 5. Nơi đặt file

Mỗi tính năng một thư mục `tech_docs/research/<feature-slug>/`, đánh số tăng dần như `research/canvas-agent-geometry/`.

| File | Ai viết | Nội dung |
|---|---|---|
| `trang-thai.md` | **Claude Code** | Ngữ cảnh cô đọng để hồi phục phiên web (§13) — không đánh số, luôn ở đầu |
| `00-mo-ta.md` | **Bạn** | Mô tả nghiệp vụ, phía, ràng buộc, cái không làm (§8) |
| `01-brief.md` | Web | Câu hỏi khảo sát (§9) |
| `02-findings.md` | **Claude Code** | Hiện trạng có bằng chứng (§10) |
| `03-design.md` | Web | Phương án, đánh đổi, kế hoạch |
| `04-…`, `05-…` | luân phiên | Vòng khảo sát bổ sung nếu còn câu hỏi mở |
| `qa.md` | **Claude Code** + bạn | Nhật ký hỏi–đáp lúc thi công (§12) |

Quy ước áp dụng: tên file `kebab-case`, tiếng Việt, không frontmatter, sơ đồ ASCII — xem [`docs-convention.md`](docs-convention.md).
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

- Không có đường dẫn `tech_docs/…` hay `../tech_docs/…`, không nhắc tên `00-mo-ta.md`, `01-brief.md`, `02-findings.md`, `03-design.md`, `qa.md`, `trang-thai.md`, `repo-map.md`.
- Trường `**Thiết kế gốc (đọc trước):**` chỉ trỏ file **trong cùng repo**; thiết kế chỉ có ở `research/` thì **bỏ trường đó** và viết thẳng vào "Quyết định đã chốt".
- Mọi thứ người làm cần biết — quyết định, ràng buộc, hợp đồng API, trích code — **chép vào task doc**, không link ra ngoài.

`tech_docs/research/` là nháp của bạn và tôi; task doc là thứ giao cho người khác. Xem `docs-convention.md` §3.1.

**Không tự tạo file trong `backend/docs/superpowers/specs/` hay `backend/docs/audits/`** — hai loại đó do bạn (vai trò reviewer) viết.

## 6. Prompt cố định dán vào Claude Web

Dán **một lần** ở đầu mỗi cuộc trò chuyện web: prompt này trước, rồi gói ngữ cảnh §4, rồi mô tả tính năng.

````text
Bối cảnh: dự án BookForge, backend Python (FastAPI + RQ worker, repo `bookforge`) +
frontend React/TS (Vite, Tiptap, repo `bookforge-fe`). Bạn KHÔNG có quyền đọc code.
Một agent khác (Claude Code) chạy trực tiếp trong repo và sẽ trả lời bạn.

Tôi dán kèm bản đồ dự án (bản đồ chức năng và/hoặc danh mục endpoint/bảng/màn hình).
Chúng là MỤC LỤC, không phải mô tả đầy đủ: đủ để bạn hỏi trúng chỗ, không đủ để bạn
kết luận về cách code chạy.

Vai của bạn: đặt câu hỏi và dựng phương án. Ràng buộc:
- KHÔNG phỏng đoán tên file, hàm, bảng, endpoint nào không có trong bản đồ tôi dán.
- Nếu tôi UPLOAD file code, bạn được nói tên hàm/biến/kiểu dữ liệu CÓ TRONG file đó,
  nhưng vẫn không được suy ra nội dung của file khác. Thiếu file nào thì ghi vào
  mục "Cần upload thêm" ở cuối câu trả lời.
- Người dùng (tôi) không thuộc cấu trúc code; đừng hỏi tôi tên hàm hay tên bảng.
  Cái gì đọc code là biết thì hỏi Claude Code, đừng hỏi tôi.
- Chỉ hỏi tôi những thứ CHỈ tôi trả lời được: mong muốn nghiệp vụ, ưu tiên, phạm vi,
  ai dùng, chấp nhận đánh đổi nào. Hỏi tối đa 5 câu, hỏi một lượt.

Tôi sẽ mô tả một tính năng. Việc của bạn ở lượt này là xuất ra DUY NHẤT một khối markdown
theo khuôn dưới đây (không viết thiết kế, không viết code):

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

Sau khi tôi dán kết quả khảo sát về, hãy chuyển sang viết `03-design.md`:
phương án + đánh đổi + kế hoạch triển khai, tách rõ phần BE và phần FE nếu đụng cả hai,
chỉ dựa trên sự thật trong kết quả đó, và nêu rõ chỗ nào vẫn còn là giả định.
````

## 7. Câu gõ vào Claude Code

**Mỗi sáng — cập nhật bản đồ** (điền ref bạn muốn lấy, xem bảng §3):

```text
Cập nhật bản đồ từ <ref> theo §3 của tech_docs/rules/2_web-code-handoff.md.
```

Ví dụ: `từ origin/dev` · `từ origin/main` · `từ feat/geometry-editor` · `từ working`
· `từ bookforge=origin/dev, bookforge-fe=feat/abc`.
Bỏ trống ref thì tôi dùng lại đúng ref ghi ở header `repo-map.md` lần trước.

**Mỗi vòng khảo sát:**

```text
Đọc tech_docs/rules/2_web-code-handoff.md và tech_docs/research/<slug>/01-brief.md,
trả lời vào tech_docs/research/<slug>/02-findings.md.
```

**Chốt:**

```text
Đọc tech_docs/research/<slug>/03-design.md, kiểm chứng lại trong repo,
rồi viết task doc theo docs-convention §1.2a.
```

**Sinh lại bản đồ từ đầu** (khi cấu trúc đổi lớn, hoặc đổi sang nhánh khác hẳn):

```text
Sinh lại tech_docs/overview/repo-map.md từ <ref> theo §3.
```

Không cần mô tả lại tính năng ở bất kỳ câu nào — mô tả đã nằm trong file.
Muốn gọn hơn nữa thì đặt bốn câu này thành slash command trong `backend/.claude/commands/`.

## 8. Khuôn `00-mo-ta.md` — bạn viết

Viết **hoàn toàn bằng ngôn ngữ nghiệp vụ**. Không cần một tên kỹ thuật nào; chỗ nào không biết thì tả hiện tượng.

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

## 9. Khuôn `01-brief.md`

Chính là khối khuôn nằm trong prompt §6 — web sinh ra, bạn lưu nguyên văn vào file.
Bốn điều quyết định chất lượng vòng lặp:

- **Mỗi câu hỏi trả lời được bằng cách đọc code**, không phải bằng cách suy nghĩ.
- **Nhãn `[ĐỊNH VỊ]` / `[XÁC MINH]`** — câu `[ĐỊNH VỊ]` cho phép hỏi mà không biết tên, và báo cho Claude Code biết phải đi tìm trước khi trả lời.
- **Mục "Cần trích nguyên văn"** — thứ giúp web không phải hỏi vòng hai.
- **Ngưỡng dừng**, nếu không hai bên sẽ khảo sát vô hạn.

## 10. Khuôn `02-findings.md` — Claude Code viết

````text
# 02 — Kết quả khảo sát: <tên tính năng>

> Phạm vi đọc: <thư mục đã thực sự đọc>. Trạng thái tại <YYYY-MM-DD>.
> Mọi đường dẫn tính từ gốc repo tương ứng (`bookforge` / `bookforge-fe`).

## Tóm tắt cho người đọc không có repo
<5–10 dòng: điều gì làm thay đổi phương án so với giả định của brief>

## Phía nào phải sửa
<kết luận BE / FE / cả hai, kể cả khi 00-mo-ta.md ghi "chưa rõ".
Liệt kê file phải đụng ở mỗi phía. Nếu cả hai: nói rõ hợp đồng giữa hai bên
(endpoint nào, shape gì) vì đó là chỗ hai task doc gặp nhau.>

## Bản đồ vùng liên quan
<tên thật của mọi thứ đụng tới — endpoint, hàm, bảng, component, job — mỗi dòng
một mục kèm đường dẫn. Đây là phần bù cho việc người hỏi không thuộc cấu trúc.>

## Tiền đề sai trong brief
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

## File nên upload lên web
| File | Số dòng | Vì sao cần cả file (không trích được) |
|---|---|---|
<chỉ liệt kê file thật sự cần; xem ngưỡng ở §11>

## Điều brief không hỏi nhưng ảnh hưởng tới thiết kế
<tối đa 5 mục — ràng buộc, va chạm, nợ kỹ thuật chắn đường>

## Chưa xác định được
<cái gì, vì sao, cần gì để xác định>
````

Ràng buộc khi viết file này:

- **Câu `[ĐỊNH VỊ]` là việc đi tìm, không phải việc đoán.** Tìm không ra thì nói rõ đã tìm ở đâu, bằng từ khoá gì.
- **Chỉ ghi cái đã đọc thấy.** Suy đoán phải gắn nhãn "giả thiết", đặt riêng, không trộn vào phần bằng chứng.
- **Tự chứa** — người đọc bên web không mở được repo, nên trích đủ code để hiểu.
- **Không thiết kế, không viết code tính năng** ở bước này.
- Trả lời hết mọi câu, kể cả khi câu trả lời là "chỗ này chưa có gì cả".
- Nếu phát hiện `repo-map.md` đã lệch thực tế, **sửa luôn dòng sai trong đó** và ghi một dòng vào mục tóm tắt.
- **Cập nhật `trang-thai.md`** (§13) trước khi kết thúc lượt.

## 11. Upload file code lên web

Bản đồ trả lời "có cái gì"; file thật trả lời "chạy thế nào". Khi web cần cái thứ hai, upload rẻ hơn nhiều so với bắt Claude Code trích dài.

**Ngưỡng chọn:**

| Tình huống | Cách làm |
|---|---|
| Hiểu được bằng ≤ 25 dòng | Claude Code trích thẳng vào `02-findings.md` |
| Cần đọc cả luồng, cả file, hoặc nhiều hàm liên quan nhau | **Upload file** — Claude Code ghi vào mục "File nên upload lên web" |
| File rất dài | Vẫn upload cả file, nhưng Claude Code nói rõ "đọc từ dòng A–B" |

**Tuyệt đối không upload:** `.env`, `.env.local`, `*.key`, `*.pem`, dump cơ sở dữ liệu, log có dữ liệu người dùng thật, bất kỳ file nào chứa token hoặc khoá API thật.
Cần cho web thấy cấu hình thì upload `frontend/.env.example` hoặc `backend/services/api/src/bookforge_api/core/settings.py` — hai file này chỉ có **tên biến và giá trị mặc định**, không có khoá.

**Sau khi upload, web được nới một luật:** được nói tên hàm, biến, kiểu dữ liệu **có trong file đã upload**.
Vẫn cấm suy ra nội dung file khác — thiếu file nào thì web ghi vào mục "Cần upload thêm", bạn upload tiếp hoặc đưa vào brief vòng sau.

## 12. Hỏi nhanh lúc thi công — `qa.md`

Đây là vòng lặp bạn dùng nhiều nhất: tôi đang viết code, gặp ràng buộc hoặc cần bạn quyết, bạn không hiểu chỗ đó, bạn mang sang web hỏi.

**Nghĩa vụ của Claude Code khi hỏi:** viết câu hỏi ở dạng **tự chứa** — đủ ngữ cảnh, có trích đoạn code liên quan, nói rõ đang bị chặn ở đâu, và nêu sẵn các phương án nếu có.
Bạn phải dán được thẳng sang web mà không phải giải thích thêm câu nào.
Không dùng từ viết tắt nội bộ. Câu chỉ cần "có/không" thì hỏi thẳng bạn, đừng đẩy sang web.

**Prompt dán ở web trước câu hỏi** (2 dòng cố định):

```text
Đây là câu hỏi/ràng buộc do agent đang viết code trong repo BookForge nêu ra.
Giải thích cho tôi bằng lời dễ hiểu, nêu 2 lựa chọn kèm đánh đổi, rồi khuyến nghị một cái.
```

**Khuôn một mục trong `qa.md`** (ghi nối tiếp, mới nhất xuống dưới):

```text
## <YYYY-MM-DD> — <câu hỏi tóm trong một dòng>

**Người hỏi:** Claude Code | Bạn
**Bối cảnh:** <file:line, hoặc đang ở bước nào của task doc>

**Câu hỏi (dán sang web):**
<khối tự chứa — ngữ cảnh + trích code + đang chặn cái gì + phương án nếu có>

**Web trả lời:** <tóm tắt 3–8 dòng, giữ phần đánh đổi>
**Chốt:** <quyết định cuối + đã ghi vào task doc nào>
```

**Luật chống mất mát:** `qa.md` là **nhật ký**, task doc mới là **nguồn sự thật**.
Mọi quyết định chốt ở web phải được chép về mục "Quyết định đã chốt" của task doc, nếu không vài hôm sau không ai nhớ vì sao làm như vậy.

## 13. `trang-thai.md` — hồi phục khi đổi tài khoản web

Web hết token, đổi tài khoản, mất sạch ngữ cảnh. File này để dán một lần là chạy tiếp được.

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

**Prompt hồi sức** — mở chat web mới, dán khối này, rồi dán prompt §6, rồi dán `trang-thai.md`:

```text
Tôi đang tiếp tục một việc dở bằng tài khoản mới, bạn chưa có ngữ cảnh gì.
Dưới đây là prompt giao thức, rồi tới file trạng thái của việc đó.
Đọc xong, nói lại trong 5 dòng bạn hiểu đang ở đâu và bước tiếp theo là gì, rồi chờ tôi.
```

Mẹo vận hành: **hỏi câu nặng nhất ngay đầu phiên web**, đừng để dồn tới lúc sắp hết token.

## 14. Quy tắc tiết kiệm token

- **Lưu file, đừng dán vào terminal.** Dán 300 dòng brief vào Claude Code tốn đúng bằng lúc nó tự đọc file, nhưng mất lịch sử và không sửa lại được.
- **Cập nhật bản đồ theo diff, không sinh lại.** Diff rỗng thì dừng ngay (§3).
- **Dán gói ngữ cảnh theo phạm vi** (§4) — làm FE thì đừng dán bản đồ backend.
- **Upload file cho web đọc** thay vì bắt Claude Code trích dài (§11).
- **Mọi phần giảng giải đẩy sang web** (§12) — Claude Code trả lời ngắn, có bằng chứng, không giảng bài.
- **Một thư mục research cho một tính năng**; ngữ cảnh nằm ở file, không nằm ở chat.
- **Đóng khung phạm vi đọc ngay trong brief** ("chỉ mảng quota", "chỉ `services/jsxgraph/`").
- **Gộp câu hỏi thành một lượt.** Hỏi lắt nhắt mỗi lần vài câu là cách đốt token nhanh nhất.

## 15. Checklist

**Mỗi sáng**

- [ ] Đã gõ câu cập nhật bản đồ **kèm ref muốn lấy** (§3); nếu có thay đổi, đã dán phần "hôm nay đổi gì" vào chat web đang mở.
- [ ] Header hai file map ghi đúng SHA, **ref** và ngày — và ref đó đúng là nhánh bạn muốn bản đồ phản ánh.

**Mỗi tính năng**

- [ ] Đã tạo `tech_docs/research/<slug>/` và viết `00-mo-ta.md`, có dòng **Phía**.
- [ ] Đã dán gói ngữ cảnh **đúng phạm vi** (§4) vào chat web.
- [ ] Brief từ web không chứa tên file/hàm/bảng nào ngoài bản đồ đã dán; thứ chưa biết nằm ở câu `[ĐỊNH VỊ]`; có "Cần trích nguyên văn" và "Ngưỡng dừng".
- [ ] `02-findings.md` có **"Phía nào phải sửa"**, **"Bản đồ vùng liên quan"**, **"File nên upload lên web"**, trả lời đủ số câu, câu nào cũng có `file:line`.
- [ ] Tiền đề sai của brief đã được sửa lại bằng cái thật, không bỏ lửng.
- [ ] Bảng "giả định đúng/sai" đã điền.
- [ ] Chốt xong: task doc ở `backend/docs/tasks/` — **hai file nếu đụng cả hai phía** (§5), có "Quyết định đã chốt" + DoD.
- [ ] Task doc **không chứa chuỗi `tech_docs`** và đọc trọn vẹn được bởi người chỉ có repo triển khai (§5).

**Khi thi công**

- [ ] Câu hỏi của Claude Code **tự chứa**, dán sang web được ngay.
- [ ] Đã ghi vào `qa.md`, và **quyết định đã chép về task doc**.
- [ ] `trang-thai.md` được cập nhật ở mọi lượt Claude Code chạy.
- [ ] Không upload file chứa khoá/token lên web (§11).
- [ ] Không tự tạo file trong `specs/` hoặc `audits/`.
