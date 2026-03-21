import json
import time
from openai import OpenAI
from src.ingestion.database import Session, LLMLog
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search company documents to answer questions about policies, procedures, or incidents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "department": {
                        "type": "string",
                        "enum": ["hr", "engineering",
                                 "sales", "finance", "general"],
                        "description": "Filter by department"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarise_document",
            "description": "Summarise a long document, meeting transcript, or any text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text to summarise"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["brief", "detailed", "action_items"],
                        "default": "detailed"
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "answer_general",
            "description": "Answer a general question that does not need document search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string"
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_agent",
            "description": "Run a multi-step agent workflow for complex requests that need multiple operations like fetching meetings, extracting risks, and generating reports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "The complex request to handle"
                    }
                },
                "required": ["request"]
            }
        }
    }
]


def route(user_message, user_id="demo"):
    start = time.time()

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role":    "system",
                "content": "You are an enterprise AI copilot. "
                           "Use the right tool for each request. "
                           "Use run_agent for complex multi-step "
                           "requests involving meetings, risks, "
                           "reports, or workflows."
            },
            {
                "role":    "user",
                "content": user_message
            }
        ],
        tools=TOOLS,
        tool_choice="auto"
    )

    latency_ms = (time.time() - start) * 1000
    message    = resp.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
    else:
        tool_name = "answer_general"
        tool_args = {"question": user_message}

    _log_call(user_id, user_message, tool_name,
              "gpt-4o", resp.usage, latency_ms)

    print(f"  → Tool: {tool_name}")
    print(f"  → Args: {tool_args}")

    return {
        "tool": tool_name,
        "args": tool_args
    }


def _log_call(user, query, tool, model, usage, latency):
    try:
        session = Session()
        log = LLMLog(
            user=user,
            query=query,
            tool_called=tool,
            model=model,
            tokens_in=usage.prompt_tokens,
            tokens_out=usage.completion_tokens,
            cost_usd=_calc_cost(model, usage),
            latency_ms=latency
        )
        session.add(log)
        session.commit()
        session.close()
    except Exception as e:
        print(f"  ✗ Logging failed: {e}")


def _calc_cost(model, usage):
    rates = {
        "gpt-4o":      (0.005, 0.015),
        "gpt-4o-mini": (0.00015, 0.0006),
    }
    r = rates.get(model, (0.005, 0.015))
    return (usage.prompt_tokens / 1000 * r[0] +
            usage.completion_tokens / 1000 * r[1])


if __name__ == "__main__":
    tests = [
        "What is the leave policy for contractors?",
        "Summarise this text: The meeting covered Q3 goals.",
        "Give me all risks from this week's meetings",
        "What is the capital of France?",
    ]
    for msg in tests:
        print(f"\nQuery: {msg}")
        route(msg)