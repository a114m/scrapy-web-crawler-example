import scrapy
import urlparse
import urllib
import time
import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, Join, TakeFirst, MapCompose, Compose
from w3lib.url import url_query_cleaner, parse_qs
from itertools import izip_longest
from decimal import Decimal
from zyda.items import RestaurantItem
from . import SiteMapLinkExtractor, group_items


class Yelp(CrawlSpider):
    name = 'yelp'
    allowed_domains = ['yelp.com']
    start_urls = ['https://www.yelp.com/bulkdata/google_sitemaps/www.yelp.com/extra-url-0.xml']
    currency = 'USD'

    rules = (
        Rule(SiteMapLinkExtractor(pattern='.*OnlineReservations.*cflt=restaurants.*'), callback='extract_restaurants'),
    )

    def follow_pagination(*args, **kwargs):
        xpath = kwargs['xpath'] if 'xpath' in kwargs else None

        def func_wrapper(*args, **kwargs):
            func = args[-1]

            def wrapper(self, response):
                for item in func(self, response):
                    yield item
                next_links = response.xpath(xpath).extract() if xpath else list()
                for link in next_links:
                    if link:
                        request = scrapy.Request(response.urljoin(link), callback=lambda response: self.follow_pagination(xpath=xpath)(func)(self, response))
                        if 'id' in response.meta and response.meta['id']:
                            request.meta['id'] = response.meta['id']
                        yield request
            return wrapper
        return func_wrapper

    @follow_pagination(xpath='//div[contains(@class, "pagination-links")]//a[contains(@class, "next")]/@href')
    def extract_restaurants(self, response):
        restaurants_urls = response.xpath("//div[@class='search-results-content']//span[@class='indexed-biz-name']/*/@href").extract()
        for url in restaurants_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_restaurant)

    def parse_restaurant(self, response):
        loader = ItemLoader(item=RestaurantItem(
            source=self.name,
            language='en',
            last_update=int(time.time())
        ), response=response)

        loader.default_input_processor = Compose(MapCompose(lambda x: x.strip() or None))
        loader.default_output_processor = TakeFirst()

        url = url_query_cleaner(response.url)
        loader.add_value('url', url)

        id = urllib.unquote(urlparse.urlparse(url).path.split('/')[-1])
        loader.add_value('id', id)

        loader.add_xpath('name', '//div[contains(@class, "biz-page-header")]//h1[contains(@class, "biz-page-title")]/text()')

        loader.address_out = Join(' - ')
        loader.add_xpath('address', "//div[contains(@class, 'map-box-address')]//text()")

        loader.add_xpath('geolocation', "//div[@class='mapbox-map']//img/@src", MapCompose(lambda url: parse_qs(url).get('center')))

        loader.add_xpath('phone_number', "//div[@class='mapbox-text']//span[@class='biz-phone']/text()")

        hours_loader = loader.nested_xpath("//div[contains(@class, 'biz-hours')]//tr/th[@scope]/..")
        hours_loader.opening_hours_in = Compose(group_items(3))
        hours_loader.opening_hours_out = Identity()
        hours_loader.add_xpath('opening_hours', './th/text() | ./td/span[@class="nowrap"]/text()')

        loader.add_xpath(
            'rating',
            '//div[contains(@class, "biz-page-header")]//div[contains(@class, "biz-rating")]/div[contains(@class, "i-stars")]/@title',
            re=r'(?:\D*)(\d+(?:\.\d+)?)'
        )

        loader.number_of_reviews_in = MapCompose(int)
        loader.add_xpath('number_of_reviews', '//div[contains(@class, "biz-page-header")]//span[contains(@class, "review-count")]/text()', re=r'^\D*(\d+)')

        info_loader = loader.nested_xpath('//div[contains(@class, "sidebar")]//div[@class="ywidget"]/ul[@class="ylist"]/li/div[contains(@class, "short-def-list")]/dl')
        info_loader.info_in = Compose(MapCompose(unicode.strip), group_items(2))
        info_loader.info_out = Identity()
        info_loader.add_xpath('info', './dt[@class="attribute-key"]/text() | ./dd/text()')

        item = loader.load_item()

        menu_url = TakeFirst()(response.xpath('//h3[@class="menu-preview-heading"]/a/@href').extract())

        if menu_url:
            yield scrapy.Request(response.urljoin(menu_url), callback=self.parse_menu, meta={'item': item})
        else:
            yield item

    def parse_menu(self, response):
        if ('item' in response.meta and response.meta['item']):
            item = response.meta['item']
        else:
            return

        mixed_menus_selectors = response.xpath('//div[@class="menu-sections"]/*')
        grouped_menus_sels = izip_longest(*[iter(mixed_menus_selectors)]*2)
        menus_list = dict()
        for menu_sel in grouped_menus_sels:
            menu_name = TakeFirst()(MapCompose(unicode.strip)(menu_sel[0].xpath('.//text()').extract())) or 'Other Menu'
            menu_content = list()
            menu_items_sel = menu_sel[1].xpath('./div[@class="menu-item"]')
            for item_sel in menu_items_sel:
                menu_item = dict()

                menu_item['name'] = TakeFirst()(MapCompose(unicode.strip)(item_sel.xpath('.//h4//text()').extract()))

                url = TakeFirst()(item_sel.xpath('.//h4//a/@href').extract())
                if url:
                    menu_item['url'] = response.urljoin(url)

                description = TakeFirst()(item_sel.xpath('.//p/text()').extract())
                if description:
                    menu_item['description'] = description

                price = TakeFirst()(MapCompose(unicode.strip)(item_sel.xpath('.//li[contains(@class, "price")]/text()').extract()))
                if price:
                    menu_item['price'] = Decimal(re.findall(r'^(?:\D*)(\d+(?:\.\d+)?)', price)[0])
                    menu_item['currency'] = self.currency

                thumbnail = TakeFirst()(item_sel.xpath('.//img/@src').extract())
                if thumbnail and 'default_avatars' not in thumbnail:
                    menu_item['thumbnail'] = thumbnail

                number_of_reviews = TakeFirst()(item_sel.xpath('.//a[@class="num-reviews"]/text()').extract())
                if number_of_reviews:
                    menu_item['number_of_reviews'] = int(re.findall(r'^(?:\D*)(\d+(?:\.\d+)?)', number_of_reviews)[0])

                menu_content.append(menu_item)

            menus_list[menu_name] = menu_content

        item['menu'] = menus_list
        yield item

    def _requests_to_follow(self, response):
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)
