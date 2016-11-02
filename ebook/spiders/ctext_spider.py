import scrapy
from ebook import items
from ebook.ItemLoaders.ctext_article_loader import CTextArticleLoader

class CTextSpider(scrapy.Spider):
	name = 'ctext-spider'
	start_urls = ['http://ctext.org/analects/zh']

	def parse(self, response):
		for article_link in response.xpath('//div[@id="content2"]/a'):
			link = article_link.css('::attr(href)').extract_first()
			title = article_link.css('::text').extract_first()
			# yield {
			# 	'link': link,
			# 	'title': title
			# }
			if link is not None:
				link = response.urljoin(link)
				yield scrapy.Request(link, callback=self.parse_article)

	def parse_article(self, response):
		l = CTextArticleLoader(item=items.CTextArticle(), response=response)
		l.add_xpath('title', '//div[@id="content3"]//h2/text()')
		l.add_xpath('content', '//div[@id="content3"]/table[2]/tr/td[3]/text()')
		l.add_value('en_title', response.url.split('/')[-2])
		# add_* invoke input processor
		# l.add_xpath('name', '//div[@class="product_name"]')
		# l.add_xpath('name', '//div[@class="product_title"]')
		# l.add_xpath('price', '//p[@id="price"]')
		# l.add_css('stock', 'p#stock]')
		# l.add_value('last_updated', 'today') # you can also use literal values
		# nested loader
		# footer_loader = loader.nested_xpath('//footer')
		# footer_loader.add_xpath('social', 'a[@class = "social"]/@href')
		# footer_loader.add_xpath('email', 'a[@class = "email"]/@href')
		return l.load_item() # invoke output processor and return the populated item