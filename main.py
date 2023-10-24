from fastapi import FastAPI, Request, UploadFile, File, Form
from typing import List
from upload import upload

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload-docs")
async def uploadDocs(ownerId: str = Form(...), files: List[UploadFile] = File(...)):
    upload(ownerId, files)
    return { "success": 1 }