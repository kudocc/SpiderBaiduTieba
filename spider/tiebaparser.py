import HTMLParser
import urlparse
from recorditem import RecordItem

#parse TieBa main page
class TieBaHTMLParser(HTMLParser.HTMLParser):
    def __init__(self, url):
        HTMLParser.HTMLParser.__init__(self)
        
        self.current_url = url
        urlparser = urlparse.urlparse(self.current_url)
        self.netlocpath = urlparse.urljoin(urlparser.netloc, urlparser.path)
        # if class of tag equals to tagClass, get the url and imageUrl
        self.tagClasses = {'p_postlist': RecordItem()}
        self.tagIds = {'thread_theme_5': RecordItem(), 'thread_list': RecordItem()}
        
        self.meet_title = False
        self.title = ''
        self.urls = []
        self.imageUrls = []
    
    def get_item_class(self, className):
        if className in self.tagClasses:
            return self.tagClasses[className]
        return None
    
    def get_item_id(self, idName):
        if idName in self.tagIds:
            return self.tagIds[idName]
        return None
    
    def get_one_item(self):
        for key in self.tagClasses:
            value = self.tagClasses[key]
            if value.records > 0:
                return value
        for key in self.tagIds:
            value = self.tagIds[key]
            if value.records > 0:
                return value
        return None
    
    def get_item(self, attrs):
        for pair in attrs:
            item = None
            key = pair[0]
            value = pair[1]
            if key == 'class':
                valueArr = value.split(' ')
                for v in valueArr:
                    if len(v) == 0:
                        continue
                    item = self.get_item_class(v)
                    if item is not None:
                        return item
            elif key == 'id':
                item = self.get_item_id(value)
                if item is not None:
                    return item
        return None
    
    def is_attrs_good(self, attrs):
        for pair in attrs:
            key = pair[0]
            value = pair[1]
            if key == 'class':
                valueArr = value.split(' ')
                for v in valueArr:
                    if len(v) == 0:
                        continue
                    if v in self.tagClasses:
                        return True
            if key == 'id':
                if value in self.tagIds:
                    return True
        return False
    
    # subclass should override it
    def filter_url(self, url):
        '''return True, if `url` need to parse, else return False'''
        return True
    
    def handle_endtag(self, tag):
        if tag == 'title':
            self.meet_title = False
        
        item = self.get_one_item()
        if item is None:
            return
        item.records -= 1
        #print 'end tag:', tag, ' record:', item.records
    
    def handle_data(self, data):
        if self.meet_title:
            self.title = data

    def handle_starttag(self, tag, attrs):
        
        if tag == 'title':
            self.meet_title = True
        
        item = None
        
        # this attrs is fit
        if self.is_attrs_good(attrs):
            #print 'attrs_good tag:', tag, ' attrs:', attrs
            itemAnother = self.get_one_item()
            if itemAnother is not None:
                raise 'overlap!!!'
            
            item = self.get_item(attrs)
            item.records = 1
            item.tagName = tag
        else:
            item = self.get_one_item()
            if item is None:
                return
            #print 'attrs not good tag:', tag, ' attrs:', attrs
            item.records += 1
        
        if tag == 'a':
            url = ''
            for pair in attrs:
                if pair[0] == 'href':
                    url = pair[1]
                    break
            if len(url) == 0:
                return
            
            parse = urlparse.urlparse(url)
            if len(parse.netloc) == 0 and url.startswith('/'):
                url = urlparse.urljoin(self.current_url, url)
            if self.filter_url(url):
                #print 'url pass, url:', url
                self.urls.append(url)
            else:
                pass
                #print 'url forbidden, url:', url
            
        elif tag == 'img':
            url = ''
            for pair in attrs:
                if pair[0] == 'src':
                    url = pair[1]
                    break
            if url:
                if url.startswith('http'):
                    self.imageUrls.append(url)

