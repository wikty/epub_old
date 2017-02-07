# -*- coding: utf-8 -*-
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RandomUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, agents=[]):
        super(RandomUserAgentMiddleware, self).__init__()
        if not agents:
            agents = ['Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)']
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        # instance of the current class
        ua_list = []
        with open(crawler.settings.get('USER_AGENT_LIST'), 'r') as f:
            ua_list = [ua.strip() for ua in f.readlines()]

        return cls(ua_list)

    def process_request(self, request, spider):
        ua = random.choice(self.agents)
        request.headers.setdefault('User-Agent', ua)