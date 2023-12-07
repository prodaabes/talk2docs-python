from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pathlib import Path
import shutil
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import jwt
import os, signal, subprocess

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

# current model.py subprocess fired by startChat() method
pro = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


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
        data["id"] = str(users[0]['_id'])
        data["fullname"] = payload_data["first_name"] + ' ' + payload_data["last_name"]

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
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        })

        # generate JWT token
        payload_data = {
            "email": email,
            "password": password
        }

        token = jwt.encode(
            payload=payload_data,
            key="tAlK2DoCs-SeCrEt"
            # algorithm='HS256'
        )

        data["success"] = True
        data["token"] = token

    return data

# this function made to upload the user files to the 'chats' folder
@app.post("/chats/{chatId}/upload-docs")
async def uploadDocs(chatId: str, files: List[UploadFile] = File(...)):
    for file in files:
        try:

            # ensure that the chat has its own directory
            file_parent_path = "chats/" + chatId
            Path(file_parent_path).mkdir(parents=True, exist_ok=True)

            file_path = file_parent_path + "/" + file.filename
            with open(file_path, "wb") as buffer:
                # copy the user file to the chat directory
                shutil.copyfileobj(file.file, buffer)

                # add the file name to the files array in the chat document in database
                db['chats'].find_one_and_update(
                    { '_id': ObjectId(chatId) },
                    {
                        '$push': {
                            'files': file.filename
                        }
                    },
                    # the upsert set to True in order to create the chat document if not exists in database
                    upsert=True
                )

                # add the file content to knowledge.txt
                subprocess.Popen(["venv/Scripts/python.exe", "add_doc.py", "--chatId", chatId, "--file", file.filename])
                    
        except Exception as e:
            print(str(e))
    return { "success": True }


# this function made to remove a single file from the 'chats' folder
@app.post("/chats/{chatId}/remove-doc")
async def removeDoc(request: Request):
    try:

        body = await request.json()

        chatId = body['chatId']
        fileName = body['fileName']

        # remove the file from the chat directory
        file_parent_path = "chats/" + chatId

        # get the document
        chatDoc = db['chats'].find_one({ '_id': ObjectId(chatId) })
        files = chatDoc['files']

        # remove the file name from the files array in the chat document in database
        db['chats'].find_one_and_update(
            { '_id': ObjectId(chatId) },
            {
                '$pull': {
                    'files': fileName
                }
            },
            # the upsert set to False in order to not create the chat document if not exists in database
            upsert=False
        )
        # delete the file from the chat directory
        Path(file_parent_path + "/" + fileName).unlink()

        # remove the file content from knowledge.txt
        subprocess.Popen(["venv/Scripts/python.exe", "remove_doc.py", "--chatId", chatId, "--file", fileName])

        # check if the document contains only 1 file
        if len(files) == 1 and fileName in files:
            # delete the entire document from database
            db['chats'].delete_one({ '_id': ObjectId(chatId) })
            # delete all messages for this chat
            db['messages'].delete_many({ 'chatId': chatId })
            # delete knowledge.txt
            Path(file_parent_path + "/knowledge.txt").unlink()
            # delete the chat directory
            Path(file_parent_path).rmdir()
                    
    except Exception as e:
        print(str(e))

    return { "success": True }



@app.post('/chats/{chatId}/start')
async def startChat(chatId: str):
    #subprocess.Popen(["venv/Scripts/python.exe", "model.py", "--chatId", chatId])
    #port = subprocess.check_output(["venv/Scripts/python.exe", "model.py", "--chatId", chatId], shell=False)
    #print("this is the port from main: " + port.decode("utf-8"))

    global pro

    if (pro != None):
        # kill the old process
        pro.kill()

    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    pro = subprocess.Popen(["venv/Scripts/python.exe", "model.py", "--chatId", chatId], stdout=subprocess.PIPE, shell=False)

    return { "success": True, "port": 8765 }


@app.get('/chats/{userId}')
async def getChats(userId: str):

    # get all chats for userId
    chatsCol = db['chats']
    query = { "userId": userId }
    cursor = chatsCol.find(query)
    chats = list(cursor)

    # without this code, we get a TypeError.
    for c in chats:
        # convert type: ObjectId to type: str
        c['id'] = str(c['_id'])
        del[c['_id']]

    return { "success": True, "chats": chats }

@app.get('/messages/{chatId}')
async def getMessages(chatId: str):

    # get all chats for userId
    messagesCol = db['messages']
    query = { "chatId": chatId }
    cursor = messagesCol.find(query)
    messages = list(cursor)

    # without this code, we get a TypeError.
    for m in messages:
        # convert type: ObjectId to type: str
        m['id'] = str(m['_id'])
        del[m['_id']]

    return { "success": True, "messages": messages }

# @app.post('/messages/send/{text}')
# async def sendMessage(chatId: str, text: str):

#     # add new message to messages collection
#     messagesCol = db['messages']
#     messagesCol.insert_one({
#         'chatId': chatId,
#         'isQuestion': True,
#         'content': text
#     })

@app.get('/chats/{chatId}/files')
async def getFiles(chatId: str):

    chatsCol = db['chats']
    query = { "_id": ObjectId(chatId) }
    chats = chatsCol.find(query, { "_id": 0 })

    files = chats[0]['files']

    return { "success": True, "files": files }