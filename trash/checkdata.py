import os, json

datadir = 'data/book3'

if __name__ == '__main__':
	l = []
	with open('data/books.jl', 'w', encoding='utf-8') as f:
		for directory, subdirs, files in os.walk(datadir):
			if directory != '.' and directory != '..':
					for fname in files:
						path = os.sep.join([directory, fname])
						#print(path)
						with open(path, 'r', encoding='utf-8') as article:
							raw = json.loads(article.readline())
							if raw.get('book', None) and raw.get('en_book', None):
								#print(raw['book'], raw['en_book'])
								f.write(json.dumps({
									'ch_name': raw['book'],
									'en_name': raw['en_book'],
									'type': 'zh'}, ensure_ascii=False))
								f.write('\n')
							else:
								l.append(fname)
	print('***********************')
	print(l)