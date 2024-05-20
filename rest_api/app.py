#fast api app
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pandas as pd
import os
from pymongo import MongoClient

# dabase environment
user_name = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
mongoClient = MongoClient(f"mongodb://{user_name}:{password}@demo_docker-mongo-1:27017/")

app = FastAPI()

@app.get("/")
def show_location():
    db = mongoClient.sensor_db
    device_col = db.device_col
    location_list = []
    for record in device_col.find():
        location_list.append(record["location"])
    return {"location": list(set(location_list))}

@app.post("/api/{id}")
def query_data(id: str, request: Request):
    #get query parameter ?location=tse ?location=siit
    location = request.query_params.get("location")
    db = mongoClient.sensor_db
    device_col = db.device_col
    #find dict with id and location 
    print(id, db)
    record = device_col.find_one({"id": id,"location": location})
    if record is None:
        resp = {"message": "No data"}
    else:
        values = []
        for v in record['sensor_log']:
            values.append(v['value'])
        resp = {"status": "ok", "data": record["sensor_log"]}
    return JSONResponse(content=resp)
