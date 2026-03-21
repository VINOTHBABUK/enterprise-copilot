from openai import OpenAI
from src.ingestion.database import Session, Meeting, Document
from src.rag.rag_chain import ask
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()


def fetch_meetings():
    session  = Session()
    meetings = session.query(Meeting)\
                      .order_by(Meeting.created_at.desc())\
                      .limit(10)\
                      .all()
    session.close()

    if not meetings:
        return []

    return [
        {
            "id":           m.id,
            "title":        m.title,
            "summary":      m.summary,
            "action_items": m.action_items or [],
            "decisions":    m.decisions or [],
            "risk_flags":   m.risk_flags or [],
        }
        for m in meetings
    ]


def fetch_documents(department=None):
    session = Session()
    q       = session.query(Document)

    if department:
        q = q.filter(Document.department == department)

    docs = q.limit(10).all()
    session.close()

    return [
        {
            "id":         d.id,
            "title":      d.title,
            "department": d.department,
            "summary":    d.summary,
            "key_facts":  d.key_facts or [],
        }
        for d in docs
    ]


def extract_risks(meetings):
    if not meetings:
        return []

    all_risks = []
    for meeting in meetings:
        risks = meeting.get("risk_flags", [])
        for risk in risks:
            all_risks.append({
                "risk":    risk,
                "meeting": meeting.get("title", "Unknown")
            })

    return all_risks


def search_knowledge(query, department=None):
    result = ask(query, department)
    return result


def generate_report(data, report_type="summary"):
    prompt = f"""You are an enterprise report generator.
Generate a clear, structured {report_type} report.

Data provided:
{json.dumps(data, indent=2)}

Format the report with:
- Executive Summary (2-3 sentences)
- Key Findings (bullet points)
- Action Items (if any)
- Risks & Blockers (if any)
- Recommendations

Keep it concise and professional."""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    print("Testing specialists...\n")

    print("Fetching meetings...")
    meetings = fetch_meetings()
    print(f"  Found {len(meetings)} meetings")

    print("\nFetching documents...")
    docs = fetch_documents()
    print(f"  Found {len(docs)} documents")

    print("\nExtracting risks...")
    risks = extract_risks(meetings)
    print(f"  Found {len(risks)} risks")
    for r in risks:
        print(f"  - {r['risk']} ({r['meeting']})")