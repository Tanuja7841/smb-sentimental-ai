from backend.services.gemini_service import ask_gemini


def generate_executive_brief(

    customer,
    sentiment,
    churn,
    root_cause,
    recovery

):

    prompt = f"""

    You are a Chief AI Operations Officer.

    Generate an executive escalation brief.

    Customer:
    {customer}

    Sentiment:
    {sentiment}

    Churn:
    {churn}

    Root Cause:
    {root_cause}

    Recovery Strategy:
    {recovery}

    Generate:

    1. Executive summary
    2. Financial risk
    3. Operational concern
    4. Leadership recommendation

    """

    return ask_gemini(prompt)