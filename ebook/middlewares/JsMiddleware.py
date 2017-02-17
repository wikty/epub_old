from scrapy.http import HtmlResponse
from selenium import webdriver

class PhantomjsRequestMiddleware(object):
    def __init__(self, phantomjs_path=None):
        if not phantomjs_path:
            raise Exception('phantomjs path should not be empty')
        self.driver = webdriver.PhantomJS(phantomjs_path)

    @classmethod
    def from_crawler(cls, crawler):
        phantomjs_path = crawler.settings.get('PHANTOMJS_PATH')

        return cls(phantomjs_path)

    def process_request(self, request, spider):
        self.driver.get(request.url)
        body = self.driver.page_source.encode('utf8')
        response = HtmlResponse(url=self.driver.current_url, body=body)
        return response # end any process_request methods


class DynamicPageProxyRequestMiddleware(object):
    def __init__(self, phantomjs_path=None, proxy=None):
        if not phantomjs_path:
            raise Exception('phantomjs path should not be empty')
        if not proxy:
            raise Exception('proxy should not be empty')
        service_args = [
            '--proxy=%s' % proxy,
            '--proxy-type=http',
            '--ignore-ssl-errors=true',
        ]
        self.driver = webdriver.PhantomJS(phantomjs_path, service_args=service_args)

    @classmethod
    def from_crawler(cls, crawler):
        phantomjs_path = crawler.settings.get('PHANTOMJS_PATH')
        proxy = crawler.settings.get('HTTP_PROXY')

        return cls(phantomjs_path, proxy)

    def process_request(self, request, spider):
        self.driver.get(request.url)
        body = self.driver.page_source.encode('utf8')
        response = HtmlResponse(url=self.driver.current_url, body=body)
        return response # end any process_request methods