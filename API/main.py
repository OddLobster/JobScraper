from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27018/")
db = client["JobPostings"]
collection = db["karriereAT"]


@app.get("/get_item/{link}")
async def read_item(link: str):
    # Retrieve item from MongoDB
    result = collection.find_one({"job_hash": link})
    result["_id"] = str(result["_id"])
    return result

@app.get("/get_items/{limit}")
async def read_all_items(limit: int):
    result = collection.find({}).limit(limit)
    x = []
    for res in result:
        res["_id"] = str(res["_id"])
        x.append(res)   
    return x

@app.get("/get_companies/{limit}")
async def read_all_items(limit: int):
    result = collection.find({}, {"company":1}).distinct("company")[:limit]
    return result

@app.get("/items/company/{company}")
async def read_all_items(company: str):
    result = collection.find({"company":company})
    x = []
    for res in result:
        res["_id"] = str(res["_id"])
        x.append(res)

    return x