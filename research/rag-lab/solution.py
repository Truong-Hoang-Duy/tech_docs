"""RAG Lab - loi giai day du. Chi xem SAU KHI da tu lam exercise.py.

Chay:
    python3 docs/rag-lab/solution.py "cau hoi cua ban"
"""

from __future__ import annotations

import math
import re
import sys
from collections import Counter
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent
CORPUS_FILES = [
    "READING_GUIDE.md",
    "features-cursor.md",
    "BAO_CAO_SO_SANH_VIET_LAI.md",
]

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def load_chunks() -> list[dict]:
    chunks = []
    for filename in CORPUS_FILES:
        path = DOCS_DIR / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for i, para in enumerate(text.split("\n\n")):
            para = para.strip()
            if len(para) < 40:
                continue
            chunks.append({"source": filename, "chunk_id": i, "text": para})
    return chunks


def tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in _TOKEN_RE.findall(text)]


def build_tf_idf(chunks: list[dict]) -> tuple[list[dict], dict[str, float]]:
    n = len(chunks)

    doc_tokens = []
    for chunk in chunks:
        tokens = tokenize(chunk["text"])
        doc_tokens.append(tokens)

    df: Counter[str] = Counter()
    for tokens in doc_tokens:
        for word in set(tokens):
            df[word] += 1

    idf = {word: math.log(n / (1 + count)) for word, count in df.items()}

    for chunk, tokens in zip(chunks, doc_tokens):
        tf = Counter(tokens)
        total = len(tokens) or 1
        chunk["vector"] = {
            word: (count / total) * idf.get(word, 0.0)
            for word, count in tf.items()
        }

    return chunks, idf


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0

    shared_keys = set(vec_a) & set(vec_b)
    dot = sum(vec_a[k] * vec_b[k] for k in shared_keys)

    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def vectorize_query(query: str, idf: dict[str, float]) -> dict[str, float]:
    tokens = tokenize(query)
    if not tokens:
        return {}
    tf = Counter(tokens)
    total = len(tokens)
    return {
        word: (count / total) * idf.get(word, 0.0)
        for word, count in tf.items()
    }


def retrieve(query: str, chunks: list[dict], idf: dict[str, float], top_k: int = 3) -> list[dict]:
    query_vec = vectorize_query(query, idf)

    scored = []
    for chunk in chunks:
        score = cosine_similarity(query_vec, chunk["vector"])
        if score > 0:
            scored.append({**chunk, "score": score})

    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:top_k]


def build_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    context_blocks = []
    for chunk in retrieved_chunks:
        context_blocks.append(
            f"[Nguon: {chunk['source']} - doan #{chunk['chunk_id']}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_blocks) if context_blocks else "(khong co ngu canh lien quan)"

    return f"""Ban la tro ly, chi duoc tra loi dua tren CONTEXT duoi day.
Neu CONTEXT khong co thong tin lien quan, hay noi "khong tim thay thong tin lien quan".

--- CONTEXT ---
{context}
--- HET CONTEXT ---

Cau hoi: {query}
Tra loi:"""


def main() -> None:
    query = " ".join(sys.argv[1:]) or "kien truc backend gom nhung service nao?"

    chunks = load_chunks()
    if not chunks:
        print("Khong tim thay corpus. Kiem tra lai duong dan DOCS_DIR.")
        return

    chunks, idf = build_tf_idf(chunks)
    results = retrieve(query, chunks, idf, top_k=3)

    print(f"Cau hoi: {query}\n")
    print(f"Top {len(results)} chunk lien quan nhat:\n")
    for r in results:
        print(f"  [score={r['score']:.4f}] {r['source']} #{r['chunk_id']}")
        print(f"    {r['text'][:120]}...\n")

    prompt = build_prompt(query, results)
    print("=" * 60)
    print("PROMPT hoan chinh (dan vao bat ky LLM mien phi nao de lay cau tra loi):")
    print("=" * 60)
    print(prompt)


if __name__ == "__main__":
    main()
