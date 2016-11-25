import re
import scrapy
from w3lib.html import remove_tags, remove_tags_with_content
from ebook import items
from ebook.ItemLoaders.ctext_article_loader import CTextArticleLoader

class CTextArticleSpider(scrapy.Spider):
	article_id = 1
	name = 'ctext-article-spider'
	start_urls = ['http://ctext.org/xunzi/zhong-ni/zh', 'http://ctext.org/xunzi/fei-xiang/zh']

	def parse(self, response):
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
		#l.add_value('article_id', response.meta['article_id'])
		l.add_value('article_id', self.article_id)
		self.article_id += 1
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
			
			content.append(ln)
			if int(item.xpath('contains(@class, "mctext")').extract_first()):
				content.append('<br/>')

			for cmt in item.xpath('*[contains(@class, "refs")]'):
				cmt = ''.join([cmti.strip() for cmti in cmt.css('::text').extract() if cmti.strip()])
				mch = re.match('(\d+)\.\s*', cmt)
				if mch:
					cmt_count += 1
					#cmtid = mch.group(1)
					cmtid = cmt_count
					cmt = '<a class="footnote-link" id="comment{id}" href="#reference{id}">&#91;{id}&#93;.</a> '.format(id=cmtid) + cmt[mch.regs[0][1]:]
					comment.append(cmt)
		
		l.add_value('content', content)
		l.add_value('comment', comment)
		l.add_value('filename', '-'.join([en_category, en_sub_category, en_title]))
		return l.load_item()