#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import string
import sqlite3
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

def test_select_url(curs):
    url = 'http://imgsrc.baidu.com/forum/wh%3D160%2C90/sign=2fb54fb05eee3d6d22938fca7526411b/157adab44aed2e73f55cda3b8001a18b87d6fa74.jpg'
    before = datetime.datetime.today()
    curs.execute('select * from downloaded_image_url where image_url=?', (url, ))
    while True:
        row = curs.fetchone()
        if row is not None:
            print 'select downloaded_image_url:', row
        else:
            break
    after = datetime.datetime.today()
    diff = after - before
    return diff.total_seconds()

def test_sort_image_size(curs):
    before = datetime.datetime.today()
    curs.execute('select * from downloaded_image_url order by image_size desc limit 5')
    while True:
        row = curs.fetchone()
        if row is not None:
            print 'sort downloaded_image_url:', row
        else:
            break
    after = datetime.datetime.today()
    diff = after - before
    return diff.total_seconds()

#test common db

conn = sqlite3.connect('record.db')
curs = conn.cursor()

time_test_select_url = test_select_url(curs)
time_test_sort_image_size = test_sort_image_size(curs)

conn.close()

#test index

conn_index = sqlite3.connect('record_index.db')
curs_index = conn_index.cursor()

index_time_test_select_url = test_select_url(curs_index)
index_time_test_sort_image_size = test_sort_image_size(curs_index)

conn_index.close()


print '---------------------------'
print 'commond db select:', time_test_select_url
print 'commond db sort:', time_test_sort_image_size
print 'index db select:', index_time_test_select_url
print 'index db sort:', index_time_test_sort_image_size
print '---------------------------'
