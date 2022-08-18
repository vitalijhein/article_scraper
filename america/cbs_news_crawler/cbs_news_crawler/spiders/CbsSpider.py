import scrapy
from pymongo.errors import DuplicateKeyError
from scrapy import Request
from datetime import datetime
from mongo_connection.MongoConnector import access_mongo_return_entries, access_mongo_return_collection


class CbsSpider(scrapy.Spider):
    name = 'CbsSpider'
    allowed_domains = ['cbsnews.com']
    start_urls = ['http://cbsnews.com/']
    client_name = "american_news_articles"
    collection_name_link_store = "cbs_com_links"
    collection_name_article_store = "cbs_com_articles"

    def start_requests(self):
        entries = access_mongo_return_entries(self.client_name, self.collection_name_link_store)
        for entry in entries:
            url = entry["link"]
            yield Request(url, callback=self.parse,
                          meta={"cbs_article_id": entry["cbs_article_id"],
                                "date": entry["date"],
                                "link": entry["link"]
                                })

    def parse(self, response, **kwargs):
        article_title = response.xpath("//h1/text()").get()
        article_body_list = response.xpath("//*[@class='content__body']//p//text()").getall()
        if article_body_list is None:
            article_body_list = response.xpath(
                "//*[@class='content__post content__body content__post--intro post-update post-update--intro amp-live-list-item']//p//text()").getall()
        article_body = " ".join(article_body_list)
        cbs_article_id = response.xpath("//*[@class='content__high-wrapper ']/@data-sort-time").get()
        if cbs_article_id is None:
            cbs_article_id = response.xpath("//*[@class='content__high-wrapper ']/@data-sort-time").get()
        link = response.meta["link"]
        date = response.xpath(
            "//*[@class='content__post content__body content__post--intro post-update post-update--intro amp-live-list-item']/@data-sort-time").get()
        if date is None:
            date = response.xpath("//*[@class='content__high-wrapper ']/@data-sort-time").get()
        downloaded_at = datetime.now()
        downloaded_at = int(round(downloaded_at.timestamp()))
        article = {
            "cbs_article_id": cbs_article_id,
            "date": date,
            "link": link,
            "title": article_title.replace("\n", "").replace("\t", "").strip(),
            "article_body": article_body.replace("\n", "").replace("\t", "").strip(),
            "downloaded_at": downloaded_at
        }
        print(article)
        article_collection_cbs = access_mongo_return_collection(self.client_name, self.collection_name_article_store)
        try:
            article_collection_cbs.insert_one(article)
        except DuplicateKeyError:
            print("duplicate was not inserted")