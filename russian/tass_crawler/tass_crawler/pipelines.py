# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymongo


class ArticleValidationPipeline:
    def process_item(self, item, _):
        adapter = ItemAdapter(item)
        if not (isinstance(adapter.get('tass_article_id'), str) and len(adapter.get('tass_article_id').strip()) > 0):
            raise DropItem('invalid id: ' + str(adapter.get('tass_article_id')))
        if not (isinstance(adapter.get('title'), str) and len(adapter.get('title').strip()) > 0):
            raise DropItem('invalid title: ' + str(adapter.get('title')))
        # Some articles don't have an abstract or a subtitle, hence
        # aggressively validating for having these attributes should
        # not be necessary
        if not (isinstance(adapter.get('subtitle'), str) or adapter.get('subtitle') is None):
            raise DropItem('invalid subtitle: ' + str(adapter.get('subtitle')))
        return item


class ArticleFormatPipeline:
    def process_item(self, item, _):
        adapter = ItemAdapter(item)
        adapter['tass_article_id'] = adapter.get('tass_article_id').strip().strip('"')
        adapter['tass_article_id'] = adapter.get('tass_article_id').strip().strip('"')
        if isinstance(adapter['subtitle'], str):
            adapter['subtitle'] = adapter.get('subtitle').strip().strip('"')
        if isinstance(adapter['article_body'], str):
            adapter['article_body'] = adapter.get('article_body').strip().strip('"')
        return adapter.item


class ArticleMongoDBPipeline:

    def __init__(self, mongo_uri, mongo_db, mongo_col):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_col = "tass_com_articles"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_col=crawler.settings.get('MONGO_COL'),
        )

    def open_spider(self, _):
        self.client = pymongo.MongoClient(self.mongo_uri, username='root', password='root')
        self.db = self.client[self.mongo_db]
        self.col = self.db["tass_com_articles"]
        #self.col.create_index('tass_article_id', unique=True)

    def close_spider(self, _):

        self.client.close()

    def process_item(self, item, _):
        if self.col.find_one({"tass_article_id": item.get('tass_article_id')}) is not None:
            self.col.update_one({'tass_article_id': item.get('tass_article_id')}, {'$set': {
                'date': item.get('date'),
                'link': item.get('link'),
                'title': item.get('title'),
                'subtitle': item.get('subtitle'),
                'article_body': item.get('article_body'),
                'downloaded_at': item.get('downloaded_at')
            }})
        else:
            self.col.insert_one(dict(item))
        return item
