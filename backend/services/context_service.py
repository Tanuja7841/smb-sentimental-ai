from services.mongodb_memory_service import (
    MongoDBMemoryService
)

memory = MongoDBMemoryService()


def build_customer_context(
    workflow_id,
    customer_id
):

    records = memory.get_customer_context(
        workflow_id,
        customer_id
    )

    context = []

    for record in records:

        context.append(

            f"""
            Agent: {record['agent_name']}
            Finding: {record['finding']}
            """

        )

    return "\n".join(context)