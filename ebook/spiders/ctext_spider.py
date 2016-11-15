import re
import scrapy
from w3lib.html import remove_tags, remove_tags_with_content
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

		if en_book != 'liji':
			return
		# if en_book not in ['analects', 'mengzi', 'liji', 'xunzi', 'xiao-jing', 'shuo-yuan', 'chun-qiu-fan-lu', 'han-shi-wai-zhuan']:
		# 	return

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
		book_type = 'tw' if response.url.split('/')[-1] == 'zh' else 'zh'
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
		
		l = CTextArticleLoader(item=items.CTextArticleItem(), response=response)
		l.add_value('booktype', book_type)
		l.add_value('article_id', response.meta['article_id'])
		l.add_value('category', category)
		l.add_value('en_category', en_category)
		l.add_value('sub_category', sub_category)
		l.add_value('en_sub_category', en_sub_category)
		l.add_value('book', book)
		l.add_value('en_book', en_book)
		l.add_value('en_title', response.url.split('/')[-2])
		l.add_xpath('title', '//div[@id="content3"]//h2/text()')

		comment = []
		content = []
		for item in response.xpath('//div[@id="content3"]/table[2]/tr/td[3]'):
			#nodes = item.xpath('child::node()[not(@class="refs")][not(self::sup)]').extract()
			nodes = item.xpath('child::node()[not(@class="refs")]').extract()
			ln = ''.join([remove_tags(nd.strip(), keep=('sup',)) for nd in nodes if remove_tags(nd.strip(), keep=('sup',))])
			ln = re.sub(r'<sup\s+[\w"=\']+>(\d+)</sup>', r'<sup><a href="#comment\1" id="reference\1">\1</a></sup>', ln)
			# if int(item.xpath('contains(@class, "mctext")').extract_first()):
			# 	content[len(content)-1] = '<br/>'.join([content[len(content)-1], ln])
			# else:
			# 	content.append(ln)
			content.append(ln)
			if int(item.xpath('contains(@class, "mctext")').extract_first()):
				content.append('<br/>')
			for cmt in item.xpath('*[contains(@class, "refs")]'):
				cmt = ''.join([cmti.strip() for cmti in cmt.css('::text').extract() if cmti.strip()])
				mch = re.match('(\d+)\.\s+', cmt)
				if mch:
					cmtid = mch.group(1)
					cmt = '<a id="comment{id}" href="#reference{id}">{id}.</a> '.format(id=cmtid) + cmt[mch.regs[0][1]:]
					comment.append(cmt)
		l.add_value('content', content)
		l.add_value('comment', comment)
		l.add_value('filename', '-'.join([en_category, en_sub_category, en_title]))
		return l.load_item()