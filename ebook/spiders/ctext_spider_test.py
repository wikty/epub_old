import re
import scrapy
from w3lib.html import remove_tags, remove_tags_with_content
from ebook import items
from ebook.ItemLoaders.ctext_article_loader import CTextArticleLoader

class CTextSpider(scrapy.Spider):
	count = 0
	name = 'ctext-spider-test'
	start_urls = ['http://ctext.org/analects/xue-er/zh', 'http://ctext.org/analects/wei-zheng/zh']

	# def parse(self, response):
	# 	for article_link in response.xpath('//div[@id="content2"]/a'):
	# 		link = article_link.css('::attr(href)').extract_first()
	# 		title = article_link.css('::text').extract_first()
	# 		# yield {
	# 		# 	'link': link,
	# 		# 	'title': title
	# 		# }
	# 		if link is not None:
	# 			link = response.urljoin(link)
	# 			yield scrapy.Request(link, callback=self.parse_article)

	def parse(self, response):
		self.count += 1
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
		
		l = CTextArticleLoader(item=items.CTextArticleItem(), response=response)
		l.add_value('article_id', self.count)
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
		# sups = {}
		# i = 0
		# trlist = response.xpath('//div[@id="content3"]/table[2]/tr/td[3]')
		# n = len(trlist)
		# while i<n:
		# 	item = trlist[i].xpath('td[3]')
		# 	# /*[not(self::p) and not(self::sup)]

		# 	pn = item.xpath('td[1]/a/text()').extract_first()
		# 	if pn:
		# 		item = item.xpath('td[3]')
				
		# 		if item.xpath('a'):
		# 			content.append(''.join([s.strip() for s in item.css('::text') if s.strip() and not s.isdegit()]))
		# 		else:
		# 			content.append(''.join([s.strip() for s in item.xpath('text()') if s.strip()]))

		# 		item = trlist[i+1].xpath('td[3]')


		# 	else:
				

		# 	n = 
		# 	if n:
		# 		item = item.xpath('td[3]')
		# 		if item.xpath('a'):
		# 			content.append(''.join([s.strip() for s in item.css('::text') if s.strip() and not s.isdegit()]))
		# 		else:
		# 			content.append(''.join([s.strip() for s in item.xpath('text()') if s.strip()]))
			
		# 	if item.xpath('sup'):
		# 		sups[item.xpath('sup/text()').extract_first()] = {
		# 			'id': len(content)-1,
		# 			'content': ''
		# 		}

		# 	if item.xpath('p[@class="refs"]'):
		# 		refs = item.xpath('p[@class="refs"]').css('::text').extract()
		# 		if refs:
		# 			n = refs[0].split('.')[0]
		# 			sups[n]['content'] = ''.join(refs)
		# 			sups[n]['content'] = sups[n]['content'][sups[n]['content'].index(' ')+1:]

		
		# l.add_xpath('content', '//div[@id="content3"]/table[2]/tr/td[3][@class="ctext"]/text()')
		# l.add_xpath('mcontent', '//div[@id="content3"]/table[2]/tr/td[3][@class="mctext"]/text()')
		l.add_value('filename', '-'.join([en_category, en_sub_category, en_title]))
		return l.load_item()