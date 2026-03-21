from src.agents.supervisor import plan
from src.agents.specialists import (
    fetch_meetings,
    fetch_documents,
    extract_risks,
    search_knowledge,
    generate_report
)
from dotenv import load_dotenv

load_dotenv()

TOOL_MAP = {
    "fetch_meetings":   fetch_meetings,
    "fetch_documents":  fetch_documents,
    "extract_risks":    extract_risks,
    "search_knowledge": search_knowledge,
    "generate_report":  generate_report,
}


def run_workflow(user_request):
    print(f"\nRequest: {user_request}")
    print("=" * 60)

    print("\nSupervisor planning...")
    supervisor_plan = plan(user_request)
    print(f"Goal: {supervisor_plan['final_goal']}")
    print(f"Steps: {len(supervisor_plan['plan'])}")

    context = {
        "request":  user_request,
        "meetings": [],
        "documents": [],
        "risks":    [],
        "knowledge": [],
        "report":   ""
    }

    for step in supervisor_plan["plan"]:
        if "tool" not in step:
            print(f"  ✗ Step missing tool key: {step}")
            continue
        
        tool_name = step["tool"]
        reason    = step["reason"]

        print(f"\nStep {step['step']}: {tool_name}")
        print(f"  Reason: {reason[:80]}...")

        if tool_name not in TOOL_MAP:
            print(f"  ✗ Unknown tool: {tool_name}")
            continue

        tool = TOOL_MAP[tool_name]

        try:
            if tool_name == "fetch_meetings":
                result = tool()
                context["meetings"] = result
                print(f"  ✓ Fetched {len(result)} meetings")

            elif tool_name == "fetch_documents":
                result = tool()
                context["documents"] = result
                print(f"  ✓ Fetched {len(result)} documents")

            elif tool_name == "extract_risks":
                result = tool(context["meetings"])
                context["risks"] = result
                print(f"  ✓ Extracted {len(result)} risks")

            elif tool_name == "search_knowledge":
                result = tool(user_request)
                context["knowledge"].append(result)
                print(f"  ✓ Knowledge search complete")

            elif tool_name == "generate_report":
                report_data = {
                    "meetings":  context["meetings"],
                    "documents": context["documents"],
                    "risks":     context["risks"],
                    "knowledge": context["knowledge"],
                    "request":   user_request
                }
                result = tool(report_data)
                context["report"] = result
                print(f"  ✓ Report generated")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)

    if context["report"]:
        print(context["report"])
    else:
        print("Generating final summary...")
        report_data = {
            "meetings":  context["meetings"],
            "documents": context["documents"],
            "risks":     context["risks"],
            "request":   user_request
        }
        print(generate_report(report_data))

    return context


if __name__ == "__main__":
    requests = [
        "Give me all risks and blockers from this week's meetings",
        "Summarise all meetings and list all action items",
    ]

    for req in requests:
        run_workflow(req)
        print("\n" + "=" * 60 + "\n")