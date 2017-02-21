# -*- coding:utf-8 -*-
import os

class ArticleRaw(object):
	def __init__(self, article):
		if 'article_id' not in article:
			print(article)
			raise Exception('article raw lost article id')
		self.id = int(article['article_id']) # required
		self.book = article.get('book', '')
		self.en_book = article.get('en_book', '')
		self.book_type = article.get('book_type', 'tw')
		self.title = article.get('title', '')
		self.en_title = article.get('en_title', '')
		self.content = article.get('content', [])
		self.comment = article.get('comment', [])
		self._content = ''
		self._comment = ''

	def get_id(self):
		return self.id

	def get_book_type(self):
		return self.book_type

	def get_title(self):
		return self.title

	def get_en_title(self):
		return self.en_title

	def get_content_body(self):
		if not self._content:
			self._content = '\n'.join(['<p>' + l + '</p>'  for l in self.content])
		return self._content

	def get_content_head(self):
		return '\n'

	def get_content_foot(self):
		return '\n'

	def get_content(self):
		content_body = self.get_content_body()
		if not content_body:
			return ''
		
		return '\n'.join([
			self.get_content_head(),
			content_body,
			self.get_content_foot()
		])


	def get_comment_body(self):
		if not self._comment:
			self._comment = '\n'.join(['<p class="footnote">' + l + '</p>' for l in self.comment])
		return self._comment

	def get_comment_head(self):
		return '\n<hr/>\n<p class="footnote">【注释】</p>\n'

	def get_comment_foot(self):
		return '\n'

	def get_comment(self):
		comment_body = self.get_comment_body()
		if not comment_body:
			return ''
		return '\n'.join([
			self.get_comment_head(),
			comment_body,
			self.get_comment_foot()
		])

	def get_body(self):
		return '\n'.join([
			self.get_content(),
			self.get_comment()
		])