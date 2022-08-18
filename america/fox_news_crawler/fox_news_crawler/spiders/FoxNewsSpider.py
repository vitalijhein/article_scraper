import pymongo
import scrapy
from pymongo.errors import DuplicateKeyError
from scrapy import Request
from datetime import datetime


class FoxNewsSpider(scrapy.Spider):
    name = 'FoxNewsSpider'
    allowed_domains = ['foxnews.com']
    start_urls = ['http://foxnews.com/']

    def start_requests(self):
        entries = self.access_mongo()
        for entry in entries:
            url = entry["link"]
            yield Request(url, callback=self.parse,
                          meta={"fox_article_id": entry["fox_article_id"],
                                "date": entry["date"],
                                "link": entry["link"]
                                })

    def parse(self, response, **kwargs):
        article_title = response.xpath("//*[@class='headline']/text()").get()
        article_subtitle = response.xpath("//*[@class='sub-headline speakable']/text()").get()
        article_body_list = response.xpath("//*[@class='article-body']//p//text()").getall()
        article_body = " ".join(article_body_list)
        fox_article_id = response.meta["fox_article_id"]
        link = response.meta["link"]
        date = response.meta["date"]
        downloaded_at = datetime.now()
        downloaded_at = int(round(downloaded_at.timestamp()))
        article = {
            "fox_article_id": fox_article_id,
            "date": date,
            "link": link,
            "title": article_title.replace("\n", "").replace("\t", "").strip(),
            "subtitle": article_subtitle.replace("\n", "").replace("\t", "").strip(),
            "article_body": article_body.replace("\n", "").replace("\t", "").strip(),
            "downloaded_at": downloaded_at
        }
        print(article)
        article_collection_fox = self.access_mongo_article_store()
        try:
            article_collection_fox.insert_one(article)
        except DuplicateKeyError:
            print("duplicate was not inserted")

    def access_mongo(self):
        my_client = pymongo.MongoClient('mongodb://localhost:27017/', username="root", password="root")
        my_database = my_client["american_news_articles"]
        my_collection = my_database["fox_com_links"]
        entries = my_collection.find()

        return entries

    def access_mongo_article_store(self):
        my_client = pymongo.MongoClient('mongodb://localhost:27017/', username="root", password="root")
        my_database = my_client["american_news_articles"]
        my_collection = my_database["fox_com_articles"]
        return my_collection
