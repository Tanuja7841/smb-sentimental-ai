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
