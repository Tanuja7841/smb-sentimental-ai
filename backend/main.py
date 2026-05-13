# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os

# load_dotenv()

# mongo_uri = os.getenv("MONGO_URI")
# client = MongoClient(mongo_uri)
# db = client["smb_gh-client"]

# print("MongoDB Connected Successfully!")
# ########################################################################
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os

# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")

# genai.configure(api_key=api_key)

# model = genai.GenerativeModel("gemini-2.0-flash")

# response = model.generate_content(
#     "Explain customer churn in simple words"
# )

# print(response.text)
##########################################################################
from db.mongodb import customers_collection

sample_customers = [
    {
        "name": "Rahul",
        "last_purchase_days": 30,
        "sentiment": "negative",
        "response_delay_days": 12
    },
    {
        "name": "Priya",
        "last_purchase_days": 5,
        "sentiment": "positive",
        "response_delay_days": 1
    }
]

customers_collection.insert_many(sample_customers)

print("Sample customers inserted!")
