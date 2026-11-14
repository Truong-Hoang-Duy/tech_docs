# Review of `feat/glossary-toggle-only` — Round 1 (`f26feec6` + `18fd8a5e`)

> **How to read this document:**
> - **🔴 Blockers (Section 1)** must be resolved before this branch can be approved. Every item carries a concrete executed reproduction, contract trace (`caller -> line -> input -> outcome`), or merge/rebase obligation.
> - **🟡 Should-fix (Section 2)** are correctness and contract-documentation gaps in the touched surface to close in the same pass.
> - **🟢 Nits (Section 3)** are non-blocking checks; they never trigger another review round on their own.
> - **Analysis and proposed fixes are technical suggestions.** The only mandatory contract is the **Definition of Done (Section 4)**. If you prefer a simpler or cleaner implementation that satisfies the DoD, feel free to use it or align before coding.
> - **Bidirectional Boundary Closure ($P \land \neg P$):** For each fix, lock both the failing counterexample ($P$) and the complementary boundary ($\neg P$) with runnable Pytest / Vitest assertions before committing. Once all DoD items pass (`🔴 Blockers = 0`), Round 2 approves immediately without further review loops.
> - Open this file with `bookforge` on `origin/feat/glossary-toggle-only` (`f26feec6`) and `bookforge-fe` on `origin/feat/glossary-toggle-only` (`18fd8a5e`) so all `file:line` references resolve directly.

| | |
| :--- | :--- |
| **Author** | `duyth` (`truonghoangduy.work@gmail.com`) |
| **Backend (`bookforge`)** | `origin/feat/glossary-toggle-only` (`f26feec652d020ef5283e5d9a50f833443c74703`, 1 commit / 13 files changed, `+1,464 / -73` lines; merge-base `a5d3fce1`, **43 commits behind `origin/dev` `af4b3933`** with a conflict in `pydantic_text_provider.py` + semantic rail drift in `school_glossary.py`) |
| **Frontend (`bookforge-fe`)** | `origin/feat/glossary-toggle-only` (`18fd8a5ea8a824796cf81ae37530e176d1c5f323`, 1 commit / 14 files changed, `+146 / -636` lines; merge-base `6a32c01d`, **41 commits behind `origin/dev` `91ffb5d1`** with conflicts in 8 files) |
| **Verdict** | **Request Changes** (`5 🔴 Blockers`, `2 🟡 Should-fix`, `2 🟢 Nits`) |
| **Summary** | Mechanical lint, typecheck, and existing unit gates pass on the isolated branch heads; keeping `glossary_ids` optional/accepted on the wire preserves backward compatibility with cached sessions and rollout windows; FE removes `-490` net lines of manual picker chrome while preserving the read-only `Từ điển chuyên ngành: Toàn bộ` badge for `agent-dich-hoc-thuat`; and auto-resolution reuses the in-memory `_AcademicGlossaryIndex`. Before merge, we need to fix silent zero-subject drops across specialist agents and subjectless `chung` prompts, restore 55+ bilingual `Phrase / SingleWord` synonyms broken by `extract_headword_variants`, stop Flow `run_flow_action` from hijacking History/Biology mindmaps into Math combinatorics via `[n-1]` scaffolding while wiring `context_settings` + workspace defaults, and cleanly rebase both repos onto `origin/dev` without dropping upstream features. |

---

## 0. Baseline Mechanical Gates (`f26feec6` + `18fd8a5e`)

Executed in detached review worktrees of `bookforge` (`f26feec6`) and `bookforge-fe` (`18fd8a5e`):

```text
# Backend (bookforge @ f26feec6)
uv run --directory services/api ruff check .                              Pass (All checks passed!)
uv run --directory services/api ruff format --check .                     Pass (1204 files already formatted)
uv run --directory services/api alembic heads                             Pass (0137_internal_support_admin (head))
uv run --directory services/api pytest -n0 tests/test_school_glossary.py  Pass (18 passed in 42.25s)
uv run --directory services/api pytest -n0 \
  tests/test_question_cards_generate_api.py \
  tests/test_errors_openapi.py \
  tests/test_feature_guardrails.py \
  tests/test_editor_assistant.py \
  tests/test_flow_artifacts.py \
  tests/test_chat_modes_workspace_enabled.py -q                           Pass (105 passed in 30.17s)
git merge-tree --write-tree origin/dev origin/feat/glossary-toggle-only   FAIL (CONFLICT in 1 file: pydantic_text_provider.py + semantic rail drift in school_glossary.py)

# Frontend (bookforge-fe @ 18fd8a5e)
npx tsc --noEmit                                                          Pass (0 errors)
npx eslint <all 14 modified files>                                        Pass (0 errors, 0 warnings)
npx vitest run \
  src/components/TiptapEditor/agent-settings/AgentSettings.test.tsx \
  src/components/TiptapEditor/agent-settings/agent-settings-model.test.ts \
  src/components/TiptapEditor/partial/document-ai-chat-panel-agent-settings.test.tsx \
  src/hooks/use-chat-modes.test.tsx \
  src/templates/HomePage/index.test.tsx \
  src/templates/HomePage/partials/use-chat-with-ai.test.tsx \
  src/templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.test.tsx \
  src/templates/QuestionBankPage/components/mass-generate/mass-generate-payload.test.ts \
  src/templates/SchoolRulesPage/SchoolRulesPage.test.tsx                  Pass (9 files / 117 tests passed in 9.25s)
git merge-tree --write-tree origin/dev origin/feat/glossary-toggle-only   FAIL (CONFLICT in 8 files)
```

---

## 1. 🔴 Blockers (Must Fix Before Merge)

### 🔴 1. Specialist Agents (`Ma trận đề`, `Infographic`, `Phiếu điền khuyết`, `Đề kiểm tra`) Drop Subject Glossary Terms on Composite Subjects (`KHTN`, `Lịch sử và Địa lí`, `GDCD`), Empty Subject Hints, or `chung`-Matching Titles

- **Locations:**
  - Shared primitive: [`services/api/src/bookforge_api/services/school_glossary.py:1583-1702`](../../services/api/src/bookforge_api/services/school_glossary.py#L1583-L1702) (`lookup_lesson_glossary`)
  - Specialist callers:
    - [`services/api/src/bookforge_api/chat/ma_tran_de_agent.py:563-579`](../../services/api/src/bookforge_api/chat/ma_tran_de_agent.py#L563-L579) (`_build_matrix_glossary_block`)
    - [`services/api/src/bookforge_api/chat/infographic_agent.py:1200-1217`](../../services/api/src/bookforge_api/chat/infographic_agent.py#L1200-L1217) (`_build_infographic_glossary_block`)
    - [`services/api/src/bookforge_api/chat/phieu_dien_khuyet_agent.py:425-442`](../../services/api/src/bookforge_api/chat/phieu_dien_khuyet_agent.py#L425-L442) (`_build_lesson_glossary_block`)
    - [`services/api/src/bookforge_api/chat/de_kiem_tra_agent.py:123-129`](../../services/api/src/bookforge_api/chat/de_kiem_tra_agent.py#L123-L129) (`expand_topic_tokens_with_glossary`)
- **What happens:**
  1. All specialist builders call `svc.lookup_lesson_glossary(..., glossary_ids=None)` and guard the new `resolve_auto_glossary_terms(...)` call behind `if not terms:`.
  2. Inside `lookup_lesson_glossary`, `inferred_subject, inferred_grade = parse_subject_and_grade(combined)` (`line 1601`) only recognizes single THPT subject names — it returns `(None, None)` for `'Khoa học tự nhiên'`, `'KHTN'`, `'GDCD'`, `'Giáo dục công dân'`, `'Tiếng Việt'`, or `''`, and returns `('dia_ly', None)` for `'Lịch sử và Địa lí'` (dropping `'lich_su'`).
  3. When `glossary_ids is None` and `inferred_subject is None`, `lookup_lesson_glossary` sets `active_domains = ['chung']` and `target_subjects = []` (`lines 1609-1618`). Step 3 then matches ubiquitous specialist words (`'KIỂM TRA ĐỊNH KÌ'`, `'MA TRẬN ĐỀ KIỂM TRA'`, `'Yêu cầu cần đạt'`, `'Đánh giá năng lực'`) against `chung` (`16` rows), returning `>= 1` `chung` term so `if not terms:` is `False` and `resolve_auto_glossary_terms` **never executes**.
- **Executed counterexample proof (on `f26feec6`):**
  - `_build_matrix_glossary_block(MaTranDeInput(exam_title='KIỂM TRA ĐỊNH KÌ GIỮA KÌ I', subject_and_grade='Khoa học tự nhiên', scope_description='Biến thiên enthalpy của phản ứng và tốc độ phản ứng'), ...)` returned **only** 3 `chung` terms (`Đánh giá định kì`, `Ma trận đề kiểm tra`, `Bản đặc tả đề kiểm tra`) and **0 `hoa_hoc` terms**.
  - `_build_matrix_glossary_block(MaTranDeInput(exam_title='KIỂM TRA ĐỊNH KÌ', subject_and_grade='', scope_description='Biến thiên enthalpy của phản ứng và định luật Lenz'), ...)` returned **only** `chung` terms and **0 subject terms**.
  - `_build_infographic_glossary_block` on `topic_or_lesson='Yêu cầu cần đạt về Operon Lac và phiên mã'`, `subject_and_grade=''` returned **only** `Yêu cầu cần đạt` (`chung`) and **0 `sinh_hoc` terms**.
  - `_build_lesson_glossary_block` on `lesson_title='Đánh giá năng lực qua bài toán đạo hàm và cực trị hàm số'`, `subject_and_grade=''` returned **only** `Đánh giá năng lực` (`chung`) and **0 `toan` terms**.
- **Suggested fix (shared primitive + sibling callers):**
  1. In `lookup_lesson_glossary` (`school_glossary.py:1600-1625`), resolve `subject_and_grade` through `expand_glossary_domains(resolve_question_subject_glossary_ids(subject_and_grade), glossary_enabled=True)` (plus `parse_subject_and_grade(combined)` for grade and fallback subject extraction) so composite subjects (`Khoa học tự nhiên` -> `vat_ly`, `hoa_hoc`, `sinh_hoc`; `Lịch sử và Địa lí` -> `lich_su`, `dia_ly`; `GDCD` -> `gdktpl`) populate `target_subjects` and `active_domains`.
  2. In `_build_matrix_glossary_block`, `_build_infographic_glossary_block`, and `_build_lesson_glossary_block`, trigger `resolve_auto_glossary_terms` whenever `not any(t.get('subject_key') != 'chung' for t in terms)` (not just `if not terms:`), and merge deduplicated subject + `chung` terms (and conventions) up to `limit`.
  - **Boundary check ($P \land \neg P$):**
    - Target case ($P$): `MaTranDeInput(exam_title='KIỂM TRA ĐỊNH KÌ GIỮA KÌ I', subject_and_grade='Khoa học tự nhiên', scope_description='Biến thiên enthalpy của phản ứng')` includes both `Ma trận đề kiểm tra` (`chung`) and `Biến thiên enthalpy chuẩn của phản ứng` (`hoa_hoc`).
    - Complementary boundary ($\neg P$): A pure general-pedagogy specialist request with no subject concepts (`'Hướng dẫn xây dựng kế hoạch bài dạy và yêu cầu cần đạt'`) returns only `chung` terms without hallucinating unrelated subject terms.

---

### 🔴 2. Any `chung` Pedagogical Term in a Subjectless Prompt Suppresses Sub-Headword Subject Fallback (`enthalpy`, `nhị phân`) and Hard-Locks `allowed_subjects = {'chung'}`

- **Locations:**
  - [`services/api/src/bookforge_api/services/school_glossary.py:1443-1458`](../../services/api/src/bookforge_api/services/school_glossary.py#L1443-L1458) (`_AcademicGlossaryIndex.scan_passage`)
  - [`services/api/src/bookforge_api/services/school_glossary.py:2148-2160`](../../services/api/src/bookforge_api/services/school_glossary.py#L2148-L2160) (`SchoolGlossaryService.resolve_auto_glossary_terms`)
- **What happens:**
  1. In `scan_passage`, hits against `chung` add score `>= 8.0` into `scores` **without** incrementing `subject_votes`. Yet `has_strong_hit = any(sc >= 8.0 for sc in scores.values())` (`line 1443`) treats a `chung` hit as a strong domain hit and skips both `scientific_subtoken_map` (`enthalpy`, `operon`, `thylakoid`, ...) and `vi_compound_subgram_map` (`nhị phân`, ...).
  2. Even if `query_fts` later runs, `resolve_auto_glossary_terms` checks `elif any(sc >= 8.0 for sc in p_scores.values()): allowed_subjects = {'chung'}` (`lines 2158-2159`), hard-locking filtering to `chung` alone whenever `p_votes` is empty and a `chung` term scored `>= 8.0`.
- **Executed counterexample proof (on `f26feec6`):**
  - `svc.resolve_auto_glossary_terms('Giải thích ngắn gọn khái niệm enthalpy', glossary_enabled=True)` -> returns **6 `hoa_hoc` terms** (`Enthalpy tạo thành chuẩn`, `Biến thiên enthalpy chuẩn của phản ứng`, ...).
  - Adding one `chung` pedagogical phrase (`'Nêu yêu cầu cần đạt khi dạy về enthalpy'`) -> returns `terms=['Yêu cầu cần đạt']` (`chung`), **0 `hoa_hoc` terms**.
  - `svc.resolve_auto_glossary_terms('Xây dựng kế hoạch bài dạy về nhị phân', glossary_enabled=True)` -> returns `terms=['Kế hoạch bài dạy']` (`chung`), **0 `tin_hoc` terms**.
- **Suggested fix:**
  1. In `scan_passage` (`school_glossary.py:1443`), check non-`chung` hits only: `has_strong_subject_hit = any(sc >= 8.0 and str(self.terms[tid].get('subject_key') or '') != 'chung' for tid, sc in scores.items())` before skipping `scientific_subtoken_map` and `vi_compound_subgram_map`.
  2. In `resolve_auto_glossary_terms` (`lines 2158-2159`), remove the `elif any(sc >= 8.0 for sc in p_scores.values()): allowed_subjects = {'chung'}` lock so the subsequent `query_fts` partial-headword pass remains free to recover subject terms alongside `chung`.
  - **Boundary check ($P \land \neg P$):**
    - Target case ($P$): `'Nêu yêu cầu cần đạt khi dạy về enthalpy'` and `'Xây dựng kế hoạch bài dạy về nhị phân'` return both the `chung` term and the matching `hoa_hoc` / `tin_hoc` terms.
    - Complementary boundary ($\neg P$): Casual/pedagogical chat with no academic sub-tokens (`'Giải thích khái niệm yêu cầu cần đạt trong GDPT 2018'`) still returns only `chung` terms.

---

### 🔴 3. Regression in Shared `extract_headword_variants` Breaks 55+ Bilingual `"Phrase / SingleWord"` Synonyms in `Agent Dịch học thuật` (`search_academic_glossary`)

- **Location:**
  - [`services/api/src/bookforge_api/services/school_glossary.py:701-711,783-787`](../../services/api/src/bookforge_api/services/school_glossary.py#L701-L711) (`extract_headword_variants`)
- **What happens:**
  1. To stop splitting compact unit ratios like `"Thông khí phổi/phút"` into bare `"phút"`, lines `705-709` added:
     ```python
     rest_slash = src[idx_ch + 1 :].strip() if ch == '/' else ''
     if ch == '/' and ' ' in piece and rest_slash and ' ' not in rest_slash and '(' not in rest_slash:
         buf.append(ch)
         idx_ch += 1
         continue
     ```
     Because `rest_slash` calls `.strip()`, **spaced bilingual slash synonyms (`A B / C`)** match `' ' in piece and ' ' not in rest_slash` and no longer split! Across the 6,831-term seed corpus, **63 headwords changed**, ~55 of which are top-level English equivalents (`'Temperature and precipitation chart / Climograph'`, `'Fairy tale / Folktale'`, `'New nobility / Gentry'`, `'Point of view / Perspective'`, `'Argumentative point / Claim'`, `'fat and oil / triglyceride'`, `'trace element / micronutrient'`, `'matter exchange / metabolism'`). Neither side is indexed separately in `porter_ngram_map`.
  2. Inside parentheses (`line 783`), `'Đồng phân hình học (geometric isomers (*cis-* / *trans-* isomers))'` splits into malformed fragments `'geometric isomers (*cis'` and `'trans-* isomers)'`.
- **Executed counterexample proof (on `f26feec6`):**
  - `extract_headword_variants('Temperature and precipitation chart / Climograph')` returns `['Temperature and precipitation chart / Climograph']`.
  - `svc.search_academic_glossary(passage_text='Analyze the temperature trends shown in this climograph and folktale study.')` returns **`[]` (0 matched terms)**, regressing [`docs/superpowers/specs/2026-11-12-dich-hoc-thuat-glossary-search-design.md`](../superpowers/specs/2026-11-12-dich-hoc-thuat-glossary-search-design.md) AC-2.
- **Suggested fix:**
  Only suppress `/` splitting when `/` is **unspaced** (directly attached on both sides: `idx_ch > 0 and not src[idx_ch - 1].isspace() and idx_ch + 1 < n_src and not src[idx_ch + 1].isspace()`) for compact unit/ratio tokens (`phổi/phút`, `S/V`, `G1/S`, `m/s`), keep spaced ` / ` alternative delimiters splitting cleanly both top-level and inside `paren_groups`, and strip `*` around sub-variants cleanly.
  - **Boundary check ($P \land \neg P$):**
    - Target case ($P$ — unit ratios preserved): `'Thông khí phổi/phút'` and `'Thông khí phút (thể tích khí lưu thông qua phổi/phút)'` never emit standalone `'phút'`; `'tỉ lệ S/V'` never emits standalone `'V'`.
    - Complementary boundary ($\neg P$ — bilingual synonyms restored): `search_academic_glossary` on `'... climograph and folktale ...'` matches both *Biểu đồ nhiệt độ và lượng mưa* (`dia_ly`) and *Truyện cổ tích* (`ngu_van`).

---

### 🔴 4. Flow `run_flow_action` Injects 15 Math Combinatorics Terms into History/Biology Mindmaps (via `_flow_selection_hint` `[n-1]` Scaffolding) AND Lacks `context_settings` Wiring + Workspace Default Fallback

- **Locations:**
  - Backend:
    - [`services/api/src/bookforge_api/chat/flow_agent.py:749-773,1020-1026,1184-1190`](../../services/api/src/bookforge_api/chat/flow_agent.py#L749-L773) (`_resolve_flow_glossary_block`, `run_flow_action`, `run_flow_chat_edit`)
    - [`services/api/src/bookforge_api/chat/editor_agent.py:487-506`](../../services/api/src/bookforge_api/chat/editor_agent.py#L487-L506) (`run_editor_assistant`)
    - Reference helper: [`services/api/src/bookforge_api/services/regulations.py:717-738`](../../services/api/src/bookforge_api/services/regulations.py#L717-L738) (`resolve_effective_context_settings`)
  - Frontend (`bookforge-fe`):
    - [`src/templates/FlowArtifactPage/index.tsx:2369-2382`](../../../bookforge-fe/src/templates/FlowArtifactPage/index.tsx#L2369-L2382) (`APIRunFlowAiActionWithEngine` call)
    - [`src/api/flow-artifacts-api.ts:60-72,374-393`](../../../bookforge-fe/src/api/flow-artifacts-api.ts#L374-L393) (`TFlowAiActionRequest`, `APIRunFlowAiAction`)
    - [`src/templates/HomePage/partials/use-chat-with-ai.ts:980-1015`](../../../bookforge-fe/src/templates/HomePage/partials/use-chat-with-ai.ts#L980-L1015) (`/mindmap` slash handler)
    - [`src/templates/HomePage/partials/chat-mindmap-slash.ts:518-528`](../../../bookforge-fe/src/templates/HomePage/partials/chat-mindmap-slash.ts#L518-L528) (`executeChatMindmapSlashCommand`)
- **What happens (two compounding bugs):**
  1. **Prompt-scaffolding subject hijack (`flow_agent.py:1020-1026`):** `run_flow_action` passes `selection_block` (`_flow_selection_hint(...)`) into `_resolve_flow_glossary_block`. That prompt wrapper contains `"=== CẤU TRÚC SƠ ĐỒ HIỆN TẠI ===\nTổng số thẻ: ... | Tổng số liên kết: ..."` and generated IDs `- [n-1] ... id="n-1" (type="...")`. Inside `scan_passage`, `n-1` hits 5 Math sequence/combinatorics entries (`Hoán vị`, `Giai thừa`, `Chỉnh hợp`, `Số hạng tổng quát của cấp số cộng`, `Tổng của n số hạng đầu của cấp số cộng` -> `+40` phantom `toan` votes), `"Sơ đồ"` adds `+12 ngu_van`, and `"liên kết"` / `"type"` add `+17 tin_hoc`, overriding the actual mindmap topic whenever `cnt * 3 < 40 * 2`.
  2. **Unwired `ai-action` / `/mindmap` callers + skipped workspace defaults:** On FE, `APIRunFlowAiActionWithEngine` and `/mindmap` never pass `context_settings`. Meanwhile on BE, both `flow_agent.py:754` (`if context_settings is None: return ''`) and `editor_agent.py:490` (`if context_settings is not None:`) return `''` when `context_settings is None`, ignoring the workspace's `default_context_settings_json` from `/school-rules` — unlike `resolve_active_regulations(db, user, context_settings)` one line above them, which calls `resolve_effective_context_settings(db, organization_id, context_settings)`.
- **Executed counterexample proof (on `f26feec6`):**
  - Mindmap `'Chiến tranh lạnh (1947-1989)'`, target node `n-2` (`'Sự đối đầu Đông - Tây — Trật tự hai cực Ianta sau Thế chiến II'`):
    - With `selection_block`: returned `['Hoán vị', 'Giai thừa', 'Chỉnh hợp', 'Số chính phương', ...]` (**15 `toan` terms, 0 `lich_su` terms**).
    - With clean node text only: returned `['Chiến tranh lạnh', 'Xu hướng hoà hoãn Đông – Tây', 'Đa cực', 'Trật tự thế giới hai cực I-an-ta', ...]`.
  - Mindmap `'Operon Lac ở vi khuẩn E. coli'`, target node `n-2` (`'Cấu trúc Operon Lac'`):
    - With `selection_block`: returned **15 `toan` terms, 0 `sinh_hoc` terms**.
    - With clean node text only: returned `['Operon', 'Gene cấu trúc', 'Vùng điều hoà', 'Codon', ...]`.
  - Casual mindmap `'Kế hoạch dã ngoại cuối tuần'` (`n-1`):
    - With `selection_block`: injected 13 `toan` / `chung` terms into a non-academic flow!
- **Suggested fix:**
  1. **BE (`flow_agent.py` & `editor_agent.py`):**
     - Never pass `selection_block` to `_resolve_flow_glossary_block`. Extract clean user text instead (`payload.title`, `payload.selected_text`, plus node `title` and `_clean_plain_description(node.description)` in `run_flow_action` and `run_flow_chat_edit`).
     - Pass `user` (or `organization_id`) into `_resolve_flow_glossary_block` and resolve `eff_ctx = resolve_effective_context_settings(db, _resolve_user_org_id(user), context_settings)` in both `flow_agent.py` and `editor_agent.py`.
  2. **FE (`bookforge-fe`):**
     - Pass `context_settings: toChatContextSettings(loadAgentSettings("mindmap"))` in `APIRunFlowAiActionWithEngine` (`FlowArtifactPage/index.tsx:2369-2382`), and pass `context_settings: outgoingContextSettings` into `executeChatMindmapSlashCommand` (`use-chat-with-ai.ts:981` -> `chat-mindmap-slash.ts:518-528`, matching `/image` at `line 1170`).
  - **Boundary check ($P \land \neg P$):**
    - Target case ($P$): `run_flow_action` on `'Chiến tranh lạnh (1947-1989)'` with node IDs `n-1`, `n-2` injects `lich_su` terms and zero `toan` terms; casual `'Kế hoạch dã ngoại cuối tuần'` injects `''`; omitting `context_settings` on a workspace whose `/school-rules` default has `glossary_enabled=True` applies the org default.
    - Complementary boundary ($\neg P$): Explicit `context_settings={"glossary_enabled": false}` overrides a `True` org default and injects `''`.

---

### 🔴 5. Rebase onto Latest `origin/dev` and Preserve Upstream Features Across Both Repos (`43` BE / `41` FE Commits Behind)

Both branches must be rebased onto the latest `origin/dev` (`git fetch origin` first) and verified with `git diff origin/dev...HEAD` on every conflicted file so zero upstream hunks are silently dropped:

1. **Backend (`bookforge`, 43 commits behind `origin/dev` `af4b3933`):**
   - [`services/api/src/bookforge_api/llm/pydantic_text_provider.py:167-198`](../../services/api/src/bookforge_api/llm/pydantic_text_provider.py#L167-L198) (**Merge conflict**): `origin/dev` added `FREE_CHAT_CONFLICT_INSTRUCTION` in `answer_without_context`, while this branch added `glossary_section` / `glossary_suffix`. Keep **both**.
   - [`services/api/src/bookforge_api/services/school_glossary.py:2048-2055`](../../services/api/src/bookforge_api/services/school_glossary.py#L2048-L2055) (**Orthography rail drift**): `origin/dev` commit `4e6af8ad` updated `format_glossary_prompt_block`'s default `header` to `'TỪ ĐIỂN THUẬT NGỮ SGK VÀ SƯ PHẠM CHUẨN...'` (`VÀ` instead of `&`, enforced by the no-ampersand prompt suite `tests/test_agent_conflict_and_orthography.py`). Keep `'VÀ'` on rebase and update any branch assertions expecting `&`.
2. **Frontend (`bookforge-fe`, 41 commits behind `origin/dev` `91ffb5d1` — 8 Conflicted Files):**
   - [`src/components/TiptapEditor/agent-settings/AgentContextSettingsDialog.tsx`](../../../bookforge-fe/src/components/TiptapEditor/agent-settings/AgentContextSettingsDialog.tsx): Preserve `origin/dev` (`57f1bedf`) `withWorkspacePrefix("/school-rules")` link while keeping toggle-only glossary UI.
   - [`src/templates/HomePage/index.tsx`](../../../bookforge-fe/src/templates/HomePage/index.tsx): Preserve `origin/dev` (`6a58d5b8`) `QuestionGenerateHandoffCard` while keeping `areChatContextSettingsEqual`.
   - [`src/templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.tsx`](../../../bookforge-fe/src/templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.tsx): Preserve **all three** `origin/dev` additions (`0c164c8a` URL handoff `initialPrefill`, `55205e80` `writableFolders` RBAC policy, and inline quick-folder creation) while removing manual glossary chip UI.
   - [`src/components/ModalSettings/index.tsx`](../../../bookforge-fe/src/components/ModalSettings/index.tsx): Reconcile `origin/dev` (`8fa39a86`) layout adjustments with the toggle-only glossary row.
   - [`src/hooks/use-chat-modes.ts`](../../../bookforge-fe/src/hooks/use-chat-modes.ts) & [`src/hooks/use-chat-modes.test.tsx`](../../../bookforge-fe/src/hooks/use-chat-modes.test.tsx): Keep `origin/dev` (`f05cfd24`) module-level `EMPTY_MODES` / `EMPTY_EXPERTS` / `EMPTY_AGENTS` constants so `query.data === undefined` never allocates per hook instance.
   - [`src/components/TiptapEditor/agent-settings/AgentSettings.test.tsx`](../../../bookforge-fe/src/components/TiptapEditor/agent-settings/AgentSettings.test.tsx) & [`src/components/TiptapEditor/partial/document-ai-chat-panel-agent-settings.test.tsx`](../../../bookforge-fe/src/components/TiptapEditor/partial/document-ai-chat-panel-agent-settings.test.tsx): Reconcile conflict hunks cleanly and keep toggle-only + workspace-prefix coverage intact.

---

## 2. 🟡 Should-fix (High-Value Improvements in Scope)

### 🟡 1. Multi-Turn Follow-Up Context in Free & Agentic Chat

- **Locations:**
  - [`services/api/src/bookforge_api/api/chat.py:1553-1560`](../../services/api/src/bookforge_api/api/chat.py#L1553-L1560) (`_run_free_chat`)
  - [`services/api/src/bookforge_api/chat/adk_agent.py:1031-1041`](../../services/api/src/bookforge_api/chat/adk_agent.py#L1031-L1041) (`_build_chat_agent`)
- **What happens:**
  Both entrypoints pass only the current turn `query` (plus `attached_text[:1500]` in `adk_agent.py`) into `resolve_auto_glossary_prompt_block`. On follow-up turns such as Turn 1: *"Phân tích quá trình nguyên phân và giảm phân (Sinh học 10)"* -> Turn 2: *"Tạo cho tôi 3 câu hỏi vận dụng về phần này"*, Turn 2 contains no subject terms, so subject glossary support vanishes on the exact turn generating the assessment items.
- **Suggested fix:**
  Include the last 1–2 prior user messages from `history` (capped, after `query` so current-turn keywords take priority) and session document titles when building `lookup_text` for `resolve_auto_glossary_prompt_block`.

### 🟡 2. Update Stale Frontend Contract Doc (`docs/frontend/chat-glossary-context.md`)

- **Location:**
  - [`docs/frontend/chat-glossary-context.md:11-60`](../frontend/chat-glossary-context.md#L11-L60)
- **What happens:**
  The contract handoff doc still specifies the removed 12-option `Khác...` checkbox picker, `glossary_enabled: true` default, `Từ điển: Toán học +1` badge copy, and `khtn` 3-subject checkbox sync rules, which now contradict both `bookforge` and `bookforge-fe`.
- **Suggested fix:**
  Update `docs/frontend/chat-glossary-context.md` to document toggle-only UX (`glossary_enabled: false` default, `Từ điển sư phạm: Đang bật` / `Từ điển: Tắt`, `Từ điển chuyên ngành: Toàn bộ` for `agent-dich-hoc-thuat`, optional/accepted `glossary_ids` on the wire for backward compatibility, and automatic backend subject resolution).

---

## 3. 🟢 Nits (Optional Verification — Non-Blocking)

- **🟢 1. `SchoolRulesPage` Parity Check After FE Rebase:** `origin/dev` (`3b577bd6`) adjusted `SchoolRulesPage` around `default_context_settings`; confirm [`src/templates/SchoolRulesPage/SchoolRulesPage.test.tsx`](../../../bookforge-fe/src/templates/SchoolRulesPage/SchoolRulesPage.test.tsx) still passes cleanly after rebasing onto `origin/dev`.
- **🟢 2. Specialist Partial-Run Synthesis (`adk_agent.py`):** Confirmed `_synthesize_from_partial_run` stays safe with the current change; no extra changes needed there.

---

## 4. Definition of Done (DoD)

- [ ] **Rebase & upstream-drop audit (`bookforge` + `bookforge-fe`):** Fetch and rebase both branches onto latest `origin/dev`, resolve all conflicts preserving upstream features (Section 1.5), keep `'VÀ'` (zero prose `&`) in `format_glossary_prompt_block`, verify single Alembic head (`alembic heads`), and inspect `git diff origin/dev...HEAD` on every conflicted file.
- [ ] **🔴 1 (`school_glossary.py` + `ma_tran_de_agent.py` + `infographic_agent.py` + `phieu_dien_khuyet_agent.py`):** Support composite/alias subjects (`Khoa học tự nhiên`, `KHTN`, `Lịch sử và Địa lí`, `GDCD`) in `lookup_lesson_glossary` and fall back to `resolve_auto_glossary_terms` whenever `terms` lacks any non-`chung` subject term, locking $P \land \neg P$ in `tests/test_school_glossary.py`.
- [ ] **🔴 2 (`school_glossary.py`):** Ignore `chung` hits when deciding `has_strong_subject_hit` in `scan_passage` and do not hard-lock `allowed_subjects = {'chung'}` when `p_votes` is empty, locking `'Nêu yêu cầu cần đạt khi dạy về enthalpy'` ($P$) and pure pedagogical `chung` prompts ($\neg P$).
- [ ] **🔴 3 (`school_glossary.py`):** Restrict unit-ratio slash skipping in `extract_headword_variants` strictly to unspaced `/` (`phổi/phút`, `S/V`, `G1/S`), preserving all spaced ` / ` bilingual English synonyms (`Climograph`, `Folktale`, etc.) and clean `*` stripping for `Agent Dịch học thuật`, locking $P \land \neg P$ in tests.
- [ ] **🔴 4 (`flow_agent.py` + `editor_agent.py` + `bookforge-fe` Flow / `/mindmap` callers):** Remove `selection_block` scaffolding (`[n-1]`, `"Sơ đồ"`, `"liên kết"`, `"type="`) from `_resolve_flow_glossary_block` inputs, route omitted `context_settings` through `resolve_effective_context_settings(db, org_id, context_settings)` in both BE agents, and wire `context_settings` into FE `APIRunFlowAiActionWithEngine` + `executeChatMindmapSlashCommand`, locking $P \land \neg P$ in tests.
- [ ] **🟡 1 (`api/chat.py` + `chat/adk_agent.py`):** Include recent user turn context + session document titles in `resolve_auto_glossary_prompt_block` lookup text for follow-up turns.
- [ ] **🟡 2 (`docs/frontend/chat-glossary-context.md`):** Update the FE contract doc to match toggle-only behavior.
- [ ] **Mechanical gates pass with 0 errors after rebase + fixes:**
  - BE: `uv run --directory services/api ruff check .`
  - BE: `uv run --directory services/api ruff format --check .`
  - BE: `uv run --directory services/api alembic heads`
  - BE: `uv run --directory services/api pytest -n0 tests/test_school_glossary.py tests/test_dich_hoc_thuat_agent.py tests/test_agent_conflict_and_orthography.py tests/test_question_cards_generate_api.py tests/test_editor_assistant.py tests/test_flow_artifacts.py tests/test_chat_modes_workspace_enabled.py tests/test_errors_openapi.py tests/test_feature_guardrails.py`
  - FE: `npx tsc --noEmit`
  - FE: `npx eslint <modified files>`
  - FE: `npx vitest run` on all affected suites (including `flow-mindmap-ux.test.tsx`, `use-chat-modes.test.tsx`, `HomePage/index.test.tsx`, `use-chat-with-ai.test.tsx`, `AgentSettings.test.tsx`, `MassQuestionGenerateDrawer.test.tsx`, `SchoolRulesPage.test.tsx`) + `npx vite build`
