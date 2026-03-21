import gradio as gr
from src.chat.router import route
from src.ingestion.database import Session, Document
from src.meetings.summariser import summarise_text
from src.rag.rag_chain import ask, format_response
from src.agents.workflow import run_workflow
from dotenv import load_dotenv

load_dotenv()


def execute_tool(tool_name, args):
    if tool_name == "search_knowledge":
        return search_docs(
            args["query"],
            args.get("department")
        )
    elif tool_name == "summarise_document":
        return summarise(
            args["content"],
            args.get("output_format", "detailed")
        )
    elif tool_name == "answer_general":
        return answer_general(args["question"])
    elif tool_name == "run_agent":
        return run_agent(args["request"])
    return "Unknown tool."


def search_docs(query, department=None):
    result = ask(query, department)
    return format_response(result)


def summarise(content, fmt):
    return summarise_text(content)


def answer_general(question):
    from openai import OpenAI
    client = OpenAI()

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":    "user",
                "content": question
            }
        ]
    )
    return resp.choices[0].message.content


def run_agent(request):
    try:
        context = run_workflow(request)
        report  = context.get("report", "")

        if report and len(report.strip()) > 10:
            return report

        # Build report manually from context if empty
        output = f"## Workflow Results\n\n"

        if context["meetings"]:
            output += f"**Meetings analysed:** {len(context['meetings'])}\n\n"
            for m in context["meetings"]:
                output += f"### {m['title']}\n"
                output += f"{m['summary']}\n\n"
                if m["action_items"]:
                    output += "**Action Items:**\n"
                    for item in m["action_items"]:
                        output += f"- {item.get('owner','?')}: {item.get('task','?')} — {item.get('due','?')}\n"
                    output += "\n"

        if context["risks"]:
            output += f"**Risks & Blockers ({len(context['risks'])} found):**\n"
            for r in context["risks"]:
                output += f"- {r['risk']} ({r['meeting']})\n"

        return output

    except Exception as e:
        return f"Agent error: {str(e)}"


def chat(message, history):
    routing       = route(message)
    tool_response = execute_tool(
        routing["tool"],
        routing["args"]
    )

    label = {
        "search_knowledge":   "Knowledge Search",
        "summarise_document": "Document Summary",
        "answer_general":     "General Answer",
        "run_agent":          "Agent Workflow",
    }.get(routing["tool"], routing["tool"])

    return f"**[{label}]**\n\n{tool_response}"


with gr.Blocks(title="Enterprise Copilot") as demo:
    gr.Markdown("# Enterprise Knowledge Copilot")
    gr.Markdown(
        "Ask questions about company knowledge, "
        "summarise meeting transcripts, run agent "
        "workflows, or get general answers."
    )

    gr.ChatInterface(
        fn=chat,
        examples=[
            "What is the leave policy for contractors?",
            "What is incident management?",
            "What is a knowledge base used for?",
            "Give me all risks and blockers from this week's meetings",
            "Summarise all meetings and list all action items",
            "Summarise this meeting: Priya will fix the auth service by Friday. Arjun will rollback PR 892 if not done. Team decided to use feature flags. Mobile push deferred to Sprint 15.",
        ],
        type="messages"
    )

if __name__ == "__main__":
    demo.launch()