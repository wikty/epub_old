import scrapy


class ProxyCheckSpider(scrapy.Spider):
	name = 'proxy-test-spider'

	start_urls = ['http://ip.42.pl/raw']

	def parse(self, response):
		print(response.body)