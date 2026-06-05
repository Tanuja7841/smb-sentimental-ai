from backend.services.gemini_service import ask_gemini
import json


def decide_agents(

    customer_data,
    sentiment_result

):

    prompt = f"""
    You are an AI Workflow Supervisor.

    Customer:
    {customer_data}

    Sentiment Analysis:
    {sentiment_result}

    Decide which agents should run.

    Available Agents:

    1. churn_agent
       -> customer retention risk

    2. root_cause_agent
       -> investigate issue

    3. recovery_agent
       -> create recovery plan

    4. executive_agent
       -> executive escalation

    Return ONLY JSON:

    {{
      "agents": [
        "churn_agent",
        "root_cause_agent"
      ]
    }}
    """

    result = ask_gemini(prompt)

    try:

        cleaned = result.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            )

        return json.loads(cleaned)

    except:

        return {
            "agents": [
                "churn_agent",
                "root_cause_agent",
                "recovery_agent",
                "executive_agent"
            ]
        }