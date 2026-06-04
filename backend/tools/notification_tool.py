def notify_executive(customer, risk):

    print("\n=========== EXECUTIVE ALERT ===========\n")

    alert = f"""
    HIGH PRIORITY CUSTOMER ALERT

    Customer:
    {customer['customer_name']}

    Risk Level:
    {risk}

    Executive attention required.
    """

    print(alert)

    return {
        "status": "Executive Alert Sent"
    }