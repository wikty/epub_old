import re, codecs, json

import scrapy
from w3lib.html import remove_tags, remove_tags_with_content
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from ebook import items
from ebook.item_loaders.ctext_article_loader import CTextArticleLoader

class CTextBookSpider(scrapy.Spider):
	name = 'ctext-book-spider'
	start_urls = ['http://ctext.org/shiji/zh']

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
		else:
			self.logger.error('Unknow Error!')

	def parse_book(self, response):
		url = '/'.join(response.url.split('/')[-2:])
		
		en_book = response.url.split('/')[-2]
		ch_book = response.xpath('//div[@id="menu"]//a[@href="{url}"]/text()'.format(url=url)).extract_first(default='')
		book_type = 'tw' if response.url.split('/')[-1] == 'zh' else 'zh'

		# book category information
		cat_id = 1
		categories = []
		for category in response.xpath('//div[@id="content"]//span[@itemscope][@itemtype]/a'):
			cat_url = category.xpath('@href').extract_first(default='/')
			en_cat = cat_url.split('/')[-2]
			ch_cat = category.xpath('span/text()').extract_first(default='')
			categories.append({
				'en_name': en_cat,
				'ch_name': ch_cat,
				'url': cat_url,
				'id': cat_id
			})
			cat_id += 1
		
		# book meta information
		bookinfo = {
			'url': response.url,
			'type': book_type,
			'en_name': en_book,
			'ch_name': ch_book,
			'categories': categories
		}

		chapterinfo_list = []
		
		article2chapter = {}
		booktree = bookinfo.copy()
		booktree['chapters'] = [] # [{id, url, ch_name, en_name, articles},...]

		xpath = '//div[@id="menu"]//a[@href="{url}"]'.format(url=url)
		subcontents = response.xpath(xpath).xpath('following-sibling::span[1][contains(@class, "subcontents")]')
		chapters = subcontents.xpath('span[contains(@class, "container")]') if subcontents else None
		articles = subcontents.xpath('a[contains(@class, "menuitem")]') if subcontents else None

		if not subcontents:
			# book has only one article
			article = response.xpath(xpath)
			article_id = 1
			chapter_id = 1
			chapterinfo = {
				'url': '',
				'ch_name': '',
				'en_name': '',
				'id': chapter_id
			}

			chapterinfo_list.append(chapterinfo.copy())

			chapterinfo['articles'] = []
			booktree['chapters'].append(chapterinfo)

			response.meta['article_id'] = article_id
			article2chapter[article_id] = chapter_id
			yield self.process_article(response, bookinfo, chapterinfo, article)
		elif chapters:
			# book has several chapters
			chapter_id = 1
			article_id = 1
			for chapter in chapters:
				chapter_url = response.urljoin(chapter.xpath('a/@href').extract_first())
				ch_chapter = chapter.xpath('a/text()').extract_first(default='')
				en_chapter = chapter.xpath('a/@href').extract_first(default='/').split('/')[-2]
				chapterinfo = {
					'url': chapter_url,
					'ch_name': ch_chapter,
					'en_name': en_chapter,
					'id': chapter_id
				}

				chapterinfo_list.append(chapterinfo.copy())

				chapterinfo['articles'] = []
				booktree['chapters'].append(chapterinfo)

				for article in chapter.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
					response.meta['article_id'] = article_id
					article2chapter[article_id] = chapter_id
					yield self.process_article(response, bookinfo, chapterinfo, article)
					article_id += 1
				chapter_id += 1
		elif articles:
			# book has several articles
			chapter_id = 1
			article_id = 1
			chapterinfo = {
				'url': '',
				'ch_name': '',
				'en_name': '',
				'id': chapter_id
			}

			chapterinfo_list.append(chapterinfo.copy())

			chapterinfo['articles'] = []
			booktree['chapters'].append(chapterinfo)

			for article in articles:
				response.meta['article_id'] = article_id
				article2chapter[article_id] = chapter_id
				yield self.process_article(response, bookinfo, chapterinfo, article)
				article_id += 1
		else:
			self.logger.error('unknow page structure: {}'.format(response.url))			

		f = codecs.open(en_book + '_tree.json', 'w', encoding='utf-8')
		line = json.dumps(booktree, ensure_ascii=False)
		f.write(line)
		f.close()
		self.logger.info('write {} book tree into file'.format(booktree['ch_name']))

		meta = {
			'chapterinfo_list': chapterinfo_list,
			'bookinfo': bookinfo,
			'article2chapter': article2chapter
		}

		f = codecs.open(en_book + '_meta.json', 'w', encoding='utf-8')
		line = json.dumps(meta, ensure_ascii=False)
		f.write(line)
		f.close()
		self.logger.info('write {} book meta into file'.format(booktree['ch_name']))

		# xpath = '//div[@id="menu"]//span[contains(@class, "subcontents")]/a[@href="{url}"]'.format(url=url)
		# article = response.xpath(xpath)
		# xpath = '//div[@id="menu"]//span[contains(@class, "subcontents")][preceding-sibling::a[1][@href="{url}"]]'.format(url=url)
		# articles = response.xpath(xpath).xpath('a[contains(@class, "menuitem")]')
		# chapters = response.xpath(xpath).xpath('span[contains(@class, "container")]')

		# article_id = 1
		# if article:
		# 	# book has single article
		# 	yield self.process_article(response, bookinfo, article, '', '', article_id)
		# 	article_id += 1
		# if menuitems:
		# 	# book has no chapter
		# 	for menuitem in menuitems:
		# 		yield self.process_article(response, bookinfo, menuitem, '', '', article_id)
		# 		article_id += 1
		# if containers:
		# 	# book has chapter
		# 	for container in containers:
		# 		chapter = container.xpath('a/text()').extract_first()
		# 		chapter_url = response.urljoin(container.xpath('a/@href').extract_first())
		# 		for menuitem in container.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
		# 			yield self.process_article(response, bookinfo, menuitem, chapter, chapter_url, article_id)
		# 			article_id += 1
		# else:
		# 	self.logger.error('unknow page structure: {}'.format(response.url))
	
	def process_article(self, response, bookinfo, chapterinfo, article):
		url = article.xpath('@href').extract_first()
		if url is None:
			self.logger.error('article url is empty')
		else:
			article_id = response.meta['article_id']
			art_url = response.urljoin(url)
			en_art = url.split('/')[-2]
			ch_art = article.xpath('text()').extract_first()

			articleinfo = {
				'url': art_url,
				'en_name': en_art,
				'ch_name': ch_art,
				'article_id': article_id
			}
			chapterinfo['articles'].append(articleinfo)

			request = scrapy.Request(art_url, callback=self.parse_article)
			request.meta['articleinfo'] = articleinfo
			request.meta['bookinfo'] = bookinfo
			
			# request.meta['bookinfo'] = {
			# 	'url': bookinfo['url'],
			# 	'en_name': bookinfo['en_name'],
			# 	'ch_name': bookinfo['ch_name'],
			# 	'categories': bookinfo['categories'],
			# 	'book_type': bookinfo['type']
			# }
			
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
		for item in response.xpath('//div[@id="content3"]/table[2]/tr/td[3]'):
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

	# def parse(self, response):
	# 	en_book = response.url.split('/')[-2]

	# 	article_id = 1
	# 	xpath = '//div[@id="content2"]/a'
	# 	for article in response.xpath(xpath):
	# 		link = article.css('::attr(href)').extract_first()
	# 		# en_artname = link.split('/')[-2]
	# 		# artname = article.css('::text').extract_first()

	# 		if link is not None:
	# 			link = response.urljoin(link)
	# 			request = scrapy.Request(link, callback=self.parse_article)
	# 			request.meta['article_id'] = article_id
	# 			article_id += 1
	# 			yield request

	def parse_article_old(self, response):
		book_type = 'tw' if response.url.split('/')[-1] == 'zh' else 'zh'
		en_title = response.url.split('/')[-2]
		article_id = response.meta['article_id']

		xpath = '//div[@id="content"]//span[@itemscope][@itemtype][%d]/a'
		category = response.xpath(xpath % 1).xpath('span/text()').extract_first(default='CATEGORY')
		category_url = response.xpath(xpath % 1).xpath('@href').extract_first(default='')
		if category_url:
			en_category = category_url.split('/')[-2]
		else:
			en_category = 'CATEGORY'
			self.logger.error('categroy parse fail: {}'.format(response.url))
			self.logger.error('article id: {}'.format(article_id))

		sub_category = response.xpath(xpath % 2).xpath('span/text()').extract_first(default='SUB-CATEGORY')
		sub_category_url = response.xpath(xpath % 2).xpath('@href').extract_first(default='')
		if sub_category_url:
			en_sub_category = sub_category_url.split('/')[-2]
		else:
			en_sub_category = 'SUB-CATEGORY'
			self.logger.error('sub category parse fail: {}'.format(response.url))
			self.logger.error('article id: {}'.format(article_id))

		book = response.xpath(xpath % 3).xpath('span/text()').extract_first(default='BOOK')
		book_url = response.xpath(xpath % 3).xpath('@href').extract_first(default='')
		if book_url:
			en_book = book_url.split('/')[-2]
		else:
			en_book = 'BOOK'
			self.logger.error('book parse fail: {}'.format(response.url))
			self.logger.error('article id: {}'.format(article_id))

		l = CTextArticleLoader(item=items.CTextArticleItem(), response=response)
		l.add_value('booktype', book_type)
		l.add_value('article_id', article_id)
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
		sup_count = 0
		cmt_count = 0
		for item in response.xpath('//div[@id="content3"]/table[2]/tr/td[3]'):
			#nodes = item.xpath('child::node()[not(@class="refs")][not(self::sup)]').extract()
			nodes = item.xpath('child::node()[not(@class="refs")]').extract()
			
			ln = ''.join([remove_tags(nd.strip(), keep=('sup',)) for nd in nodes if remove_tags(nd.strip(), keep=('sup',))])
			if re.search(r'<sup\s+[\w"=\']+>\s*(\d+)\s*</sup>', ln):
				sup_count += 1
				# ln = re.sub(r'<sup\s+[\w"=\']+>\s*(\d+)\s*</sup>', r'<sup><a class="footnote-link" href="#comment\1" id="reference\1">&#91;\1&#93;</a></sup>', ln)
				ln = re.sub(r'<sup\s+[\w"=\']+>\s*(\d+)\s*</sup>', '<sup><a class="footnote-link" href="#comment{id}" id="reference{id}">&#91;{id}&#93;</a></sup>'.format(id=sup_count), ln)
			if int(item.xpath('contains(@class, "mctext")').extract_first()):
				content[len(content)-1] = '<br/>'.join([content[len(content)-1], ln])
			else:
				content.append(ln)
			# content.append(ln)
			# if int(item.xpath('contains(@class, "mctext")').extract_first()):
			# 	content.append('<br/>')

			for cmt in item.xpath('*[contains(@class, "refs")]'):
				cmt = ''.join([cmti.strip() for cmti in cmt.css('::text').extract() if cmti.strip()])
				mch = re.match('(\d+)\.\s*', cmt)
				if mch:
					cmt_count += 1
					#cmtid = mch.group(1)
					cmtid = cmt_count
					cmt = '<a class="footnote-link" id="comment{id}" href="#reference{id}">&#91;{id}&#93; </a> '.format(id=cmtid) + cmt[mch.regs[0][1]:]
					comment.append(cmt)
		
		l.add_value('content', content)
		l.add_value('comment', comment)
		l.add_value('filename', '-'.join([en_category, en_sub_category, en_title]))
		return l.load_item()