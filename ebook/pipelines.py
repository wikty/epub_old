# -*- coding: utf-8 -*-
import os
import errno
import json
import codecs

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = codecs.open('articles.jl', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()

class StoreArticlesInBook(object):

    def __init__(self):
        self.fd = {}

    def process_item(self, item, spider):
        en_book = dict(item).get('en_book', None)
        if en_book is not None:
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            if en_book not in self.fd:
                self.fd[en_book] = codecs.open('.'.join([en_book, 'jl']), 'w', encoding='utf-8')
            self.fd[en_book].write(line)

        return item

    def spider_closed(self, spider):
        for fname in self.fd:
            self.fd[fname].close()

class EbookPipeline(object):
    def process_item(self, item, spider):
        return item
