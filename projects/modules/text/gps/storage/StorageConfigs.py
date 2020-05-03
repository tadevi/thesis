from collections import MutableMapping

DEFAULT_MONGO_URL = "mongodb+srv://tai_than:tai_than123456@cluster0-osct2.mongodb.net/test?retryWrites=true&w=majority"
DEFAULT_MONGO_DB = "iot-db"


class StorageConfigs:
    def __init__(self,
                 collection_name: str,
                 mongo_url: str = DEFAULT_MONGO_URL,
                 db_name: str = DEFAULT_MONGO_DB
                 ):
        self.db_name = db_name
        self.collection_name = collection_name
        self.mongo_url = mongo_url
