# zyda
docker-compose of different pipeline components to scrap example website 'yelp' and archiving the scrapped data to MongoDB, the components:
* Scrapy as the first pipeline component to crawl the the website and write the output restaurants to RabbitMQ in real-time
* RabbitMQ as Messaging Q to store the messages between pipeline components and allows the pipeline to be extensible
* Archivist is a python component to read restaurants from RabbitMQ and save them to MongoDB
* MongoDB as NoSQL database to store the extracted restaurants data
