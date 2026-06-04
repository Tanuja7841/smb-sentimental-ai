def create_followup_task(customer):

    print("\n=========== CRM TASK CREATED ===========\n")

    task = f"""
    Follow up with {customer['customer_name']}
    within 24 hours.
    """

    print(task)

    return {
        "task": task,
        "status": "Scheduled"
    }