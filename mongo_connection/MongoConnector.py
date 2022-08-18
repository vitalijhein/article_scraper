import pymongo


def access_mongo_return_entries(client_name, collection_name):
    my_client = pymongo.MongoClient('mongodb://localhost:27017/', username="root", password="root")
    my_database = my_client[client_name]
    my_collection = my_database[collection_name]
    entries = my_collection.find()

    return entries


def access_mongo_return_collection(client_name, collection_name):
    my_client = pymongo.MongoClient('mongodb://localhost:27017/', username="root", password="root")
    my_database = my_client[client_name]
    my_collection = my_database[collection_name]
    return my_collection
