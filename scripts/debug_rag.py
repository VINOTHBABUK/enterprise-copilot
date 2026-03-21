from src.rag.retriever import hybrid_search

results = hybrid_search("leave policy contractors", k=5)

for i, r in enumerate(results):
    print(f"--- Chunk {i+1} ---")
    print(r["content"])
    print()