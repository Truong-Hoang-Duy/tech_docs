# DB dev khi task đổi cấu trúc bảng

Status: phiếu tra cứu, viết 2026-09-09. Áp dụng cho máy dev chạy SQLite.
Mọi lệnh chạy từ `backend/services/api` (venv tự kích hoạt khi `cd` vào đó).

## Làm nhanh: xoá tay `storage/bookforge.db` rồi chạy 2 lệnh

Xoá file bằng tay xong, chạy **cả hai** lệnh dưới. Một lệnh là chưa đủ.

```bash
cd backend/services/api

# 1. Dựng lại toàn bộ bảng + tổ chức mặc định + tài khoản
uv run python scripts/create_user.py --email owner@example.com --password "Supersafe123!" --full-name "Book Owner" --role admin

# 2. Seed khung chương trình (lệnh 1 KHÔNG làm việc này)
uv run python -c "
from bookforge_api.core.db import session_scope
from bookforge_api.services.question_curriculum_seed import seed_system_curriculum
with session_scope() as db: seed_system_curriculum(db)
print('seed xong')
"
```

Đo thật sau khi chạy (2026-09-09):

| | Chỉ lệnh 1 | Sau cả 2 lệnh |
|---|---|---|
| Số bảng | 49, khớp hoàn toàn với model | 49 |
| `organizations` / `users` | 1 / 1 | 1 / 1 |
| Khung kiến thức / năng lực / node | **0 / 0 / 0** | 44 / 11 / 2239 |

`scripts/create_user.py` tự gọi `init_db()` nên nó dựng đủ **bảng**, kể cả cột mới của migration vừa merge.
Nhưng seed khung chương trình chỉ nằm trong migration, mà máy dev không chạy migration — nên phải gọi tay ở lệnh 2. Bỏ lệnh 2 thì Ngân hàng câu hỏi rỗng.

Rồi khởi động lại API. Phần còn lại của file là chi tiết khi bạn **không** muốn xoá dữ liệu dev.

## Khi nào đọc file này

API trả 500, log có dòng dạng:

```text
sqlite3.OperationalError: no such column: canvas_chat_sessions.source_chat_session_id
                                          └──── bảng ────┘ └────── cột ──────┘
```

Khởi động lại app không hết. Phải tự sửa schema.

**Vì sao:** máy dev dựng bảng bằng `create_all` (chạy tự động lúc khởi động), không phải bằng alembic.
`create_all` chỉ tạo **bảng còn thiếu**, không bao giờ **thêm cột vào bảng đã có**.

**Đừng chạy `alembic upgrade head`** — DB dev không có bảng `alembic_version` nên alembic chạy lại từ đầu và báo `table organizations already exists`.

---

## Cách 1 — dựng lại từ đầu (mất dữ liệu dev)

Xem mục "Làm nhanh" ở đầu file. Nhớ sao lưu trước nếu còn tiếc:

```bash
cp storage/bookforge.db storage/bookforge.db.bak && rm storage/bookforge.db
```

---

## Cách 2 — vá tay (giữ nguyên dữ liệu dev)

Mở file migration mới nhất trong `alembic/versions/`, đọc hàm `upgrade()`, dịch sang SQL.

**Ví dụ thật** — migration `0088` có đoạn này:

```python
_TABLE = 'canvas_chat_sessions'                                   # ← đầu file
_COLUMN = 'source_chat_session_id'
_INDEX = 'ix_canvas_chat_sessions_source_chat_session_id'
...
op.add_column(_TABLE, sa.Column(_COLUMN, sa.String(36), nullable=True))
op.create_index(_INDEX, _TABLE, [_COLUMN])
```

Một số file đặt hằng số ở đầu như trên, một số viết thẳng chuỗi vào lời gọi — giá trị thật đều nằm ngay trong file đó.

Dịch thành:

```bash
cd backend/services/api
cp storage/bookforge.db storage/bookforge.db.bak
python -c "
import sqlite3
c = sqlite3.connect('storage/bookforge.db')
c.execute('ALTER TABLE canvas_chat_sessions ADD COLUMN source_chat_session_id VARCHAR(36)')
c.execute('CREATE INDEX ix_canvas_chat_sessions_source_chat_session_id ON canvas_chat_sessions (source_chat_session_id)')
c.commit(); c.close()
print('xong')
"
```

Chỗ cần thay khi migration khác:

| Trong migration | Thay vào SQL |
|---|---|
| `'canvas_chat_sessions'` | tên bảng |
| `'source_chat_session_id'` | tên cột |
| `sa.String(36)` | `VARCHAR(36)` · `sa.Integer()` → `INTEGER` · `sa.Boolean()` → `BOOLEAN` · `sa.Text()` → `TEXT` · `sa.DateTime()` → `DATETIME` · `sa.JSON()` → `JSON` |
| `'ix_...'` | tên index (bỏ luôn câu `CREATE INDEX` nếu migration không có) |

**Bỏ qua `op.create_foreign_key`.** SQLite không gắn được khoá ngoại vào bảng đã có; migration của dự án cũng đã bỏ qua nó (`if not _is_sqlite()`).

---

## Kiểm tra lại (chạy sau cả hai cách)

Câu này đối chiếu toàn bộ model với DB thật:

```bash
cd backend/services/api
python -c "
import sqlite3
import bookforge_api.models  # noqa
from bookforge_api.core.db import Base
c = sqlite3.connect('storage/bookforge.db')
tables = {r[0] for r in c.execute(\"select name from sqlite_master where type='table'\")}
lech = []
for name, t in Base.metadata.tables.items():
    if name not in tables:
        lech.append('THIEU BANG ' + name); continue
    cols = {r[1] for r in c.execute(f'PRAGMA table_info({name})')}
    lech += [f'THIEU COT {name}.{col.name}' for col in t.columns if col.name not in cols]
print(lech or 'KHOP HOAN TOAN')
"
```

`KHOP HOAN TOAN` là xong. Ra danh sách thì vá tiếp theo Cách 2.

Sau Cách 1, số liệu tham chiếu: `organizations` 1 · `question_knowledge_frameworks` 44 · `question_competency_frameworks` 11 · `question_knowledge_nodes` 2239.
Bốn bảng khung rỗng nghĩa là quên bước seed.

---

## Hai điều dễ nhầm

**`storage/` không bị xoá cùng DB.** File tài liệu cũ thành mồ côi (~900 MB nếu dùng lâu). Muốn dọn thì xoá `storage/organizations/`, `storage/staging/`, `storage/trash/` — đừng xoá cả `storage/`, vì `logs/` và file `.bak` nằm trong đó.

**Log đầy `redis.exceptions.TimeoutError`** là do Redis không chạy, không liên quan tới DB. Request vẫn trả 200.
