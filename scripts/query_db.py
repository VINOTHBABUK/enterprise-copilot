import sqlite3

conn = sqlite3.connect("data/copilot.db")
cursor = conn.cursor()

print("\n=== DOCUMENTS ===")
cursor.execute("""
    SELECT id, title, department, doc_type, summary
    FROM documents
""")
rows = cursor.fetchall()
for row in rows:
    print(f"\nID:         {row[0]}")
    print(f"Title:      {row[1]}")
    print(f"Department: {row[2]}")
    print(f"Doc type:   {row[3]}")
    print(f"Summary:    {row[4][:150]}...")

print("\n=== LLM LOGS ===")
cursor.execute("""
    SELECT id, user, tool_called, model, tokens_in, cost_usd, latency_ms
    FROM llm_logs
""")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"\nID:       {row[0]}")
        print(f"User:     {row[1]}")
        print(f"Tool:     {row[2]}")
        print(f"Model:    {row[3]}")
        print(f"Tokens:   {row[4]}")
        print(f"Cost:     ${row[5]:.5f}")
        print(f"Latency:  {row[6]:.0f}ms")
else:
    print("No logs yet — run router.py first")

conn.close()