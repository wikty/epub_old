class ChapterRaw(object):
	def __init__(self, chapter):
		if 'title' not in chapter or not chapter['title']:
			raise Exception('chapter must be have a id field and not empty')
		if 'id' not in chapter or not chapter['id']:
			raise Exception('chapter must be have a id field')
		self.id = int(chapter['id'])
		self.title = chapter.get('title', '')
		self.en_title = chapter.get('en_title', '')
		self.articles = chapter.get('articles', [])
	
	def get_id(self):
		return self.id

	def get_title(self):
		return self.title
	
	def get_en_title(self):
		return self.en_title
	
	def get_articles(self):
		return self.articles