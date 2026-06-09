def calculate_churn_score(customer):

    score = 0

    # Purchase/visit inactivity (supports both old and new data formats)
    inactivity = customer.get("last_purchase_days", customer.get("last_visit_days", 0))
    if inactivity > 40:
        score += 40
    elif inactivity > 20:
        score += 20

    # Sentiment
    if customer.get("sentiment") == "negative":
        score += 35

    # Response delay
    if customer.get("response_delay_days", 0) > 10:
        score += 25

    return min(score, 100)


def classify_risk(score):

    if score >= 70:
        return "High"

    elif score >= 40:
        return "Medium"

    return "Low"

def business_priority(customer, churn_score):

    if customer.get("total_spent", 0) > 30000 and churn_score > 50:
        return "Critical"

    elif churn_score > 70:
        return "High"

    return "Normal"

def sentiment_score(message):

    negative_words = [
        "bad",
        "slow",
        "worst",
        "angry",
        "delay",
        "issue",
        "problem",
        "refund",
        "late",
        "terrible"
    ]

    score = 0

    lower_message = message.lower()

    for word in negative_words:

        if word in lower_message:
            score += 15

    return min(score, 100)


def classify_sentiment_risk(score):

    if score >= 60:
        return "High"

    elif score >= 30:
        return "Medium"

    return "Low"
