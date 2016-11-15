# -*- coding: utf-8 -*-
import random

# The proxy host format like: ip:port or username:password@ip:port

class RandomProxyMiddleware(object):
	def __init__(self, proxies):
		self.proxies = proxies

	@classmethod
	def from_crawler(cls, crawler):
		proxy_list = []
		with open(crawler.settings.get('PROXY_LIST'), 'r') as f:
			proxy_list = [ip.strip() for ip in f]

		return cls(proxy_list)

	def process_request(self, request, spider):
		request.meta['proxy'] = 'http://{}'.format(random.choice(self.proxies))
		print('Proxy:', request.meta['proxy'])