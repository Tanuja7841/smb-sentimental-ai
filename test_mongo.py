from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi 

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

    print("Collections:")
    print(db.list_collection_names())
    print("✅ MongoDB Connected Successfully!")

except Exception as e:
    print("❌ Connection Failed")
    print(e)