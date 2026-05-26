def calculate_churn_score(customer):

    score = 0

    # Purchase inactivity
    if customer["last_purchase_days"] > 40:
        score += 40
    elif customer["last_purchase_days"] > 20:
        score += 20

    # Sentiment
    if customer["sentiment"] == "negative":
        score += 35

    # Response delay
    if customer["response_delay_days"] > 10:
        score += 25

    return min(score, 100)


def classify_risk(score):

    if score >= 70:
        return "High"

    elif score >= 40:
        return "Medium"

    return "Low"

def business_priority(customer, churn_score):

    if customer["total_spent"] > 30000 and churn_score > 50:
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