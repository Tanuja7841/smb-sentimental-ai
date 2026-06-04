class MongoMemoryService:

    def get_customer_context(
        workflow_id,
        customer_id
        ):
            
            return list(
                agent_memory.find(
                    {
                    "workflow_id": workflow_id,
                    "customer_id": customer_id
                    }
                )
            )

    def save_agent_memory(
        workflow_id,
        customer_id,
        agent_name,
        finding
    ):
        
        agent_memory.insert_one({
            "workflow_id": workflow_id,
            "customer_id": customer_id,
            "agent_name": agent_name,
            "finding": finding,
            "timestamp": datetime.utcnow()
        })

    def save_task(self):
        pass

    def get_pending_tasks(self):
        pass

    def save_agent_message(self):
        pass

    def get_agent_messages(self):
        pass

    def save_workflow(
        workflow_id,
        customer_id
    ):
        
        workflows.insert_one({
            "workflow_id": workflow_id,
            "customer_id": customer_id,
            "status": "active"
        })
