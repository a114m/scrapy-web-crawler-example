from os import getenv
import pymongo
import logging
import traceback

logger = logging.getLogger(__name__)


class MongoDBClient(object):
    def __init__(self):
        self.host_name = getenv('MONGO_HOST', 'localhost')
        self.port = getenv('MONGO_PORT', 27017)
        self.db_name = getenv('MONGO_DB', 'zyda')
        self.collection_name = getenv('MONGO_COLLECTION', 'restaurants')
        self.client = pymongo.MongoClient(self.host_name, self.port)
        self.collection = self.client[self.db_name][self.collection_name]

    def get_collection(self):
        return self.collection

    def add_or_update(self, item):
        try:
            res = self.collection.replace_one({'id': item['id']}, item, upsert=True)
            return True if res.upserted_id else False
        except Exception as e:
            logger.error(
                "Error adding item to mongo collection '%s': %s\n%s" %
                (self.collection.name, traceback.format_exc(), getattr(e, 'details', e))
            )
            return False
