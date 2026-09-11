# BookForge — Công tắc hệ thống

> **Đây là tài liệu VẬN HÀNH: bật/tắt cái gì, bật ở đâu, bật xong thì tính năng nào xuất hiện.**
> Không phải tài liệu thiết kế — muốn biết *vì sao* một cờ tồn tại thì đọc spec dẫn ở từng mục.
> Nguồn: `bookforge@60b14b4` (dev) · `bookforge-fe@9bfd2fd` (dev) — **2026-09-11**.
> Đường dẫn BE tính từ gốc repo `bookforge`, FE tính từ gốc repo `bookforge-fe`.
> [`repo-map.md` §6](repo-map.md) là bản mục lục một bảng; file này là bản chi tiết của mục đó.

---

## 1. Bốn tầng công tắc

| Tầng | Nơi cầm công tắc | Phạm vi | Ai bật | Hiệu lực khi nào |
|---|---|---|---|---|
| **1. Công tắc sản phẩm** (§2) | env **VÀ** bảng `organization_feature_flags` | Từng tổ chức | DevOps (env) + vận hành (grant) | env: restart container · grant: request kế tiếp |
| **2. Công tắc chỉ env** (§3) | env | Toàn deployment | DevOps | Restart container |
| **3. Entitlement khác** (§4) | Bảng grant riêng, không qua bảng feature flags | Từng tổ chức | Vận hành, bằng CLI | Request kế tiếp |
| **4. Công tắc vận hành** (§5) | env / compose profile | Toàn deployment | DevOps | Restart container |
| **5. Công tắc frontend** (§6) | `VITE_*` lúc build | Toàn bản build | FE build | Build lại |

### 1.1 Luật vàng của tầng 1: **env AND grant**

Một tính năng sản phẩm chỉ bật khi **cả hai** đều đúng — env bật ở deployment **và** tổ chức có dòng grant:

```python
# services/api/src/bookforge_api/services/features.py:79-88
def feature_enabled(db, organization_id, key) -> bool:
    spec = PRODUCT_FEATURES.get(key)
    if spec is None: return False
    if not bool(getattr(get_settings(), spec.env_attr)): return False   # ← tầng env
    if spec.source == 'expert_grants': return _org_has_expert_grant(db, organization_id)
    return _org_has_flag_row(db, organization_id, key)                   # ← tầng grant
```

Đây là **nơi duy nhất** trả lời câu "tổ chức này có được dùng mặt hàng này không". Mọi chỗ khác đều gọi vào đây.

**Sự hiện diện của dòng DB CHÍNH LÀ quyền** — bật là một `INSERT`, tắt là một `DELETE`, không có cột soft-disable
([`models/features.py:17-28`](../../backend/services/api/src/bookforge_api/models/features.py)).
Không có cache, nên revoke có hiệu lực ngay ở request kế tiếp của tổ chức đó.

### 1.2 Frontend biết được gì

Backend trả danh sách key đã bật trong response đăng nhập và `GET /api/auth/me`
([`api/auth.py:43`](../../backend/services/api/src/bookforge_api/api/auth.py)), FE đọc qua `user.features`:

```text
BE: enabled_features(db, org_id) → ["question_bank", "chat_workspace"]
FE: useFeature("question_bank")   (hooks/use-feature.ts)
    <RequireFeature feature="…">  (components/RequireFeature/index.tsx → Navigate to "/")
```

Hệ quả vận hành: **grant xong mà FE chưa thấy** là do `auth-context` còn giữ user cũ — bảo người dùng tải lại trang hoặc đăng nhập lại.

---

## 2. Công tắc sản phẩm (7 key)

Khai báo tập trung tại [`services/features.py:44-55`](../../backend/services/api/src/bookforge_api/services/features.py).
Mặc định trong `compose.common.yml` là **`false` hết**, trừ chỗ ghi rõ.

| Key | Biến env | Mặc định | Nguồn grant | Bật lên thì mở ra cái gì |
|---|---|---|---|---|
| `question_bank` | `BOOKFORGE_QUESTION_BANK_ENABLED` | `false` | `organization_feature_flags` | Toàn bộ phân hệ Ngân hàng câu hỏi (9 router BE + 11 route FE) |
| `chat_workspace` | `BOOKFORGE_CHAT_WORKSPACE_ENABLED` | `false` | `organization_feature_flags` | Chat soạn thảo có chủ đích (kế hoạch bài dạy) + 4 tool |
| `chat_document_tools` | `BOOKFORGE_CHAT_DOCUMENT_TOOLS_ENABLED` | `false` | `organization_feature_flags` | 5 tool đọc–điều hướng tài liệu của chat agent + doc summary |
| `editor_focus_envelope` | `BOOKFORGE_EDITOR_FOCUS_ENVELOPE_ENABLED` | `false` | `organization_feature_flags` | Editor agent làm việc được trên tài liệu dài |
| `grid_deck` | `BOOKFORGE_GRID_DECK_ENABLED` | `false` | `organization_feature_flags` | Bộ template PPTX Grid |
| `legal_mode` | `BOOKFORGE_LAW_ENABLED` | `false` | `organization_feature_flags` | Chế độ chat Trợ lý pháp lý |
| `expert_agents` | `BOOKFORGE_EXPERT_AGENTS_ENABLED` | `false` | **`expert_agent_grants`** (bảng riêng) | Chat với trợ lý chuyên gia theo kho riêng |

> `expert_agents` đọc grant từ bảng khác nên **không cấp được bằng `grant_feature`** — script sẽ báo `ValueError`. Xem §4.2.

`DEFAULT_FEATURE_GRANTS_FOR_NEW_ORGS` đang **rỗng** ([`features.py:21`](../../backend/services/api/src/bookforge_api/services/features.py)):
tổ chức tạo mới **không** tự có tính năng nào, phải cấp tay.

---

### 2.1 `question_bank` — Ngân hàng câu hỏi

**Bật lên thì có gì**

*Backend* — 9 router được gắn `Depends(require_feature('question_bank'))` một lượt tại [`main.py:87-96`](../../backend/services/api/src/bookforge_api/main.py):

| Router | Mảng chức năng |
|---|---|
| `question_folders` | Thư mục câu hỏi |
| `question_knowledge_frameworks` · `question_knowledge_nodes` | Khung kiến thức + node |
| `question_competency_frameworks` · `question_competency_nodes` | Khung năng lực + node |
| `question_cards` | Thẻ câu hỏi, sinh câu hỏi bằng AI, **và trích đề từ PDF** (`exam_extract`) |
| `question_cart` | Giỏ chọn câu hỏi |
| `question_collections` | Bộ sưu tập câu hỏi |
| `test_papers` | Đề kiểm tra |

*Frontend* — 11 route bọc `protectedFeatureRoute("question_bank", …)` trong [`App.tsx`](../../frontend/src/App.tsx): `/question-bank`, `/question-bank/folders`, `/question-bank/curriculum`, `/question-bank/editor/:cardId`, `/question-bank/import`, … Ngoài ra:

- Mục Ngân hàng câu hỏi trên sidebar — [`components/Sidebar/index.tsx:621,738`](../../frontend/src/components/Sidebar/index.tsx)
- Hành động "tạo câu hỏi từ tài liệu" ở trang Tài liệu — [`templates/DocumentsPage/index.tsx:17-18,106`](../../frontend/src/templates/DocumentsPage/index.tsx)

**Tắt thì sao**: mọi endpoint trả `403 feature_not_available`; FE `Navigate to "/"`; mục sidebar biến mất.

**Phụ thuộc thêm**: đẩy câu hỏi sang Canvas LMS cần `BOOKFORGE_COHOTA_API_TOKEN` + `_COURSE_ID` + `_QUESTION_BANK_ID` ([`settings.py:364-380`](../../backend/services/api/src/bookforge_api/core/settings.py)). Thiếu token thì phân hệ vẫn chạy, chỉ mất phần đồng bộ.

---

### 2.2 `chat_workspace` — Chat soạn thảo có chủ đích

**Bật lên thì có gì**

Bốn tool được đăng ký thêm cho chat agent ([`chat/adk_agent.py:987-1013`](../../backend/services/api/src/bookforge_api/chat/adk_agent.py)):

| Tool | Việc |
|---|---|
| `search_library` | Tìm trong kho tài liệu của tổ chức theo tiêu đề/tóm tắt |
| `set_output` | Bật chế độ "kế hoạch bài dạy" dính theo phiên (`giao_an` / `ke_hoach` / `khbd`) |
| `write_draft` | Đệm toàn văn markdown của bản nháp — **chỉ đăng ký sau khi `output_type` đã được set** |
| `check_draft` | Đối chiếu bản nháp với khung Phụ lục IV, trả về `ok` + nhãn còn thiếu |

Kèm theo:
- **Tự động nâng ngân sách agent**: phiên workspace luôn dùng ngân sách mở rộng (7→14 request, 5→12 tool call) kể cả khi `chat_agent_expanded_budget_enabled` đang tắt — [`adk_agent.py:1277`](../../backend/services/api/src/bookforge_api/chat/adk_agent.py).
- **Phiên workspace cô lập**: khi bật mà chưa có tài liệu nào `ai_ready`, phiên chạy ở chế độ isolated ([`adk_agent.py:458`](../../backend/services/api/src/bookforge_api/chat/adk_agent.py)).
- `GET /api/chat/modes` trả `workspace_enabled: true` ([`api/chat.py:1983`](../../backend/services/api/src/bookforge_api/api/chat.py)) — FE đọc ở [`templates/HomePage/index.tsx:361`](../../frontend/src/templates/HomePage/index.tsx).

**Tắt thì sao**: chat chạy đúng như cũ — hỏi đáp trên tài liệu, không có khái niệm bản nháp/loại đầu ra.

**Lưu ý**: `search_library` **trả rỗng** nếu `chat_document_tools` đang tắt ([`chat/workspace_tools.py:143`](../../backend/services/api/src/bookforge_api/chat/workspace_tools.py)) — hai cờ này nên bật cùng nhau.

---

### 2.3 `chat_document_tools` — Bộ tool đọc tài liệu của chat agent

**Bật lên thì có gì** — 5 tool ([`adk_agent.py:773-796`](../../backend/services/api/src/bookforge_api/chat/adk_agent.py)):

| Tool | Việc | Trần |
|---|---|---|
| `get_document_overview` | Tiêu đề, độ dài, outline, tóm tắt từng mục | `chat_overview_max_sections=60` |
| `get_document_summaries` | Tóm tắt định tuyến từng tài liệu | — |
| `search_documents` | "Tôi có tài liệu nào về X không" | `chat_document_search_return_count=8` |
| `get_document_outline` | Heading + khoảng trang từng mục | `chat_outline_max_sections=60`, `max_depth=2` |
| `read_section` | Đọc trọn một mục theo `node_id` | — |

Kèm theo:
- **Sinh doc summary**: chỉ chạy khi cờ bật — [`services/doc_summary.py:211,258`](../../backend/services/api/src/bookforge_api/services/doc_summary.py), [`services/document_trash.py:79`](../../backend/services/api/src/bookforge_api/services/document_trash.py), và script `backfill_doc_summaries.py:76`.
- **Manifest outline**: outline cấp 1 được nhúng thẳng vào instruction khi phiên có ≤ `chat_manifest_outline_max_documents=2` tài liệu.

**Tắt thì sao** — ba tool sau **luôn luôn có**, không phụ thuộc cờ: `read_pages`, `find_passages`, `read_document`. Nghĩa là agent vẫn đọc được tài liệu, chỉ **mù về cấu trúc**: không biết tài liệu có mấy chương, chương 3 ở trang nào, phải mò bằng `find_passages`.

---

### 2.4 `editor_focus_envelope` — Envelope ngữ cảnh cho Editor agent

**Bật lên thì có gì** ([`chat/editor_agent.py:720`](../../backend/services/api/src/bookforge_api/chat/editor_agent.py), [`api/editor.py:1389`](../../backend/services/api/src/bookforge_api/api/editor.py)):
tài liệu dài được gửi cho agent dưới dạng **bản đồ tài liệu + đầu + đuôi + cửa sổ quanh chỗ con trỏ**, thay vì một khối đơn độc.

| Knob đi kèm | Mặc định | Ý nghĩa |
|---|---|---|
| `BOOKFORGE_EDITOR_FULL_CONTEXT_MAX_WORDS` | `6000` | Trên ngưỡng này mới chuyển sang envelope |
| `BOOKFORGE_EDITOR_ENVELOPE_WINDOW_BLOCKS` | `6` | **Sàn**, không phải trần — cửa sổ mỗi bên con trỏ rồi nở tới hết ngân sách ký tự |
| `BOOKFORGE_EDITOR_ENVELOPE_HEAD_TAIL_BLOCKS` | `3` | Số block lấy ở đầu và cuối tài liệu |
| `BOOKFORGE_EDITOR_MAP_MAX_SECTION_WORDS` | `1500` | Mục dài hơn thì chẻ xuống cấp heading kế tiếp |

**Tắt thì sao** — đúng hành vi cũ: dưới 6000 từ gửi cả tài liệu, **trên 6000 từ thì không gửi gì thêm**. Cờ này chính là đường lùi (rollback) của tính năng.

**Trần cứng độc lập**: `BOOKFORGE_EDITOR_DOCUMENT_MAX_WORDS=50000` — editor agent từ chối tài liệu lớn hơn, bật cờ cũng không vượt được.

---

### 2.5 `grid_deck` — Bộ template PPTX Grid

**Bật lên thì có gì** ([`services/pptx_template_access.py:38-60`](../../backend/services/api/src/bookforge_api/services/pptx_template_access.py)):

- `GRID_TEMPLATES` được nối vào danh mục template sau `CANVA_TEMPLATES` — **thứ tự là chịu tải**: picker phân trang 4 ô/trang, đảo thứ tự là xáo lại UI của mọi tổ chức.
- Template mặc định của luồng tạo slide đổi thành `grid_set14` ([`api/standalone_presentations.py:168`](../../backend/services/api/src/bookforge_api/api/standalone_presentations.py)).
- Engine render đi qua `pptx/grid_engine.py` thay vì painter lập trình sẵn (`standalone_presentations.py:218,829,890`).

**Tắt thì sao** — theme rơi về painter lập trình, đúng hành vi cũ. Cờ này **chính là rollback**.

**Cảnh báo trong code**: chỉ bật sau khi đã render deck và **nhìn tận mắt trên CẢ HAI renderer** (PowerPoint thật và ảnh Gotenberg thật) — kiểm trên một cái coi như chưa kiểm ([`settings.py:277-282`](../../backend/services/api/src/bookforge_api/core/settings.py)).

---

### 2.6 `legal_mode` — Trợ lý pháp lý

**Bật lên thì có gì**

- Chế độ chat `legal` được phép tạo phiên ([`api/chat.py:2077`](../../backend/services/api/src/bookforge_api/api/chat.py)) và hiện `enabled: true` trong `GET /api/chat/modes` ([`chat.py:1968`](../../backend/services/api/src/bookforge_api/api/chat.py)).
- Bộ tool tra cứu pháp điển (`chat/legal_tools.py`) gọi sang service `phapdien` qua `LawClient`.
- **Ngân sách riêng, cao hơn**: `chat_agent_request_limit_legal=10`, `chat_agent_tool_calls_limit_legal=8` (tra cứu pháp lý nặng về tìm kiếm).
- Editor agent cũng đọc `law_enabled` ([`editor_agent.py:524`](../../backend/services/api/src/bookforge_api/chat/editor_agent.py)).

**Hai lỗi khác nhau khi tắt** ([`api/chat.py:112-118`](../../backend/services/api/src/bookforge_api/api/chat.py)) — phân biệt được nguyên nhân ngay từ mã lỗi:

| Tình huống | Mã lỗi |
|---|---|
| env `BOOKFORGE_LAW_ENABLED=false` | `law_service_disabled` |
| env bật nhưng tổ chức chưa được grant | `feature_not_available` |

**Phụ thuộc hạ tầng** — bật cờ mà chưa dựng service thì chat lỗi lúc gọi tool:

```text
BOOKFORGE_LAW_SERVICE_URL=http://127.0.0.1:9382
BOOKFORGE_LAW_API_TOKEN=<phải TRÙNG với BOOKFORGE_LAW_API_TOKEN trong lawforge-bundle/.env>
BOOKFORGE_LAW_TIMEOUT_SECONDS=90    BOOKFORGE_LAW_TOOL_TIMEOUT_SECONDS=20
```

Service đóng gói rời ở [`backend/lawforge-bundle/`](../../backend/lawforge-bundle/) (cần `OPENAI_API_KEY` riêng + file index `phapdien.sqlite`).

**Công tắc con**: `BOOKFORGE_LAW_DRAFTING_ENABLED` — xem §3.6.

---

### 2.7 `expert_agents` — Trợ lý chuyên gia

**Khác biệt duy nhất so với 6 key trên**: grant đọc từ bảng `expert_agent_grants`, không phải `organization_feature_flags`
([`features.py:53`](../../backend/services/api/src/bookforge_api/services/features.py), [`services/expert_grounding.py:29-40`](../../backend/services/api/src/bookforge_api/services/expert_grounding.py)).

**Bật lên thì có gì**: chat mode `expert` — hỏi đáp có dẫn chứng trên kho riêng của một chuyên gia, lưu như **nội dung nền tảng** trong dataset RAGFlow riêng chứ không phải Document của tổ chức. Danh sách chuyên gia được cấp trả trong `GET /api/chat/modes` (trường `experts`). Phiên expert **không có tài liệu BookForge nào trong scope** — kho chính là scope.

**Cần cả ba**: env bật · có dòng `expert_agent_grants` cho tổ chức · `ExpertAgent.enabled = true`.

**Cách cấp**: xem §4.2 — `grant_feature --feature expert_agents` sẽ bị từ chối.

---

## 3. Công tắc chỉ env (8 cờ, không cấp theo tổ chức)

Danh sách chốt tại [`features.py:23-34`](../../backend/services/api/src/bookforge_api/services/features.py) (`ENV_ONLY_ENABLED_ATTRS`).
Bật là bật cho **toàn deployment**, mọi tổ chức.

| Cờ | Env | Mặc định (compose) | Tác dụng một dòng |
|---|---|---|---|
| `knowledge_enabled` | `BOOKFORGE_KNOWLEDGE_ENABLED` | **`true`** | Công tắc tổng của RAG |
| `knowledge_per_org_collections_enabled` | `BOOKFORGE_KNOWLEDGE_PER_ORG_COLLECTIONS_ENABLED` | `false` | Mỗi tổ chức một dataset RAGFlow riêng |
| `chat_inline_images_enabled` | `BOOKFORGE_CHAT_INLINE_IMAGES_ENABLED` | **`true`** | Cho agent chèn hình từ tài liệu vào câu trả lời |
| `chat_agent_expanded_budget_enabled` | `BOOKFORGE_CHAT_AGENT_EXPANDED_BUDGET_ENABLED` | `false` | Nới ngân sách vòng lặp agent |
| `model_switcher_enabled` | `BOOKFORGE_MODEL_SWITCHER_ENABLED` | `false` | Cho người dùng tự chọn model |
| `law_drafting_enabled` | `BOOKFORGE_LAW_DRAFTING_ENABLED` | `false` | Soạn thảo văn bản pháp lý trong chế độ pháp lý |
| `authorization_document_shadow_enabled` | `BOOKFORGE_AUTHORIZATION_DOCUMENT_SHADOW_ENABLED` | `false` | Chạy song song engine phân quyền, chỉ để đối chiếu |
| `authorization_document_view_enforcement_enabled` | `BOOKFORGE_AUTHORIZATION_DOCUMENT_VIEW_ENFORCEMENT_ENABLED` | `false` | Chuyển quyết định VIEW sang engine mới |

### 3.1 `knowledge_enabled` — công tắc tổng của RAG

Cờ ảnh hưởng rộng nhất trong hệ thống. **Tắt thì**:

- Không index, không reindex tài liệu — [`services/knowledge_indexing.py:317,349`](../../backend/services/api/src/bookforge_api/services/knowledge_indexing.py)
- Tài liệu tạo trong app mang `rag_status = 'disabled'` — [`services/inapp_document.py:98`](../../backend/services/api/src/bookforge_api/services/inapp_document.py)
- Editor không enqueue reindex sau khi lưu — [`api/editor.py:1193`](../../backend/services/api/src/bookforge_api/api/editor.py)
- Chat bỏ qua kiểm tra `ai_ready` — [`api/chat.py:1795`](../../backend/services/api/src/bookforge_api/api/chat.py)
- `/health` bỏ phần kiểm tra knowledge — [`api/health.py:130`](../../backend/services/api/src/bookforge_api/api/health.py)

**Cần hạ tầng**: `knowledge-ingestion` (`:9380`) + `knowledge-retrieval` (`:9381`) + MySQL + Elasticsearch. Bật cờ mà thiếu service thì mọi lần upload đều lỗi index.

**Knob đi kèm** — `BOOKFORGE_KNOWLEDGE_CHUNK_TOKEN_NUM=512` là **nguồn duy nhất** cho cả ingestion lẫn retrieval, đổi một chỗ là đổi cả hai (cố tình, để không lệch nhau).

### 3.2 `knowledge_per_org_collections_enabled`

Bật thì mỗi tổ chức có dataset RAGFlow riêng, hâm sẵn lúc upload đầu tiên ([`knowledge_indexing.py:162,426`](../../backend/services/api/src/bookforge_api/services/knowledge_indexing.py)). **Chỉ có tác dụng khi `knowledge_enabled` cũng bật** — điều kiện `AND` nằm ngay trong code.

### 3.3 `chat_inline_images_enabled` (mặc định **bật**)

Cờ này **chỉ chi phối phần instruction** gửi cho model ([`adk_agent.py:1415`](../../backend/services/api/src/bookforge_api/chat/adk_agent.py)). Hai việc sau **chạy vô điều kiện, không tắt được**:

1. Viết lại đường dẫn hình trong tài liệu thành URL phục vụ được — đây là bản vá rò rỉ đường dẫn.
2. Lọc hình trong câu trả lời theo allowlist — đây là thứ khiến tính năng an toàn.

Tắt cờ chỉ tạo ra hệ thống *có URL đúng trong text nhưng không bao giờ bảo model dùng*.

### 3.4 `chat_agent_expanded_budget_enabled`

| | Thường | Mở rộng | Pháp lý |
|---|---|---|---|
| `request_limit` | 7 | **14** | 10 |
| `tool_calls_limit` | 5 | **12** | 8 |

Lý do tồn tại: ở mức 5 tool call × 15 trang/lần, trần cứng một lượt đọc được là 75 trang — "tóm tắt cuốn 200 trang" **không thể** trả lời trung thực dù agent có hành xử thế nào.

Giữ cho phần headroom thêm không biến thành chi phí truy hồi là mấy trần riêng của từng tool: `chat_read_max_calls=8`, `chat_read_total_char_budget=120000`, `chat_retrieval_max_queries=4`.

Phiên `chat_workspace` **luôn** dùng ngân sách mở rộng dù cờ này tắt (§2.2).

### 3.5 `model_switcher_enabled`

Tắt → `GET /api/chat/models` chỉ trả **một** entry mặc định, client hiện một ô khoá và hành xử y như trước khi có tính năng ([`llm/model_registry.py:111-128`](../../backend/services/api/src/bookforge_api/llm/model_registry.py)).
Bật → trả mọi entry trong `MODEL_REGISTRY` **có credential tương ứng đã cấu hình**. Không có key của provider nào thì entry đó tự ẩn.

Cố tình không raise lỗi: `model_id` lạ/không được cấp thì rơi về route theo operation chứ không làm hỏng cuộc chat.

### 3.6 `law_drafting_enabled`

Thêm tool `law_draft_*` và một khối instruction soạn thảo ([`adk_agent.py:965,1493`](../../backend/services/api/src/bookforge_api/chat/adk_agent.py), [`chat/legal_tools.py:151`](../../backend/services/api/src/bookforge_api/chat/legal_tools.py)).
Điều kiện thực tế là `law_drafting_enabled AND legal_enabled` (`adk_agent.py:586`) — bật riêng cờ này mà `legal_mode` tắt thì **không có tác dụng gì**.

### 3.7 + 3.8 Hai cờ phân quyền tài liệu

Đây là cặp công tắc di trú (migration), phải bật **theo thứ tự**:

| Bước | Cờ | Hành vi |
|---|---|---|
| 1 | `authorization_document_shadow_enabled` | Chạy engine song song **chỉ để quan sát**; Legacy vẫn là đường quyết định duy nhất; mọi lỗi shadow bị cô lập khỏi request ([`services/document_authorization_shadow.py:54,95`](../../backend/services/api/src/bookforge_api/services/document_authorization_shadow.py)) |
| 2 | `authorization_document_view_enforcement_enabled` | Chuyển hẳn quyết định **VIEW** sang engine ([`services/document_authorization_enforcement.py:55`](../../backend/services/api/src/bookforge_api/services/document_authorization_enforcement.py)) |

Cờ 2 là **công tắc rollback theo từng hành động**: tắt là khôi phục đúng đường VIEW của Legacy.
Kiểm tra đang chạy đường nào: `GET /health` trả `document_view: "engine" | "legacy"` ([`api/health.py:92`](../../backend/services/api/src/bookforge_api/api/health.py)).

---

## 4. Entitlement theo tổ chức không đi qua bảng feature flags (3 loại)

Ba thứ này cũng là công tắc theo tổ chức, nhưng **nằm ở bảng khác** và có CLI riêng — dễ bị bỏ sót khi rà soát.

### 4.1 Template PPTX bị hạn chế — bảng `pptx_template_grants`

```bash
docker exec -it bookforge2-api python -m bookforge_api.scripts.grant_pptx_template \
    --org-id <uuid> --template-key canva_biology
docker exec -it bookforge2-api python -m bookforge_api.scripts.grant_pptx_template \
    --org-id <uuid> --template-key canva_biology --revoke
docker exec -it bookforge2-api python -m bookforge_api.scripts.grant_pptx_template --list
```

Tập template một tổ chức được offer = `public + (restricted ∩ granted)` ([`pptx_template_access.py:53-66`](../../backend/services/api/src/bookforge_api/services/pptx_template_access.py)).
Từ chối dùng chung mã lỗi với "theme không tồn tại" — cố ý, để tổ chức không suy ra được template nào đang tồn tại mà mình không có.
Grant cho một key đã khai tử thì **trơ**, không lỗi.

### 4.2 Chuyên gia — bảng `expert_agent_grants`

Cấp kèm lúc nạp kho (idempotent, chạy lại sẽ xoá–nạp lại và cập nhật dòng tại chỗ):

```bash
uv run --directory services/api python -m bookforge_api.scripts.ingest_expert_corpus \
    --corpus  <path>/corpus.json  --expert <path>/expert.json \
    --slug    sinh-hoc-thay-cong  --subject sinh_hoc \
    --name    "Trợ lý Sinh học 12 – thầy …" \
    --grant-org <org-uuid>
```

### 4.3 Cổng duyệt tài liệu — cột trên `organizations`

```bash
docker exec -it bookforge2-api python -m bookforge_api.scripts.set_document_approval_policy \
    --organization-id <uuid> --on
```

**Cố tình là CLI, không phải màn hình cài đặt**: nếu để nút này trong modal cài đặt tổ chức, một quản trị viên trường có thể tự tắt đúng cái cổng mà mình là người duyệt.

---

## 5. Công tắc vận hành / hạ tầng

| Env | Mặc định code | Mặc định compose | Tác dụng |
|---|---|---|---|
| `BOOKFORGE_QUEUE_INLINE` | `true` | **`false`** | `true` = chạy job ngay trong request (dev/test); `false` = đẩy sang RQ worker |
| `BOOKFORGE_EXAM_EXTRACT_INLINE_BLOCKING` | `false` | — | **Chỉ có nghĩa khi `queue_inline` bật.** `true` chạy job trích đề trong request (test suite dựa vào đây); client thật muốn `false` để route trả `202` rồi poll |
| `BOOKFORGE_KNOWLEDGE_DOCUMENT_DELETE_SUPPORTED` | `true` | — | Đặt `false` trên bản RAGFlow không đăng ký route DELETE (mọi delete `405`) — tránh round-trip chắc chắn hỏng + log lỗi gây hiểu nhầm |
| `BOOKFORGE_SESSION_COOKIE_SECURE` | `true` | `true` | Fail-closed. Chỉ dev mới đặt `false` |
| `BOOKFORGE_EMAIL_PROVIDER` | `console` | `console` | `console` in ra log; `resend` gửi thật (cần `BOOKFORGE_RESEND_API_KEY`) |
| `BOOKFORGE_ENV` | `development` | `production` | `production` **bắt buộc** phải set `BOOKFORGE_APP_ORIGIN` — validator raise ngay lúc khởi động |

### 5.1 Nhóm công tắc số tiến trình — có validator chặn cứng

`BOOKFORGE_UVICORN_WORKERS` · `BOOKFORGE_WORKER_COUNT` · `BOOKFORGE_INDEX_WORKER_COUNT` · `BOOKFORGE_DB_POOL_SIZE` · `BOOKFORGE_DB_MAX_OVERFLOW` · `BOOKFORGE_PG_MAX_CONNECTIONS`

Container **fail ngay lúc start** nếu `(uvicorn + worker + index_worker) × (pool_size + max_overflow) > pg_max_connections − 3`
([`settings.py:412-432`](../../backend/services/api/src/bookforge_api/core/settings.py)). Đây là hàng rào dựng sau sự cố production "Đang kiểm tra phiên đăng nhập…" (QueuePool cạn).

Ba cách xử lý khi đụng trần: hạ pool, hạ số tiến trình, hoặc nâng `BOOKFORGE_PG_MAX_CONNECTIONS` — **nâng thì phải sửa kèm `postgres -c max_connections=N` trong compose**, không thì vô nghĩa.

Cảnh báo mềm liên quan: `BOOKFORGE_GEMINI_HTTP_POOL` nhỏ hơn `BOOKFORGE_GEMINI_MAX_IN_FLIGHT` → limiter tự kẹp concurrency xuống bằng pool và log warning lúc start.

### 5.2 Profile hiệu năng — `infra/profiles/{dev,prod,bulk}.env`

Không phải cờ bật/tắt mà là **bộ knob thay cả cụm** (`BOOKFORGE_GEMINI_HTTP_POOL`, `BOOKFORGE_INGEST_JOB_TIMEOUT_SECONDS`, `BOOKFORGE_UVICORN_WORKERS`, `BOOKFORGE_WORKER_COUNT`). File profile **đè lên** `infra/shared/.env`. Profile `bulk` nâng timeout ingest lên 10800s cho sách lớn chạy 3 tiếng.

---

## 6. Công tắc frontend (build-time)

FE **không** có cờ per-org của riêng nó — mọi quyết định theo tổ chức đến từ `user.features` do BE trả (§1.2). Chỉ có 3 biến `VITE_*`:

| Biến | Mặc định | Tác dụng |
|---|---|---|
| `VITE_ENABLE_FEEDBACK_PROTOTYPE` | `false` | Bản prototype "cải thiện phản hồi" |
| `VITE_DEV_EMAIL` / `VITE_DEV_PASSWORD` | rỗng | Tự đăng nhập khi dev — **để trống ở mọi build thật** |
| `VITE_BOOKFORGE_BACKEND_TARGET` | — | Backend mà dev server proxy tới |

`VITE_ENABLE_FEEDBACK_PROTOTYPE` so sánh **chuỗi** `=== "true"` ([`lib/feature-flags.ts`](../../frontend/src/lib/feature-flags.ts)) — viết `1`, `TRUE`, `yes` đều bị coi là tắt. Bật thì mở: route `/feedback-improvement/*`, mục sidebar ([`Sidebar/index.tsx:733`](../../frontend/src/components/Sidebar/index.tsx)), nhánh trong [`main.tsx:21`](../../frontend/src/main.tsx) và [`HomePage/index.tsx:283`](../../frontend/src/templates/HomePage/index.tsx).

Đây là cờ **lúc build**, không phải lúc chạy — đổi là phải build lại FE.

---

## 7. Quy trình bật một tính năng sản phẩm cho một tổ chức

```bash
# 1) Bật env ở infra/shared/.env  (KHÔNG sửa compose — compose chỉ passthrough ${VAR:-default})
BOOKFORGE_CHAT_WORKSPACE_ENABLED=true
BOOKFORGE_CHAT_DOCUMENT_TOOLS_ENABLED=true     # workspace cần cờ này, xem §2.2

# 2) Khởi động lại api VÀ worker  (get_settings() có lru_cache, không reload nóng)
docker compose --env-file infra/shared/.env -f services/api/compose.yml up -d

# 3) Cấp cho tổ chức
docker exec -it bookforge2-api python -m bookforge_api.scripts.grant_feature \
    --org-id <uuid> --feature chat_workspace --feature chat_document_tools

# 4) Kiểm chứng — script tự in ra kết quả sau khi chạy
docker exec -it bookforge2-api python -m bookforge_api.scripts.grant_feature --org-id <uuid> --list
#   → granted_rows=['chat_document_tools', 'chat_workspace']
#   → resolved=['chat_document_tools', 'chat_workspace']     ← dòng NÀY mới là sự thật
```

**Đọc kết quả cho đúng**: `granted_rows` là dòng trong DB, `resolved` là kết quả sau khi đã AND với env.
`granted_rows` có mà `resolved` không có ⇒ **env đang tắt**, không phải lỗi grant.

Thu hồi:

```bash
... grant_feature --org-id <uuid> --feature chat_workspace --revoke
```

Mỗi lần grant/revoke thành công đều ghi một event `feature_granted` / `feature_revoked` kèm `feature_key` — có dấu vết kiểm toán.

---

## 8. Bẫy thường gặp

1. **Bật env rồi mà tính năng vẫn tắt.** Thiếu bước grant. Triệu chứng: `403 feature_not_available`, FE đá về `/`. Chạy `--list` và đọc dòng `resolved`.
2. **Sửa env rồi mà không ăn.** `get_settings()` bọc `lru_cache` ([`settings.py:526`](../../backend/services/api/src/bookforge_api/core/settings.py)) — **phải restart container**, không có reload nóng.
3. **Chỉ restart `api`, quên `worker`.** Job nền đọc cùng `Settings`; thiếu bước này thì HTTP một đằng, job một nẻo.
4. **Sửa `compose.common.yml` thay vì `.env`.** File compose chỉ là `${VAR:-default}` passthrough, và **được CI đồng bộ sang mọi stack** — sửa ở đó sẽ bị ghi đè.
5. **`grant_feature --feature expert_agents`** → `ValueError`. Key này đọc bảng khác, phải đi đường §4.2.
6. **`--all-orgs` từ chối chạy khi `BOOKFORGE_ENV=production`** ([`grant_feature.py:93`](../../backend/services/api/src/bookforge_api/scripts/grant_feature.py)) — chủ ý, không phải lỗi.
7. **Tổ chức mới không có tính năng nào.** `DEFAULT_FEATURE_GRANTS_FOR_NEW_ORGS` rỗng. Onboarding tổ chức mới phải có bước grant.
8. **Tắt `chat_inline_images_enabled` không tắt được phần bảo mật** — xem §3.3. Đừng dùng cờ này làm biện pháp ứng cứu sự cố rò rỉ.
9. **FE vẫn thấy tính năng sau khi revoke.** BE không cache, nhưng `auth-context` phía FE giữ user cũ. Tải lại trang.
10. **Bật `legal_mode` / `knowledge_enabled` mà chưa dựng service phụ thuộc** — cờ bật thành công, lỗi nổ lúc người dùng chat/upload. Dựng hạ tầng trước, bật cờ sau.

---

## 9. Tra nhanh — sửa gì ở đâu

| Muốn làm gì | Mở file nào |
|---|---|
| Thêm một product key mới | [`services/features.py:44-55`](../../backend/services/api/src/bookforge_api/services/features.py) + khai `*_enabled` trong [`core/settings.py`](../../backend/services/api/src/bookforge_api/core/settings.py) + passthrough trong [`services/api/compose.common.yml`](../../backend/services/api/compose.common.yml) |
| Xem cờ nào chỉ có env | `ENV_ONLY_ENABLED_ATTRS` — [`features.py:23-34`](../../backend/services/api/src/bookforge_api/services/features.py) |
| Chặn một router theo cờ | `Depends(require_feature('<key>'))` — mẫu ở [`main.py:87`](../../backend/services/api/src/bookforge_api/main.py) |
| Chặn theo tổ chức trong thân hàm | `feature_enabled(db, org_id, '<key>')` / `assert_feature(...)` |
| Chặn một route FE | `protectedFeatureRoute("<key>", <Page />)` — [`App.tsx`](../../frontend/src/App.tsx) |
| Ẩn/hiện một khối UI FE | `useFeature("<key>")` — [`hooks/use-feature.ts`](../../frontend/src/hooks/use-feature.ts) |
| Xem trạng thái đường phân quyền đang chạy | `GET /health` → `document_view` |
| Kiểm kê grant toàn hệ thống | `grant_feature --list` (không kèm `--org-id`) |
