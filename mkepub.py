#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, getopt, sys, json
from epubMaker.epub_generator import EpubGenerator

with open('booklist.jl', 'r', encoding='utf-8') as f:
	for line in f:
		item = json.loads(line)
		ebook_name = item['bookname']
		if os.path.exists(os.sep.join(['epub', ebook_name])):
			print('EBook', ebook_name, 'existed')
			continue
		print('EBook', ebook_name, 'generating...')
		config = {}
		config['booktype'] = item['booktype']
		config['bookname'] = ebook_name
		config['bookcname'] = item['bookcname']
		config['bookcat'] = item['bookcat']
		config['bookid'] = '00000002-20161001'
		config['author'] = '待填充'
		config['publisher'] = '©藝雅出版社'
		config['coverfile'] = 'cover.jpg'
		config['rootpath'] = os.getcwd()
		print(os.getcwd())
		config['jsonfile'] = ebook_name+'.jl'
		EpubGenerator(**config).run()
		os.chdir(os.sep.join(['epub', ebook_name]))
		# os.system("zip -rq " + '.'.join([ebook_name, 'epub']) + " *")
		# mimetype must be plain text(no compressed), 
		# must be first file in archive, so other inable-unzip 
		# application can read epub's first 30 bytes
		os.system("zip -0Xq " + '.'.join([ebook_name, 'epub']) + " mimetype")
		os.system("zip -Xr9Dq " + '.'.join([ebook_name, 'epub']) + " *")
		os.chdir('..')
		os.chdir('..')