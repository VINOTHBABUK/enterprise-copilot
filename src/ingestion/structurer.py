import json
from openai import OpenAI
from src.ingestion.database import Session, Document
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

STRUCTURE_PROMPT = """You are a document analyst.
Extract structured information from the text below.

Return ONLY valid JSON with these exact keys:
{
  "title":      "clear document title",
  "department": "one of: hr / engineering / sales / finance / general",
  "summary":    "2-3 sentence summary of the document",
  "key_facts":  ["fact 1", "fact 2", "fact 3"],
  "doc_type":   "one of: policy / guide / meeting / report / wiki"
}

Document text:
"""


def structure_document(raw_text):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": STRUCTURE_PROMPT + raw_text[:8000]
            }],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"  ✗ Structuring failed: {e}")
        return None


def structure_all_unprocessed():
    session = Session()
    unprocessed = session.query(Document)\
                         .filter(Document.summary == None)\
                         .all()

    print(f"Found {len(unprocessed)} unprocessed documents")

    for doc in unprocessed:
        print(f"Structuring: {doc.title or doc.url}")
        structured = structure_document(doc.raw_text)

        if structured:
            doc.title      = structured.get("title", doc.title)
            doc.department = structured.get("department", doc.department)
            doc.summary    = structured.get("summary", "")
            doc.key_facts  = structured.get("key_facts", [])
            doc.doc_type   = structured.get("doc_type", "wiki")
            print(f"  ✓ {doc.department} | {doc.doc_type}")

    session.commit()
    session.close()
    print("✓ Structuring complete")


if __name__ == "__main__":
    structure_all_unprocessed()