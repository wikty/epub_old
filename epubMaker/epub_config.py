import os, json

class EpubConfig(object):
	_book_meta_info = {
		'tw': {
			'bookcat': '叢書名',
			'bookid': 'xxxxxxxx-xxxxxxxx',
			'author': '〔朝代〕作者名　身份',
			'publisher': '©藝雅出版社',
			'covertitle': '封面',
			'fronttitle': '版權信息',
			'contentstitle': '目錄',
			'navtitle': '目錄'
		},
		'zh': {
			'bookcat': '丛书名',
			'bookid': 'xxxxxxxx-xxxxxxxx',
			'author': '〔朝代〕作者名　身份',
			'publisher': '©艺雅出版社',
			'covertitle': '封面',
			'fronttitle': '版权信息',
			'contentstitle': '目录',
			'navtitle': '目录'
		}
	}

	_target_epub_files = {
		'coverpage': 'coverpage.xhtml',
		'frontpage': 'frontpage.xhtml',
		'contentspage': 'contents.xhtml',
		'navpage': 'nav.xhtml',
		'packagefile': 'package.opf',
		'ncxfile': 'toc.ncx',
		'maincssfile': 'main.css',
		'coverfile': 'cover.jpg',
		'mimetype': 'mimetype',
		'container': 'container.xml'
	}

	_source_epub_files = {
		'maincssfile': 'main.css',
		'coverfile': 'cover.jpg',
		'mimetype': 'mimetype',
		'container': 'container.xml'
	}

	def __init__(self, bookname, bookcname, booktype, targetdir, sourcedir, templatedir, datadir):
		# check target & source directory validation
		targetdir = targetdir.rstrip('/')
		sourcedir = sourcedir.rstrip('/')
		templatedir = templatedir.rstrip('/')
		datadir = datadir.rstrip('/')
		if not os.path.exists(targetdir):
			raise Exception('epub target directory not existed')
		if not os.path.exists(targetdir):
			raise Exception('epub source directory not existed')
		if not os.path.exists(templatedir):
			raise Exception('epub template directory not existed')
		if not os.path.exists(datadir):
			raise Exception('epub data directory not existed')

		# directory
		self.targetdir = targetdir
		self.sourcedir = sourcedir
		self.templatedir = templatedir
		self.datadir = datadir

		# this book's basic information
		self.bookname = bookname
		self.bookcname = bookcname
		self.booktype = booktype if booktype in ['tw', 'zh'] else 'tw'
		# book meta information for all books
		self.book_meta_info = self._book_meta_info['tw'] if self.booktype == 'tw' else self._book_meta_info['zh']

		# data source files, are contained in the target directory
		self._source_data_files = {
			'jsonfile': self.bookname+'.jl', # data json filename(should in rootpath director)
			'metafile': self.bookname+'_meta.json', # meta information of the above data file
		}

		self.source_data_files = {
			'jsonfile': os.sep.join([datadir, self._source_data_files['jsonfile']]),
			'metafile': os.sep.join([datadir, self._source_data_files['metafile']])
		}

		# chapter and article meta
		if not os.path.exists(self.source_data_files['metafile']):
			self.is_standalone = True
		else:
			self.source_data_meta = {}
			with open(self.source_data_files['metafile'], 'r', encoding='utf-8') as f:
				item = json.loads(f.read())
				chapter_list = item['chapterinfo_list']
				art2chap = item['article2chapter']
			# standalone book means that don't have chapter
			self.is_standalone = len(chapter_list) < 2
			# article id to chapter id
			self.source_data_meta['article2chapter'] = {int(k):int(v) for k,v in art2chap.items()}
			# chapter has many articles(sorted)
			self.source_data_meta['articles_in_chapter'] = {}
			for artid, chapid in art2chap.items():
				artid = int(artid)
				chapid = int(chapid)
				if chapid not in self.source_data_meta['articles_in_chapter']:
					self.source_data_meta['articles_in_chapter'][chapid] = []
				self.source_data_meta['articles_in_chapter'][chapid].append(artid)
			for chapid in self.source_data_meta['articles_in_chapter']:
				self.source_data_meta['articles_in_chapter'][chapid] = sorted(self.source_data_meta['articles_in_chapter'][chapid])
			# chapters information
			self.source_data_meta['chapters'] = {}
			for chapter in chapter_list:
				chapid = int(chapter['id'])
				ch_chapname = chapter['ch_name']
				en_chapname = chapter['en_name']
				self.source_data_meta['chapters'][chapid] = {
					'id': chapid,
					'title': ch_chapname,
					'en_title': en_chapname,
					'articles': self.source_data_meta['articles_in_chapter'][chapid]
				}

		# target epub directory
		self.target_epub_dirs = {
			'root': os.sep.join([targetdir, 'epub', bookname]),
			'epub': os.sep.join([targetdir, 'epub', bookname,'EPUB']),
			'metainf': os.sep.join([targetdir, 'epub', bookname,'META-INF']),
			'xhtml': os.sep.join([targetdir, 'epub', bookname,'EPUB','xhtml']),
			'img': os.sep.join([targetdir, 'epub', bookname,'EPUB','img']),
			'css': os.sep.join([targetdir, 'epub', bookname,'EPUB','css']),
			'js': os.sep.join([targetdir, 'epub', bookname,'EPUB','js'])
		}

		self.target_epub_files = {}
		for k,v in self._target_epub_files.items():
			if v.endswith('.xhtml'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['xhtml'], v])
			elif v.endswith('.css'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['css'], v])
			elif v.endswith('.js'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['js'], v])
			elif v.endswith('.jpg') or v.endswith('.png'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['img'], v])
			elif v.endswith('.opf') or v.endswith('.ncx'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['epub'], v])
			elif k == 'container':
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['metainf'], v])
			elif k == 'mimetype':
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['root'], v])
			else:
				raise Exception('unknow target epub file type')

		# source epub directory
		self.source_epub_dirs = {
			'root': sourcedir,
			'epub': os.sep.join([sourcedir, 'EPUB']),
			'metainf': os.sep.join([sourcedir, 'META-INF']),
			'xhtml': os.sep.join([sourcedir, 'EPUB', 'xhtml']),
			'img': os.sep.join([sourcedir, 'EPUB', 'img']),
			'css': os.sep.join([sourcedir, 'EPUB', 'css']),
			'js': os.sep.join([sourcedir, 'EPUB','js'])
		}

		self.source_epub_files = {}
		for k,v in self._source_epub_files.items():
			if k == 'maincssfile':
				self.source_epub_files[k] = os.sep.join([self.source_epub_dirs['css'], v])
			elif k == 'coverfile':
				self.source_epub_files[k] = os.sep.join([self.source_epub_dirs['img'], v])
			elif k == 'mimetype':
				self.source_epub_files[k] = os.sep.join([self.source_epub_dirs['root'], v])
			elif k == 'container':
				self.source_epub_files[k] = os.sep.join([self.source_epub_dirs['metainf'], v])
			else:
				raise Exception('unknow source epub file')

	def get_bookname(self):
		return self.bookname

	def get_bookcname(self):
		return self.bookcname

	def get_booktype(self):
		return self.booktype

	def get_epub_targetdir(self):
		return self.targetdir

	def get_epub_sourcedir(self):
		return self.sourcedir

	def get_book_meta(self, name):
		if not name in self.book_meta_info:
			raise Exception('{} not in book meta information'.format(name))
		return self.book_meta_info[name]

	def get_target_epub_dirs(self):
		return self.target_epub_dirs

	def get_target_epub_dirname(self, name):
		if not name in self.target_epub_dirs:
			raise Exception('{} epub directory not existed'.format(name))
		return self.target_epub_dirs[name]

	def get_target_epub_files(self, full=True):
		if full:
			return self.target_epub_files
		else:
			return self._target_epub_files

	def get_target_epub_filename(self, name, full=True):
		if full:
			files = self.target_epub_files
		else:
			files = self._target_epub_files

		if not name in files:
				raise Exception('{} epub file not existed'.format(name))
		return files[name]

	def get_source_epub_files(self, full=True):
		if full:
			return self.source_epub_files
		else:
			return self._source_epub_files

	def get_source_epub_filename(self, name, full=True):
		if full:
			files = self.source_epub_files
		else:
			files = self._source_epub_files

		if not name in files:
			raise Exception('{} epub source filename not existed'.format(name))
		return files[name]

	def get_source_data_filename(self, name, full=True):
		if full:
			files = self.source_data_files
		else:
			files = self._source_data_files
		if name not in files:
			raise Exception('{} source data not existed'.format(name))
		return files[name]

	def get_templatedir(self):
		return self.templatedir

	def is_standalone_book(self):
		return self.is_standalone

	def get_chapter_id(self, article_id=None):
		if not article_id:
			return sorted(self.source_data_meta['chapters'].keys())
		
		article_id = int(article_id)
		return self.source_data_meta['article2chapter'].get(article_id, None)

	def get_chapter(self, chapter_id):
		chapter_id = int(chapter_id)
		return self.source_data_meta['chapters'].get(chapter_id, None)

	def get_chapters(self):
		return self.source_data_meta['chapters']

	def get_prefix_of_article_in_contents(self):
		return 'a'

	def get_prefix_of_chapter_in_contents(self):
		return 'c'