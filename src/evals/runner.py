import time
from openai import OpenAI
from src.evals.evaluator import evaluate
from src.ingestion.database import Session, LLMLog
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

TEST_QUESTIONS = [
    {
        "question": "What is incident management?",
        "department": "engineering"
    },
    {
        "question": "What is a knowledge base?",
        "department": "general"
    },
    {
        "question": "What is leave of absence?",
        "department": "hr"
    },
    {
        "question": "How do you handle service disruptions?",
        "department": "engineering"
    },
    {
        "question": "What are best practices for knowledge management?",
        "department": "general"
    },
]

MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
]

COST_RATES = {
    "gpt-4o":      (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
}


def run_model(model, question):
    start = time.time()

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful enterprise assistant. Answer clearly and concisely."
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    latency_ms = (time.time() - start) * 1000
    answer     = resp.choices[0].message.content
    usage      = resp.usage

    rates      = COST_RATES.get(model, (0.005, 0.015))
    cost       = (usage.prompt_tokens / 1000 * rates[0] +
                  usage.completion_tokens / 1000 * rates[1])

    return answer, latency_ms, cost, usage


def run_evals():
    print("Running evaluations...\n")
    results = []

    for model in MODELS:
        print(f"Model: {model}")
        print("-" * 40)

        model_scores    = []
        model_latencies = []
        model_costs     = []

        for item in TEST_QUESTIONS:
            question = item["question"]
            print(f"  Q: {question[:50]}...")

            answer, latency_ms, cost, usage = run_model(
                model, question
            )
            score, reason = evaluate(question, answer)

            model_scores.append(score)
            model_latencies.append(latency_ms)
            model_costs.append(cost)

            print(f"     Score: {score:.2f} | "
                  f"Latency: {latency_ms:.0f}ms | "
                  f"Cost: ${cost:.5f}")
            print(f"     Reason: {reason}")

            _save_log(question, model, usage,
                      latency_ms, cost, score)

        avg_score   = sum(model_scores) / len(model_scores)
        avg_latency = sum(model_latencies) / len(model_latencies)
        avg_cost    = sum(model_costs) / len(model_costs)

        results.append({
            "model":       model,
            "avg_score":   avg_score,
            "avg_latency": avg_latency,
            "avg_cost":    avg_cost,
        })

        print(f"\n  Average — Score: {avg_score:.2f} | "
              f"Latency: {avg_latency:.0f}ms | "
              f"Cost: ${avg_cost:.5f}\n")

    return results


def _save_log(query, model, usage, latency, cost, score):
    try:
        session = Session()
        log = LLMLog(
            user        = "eval_runner",
            query       = query,
            tool_called = "eval",
            model       = model,
            tokens_in   = usage.prompt_tokens,
            tokens_out  = usage.completion_tokens,
            latency_ms  = latency,
            cost_usd    = cost,
            eval_score  = score
        )
        session.add(log)
        session.commit()
        session.close()
    except Exception as e:
        print(f"  ✗ Log failed: {e}")


if __name__ == "__main__":
    run_evals()