from services.gemini_service import ask_gemini
from services.mongodb_memory_service import (
    MongoDBMemoryService
)

memory = MongoDBMemoryService()


def analyze_root_cause(
    customer,
    sentiment_result,
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

    You are an enterprise AI observability system.

    Previous Agent Findings:

    {context_text}

    Analyze this business situation.

    Customer:
    {customer}

    Sentiment Analysis:
    {sentiment_result}

    Identify:

    1. Root cause category
    2. Operational issue
    3. Business impact
    4. Severity
    5. Recommended fix

    Possible root causes:
    - Support Delay
    - Pricing Issue
    - Product Quality
    - Delivery Failure
    - Poor Engagement
    - Technical Problem

    Return response in JSON format.

    """

    return ask_gemini(prompt)