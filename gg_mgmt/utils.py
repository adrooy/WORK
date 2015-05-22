#-*- coding:utf-8 -*-


import time
import MySQLdb
import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.db import connections

from HTMLParser import HTMLParser 
from re import sub 
from sys import stderr 
from traceback import print_exc 
 

class _DeHTMLParser(HTMLParser): 
    def __init__(self): 
        HTMLParser.__init__(self) 
        self.__text = [] 
 
    def handle_data(self, data): 
        text = data.strip() 
        if len(text) > 0: 
            text = sub('[ \t\r\n]+', ' ', text) 
            self.__text.append(text + ' ') 
 
    def handle_starttag(self, tag, attrs): 
        if tag == 'p': 
#            self.__text.append('\n\n') 
            self.__text.append('\n') 

        elif tag == 'br': 
            self.__text.append('\n') 
 
    def handle_startendtag(self, tag, attrs): 
        if tag == 'br': 
   #         self.__text.append('\n\n') 
            self.__text.append('\n') 
 
    def text(self): 
        return ''.join(self.__text).strip() 


def dehtml(text): 
    try: 
        parser = _DeHTMLParser() 
        parser.feed(text) 
        parser.close() 
        return parser.text() 
    except: 
        print_exc(file=stderr) 
        return text 
 

def get_pagination(request, queryset, per_page, after_range_num=5, before_range_num=4):
    paginator = Paginator(queryset, per_page)
    count_page = len(queryset) / per_page
    try:
        page_num = int(request.GET.get('pn'))  # 页码
    except:
        page_num = 1  # 默认为1
    try:
        objects = paginator.page(page_num)  # 尝试获得分页列表
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)  # 如果页数不存在，获得最后一页
    except PageNotAnInteger:
        objects = paginator.page(1)  # 如果不是一个整数，获得第一页
    #根据参数配置导航显示范围
    if page_num >= after_range_num:
        page_range = paginator.page_range[page_num - after_range_num: page_num + before_range_num]
    else:
        page_range = paginator.page_range[0: page_num + before_range_num]
    return objects, page_range, per_page, count_page


def get_info(a, b, c, d):
    key = '%s_%s_%s_%s' % (a, b, c, d)
    vari_info = cache.get(key)
    if vari_info is None:
        cursor_m = connections['forum'].cursor()
        cursor_m.execute("SELECT `%s` FROM `%s` WHERE `%s` = '%s'" % (a, b, c,
                    d))
        try:
            vari_info = cursor_m.fetchone()[0]
            cache.set(key, vari_info)
        except Exception:
            vari_info = ''
    return vari_info


def get_vari_value(vari_id, string):
    key = '%s_%s' % (vari_id, string)
    vari_info = cache.get(key)
    if vari_info is None:
        cursor_m = connections['forum'].cursor()
        cursor_m.execute("SELECT `%s` FROM `iplay_article_vari_info` WHERE `vari_id` = '%s'" % (string, vari_id))
        try:
            vari_info = cursor_m.fetchone()[0]
            cache.set(key, vari_info)
        except Exception:
            vari_info = ''
    return vari_info


def get_game_info(game_id, string):
    key = '%s_%s' % (game_id, string)
    game_info = cache.get(key)
    if game_info is None:
        cursor_m = connections['forum'].cursor()
        cursor_m.execute("SELECT `%s` FROM `iplay_game_label_info` WHERE `game_id` = '%s'" % (string, game_id))
        try:
            game_info = cursor_m.fetchone()[0]
            cache.set(key, game_info)
        except Exception:
            game_info = ''
    return game_info


def get_timestamp(date):
    timeArray = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def get_date(timeStamp):
    if timeStamp:
        timeArray = time.localtime(timeStamp)
        date = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
    else:
        date = ''
    return date


def get_apk_size(size):
    if size/1024.0/1024.0/1024.0 >= 1:
        return '%sＧ' % str(round((size/1024.0/1024.0/1024.0),2))
    if size/1024.0/1024.0 >= 1:
        return '%sＭＢ' % str(round((size/1024.0/1024.0),2))
    if sizi/1024.0:
        return '%sＫＢ' % str(round((size/1024.0),2))
    return '%sＢ' % size


def get_download_cnt(cnt):
    if not cnt:
        return '%s次' % str(random.randint(100, 1000))
    if (int(cnt)*random.randint(23, 24))/10000:
        return '%s万次' % str((int(cnt)*random.randint(23, 24))/10000)
    else:
        return '%s次' % str((cnt)*random.randint(23, 24))


def get_sorted(sort_data, sort_keys, sort_key):
#    sort_key = 'a'
#    sort_keys = {'1':{'num': 4,'a':13},'2':{'num': 6,'a':24},'3':{'num': 3, 'a':2}}
#    sorted_keys = {'1':[2,3],'2':[4,8],'3':[1,1]}
#    games = {'1':3,'2':5,'3':2}
    sorted_keys = sorted(sort_keys.items(),key=lambda d:int(d[1][sort_key]),reverse = True)
    sorted_data = []
    number = 1
    for item in sorted_keys:
        game_id = item[0]
        game = sort_data[game_id]
        game.index = number 
        number += 1
        sorted_data.append(game)
    return sorted_data
