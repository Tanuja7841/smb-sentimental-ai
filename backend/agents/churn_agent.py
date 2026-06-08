from backend.services.gemini_service import ask_gemini
from backend.services.analytics_service import (
    calculate_churn_score,
    classify_risk
)


def analyze_customer(customer, mcp, workflow_id=None, customer_id=None):
    """
    Churn Agent — Predicts customer churn risk.

    Uses MCP client to retrieve context from previous agents
    and historical customer profiles.

    Args:
        customer: Customer data dict
        mcp: MongoMCPClient instance
        workflow_id: Current workflow ID
        customer_id: Customer identifier
    """

    churn_score = calculate_churn_score(customer)
    risk_level = classify_risk(churn_score)

    # Get context from previous agents via MCP
    context_text = ""
    if workflow_id and customer_id:
        context = mcp.get_customer_context(workflow_id, customer_id)
        if isinstance(context, list):
            context_text = "\n".join([
                f"Agent: {item.get('agent_name')}\nFinding: {item.get('finding')}"
                for item in context
            ])

    # Get historical profile via MCP
    profile = mcp.get_customer_profile(customer_id) if customer_id else {}

    prompt = f"""
    You are an elite AI business operations agent.

    Customer Historical Profile:
    {profile}

    Previous Agent Findings:
    {context_text}

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

    if ai_analysis is None:
        ai_analysis = "Gemini unavailable."

    return {
        "customer": customer["name"],
        "churn_score": churn_score,
        "risk_level": risk_level,
        "analysis": ai_analysis
    }
