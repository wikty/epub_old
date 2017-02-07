# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
# from scrapy.loader.processors import Join, MapCompose, TakeFirst
# from w3lib.html import remove_tags

class EbookItem(scrapy.Item):
    pass

class CTextArticleItem(scrapy.Item):
	# title = scrapy.Field(serializer=title_serializer)
	# content = scrapy.Field(serializer=content_serializer)

	url = scrapy.Field()
	article_id = scrapy.Field()
	# category = scrapy.Field()
	# en_category = scrapy.Field()
	# sub_category = scrapy.Field()
	# en_sub_category = scrapy.Field()
	book = scrapy.Field()
	en_book = scrapy.Field()
	en_title = scrapy.Field()
	title = scrapy.Field()
	content = scrapy.Field()
	comment = scrapy.Field()
	#filename = scrapy.Field()
	book_type = scrapy.Field()

# class CTextBookInfoItem(scrapy.Item):
# 	name = scrapy.Field()
# 	en_name = scrapy.Field()
# 	category = scrapy.Field()
# 	en_category = scrapy.Field()
# 	url = scrapy.Field()
# 	# [{'name', 'en_name', 'url'}]
# 	article_list = scrapy.Field()