# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from scrapy.link import Link
from itertools import izip_longest
import re


class SiteMapLinkExtractor():
    def __init__(self, pattern):
        self.pattern = pattern

    def extract_links(self, response):
        for link in response.xpath('//text()').extract():  # XXX: [:1] is for dev purpose, remove it
            if re.match(self.pattern, link):
                return [Link(link)]


def group_items(n, multiple_values=True):
    def func(input):
        grouped = map(lambda input: {input[0]: input[1:]}, izip_longest(*[iter(input)] * n))
        return {k: v if (multiple_values and len(v) > 1) else v[0] for dic in grouped for k, v in dic.items()}
    return func
