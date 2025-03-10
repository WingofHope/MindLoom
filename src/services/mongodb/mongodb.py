# src/services/mongodb/mongodb.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import time

from config import config
from services.logger.create_logger import CreateLogger

MONGO_CONFIG = config.get("prompts.mongodb_config")

class MongoDB:
    def __init__(self):
        self.logger = BaseLogger('mongodb').get_logger()
        
        # 读取配置
        connection_string = MONGO_CONFIG.get('connection_string')
        if not connection_string:
            # 如果没有提供连接字符串，则使用用户名、密码等信息生成
            connection_string = self.build_connection_string()
            
        self.db_name = MONGO_CONFIG['db_name']
        self.client = None
        self.db = None
        self.connect_attempts = 3
        
        self.connect(connection_string)

    def build_connection_string(self):
        # 生成 MongoDB 连接字符串
        username = MONGO_CONFIG['username']
        password = MONGO_CONFIG['password']
        host = MONGO_CONFIG['host']
        port = MONGO_CONFIG['port']
        db_name = MONGO_CONFIG['db_name']
        
        return f"mongodb://{username}:{password}@{host}:{port}/{db_name}"

    def connect(self, connection_string):
        attempt = 1
        while attempt <= self.connect_attempts:
            try:
                # 连接到 MongoDB
                self.client = MongoClient(connection_string)
                self.db = self.client[self.db_name]
                self.logger.info("Connected to MongoDB successfully!")
                return
            except ConnectionFailure as e:
                self.logger.error(f"Attempt {attempt} failed to connect to MongoDB: {e}")
                if attempt == self.connect_attempts:
                    self.logger.error(f"Maximum attempts reached. Could not connect to MongoDB.")
                    return
                attempt += 1
                time.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                self.logger.error(f"Unexpected error during connection attempt {attempt}: {e}")
                if attempt == self.connect_attempts:
                    return
                attempt += 1

    def close(self):
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed.")
            
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
            return None

    def find_one(self, collection_name, query):
        if self.client is None:
            self.logger.info("Not connected to MongoDB! Attempting to reconnect...")
            self.connect(MONGO_CONFIG['connection_string'])

        try:
            collection = self.db[collection_name]
            result = collection.find_one(query)
            return result
        except Exception as e:
            self.logger.error(f"Failed to find document: {e}")
            return None
