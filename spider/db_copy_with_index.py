#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import string
import sqlite3

reload(sys)
sys.setdefaultencoding('utf-8')


#define method

def insert_url_in_image_table(tiebarUrl, imageUrl, md5, image_size):
    curs.execute('insert into downloaded_image_url (tiebar_url, image_url, md5, image_size) values (?, ?, ?, ?)', (tiebarUrl, imageUrl, md5, image_size))
    conn.commit()

def insert_url_in_parsed_url_table(url, title, datetime):
    curs.execute('insert into parsed_url (url, title, parsed_time) values (?, ?, ?)', (url, title, datetime))
    conn.commit()

def clear_wait_parse_url_table():
    curs.execute('delete from wait_parse_url')
    conn.commit()

def insert_url_in_wait_parse_url_table(url):
    curs.execute('insert into wait_parse_url (url) values (?)', (url,))
    conn.commit()

def insert_urls_in_wait_parse_url_table(url):
    curs.executemany('insert into wait_parse_url (url) values (?)', (url,))
    conn.commit()

#go

#old
conn_from = sqlite3.connect('record.db')
curs_from = conn_from.cursor()

#new
conn = sqlite3.connect('record_index.db')
curs = conn.cursor()
curs.execute('''create table if not exists downloaded_image_url (id INTEGER PRIMARY KEY autoincrement, tiebar_url text, image_url text, md5 text, image_size integer)''')
curs.execute('''create index if not exists downloaded_image_url_index1 on downloaded_image_url(image_url)''')
curs.execute('''create index if not exists downloaded_image_url_index2 on downloaded_image_url(image_size)''')

curs.execute('''create table if not exists parsed_url (id INTEGER PRIMARY KEY autoincrement, url text, title text, parsed_time date)''')
curs.execute('''create table if not exists wait_parse_url (id INTEGER PRIMARY KEY autoincrement, url text)''')

print 'finish create table'

#load downloaded_image_url
curs_from.execute('select * from downloaded_image_url')
while True:
    url = curs_from.fetchone()
    if url is not None:
        print 'downloaded_image_url:', url
        id = url[0]
        tiebar_url = url[1]
        image_url = url[2]
        md5 = url[3]
        image_size = url[4]
        insert_url_in_image_table(tiebar_url, image_url, md5, image_size)
    else:
        break

#load parsed url
curs_from.execute('select * from parsed_url')
while True:
    url = curs_from.fetchone()
    if url is not None:
        print 'parsed_url:', url
        parsed_url = url[1]
        title = url[2]
        parsed_time = url[3]
        insert_url_in_parsed_url_table(parsed_url, title, parsed_time)
    else:
        break

wait_parse_url = []
#load wait parse
curs_from.execute('select * from wait_parse_url')
while True:
    url = curs_from.fetchone()
    if url is not None:
        wait_url = url[1]
        if wait_url not in wait_parse_url:
            print 'wait_parse_url:', url
            wait_parse_url.append(wait_url)
            insert_url_in_wait_parse_url_table(url[1])
    else:
        break

conn_from.close()
conn.close()

print '----------finish load data from table-----------'
