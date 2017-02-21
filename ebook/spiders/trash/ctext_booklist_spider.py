import codecs, json, re
import scrapy
from w3lib.html import remove_tags, remove_tags_with_content
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from ebook import items
from ebook.item_loaders.ctext_article_loader import CTextArticleLoader

class CTextBookListSpider(scrapy.Spider):
	name = 'ctext-booklist-spider'

	def __init__(self, bookname=None, *args, **kwargs):
		super(CTextBookListSpider, self).__init__(*args, **kwargs)
		self.start_urls = []
		if bookname:
			if bookname.find(',') != -1:
				bookname = bookname.split(',')
			else:
				bookname = [bookname]
		else:
			bookname = []
			print('bookname is empty')

		with open('booklist.jl', 'r', encoding='utf-8') as f:
			item = json.loads(f.readline())
			l = item.get('url', '').split('/')
			if not l or len(l) < 2:
				self.logger.error('bad book url: {}'.format(item.get('name', '')))
			else:
				if l[-2] in bookname:
					count = 1
					for article in item.get('articles', []):
						if article.get('url', None):
							url = article['url']+'?'+str(count)
							self.start_urls.append(url)
							count += 1
							self.logger.info('Add URL: {}'.format(url))
						else:
							self.logger.error('bad article url: {}'.format(article.get('name', '')))

	def start_requests(self):
		for url in self.start_urls:
			yield scrapy.Request(
				url,
				callback=self.parse_article,
				errback=self.errback,
				dont_filter=True)

	def closed(self, reason):
		pass

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

	def parse_article(self, response):
		book_type = 'tw'
		en_title = response.url.split('/')[-2]
		article_id = int(response.url.split('?')[-1])

		xpath = '//div[@id="content"]//span[@itemscope][@itemtype][%d]/a'
		category = response.xpath(xpath % 1).xpath('span/text()').extract_first(default='CATEGORY')
		category_url = response.xpath(xpath % 1).xpath('@href').extract_first(default='')
		if category_url:
			en_category = category_url.split('/')[-2]
		else:
			en_category = 'CATEGORY'
			self.logger.error('categroy parse fail: {}'.format(response.url))

		sub_category = response.xpath(xpath % 2).xpath('span/text()').extract_first(default='SUB-CATEGORY')
		sub_category_url = response.xpath(xpath % 2).xpath('@href').extract_first(default='')
		if sub_category_url:
			en_sub_category = sub_category_url.split('/')[-2]
		else:
			en_sub_category = 'SUB-CATEGORY'
			self.logger.error('sub category parse fail: {}'.format(response.url))

		book = response.xpath(xpath % 3).xpath('span/text()').extract_first(default='BOOK')
		book_url = response.xpath(xpath % 3).xpath('@href').extract_first(default='')
		if book_url:
			en_book = book_url.split('/')[-2]
		else:
			en_book = 'BOOK'
			self.logger.error('book parse fail: {}'.format(response.url))
		
		l = CTextArticleLoader(item=items.CTextArticleItem(), response=response)
		l.add_value('booktype', book_type)
		l.add_value('article_id', article_id)
		l.add_value('category', category)
		l.add_value('en_category', en_category)
		l.add_value('sub_category', sub_category)
		l.add_value('en_sub_category', en_sub_category)
		l.add_value('book', book)
		l.add_value('en_book', en_book)
		l.add_value('en_title', en_title)
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