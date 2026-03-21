from rank_bm25 import BM25Okapi
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.rag.embedder import get_vectorstore
from dotenv import load_dotenv

load_dotenv()

_vectorstore = None
_bm25        = None
_bm25_docs   = None


def get_vs():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = get_vectorstore()
    return _vectorstore


def vector_search(query, department=None, k=5):
    vs = get_vs()

    where = None
    if department:
        where = {"department": department}

    results = vs.similarity_search_with_score(
        query,
        k=k,
        filter=where
    )

    return [
        {
            "content":    doc.page_content,
            "source":     doc.metadata.get("source", ""),
            "title":      doc.metadata.get("title", ""),
            "department": doc.metadata.get("department", ""),
            "score":      float(score),
            "method":     "vector"
        }
        for doc, score in results
    ]


def build_bm25_index():
    global _bm25, _bm25_docs
    vs      = get_vs()
    results = vs.get()

    if not results or not results["documents"]:
        print("No documents in vectorstore yet.")
        return

    _bm25_docs = []
    for i, text in enumerate(results["documents"]):
        meta = results["metadatas"][i] if results["metadatas"] else {}
        _bm25_docs.append({
            "content":    text,
            "source":     meta.get("source", ""),
            "title":      meta.get("title", ""),
            "department": meta.get("department", ""),
        })

    tokenized = [doc["content"].split() for doc in _bm25_docs]
    _bm25     = BM25Okapi(tokenized)
    print(f"✓ BM25 index built with {len(_bm25_docs)} chunks")


def bm25_search(query, k=5):
    global _bm25, _bm25_docs

    if _bm25 is None:
        build_bm25_index()

    if _bm25 is None:
        return []

    tokens = query.split()
    scores = _bm25.get_scores(tokens)

    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    return [
        {
            "content":    _bm25_docs[i]["content"],
            "source":     _bm25_docs[i]["source"],
            "title":      _bm25_docs[i]["title"],
            "department": _bm25_docs[i]["department"],
            "score":      float(scores[i]),
            "method":     "bm25"
        }
        for i in top_indices
        if scores[i] > 0
    ]


def hybrid_search(query, department=None, k=5):
    vector_results = vector_search(query, department, k)
    bm25_results   = bm25_search(query, k)

    seen    = set()
    merged  = []

    for result in vector_results + bm25_results:
        key = result["content"][:100]
        if key not in seen:
            seen.add(key)
            merged.append(result)

    merged = merged[:k]
    return merged


if __name__ == "__main__":
    print("Testing hybrid search...\n")

    results = hybrid_search("leave policy contractors", k=3)

    for i, r in enumerate(results):
        print(f"Result {i+1}:")
        print(f"  Title:   {r['title']}")
        print(f"  Method:  {r['method']}")
        print(f"  Score:   {r['score']:.4f}")
        print(f"  Content: {r['content'][:150]}...")
        print()