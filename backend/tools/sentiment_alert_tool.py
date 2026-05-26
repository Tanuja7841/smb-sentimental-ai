def generate_sentiment_alert(customer, risk_level):

    if risk_level == "High":

        return f"""
        SENTIMENT ALERT:
        Customer {customer} shows HIGH frustration level.
        Immediate escalation recommended.
        """

    elif risk_level == "Medium":

        return f"""
        WARNING:
        Customer {customer} shows moderate dissatisfaction.
        Monitor closely.
        """

    return "No major sentiment risks detected."