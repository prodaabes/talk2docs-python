from fastapi import FastAPI, Request, UploadFile, File, Form
from typing import List
from upload import upload
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()


def pingMongoClient():
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        pingMongoClient()


uri = "mongodb+srv://prodaabes:123456Fafa@cluster0.wu7x6ae.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
pingMongoClient()


db = client.get_database('talk2docs-db')


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload-docs")
async def uploadDocs(ownerId: str = Form(...), files: List[UploadFile] = File(...)):
    upload(ownerId, files)
    return { "success": 1 }

@app.get("/get-all-users")
async def getUsers():
    users = list()
    users_cluster = db.get_collection('users').find({}, {'_id': 0})
    for user in users_cluster:
        users.append(user)
    return users