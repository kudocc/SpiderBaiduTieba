# -*- coding: utf-8 -*-
import tiebaparser
import urlparse
from recorditem import RecordItem

# 贴吧首页
class HomeParser (tiebaparser.TieBaHTMLParser):
    def __init__(self, url):
        tiebaparser.TieBaHTMLParser.__init__(self, url)
        self.tagClasses = {}
        # 'thread_list' is for thread, 'frs_list_pager' is for page index
        self.tagIds = {'thread_list': RecordItem(), 'frs_list_pager': RecordItem()}
        self.param_kw = self.query_string_value_of_key(url, 'kw')
    
    def query_string_value_of_key(self, url, key):
        dictionary = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
        if key in dictionary:
            return dictionary[key]
        else:
            return None;

    def filter_url(self, url):
        parser = urlparse.urlparse(url)
        path = urlparse.urljoin(parser.netloc, parser.path)
        # if path is not equal to self.netlocpath, it is other home page or it is a thread
        if not path == self.netlocpath:
            if url.startswith('http://tieba.baidu.com/p'):
                return True
            else:
                return False
        kw = self.query_string_value_of_key(url, 'kw')
        if kw == self.param_kw:
            return True
        else:
            return False