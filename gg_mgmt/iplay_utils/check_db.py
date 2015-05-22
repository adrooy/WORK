#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
import datetime
from utils import forum_data_conn, getTimeStamp, getDate


DATE = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
time_stamp = getTimeStamp(DATE)          


@forum_data_conn
def update_topicInfo(db):
    time_stamp = getTimeStamp(DATE)
    topicInfo = False
    sql = "SELECT count(0) FROM  iplay_topic_info WHERE enabled=0 AND topic_date<>0 AND topic_date<=%s AND (unrelease_date=0 or unrelease_date>%s) " % (time_stamp, time_stamp) 
    db.execute(sql)
    number = int(db.fetchall()[0][0])
    if number:
        topicInfo = True
    sql = "SELECT count(0) FROM iplay_topic_info WHERE enabled=1 AND unrelease_date<>0 AND unrelease_date<=%s" % time_stamp
    db.execute(sql)
    number = int(db.fetchall()[0][0])
    if number:
        topicInfo = True
    sql = "UPDATE iplay_topic_info SET enabled=1 WHERE enabled=0 AND topic_date<>0 AND topic_date<=%s" % time_stamp
    db.execute(sql)
    #下线
    sql = "UPDATE iplay_topic_info SET enabled=0 WHERE enabled=1 AND unrelease_date<>0 AND unrelease_date<=%s" % time_stamp
    db.execute(sql)
    return topicInfo

@forum_data_conn
def update_recommendBanner(db):
    time_stamp = getTimeStamp(DATE)          
    #print [time_stamp]
    recommendBanner = False
    sql = "SELECT count(0) FROM iplay_recomend_banner_info WHERE enabled=0 AND release_date<>0 AND release_date<=%s AND (unrelease_date=0 or unrelease_date>%s) " % (time_stamp, time_stamp)
    db.execute(sql)
    number = int(db.fetchall()[0][0])
    if number:
        recommendBanner = True
    sql = "SELECT count(0) FROM iplay_recomend_banner_info WHERE enabled=1 AND unrelease_date<>0 AND unrelease_date<=%s" % time_stamp
    db.execute(sql)
    number = int(db.fetchall()[0][0])
    if number:
        recommendBanner = True
    sql = "UPDATE iplay_recomend_banner_info SET enabled=1 WHERE enabled=0 AND release_date<>0 AND release_date<=%s" % time_stamp
    db.execute(sql)
    #下线
    sql = "UPDATE iplay_recomend_banner_info SET enabled=0 WHERE enabled=1 AND unrelease_date<>0 AND unrelease_date<=%s" % time_stamp
    db.execute(sql)
    return recommendBanner

@forum_data_conn
def update_recommendGame(db):
    time_stamp = getTimeStamp(DATE)          
    #print [time_stamp]
    recommendGame = False
    sql = "SELECT count(0) FROM iplay_recomend_game WHERE enabled=0 AND release_date<>0 AND release_date<=%s AND (unrelease_date=0 or unrelease_date>%s) " % (time_stamp, time_stamp)
    db.execute(sql)
    number = int(db.fetchall()[0][0])
    if number:
        recommendGame = True
    sql = "SELECT count(0) FROM iplay_recomend_game WHERE enabled=1 AND unrelease_date<>0 AND unrelease_date<=%s" % time_stamp
    db.execute(sql)
    number = int(db.fetchall()[0][0])
    if number:
        recommendGame = True
    sql = "UPDATE iplay_recomend_game SET enabled=1 WHERE enabled=0 AND release_date<>0 AND release_date<=%s" % time_stamp
    db.execute(sql)
    #下线
    sql = "UPDATE iplay_recomend_game SET enabled=0 WHERE enabled=1 AND unrelease_date<>0 AND unrelease_date<=%s" % time_stamp
    db.execute(sql)
    return recommendGame

@forum_data_conn
def update_categoryGame(db):
    time_stamp = getTimeStamp(DATE)          
    #print [time_stamp]
    categoryGame = False
    sql = "SELECT count(0) FROM iplay_category_game_order_adjust WHERE enabled=0 AND release_date<>0 AND release_date<=%s AND (unrelease_date=0 or unrelease_date>%s) " % (time_stamp, time_stamp)
    db.execute(sql)
    number = int(db.fetchall()[0][0])
    if number:
        categoryGame = True
    sql = "SELECT count(0) FROM iplay_category_game_order_adjust WHERE enabled=1 AND unrelease_date<>0 AND unrelease_date<=%s" % time_stamp
    db.execute(sql)
    number = int(db.fetchall()[0][0])
    if number:
        categoryGame = True
    sql = "UPDATE iplay_category_game_order_adjust SET enabled=1 WHERE enabled=0 AND release_date<>0 AND release_date<=%s" % time_stamp
    db.execute(sql)
    #下线
    sql = "UPDATE iplay_category_game_order_adjust SET enabled=0 WHERE enabled=1 AND unrelease_date<>0 AND unrelease_date<=%s" % time_stamp
    db.execute(sql)
    return categoryGame

def release():
    os.system('python /root/operation/step_09_gen_mapping_tables_for_service/09_8_gen_category_to_game_result.py')
    os.system("wget -O - 'http://127.0.0.1:8080/gamecommunity/instruction!clear.action?name=table'")

def main():
    topicInfo = update_topicInfo()
    recommendBanner = update_recommendBanner()
    recommendGame = update_recommendGame()
    categoryGame = update_categoryGame()
    print topicInfo
    print recommendGame
    print recommendBanner
    print categoryGame
    if topicInfo or recommendGame or recommendBanner or categoryGame:
        release()

if __name__ == '__main__':
    main()
