from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List
from upload import upload
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import jwt
from jose import JWTError
from datetime import datetime, timedelta

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def pingMongoClient():
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        pingMongoClient()

uri = "mongodb://localhost:27017"

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
    return {"success": 1}

@app.post("/login")
async def login(request: Request):
    body = await request.json()
    email = body["email"]
    password = body["password"]
    print(f"Received email: {email}, password: {password}")

    usersCol = db['users']
    query = {"email": email, "password": password}
    cursor = usersCol.find(query)
    users = list(cursor)
    
    data = {}
    if len(users) == 0:
        data["success"] = False
    else:
        payload_data = {"email": email, "password": password}
        token = jwt.encode(payload=payload_data, key="tAlK2DoCs-SeCrEt")
        data["success"] = True
        data["token"] = token

    return data

@app.post("/register")
async def register(request: Request):
    body = await request.json()
    first_name = body["first_name"]
    last_name = body["last_name"]
    email = body["email"]
    password = body["password"]

    usersCol = db['users']
    query = {"email": email}
    cursor = usersCol.find(query)
    users = list(cursor)
    
    data = {}
    if len(users) > 0:
        data["success"] = False
    else:
        usersCol.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        })

        payload_data = {"email": email, "password": password}
        token = jwt.encode(payload=payload_data, key="tAlK2DoCs-SeCrEt")
        data["success"] = True
        data["token"] = token

    return data


