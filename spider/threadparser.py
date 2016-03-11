# -*- coding: utf-8 -*-
import tiebaparser
import urlparse
from recorditem import RecordItem

# 帖子
class ThreadParser (tiebaparser.TieBaHTMLParser):
    def __init__(self, url):
        tiebaparser.TieBaHTMLParser.__init__(self, url)
        # 'd_post_content_main' is for post list and 'l_posts_num' is for page index
        self.tagClasses = {'d_post_content_main': RecordItem(), 'l_posts_num': RecordItem()}
        self.tagIds = {}

    def filter_url(self, url):
        urlparser = urlparse.urlparse(url)
        netlocpath = urlparse.urljoin(urlparser.netloc, urlparser.path)
        if netlocpath == self.netlocpath:
            return True
        else:
            return False
