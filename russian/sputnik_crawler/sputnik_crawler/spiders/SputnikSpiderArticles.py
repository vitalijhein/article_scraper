from datetime import datetime

import scrapy
from pymongo.errors import DuplicateKeyError
from scrapy import Request

from mongo_connection.MongoConnector import access_mongo_return_entries, access_mongo_return_collection


class SputnikSpider(scrapy.Spider):
    name = 'SputnikSpiderArticles'
    allowed_domains = ['sputniknews.com']
    start_urls = ['http://sputniknews.com/']
    client_name = "russian_news_articles"
    collection_name_link_store = "sputnik_com_links"
    collection_name_article_store = "sputnik_com_articles"

    def start_requests(self):
        entries = access_mongo_return_entries(self.client_name, self.collection_name_link_store)
        for entry in entries:
            url = entry["link"]
            yield Request(url, callback=self.parse,
                          meta={"sputnik_id": entry["sputnik_article_id"],
                                "link": entry["link"]
                                })

    def parse(self, response, **kwargs):
        article_title = response.xpath("//*[@class='article__title']/text()").get()
        article_subtitle = response.xpath("//*[@class='article__announce-text']/text()").get()
        article_body_list = response.xpath("//*[@class='article__text']//text()").getall()
        article_body = " ".join(article_body_list)
        sputnik_id = response.meta["sputnik_id"]
        link = response.meta["link"]
        date = response.xpath("//*[@class='convert-date']/@data-unixtime").get()

        downloaded_at = datetime.now()
        downloaded_at = int(round(downloaded_at.timestamp()))
        article = {
            "sputnik_article_id": sputnik_id,
            "date": date,
            "link": link,
            "title": article_title.replace("\n", "").replace("\t", "").strip(),
            "subtitle": article_subtitle.replace("\n", "").replace("\t", "").strip(),
            "article_body": article_body.replace("\n", "").replace("\t", "").strip(),
            "downloaded_at": downloaded_at
        }

        article_collection_sputnik = access_mongo_return_collection(self.client_name, self.collection_name_article_store)
        try:
            article_collection_sputnik.insert_one(article)
        except DuplicateKeyError:
            print("duplicate was not inserted")
