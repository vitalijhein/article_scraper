import scrapy
from pymongo.errors import DuplicateKeyError
from scrapy import Request
from datetime import datetime
from mongo_connection.MongoConnector import access_mongo_return_entries, access_mongo_return_collection


class TassArticleSpider(scrapy.Spider):
    name = 'TassArticleSpider'
    allowed_domains = ['tass.com']
    client_name = "russian_news_articles"
    collection_name_link_store = "tass_com_link"
    collection_name_article_store = "tass_com_articles"
    headers = {
        "Cookie": "newsListCounter=41; _ym_isad=2; _ym_d=1657542446; _ym_uid=1657542446508962937; __lhash_=61d34115cf5ffcbd563bfa5b2ed1facf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Host": "tass.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
        "Accept-Language": "de-DE,de;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    def start_requests(self):
        entries = access_mongo_return_entries(self.client_name, self.collection_name_link_store)
        for entry in entries:
            url = entry["link"]
            yield Request(url, callback=self.parse, headers=self.headers,
                          meta={"tass_article_id": entry["tass_article_id"],
                                "date": entry["date"],
                                "link": entry["link"]
                                })

    def parse(self, response, **kwargs):
        article_title = response.xpath("//*[@class='news-header__title']/text()").get()
        article_subtitle = response.xpath("//*[@class='news-header__lead']/text()").get()
        article_body_list = response.xpath("//*[@class='text-block']//p/text()").getall()
        article_body = " ".join(article_body_list)
        tass_article_id = response.meta["tass_article_id"]
        link = response.meta["link"]
        date = response.meta["date"]
        downloaded_at = datetime.now()
        downloaded_at = int(round(downloaded_at.timestamp()))
        article = {
            "tass_article_id": tass_article_id,
            "date": date,
            "link": link,
            "title": article_title.replace("\n", "").replace("\t", "").strip(),
            "subtitle": article_subtitle.replace("\n", "").replace("\t", "").strip(),
            "article_body": article_body.replace("\n", "").replace("\t", "").strip(),
            "downloaded_at": downloaded_at
        }

        article_collection_tass = access_mongo_return_collection(self.client_name, self.collection_name_article_store)
        try:
            article_collection_tass.insert_one(article)
        except DuplicateKeyError:
            print("duplicate was not inserted")

        yield article
