import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

JUDGE_PROMPT = """You are an expert evaluator assessing the quality of AI responses.

Given a question and an AI response, score the response from 0 to 1.

Scoring criteria:
- 1.0  Perfect — accurate, complete, clear
- 0.8  Good — mostly accurate, minor gaps
- 0.6  Acceptable — partially correct
- 0.4  Poor — mostly wrong or incomplete
- 0.2  Bad — largely incorrect
- 0.0  Completely wrong or no answer

Return ONLY valid JSON:
{
  "score": 0.0,
  "reason": "one sentence explanation"
}

Question: {question}
AI Response: {response}
"""


def evaluate(question, response):
    try:
        prompt = JUDGE_PROMPT.replace(
            "{question}", question
        ).replace(
            "{response}", response
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(resp.choices[0].message.content)
        score  = float(result.get("score", 0))
        reason = result.get("reason", "")
        return score, reason

    except Exception as e:
        print(f"  ✗ Evaluation failed: {e}")
        return 0.0, "evaluation failed"


if __name__ == "__main__":
    question = "What is incident management?"
    response = "Incident management is the process of identifying, analysing, and resolving incidents to restore normal service operations as quickly as possible."

    score, reason = evaluate(question, response)
    print(f"Score:  {score}")
    print(f"Reason: {reason}")