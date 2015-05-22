#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.mysql_client import connections
__author__ = 'duchunhai'

LABEL_INFO_TABLE = "`forum`.`iplay_game_label_info`"
PKG_INFO_TABLE = "`forum`.`iplay_game_pkg_info`"
DL_STATIC_TABLE = "`iplayReport`.`iplay_download_static_newgen_view`"


def gen_pkg_dl_sum_info_week(ymd):
    print "gen_pkg_dl_sum_info_week..."
    conn = connections('DictCursor')
    cur = conn.cursor()
    pkg_to_dl_cnt = {}
    cur.execute("SELECT content_id, SUM(counts) AS cnt FROM %s WHERE content_type = 'gamepackage' AND ymd>%s GROUP BY content_id" % (DL_STATIC_TABLE, ymd))
    for row in cur.fetchall():
        pkg_to_dl_cnt[row["content_id"]] = row["cnt"]
    return pkg_to_dl_cnt


def gen_label_dl_sum_info(last_7_pkg_to_dl_cnt, pkg_to_dl_cnt):
    print "gen_label_dl_sum_info..."
    conn = connections('DictCursor')
    cur = conn.cursor()
    label_to_dl_cnt = {}
    last_7_label_to_dl_cnt = {}
    cur.execute("SELECT DISTINCT label.`game_id` FROM %s label RIGHT JOIN %s pkg ON label.game_id = pkg.game_id WHERE pkg.is_plugin_required = 1  OR label.source = 2 OR label.source = 3 OR label.source = 4 AND label.enabled = 1" % (LABEL_INFO_TABLE, PKG_INFO_TABLE))

    for row in cur.fetchall():
        label_id = row["game_id"]
        cur.execute("SELECT apk_id FROM %s WHERE game_id = '%s'" % (PKG_INFO_TABLE, label_id))
        cnt = 0
        week = 0
        for apk in cur.fetchall():
            if apk["apk_id"] in pkg_to_dl_cnt:
                cnt += pkg_to_dl_cnt[apk["apk_id"]]
            if apk["apk_id"] in last_7_pkg_to_dl_cnt:
                week += last_7_pkg_to_dl_cnt[apk["apk_id"]]
        label_to_dl_cnt[label_id] = cnt
        last_7_label_to_dl_cnt[label_id] = week
    cur.close()
    conn.close()
    return last_7_label_to_dl_cnt, label_to_dl_cnt


def gen_pkg_dl_sum_info():
    print "gen_pkg_dl_sum_info..."
    conn = connections('DictCursor')
    cur = conn.cursor()
    pkg_to_dl_cnt = {}
    cur.execute("SELECT content_id, SUM(counts) AS cnt FROM %s WHERE content_type = 'gamepackage' GROUP BY content_id" % DL_STATIC_TABLE)
    for row in cur.fetchall():
        pkg_to_dl_cnt[row["content_id"]] = row["cnt"]
    return pkg_to_dl_cnt


def update_label_sum_info(conn_cur_str, label_dic, week_label_dic):
    print "update_label_sum_info...", conn_cur_str
    conn = connections(conn_cur_str)
    cur = conn.cursor()

    with open('%s/label_download_cnt' % BASE_DIR, 'w') as files:
        for label_id in label_dic:
            gg_download_week = week_label_dic[label_id] if label_id in week_label_dic else 0
            if label_dic[label_id] != 0:
                cur.execute("UPDATE %s SET gg_download_cnt = %d, gg_download_week = %d WHERE game_id = '%s'" % (LABEL_INFO_TABLE, label_dic[label_id], gg_download_week, label_id))
                files.write('%s,%d,%d\n' % (label_id, label_dic[label_id], gg_download_week))

    cur.close()
    conn.close()


def update_pkg_sum_info(conn_cur_str, pkg_dic, week_pkg_dic):
    print "update_pkg_sum_info...", conn_cur_str
    conn = connections(conn_cur_str)
    cur = conn.cursor()

    with open('%s/pkg_download_cnt' % BASE_DIR, 'w') as files:
        for apk_id in pkg_dic:
            gg_download_week = week_pkg_dic[apk_id] if apk_id in week_pkg_dic else 0
            if pkg_dic[apk_id] != 0:
                cur.execute("UPDATE %s SET gg_download_cnt = %d, gg_download_week = %d WHERE apk_id = '%s'" % (PKG_INFO_TABLE, pkg_dic[apk_id], gg_download_week, apk_id))
                files.write('%s,%d,%d\n' % (apk_id, pkg_dic[apk_id], gg_download_week))

    cur.close()
    conn.close()


def update_dl_cnt():
    #七天前
    print '/n/n/n'
    print 'START'
    print datetime.datetime.now()
    ymd = (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y%m%d')
    week_pkg_dic = gen_pkg_dl_sum_info_week(ymd)
    pkg_dic = gen_pkg_dl_sum_info()
    week_label_dic, label_dic = gen_label_dl_sum_info(week_pkg_dic, pkg_dic)
    #update_label_sum_info('LinodeDictCursor', label_dic, week_label_dic)
    update_label_sum_info('DictCursor', label_dic, week_label_dic)
    #update_pkg_sum_info('LinodeDictCursor', pkg_dic, week_pkg_dic)
    update_pkg_sum_info('DictCursor', pkg_dic, week_pkg_dic)
    print 'END'


if __name__ == '__main__':
    update_dl_cnt()
