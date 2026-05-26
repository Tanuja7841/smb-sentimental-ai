from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["smb_gh-client"]

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
# from db.mongodb import customers_collection

# sample_customers = [
#     {
#         "name": "Rahul",
#         "last_purchase_days": 30,
#         "sentiment": "negative",
#         "response_delay_days": 12
#     },
#     {
#         "name": "Priya",
#         "last_purchase_days": 5,
#         "sentiment": "positive",
#         "response_delay_days": 1
#     }
# ]

# customers_collection.insert_many(sample_customers)

# print("Sample customers inserted!")
########################################################################
# from db.mongodb import customers_collection
# from agents.churn_agent import analyze_customer

# customers = customers_collection.find()

# for customer in customers:

#     result = analyze_customer(customer)

#     print("\n====================")
#     print(f"Customer: {customer['name']}")
#     print(result)




# from pymongo import MongoClient
# from pymongo.server_api import ServerApi
# import certifi

# # uri = "MONGO_URI"

# client = MongoClient(
#     mongo_uri,
#     server_api=ServerApi('1'),
#     tlsCAFile=certifi.where()
# )

# try:
#     client.admin.command('ping')
#     print("Connected Successfully!")

# except Exception as e:
#     print(e)

# from dotenv import load_dotenv
# import os

# load_dotenv()

# print(os.getenv("MONGO_URI"))

# import json

# from agents.churn_agent import analyze_customer


# with open("backend/data/customers.json", "r") as file:

#     customers = json.load(file)


# for customer in customers:

#     result = analyze_customer(customer)

#     print("\n======================")
#     print(f"Customer: {customer['name']}")
#     print(result)

####=====================================================================

# import json

# from agents.churn_agent import analyze_customer
# from tools.recommendation_tool import generate_alert

# with open("backend/data/customers.json", "r") as file:

#     customers = json.load(file)


# # for customer in customers:

# #     result = analyze_customer(customer)
# #     alert = generate_alert(result)

# #     print("\n========================")
# #     print(f"Customer: {result['customer']}")
# #     print(f"Risk Level: {result['risk_level']}")
# #     print(f"Churn Score: {result['churn_score']}")
# #     print(alert)
# #     print(result["analysis"])

# import json

# from agents.sentiment_agent import analyze_message

# from services.analytics_service import (
#     sentiment_score,
#     classify_sentiment_risk
# )

# from tools.sentiment_alert_tool import generate_sentiment_alert
# from tools.memory_viewer import show_memory

# with open("backend/data/whatsapp_messages.json", "r") as file:

#     messages = json.load(file)


# for item in messages:

#     score = sentiment_score(item["message"])

#     risk_level = classify_sentiment_risk(score)

#     ai_analysis = analyze_message(item)

#     alert = generate_sentiment_alert(
#         item["customer"],
#         risk_level
#     )

#     # print("\n========================")
#     # print(f"Customer: {item['customer']}")
#     # print(f"Sentiment Score: {score}")
#     # print(f"Risk Level: {risk_level}")

#     # print("\nAI STRUCTURED ANALYSIS:")
#     # print(json.dumps(ai_analysis, indent=4))

#     # print("\nALERT:")
#     # print(alert)

#===============================================================================
import json

from agents.sentiment_agent import analyze_message

from orchestrator import orchestrate_customer_issue


with open("backend/data/customers.json", "r") as file:

    customers = json.load(file)


with open("backend/data/whatsapp_messages.json", "r") as file:

    messages = json.load(file)


customer_lookup = {
    customer["name"]: customer
    for customer in customers
}


for item in messages:

    print("\n==============================")
    print(f"Customer Message: {item['customer']}")

    sentiment_result = analyze_message(item)

    print("\n=========== SENTIMENT ANALYSIS ===========\n")
    print(sentiment_result)

    customer_data = customer_lookup.get(item["customer"])

    if customer_data:

        orchestration_result = orchestrate_customer_issue(
            customer_data,
            sentiment_result
        )

        print("\n=========== FINAL RESULT ===========\n")
        print(orchestration_result)
