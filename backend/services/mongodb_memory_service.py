from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi 

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(
        mongo_uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )

db = client["smb_sentinel"]

memory_collection = db["agent_memory"]


def add_memory(
    agent,
    customer,
    event,
    severity,
    metadata=None
):

    memory_collection.insert_one({

        "timestamp": datetime.utcnow(),

        "agent": agent,

        "customer": customer,

        "event": event,

        "severity": severity,

        "metadata": metadata or {}

    })


def load_memory():

    return list(
        memory_collection.find(
            {},
            {"_id": 0}
        )
    )


def get_customer_memory(customer):

    return list(
        memory_collection.find(
            {"customer": customer},
            {"_id": 0}
        )
    )