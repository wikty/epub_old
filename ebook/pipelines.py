# -*- coding: utf-8 -*-
import os
import errno
import json
import codecs

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class ExamplePipeline(object):
    factor = 1.5
    collection_name = 'mongo_scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        # mongo database args
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        # record id
        self.ids_seen = set()

    def open_spider(self, spider):
        # open json file
        self.f = open('example_items.jl', 'wb')
        
        # connect mongo database server
        # import pymongo
        # self.client = pymongo.MongoClient(self.mongo_uri)
        # self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        # close json file
        self.f.close()

        # close mongo connection
        self.client.close()

    # called to create a pipeline instance from a Crawler, 
    # so this class method must return a pipeline instance.
    # crawl object provides access to all scrapy core components like settings
    @staticmethod
    def from_crawl(cls, crawler):
        # return a instance of pipeline
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def process_item(self, item, spider):
        # modify&drop item
        if item['price']:
            if item['price_exculdes_vat']:
                item['price'] *= self.factor
            return item
        else:
            raise scrapy.exceptions.DropItem('missing price field')

        # stores items from all spiders into a single json file
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.f.write(line)
        return item

        # stores items from all spiders into mongo database
        self.db[self.collection_name].insert(dict(item))
        return item

        # drop duplicate items
        if item['id'] in self.ids_seen:
            raise scrapy.exceptions.DropItem('duplicate item')
        else:
            self.ids_seen.add(item['id'])
            return item

class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = codecs.open('articles.jl', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        if self.file:
            self.file.close()

class StoreArticlesInBookPipeline(object):

    def __init__(self):
        self.datadir = 'data'
        self.fd = {}
        self.fd['__books'] = codecs.open('books.jl', 'a+', encoding='utf-8')
        self.books = self.fd['__books']

    def process_item(self, item, spider):
        en_book = dict(item).get('en_book', None)
        if en_book is not None:
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            if en_book not in self.fd:
                book_filename = os.sep.join([self.datadir, '%s.jl' % en_book])
                self.fd[en_book] = codecs.open(book_filename, 'w', encoding='utf-8')
                self.books.write(json.dumps({
                    'type': dict(item).get('book_type', ''),
                    'ch_name': dict(item).get('book', ''),
                    'en_name': dict(item).get('en_book', '')
                }, ensure_ascii=False) + "\n")

            self.fd[en_book].write(line)

        return item

    def spider_closed(self, spider):
        for fname in self.fd:
            if self.fd[fname]:
                self.fd[fname].close()