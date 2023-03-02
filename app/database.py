import os

import pymongo
from pymongo.server_api import ServerApi


MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'store_image_coordinates')


def get_database() -> pymongo.collection:
    """Returns a database collection with images"""
    client = pymongo.MongoClient(MONGO_URI, server_api=ServerApi('1'))
    dbname = client[DB_NAME]
    collection = dbname['image_coordinates']
    return collection
