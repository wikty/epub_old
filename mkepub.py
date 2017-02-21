#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, getopt, sys, json, subprocess
from epubmaker import EpubGenerator
from epubmaker import EpubConfig

current_directory = os.getcwd()
book_list_filename = 'books.jl'
epub_data_directory = os.sep.join([current_directory, 'data'])
epub_target_directory = os.sep.join([current_directory, 'epub'])
epub_source_directory = os.sep.join(['epubmaker', 'epub'])
epub_template_directory = os.sep.join(['epubmaker', 'templates'])
epubcheck_relative_path = '../../epubcheck-4.0.1/epubcheck.jar' # relative to the *.epub file
existed_list = []

with open(book_list_filename, 'r', encoding='utf-8') as f:
	for line in f:
		item = json.loads(line)
		en_name = item['en_name']
		# check if book has existed
		if os.path.exists(os.sep.join([epub_target_directory, en_name])):
			print('[EBook Maker]', en_name, 'existed')
			existed_list.append(en_name)
			continue
		
		# config epub generator
		print('[EBook Maker]', en_name, 'generating...')
		epub_data_jsonfile = os.sep.join([epub_data_directory, '%s.jl' % en_name])
		epub_data_metafile = os.sep.join([epub_data_directory, '%s_meta.json' % en_name])
		config = EpubConfig(
			item['en_name'], 
			item['ch_name'], 
			item['type'], 
			epub_target_directory, 
			epub_source_directory,
			epub_template_directory,
			epub_data_jsonfile,
			epub_data_metafile
		)
		EpubGenerator(config).run()
		# targetdir = os.getcwd() # epub target directory
		# datadir = os.sep.join([targetdir, 'data'])
		# sourcedir = os.sep.join([targetdir, epub_source_directory]) # epub source directory
		# templatedir = os.sep.join([targetdir, epub_template_directory]) # epub templates directory
		
		# archive epub
		# mimetype must be plain text(no compressed), 
		# must be first file in archive, so other inable-unzip 
		# application can read epub's first 30 bytes
		print('[EBook Maker]', en_name, 'archiving...')
		os.chdir(os.sep.join([epub_target_directory, en_name]))
		zipname = '.'.join([en_name, 'epub'])
		os.system("zip -0Xq %s mimetype" % zipname)
		os.system("zip -Xr9Dq %s *" % zipname)
		
		# check epub file validation
		print('[EBook Maker]', zipname, 'validating...')
		try:
			validation = subprocess.check_output("java -jar %s %s" % (epubcheck_relative_path, zipname), 
				stderr=subprocess.STDOUT, 
				shell=True)
		except subprocess.CalledProcessError as e:
			validation = e.output
		invalid = validation.decode('utf-8').find('No errors') < 0
		if invalid:
			with open(zipname+'.errors', 'wb') as f:
				print('[EBook Maker]', 'generate validation report', zipname+'.errors')
				f.write(validation)
		else:
			with open(zipname+'.ok', 'wb') as f:
				print('[EBook Maker]', 'epub has no errors')
				f.write(validation)

		# generate .doc
		print('[EBook Maker]', '%s.doc' % en_name, 'generating...')
		os.system('pandoc %s -o %s.doc' % (zipname, en_name))
		
		os.chdir('..')
		os.chdir('..')