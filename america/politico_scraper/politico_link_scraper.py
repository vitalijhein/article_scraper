import sys
from datetime import datetime

import pymongo
import requests
from bs4 import BeautifulSoup, Tag
from pymongo.errors import DuplicateKeyError
import dateutil.parser as dp
import re


def main():
    offset = 0

    politico_json_wire = access_api(offset)
    # soup = BeautifulSoup(news_front_response, features="lxml")
    entries, my_collection = access_mongo_links()
    test = store_links_mongo(politico_json_wire, my_collection)

    while test != False:
        offset += 1
        # print(var + 1)
        politico_json_new = access_api(offset)
        test = store_links_mongo(politico_json_new, my_collection)

    entries, my_collection = access_mongo_links()
    for entry in entries:
        url = entry["link"]
        print(url)
        politico_response = access_api_articles(url)
        my_collection = access_mongo_articles()
        store_articles_mongo(entry, politico_response, my_collection)


def access_api(offset):
    url = f"https://www.politico.com/news/ukraine/{offset}"
    #print(url)

    payload = {}
    headers = {
        'Referer': 'https://www.politico.com/news/ukraine',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        'Cookie': '__cf_bm=NKumnCneViaQ1qQmKaxoUYLr3YuqhyNzLo_Z1THjiEQ-1658416901-0-Aap6mgVgn1nIQ4kD4RLZSSrteAlZyfKpl70a5QGf/VrfBUkdisJPT/Opa5MMwFuYxD63QoCdztgyxT9glCpMz8M=; __cfruid=1c036d6987127fd1705da61d2b46b4cb442fedc0-1658416901'
    }
    politico_response = requests.request("GET", url, headers=headers, data=payload)

    return politico_response.text


def access_api_articles(url):
    payload = {}
    headers = {
        'Cookie': '__cf_bm=ZpU0NdOtyvn4fkFcqG1iUsULjVmz0LyKzAFgqYX1kuc-1658736519-0-AY7P0PkOBmx43SLV2h6d/DYK6BPAKEEP2+MEMnhiybxiBt6aNE8sRFgUhbIoPmYHec+1gTv6d2Va3mmQhrnVqHg=; __cfruid=0f225baa4a30fe3b060405ed77305911eec5882c-1658736519'
    }

    politico_response = requests.request("GET", url, headers=headers, data=payload)

    return politico_response.text


def access_mongo_links():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/', username="root", password="root")
    mydatabase = myclient["american_news_articles"]
    my_collection = mydatabase["politico_com_links"]
    # print(mycollection)
    entries = my_collection.find()
    return entries, my_collection


def access_mongo_articles():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/', username="root", password="root")
    mydatabase = myclient["american_news_articles"]
    my_collection = mydatabase["politico_com_articles"]
    # print(mycollection)
    return my_collection


def store_links_mongo(politico_response, mycollection):
    soup = BeautifulSoup(politico_response, features="lxml")
    list_contents = soup.findAll('article', {'class': 'story-frag format-m'})
    # list_contents = soup.findAll('p', {'class': 'category'})
    fallback_date = ""
    for contens in list_contents:
        link = contens.find("header").find("h3").find("a").get("href")
        forbidden = ["/video", "/gallery"]
        print(link)
        if "/news" not in link:
            print("forbidden: "+link)
            continue

        id = re.search("\d{6,8}", link)
        title = contens.find("header").find("h3").find("a").get_text()
        try:
            date = contens.find('p', {'class': 'timestamp'}).find("time").get_text()
        except AttributeError:
            date = fallback_date

        fallback_date = date
        parsed_date = dp.parse(date)
        date_stamp = str(parsed_date.timestamp()).split(".")[0]
        stop_date = 1645660801

        article = {
            "politico_article_id": id.group(),
            "date": date_stamp,
            "title": title,
            "link": link
        }
        #print(article)
        if int(date_stamp) >= int(stop_date):
            try:
                mycollection.insert_one(article)
            except DuplicateKeyError:
                #print("duplicate was not inserted")
                continue
        else:
            return False
    return True


def store_articles_mongo(entry, politico_response, mycollection):
    soup = BeautifulSoup(politico_response, features="lxml")
    list_contents = soup.findAll('main', {'id': 'main'})

    for politico_article in list_contents:
        article_title = politico_article.find('h2', {'class': 'headline'}).get_text()
        article_subtitle = politico_article.find('p', {'class': 'dek'}).get_text()
        article_body = politico_article.findAll('p', {'class': 'story-text__paragraph'})
        body = ""
        for paragraph in article_body:
            if len(paragraph) == 1:
                body += " " + paragraph.get_text()
            if len(paragraph) > 1:
                for tags in paragraph.contents:
                    body += tags.get_text()

        downloaded_at = datetime.now()
        downloaded_at = int(round(downloaded_at.timestamp()))
        article = {
            "politico_article_id": entry["politico_article_id"],
            "date": entry["date"],
            "link": entry["link"],
            "title": article_title.replace("\n", "").replace("\t", "").strip(),
            "subtitle": article_subtitle.replace("\n", "").replace("\t", "").strip(),
            "article_body": body.replace("\n", "").replace("\t", "").strip(),
            "downloaded_at": downloaded_at
        }
        try:
            mycollection.insert_one(article)
        except DuplicateKeyError:
            #print("duplicate was not inserted")
            continue


main()
