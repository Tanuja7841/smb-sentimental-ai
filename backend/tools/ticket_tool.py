import uuid


def create_escalation_ticket(customer, issue):

    ticket_id = str(uuid.uuid4())[:8]

    print("\n=========== TICKET CREATED ===========\n")

    print(f"""
    Ticket ID: {ticket_id}
    Customer: {customer.get('name', 'Customer')}
    Issue: {issue}
    Priority: Critical
    """)

    return {
        "ticket_id": ticket_id,
        "status": "Created"
    }