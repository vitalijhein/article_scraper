import scrapy
import dateparser
from pymongo.errors import DuplicateKeyError
from mongo_connection.MongoConnector import access_mongo_return_entries, access_mongo_return_collection


class RtLinkSpider(scrapy.Spider):
    name = 'RtLinkSpider'
    allowed_domains = ['rt.com']
    start_urls = ['https://www.rt.com/search?q=Ukraine&type=News&xcategory=sport']
    client_name = "russian_news_articles"
    collection_name_link_store = "rt_com_links"

    def parse(self, response, **kwargs):
        #known naming issue, since actually we
        my_collection = access_mongo_return_collection(self.client_name, self.collection_name_link_store)
        articles_selectors = response.xpath('//*[@class="card-rows__content"]')
        print(articles_selectors)
        date = ""
        stop_date = 1645660801
        for curr_selector in articles_selectors:
            date = curr_selector.xpath(".//*[@class='date']/text()").get()
            date = dateparser.parse(date)
            date = int(round(date.timestamp()))
            article = {
                "rt_id": curr_selector.xpath(".//a/@href").get(),
                "date": date,
                "title": curr_selector.xpath(".//a/text()").get(),
                "link": "https://www.rt.com" + curr_selector.xpath(".//a/@href").get()
            }
            try:
                my_collection.insert_one(article)
            except DuplicateKeyError:
                print("duplicate was not inserted")
                continue

        if int(date) >= int(stop_date):
            next_page = "https://www.rt.com" + response.xpath('//a[@id="listingBtn"]/@data-href').get()
            print(next_page)
            yield response.follow(next_page, self.parse)
