from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")


client = MongoClient(
    mongo_uri,
    tls=True,
    tlsAllowInvalidCertificates=True
)


try:
    client.admin.command("ping")
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ Connection failed:", e)

db = client["smb_sentinel"]
customers_collection = db["customers"]