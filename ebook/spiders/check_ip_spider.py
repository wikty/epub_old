import scrapy


class CheckIpSpider(scrapy.Spider):
	name = 'check-ip'

	start_urls = ['http://ip.42.pl/raw', 'https://www.atagar.com/echo.php']

	def parse(self, response):
		print(response.body)