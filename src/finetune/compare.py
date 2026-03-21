import time
import json
from openai import OpenAI
from src.rag.rag_chain import ask
from src.evals.evaluator import evaluate
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

TEST_QUESTIONS = [
    "What is a leave of absence?",
    "How is earned leave accumulated?",
    "What is incident management?",
    "How do you restore service after an incident?",
    "What is a knowledge base used for?",
]


def run_gpt4o(question):
    start = time.time()
    resp  = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role":    "system",
                "content": "You are a helpful enterprise assistant."
            },
            {
                "role":    "user",
                "content": question
            }
        ]
    )
    latency = (time.time() - start) * 1000
    answer  = resp.choices[0].message.content
    usage   = resp.usage
    cost    = (usage.prompt_tokens / 1000 * 0.005 +
               usage.completion_tokens / 1000 * 0.015)
    return answer, latency, cost


def run_gpt4o_mini(question):
    start = time.time()
    resp  = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":    "system",
                "content": "You are a helpful enterprise assistant."
            },
            {
                "role":    "user",
                "content": question
            }
        ]
    )
    latency = (time.time() - start) * 1000
    answer  = resp.choices[0].message.content
    usage   = resp.usage
    cost    = (usage.prompt_tokens / 1000 * 0.00015 +
               usage.completion_tokens / 1000 * 0.0006)
    return answer, latency, cost


def run_rag(question):
    start  = time.time()
    result = ask(question)
    latency = (time.time() - start) * 1000
    answer  = result["answer"]
    cost    = 0.0001
    return answer, latency, cost


def compare_all():
    print("\nRunning model comparison...\n")

    models = {
        "gpt-4o":      run_gpt4o,
        "gpt-4o-mini": run_gpt4o_mini,
        "rag-pipeline": run_rag,
    }

    results = {m: {"scores": [], "latencies": [], "costs": []}
               for m in models}

    for question in TEST_QUESTIONS:
        print(f"Q: {question[:60]}")
        print("-" * 60)

        for model_name, run_fn in models.items():
            try:
                answer, latency, cost = run_fn(question)
                score, reason         = evaluate(question, answer)

                results[model_name]["scores"].append(score)
                results[model_name]["latencies"].append(latency)
                results[model_name]["costs"].append(cost)

                print(f"  {model_name:<20} "
                      f"score={score:.2f} "
                      f"latency={latency:.0f}ms "
                      f"cost=${cost:.5f}")

            except Exception as e:
                print(f"  {model_name:<20} ✗ {e}")

        print()

    print("\n" + "=" * 65)
    print(f"{'MODEL':<22} {'ACCURACY':>10} {'LATENCY':>12} {'COST/Q':>10}")
    print("=" * 65)

    for model_name, data in results.items():
        if not data["scores"]:
            continue
        avg_score   = sum(data["scores"]) / len(data["scores"])
        avg_latency = sum(data["latencies"]) / len(data["latencies"])
        avg_cost    = sum(data["costs"]) / len(data["costs"])

        print(f"{model_name:<22} "
              f"{avg_score*100:>9.1f}% "
              f"{avg_latency:>10.0f}ms "
              f"${avg_cost:>9.5f}")

    print("=" * 65)

    print("\nKey insight:")
    if "gpt-4o" in results and "gpt-4o-mini" in results:
        c1 = sum(results["gpt-4o"]["costs"]) / len(results["gpt-4o"]["costs"])
        c2 = sum(results["gpt-4o-mini"]["costs"]) / len(results["gpt-4o-mini"]["costs"])
        s1 = sum(results["gpt-4o"]["scores"]) / len(results["gpt-4o"]["scores"])
        s2 = sum(results["gpt-4o-mini"]["scores"]) / len(results["gpt-4o-mini"]["scores"])

        savings      = ((c1 - c2) / c1) * 100
        quality_diff = (s1 - s2) * 100

        print(f"  gpt-4o-mini is {savings:.0f}% cheaper than gpt-4o")
        print(f"  Quality difference: {quality_diff:.1f}%")
        print(f"  RAG pipeline adds citations and grounding")
        print(f"  Recommendation: RAG + gpt-4o-mini for most queries")


if __name__ == "__main__":
    compare_all()