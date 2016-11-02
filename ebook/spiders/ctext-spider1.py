import scrapy
from ebook import items
from ebook.ItemLoaders.ctext_article_loader import CTextArticleLoader

class CTextSpider(scrapy.Spider):
	name = 'ctext-spider1'
	start_urls = ['http://ctext.org/zh']

	def parse(self, response):
		menu = response.xpath('//div[@id="menu"]')
		catlink1 = menu.xpath('div[1]/a')
		catlink2 = menu.xpath('div[2]/a')
		
		catlist = [catlink1]

		for catlink in catlist:
			link = catlink.css('::attr(href)').extract_first()
			# catname = catlink.css('::text').extract_first()

			if link is not None:
				link = response.urljoin(link)
				yield scrapy.Request(link, callback=self.parse_category)

	def parse_category(self, response):
		en_category = response.url.split('/')[-2]

		if en_category != 'pre-qin-and-han':
			return

		# menu = response.xpath('//div[@id="menu"]')
		# xpath = 'div[contains(@class, "menuitem")]/a[contains(@href, "' + en_category + '")]'
		# catlink = menu.xpath(xpath)
		# cn_category = catlink.css('::text').extract_first()

		xpath = '//div[@id="menu"]/div[contains(@class, "menuitem")]/a[contains(@href, "%s")]/parent::div/following-sibling::div[1]/preceding-sibling::span[preceding-sibling::div/a[contains(@href, "%s")]]/a'
		for subcat in response.xpath(xpath % (en_category, en_category)):
			link = subcat.css('::attr(href)').extract_first()
			catname = subcat.css('::text').extract_first()
			
			if link is not None:
				link = response.urljoin(link)
				yield scrapy.Request(link, callback=self.parse_subcat)

	def parse_subcat(self, response):
		en_subcat = response.url.split('/')[-2]

		if en_subcat != 'confucianism':
			return

		xpath = '//div[@id="menu"]//a[contains(@href, "%s")]/following-sibling::span[1]/a'
		for book in response.xpath(xpath % en_subcat):
			link = book.css('::attr(href)').extract_first()
			bookname = book.css('::text').extract_first()

			if link is not None:
				link = response.urljoin(link)
				yield scrapy.Request(link, callback=self.parse_book)

	def parse_book(self, response):
		en_book = response.url.split('/')[-2]

		if en_book != 'analects':
			return

		xpath = '//div[@id="content2"]/a'
		for article in response.xpath(xpath):
			link = article.css('::attr(href)').extract_first()
			artname = article.css('::text').extract_first()

			if link is not None:
				link = response.urljoin(link)
				yield scrapy.Request(link, callback=self.parse_article)

	def parse_article(self, response):
		en_title = response.url.split('/')[-2]
		xpath = '//div[@id="content"]//span[@itemscope][@itemtype][%d]/a'
		category = response.xpath(xpath % 1).xpath('span/text()').extract_first()
		category_url = response.xpath(xpath % 1).xpath('@href').extract_first()
		en_category = category_url.split('/')[-2]
		sub_category = response.xpath(xpath % 2).xpath('span/text()').extract_first()
		sub_category_url = response.xpath(xpath % 2).xpath('@href').extract_first()
		en_sub_category = sub_category_url.split('/')[-2]
		book = response.xpath(xpath % 3).xpath('span/text()').extract_first()
		book_url = response.xpath(xpath % 3).xpath('@href').extract_first()
		en_book = book_url.split('/')[-2]

		l = CTextArticleLoader(item=items.CTextArticle(), response=response)
		l.add_value('category', category)
		l.add_value('en_category', en_category)
		l.add_value('sub_category', sub_category)
		l.add_value('en_sub_category', en_sub_category)
		l.add_value('book', book)
		l.add_value('en_book', en_book)
		l.add_value('en_title', response.url.split('/')[-2])
		l.add_xpath('title', '//div[@id="content3"]//h2/text()')
		l.add_xpath('content', '//div[@id="content3"]/table[2]/tr/td[3]/text()')
		l.add_value('filename', '-'.join([en_category, en_sub_category, en_title]))
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