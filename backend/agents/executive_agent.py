from backend.services.gemini_service import ask_gemini
import json


def executive_agent(
    customer,
    sentiment_result,
    churn_result,
    root_cause_result,
    recovery_result
):

    prompt = f"""
You are a Chief Customer Officer (CCO).

Create an executive summary for senior leadership.

Customer:
{customer}

Sentiment Analysis:
{sentiment_result}

Churn Analysis:
{churn_result}

Root Cause Analysis:
{root_cause_result}

Recovery Strategy:
{recovery_result}

Return ONLY valid JSON.

{{
    "customer": "",
    "priority": "",
    "overall_status": "",
    "business_risk": "",
    "revenue_at_risk": "",
    "executive_summary": "",
    "recommended_actions": [
        "",
        "",
        ""
    ],
    "executive_owner": "",
    "next_review": ""
}}

Rules:

- Do NOT return markdown.
- Do NOT return explanations.
- Do NOT wrap JSON inside ```json.
- revenue_at_risk should come from customer["total_spent"].
- priority must be one of:
  Critical
  High
  Medium
  Low
"""

    result = ask_gemini(prompt)

    if result is None:

        return {
            "customer": customer["name"],
            "priority": "Critical",
            "overall_status": "High Churn Risk",
            "business_risk": "Customer churn",
            "revenue_at_risk": customer["total_spent"],
            "executive_summary": "Immediate executive intervention required.",
            "recommended_actions": [
                "Contact customer immediately",
                "Assign account manager",
                "Monitor recovery"
            ],
            "executive_owner": "VP Customer Success",
            "next_review": "24 Hours"
        }

    try:

        cleaned = result.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "")
            cleaned = cleaned.replace("```", "")

        return json.loads(cleaned)

    except Exception as e:

        print("Executive Agent JSON Error:", e)
        print(result)

        return {
            "customer": customer["name"],
            "priority": "Critical",
            "overall_status": "High Churn Risk",
            "business_risk": "Customer churn",
            "revenue_at_risk": customer["total_spent"],
            "executive_summary": "Immediate executive intervention required.",
            "recommended_actions": [
                "Contact customer immediately",
                "Assign account manager",
                "Monitor recovery"
            ],
            "executive_owner": "VP Customer Success",
            "next_review": "24 Hours"
        }