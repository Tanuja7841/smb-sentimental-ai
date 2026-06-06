from backend.services.gemini_service import ask_gemini
import json


def decide_agents(customer_data, sentiment_result):
    """
    Supervisor Agent

    Uses:
    1. Gemini for intelligent workflow routing
    2. Business rules to guarantee critical agents execute
    """

    prompt = f"""
You are the Supervisor Agent of an enterprise multi-agent AI platform.

Your job is to decide which downstream AI agents should execute.

Customer Data:
{customer_data}

Sentiment Analysis:
{sentiment_result}

Available Agents

1. churn_agent
- Predict customer churn risk.

2. root_cause_agent
- Identify operational or business issues.

3. recovery_agent
- Create customer recovery strategy.

4. executive_agent
- Generate executive recommendations and revenue protection strategy.

Decision Rules:

• churn_agent should ALWAYS run.

• root_cause_agent should ALWAYS run.

• recovery_agent should run if:
    - Sentiment is Negative
    - Urgency is High
    - Frustration is High
    - Business Risk is High
    - Churn Risk is High
    - Customer spending exceeds $10,000

• executive_agent should run if:
    - Revenue at risk exceeds $10,000
    - Severity is High
    - Customer is strategic
    - Executive escalation is needed
    - Churn Risk is High

Return ONLY valid JSON.

Example:

{{
    "agents":[
        "churn_agent",
        "root_cause_agent",
        "recovery_agent",
        "executive_agent"
    ]
}}
"""

    default_agents = {
        "churn_agent",
        "root_cause_agent"
    }

    try:

        result = ask_gemini(prompt)

        if result:

            cleaned = result.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").replace("```", "")

            llm_response = json.loads(cleaned)

            agents = set(llm_response.get("agents", []))

        else:
            agents = set()

    except Exception:

        agents = set()

    # --------------------------------------------------
    # Mandatory Agents
    # --------------------------------------------------

    agents.update(default_agents)

    # --------------------------------------------------
    # Deterministic Business Rules
    # --------------------------------------------------

    sentiment = str(
        sentiment_result.get("sentiment", "")
    ).lower()

    urgency = str(
        sentiment_result.get("urgency", "")
    ).lower()

    frustration = str(
        sentiment_result.get("frustration_level", "")
    ).lower()

    business_risk = str(
        sentiment_result.get("business_risk", "")
    ).lower()

    total_spent = customer_data.get(
        "total_spent",
        0
    )

    churn_score = customer_data.get(
        "churn_score",
        0
    )

    if (
        sentiment == "negative"
        or urgency == "high"
        or frustration == "high"
        or "high" in business_risk
        or churn_score >= 50
        or total_spent >= 10000
    ):
        agents.add("recovery_agent")

    if (
        total_spent >= 10000
        or churn_score >= 70
        or "high" in business_risk
    ):
        agents.add("executive_agent")

    # --------------------------------------------------
    # Priority Order
    # --------------------------------------------------

    ordered_agents = [
        agent
        for agent in [
            "churn_agent",
            "root_cause_agent",
            "recovery_agent",
            "executive_agent"
        ]
        if agent in agents
    ]

    return {
        "agents": ordered_agents
    }