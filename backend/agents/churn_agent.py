from backend.services.gemini_service import ask_gemini
from backend.services.analytics_service import (
    calculate_churn_score,
    classify_risk
)


def analyze_customer(customer):

    churn_score = calculate_churn_score(customer)

    risk_level = classify_risk(churn_score)

    prompt = f"""
    You are an elite AI business operations agent.

    Analyze this customer.

    Customer:
    {customer}

    Churn Score:
    {churn_score}/100

    Risk Level:
    {risk_level}

    Tasks:
    1. Explain WHY customer may churn
    2. Explain urgency
    3. Recommend immediate actions
    4. Suggest long-term retention strategy
    5. Explain business impact

    Keep response concise but executive-level.
    """

    ai_analysis = ask_gemini(prompt)

    return {
        "customer": customer["name"],
        "churn_score": churn_score,
        "risk_level": risk_level,
        "analysis": ai_analysis
    }