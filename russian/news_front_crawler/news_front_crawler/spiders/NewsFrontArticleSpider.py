from datetime import datetime
import scrapy
from pymongo.errors import DuplicateKeyError
from scrapy import Request
from mongo_connection.MongoConnector import access_mongo_return_entries, access_mongo_return_collection


class NewsFrontSpider(scrapy.Spider):
    name = 'NewsFrontArticleSpider'
    allowed_domains = ['en.news-front.info']
    client_name = "russian_news_articles"
    collection_name_link_store = "news_front_com_links"
    collection_name_article_store = "news_front_com_articles"

    def start_requests(self):
        entries = access_mongo_return_entries(self.client_name, self.collection_name_link_store)
        for entry in entries:
            url = entry["link"]
            yield Request(url, callback=self.parse,
                          meta={"news_front_id": entry["news_front_article_id"],
                                "date": entry["date"],
                                "link": entry["link"]
                                })

    def parse(self, response, **kwargs):
        article_title = response.xpath("//*[@class='entry-title']/text()").get()
        article_subtitle = response.xpath("//*[@class='article__content']//span/text()").get()
        article_body_list = response.xpath("//*[@class='article__content']//span/text()").getall()
        article_body_list = article_body_list[1:]
        article_body = " ".join(article_body_list)
        news_front_id = response.meta["news_front_id"]
        link = response.meta["link"]
        date = response.meta["date"]

        downloaded_at = datetime.now()
        downloaded_at = int(round(downloaded_at.timestamp()))
        article = {
            "news_front_article_id": news_front_id,
            "date": date,
            "link": link,
            "title": article_title.replace("\n", "").replace("\t", "").strip(),
            "subtitle": article_subtitle.replace("\n", "").replace("\t", "").strip(),
            "article_body": article_body.replace("\n", "").replace("\t", "").strip(),
            "downloaded_at": downloaded_at
        }

        article_collection_pravda = access_mongo_return_collection(self.client_name, self.collection_name_article_store)
        try:
            article_collection_pravda.insert_one(article)
        except DuplicateKeyError:
            print("duplicate was not inserted")

        yield article