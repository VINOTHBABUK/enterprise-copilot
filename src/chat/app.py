import gradio as gr
from src.chat.router import route
from src.ingestion.database import Session, Document
from src.meetings.summariser import summarise_text
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
    return "Unknown tool."


def search_docs(query, department=None):
    session  = Session()
    q        = session.query(Document)

    if department:
        q = q.filter(Document.department == department)

    keywords = query.split()
    for keyword in keywords:
        if len(keyword) > 4:
            q = q.filter(Document.raw_text.contains(keyword))

    docs = q.limit(3).all()
    session.close()

    if not docs:
        return "No matching documents found in the knowledge base."

    results = []
    for doc in docs:
        results.append(
            f"**{doc.title}** ({doc.department})\n"
            f"{doc.summary or doc.raw_text[:300]}...\n"
            f"Source: {doc.url}"
        )
    return "\n\n---\n\n".join(results)


def summarise(content, fmt):
    return summarise_text(content)


def answer_general(question):
    from openai import OpenAI
    client = OpenAI()

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )
    return resp.choices[0].message.content


def chat(message, history):
    routing       = route(message)
    tool_response = execute_tool(routing["tool"], routing["args"])

    label = {
        "search_knowledge":   "Knowledge Search",
        "summarise_document": "Document Summary",
        "answer_general":     "General Answer",
    }.get(routing["tool"], routing["tool"])

    return f"**[{label}]**\n\n{tool_response}"


with gr.Blocks(title="Enterprise Copilot") as demo:
    gr.Markdown("# Enterprise Knowledge Copilot")
    gr.Markdown(
        "Ask questions about company knowledge, "
        "summarise meeting transcripts, or get general answers."
    )

    gr.ChatInterface(
        fn=chat,
        examples=[
            "What is the leave policy for contractors?",
            "What is incident management?",
            "What is a knowledge base used for?",
            "What is the capital of France?",
            "Summarise this meeting: Priya will fix the auth service by Friday. Arjun will rollback PR 892 if not done. Team decided to use feature flags. Mobile push deferred to Sprint 15.",
        ],
        type="messages"
    )

if __name__ == "__main__":
    demo.launch()