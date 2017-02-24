class ChapterRaw(object):
	def __init__(self, chapter):
		if 'ch_name' not in chapter or not chapter['ch_name']:
			raise Exception('chapter must be have a ch_name field and not empty')
		if 'id' not in chapter or not chapter['id']:
			raise Exception('chapter must be have a id field')
		self.id = int(chapter['id'])
		self.title = chapter.get('ch_name', '')
		self.en_title = chapter.get('en_name', '')
		self.articles = chapter.get('articles', [])
	
	def get_id(self):
		return self.id

	def get_title(self):
		return self.title
	
	def get_en_title(self):
		return self.en_title
	
	def get_articles(self):
		return self.articles