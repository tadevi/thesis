import pymongo

print("start init face db")

client = pymongo.MongoClient("mongodb://localhost:27017/")
col = client["cloud-db"]["profile"]
col.drop()
col.insert_many([
    {"id": "02cbf741-5afd-403c-b4ca-08c070058582", "name": "Obama", "age": 50},
    {"id": "e6a8d809-59bc-440b-8a92-4629b9d76f3b", "name": "Misthy", "age": 25},
    {"id": "8d5ce536-e734-4f3b-8151-e02168ff4eac", "name": "Than Đuc Tai", "age": 22},
    {"id": "5ba85527-e583-4234-aa4a-609a964a73ba", "name": "Luong Tuan Kiet", "age": 23},
    {"id": "50fc43f4-f122-4d6a-b4d3-552385b65403", "name": "Key", "age": 42},
    {"id": "17eb17f0-325f-496c-b8ee-6b4eb45c55b7", "name": "Erik", "age": 23}
])

print("stop init face db")
