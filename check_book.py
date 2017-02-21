import os, json, shutil

def is_ok(data_file, meta_file):
	if not os.path.exists(meta_file):
		raise Exception('meta file [%s] not exists' % meta_file)
	if not os.path.exists(data_file):
		raise Exception('data file [%s] not exists' % data_file)

	# get article list
	f = open(meta_file, 'r', encoding='utf8')
	metainfo = json.loads(f.read())
	f.close()
	book = metainfo.get('book', None)
	chapters = metainfo.get('chapters', None)
	articles = metainfo.get('articles', None)
	if not book:
		raise Exception('meta data should have book field')
	if not chapters:
		raise Exception('meta data should have chapters field')
	if not articles:
		raise Exception('meta data should have articles field')

	bookname = book['ch_name']
	en_bookname = book['en_name']
	article_info_dict = {}
	for chapter in chapters:
		for article_id in chapter.get('articles', []):
			if not articles.get(str(article_id), None):
				raise Exception('[Book %s] lost article id %d' % (bookname, article_id))
			if not articles[str(article_id)].get('url', None):
				raise Exception('[Book: %s, Article ID: %d] lost url' % (bookname, article_id))
			if not articles[str(article_id)].get('ch_name', None):
				raise Exception('[Book: %s, Article ID: %d] lost ch_name' % (bookname, article_id))
			article_info_dict[article_id] = {
				'url': articles[str(article_id)]['url'],
				'title': articles[str(article_id)]['ch_name']
			}

	# get bad article item list
	good_article_list = []
	bad_article_list = []
	f = open(data_file, 'r', encoding='utf8')
	lines = f.readlines()
	f.close()
	for line in lines:
		item = json.loads(line)
		if item.get('article_id', None) and item.get('content', None):
			good_article_list.append(item['article_id'])
	for article_id in set(article_info_dict.keys())-set(good_article_list):
		bad_article_list.append([
			article_id,
			article_info_dict[article_id]['url'],
			article_info_dict[article_id]['title']
		])
	ok = False if bad_article_list else True
	return [ok, {'ch_name': bookname, 'en_name': en_bookname}, bad_article_list]

def check(datadir, book_list_file='_books.jl', report_file='_report.jl'):
	if not os.path.exists(datadir):
		raise Exception('data directory not exists')
	hotdir = os.sep.join([datadir, 'hot'])

	if os.path.exists(hotdir):
		shutil.rmtree(hotdir)
	os.mkdir(hotdir)

	bfname = os.sep.join([hotdir, book_list_file])
	rfname = os.sep.join([hotdir, report_file])

	total_count = 0
	ok_count = 0
	with open(bfname, 'w', encoding='utf8') as bf, open(rfname, 'w', encoding='utf8') as rf:
		for directory, subdirs, files in os.walk(datadir):
			if directory == '.' or directory == '..' or directory == hotdir:
				continue
			for fname in files:
				if fname.find('_meta') >= 0:
					continue
				total_count += 1
				data_file = os.sep.join([directory, fname])
				meta_file = '.'.join(fname.split('.')[:-1]) + '_meta.json'
				meta_file = os.sep.join([directory, meta_file])
				[ok, bookinfo, articles] = is_ok(data_file, meta_file)
				if ok:
					ok_count += 1
					bf.write(json.dumps({
						'ch_name': bookinfo['ch_name'],
						'en_name': bookinfo['en_name'],
						'type': 'tw'
					}, ensure_ascii=False))
					bf.write('\n')
					shutil.copy(data_file, hotdir)
					shutil.copy(meta_file, hotdir)
				else:
					rf.write(json.dumps({
						'ch_name': bookinfo['ch_name'],
						'en_name': bookinfo['en_name'],
						'articles': articles
					}, ensure_ascii=False))
					rf.write('\n')
	return [total_count, ok_count]

if __name__ == '__main__':
	print(check('tmp'))