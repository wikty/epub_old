from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity

def title_processor_in(data):
	return ''.join([item.strip() for item in data])

def content_processor_in(data):
	return data.strip() if data.strip() else None

def common_processor_in(data):
	return data

class CTextArticleLoader(ItemLoader):
	# And you can also declare a default input/output processors using
	# the ItemLoader.default_input_processor and 
	# ItemLoader.default_output_processor attributes.
	
	#default_output_processor = TakeFirst()

	category = MapCompose(common_processor_in)
	en_category = MapCompose(common_processor_in)
	sub_category = MapCompose(common_processor_in)
	en_sub_category = MapCompose(common_processor_in)
	book = MapCompose(common_processor_in)
	en_book = MapCompose(common_processor_in)
	en_title_in = MapCompose(common_processor_in)
	title_in = MapCompose(title_processor_in)
	content_in = MapCompose(content_processor_in)

	#content_out = Join(separator='\n')
	
	# input processors are declared using the _in suffix
	
	# name_in = MapCompose(unicode.title)
	
	# output processors are declared using the _out suffix
	
	# name_out = Join()
	# price_in = MapCompose(unicode.strip)