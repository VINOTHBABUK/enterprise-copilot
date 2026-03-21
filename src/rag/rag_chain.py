from openai import OpenAI
from src.rag.retriever import hybrid_search
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

RAG_PROMPT = """You are an enterprise knowledge assistant.
Answer the question based on the context provided below.
Use the information available even if it is partial.
If there is truly no relevant information, say so.

Always end your answer with:
Source: [document title]

Context:
{context}

Question: {question}

Answer:"""


def ask(question, department=None, k=5):
    print(f"\nSearching knowledge base...")
    chunks = hybrid_search(question, department, k)

    if not chunks:
        return {
            "answer":  "No relevant documents found.",
            "sources": [],
            "chunks":  0
        }

    context = "\n\n---\n\n".join([
        f"From: {c['title']}\n{c['content']}"
        for c in chunks
    ])

    sources = list(set([
        c['title'] for c in chunks if c['title']
    ]))

    print(f"Found {len(chunks)} relevant chunks")
    print(f"Sources: {sources}")

    prompt = RAG_PROMPT\
        .replace("{context}", context)\
        .replace("{question}", question)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful enterprise assistant. Answer based only on the provided context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = resp.choices[0].message.content

    return {
        "answer":  answer,
        "sources": sources,
        "chunks":  len(chunks)
    }


def format_response(result):
    output  = result["answer"]
    output += f"\n\n---"
    output += f"\nSources: {', '.join(result['sources'])}"
    output += f"\nChunks retrieved: {result['chunks']}"
    return output


if __name__ == "__main__":
    questions = [
        "What is the leave policy for contractors?",
        "How do you handle a service incident?",
        "What is a knowledge base used for?",
    ]

    for q in questions:
        print(f"\nQuestion: {q}")
        print("-" * 50)
        result = ask(q)
        print(format_response(result))
        print()