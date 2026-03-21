from src.ingestion.database import Session, LLMLog
from dotenv import load_dotenv

load_dotenv()


def get_usage_stats():
    session = Session()
    logs    = session.query(LLMLog).all()
    session.close()

    if not logs:
        return {
            "total_queries":   0,
            "total_cost":      0,
            "avg_latency":     0,
            "avg_score":       0,
            "by_model":        {},
            "by_tool":         {},
            "by_user":         {},
        }

    total_queries = len(logs)
    total_cost    = sum(l.cost_usd or 0 for l in logs)
    avg_latency   = sum(l.latency_ms or 0 for l in logs) / total_queries
    scores        = [l.eval_score for l in logs if l.eval_score]
    avg_score     = sum(scores) / len(scores) if scores else 0

    by_model = {}
    for log in logs:
        m = log.model or "unknown"
        if m not in by_model:
            by_model[m] = {
                "count":   0,
                "cost":    0,
                "latency": []
            }
        by_model[m]["count"]  += 1
        by_model[m]["cost"]   += log.cost_usd or 0
        by_model[m]["latency"].append(log.latency_ms or 0)

    for m in by_model:
        lats = by_model[m]["latency"]
        by_model[m]["avg_latency"] = sum(lats) / len(lats)
        del by_model[m]["latency"]

    by_tool = {}
    for log in logs:
        t = log.tool_called or "unknown"
        if t not in by_tool:
            by_tool[t] = {"count": 0, "cost": 0}
        by_tool[t]["count"] += 1
        by_tool[t]["cost"]  += log.cost_usd or 0

    by_user = {}
    for log in logs:
        u = log.user or "unknown"
        if u not in by_user:
            by_user[u] = {"count": 0, "cost": 0}
        by_user[u]["count"] += 1
        by_user[u]["cost"]  += log.cost_usd or 0

    return {
        "total_queries": total_queries,
        "total_cost":    round(total_cost, 5),
        "avg_latency":   round(avg_latency, 0),
        "avg_score":     round(avg_score, 2),
        "by_model":      by_model,
        "by_tool":       by_tool,
        "by_user":       by_user,
    }


def print_dashboard():
    stats = get_usage_stats()

    print("\n" + "=" * 60)
    print("ENTERPRISE COPILOT — OBSERVABILITY DASHBOARD")
    print("=" * 60)

    print(f"\nTotal queries:   {stats['total_queries']}")
    print(f"Total cost:      ${stats['total_cost']:.5f}")
    print(f"Avg latency:     {stats['avg_latency']:.0f}ms")
    print(f"Avg eval score:  {stats['avg_score']:.2f}")

    print("\n--- By Model ---")
    for model, data in stats["by_model"].items():
        print(f"  {model:<20} "
              f"queries={data['count']:>4} "
              f"cost=${data['cost']:.5f} "
              f"latency={data['avg_latency']:.0f}ms")

    print("\n--- By Tool ---")
    for tool, data in stats["by_tool"].items():
        print(f"  {tool:<25} "
              f"queries={data['count']:>4} "
              f"cost=${data['cost']:.5f}")

    print("\n--- By User ---")
    for user, data in stats["by_user"].items():
        print(f"  {user:<20} "
              f"queries={data['count']:>4} "
              f"cost=${data['cost']:.5f}")

    print("=" * 60)


if __name__ == "__main__":
    print_dashboard()