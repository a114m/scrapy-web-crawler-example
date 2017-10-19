# -*- coding: utf-8 -*-

import scrapy


class RestaurantItem(scrapy.Item):
    source = scrapy.Field()
    language = scrapy.Field()
    url = scrapy.Field()
    last_update = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    geolocation = scrapy.Field()
    phone_number = scrapy.Field()
    opening_hours = scrapy.Field()
    rating = scrapy.Field()
    number_of_reviews = scrapy.Field()
    info = scrapy.Field()
    menu = scrapy.Field()
    images = scrapy.Field()

# 
# class MenuItem(scrapy.Item):
#     restaurant_id = scrapy.Field()
#     source = scrapy.Field()
#     language = scrapy.Field()
#     url = scrapy.Field()
#     last_update = scrapy.Field()
#     menu = scrapy.Field()
#     number_of_reviews = scrapy.Field()
#     images = scrapy.Field()
