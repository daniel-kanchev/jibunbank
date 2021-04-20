import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from jibunbank.items import Article


class jibunbankSpider(scrapy.Spider):
    name = 'jibunbank'
    start_urls = ['https://www.jibunbank.co.jp/corporate/news/']

    def parse(self, response):
        yield response.follow(response.url, self.parse_year, dont_filter=True)

        years = response.xpath('//div[@class="subNavi-main"]//a/@href').getall()
        yield from response.follow_all(years, self.parse_year)

    def parse_year(self, response):
        links = response.xpath('//dd/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = " ".join(response.xpath('//div[@class="heading-main"]//text()').getall()).strip()

        date = response.xpath('//div[@class="heading-sub"]/p/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="c-ground-01"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
