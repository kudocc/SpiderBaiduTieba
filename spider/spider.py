#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import os
import sys
import string
import Queue
import urlparse
import pprint
from pybloom import ScalableBloomFilter
from HTMLParser import HTMLParser
import homeparser
import threadparser
import sqlite3
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

#init
basePath = '/Users/kudocc/Desktop/papapa/'
initial_page = 'http://tieba.baidu.com/f?ie=utf-8&kw=%E6%9D%80%E6%88%AE%E9%83%BD%E5%B8%82'
#initial_page = 'http://tieba.baidu.com/p/4308012877'
url_queue = Queue.Queue()

parsed_urls = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)
downloaded_image_urls = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)

#load context from file
conn = sqlite3.connect('record.db')
curs = conn.cursor()
curs.execute('''create table if not exists downloaded_image_url (id INTEGER PRIMARY KEY autoincrement, url text)''')
curs.execute('''create table if not exists parsed_url (id INTEGER PRIMARY KEY autoincrement, url text)''')
curs.execute('''create table if not exists wait_parse_url (id INTEGER PRIMARY KEY autoincrement, url text)''')
print 'finish create table'

#load downloaded image urls
curs.execute('select url from downloaded_image_url')
while True:
    url = curs.fetchone()
    if url is not None:
        print 'downloaded image url:', url[0]
        downloaded_image_urls.add(url[0])
    else:
        break
#load parsed urls
curs.execute('select url from parsed_url')
while True:
    url = curs.fetchone()
    if url is not None:
        print 'parsed url:', url[0]
        parsed_urls.add(url[0])
    else:
        break
#load wait parse queue urls
curs.execute('select url from wait_parse_url')
while True:
    url = curs.fetchone()
    if url is not None:
        print 'wait parse url:', url[0]
        url_queue.put(url[0])
    else:
        break
print 'finish load data from table'

def insert_url_in_image_table(url):
    curs.execute('insert into downloaded_image_url (url) values (?)', (url,))
    conn.commit()

def insert_url_in_parsed_url_table(url):
    curs.execute('insert into parsed_url (url) values (?)', (url,))
    conn.commit()

def clear_wait_parse_url_table():
    curs.execute('delete from wait_parse_url')
    conn.commit()

def insert_url_in_wait_parse_url_table(url):
    curs.execute('insert into wait_parse_url (url) values (?)', (url,))
    conn.commit()

def insert_urls_in_wait_parse_url_table(list):
    curs.executemany('insert into wait_parse_url (url) values (?)', list)
    conn.commit()

def is_url_home(url):
    dictionary = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
    if 'kw' in dictionary:
        return True
    else:
        return False

def extract_urls(url):
    print 'begin parse url:', url
    m = None
    if is_url_home(url):
        m = homeparser.HomeParser(url)
    else:
        m = threadparser.ThreadParser(url)

    directory = os.path.join(basePath, url)
    try:
        stream = urllib2.urlopen(url)
        str = stream.read()
        soup = BeautifulSoup(str, 'html.parser')
        pretty_str = soup.prettify()
        print pretty_str
        m.feed(pretty_str)
        print 'after feed'
    except (urllib2.URLError, ) as e:
        print 'exception raised when parse url:', url, 'reason:', e.reason
        return []

    # make dir
    if not os.path.exists(directory):
        os.makedirs(directory)
    # download images
    for imageUrl in m.imageUrls:
        if imageUrl in downloaded_image_urls:
            continue
        downloaded_image_urls.add(imageUrl)
        insert_url_in_image_table(imageUrl)
        imageName = None
        indexOfSlash = string.rfind(imageUrl, '/')
        if indexOfSlash != -1:
            imageName = imageUrl[indexOfSlash+1:]
        else:
            imageName = str(datetime.datetime.utcnow())
        print 'downloaded image url:', imageUrl
        if imageName is not None:
            try:
                stream = urllib2.urlopen(imageUrl)
                if stream is not None and stream.getcode() >= 200:
                    s = stream.read()
                    filePath = os.path.join(directory, imageName)
                    file = open(filePath, 'wb+')
                    file.write(s)
                    file.close()
                    print 'downloaded image url:', imageUrl, ' at location:', filePath
            except (urllib2.URLError, Exception) as e:
                print 'exception raised when download ', imageUrl , ' reason:', e.reason

    # finish parsing url
    parsed_urls.add(url)
    insert_url_in_parsed_url_table(url)

    return m.urls

def main():
    
    if url_queue.empty():
        url_queue.put(initial_page)

    current_url = None
    try:
        while(True):
            if url_queue.qsize() > 0:
                current_url = url_queue.get()
                urls = extract_urls(current_url)
                print 'extract url:', current_url, 'result:', urls
                for next_url in urls:
                    if next_url not in parsed_urls:
                        url_queue.put(next_url)
            else:
                break

    except KeyboardInterrupt:
        clear_wait_parse_url_table()
        if current_url is not None:
            insert_url_in_wait_parse_url_table(current_url)
        if not url_queue.empty():
            list = []
            while url_queue.qsize() > 0:
                url = url_queue.get()
                list.append((url, ))
            insert_urls_in_wait_parse_url_table(list)
        conn.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

main()