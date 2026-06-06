from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi 

from backend.services.mongodb_memory_service import (
    MongoDBMemoryService
)

memory = MongoDBMemoryService()
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

print("URI Loaded:", mongo_uri[:30] + "...")

try:
    client = MongoClient(
        mongo_uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )

    db = client["smb_sentinel"]
    client.admin.command(
        "ping"
    )

    print(
        "MongoDB Connected"
    )
    print("Collections:")
    print(db.list_collection_names())
    print("✅ MongoDB Connected Successfully!")
    print(memory.db.tasks.count_documents({}))
    print(memory.db.agent_messages.count_documents({}))
    print(memory.db.customer_profiles.count_documents({}))
    # print(memory.db.list_collection_names())
    # for x in memory.memory_collection.find():
    #     print(x)
    # for x in memory.task_collection.find():
    #     print(x)
    # for x in memory.message_collection.find():
    #     print(x)
    # for x in memory.customer_profile_collection.find():
    #     print(x)

except Exception as e:
    print("❌ Connection Failed")
    print(e)

# # test_workflow.py

# from backend.services.mongodb_memory_service import (
#     MongoDBMemoryService
# )

# memory = MongoDBMemoryService()

# memory.save_workflow(
#     workflow_id="wf_test_001",
#     customer_id="cust_001"
# )

# # print("Workflow Saved")
# from pymongo import MongoClient
# import certifi
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = MongoClient(
#     os.getenv("MONGO_URI"),
#     tls=True,
#     tlsCAFile=certifi.where(),
#     serverSelectionTimeoutMS=15000
# )

# print(client.admin.command("ping"))

memory.db.tasks.delete_many({})
memory.db.agent_messages.delete_many({})
memory.db.agent_context.delete_many({})
memory.db.workflows.delete_many({})