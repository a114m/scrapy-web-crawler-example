zyda
=============
Example of scraping website 'yelp.com' using `scrapy`, posting the extracting restaurants to messaging queue `RabbitMQ` using AMQP and a python worker to consume the restaurant items from the message q and archive them `MongoDB`, the components:
* Scrapy as the first pipeline component to crawl the the website and write the output restaurants to RabbitMQ in real-time
* RabbitMQ as Messaging Q to store the messages between pipeline components and allows the pipeline to be extensible
* Archivist is a python component to read restaurants from RabbitMQ and save them to MongoDB
* MongoDB as NoSQL database to store the extracted restaurants data

All components are installed and started using `docker-compose` magic.

## Installation
Before you go on you need `docker` to be installed and its daemon running and `docker-compose` command installed as well but no further steps installation.

## Running
- In the project root:
```
$ docker-compose up
```
This will pull docker images and start scrapy spider also RabbitMQ, MongoDB, and Archivist worker.


**Make sure you don't have a local daemons running for rabbitmq/mongodb listening locally on default ports that will definitely conflict with docker exposed ports**

## Examining Results
- Scrapy will log extracted items and requests to the standard output stdout.
- RabbitMQ message queues can be monitored using RabbitMQ management plugin that's already pre-installed and provides web interface that can be accessed on http://localhost:15672/ .
- MongoDB can be accessed using a mongo client or any other preferred way, mongo is listening on `localhost` on port `27017` .
Installing mongo client for fedora:
```
$ sudo yum install mongo-tools
```
Connecting to MongoDB and examining result
```
$ mongo
$ use zyda
$ db.restaurants.count()  # show the collected restaurants count
$ db.restaurants.find().limit(5)  # to show sample of the collected data
```
