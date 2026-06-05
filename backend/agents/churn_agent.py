from services.gemini_service import ask_gemini
from services.analytics_service import (
    calculate_churn_score,
    classify_risk
)
from services.mongodb_memory_service import (
    MongoDBMemoryService
)

memory = MongoDBMemoryService()


def analyze_customer(
    customer,
    workflow_id=None,
    customer_id=None
    ):

    churn_score = calculate_churn_score(customer)

    risk_level = classify_risk(churn_score)
    context = []

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
    
    profile = memory.get_customer_profile(
        customer_id
    )

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

    return {
        "customer": customer["name"],
        "churn_score": churn_score,
        "risk_level": risk_level,
        "analysis": ai_analysis
    }