import codecs, json
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class CTextMenuSpiderTest(scrapy.Spider):
	name = 'test-ctext-menu'
	start_urls = ['http://ctext.org/zh']

	def start_requests(self):
		for url in self.start_urls:
			yield scrapy.Request(
				url,
				callback=self.parse,
				errback=self.errback,
				dont_filter=True)
		self.f = codecs.open('booklist1.jl', 'a+', encoding='utf-8')

	def closed(self, reason):
		self.f.close()

	def parse(self, response):
		xpath = '//div[@id="menu"]/div[contains(@class, "listhead")][position() < 3]/a'
		for sup_category in [response.xpath(xpath)[0]]:
			url = sup_category.xpath('@href').extract_first()
			name = sup_category.xpath('text()').extract_first()
			xpath = 'parent::div/following-sibling::div[1]/preceding-sibling::span[contains(@class, "menuitem")][preceding-sibling::div/a[contains(@href, "{url}")]]'.format(url=url)
			if url is None:
				self.logger.error('sup category is empty')
			else:
				self.logger.info('sup category: {}'.format(name))
				self.logger.info('sup category url: {}'.format(url))

			for category in sup_category.xpath(xpath):
				self.logger.info('category: {}'.format(category.xpath('a/text()').extract_first()))
				self.logger.info('category url: {}'.format(category.xpath('a/@href').extract_first()))
				
				for book in category.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
					bookinfo = {
						'url': response.urljoin(book.xpath('@href').extract_first()),
						'name': book.xpath('text()').extract_first(),
						'category': category.xpath('a/text()').extract_first(),
						'articles': []
					}
					if bookinfo['url'] is None:
						self.logger.error('book is empty')
					else:
						self.logger.info('book: {}'.format(bookinfo['name']))
						self.logger.info('book url: {}'.format(bookinfo['url']))
						request = scrapy.Request(bookinfo['url'], callback=self.parse_book)
						request.meta['bookinfo'] = bookinfo
						yield request

	def parse_book(self, response):
		url = '/'.join(response.url.split('/')[-2:])
		article = response.xpath('//div[@id="menu"]//span[contains(@class, "subcontents")]/a[contains(@href, "{url}")]'.format(url=url))
		xpath = '//div[@id="menu"]//span[contains(@class, "subcontents")][preceding-sibling::a[1][contains(@href, "{url}")]]'.format(url=url)
		menuitems = response.xpath(xpath).xpath('a[contains(@class, "menuitem")]')
		containers = response.xpath(xpath).xpath('span[contains(@class, "container")]')
		
		if article:
			# book has single article
			self.process_article(response, article, '', '')
		elif menuitems:
			# book has no chapter
			for menuitem in menuitems:
				self.process_article(response, menuitem, '', '')
		elif containers:
			# book has chapter
			for container in containers:
				chapter = container.xpath('a/text()').extract_first()
				chapter_url = response.urljoin(container.xpath('a/@href').extract_first())
				for menuitem in container.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
					self.process_article(response, menuitem, chapter, chapter_url)
		else:
			self.logger.error('unknow page structure: {}'.format(response.url))
		line = json.dumps(response.meta['bookinfo'], ensure_ascii=False) + "\n"
		self.f.write(line)
		self.logger.info('write book into file: {}'.format(response.meta['bookinfo']['name']))

	def process_article(self, response, link, chapter, chapter_url):
		articleinfo = {
			'url': response.urljoin(link.xpath('@href').extract_first()),
			'name': link.xpath('text()').extract_first(),
			'chapter': chapter,
			'chapter_url': chapter_url
		}
		if articleinfo['url'] is None:
			self.logger.error('article is empty')
		response.meta['bookinfo']['articles'].append(articleinfo)	

	def errback(self, failure):
		# log all failures
		self.logger.error(repr(failure))

		# in case you want to do something special for some errors,
		# you may need the failure's type:

		if failure.check(HttpError):
		    # these exceptions come from HttpError spider middleware
		    # you can get the non-200 response
		    response = failure.value.response
		    self.logger.error('HttpError on %s', response.url)

		elif failure.check(DNSLookupError):
		    # this is the original request
		    request = failure.request
		    self.logger.error('DNSLookupError on %s', request.url)

		elif failure.check(TimeoutError, TCPTimedOutError):
		    request = failure.request
		    self.logger.error('TimeoutError on %s', request.url)

	def parse1(self, response):
		menu = response.xpath('//div[@id="menu"]')
		link1 = menu.xpath('div[contains(@class, "listhead")][1]/a')
		link2 = menu.xpath('div[contains(@class, "listhead")][2]/a')

		for link in [link1, link2]:
			url = link.css('::attr(href)').extract_first()
			name = link.css('::text').extract_first()
			absurl = response.urljoin(url)
			if url is None or name is None:
				raise Exception('bad link')
			
			self.menu['root']['children'][absurl] = {
				'url': url,
				'name': name
			}
			xpath = 'parent::div/following-sibling::div[1]/preceding-sibling::span[contains(@class, "menuitem")][preceding-sibling::div/a[contains(@href, "{listhead}")]]'.format(listhead=url)
			self.menu['root']['children'][absurl]['children'] = self.process_category(response, link.xpath(xpath))

			print(self.menu)

	def process_category(self, response, categories):
		parent = {}
		for category in categories:
			url = category.xpath('a/@href').extract_first()
			name = category.xpath('a/text()').extract_first()
			absurl = response.urljoin(url)
			if url is None or name is None:
				raise Exception('bad link')

			parent[absurl] = {
				'url': url,
				'name': name
			}
			xpath = 'span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'
			parent[absurl]['children'] = self.process_book(response, category.xpath(xpath))
		return parent

	def process_book(self, response, books):
		parent = {}
		for book in books:
			url = book.xpath('@href').extract_first()
			name = book.xpath('text()').extract_first()
			absurl = response.urljoin(url)
			if url is None or name is None:
				raise Exception('bad url')
			parent[absurl] = {
				'url': url,
				'name': name,
				'children': {}
			}
			page = scrapy.Selector(text=urllib.request.urlopen(absurl).read().decode('utf-8'))
			xpath = '//div[@id="menu"]//span[contains(@class, "subcontents")][preceding-sibling::a[1][contains(@href, "{url}")]]'.format(url=url)
			menuitems = page.xpath(xpath+'/a[contains(@class, "menuitem")]')
			menuitem_containers = page.xpath(xpath+'/span[contains(@class, "menuitem")][contains(@class, "menuitem")]')
			if menuitems is not None:
				for menuitem in menuitems:
					url = menuitem.xpath('@href').extract_first()
					name = menuitem.xpath('text()').extract_first()
					if url is None or name is None:
						raise Exception('bad url')
					parent[absurl]['children'][response.urljoin(url)] = {
						'url': url,
						'name': name,
						'children': None
					}
			elif menuitem_containers is not None:
				for container in menuitem_containers:
					url =  container.xpath('a/@href').extract_first()
					name = container.xpath('a/text()').extract_first()
					if url is None or name is None:
						raise Exception('bad url')
					parent[absurl]['children'][response.urljoin(url)] = {
						'url': url,
						'name': name,
						'children': {}
					}
					temp = parent[absurl]['children'][response.urljoin(url)]['children']
					for menuitem in container.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
						url = menuitem.xpath('@href').extract_first()
						name = menuitem.xpath('text()').extract_first()
						if url is None or name is None:
							raise Exception('bad url')
						temp[response.urljoin(url)] = {
							'url': url,
							'name': name,
							'children': None
						}
		return parent


				




