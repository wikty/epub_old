# -*- coding: utf-8 -*-

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity
from w3lib.html import remove_tags, remove_tags_with_content

def drop_empty_processor_in(data):
	data = data.strip()
	return data if data else None

def remove_title_tag_processor_in(data):
	return data.strip('》《')

def common_processor_in(data):
	return data

class CTextArticleLoader(ItemLoader):
	# And you can also declare a default input/output processors using
	# the ItemLoader.default_input_processor and 
	# ItemLoader.default_output_processor attributes.
	
	#default_output_processor = TakeFirst()

	article_id_in = MapCompose(common_processor_in)
	article_id_out = TakeFirst()
	category_in = MapCompose(common_processor_in)
	category_out = Join()
	en_category_in = MapCompose(common_processor_in)
	en_category_out = Join()
	sub_category_in = MapCompose(common_processor_in)
	sub_category_out = Join()
	en_sub_category_in = MapCompose(common_processor_in)
	en_sub_category_out = Join()
	book_in = MapCompose(common_processor_in)
	book_out = Join()
	en_book_in = MapCompose(common_processor_in)
	en_book_out = Join()
	en_title_in = MapCompose(common_processor_in)
	en_title_out = Join()
	title_in = MapCompose(drop_empty_processor_in, remove_title_tag_processor_in)
	title_out = Join()
	content_in = MapCompose(drop_empty_processor_in)
	#content_out = Join(separator='\n')
	mcontent_in = MapCompose(drop_empty_processor_in)