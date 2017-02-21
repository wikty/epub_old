import re, codecs, json, os

import scrapy
from w3lib.html import remove_tags, remove_tags_with_content
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from ebook import items
from ebook.item_loaders.ctext_article_loader import CTextArticleLoader

class CTextBookSpider(scrapy.Spider):
	name = 'ctext-book'
	start_urls = ['http://ctext.org/shiji/zh']
	failure_urls = []
	success_urls = []
	datadir = 'data'

	def __init__(self, book_list_file=None, book_num=None, *args, **kwargs):
		super(CTextBookSpider, self).__init__(*args, **kwargs)
		if book_list_file and os.path.exists(book_list_file):
			with open(book_list_file, 'r', encoding='utf8') as f:
				lines = f.readlines()
				if book_num:
					book_num = int(book_num)
					lines = lines[:book_num]
			if lines:
				self.start_urls = [json.loads(line)['url'] for line in lines]

	def start_requests(self):
		for url in self.start_urls:
			request = scrapy.Request(
				url,
				callback=self.parse_book,
				errback=self.errback,
				#dont_filter=True
			)
			
			yield request

	def closed(self, reason):
		report_file = os.sep.join([self.datadir, '%s_report.json' % self.name])
		with open(report_file, 'w', encoding='utf8') as f:
			f.write(json.dumps({
				'start_urls': self.start_urls,
				'success_urls': self.success_urls,
				'failure_urls': self.failure_urls
			}, ensure_ascii=False))

	def errback(self, failure):
		# log all failures
		self.logger.error(repr(failure))

		# in case you want to do something special for some errors,
		# you may need the failure's type:

		url = ''
		if failure.check(HttpError):
			# these exceptions come from HttpError spider middleware
			# you can get the non-200 response
			response = failure.value.response
			self.logger.error('HttpError on %s', response.url)
			url = response.url

		elif failure.check(DNSLookupError):
			# this is the original request
			request = failure.request
			self.logger.error('DNSLookupError on %s', request.url)
			url = request.url

		elif failure.check(TimeoutError, TCPTimedOutError):
			request = failure.request
			self.logger.error('TimeoutError on %s', request.url)
			url = request.url

		else:
			self.logger.error('Unknow Error!')

		if url:
			self.failure_urls.append(url)

	def parse_book(self, response):
		try:
			url_components = response.url.split('/')
			url = '/'.join(url_components[-2:])
			en_book = url_components[-2]
			ch_book = response.xpath('//div[@id="menu"]//a[@href="{url}"]/text()'.format(url=url)).extract_first()
			book_type = 'tw' if url_components[-1] == 'zh' else 'zh'

			# book category information
			category_level = 1
			categories = []
			for category in response.xpath('//div[@id="content"]//span[@itemscope][@itemtype]/a'):
				category_url = category.xpath('@href').extract_first(default='/')
				en_category = category_url.split('/')[-2]
				ch_category = category.xpath('span/text()').extract_first(default='')
				categories.append({
					'en_name': en_category,
					'ch_name': ch_category,
					'url': category_url,
					'id': category_level
				})
				category_level += 1
		
			# book meta information
			bookinfo = {
				'url': response.url,
				'type': book_type,
				'en_name': en_book,
				'ch_name': ch_book,
				'categories': categories,
				'standalone': True
			}
			
			chapter_list = []
			article_dict = {}
			
			xpath = '//div[@id="menu"]//a[@href="{url}"]'.format(url=url)
			article = response.xpath(xpath)
			subcontents = response.xpath(xpath).xpath('following-sibling::span[1][contains(@class, "subcontents")]')
			chapters = subcontents.xpath('span[contains(@class, "container")]') if subcontents else None
			articles = subcontents.xpath('a[contains(@class, "menuitem")]') if subcontents else None

			# book has only one article
			if not subcontents:
				article_id = 1
				chapter_id = 1
				chapterinfo = {
					'url': '',
					'ch_name': '',
					'en_name': '',
					'id': chapter_id,
					'articles': []
				}
				chapter_list.append(chapterinfo)

				yield self.process_article(response, bookinfo, chapterinfo, article_dict, article_id, article)
			elif chapters:
				# book has several chapters
				bookinfo['standalone'] = False
				article_id = 1
				chapter_id = 1
				for chapter in chapters:
					chapter_url = response.urljoin(chapter.xpath('a/@href').extract_first())
					ch_chapter = chapter.xpath('a/text()').extract_first(default='')
					en_chapter = chapter.xpath('a/@href').extract_first(default='/').split('/')[-2]
					chapterinfo = {
						'url': chapter_url,
						'ch_name': ch_chapter,
						'en_name': en_chapter,
						'id': chapter_id,
						'articles': []
					}
					chapter_list.append(chapterinfo)

					for article in chapter.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
						yield self.process_article(response, bookinfo, chapterinfo, article_dict, article_id, article)
						article_id += 1
					chapter_id += 1
			elif articles:
				# book has several articles
				article_id = 1
				chapter_id = 1
				chapterinfo = {
					'url': '',
					'ch_name': '',
					'en_name': '',
					'id': chapter_id,
					'articles': []
				}
				chapter_list.append(chapterinfo)
				
				for article in articles:
					yield self.process_article(response, bookinfo, chapterinfo, article_dict, article_id, article)
					article_id += 1
			else:
				self.logger.error('unknow page structure: {}'.format(response.url))
				raise Exception('unknow page structure')
			self.write_bookmeta(chapter_list, article_dict, bookinfo)
		except Exception:
			self.failure_urls.append(response.url)
		else:
			self.success_urls.append(response.url)
	
	def write_bookmeta(self, chapters, articles, book):
		meta_filename = os.sep.join([self.datadir, '%s_meta.json' % book['en_name']])
		f = codecs.open(meta_filename, 'w', encoding='utf-8')
		line = json.dumps({
			'chapters': chapters,
			'articles': articles,
			'book': book
		}, ensure_ascii=False)
		f.write(line)
		f.close()
		self.logger.info('write {} book meta data into file'.format(book['ch_name']))

	def process_article(self, response, bookinfo, chapterinfo, article_dict, article_id, article):
		chapterinfo['articles'].append(article_id)
		article_dict[article_id] = {
			'chapter_id': chapterinfo['id'],
			'url': '',
			'en_name': '',
			'ch_name': ''
		}

		url = article.xpath('@href').extract_first()
		if url is None:
			self.logger.error('article url is empty in book [%s]' % response.url)
		else:
			try:
				article_url = response.urljoin(url)
				en_article = article_url.split('/')[-2]
				ch_article = article.xpath('text()').extract_first()

				article_dict[article_id]['url'] = article_url
				article_dict[article_id]['en_name'] = en_article
				article_dict[article_id]['ch_name'] = ch_article
				articleinfo = {
					'url': article_url,
					'en_name': en_article,
					'ch_name': ch_article,
					'article_id': article_id
				}

				request = scrapy.Request(article_url, callback=self.parse_article)
				request.meta['articleinfo'] = articleinfo
				request.meta['bookinfo'] = bookinfo
			except Exception:
				return None
			else:
				return request
	
	def parse_article(self, response):
		bookinfo = response.meta['bookinfo']
		articleinfo = response.meta['articleinfo']

		l = CTextArticleLoader(item=items.CTextArticleItem(), response=response)
		
		l.add_value('article_id', articleinfo['article_id'])
		l.add_value('title', articleinfo['ch_name'])
		l.add_value('en_title', articleinfo['en_name'])
		l.add_value('book', bookinfo['ch_name'])
		l.add_value('en_book', bookinfo['en_name'])
		l.add_value('book_type', bookinfo['type'])
		l.add_value('url', response.url)

		comment = []
		content = []
		sup_count = 0
		cmt_count = 0
		tds = response.xpath('//div[@id="content3"]/table[2]/tbody/tr/td[3]')
		if not tds:
			tds = response.xpath('//div[@id="content3"]/table[2]/tr/td[3]')
		for item in tds:
			#nodes = item.xpath('child::node()[not(@class="refs")][not(self::sup)]').extract()
			nodes = item.xpath('child::node()[not(@class="refs")]').extract()
			cmts = item.xpath('*[contains(@class, "refs")]').extract()

			def replace_sup(m):
				nonlocal sup_count
				sup_count += 1
				return '<sup><a class="footnote-link" href="#comment{id}" id="reference{id}">&#91;{id}&#93;</a></sup>'.format(id=sup_count)

			ln = ''.join([remove_tags(nd.strip(), keep=('sup',)) for nd in nodes if remove_tags(nd.strip(), keep=('sup',))])
			ln = re.sub(r'<sup\s+[\w"=\']+>\s*(\d+)\s*</sup>', replace_sup, ln)
			
			if int(item.xpath('contains(@class, "mctext")').extract_first()):
				content[len(content)-1] = '<br/>'.join([content[len(content)-1], ln])
			else:
				content.append(ln)
			# content.append(ln)
			# if int(item.xpath('contains(@class, "mctext")').extract_first()):
			# 	content.append('<br/>')

			for cmt in cmts:
				cmt = remove_tags(cmt)
				for m in re.split(r'\d+\s*\.\s*', cmt):
					if m.strip():
						cmt_count += 1
						s = '<a class="footnote-link" id="comment{id}" href="#reference{id}">&#91;{id}&#93; </a> {cmt}'.format(id=cmt_count, cmt=m)
						comment.append(s)
		l.add_value('content', content)
		l.add_value('comment', comment)

		return l.load_item()