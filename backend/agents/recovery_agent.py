from backend.services.gemini_service import ask_gemini


def generate_recovery_strategy(

    customer,
    churn_analysis,
    root_cause

):

    prompt = f"""

    You are an AI customer recovery strategist.

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