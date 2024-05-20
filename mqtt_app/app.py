import paho.mqtt.client as mqtt
import os
import json
from datetime import datetime
from pymongo import MongoClient

# database
user_name = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
mongoClient = MongoClient(f"mongodb://{user_name}:{password}@demo_docker-mongo-1:27017/")

# on_connect callback
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("tgr2023/#")

# on_message callback
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # insert to database
    db = mongoClient.sensor_db
    device_col = db.device_col
    data = json.loads(msg.payload) # payload = {"value": 1}, location -> tgr2023/???
    #find document by Id
    record = device_col.find_one({"id": msg.topic.split('/')[-1]})
    if record is None:
        record = {
            "id": msg.topic.split('/')[-1],
            "location": msg.topic.split('/')[-2],
            "sensor_log": [{ "timestamp": datetime.now().isoformat(), "value": data["value"]},]
        }
        device_col.insert_one(record)
    else:
        record["sensor_log"].append({ "timestamp": datetime.now().isoformat(), "value": data["value"]})
        device_col.update_one({"id": msg.topic.split('/')[-1]}, {"$set": record})

    print(record)
    print("=====================================")   
    #print all data
    for x in device_col.find():
        print(x)

# init MQTT client
if __name__ == '__main__':
    # MQTT
    mqttClient = mqtt.Client()
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    mqttClient.connect("broker.hivemq.com", 1883, 60)
    mqttClient.loop_forever()