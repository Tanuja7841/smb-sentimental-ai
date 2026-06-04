def send_recovery_email(customer, recovery_strategy):

    print("\n=========== EMAIL TOOL ===========\n")

    email = f"""

    TO: {customer['customer_name']}

    SUBJECT: We're Sorry — Let's Fix This

    Dear {customer['customer_name']},

    We noticed your recent experience was not ideal.

    Our AI operations team has reviewed the issue.

    Recovery Plan:
    {recovery_strategy}

    We value your business deeply.

    Regards,
    AI SMB Survival Team

    """

    print(email)

    return {
        "status": "Email Sent",
        "customer": customer["customer_name"]
    }