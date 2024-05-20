import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os

# database
user_name = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
mongoClient = MongoClient(f"mongodb://{user_name}:{password}@demo_docker-mongo-1:27017/")

st.sidebar.title("TGR2023")
location = st.sidebar.selectbox("Location", ["tse", "siit", "home"])

# get data from database
db = mongoClient.sensor_db
device_col = db.device_col
record = device_col.find_one({"location": location})


if record is None:
    st.write("No data")
else:  
    df = pd.DataFrame(record["sensor_log"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.line_chart(df.value)

latlng = {"lat" : [13.6525], "lon" : [100.4936]}
map_df = pd.DataFrame(latlng)
st.map(map_df)
