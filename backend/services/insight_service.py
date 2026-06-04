import json

from backend.services.gemini_service import ask_gemini


INSIGHT_FILE = "backend/data/latest_insight.json"


def generate_executive_insight(metrics):

    prompt = f"""

    You are an AI business strategist.

    Analyze these business metrics:

    Total Customers: {metrics['total_customers']}
    High Risk Customers: {metrics['high_risk_customers']}
    Revenue At Risk: {metrics['revenue_at_risk']}
    Business Health Score: {metrics['business_health_score']}
    Escalations: {metrics['total_escalations']}

    Generate:
    - executive summary
    - operational issue
    - business risk
    - recommended action

    """

    insight = ask_gemini(prompt)

    with open(INSIGHT_FILE, "w") as file:

        json.dump(
            {"insight": insight},
            file,
            indent=4
        )

    return insight


def load_latest_insight():

    with open(INSIGHT_FILE, "r") as file:

        data = json.load(file)

    return data["insight"]