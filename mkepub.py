#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, getopt, sys, json
from epubMaker.epub_generator import EpubGenerator

#ebook_name = 'eBookTest'

# try:
#     opts, args = getopt.getopt(sys.argv[1:], "n:")
#     if opts and opts[0][0] == '-n':
#     	ebook_name = opts[0][1]

# except getopt.GetoptError:
# 	raise

ebook_name = 'analects'
config = {}
config['booktype'] = 'tw'
config['bookname'] = ebook_name
config['bookcname'] = '論語'
config['bookcat'] = '先秦兩漢儒家经典'
config['bookid'] = '00000002-20161001'
config['author'] = '〔春秋-戰國〕孔子及其弟子'
config['publisher'] = '©艺雅出版社'
config['coverfile'] = 'cover.jpg'
config['rootpath'] = os.getcwd()
config['jsonfile'] = ebook_name+'.jl'
EpubGenerator(**config).run()
os.chdir(os.sep.join(['epub', ebook_name]))
os.system("zip -rq " + '.'.join([ebook_name, 'epub']) + " *")
os.chdir('..')