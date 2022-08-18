import scrapy
from pymongo.errors import DuplicateKeyError
from scrapy import Request
from datetime import datetime
from mongo_connection.MongoConnector import access_mongo_return_entries, access_mongo_return_collection

class CnnArticleSpider(scrapy.Spider):
    name = 'CnnArticleSpider'
    allowed_domains = ['edition.cnn.de']
    start_urls = ['http://edition.cnn.de/']
    client_name = "american_news_articles"
    collection_name_link_store = "cnn_com_links"
    collection_name_article_store = "cnn_com_articles"

    def start_requests(self):
        entries = access_mongo_return_entries(self.client_name, self.collection_name_link_store)
        for entry in entries:
            url = entry["link"]
            url = url.replace("www.cnnnews", "edition.cnn")
            yield Request(url, callback=self.parse,
                          meta={"cnn_article_id": entry["cnn_article_id"],
                                "date": entry["date"],
                                "link": entry["link"]
                                })

    def parse(self, response, **kwargs):
        article_title = response.xpath("//h1/text()").get()
        #article_subtitle = response.xpath("//*[@class='zn-body__paragraph speakable']//*//text()").get()
        article_body_list = response.xpath("//*[@class='zn-body__paragraph']//text()").getall()
        article_body = " ".join(article_body_list)
        cnn_article_id = response.meta["cnn_article_id"]
        link = response.meta["link"]
        url = link.replace("www.cnnnews", "edition.cnn")

        date = response.meta["date"]
        downloaded_at = datetime.now()
        downloaded_at = int(round(downloaded_at.timestamp()))
        article = {
            "cnn_article_id": cnn_article_id,
            "date": date,
            "link": url,
            "title": article_title.replace("\n", "").replace("\t", "").strip(),
            "article_body": article_body.replace("\n", "").replace("\t", "").strip(),
            "downloaded_at": downloaded_at
        }
        print(article)
        article_collection_abc = access_mongo_return_collection(self.client_name, self.collection_name_article_store)
        try:
            article_collection_abc.insert_one(article)
        except DuplicateKeyError:
            print("duplicate was not inserted")
