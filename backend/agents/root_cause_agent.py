import json

from backend.services.gemini_service import ask_gemini
from backend.services.mongodb_memory_service import MongoDBMemoryService

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

        context_text = "\n\n".join(
            [
                f"Agent: {item.get('agent_name')}\nFinding: {item.get('finding')}"
                for item in context
            ]
        )

    prompt = f"""
You are an enterprise AI observability system.

Previous Agent Findings:
{context_text}

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

Return ONLY valid JSON.

Example:

{{
    "root_cause_category":"Support Delay",
    "operational_issue":"Slow support response",
    "business_impact":"Customer dissatisfaction",
    "severity":"High",
    "recommended_fix":"Assign senior support engineer"
}}
"""

    result = ask_gemini(prompt)

    if not result or result.startswith("Gemini Error"):
        return {
            "root_cause_category": "Unknown",
            "operational_issue": "Gemini unavailable",
            "business_impact": "Unknown",
            "severity": "Unknown",
            "recommended_fix": "Retry later"
        }

    try:

        cleaned = result.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        return json.loads(cleaned)

    except Exception:

        return {
            "root_cause_category": "Unknown",
            "operational_issue": result,
            "business_impact": "Unknown",
            "severity": "Unknown",
            "recommended_fix": "Manual review required"
        }