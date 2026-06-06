def send_recovery_email(customer, recovery_strategy):
    plan = recovery_strategy.get(

        "immediate_recovery_plan",

        "Our team is reviewing your issue."

    )

    retention = recovery_strategy.get(

        "retention_strategy",

        ""

    )
    print("\n=========== EMAIL TOOL ===========\n")

    email = f"""

    TO:
    {customer.get("name")}

    SUBJECT:
    We're Sorry — Let's Fix This

    Dear {customer.get("name")},

    We sincerely apologize for your recent experience.

    Immediate Recovery Plan

    {plan}

    Long-Term Commitment

    {retention}

    Thank you for giving us the opportunity to improve.

    Regards,

    AI Customer Success Team

    """

    print(email)

    return {
        "status": "Email Sent",
        "customer": customer.get("name", "Customer")
    }