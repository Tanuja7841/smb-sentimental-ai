def generate_alert(result):

    if result["risk_level"] == "High":

        return f"""
        ALERT:
        {result['customer']} is at HIGH churn risk.
        Immediate retention action required.
        """

    return "No urgent alerts."