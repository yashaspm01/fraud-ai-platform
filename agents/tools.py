from services.risk_service import score_transaction
from rag.generate_answer import generate_answer
from agents.approval import request_case_closure


TOOLS = [
    {
        "name": "get_risk_score",
        "description": "Get the fraud risk score for a transaction. Use this when you need to know how risky a specific transaction is.",
        "parameters": {
            "amount": "number - transaction amount",
            "sender_balance_before": "number - sender's balance before the transaction",
            "sender_balance_after": "number - sender's balance after the transaction",
            "hour_of_day": "integer 0-23 - hour the transaction occurred",
        },
    },
    {
        "name": "search_policy",
        "description": "Search compliance/policy documents for guidance on procedures, requirements, and definitions found in the BSA/AML manual. Best for questions about what examiners/analysts should DO in a situation, not for statistical thresholds or numeric cutoffs, which this tool does not contain.",
        "parameters": {
            "question": "string - a policy/procedure question, e.g. 'what should be done when a transaction is flagged as high risk'",
        },
    },
]

TOOLS.append({
    "name": "recommend_case_closure",
    "description": "Recommend that a fraud case be closed, with your reasoning. This does NOT close the case — it only submits a recommendation for human approval.",
    "parameters": {
        "transaction_id": "string - UUID of the transaction",
        "recommendation": "string - your reasoning for why this case should be closed",
    },
})


def call_tool(tool_name: str, arguments: dict):
    if tool_name == "get_risk_score":
        return score_transaction(arguments)

    if tool_name == "search_policy":
        answer, sources = generate_answer(arguments["question"])
        return {"answer": answer, "sources": [s.chunk_index for s in sources]}

    if tool_name == "recommend_case_closure":
        return request_case_closure(arguments["transaction_id"], arguments["recommendation"])

    raise ValueError(f"Unknown tool: {tool_name}")
