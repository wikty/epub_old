from optparse import OptionParser
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

parser = OptionParser()
parser.add_option('-n', '--name', dest='spider_name', help='run the specific name spider')
(options, args) = parser.parse_args()

if options.spider_name:
	process = CrawlerProcess(get_project_settings())
	process.crawl(options.spider_name)
	process.start()