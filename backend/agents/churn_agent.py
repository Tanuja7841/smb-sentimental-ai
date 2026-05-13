from services.gemini_service import ask_gemini

def analyze_customer(customer):

    prompt = f"""
    Analyze this customer for churn risk.

    Customer Data:
    Name: {customer['name']}
    Last Purchase Days: {customer['last_purchase_days']}
    Sentiment: {customer['sentiment']}
    Response Delay Days: {customer['response_delay_days']}

    Return:
    1. Churn Risk (Low/Medium/High)
    2. Explanation
    3. Recommended Action
    """

    response = ask_gemini(prompt)

    return response