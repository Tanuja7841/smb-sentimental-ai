from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import certifi
import os

load_dotenv()

class MongoDBMemoryService:

    def __init__(self):

        mongo_uri = os.getenv("MONGO_URI")

        self.client = MongoClient(
            mongo_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )

        self.db = self.client["smb_sentinel"]

        self.memory_collection = self.db["agent_memory"]

        self.workflow_collection = self.db["workflows"]

        self.task_collection = self.db["agent_tasks"]

        self.message_collection = self.db["agent_messages"]

        self.customer_profile_collection = (
            self.db["customer_profiles"]
        )

    def save_workflow(
        self,
        workflow_id,
        customer_id
    ):

        self.workflow_collection.insert_one({

            "workflow_id": workflow_id,
            "customer_id": customer_id,
            "status": "active",
            "created_at": datetime.utcnow()

        })

    def save_agent_memory(
        self,
        workflow_id,
        customer_id,
        agent_name,
        finding
    ):

        self.memory_collection.insert_one({

            "workflow_id": workflow_id,
            "customer_id": customer_id,
            "agent_name": agent_name,
            "finding": finding,
            "timestamp": datetime.utcnow()

        })

    def get_customer_context(
        self,
        workflow_id,
        customer_id
    ):

        return list(

            self.memory_collection.find(

                {
                    "workflow_id": workflow_id,
                    "customer_id": customer_id
                },

                {"_id": 0}

            ).sort("timestamp", 1)

        )
    
    def load_memory(self):
        return list(
            self.memory_collection.find(
                {},
                {"_id": 0}
            )
        )
    
    def get_customer_memory(
        self,
        customer_id
    ):

        return list(

            self.memory_collection.find(

                {
                    "customer_id": customer_id
                },

                {"_id": 0}

            )

        )
    
    def create_task(
        self,
        workflow_id,
        assigned_agent,
        task_type,
        task_details
        ):

        self.task_collection.insert_one({

            "workflow_id": workflow_id,
            "assigned_agent": assigned_agent,
            "task_type": task_type,
            "task_details": task_details,
            "status": "pending",
            "created_at": datetime.utcnow()

        })
    
    def get_tasks_for_agent(
        self,
        workflow_id,
        agent_name
    ):

        return list(
            self.task_collection.find(
                {
                    "workflow_id": workflow_id,
                    "assigned_agent": agent_name,
                    "status": "pending"
                },
                {"_id": 0}
            )
        )
    
    def complete_task(
            self,
            task_id
        ):

            self.task_collection.update_one(

                {"_id": task_id},

                {
                    "$set": {
                        "status": "completed"
                    }
                },
        {"_id": 0}
    )

    def get_workflows(self):
        return list(

            self.workflow_collection.find(
                {},
                {"_id": 0}
            ).sort(
                "created_at",
                -1
            )

        )
    
    def get_agent_tasks(self):
        return list(

            self.task_collection.find(
                {},
                {"_id": 0}
            ).sort(
                "created_at",
                -1
            )

        )
    
    def save_supervisor_decision(
        self,
        workflow_id,
        customer_id,
        selected_agents
    ):

        self.memory_collection.insert_one({

            "workflow_id": workflow_id,
            "customer_id": customer_id,
            "agent_name": "supervisor_agent",
            "finding": {
                "selected_agents": selected_agents
            },
            "timestamp": datetime.utcnow()

        })

    def send_agent_message(
        self,
        workflow_id,
        from_agent,
        to_agent,
        message
    ):

        self.message_collection.insert_one({

            "workflow_id": workflow_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message": message,
            "created_at": datetime.utcnow()

        })

    def get_agent_messages(
        self,
        workflow_id,
        agent_name
    ):

        return list(

            self.message_collection.find({

                "workflow_id": workflow_id,
                "to_agent": agent_name

            })

        )
    def upsert_customer_profile(
        self,
        customer_id,
        customer_name,
        churn_score=None,
        risk_level=None,
        root_cause=None,
        recovery_strategy=None
    ):

        self.customer_profile_collection.update_one(

            {
                "customer_id": customer_id
            },

            {
                "$set": {

                    "customer_name": customer_name,

                    "last_churn_score": churn_score,

                    "last_risk_level": risk_level,

                    "last_root_cause": root_cause,

                    "last_recovery_strategy":
                        recovery_strategy,

                    "updated_at":
                        datetime.utcnow()
                },

                "$inc": {
                    "incident_count": 1
                }
            },

            upsert=True

        )

    def get_customer_profile(
        self,
        customer_id
    ):

        return self.customer_profile_collection.find_one(

            {
                "customer_id": customer_id
            },

            {
                "_id": 0
            }

        )
    
    def get_workflow_timeline(
        self,
        workflow_id
    ):

        return list(

            self.memory_collection.find(
                {
                    "workflow_id": workflow_id
                },
                {"_id": 0}
            ).sort(
                "timestamp",
                1
            )

        )
    def get_workflow_tasks(
        self,
        workflow_id
    ):

        return list(

            self.task_collection.find(
                {
                    "workflow_id": workflow_id
                },
                {"_id": 0}
            )

        )
    
    def complete_workflow(
            self,
            workflow_id
        ):

            self.workflow_collection.update_one(

                {
                    "workflow_id": workflow_id
                },

                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow()
                    }
                }

            )