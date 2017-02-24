#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, getopt, sys, json, subprocess, shutil, time
from epubmaker import EpubGenerator
from epubmaker import EpubConfig

report = {
	'existed': [],
	'invalid': [],
	'valid': []
}

# check directory
today = time.strftime('%Y_%m_%d')
current_directory = os.path.abspath(os.getcwd())
epub_data_directory = os.sep.join([current_directory, 'data', today])
epub_source_directory = os.sep.join([current_directory, 'epubmaker', 'epub'])
epub_template_directory = os.sep.join([current_directory, 'epubmaker', 'templates'])
epub_check_path = os.sep.join([current_directory, 'epubcheck-4.0.1/epubcheck.jar']) # relative to the *.epub file
book_list_filename = os.sep.join([epub_data_directory, 'books.jl'])
book_target_directory = os.sep.join([current_directory, 'products', today, 'book'])
epub_target_directory = os.sep.join([current_directory, 'products', today, 'epub'])
report_filename = os.sep.join([current_directory, 'products', today, 'report.json'])

source_items = [
	epub_data_directory,
	epub_source_directory,
	epub_template_directory,
	epub_check_path,
	book_list_filename
]

target_dirs = [
	book_target_directory,
	epub_target_directory
]

for source_item in source_items:
	if not os.path.exists(source_item):
		raise Exception('[%s] not exists' % source_item)

for target_dir in target_dirs:
	if not os.path.exists(target_dir):
		os.makedirs(target_dir)

# generate epub and word
with open(book_list_filename, 'r', encoding='utf-8') as f:
	for line in f:
		item = json.loads(line)
		en_name = item['en_name']
		ch_name = item['ch_name']
		bookdir = os.sep.join([epub_target_directory, en_name])
		
		# check if book has existed
		if os.path.exists(bookdir):
			print('[EBook Maker]', en_name, 'exists')
			report['existed'].append({
				'en_name': en_name,
				'ch_name': ch_name
			})
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
		
		# archive epub
		# mimetype must be plain text(no compressed), 
		# must be first file in archive, so other inable-unzip 
		# application can read epub's first 30 bytes
		print('[EBook Maker]', en_name, 'archiving...')
		os.chdir(bookdir)
		epubname = '%s.epub' % en_name
		os.system("zip -0Xq %s mimetype" % epubname)
		os.system("zip -Xr9Dq %s *" % epubname)
		
		# check epub file validation
		print('[EBook Maker]', epubname, 'validating...')
		try:
			validation = subprocess.check_output("java -jar %s %s" % (epub_check_path, epubname), 
				stderr=subprocess.STDOUT, 
				shell=True)
		except subprocess.CalledProcessError as e:
			validation = e.output
		invalid = validation.decode('utf-8').find('No errors') < 0
		if invalid:
			print('[EBook Maker]', 'epub has errors', epubname+'.errors')
			report['invalid'].append({
				'en_name': en_name,
				'ch_name': ch_name,
				'message': validation.decode('utf-8')
			})
		else:
			print('[EBook Maker]', 'epub is ok')
			report['valid'].append({
				'en_name': en_name,
				'ch_name': ch_name,
				'message': validation.decode('utf-8')
			})

		# generate .doc
		wordname = '%s.docx' % en_name
		print('[EBook Maker]', wordname, 'generating...')
		os.system('pandoc %s -o %s' % (epubname, wordname))

		# move to product directory
		print('[EBook Maker]', en_name, 'moving...')
		product_epubname = os.sep.join([book_target_directory, '%s.epub' % ch_name])
		product_wordname = os.sep.join([book_target_directory, '%s.docx' % ch_name])
		shutil.move(epubname, product_epubname)
		shutil.move(wordname, product_wordname)
		
		os.chdir(current_directory)

# generate report
print('[EBook Maker]', 'generate report.json')
with open(report_filename, 'w', encoding='utf8') as f:
	f.write(json.dumps(report, ensure_ascii=False, indent=4))