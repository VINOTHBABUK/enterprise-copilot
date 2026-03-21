from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

SUPERVISOR_PROMPT = """You are a supervisor agent for an enterprise AI copilot.
Your job is to analyse the user request and create a step-by-step plan.

Available specialist tools:
- fetch_meetings     : retrieves all meetings from database
- fetch_documents    : retrieves company documents
- extract_risks      : extracts risks from meetings
- search_knowledge   : searches knowledge base with RAG
- generate_report    : generates formatted report

Return ONLY valid JSON:
{
  "plan": [
    {"step": 1, "tool": "tool_name", "reason": "why this step"},
    {"step": 2, "tool": "tool_name", "reason": "why this step"}
  ],
  "final_goal": "what the final output should be"
}

User request: {request}
"""


def plan(user_request):
    prompt = SUPERVISOR_PROMPT.replace(
        "{request}", user_request
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    result = json.loads(resp.choices[0].message.content)
    return result


if __name__ == "__main__":
    requests = [
        "Give me all risks from this week's meetings",
        "Summarise all meetings and create an action item report",
        "What is our leave policy and what risks exist?",
    ]

    for req in requests:
        print(f"\nRequest: {req}")
        print("-" * 50)
        result = plan(req)
        print(f"Goal: {result['final_goal']}")
        print("Plan:")
        for step in result["plan"]:
            print(f"  Step {step['step']}: "
                  f"{step['tool']} — {step['reason']}")