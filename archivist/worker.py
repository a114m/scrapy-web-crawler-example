from os import getenv
from zyda.archivist import ArchiveToMongo
from zyda.rabbitmq_client import RabbitMQClient
from zyda.mongo_client import MongoDBClient
import logging


logging.basicConfig(
    level=getattr(logging, getenv('LOG_LEVEL', 'DEBUG'))
)

logger = logging.getLogger(__name__)


def main():
    mq_client = RabbitMQClient()
    mongo_client = MongoDBClient()

    archivist = ArchiveToMongo(mq_client, mongo_client)
    archivist.run()


if __name__ == '__main__':
    main()
