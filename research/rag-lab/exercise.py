"""RAG Lab (mien phi, khong can API key, khong can pip install).

Bai tap: tu code phan sparse retrieval (TF-IDF + cosine similarity) -
chinh la mot nua thuat toan hybrid search dang chay that trong
backend/services/knowledge-retrieval/rag/nlp/search.py cua project nay.

Corpus: cac file markdown trong docs/ cua chinh project bookforge.

Chay:
    python3 docs/rag-lab/exercise.py "cau hoi cua ban"

Xem docs/rag-lab/README.md de hieu ly thuyet truoc khi lam.
Xem docs/rag-lab/solution.py de doi chieu SAU KHI da tu lam.
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


def load_chunks() -> list[dict]:
    """Doc cac file markdown va cat theo doan (paragraph). Da lam san."""
    chunks = []
    for filename in CORPUS_FILES:
        path = DOCS_DIR / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for i, para in enumerate(text.split("\n\n")):
            para = para.strip()
            if len(para) < 40:  # bo qua doan qua ngan (heading rong, v.v.)
                continue
            chunks.append({"source": filename, "chunk_id": i, "text": para})
    return chunks


def tokenize(text: str) -> list[str]:
    """TODO 1: tach text thanh danh sach token (tu) da lowercase.

    Goi y:
    - Dung regex de lay cac chuoi ky tu chu + so, giu duoc dau tieng Viet.
      Vi du pattern: r"[\\wàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩ...]+"
      (de don gian, ban co the dung r"\\w+" truoc, tieng Viet co dau van
      hoat dong duoc vi \\w trong Python 3 mac dinh la Unicode-aware).
    - Loai bo token toan la so hoac qua ngan (vi du 1 ky tu) neu muon,
      khong bat buoc.

    Return: list[str], vi du tokenize("Xin chao Ban Forge!")
            -> ["xin", "chao", "ban", "forge"]
    """
    raise NotImplementedError("TODO 1: implement tokenize()")


def build_tf_idf(chunks: list[dict]) -> tuple[list[dict], dict[str, float]]:
    """TODO 2: tinh TF-IDF vector cho tung chunk.

    TF-IDF cua tu w trong doc d:
        tf(w, d)  = so lan w xuat hien trong d / tong so tu trong d
        idf(w)    = log(N / (1 + df(w)))
            N = tong so chunk, df(w) = so chunk co chua w it nhat 1 lan
        tfidf(w, d) = tf(w, d) * idf(w)

    Cac buoc:
    1. Voi moi chunk, tokenize() text -> dem tan suat tung tu (Counter).
    2. Tinh document frequency df(w) cho moi tu tren toan corpus.
    3. Tinh idf(w) = math.log(N / (1 + df(w))) cho moi tu xuat hien it nhat
       1 lan trong corpus.
    4. Voi moi chunk, tinh vector tfidf: dict[tu -> diem tfidf].
       Luu vector nay vao chunk["vector"] (them key moi vao dict co san).

    Return: (chunks da co them key "vector", dict idf toan corpus)
            -> can idf de sau nay vector-hoa CAU HOI bang chinh idf nay.
    """
    raise NotImplementedError("TODO 2: implement build_tf_idf()")


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """TODO 3: tinh cosine similarity giua 2 vector dang sparse (dict).

    cosine(a, b) = dot(a, b) / (norm(a) * norm(b))

    Vi vector la sparse (dict), chi can duyet qua cac key CHUNG giua a va b
    de tinh dot product (khong can dense array).

    Neu norm(a) == 0 hoac norm(b) == 0 -> return 0.0 (tranh chia cho 0).
    """
    raise NotImplementedError("TODO 3: implement cosine_similarity()")


def vectorize_query(query: str, idf: dict[str, float]) -> dict[str, float]:
    """Da lam san: bien cau hoi thanh tf-idf vector, dung idf cua corpus."""
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
    """TODO 4: ghep vectorize_query + cosine_similarity de tra ve top_k chunk.

    Cac buoc:
    1. query_vec = vectorize_query(query, idf)
    2. Voi moi chunk, tinh score = cosine_similarity(query_vec, chunk["vector"])
    3. Sap xep chunk theo score giam dan, lay top_k
    4. Return list[dict] gom cac chunk (co them key "score"), da sap xep

    Bo qua chunk co score == 0 (khong lien quan gi ca).
    """
    raise NotImplementedError("TODO 4: implement retrieve()")


def build_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """TODO 5: ghep query + cac chunk lay duoc thanh 1 prompt hoan chinh.

    Day chinh la viec ma backend/services/knowledge-retrieval/rag/prompts/generator.py
    lam trong he thong that: nhet context vao truoc, roi moi den cau hoi, kem
    huong dan cho LLM chi duoc tra loi dua tren context.

    Format goi y (co the tuy chinh):

        Ban la tro ly, chi duoc tra loi dua tren CONTEXT duoi day.
        Neu CONTEXT khong co thong tin lien quan, hay noi "khong tim thay
        thong tin lien quan".

        --- CONTEXT ---
        [Nguon: <source> - doan #<chunk_id>]
        <text>

        [Nguon: <source> - doan #<chunk_id>]
        <text>
        --- HET CONTEXT ---

        Cau hoi: <query>
        Tra loi:
    """
    raise NotImplementedError("TODO 5: implement build_prompt()")


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
