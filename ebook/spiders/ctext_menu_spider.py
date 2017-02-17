import re, urllib, codecs, json

import scrapy
from w3lib.html import remove_tags, remove_tags_with_content

from ebook import items
from ebook.item_loaders.ctext_article_loader import CTextArticleLoader


class CTextMenuSpider(scrapy.Spider):
	name = 'ctext-menu'
	start_urls = ['http://ctext.org/zh']

	booklist = []
	booknames = []

	menu = {
		'root': {
			'url': 'http://ctext.org/zh', 
			'name': 'ctext',
			'children': {}
		}
	}

	def parse(self, response):
		xpath = '//div[@id="menu"]/div[contains(@class, "listhead")][position() < 3]/a'
		for link in response.xpath(xpath):
			url = link.css('::attr(href)').extract_first()
			xpath = 'parent::div/following-sibling::div[1]/preceding-sibling::span[contains(@class, "menuitem")][preceding-sibling::div/a[contains(@href, "{url}")]]'.format(url=url)
			if url is None:
				raise Exception('bad link')
			for category in link.xpath(xpath):
				for book in category.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
					bookinfo = {
						'url': response.urljoin(book.xpath('@href').extract_first()),
						'name': book.xpath('text()').extract_first(),
						'category': category.xpath('a/text()').extract_first(),
						'articles': []
					}
					if bookinfo['url'] is None:
						raise Exception('bad book url')
					self.booknames.append(bookinfo['name'])
					self.booklist.append(bookinfo)
					request = scrapy.Request(bookinfo['url'], callback=self.parse_book)
					request.meta['articles'] = bookinfo['articles']
					yield request
		with codecs.open('booklist.jl', 'w', encoding='utf-8') as f:
			for bookinfo in self.booklist:
				line = json.dumps(bookinfo, ensure_ascii=False) + "\n"
				f.write(line)
		print(self.booknames)

	def parse_book(self, response):
		url = '/'.join(response.url.split('/')[-2:])
		xpath = '//div[@id="menu"]//span[contains(@class, "subcontents")][preceding-sibling::a[1][contains(@href, "{url}")]]'.format(url=url)
		menuitems = response.xpath(xpath).xpath('a[contains(@class, "menuitem")]')
		containers = response.xpath(xpath).xpath('span[contains(@class, "container")]')
		if menuitems:
			for menuitem in menuitems:
				self.process_article(response, menuitem, '', '')
		elif containers:
			for container in containers:
				chapter = container.xpath('a/text()').extract_first()
				chapter_url = response.urljoin(container.xpath('a/@href').extract_first())
				for menuitem in container.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
					self.process_article(response, menuitem, chapter, chapter_url)
		else:
			raise Exception('unknow page structure')

	def process_article(self, response, menuitem, chapter, chapter_url):
		articleinfo = {
			'url': response.urljoin(menuitem.xpath('@href').extract_first()),
			'name': menuitem.xpath('text()').extract_first(),
			'chapter': chapter,
			'chapter_url': chapter_url
		}
		if articleinfo['url'] is None:
			raise Exception('bad article url')
		response.meta['articles'].append(articleinfo)	

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


				




