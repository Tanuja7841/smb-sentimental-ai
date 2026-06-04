from services.gemini_service import ask_gemini
from services.mongodb_memory_service import (
    MongoDBMemoryService
)

memory = MongoDBMemoryService()


def generate_recovery_strategy(

    customer,
    churn_analysis,
    root_cause,
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

    prompt = f"""

    You are an AI customer recovery strategist.

    Previous Agent Findings:

    {context_text}

    Customer:
    {customer}

    Churn Analysis:
    {churn_analysis}

    Root Cause:
    {root_cause}

    Generate:

    1. Immediate recovery plan
    2. Retention strategy
    3. Executive recommendation
    4. Revenue protection action

    Keep concise and strategic.

    """

    return ask_gemini(prompt)