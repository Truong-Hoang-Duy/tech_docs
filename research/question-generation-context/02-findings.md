# 02 — Kết quả khảo sát: Ô nhập ngữ cảnh khi tạo câu hỏi trong thư mục câu hỏi

> Phạm vi đọc: BE `backend/services/api/src/bookforge_api/{schemas/question_bank.py, api/question_cards.py (đoạn /generate), services/question_cards_ai.py, llm/question_bank_prompts.py}` + grep test `tests/test_question_*`;
> FE `frontend/src/{api/question-bank-api.ts, templates/QuestionBankPage/components/mass-generate/, question-bank-shared.ts}` + chỗ mount drawer trong `folder-list/`, `cards/`, `sets/`, `import-notebook/`, `DocumentsPage/`.
> Trạng thái tại 2026-09-14 — `bookforge` `dev` @ `ebd0693a`, `bookforge-fe` `dev` @ `a09c30d`.
> Mọi đường dẫn BE tính từ `backend/services/api/src/bookforge_api/`, FE tính từ `frontend/src/` (trừ khi ghi rõ).

## Tóm tắt cho người đọc không có repo

- **API đã có sẵn một ô văn bản tự do: trường `hint`** (tối đa 1000 ký tự) trong `POST /api/question-cards/generate`. Nhưng **FE gửi cứng `hint: null`** ở mọi nơi — người dùng không có chỗ gõ.
- `hint` hiện mang nghĩa hẹp: được chèn vào prompt dưới nhãn **"Mục tiêu liên quan"**, và **bị bỏ hẳn khi người dùng chọn Kiến thức / Năng lực** trong khung chương trình. Hành vi này đã được khoá bằng test.
- Có **một drawer dùng chung** cho mọi nút "Tạo câu hỏi mới": `MassQuestionGenerateDrawer` (tiêu đề "Tạo câu hỏi hàng loạt"). Thêm ô ở đây là có ở cả thư mục, danh sách câu hỏi, bộ đề và trang Tài liệu.
- Hiện trạng trong mô tả lệch một chút: ô **"Loại câu hỏi" có 4 lựa chọn** — Trắc nghiệm, Đúng/Sai, Trả lời ngắn, Tự luận. **Không có "Điền vào chỗ trống"** trong luồng AI.
- **Loại câu hỏi được ép cứng** (output của LLM bị kiểm tra theo đúng schema của loại đó) → ngữ cảnh không thể đổi loại câu hỏi. **Mức độ nhận thức chỉ nằm trong prompt**, không bị kiểm tra lại; **số lượng câu cũng không bị kiểm tra** (prompt nói "đúng N câu", schema chỉ đòi ≥ 1).
- Sinh câu hỏi chạy **đồng bộ** trong request, không có job nền; kết quả **lưu thẳng vào thư mục** ở trạng thái "Mới", không có bước xem trước.
- `1_repo-map.md` không lệch ở vùng đã đọc.

## Phía nào phải sửa

**FE chắc chắn; BE tuỳ phương án** (quyết định ở `03-design.md`):

| Nếu… | BE phải đụng | FE phải đụng |
|---|---|---|
| Dùng lại `hint` nguyên nghĩa hiện tại | Không cần | Thêm ô vào drawer, gửi `hint` |
| Dùng lại `hint` nhưng muốn ngữ cảnh luôn có hiệu lực, kể cả khi đã chọn Kiến thức/Năng lực, và đổi nhãn "Mục tiêu liên quan" | `llm/question_bank_prompts.py`, `api/question_cards.py` (`_generated_content_json` + đoạn `pop('hint')`), sửa test `test_question_curriculum_api.py` | Như trên |
| Thêm trường mới riêng cho ngữ cảnh | `schemas/question_bank.py`, `api/question_cards.py`, `services/question_cards_ai.py`, `llm/question_bank_prompts.py` + test | Như trên, thêm field vào `TGenerateQuestionCardsRequest` |

File FE luôn phải đụng:
- `templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.tsx` — state + ô nhập + `buildPayload`.
- `api/question-bank-api.ts` — chỉ khi thêm trường mới.

**Hợp đồng giữa hai bên:** `POST /api/question-cards/generate`, body `QuestionCardGenerateRequest` (trích đủ ở mục "Trích nguyên văn"), response `{ cards: QuestionCardResponse[] }`, HTTP 201.

## Bản đồ vùng liên quan

**BE**
- `POST /api/question-cards/generate` → hàm `generate` — `api/question_cards.py:690-845`
- `_generated_content_json` (ghi/bỏ `hint` vào `content_json`) — `api/question_cards.py:680-687`
- `_GENERATE_OUTPUT_BUDGET = 4096` — `api/question_cards.py:155`
- `QuestionCardGenerateRequest` / `QuestionCardGenerateResponse` — `schemas/question_bank.py:585-615`
- `GeneratableQuestionType`, `CognitiveLevel` — `schemas/question_bank.py:18-19`
- `generate_question_cards`, `build_output_model`, `OUTPUT_REPAIR_PASSES` — `services/question_cards_ai.py:61-150`
- `question_generation_system_prompt`, `question_generation_user_prompt` — `llm/question_bank_prompts.py:35-96`
- Kiểm tra hạn mức: `require_ai_action`, `validate_question_set_request`, `provider_max_output_tokens` — gọi tại `api/question_cards.py:706-738`
- Ghi nhật ký AI: `record_ai_action(action_type='question_set_generation')` — `api/question_cards.py:740-749, 827-842`
- Test khoá hành vi `hint`: `tests/test_question_cards_generate_api.py:118-130`, `tests/test_question_curriculum_api.py:412, 474-509, 512-532`, `tests/test_question_cards_ai.py:336`

**FE**
- `APIGenerateQuestionCards` — `api/question-bank-api.ts:1411-1420`
- `TGenerateQuestionCardsRequest` — `api/question-bank-api.ts:767-782`
- `MassQuestionGenerateDrawer` (1961 dòng, có `eslint-disable max-lines`) — `templates/QuestionBankPage/components/mass-generate/MassQuestionGenerateDrawer.tsx:307`; `buildPayload` tại `:828-863`; khối "B. Cấu hình chung" tại `:1037-1194`
- `buildGeneratePayload` + `MassGenerateFormState` — `…/mass-generate/mass-generate-payload.ts` (**chỉ test dùng**, drawer không gọi)
- `questionTypeOptions`, `cognitiveLevelOptions` — `templates/QuestionBankPage/question-bank-shared.ts:216-251`
- Nơi mount drawer:
  - `…/folder-list/FolderListScreen.tsx:2217` — nút "Tạo câu hỏi mới" `:1633-1635`, xử lý kết quả `handleCreateFolderMassQuestions` `:1330-1369`
  - `…/cards/CardsPage.tsx:1271` — nút "Tạo câu hỏi mới" `:1063-1065`, và `onBulkCreate` `:1203`
  - `…/sets/QuestionCollectionSetsPage.tsx:2287` — nút "Tạo câu hỏi mới" `:3424`
  - `templates/DocumentsPage/index.tsx:123` — mở với `sourceDocument` (tiêu đề đổi thành "Tạo câu hỏi từ tài liệu")
- Luồng khác cũng gọi `/generate` nhưng **không qua drawer**: `…/import-notebook/QuestionImportNotebookPage.tsx:703-780` (mỗi cell sinh 1 câu, cũng gửi `hint: null`)

## Tiền đề sai trong brief / mô tả

- **"3 nút: tự luận / trắc nghiệm / điền vào chỗ trống"** → thật ra là **một ô chọn "Loại câu hỏi" với 4 giá trị**: Trắc nghiệm (`multiple_choice`), Đúng/Sai (`true_false`), Trả lời ngắn (`short_answer`), Tự luận (`essay`). "Điền khuyết" (`fill_blank`) có trong danh sách loại chung nhưng bị lọc khỏi drawer vì BE không cho sinh (`services/question_cards_ai.py:20-23`).
- **"Thang Bloom"** → không có ô nào tên Bloom. Có ô **"Mức độ nhận thức"** (không bắt buộc), 6 mức: Nhận biết, Thông hiểu, Vận dụng, Phân tích, Đánh giá, Sáng tạo.
- **Brief giả định API "chưa có trường văn bản tự do"** → đã có `hint`, chỉ là FE không dùng (xem Q1, Q7).

## Trả lời câu hỏi

### Q1 — `/generate` nhận những trường nào? Đã có trường văn bản tự do chưa? Đồng bộ hay job nền?

**Trả lời:** 13 trường, `extra='forbid'` (gửi trường lạ → 422). **Đã có `hint: str | None`, tối đa 1000 ký tự.** Ngoài ra có `source_text` (≤ 20 000 ký tự) nhưng đó là **ngữ liệu để bám**, không phải lời dặn (xem Q3). Chạy **đồng bộ**: handler gọi thẳng `generate_question_cards` → `agent.run_sync(...)`, không enqueue job.

**Bằng chứng:** `schemas/question_bank.py:585-611`
```python
class QuestionCardGenerateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    folder_id: str
    subject: str = Field(min_length=1, max_length=64)
    grade: str = Field(min_length=1, max_length=32)
    topic: str = Field(min_length=1, max_length=255)
    question_type: GeneratableQuestionType
    num_questions: int = Field(ge=1, le=100)
    cognitive_level: CognitiveLevel | None = None
    hint: str | None = Field(default=None, max_length=1000)
    knowledge_node_ids: list[str] | None = None
    competency_node_ids: list[str] | None = None
    source_text: str | None = Field(default=None, max_length=20000)
    source_label: str | None = Field(default=None, max_length=255)
    expert_agent_id: str | None = Field(default=None)

    @model_validator(mode='after')
    def reject_both_grounding_sources(self):
        if self.expert_agent_id and self.source_text:
            raise ValueError('provide expert_agent_id or source_text, not both')
        return self
```
`services/question_cards_ai.py:128` — `result = agent.run_sync(question_generation_user_prompt(...))`

### Q2 — Prompt được dựng ở đâu, tham số chèn thế nào, có tách system / user không?

**Trả lời:** Dựng ở `llm/question_bank_prompts.py`. **Có tách:** system prompt cố định (vai "chuyên gia khảo thí", quy tắc chung), user prompt ghép từng dòng từ tham số request. `hint` chỉ được chèn **khi không chọn Kiến thức và Năng lực nào**, dưới nhãn "Mục tiêu liên quan".

**Bằng chứng:** `llm/question_bank_prompts.py:35-48` (system)
```python
def question_generation_system_prompt() -> str:
    return (
        'Bạn là chuyên gia khảo thí cho giáo dục phổ thông Việt Nam.\n'
        'Nhiệm vụ: soạn câu hỏi kiểm tra có cấu trúc, chính xác về kiến thức, bám chương trình.\n'
        '\n'
        'Quy tắc bắt buộc:\n'
        '- Viết toàn bộ bằng tiếng Việt.\n'
        f'{_MATH_FORMAT_RULE}\n'
        '- "stem" là câu dẫn, không được để trống.\n'
        '- Luôn có "explanation" giải thích vì sao đáp án đúng.\n'
        '- Đáp án phải chính xác. Nếu không chắc chắn về một dữ kiện, hãy chọn nội dung khác mà bạn chắc chắn.\n'
        '- Không tạo câu mơ hồ, không dùng phủ định kép, không gài bẫy.\n'
        '- Không lặp lại câu hỏi trong cùng một lần sinh.\n'
    )
```
`llm/question_bank_prompts.py:66-96` (user)
```python
    lines = [
        f'Soạn đúng {num_questions} câu hỏi.',
        f'Môn: {subject}',
        f'Lớp: {grade}',
        f'Chủ đề: {topic}',
        f'Dạng câu hỏi: {question_type}',
        _TYPE_GUIDANCE[question_type],
    ]
    if cognitive_level:
        lines.append(f'Mức độ nhận thức: {_COGNITIVE_LABELS.get(cognitive_level, cognitive_level)}')
    # … gom knowledge_lines / competency_lines …
    for path in knowledge_lines:
        lines.append(f'Kiến thức: {path}')
    for path in competency_lines:
        lines.append(f'Năng lực: {path}')
    if hint and not knowledge_lines and not competency_lines:
        lines.append(f'Mục tiêu liên quan: {hint}')
        lines.append('Các câu hỏi cần bám mục tiêu liên quan này khi chọn trọng tâm kiểm tra.')
    if source_text:
        lines.append('')
        lines.append('Bám sát ngữ liệu sau. Chỉ dùng thông tin có trong ngữ liệu này:')
        lines.append(source_text)
    else:
        lines.append('')
        lines.append('Không có ngữ liệu kèm theo. Dùng kiến thức chuẩn của chương trình.')
    return '\n'.join(lines)
```
Lưu ý: dòng `Dạng câu hỏi:` in **mã kỹ thuật** (`multiple_choice`…), không phải nhãn tiếng Việt.

### Q3 — Câu hỏi được sinh dựa trên nguồn gì?

**Trả lời:** Ba khả năng, loại trừ nhau theo thứ tự ưu tiên:
1. `expert_agent_id` → truy hồi từ kho tri thức của Expert Agent theo `topic` (`build_corpus_grounding`), đưa vào như `source_text`.
2. `source_text` do người dùng dán (hoặc mục lục tài liệu khi mở từ trang Tài liệu) → prompt ép "Chỉ dùng thông tin có trong ngữ liệu này".
3. Không có gì → "Dùng kiến thức chuẩn của chương trình", chỉ dựa trên môn / lớp / chủ đề / Kiến thức / Năng lực.

Node Kiến thức / Năng lực được đổi thành đường dẫn chữ (`resolve_curriculum_paths`) rồi chèn vào prompt.

**Bằng chứng:** `api/question_cards.py:709-730`
```python
    hint = payload.hint.strip() if payload.hint else None
    knowledge_paths, competency_paths = resolve_curriculum_paths(
        db, actor=user, subject=folder.subject, grade=folder.grade,
        knowledge_node_ids=payload.knowledge_node_ids,
        competency_node_ids=payload.competency_node_ids,
    )

    if payload.expert_agent_id:
        expert = resolve_expert(db, user, payload.expert_agent_id)
        source_text, citation = build_corpus_grounding(expert, payload.topic)
    elif payload.source_text:
        source_text = payload.source_text
        citation = {'kind': 'pasted_text', 'label': payload.source_label or 'Ngữ liệu do người dùng cung cấp'}
    else:
        source_text = None
        citation = None
```

### Q4 — Output được kiểm tra ở đâu? Có ép loại / số lượng / mức nhận thức không? Có quota, giới hạn đầu vào không?

**Trả lời:**
- **Loại câu hỏi: ép cứng.** Output type của agent chính là payload model mà API dùng để validate loại đó. Sai shape thì PydanticAI trả lỗi cho model sửa, tối đa 2 lượt; vẫn sai → 502, không tạo câu nào.
- **Số lượng: không ép.** Schema chỉ đòi `min_length=1`; handler lặp qua `result.payloads`, không so với `num_questions`.
- **Mức độ nhận thức: không ép.** Chỉ có trong prompt. Thẻ được lưu `cognitive_level=payload.cognitive_level` (giá trị người dùng chọn), bất kể LLM viết câu ở mức nào.
- **LaTeX:** có validator riêng `install_latex_output_validator`.
- **Hạn mức:** kiểm tra theo thứ tự trước khi tốn token — lượt AI (429), số câu theo gói (400 `quota_request_too_large`, trần hạ tầng 100), thư mục (404). Output tối đa 4096 token (`_GENERATE_OUTPUT_BUDGET`), điều chỉnh qua `provider_max_output_tokens` với ước lượng đầu vào **chỉ tính `source_text`** + 256.
- **Giới hạn đầu vào văn bản:** `hint` ≤ 1000, `source_text` ≤ 20 000 (Pydantic, trả 422).

**Bằng chứng:** `services/question_cards_ai.py:74-86, 118-127`
```python
def build_output_model(question_type: str) -> type[BaseModel]:
    payload_model = PAYLOAD_MODELS[question_type]
    return create_model(
        'GeneratedCards',
        cards=(list[payload_model], Field(min_length=1)),  # type: ignore[valid-type]
    )
# …
    agent = Agent(
        model,
        instructions=question_generation_system_prompt(),
        output_type=build_output_model(question_type),
        output_retries=OUTPUT_REPAIR_PASSES,   # = 2
        model_settings=model_settings,
    )
    install_latex_output_validator(agent)
```
`api/question_cards.py:705-708, 732-738`
```python
    # Order matters: every cheap check runs before a token is spent.
    require_ai_action(response, context)  # 429
    validate_question_set_request(num_questions=payload.num_questions, plan=context.plan, settings=settings)  # 400
    folder = get_folder_for_question_add(db, user, payload.folder_id)  # 404
# …
    estimated_input_tokens = (len(source_text or '') + 3) // 4 + 256
    max_output_tokens = provider_max_output_tokens(
        _GENERATE_OUTPUT_BUDGET,
        plan=context.plan,
        settings=settings,
        estimated_input_tokens=estimated_input_tokens,
    )
```
`api/question_cards.py:796-809` — thẻ lưu `question_type` và `cognitive_level` lấy từ payload request, không từ output LLM.

### Q5 — Màn hình tạo hàng loạt là component nào, gồm những ô gì? Có entry point khác không?

**Trả lời:** Là `MassQuestionGenerateDrawer`, một drawer trượt từ phải. Tiêu đề "Tạo câu hỏi hàng loạt", hoặc "Tạo câu hỏi từ tài liệu" khi mở từ trang Tài liệu. **"Tạo câu hỏi mới" và "tạo hàng loạt" là một:** mọi nút "Tạo câu hỏi mới" đều mở drawer này. Có 4 nơi mount (xem Bản đồ): màn danh sách thư mục, màn câu hỏi trong thư mục, bộ đề, trang Tài liệu.

Các khối và ô trong drawer:

```text
A. Nguồn tạo câu hỏi   — chọn tài liệu / mục lục, bật kho tri thức Expert,
                          hoặc ô "Ngữ liệu tham chiếu" (rich text ≤ 20 000) + "Tên nguồn" + "Dùng ngữ liệu" Bật/Tắt
B. Cấu hình chung      — Thư mục lưu *, Khối/lớp *, Môn học *, Chủ đề * (ô text),
                          Loại câu hỏi (4 giá trị), Mức độ nhận thức (không bắt buộc, 6 mức),
                          Kiến thức (cây node), Năng lực (cây node), Tag sẽ gắn
C. Sản lượng           — Số lượng câu hỏi (1–100)
D. Tùy chọn chất lượng — 3 checkbox luôn bật (chỉ hiển thị) + "Có trích dẫn từ nguồn"
E. Xem trước đầu ra    — tóm tắt số câu, loại, "Có nguồn" (không phải xem trước câu hỏi thật)
```

**Không có ô nào cho lời dặn / ngữ cảnh.** Luồng notebook nhập câu hỏi (`QuestionImportNotebookPage`) cũng gọi `/generate` nhưng có form riêng, không dùng drawer.

**Bằng chứng:** `…/mass-generate/MassQuestionGenerateDrawer.tsx:1122-1148`
```tsx
              <MassField label="Loại câu hỏi">
                <QuestionBankSelect
                  className="w-full"
                  label="Loại câu hỏi"
                  value={questionType}
                  options={generatableQuestionTypeOptions}
                  …
                />
              </MassField>
              <MassField label="Mức độ nhận thức">
                <QuestionBankSelect
                  className="w-full"
                  label="Không bắt buộc"
                  value={cognitiveLevel}
                  options={[
                    { label: "Không bắt buộc", value: "" },
                    ...cognitiveLevelOptions,
                  ]}
                  …
                  onChange={setCognitiveLevel}
                />
              </MassField>
```
`templates/QuestionBankPage/question-bank-shared.ts:216-251`
```ts
export const questionTypeOptions: Array<TFilterOption<TQuestionType>> = [
  { label: "Trắc nghiệm", value: "multiple_choice" },
  { label: "Đúng/Sai", value: "true_false" },
  { label: "Trả lời ngắn", value: "short_answer" },
  { label: "Tự luận", value: "essay" },
  { label: "Điền khuyết", value: "fill_blank" },   // ← bị lọc khỏi drawer
  // matching, ordering, passage, visual …           ← bị lọc khỏi drawer
];
export const cognitiveLevelOptions: Array<TFilterOption<TCognitiveLevel>> = [
  { label: "Nhận biết", value: "nhan_biet" },
  { label: "Thông hiểu", value: "thong_hieu" },
  { label: "Vận dụng", value: "van_dung" },
  { label: "Phân tích", value: "phan_tich" },
  { label: "Đánh giá", value: "danh_gia" },
  { label: "Sáng tạo", value: "sang_tao" },
];
```
`…/folder-list/FolderListScreen.tsx:1630-1636`
```tsx
              <FolderListToolbarButton
                icon="plus"
                isPrimary
                onClick={() => setMassGenerateOpen(true)}
              >
                Tạo câu hỏi mới
              </FolderListToolbarButton>
```

### Q6 — Khi bấm tạo, gọi hàm API nào, payload gì, kết quả hiển thị ở đâu?

**Trả lời:** Nút "Tạo N câu hỏi" gọi `onCreate(buildPayload(), { tags })`. Component cha gọi `APIGenerateQuestionCards(payload)`, gắn tag cho từng thẻ bằng `APIUpdateQuestionCard`, đóng drawer, hiện toast "Đã tạo N câu hỏi bằng AI", rồi refetch danh sách. **Không có bước xem trước / chỉnh sửa:** thẻ đã được BE lưu vào thư mục với trạng thái `new` (vào hàng chờ duyệt).

**Bằng chứng:** `…/mass-generate/MassQuestionGenerateDrawer.tsx:828-863`
```tsx
  const buildPayload = (): TGenerateQuestionCardsRequest => {
    const sourcePayloadText = activeSourceDocument ? outlineSourceText : sourceText.trim();
    const shouldAttachSource = Boolean(activeSourceDocument) || citationEnabled;
    const shouldUseExpertGrounding = expertGroundingEnabled && Boolean(groundingExpert?.id);

    return {
      folder_id: folderId,
      subject: subjectValue,
      grade: gradeValue,
      topic: topicValue.trim(),
      question_type: questionType,
      num_questions: questionCount,
      cognitive_level: cognitiveLevel ? (cognitiveLevel as TCognitiveLevel) : null,
      hint: null,
      knowledge_node_ids: knowledgeNodeIds,
      competency_node_ids: competencyNodeIds,
      expert_agent_id: shouldUseExpertGrounding ? (groundingExpert?.id ?? null) : null,
      source_text: !shouldUseExpertGrounding && shouldAttachSource ? sourcePayloadText || null : null,
      source_label: /* … tên nguồn / tên tài liệu / "Ngữ liệu tham chiếu" … */,
    };
  };
```
(đã gộp dòng cho gọn, logic giữ nguyên)

`…/folder-list/FolderListScreen.tsx:1336-1364` — `APIGenerateQuestionCards` → gắn tag → `setMassGenerateOpen(false)` → toast → `folders.refetch()`, `allCards.refetch()`, `cards.refetch()`.

### Q7 — Đã có chỗ nào cho người dùng gõ văn bản tự do gửi AI trong ngân hàng câu hỏi chưa?

**Trả lời:**
- **`hint` phía BE — có, nhưng FE không bao giờ gửi.** Grep `hint:` trong `frontend/src`: chỉ thấy `hint: null` ở drawer (`:846`), `mass-generate-payload.ts:43`, notebook (`QuestionImportNotebookPage.tsx:762`), và một fixture test. Khi gửi, BE còn **ghi `hint` vào `content_json.hint` của thẻ** (nếu không chọn Kiến thức/Năng lực). FE coi `hint` là một khoá của phần đáp án khi sửa nhanh (`question-detail-model.ts:102`).
- **Ô "Ngữ liệu tham chiếu" — có, đang hiển thị.** Là `QuestionRichTextInput`, `maxLength=20000`, placeholder "Dán ngữ liệu, đoạn văn, nội dung bài học…". Nhưng nó đi vào `source_text`, và prompt ép **"Chỉ dùng thông tin có trong ngữ liệu này"**, kèm gắn `citation` vào thẻ. Nếu người dùng gõ lời dặn vào đây, AI sẽ coi lời dặn là nội dung kiến thức.
- **`/convert`, `/extract`:** không nhận văn bản tự do (`QuestionCardConvertRequest` chỉ có `card_ids`, `target_type`).

**Bằng chứng:** `api/question_cards.py:680-687`
```python
def _generated_content_json(content: dict[str, Any], *, hint: str | None, use_curriculum: bool) -> dict[str, Any]:
    payload = dict(content)
    if use_curriculum:
        payload.pop('hint', None)
        return payload
    if hint:
        payload['hint'] = hint
    return payload
```
`tests/test_question_curriculum_api.py:474-509` — `test_generate_persists_node_ids_and_skips_hint`: gửi `'hint': 'should ignore'` kèm node → khẳng định `'hint' not in content_json`.
`…/mass-generate/MassQuestionGenerateDrawer.tsx:1811-1818`
```tsx
    <QuestionRichTextInput
      className="mt-3 border-stroke-soft-200"
      editorClassName="min-h-[118px] px-3 py-2 text-label-sm text-strong-950"
      maxLength={MAX_SOURCE_TEXT_LENGTH}
      value={sourceText}
      placeholder="Dán ngữ liệu, đoạn văn, nội dung bài học... nếu muốn câu hỏi bám nguồn."
      onChange={onSourceTextChange}
    />
```

## Giả định của brief — đúng / sai

| # | Giả định | Kết luận | Bằng chứng |
|---|---|---|---|
| 1 | Màn hình tạo hàng loạt gọi `POST /api/question-cards/generate` | **Đúng** | `api/question-bank-api.ts:1411-1420`; `FolderListScreen.tsx:1337` |
| 2 | "Tạo câu hỏi mới" và "tạo hàng loạt" là cùng một hộp thoại | **Đúng** — và dùng chung ở 4 nơi | Q5 |
| 3 | Request chưa có trường văn bản tự do | **Sai** — có `hint` ≤ 1000, nhưng nghĩa hẹp và bị bỏ khi có Kiến thức/Năng lực | Q1, Q2, Q7 |
| 4 | Sinh câu hỏi chạy đồng bộ, không job nền | **Đúng** | `services/question_cards_ai.py:128` |
| 5 | Ô chọn được chèn vào prompt và/hoặc ép ở tầng kiểm tra output | **Một phần** — loại: ép cứng; mức nhận thức: chỉ prompt | Q4 |
| 6 | Số lượng câu do tham số quyết định, không do prompt | **Sai** — chỉ có prompt "Soạn đúng N câu", không kiểm tra số lượng | Q4 |
| 7 | Thẻ sinh ra không lưu lại tham số đầu vào | **Sai một phần** — thẻ lưu `hint` vào `content_json` (khi không có node); `record_ai_action.metadata` lưu `hint`, `topic`, `num_questions`… | `api/question_cards.py:680-687, 740-749` |

## Trích nguyên văn theo yêu cầu

**Request schema `/generate`** — xem Q1 (đủ 13 trường + validator).

**Response schema:** `schemas/question_bank.py:614-615`
```python
class QuestionCardGenerateResponse(BaseModel):
    cards: list[QuestionCardResponse]
```
Lỗi được khai báo: `auth_required`, `access_denied`, `question_folder_not_found`, `quota_exceeded`, `quota_request_too_large`, `editor_assistant_unavailable`, `editor_assistant_failed` (`api/question_cards.py:202-210`).

**Kiểu literal:** `schemas/question_bank.py:18-19`
```python
GeneratableQuestionType = Literal['multiple_choice', 'true_false', 'short_answer', 'essay']
CognitiveLevel = Literal['nhan_biet', 'thong_hieu', 'van_dung', 'phan_tich', 'danh_gia', 'sang_tao']
```

**Prompt sinh câu hỏi** — xem Q2. **Đoạn kiểm tra output** — xem Q4.

**Payload FE:** `api/question-bank-api.ts:767-782`
```ts
export type TGenerateQuestionCardsRequest = {
  folder_id: string;
  subject: string;
  grade: string;
  topic: string;
  question_type: TGeneratableQuestionType;
  num_questions: number;
  cognitive_level?: TCognitiveLevel | null;
  hint?: string | null;
  knowledge_node_ids?: string[] | null;
  competency_node_ids?: string[] | null;
  source_text?: string | null;
  source_label?: string | null;
  // Grounding via an Expert Agent's corpus; mutually exclusive with source_text (API rejects both).
  expert_agent_id?: string | null;
};
```

**State / JSX form** — danh sách ô ở Q5, đoạn JSX hai ô chọn ở Q5, `buildPayload` ở Q6.

## Vùng nên nhờ Gemini đọc thêm

Không cần — vùng liên quan đã đọc đủ trong một lượt.

## Điều brief không hỏi nhưng ảnh hưởng tới thiết kế

1. **Có hai hàm dựng payload song song.** `mass-generate-payload.ts` (`buildGeneratePayload`, có test riêng) **không được drawer gọi**. Drawer tự dựng trong `buildPayload` (`:828`). Sửa nhầm file sẽ qua test mà không đổi hành vi.
2. **Drawer đã 1961 dòng**, tắt `max-lines` bằng `eslint-disable` (dòng 1). Quy ước FE là 300 dòng/file, 100 dòng/hàm (`frontend/CONVENTION.md:3-5`). Thêm ô trực tiếp vào đây sẽ làm file dài thêm.
3. **Ngữ cảnh người dùng đi vào user prompt, cạnh system prompt cố định.** Lời dặn kiểu "Bạn là giáo viên…" không đổi được loại câu hỏi (bị schema chặn), nhưng **có thể** lệch số câu và mức nhận thức mà không ai phát hiện (Q4).
4. **Ước lượng token đầu vào không tính `hint`** (`api/question_cards.py:732`, chỉ `source_text` + 256). Với 1000 ký tự (~250 token) thì còn nằm trong phần dư 256; nếu nới giới hạn ngữ cảnh thì công thức này phải tính thêm.
5. **Drawer dùng chung 4 nơi**, gồm cả trang Tài liệu (luôn có `source_text` từ mục lục). Ngữ cảnh + ngữ liệu bắt buộc sẽ cùng xuất hiện ở đó, trong khi prompt đang ép "Chỉ dùng thông tin có trong ngữ liệu".

## Chưa xác định được

- **Chất lượng thực tế khi ngữ cảnh mâu thuẫn ô chọn** (ví dụ gõ "mức độ khó" nhưng chọn "Vận dụng"): không đọc code mà biết được, phải chạy thử với model đang cấu hình (`llm_question_bank_reasoning_effort`, route `question_bank`).
- **`content_json.hint` có được hiển thị ở đâu không.** Đã grep `\bhint\b` trong `templates/QuestionBankPage/` (bỏ test, `submitHint`, `destinationHint`): chỉ có `question-detail-model.ts:102`, là danh sách khoá dùng khi sửa nhanh phần đáp án. Không thấy màn nào hiển thị riêng. Chưa kiểm tra phía xuất đề / đẩy sang Cohota có đọc `hint` không.
- File `Tạo sinh câu hỏi - Test.pdf` ở gốc workspace: **chưa mở**, không rõ có liên quan không.
