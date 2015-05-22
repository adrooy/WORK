#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'duchunhai'


import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)

from database.mysql_client import connections

THREAD_TABLE = 'forum.pre_forum_thread'
TYPE_OPTION_TABLE = 'forum.pre_forum_typeoption'
TYPE_OPTION_VAR_TABLE = 'forum.pre_forum_typeoptionvar'
GAME_LABEL_TABEL = 'forum.iplay_game_label_info'
GAME_PKG_TABLE = 'forum.iplay_game_pkg_info'
CATEGORY_TABLE = 'forum.iplay_game_category_info'
FORECAST_TABLE = 'forum.iplay_game_forecast_info'

formurlbase = 'forum/forum.php?mod=forumdisplay&fid=%d'


# dic : category name to forum category id
def generate_lv1_cat_dic():
    dic = dict()
    dic["休闲时间"] = 49
    dic["跑酷竞速"] = 48
    dic["宝石消除"] = 47
    dic["网络游戏"] = 46
    dic["动作射击"] = 45
    dic["扑克棋牌"] = 44
    dic["儿童益智"] = 43
    dic["塔防守卫"] = 42
    dic["体育格斗"] = 41
    dic["角色扮演"] = 40
    dic["经营策略"] = 39
    dic["破解"] = 2
    dic["其他"] = 2
    return dic


# dic : category name to forum category id
def generate_lv2_cat_dic(conn):

    lv1dic = generate_lv1_cat_dic()
    dic = dict()
    cur = conn.cursor()
    cur.execute("select * from %s " % CATEGORY_TABLE)

    cats = cur.fetchall()
    dic_id_to_name = dict()
    for cat in cats:
        cat_id = str(int(cat['id']))
        dic_id_to_name[cat_id] = lv1dic[cat['name']]
    return dic_id_to_name


def generate_label_form_url(conn):
    cur = conn.cursor()

    lv1_cat_dic = generate_lv1_cat_dic()
    lv2_cat_dic = generate_lv2_cat_dic(conn)

    cur.execute("select * from %s WHERE game_id NOT IN ('3e73c512')" % GAME_LABEL_TABEL)
    labels = cur.fetchall()

    n = 0
    for label in labels:
        gameId = label["game_id"]
        types = label["origin_types"]
        fid = 0
        if not types or len(types) == 0:
            fid = 2
        else:
            cats = types.split("\n")

        if fid == 0:
            for cat in cats:
                if lv1_cat_dic.has_key(cat):
                    fid = lv1_cat_dic[cat]
                    break
        if fid == 0:
            for cat in cats:
                if lv2_cat_dic.has_key(cat):
                    fid = lv2_cat_dic[cat]
                    break
        if fid == 0:
            fid = 2
        form_url = formurlbase % fid
        sqlstr = "update %s set forum_url = '%s' where game_id = '%s'" % (GAME_LABEL_TABEL, form_url, gameId.encode('ascii'))
        cur.execute(sqlstr)
        n += 1
    print "update %d lable info" % n


def generate_pkg_form_url(conn):
    cur = conn.cursor()

    lv1_cat_dic = generate_lv1_cat_dic()
    lv2_cat_dic = generate_lv2_cat_dic(conn)

    cur.execute("select * from %s WHERE game_id NOT IN ('3e73c512')" % GAME_PKG_TABLE)
    labels = cur.fetchall()

    n = 0
    for label in labels:
        apkid = label["apk_id"]
        types = label["origin_types"]
        fid = 0
        if not types or len(types) == 0:
            fid = 2
        else:
            cats = types.split("\n")

        if fid == 0:
            for cat in cats:
                if lv1_cat_dic.has_key(cat):
                    fid = lv1_cat_dic[cat]
                    break
        if fid == 0:
            for cat in cats:
                if lv2_cat_dic.has_key(cat):
                    fid = lv2_cat_dic[cat]
                    break
        if fid == 0:
            fid = 2
        form_url = formurlbase % fid
        sqlstr = "update %s set forum_url = '%s' where apk_id = '%s'" % (GAME_PKG_TABLE, form_url, apkid.encode('ascii'))
        cur.execute(sqlstr)
        n += 1
    # hard code for DaoTaChuanQi forum url
    sqlstr = "UPDATE %s SET forum_url = 'forum/forum.php?mod=forumdisplay&fid=62' WHERE game_id = '3e73c512'" % GAME_PKG_TABLE
    cur.execute(sqlstr)
    print "update %d pkg info" % n


def generate_forecast_form_url(conn):
    cur = conn.cursor()

    lv1_cat_dic = generate_lv1_cat_dic()
    lv2_cat_dic = generate_lv2_cat_dic(conn)

    cur.execute("select * from %s" % FORECAST_TABLE)
    labels = cur.fetchall()

    n = 0
    for label in labels:
        apkid = label["game_id"]
        types = label["category_ids"]
        fid = 0
        if not types or len(types) == 0:
            fid = 2
        else:
            cats = types.split(",")

        if fid == 0:
            for cat in cats:
                if lv1_cat_dic.has_key(cat):
                    fid = lv1_cat_dic[cat]
                    break
        if fid == 0:
            for cat in cats:
                if lv2_cat_dic.has_key(cat):
                    fid = lv2_cat_dic[cat]
                    break
        if fid == 0:
            fid = 2
        form_url = formurlbase % fid
        sqlstr = "update %s set forum_url = '%s' where game_id = '%s'" % (FORECAST_TABLE, form_url, apkid.encode('ascii'))
        cur.execute(sqlstr)
        n += 1
    print "update %d forecast info" % n


print 'START STEP : %s' % __file__
conn = connections('DictCursor')
generate_label_form_url(conn)
generate_pkg_form_url(conn)
generate_forecast_form_url(conn)
if conn:
    conn.commit()
if conn:
    conn.close()
