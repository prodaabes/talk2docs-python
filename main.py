from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from upload import upload
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import jwt

# command to run the server: uvicorn main:app --host <ip-address> --port 80 --reload
app = FastAPI()


# cors required for web app #
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
# cors required for web app #


def pingMongoClient():
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        pingMongoClient()


# uri = "mongodb+srv://prodaabes:123456Fafa@cluster0.wu7x6ae.mongodb.net/?retryWrites=true&w=majority"
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
    return { "success": 1 }

@app.post("/login")
async def login(request: Request):

    # get the request body
    body = await request.json()

    # get email and password from body
    email = body["email"]
    password = body["password"]

    # check if the email and password exists in our database
    usersCol = db['users']
    query = { "email": email, "password": password }
    cursor = usersCol.find(query)
    users = list(cursor)
    
    # this data will be returned in response
    data = {}

    if len(users) == 0:
        data["success"] = False
    else:
        # generate JWT token

        payload_data = {
            "first_name": users[0]['first_name'],
            "last_name": users[0]['last_name'],
            "email": email
        }

        token = jwt.encode(
            payload=payload_data,
            key="tAlK2DoCs-SeCrEt"
        )

        data["success"] = True
        data["token"] = token

    return data

@app.post("/register")
async def register(request: Request):

    # get the request body
    body = await request.json()

    # get user data from body
    first_name = body["first_name"]
    last_name = body["last_name"]
    email = body["email"]
    password = body["password"]

    # check if the email already exists in our database
    usersCol = db['users']
    query = { "email": email }
    cursor = usersCol.find(query)
    users = list(cursor)
    
    # this data will be returned in response
    data = {}

    # if email already exists, don't register
    if len(users) > 0:
        data["success"] = False
    else:
        usersCol.insert_one({
            first_name: first_name,
            last_name: last_name,
            email: email,
            password: password
        })

        # generate JWT token
        payload_data = {
            "email": email,
            "password": password
        }

        token = jwt.encode(
            payload=payload_data,
            key="tAlK2DoCs-SeCrEt"
        )

        data["success"] = True
        data["token"] = token

    return data