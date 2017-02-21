import re, urllib, codecs, json

import scrapy
from w3lib.html import remove_tags, remove_tags_with_content

from ebook import items
from ebook.item_loaders.ctext_article_loader import CTextArticleLoader


class CTextMenuSpider(scrapy.Spider):
	name = 'ctext-menu'
	start_urls = ['http://ctext.org/zh']
	book_list = []

	def parse(self, response):
		xpath = '//div[@id="menu"]/div[contains(@class, "listhead")][position() < 3]/a'
		for link in response.xpath(xpath):
			url = link.xpath('@href').extract_first()
			if not url:
				raise Exception('web page changed')
			
			xpath = 'parent::div/following-sibling::div[1]/preceding-sibling::span[contains(@class, "menuitem")][preceding-sibling::div/a[contains(@href, "{url}")]]'.format(url=url)
			for category in link.xpath(xpath):
				category_name = category.xpath('a[1][contains(@class, "menuitem")]/text()').extract_first()
				category_url = category.xpath('a[1][contains(@class, "menuitem")]/@href').extract_first()
				if not category_url:
					raise Exception('web page changed')
				category_url = response.urljoin(category_url)
				
				for book in category.xpath('span[contains(@class, "subcontents")]/a[contains(@class, "menuitem")]'):
					book_url = book.xpath('@href').extract_first()
					book_name = book.xpath('text()').extract_first()
					if not book_url:
						raise Exception('web page changed')
					bookinfo = {
						'url': response.urljoin(book_url),
						'name': book_name,
						'category_name': category_name,
						'category_url': category_url
					}
					self.book_list.append(bookinfo)
		with codecs.open('booklist.jl', 'w', encoding='utf-8') as f:
			for bookinfo in self.book_list:
				line = json.dumps(bookinfo, ensure_ascii=False) + "\n"
				f.write(line)