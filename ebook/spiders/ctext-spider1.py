import scrapy
from ebook import items
from ebook.ItemLoaders.ctext_article_loader import CTextArticleLoader

class CTextSpider(scrapy.Spider):
	name = 'ctext-spider'
	start_urls = ['http://ctext.org/zh']

	def parse(self, response):
		menu = response.xpath('//div[@id="menu"]')
		catlink1 = menu.xpath('div[1]/a')
		catlink2 = menu.xpath('div[2]/a')
		
		catlist = [catlink1]

		for catlink in catlist:
			link = catlink.css('::attr(href)').extract_first()
			# en_catname = link.split('/')[-2]
			# catname = catlink.css('::text').extract_first()

			if link is not None:
				link = response.urljoin(link)
				yield scrapy.Request(link, callback=self.parse_category)

	def parse_category(self, response):
		en_category = response.url.split('/')[-2]

		if en_category != 'pre-qin-and-han':
			return

		xpath = '//div[@id="menu"]/div[contains(@class, "menuitem")]/a[contains(@href, "%s")]/parent::div/following-sibling::div[1]/preceding-sibling::span[preceding-sibling::div/a[contains(@href, "%s")]]/a'
		for subcat in response.xpath(xpath % (en_category, en_category)):
			link = subcat.css('::attr(href)').extract_first()
			# en_sub_catname = link.split('/')[-2]
			# sub_catname = subcat.css('::text').extract_first()
			
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
			# en_bookname = link.split('/')[-2]
			# bookname = book.css('::text').extract_first()

			if link is not None:
				link = response.urljoin(link)
				yield scrapy.Request(link, callback=self.parse_book)

	def parse_book(self, response):
		en_book = response.url.split('/')[-2]

		if en_book != 'analects':
			return

		article_id = 1
		xpath = '//div[@id="content2"]/a'
		for article in response.xpath(xpath):
			link = article.css('::attr(href)').extract_first()
			# en_artname = link.split('/')[-2]
			# artname = article.css('::text').extract_first()

			if link is not None:
				link = response.urljoin(link)
				request = scrapy.Request(link, callback=self.parse_article)
				request.meta['article_id'] = article_id
				article_id += 1
				yield request

	def parse_article(self, response):
		en_title = response.url.split('/')[-2]

		if en_title not in ['xue-er', 'wei-zheng']:
			return

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
		l.add_value('article_id', response.meta['article_id'])
		l.add_value('category', category)
		l.add_value('en_category', en_category)
		l.add_value('sub_category', sub_category)
		l.add_value('en_sub_category', en_sub_category)
		l.add_value('book', book)
		l.add_value('en_book', en_book)
		l.add_value('en_title', response.url.split('/')[-2])
		l.add_xpath('title', '//div[@id="content3"]//h2/text()')

		content = []
		for item in response.xpath('//div[@id="content3"]/table[2]/tr/td[3]'):
			
			if item.xpath('sup'):
				pass
			if item.xpath('p[@class="refs"]'):
				pass
		
		sups = {}
		i = 0
		trlist = response.xpath('//div[@id="content3"]/table[2]/tr/td[3]')
		n = len(trlist)
		while i<n:
			item = trlist[i].xpath('td[3]')
			# /*[not(self::p) and not(self::sup)]

			pn = item.xpath('td[1]/a/text()').extract_first()
			if pn:
				item = item.xpath('td[3]')
				
				if item.xpath('a'):
					content.append(''.join([s.strip() for s in item.css('::text') if s.strip() and not s.isdegit()]))
				else:
					content.append(''.join([s.strip() for s in item.xpath('text()') if s.strip()]))

				item = trlist[i+1].xpath('td[3]')


			else:
				

			n = 
			if n:
				item = item.xpath('td[3]')
				if item.xpath('a'):
					content.append(''.join([s.strip() for s in item.css('::text') if s.strip() and not s.isdegit()]))
				else:
					content.append(''.join([s.strip() for s in item.xpath('text()') if s.strip()]))
			
			if item.xpath('sup'):
				sups[item.xpath('sup/text()').extract_first()] = {
					'id': len(content)-1,
					'content': ''
				}

			if item.xpath('p[@class="refs"]'):
				refs = item.xpath('p[@class="refs"]').css('::text').extract()
				if refs:
					n = refs[0].split('.')[0]
					sups[n]['content'] = ''.join(refs)
					sups[n]['content'] = sups[n]['content'][sups[n]['content'].index(' ')+1:]

		
		# l.add_xpath('content', '//div[@id="content3"]/table[2]/tr/td[3][@class="ctext"]/text()')
		# l.add_xpath('mcontent', '//div[@id="content3"]/table[2]/tr/td[3][@class="mctext"]/text()')
		l.add_value('filename', '-'.join([en_category, en_sub_category, en_title]))
		return l.load_item()