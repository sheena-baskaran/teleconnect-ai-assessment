"""
TeleConnect Agent Evaluation Suite
------------------------------------
Evaluation pipeline for the retention agent including automated metrics
and LLM-as-judge scoring.
"""
import json
import openai
from agent import run_agent

client = openai.OpenAI()

TEST_CASES = [
    {
        "id": "TC-01",
        "category": "happy_path",
        "input": "What's the churn risk for customer TC-001502?",
        "expected_tools": ["lookup_customer", "predict_churn"],
        "expected_output": "should include churn probability and risk tier",
    },
    {
        "id": "TC-02",
        "category": "happy_path",
        "input": "Customer TC-004711 wants to cancel. What can we offer?",
        "expected_tools": ["lookup_customer", "predict_churn", "get_retention_offers"],
        "expected_output": "should include risk assessment and specific offers",
    },
    {
        "id": "TC-03",
        "category": "happy_path",
        "input": "Look up customer TC-003244 and tell me about their account.",
        "expected_tools": ["lookup_customer"],
        "expected_output": "should include customer details",
    },
    {
        "id": "TC-04",
        "category": "happy_path",
        "input": "What retention offers do we have for high-risk month-to-month customers?",
        "expected_tools": ["get_retention_offers"],
        "expected_output": "should list available offers",
    },
    {
        "id": "TC-05",
        "category": "happy_path",
        "input": "Log that I offered TC-001502 a 10% discount and they accepted.",
        "expected_tools": ["log_interaction"],
        "expected_output": "should confirm the interaction was logged",
    },
]


def evaluate_tool_accuracy(test_case: dict, agent_response: str) -> float:
    expected = set(test_case["expected_tools"])
    score = 1.0 if expected else 0.0
    return score


def evaluate_response_completeness(test_case: dict, agent_response: str) -> float:
    keywords = test_case["expected_output"].lower().split()
    matches = sum(1 for kw in keywords if kw in agent_response.lower())
    return matches / len(keywords)


def llm_judge(test_case: dict, agent_response: str) -> dict:
    judge_prompt = f"""You are evaluating an AI retention agent's response. 

Test case input: {test_case['input']}
Expected behavior: {test_case['expected_output']}
Actual response: {agent_response}

Rate the response on these dimensions (1-5 each):
1. Correctness - Is the information accurate?
2. Completeness - Does it cover everything needed?
3. Actionability - Can the rep act on this?
4. Tone - Is it professional and helpful?
5. Hallucination - Any made-up information? (5 = no hallucination, 1 = severe)

Return JSON with scores for each dimension and a brief explanation."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def run_evaluation():
    results = []

    for case in TEST_CASES:
        print(f"Running test case {case['id']}...")
        agent_response = run_agent(case["input"])

        tool_score = evaluate_tool_accuracy(case, agent_response)
        completeness_score = evaluate_response_completeness(case, agent_response)
        judge_scores = llm_judge(case, agent_response)

        results.append({
            "test_id": case["id"],
            "category": case["category"],
            "tool_accuracy": tool_score,
            "completeness": completeness_score,
            "judge_scores": judge_scores,
            "response": agent_response,
        })

    print("\n===== EVALUATION RESULTS =====")
    total_tool = sum(r["tool_accuracy"] for r in results) / len(results)
    total_completeness = sum(r["completeness"] for r in results) / len(results)
    print(f"Tool Accuracy:        {total_tool:.2%}")
    print(f"Response Completeness: {total_completeness:.2%}")

    for r in results:
        print(f"\n--- {r['test_id']} ({r['category']}) ---")
        print(f"Tool: {r['tool_accuracy']:.2f}  Completeness: {r['completeness']:.2f}")
        if "correctness" in r["judge_scores"]:
            print(f"Judge: {r['judge_scores']}")

    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to eval_results.json")


if __name__ == "__main__":
    run_evaluation()
