import json
from datetime import datetime
from openai import OpenAI
from src.ingestion.database import Session, Meeting
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

SUMMARY_PROMPT = """You are an expert meeting analyst.
Analyse this meeting transcript and extract structured information.

Return ONLY valid JSON with these exact keys:
{
  "title":        "short descriptive meeting title",
  "summary":      "2-3 sentence overview of the meeting",
  "action_items": [
    {"task": "description", "owner": "person name", "due": "timeframe"}
  ],
  "decisions":    ["decision 1", "decision 2"],
  "risk_flags":   ["risk 1", "risk 2"]
}

If no action items, decisions, or risks are found return empty lists.

Transcript:
"""


def summarise_transcript(transcript, meeting_date=None):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": SUMMARY_PROMPT + transcript[:12000]
            }],
            response_format={"type": "json_object"}
        )
        result = json.loads(resp.choices[0].message.content)
        return result
    except Exception as e:
        print(f"  ✗ Summarisation failed: {e}")
        return None


def save_meeting(transcript, audio_path="", meeting_date=None):
    print("Summarising transcript...")
    structured = summarise_transcript(transcript)

    if not structured:
        return None

    session = Session()
    meeting = Meeting(
        title        = structured.get("title", "Untitled Meeting"),
        date         = meeting_date or datetime.utcnow(),
        transcript   = transcript,
        summary      = structured.get("summary", ""),
        action_items = structured.get("action_items", []),
        decisions    = structured.get("decisions", []),
        risk_flags   = structured.get("risk_flags", [])
    )
    session.add(meeting)
    session.commit()

    print(f"  ✓ Meeting saved: {meeting.title}")
    print(f"  ✓ Action items: {len(meeting.action_items)}")
    print(f"  ✓ Decisions:    {len(meeting.decisions)}")
    print(f"  ✓ Risk flags:   {len(meeting.risk_flags)}")

    session.close()
    return meeting


def summarise_text(transcript):
    structured = summarise_transcript(transcript)
    if not structured:
        return "Could not summarise."

    output  = f"**{structured.get('title', 'Meeting')}**\n\n"
    output += f"**Summary**\n{structured.get('summary', '')}\n\n"

    items = structured.get("action_items", [])
    if items:
        output += "**Action Items**\n"
        for item in items:
            output += f"- {item.get('owner','?')}: {item.get('task','?')} — {item.get('due','?')}\n"
        output += "\n"

    decisions = structured.get("decisions", [])
    if decisions:
        output += "**Decisions**\n"
        for d in decisions:
            output += f"- {d}\n"
        output += "\n"

    risks = structured.get("risk_flags", [])
    if risks:
        output += "**Risk Flags**\n"
        for r in risks:
            output += f"- {r}\n"

    return output


if __name__ == "__main__":
    test_transcript = """
    Good morning everyone. Let's start the sprint review.
    Priya, can you give us the auth service update?

    Priya: Sure. We identified the latency spike — it's coming
    from PR 892. I'll profile it by Friday and fix it.

    Arjun: If it's not fixed by end of day today I'll roll it back.
    We can't have 12 percent of logins failing.

    Manager: Agreed. Let's also adopt feature flags going forward
    for any auth changes — that's decided. Mobile push notifications
    are deferred to Sprint 15.

    Priya: One more risk — if the latency continues, it could
    affect our SLO targets for the quarter.
    """

    result = summarise_text(test_transcript)
    print(result)