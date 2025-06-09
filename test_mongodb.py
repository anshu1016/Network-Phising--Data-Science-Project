
from pymongo.mongo_client import MongoClient

from urllib.parse import quote_plus
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()
print("USERNAME:", os.getenv("MONGO_DB_USERNAME"))
print("PASSWORD:", os.getenv("MONGO_DB_PASSWORD"))  # Should not be None
username = quote_plus(os.getenv("MONGO_DB_USERNAME"))
password = quote_plus(os.getenv("MONGO_DB_PASSWORD"))

uriURL = f"mongodb+srv://{username}:{password}@neog.5v8po5k.mongodb.net/?retryWrites=true&w=majority&appName=neoG"

uri = uriURL

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)