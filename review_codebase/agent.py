"""
TeleConnect Retention Agent
----------------------------
Agent that helps retention reps handle at-risk customers using tool calling.
"""
import json
import openai
from tools import lookup_customer, predict_churn, get_retention_offers, log_interaction

client = openai.OpenAI()

SYSTEM_PROMPT = """You are a helpful retention agent for TeleConnect. You help customer 
retention representatives handle at-risk customers. You have access to tools for looking 
up customers, predicting churn, finding retention offers, and logging interactions.

Be helpful and provide actionable recommendations to the rep. If a customer is at risk 
of churning, suggest appropriate retention offers. Always be professional.

If something seems wrong, escalate to a supervisor."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Look up a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"}
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "predict_churn",
            "description": "Predict churn for a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_data": {"type": "object"}
                },
                "required": ["customer_data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_retention_offers",
            "description": "Get offers for a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_tier": {"type": "string"},
                    "contract_type": {"type": "string"},
                },
                "required": ["risk_tier"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_interaction",
            "description": "Log an interaction",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "offer_made": {"type": "string"},
                    "outcome": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["customer_id"],
            },
        },
    },
]

conversation_history = []


def execute_tool(name: str, arguments: dict):
    if name == "lookup_customer":
        return lookup_customer(**arguments)
    elif name == "predict_churn":
        return predict_churn(**arguments)
    elif name == "get_retention_offers":
        return get_retention_offers(**arguments)
    elif name == "log_interaction":
        return log_interaction(**arguments)


def run_agent(user_message: str) -> str:
    conversation_history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS,
        temperature=0.7,
    )

    assistant_message = response.choices[0].message

    while assistant_message.tool_calls:
        conversation_history.append(assistant_message.model_dump())

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = execute_tool(function_name, arguments)

            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            tools=TOOLS,
            temperature=0.7,
        )
        assistant_message = response.choices[0].message

    conversation_history.append({"role": "assistant", "content": assistant_message.content})
    return assistant_message.content


if __name__ == "__main__":
    while True:
        user_input = input("\nRep > ")
        if user_input.lower() in ("quit", "exit"):
            break
        response = run_agent(user_input)
        print(f"\nAgent > {response}")
