import scrapy

class ProxyCheckSpider(scrapy.Spider):
	name = 'proxy-check-spider'

	start_urls = ['http://ip.42.pl/raw']

	def parse(self, response):
		print(response.xpath('//text()').extract_first())