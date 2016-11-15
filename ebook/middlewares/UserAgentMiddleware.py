# -*- coding: utf-8 -*-
import random

class RandomUserAgentMiddleware(object):
    def __init__(self, agents=['Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)']):
        self.agents = agents

    @classmethod
    def from_crawler(cls,crawler):
        # instance of the current class
        ua_list = []
        with open(crawler.settings.get('USER_AGENT_LIST'), 'r') as f:
            ua_list = [ua.strip() for ua in f]

        return cls(ua_list)

    def process_request(self, request, spider):
        ua = random.choice(self.agents)
        request.headers.setdefault('User-Agent', ua)
        print('User-Agent:', ua)
