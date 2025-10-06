from pymongo import MongoClient
from dotenv import load_dotenv
import os
import socket
import ssl
import certifi

load_dotenv()
print(f"MONGO_URI: {os.getenv('MONGO_URI')}")
try:
    print("Attempting to connect to MongoDB Atlas...")
    client = MongoClient(
        os.getenv('MONGO_URI'),
        serverSelectionTimeoutMS=60000,
        connectTimeoutMS=60000,
        tls=True,
        tlsCAFile=certifi.where()
    )
    print("Connected to MongoDB Atlas")
    print(f"Server status: {client.admin.command('ping')}")
    print(f"Databases: {client.list_database_names()}")
    db = client.get_database('blockedin')
    print(f"Collections in blockedin: {db.list_collection_names()}")
    db.users.drop()
    print("Users collection dropped")
except Exception as e:
    print(f"Connection failed: {e}")
    try:
        socket.setdefaulttimeout(5)
        host = os.getenv('MONGO_URI').split('@')[1].split('/')[0]
        socket.gethostbyname(host)
        print(f"DNS resolution successful for {host}")
        nc_result = os.system(f'nc -zv {host} 27017')
        print(f"Netcat result: {nc_result}")
    except socket.gaierror:
        print(f"DNS resolution failed for {host}")