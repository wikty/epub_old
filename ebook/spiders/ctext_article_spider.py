import re
import scrapy
from w3lib.html import remove_tags, remove_tags_with_content
from ebook import items
from ebook.item_loaders.ctext_article_loader import CTextArticleLoader

class CTextArticleSpider(scrapy.Spider):
	article_id = 1
	name = 'ctext-article'
	start_urls = ['http://ctext.org/xunzi/zhong-ni/zh', 'http://ctext.org/xunzi/fei-xiang/zh']

	def start_requests(self):
		for url in self.start_urls:
			request = scrapy.Request(
				url,
				callback=self.parse,
				#errback=self.errback,
				#dont_filter=True
			)
			request.meta['article_id'] = self.article_id
			self.article_id += 1
			yield request

	def parse(self, response):
		book_type = 'tw' if response.url.split('/')[-1] == 'zh' else 'zh'
		en_title = response.url.split('/')[-2]
		article_id = response.meta['article_id']

		xpath = '//div[@id="content"]//span[@itemscope][@itemtype][%d]/a'
		# category = response.xpath(xpath % 1).xpath('span/text()').extract_first()
		# category_url = response.xpath(xpath % 1).xpath('@href').extract_first()
		# en_category = category_url.split('/')[-2]
		# sub_category = response.xpath(xpath % 2).xpath('span/text()').extract_first()
		# sub_category_url = response.xpath(xpath % 2).xpath('@href').extract_first()
		# en_sub_category = sub_category_url.split('/')[-2]
		book_url = response.xpath(xpath % 3).xpath('@href').extract_first()
		en_book = book_url.split('/')[-2]
		book = response.xpath(xpath % 3).xpath('span/text()').extract_first()
		
		xpath = '//div[@id="content3"]//h2/text()'
		title = response.xpath(xpath).extract_first()
		
		l = CTextArticleLoader(item=items.CTextArticleItem(), response=response)
		l.add_value('url', response.url)
		l.add_value('article_id', article_id)
		l.add_value('book', book)
		l.add_value('en_book', en_book)
		l.add_value('title', title)
		l.add_value('en_title', en_title)
		l.add_value('book_type', book_type)

		comment = []
		content = []
		sup_count = 0
		cmt_count = 0
		for item in response.xpath('//div[@id="content3"]/table[2]/tbody/tr/td[3]'):
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