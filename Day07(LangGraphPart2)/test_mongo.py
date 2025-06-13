# test_mongo.py
from pymongo import MongoClient

client = MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")
print(client.list_database_names())
