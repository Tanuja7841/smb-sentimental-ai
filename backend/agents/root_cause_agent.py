from backend.services.gemini_service import ask_gemini


def analyze_root_cause(customer, sentiment_result):

    prompt = f"""

    You are an enterprise AI observability system.

    Analyze this business situation.

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

    Return response in JSON format.

    """

    return ask_gemini(prompt)