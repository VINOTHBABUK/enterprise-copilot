from src.ingestion.database import Session, LLMLog
from dotenv import load_dotenv

load_dotenv()


def print_dashboard():
    session = Session()

    logs = session.query(LLMLog)\
                  .filter(LLMLog.tool_called == "eval")\
                  .all()

    session.close()

    if not logs:
        print("No eval results yet. Run runner.py first.")
        return

    models = {}
    for log in logs:
        m = log.model
        if m not in models:
            models[m] = {
                "scores":    [],
                "latencies": [],
                "costs":     []
            }
        if log.eval_score is not None:
            models[m]["scores"].append(log.eval_score)
        if log.latency_ms is not None:
            models[m]["latencies"].append(log.latency_ms)
        if log.cost_usd is not None:
            models[m]["costs"].append(log.cost_usd)

    print("\n" + "=" * 65)
    print(f"{'MODEL':<20} {'ACCURACY':>10} {'LATENCY':>12} {'COST/Q':>10}")
    print("=" * 65)

    for model, data in models.items():
        avg_score   = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        avg_latency = sum(data["latencies"]) / len(data["latencies"]) if data["latencies"] else 0
        avg_cost    = sum(data["costs"]) / len(data["costs"]) if data["costs"] else 0

        print(f"{model:<20} "
              f"{avg_score*100:>9.1f}% "
              f"{avg_latency:>10.0f}ms "
              f"${avg_cost:>9.5f}")

    print("=" * 65)
    print("\nInsight:")

    if len(models) >= 2:
        model_list = list(models.items())
        m1_name, m1 = model_list[0]
        m2_name, m2 = model_list[1]

        s1 = sum(m1["scores"]) / len(m1["scores"]) if m1["scores"] else 0
        s2 = sum(m2["scores"]) / len(m2["scores"]) if m2["scores"] else 0
        c1 = sum(m1["costs"]) / len(m1["costs"]) if m1["costs"] else 0
        c2 = sum(m2["costs"]) / len(m2["costs"]) if m2["costs"] else 0

        if c2 > 0:
            savings = ((c1 - c2) / c1) * 100
            quality_diff = (s1 - s2) * 100
            print(f"  {m2_name} is {savings:.0f}% cheaper than {m1_name}")
            print(f"  Quality difference: {quality_diff:.1f}%")

            if quality_diff < 15:
                print(f"  Recommendation: Use {m2_name} for routine queries")
                print(f"  and {m1_name} only for complex synthesis tasks")


if __name__ == "__main__":
    print_dashboard()