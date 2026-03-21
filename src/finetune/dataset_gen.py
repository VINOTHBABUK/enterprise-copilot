import json
import os
from openai import OpenAI
from src.ingestion.database import Session, Document
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

DATASET_PATH = "./data/structured/training_data.jsonl"

QA_PROMPT = """You are a dataset generator for fine-tuning a language model.

Given the document text below, generate 5 question-answer pairs.
Questions should be realistic things an employee would ask.
Answers should be clear, concise, and based ONLY on the document.

Return ONLY valid JSON in this exact format:
{
  "pairs": [
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."}
  ]
}

Document title: {title}
Document text:
{text}
"""


def generate_qa_pairs(doc):
    try:
        prompt = QA_PROMPT\
            .replace("{title}", doc.title or "")\
            .replace("{text}", doc.raw_text[:6000])

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(resp.choices[0].message.content)
        pairs  = result.get("pairs", [])
        return pairs

    except Exception as e:
        print(f"  ✗ Generation failed: {e}")
        return []


def format_for_training(question, answer):
    return {
        "messages": [
            {
                "role":    "system",
                "content": "You are a helpful enterprise knowledge assistant."
            },
            {
                "role":    "user",
                "content": question
            },
            {
                "role":    "assistant",
                "content": answer
            }
        ]
    }


def generate_dataset():
    session   = Session()
    documents = session.query(Document)\
                       .filter(Document.summary != None)\
                       .all()
    session.close()

    if not documents:
        print("No documents found. Run scraper + structurer first.")
        return

    print(f"Generating Q&A pairs from {len(documents)} documents...\n")

    os.makedirs("data/structured", exist_ok=True)
    all_pairs = []

    for doc in documents:
        print(f"Document: {doc.title}")
        pairs = generate_qa_pairs(doc)
        print(f"  ✓ Generated {len(pairs)} Q&A pairs")

        for pair in pairs:
            formatted = format_for_training(
                pair["question"],
                pair["answer"]
            )
            all_pairs.append(formatted)

    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        for item in all_pairs:
            f.write(json.dumps(item) + "\n")

    print(f"\n✓ Dataset saved to {DATASET_PATH}")
    print(f"✓ Total training examples: {len(all_pairs)}")

    print("\nSample Q&A pairs:")
    print("-" * 50)
    for item in all_pairs[:3]:
        msgs = item["messages"]
        print(f"Q: {msgs[1]['content']}")
        print(f"A: {msgs[2]['content'][:150]}...")
        print()


if __name__ == "__main__":
    generate_dataset()