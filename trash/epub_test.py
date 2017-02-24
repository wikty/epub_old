#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, getopt, sys, json, subprocess
from epubMaker import EpubGenerator
from epubMaker import EpubConfig

with open('books.jl', 'r', encoding='utf-8') as f:
	for line in f:
		item = json.loads(line)
		ebook_name = item['en_name']
		if os.path.exists(os.sep.join(['epub', ebook_name])):
			print('EBook', ebook_name, 'existed')
			continue
		#print('EBook', ebook_name, 'generating...')
		
		targetdir = os.getcwd() # epub target directory
		sourcedir = os.sep.join([targetdir, 'epubMaker', 'epub']) # epub source directory
		templatedir = os.sep.join([targetdir, 'epubMaker', 'templates']) # epub templates directory
		config = EpubConfig(item['en_name'], item['ch_name'], item['type'], targetdir, sourcedir, templatedir)
		
		# test config
		print(config.is_standalone_book())
		
		for i in config.get_chapter_id():
			chapter = config.get_chapter(i)
			if not chapter:
				break
			print('Chapter', i, chapter)

		#EpubGenerator(config).run()
		
		# archive epub
		# mimetype must be plain text(no compressed), 
		# must be first file in archive, so other inable-unzip 
		# application can read epub's first 30 bytes
		# os.chdir(os.sep.join(['epub', ebook_name]))
		# zipname = '.'.join([ebook_name, 'epub'])
		# os.system("zip -0Xq " + zipname + " mimetype")
		# os.system("zip -Xr9Dq " + zipname + " *")
		
		# print('EBook', zipname, 'validating...')
		# # check epub file validation
		# try:
		# 	validation = subprocess.check_output("java -jar ../../epubcheck-4.0.1/epubcheck.jar " + zipname, stderr=subprocess.STDOUT, shell=True)
		# except subprocess.CalledProcessError as e:
		# 	validation = e.output
		# if validation.decode('utf-8').find('No errors') < 0:
		# 	with open(zipname+'.errors', 'wb') as f:
		# 		print('EBook', 'generate validation report', zipname+'.errors')
		# 		f.write(validation)
		# else:
		# 	with open(zipname+'.ok', 'wb') as f:
		# 		print('EBook has no errors')
		# 		f.write(validation)
		
		# os.chdir('..')
		# os.chdir('..')