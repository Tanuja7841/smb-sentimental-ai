from services.gemini_service import ask_gemini
from services.mongodb_memory_service import (
    MongoDBMemoryService
)

memory = MongoDBMemoryService()


def generate_executive_brief(

    customer,
    sentiment,
    churn,
    root_cause,
    recovery,
    workflow_id=None,
    customer_id=None

):

    context_text = ""

    if workflow_id and customer_id:

        context = memory.get_customer_context(
            workflow_id,
            customer_id
        )

        context_text = "\n".join([
            f"Agent: {item['agent_name']}\nFinding: {item['finding']}"
            for item in context
        ])

    print("\n===== EXECUTIVE AGENT CONTEXT =====")
    print(context_text)

    prompt = f"""

    You are a Chief AI Operations Officer.

    Previous Agent Findings:

    {context_text}

    Customer:
    {customer}

    Sentiment:
    {sentiment}

    Churn:
    {churn}

    Root Cause:
    {root_cause}

    Recovery Strategy:
    {recovery}

    Generate:

    1. Executive Summary
    2. Financial Risk
    3. Operational Concern
    4. Leadership Recommendation
    5. Revenue Protection Plan

    Keep the response executive-level and concise.

    """

    return ask_gemini(prompt)