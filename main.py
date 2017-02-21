import os
from optparse import OptionParser
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

parser = OptionParser()
parser.add_option('-n', '--name', dest='spider_name', help='run the specific name spider')
parser.add_option('-a', '--arguments', dest='arguments', help='arguments for the spider, e.g k1=v1;k2=v2')
parser.add_option('-j', '--job', dest='job', help='crawl persistence')
(options, args) = parser.parse_args()

if options.spider_name:
	cmd = 'scrapy crawl %s' % options.spider_name
	if options.job:
		cmd = cmd + ' -s JOBDIR=jobdir'
	if options.arguments:
		cmd = cmd + ' -a %s' % ' -a '.join(options.arguments.split(';'))
	os.system(cmd)
else:
	print('please type your spider name')

# example:
# python main.py -n ctext-book -a book_list_file=booklist.jl;book_num=5

# if options.spider_name:
# 	process = CrawlerProcess(get_project_settings())
# 	process.crawl(options.spider_name)
# 	process.start()