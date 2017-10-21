import logging
import json

logger = logging.getLogger(__name__)


class ArchiveToMongo(object):
    def __init__(self, mq_client, mongo_client):
        self.mq_client = mq_client
        self.mongo_client = mongo_client

    def run(self):
        self.mq_client.start_consuming(self.receive_msg)

    def receive_msg(self, ch, method, properties, body):
        try:
            restaurant = json.loads(body)
        except Exception as err:
            logger.error("Failed parsing message read from MsgQ: %s\n\n%s" % (err, restaurant))
            return
        if self.mongo_client.add_or_update(restaurant):
            logger.info("Saved resturant to mongo successfully")
        else:
            logger.info("Wasn't able to save resturant to mongo")
