import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

# uri = "mongodb+srv://prodaabes:123456Fafa@cluster0.wu7x6ae.mongodb.net/?retryWrites=true&w=majority"
uri = os.environ.get("MONGODB_URL")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.get_database('talk2docs-db')

def pingMongoClient():
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        pingMongoClient()