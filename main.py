from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/printName")
async def printName(item: Item):
    return item