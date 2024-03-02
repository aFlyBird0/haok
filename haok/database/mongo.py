from pymongo import MongoClient
from pymongo.server_api import ServerApi

from haok.config.settings import get_settings

def _get_default_db():
    uri = get_settings().database.url
    db_name = get_settings().database.db_name
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    # print(self.client.list_databases())
    db = client[db_name]
    return db


default_db = _get_default_db()
