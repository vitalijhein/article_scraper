# Spiegel Crawler
A python `scrapy` based crawler that scrapes through the [international section of spiegel](https://www.spiegel.de/international/) and drops the result in a `mongodb` database.

## Requirements
- [Install `docker`](https://docs.docker.com/engine/install/)
- [Install `docker-compose`](https://docs.docker.com/compose/install/)
- Ensure port `27017` is open and not used by other processes

## Quick Start
- open a terminal and clone this repository
```
git clone https://github.com/Logician724/spiegel-crawler.git 
```
- open the repository directory. 
```
cd spiegel-crawler
```
- run `docker-compose` in detached mode
```
docker-compose up --build -d  
```
- to continuously read the logs, type into your terminal in your repository directory[Optional]
```
docker-compose logs -f
```
- to stop the crawler, type into your terminal in your repository directory
```
docker-compose down
```

## Overview
The script uses the scrapy library to crawl through the `spiegel` international section.

### Python Modules
The most important modules are
- `spiegel_spider.py` : This module houses the crawler logic for extracting info from the website.
- `pipelines.py` : This module has a few pipelines that process the extracted information from the crawler.

    - `ArticleValidationPipeline` Runs basic validation on datatypes and lengths resulting from extraction.
    - `ArticleFormatPipeline` Mostly strips data points from all leading and trailing white spaces.
    - `ArticleMongoDBPipeline` This houses the logic that runs the duplicate check and either inserts a new document or updates one in the database.

### Docker Containers
There are 2 containers in the system

- `article_scraper` container: Run the [cron](https://wiki.debian.org/cron) process that schedules the crawler script to run

    - Once on script initialization for the purpose of testing.
    - Once every 15 minutes. speficially on the 0th, 15th, 30th, and 45th minute of each hour.
- `mongo` container: Runs the mongodb database engine and listens for connections on port `27017` 

## Crawl Result Set

There are a few ways to access the crawl result set, the fastest of which is as follows.
- Make sure the crawler is still running by inspecting the result of
```
docker container ls
```
In case you find a container with the name `mongo` similar to the following example output, then the crawler is still running.
```
CONTAINER ID   IMAGE                     COMMAND                  CREATED          STATUS          PORTS                                           NAMES
98bb44c05822   article_scraper_crawler   "./entrypoint.sh"        32 minutes ago   Up 32 minutes                                                   spiegel-crawler
65d71518b49a   mongo                     "docker-entrypoint.s…"   32 minutes ago   Up 32 minutes   0.0.0.0:27017->27017/tcp, :::27017->27017/tcp   mongo
```
- Open the mongo shell
```
docker exec -it mongo mongo -u root -p root
```
- Switch to the crawler database
```
use crawler
```
- Return the crawler result set
```
db.crawler.find()
```
- A limited sample of the result set will be returned. As instructed you can type `it` for more documents.

- You can filter your query result by following the [mongodb find api docs](https://docs.mongodb.com/manual/reference/method/db.collection.find/). e.g. to return all documents that contain the word `Free` in their abstract.

```
db.crawler.find({abstract: {$regex: "Free"}})
```
- Once done type `exit` to leave the mongo shell.

### Note
The instructions above assume the default configuration in `env.default` has not been modified. In case of modification, you will have to change your commands accordingly.

## Customization

The repository uses an `env.default` file that houses the default configuration for the respository for quick startup. The following variables can be changed or added in `.env.default` file to make them customizable

- `MONGO_URI` : used by the crawler to connect to the correct database. The database connection string format follows the [standard mongodb format](https://docs.mongodb.com/manual/reference/connection-string/).

- `MONGO_DB` : used by the crawler to configure the name of the database the crawler uses to dump the crawl run result. The default name is `crawler`.

- `MONGO_COL` : used by the crawler to configure the name of the collection the crawler uses to dump the crawl run result inside the database specified by `MONGO_DB`. The default collection name is `crawler`.

- `MONGO_INITDB_ROOT_USERNAME` : used by the `mongo` image to configure the `mongodb` root username.

- `MONGO_INITDB_ROOT_PASSWORD` : used by the `mongo` image to configure the `mongodb` root password.

- For more info on environment customization for `mongo` image, check [here](https://hub.docker.com/_/mongo/)
# article_scraper
