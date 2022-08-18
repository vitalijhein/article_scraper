import scrapy
from pymongo.errors import DuplicateKeyError
from scrapy import Request
from datetime import datetime
from mongo_connection.MongoConnector import access_mongo_return_entries, access_mongo_return_collection


class AbcNewsSpider(scrapy.Spider):
    name = 'AbcNewsSpider'
    allowed_domains = ['abcnews.go.com']
    start_urls = ['http://abcnews.go.com/']
    client_name = "american_news_articles"
    collection_name_link_store = "abc_com_links"
    collection_name_article_store = "abc_com_articles"

    def start_requests(self):
        entries = access_mongo_return_entries(self.client_name, self.collection_name_link_store)
        for entry in entries:
            url = entry["link"]
            yield Request(url, callback=self.parse,
                          meta={"abc_article_id": entry["abc_article_id"],
                                "date": entry["date"],
                                "link": entry["link"]
                                })

    def parse(self, response, **kwargs):
        article_title = response.xpath("//h1/text()").get()
        article_subtitle = response.xpath("//*[@class='stExy xTlfF KrUxN nOQZC WLXON IPnV ']/text()").get()
        article_body_list = response.xpath("//*[@class='fnmMv geuMB alqtB wqIGQ ']//text()").getall()
        article_body = " ".join(article_body_list)
        abc_article_id = response.meta["abc_article_id"]
        link = response.meta["link"]
        date = response.meta["date"]
        downloaded_at = datetime.now()
        downloaded_at = int(round(downloaded_at.timestamp()))
        article = {
            "abc_article_id": abc_article_id,
            "date": date,
            "link": link,
            "title": article_title.replace("\n", "").replace("\t", "").strip(),
            "subtitle": article_subtitle.replace("\n", "").replace("\t", "").strip(),
            "article_body": article_body.replace("\n", "").replace("\t", "").strip(),
            "downloaded_at": downloaded_at
        }
        print(article)
        article_collection_abc = access_mongo_return_collection(self.client_name, self.collection_name_link_store)
        try:
            article_collection_abc.insert_one(article)
        except DuplicateKeyError:
            print("duplicate was not inserted")
