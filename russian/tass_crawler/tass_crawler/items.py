# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field, Item


class TassCrawlerItem(Item):
    tass_article_id = Field()
    date = Field()
    link = Field()
    title = Field()
    subtitle = Field()
    article_body = Field()
    downloaded_at = Field()
