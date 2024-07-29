# src/services/mongodb/mongodb.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import time
import os

from ...config import MONGO_CONFIG
from ..logger.base_logger import BaseLogger

class MongoDB:
    def __init__(self):
        self.logger = BaseLogger('mongodb').get_logger()
        self.host = MONGO_CONFIG['host']
        self.port = MONGO_CONFIG['port']
        self.username = MONGO_CONFIG['username']
        self.password = MONGO_CONFIG['password']
        self.db_name = MONGO_CONFIG['db_name']
        self.auth_source = MONGO_CONFIG.get('auth_source')
        self.client = None
        self.db = None
        self.connect_attempts = 3
        self.connect()

    def connect(self):
        attempt = 1
        while attempt <= self.connect_attempts:
            try:
                self.client = MongoClient(
                    host=self.host, 
                    port=self.port, 
                    username=self.username, 
                    password=self.password,
                    authSource=self.auth_source
                )
                self.db = self.client[self.db_name]
                self.logger.info("Connected to MongoDB successfully!")
                return
            except ConnectionFailure as e:
                self.logger.error(f"Attempt {attempt} failed to connect to MongoDB: {e}")
                if attempt == self.connect_attempts:
                    self.logger.error(f"Maximum attempts reached. Could not connect to MongoDB.")
                    return
                attempt += 1
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return

    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def insert_one(self, collection_name, document):
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            self.logger.info(f"Inserted document with id {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            self.logger.error(f"Failed to insert document: {e}")
            return

    def find_one(self, collection_name, query):
        if self.client is None:
            self.logger.info("Not connected to MongoDB! Attempting to reconnect...")
            self.connect()

        try:
            collection = self.db[collection_name]
            result = collection.find_one(query)
            return result
        except Exception as e:
            self.logger.error(f"Failed to find document: {e}")
            return None

mongo_db = MongoDB()
