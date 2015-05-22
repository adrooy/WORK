# coding=utf-8
# 第一步: 把所有匹配到的source!=3的pkg对应的label的game_types里添加上"破解\n辅助专区" (也许还应该禁用同label下不支持插件的pkg, 但可能会导致"我的游戏"匹配变少, 先不改)
# 第二步: 把所有匹配到的source!=3的pkg的game_types里添加上"破解\n辅助专区"
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.mysql_client import connections
import re
THREAD_TABLE = "`forum`.`pre_forum_thread`"
RES_INFO_TABLE = "`forum`.`pre_iplay_game_resource_info`"
RES_CONDITION_TABLE = "`forum`.`pre_iplay_game_resource_match_condition`"
PKG_INFO_TABLE = "`forum`.`iplay_game_pkg_info`"
LABEL_INFO_TABLE = "`forum`.`iplay_game_label_info`"
PKG_LABEL_MAPPING_TABLE = "`forum`.`iplay_game_label_to_pkg_result`"
MAPPING_TABLE = "`forum`.`iplay_resource_match_result`"
CATEGORY_TABLE = "`forum`.`iplay_game_category_info`"

all_plugin_ids = []
lv1_cat_dic = {}
lv2_cat_dic = {}


def init_all_plugin_ids(cur):
    cur.execute("SELECT DISTINCT(`id`) FROM %s where resource_type = 1" % RES_INFO_TABLE)
    for row in cur.fetchall():
        all_plugin_ids.append(row['id'])


def init_category_id_dic(cur):
    global lv1_cat_dic, lv2_cat_dic

    cur.execute("select `name`, `id`, `parent_id` from %s" % CATEGORY_TABLE)
    for row in cur.fetchall():
        if row['parent_id'] == 0:
            lv1_cat_dic[row['name']] = row['id']
        else:
            lv2_cat_dic[row['name']] = row['id']


# step 1
def update_label_game_types(cur):
    cur.execute("UPDATE %s set `game_types` = ''" % LABEL_INFO_TABLE)
    label_ids = []
    n = 0
    cur.execute("SELECT `label_id`, `resource_id` FROM %s INNER JOIN %s ON %s.`pkg_id` = %s.`apk_id` " % (PKG_LABEL_MAPPING_TABLE, MAPPING_TABLE, PKG_LABEL_MAPPING_TABLE, MAPPING_TABLE))
    for row in cur.fetchall():
        if row['resource_id'] in all_plugin_ids and row['label_id'] not in label_ids:
            label_ids.append(row['label_id'])
            n += 1
    sqlstr = "UPDATE %s set `game_types` = '破解\n辅助专区' where `game_id` in (%s) and %s.`source` <> 3" % (LABEL_INFO_TABLE, ",".join("'" + c + "'" for c in label_ids), LABEL_INFO_TABLE)
    cur.execute(sqlstr)
    print "update %d label game types" % n


# step 2
def update_pkg_game_types(cur):
    cur.execute("UPDATE %s set `game_types` = ''" % PKG_INFO_TABLE)
    apk_ids = []
    n = 0
    cur.execute("SELECT `apk_id`, `resource_id` FROM %s " % MAPPING_TABLE)
    for row in cur.fetchall():
        if row['resource_id'] in all_plugin_ids and row['apk_id'] not in apk_ids:
            apk_ids.append(row['apk_id'])
            n += 1
    sqlstr = "UPDATE %s set `game_types` = '破解\n辅助专区' where `apk_id` in (%s) and %s.`source` <> 3" % (PKG_INFO_TABLE, ",".join("'" + c + "'" for c in apk_ids), PKG_INFO_TABLE)
    cur.execute(sqlstr)
    print "update %d label game types" % n


def update_label_category_id(cur):
    cur.execute("select * from %s" % LABEL_INFO_TABLE)
    labels = cur.fetchall()

    n = 0
    for label in labels:
        game_id = label["game_id"]
        types = label["origin_types"]
        category_id = 0
        if not types or len(types) == 0:
            category_id = 2
        else:
            cats = types.split("\n")

        if category_id == 0:
            for cat in cats:
                if lv1_cat_dic.has_key(cat):
                    category_id = lv1_cat_dic[cat]
                    break
        if category_id == 0:
            for cat in cats:
                if lv2_cat_dic.has_key(cat):
                    category_id = lv2_cat_dic[cat]
                    break
        if category_id == 0:
            category_id = 2
        sqlstr = "update %s set category_id = '%d' where game_id = '%s'" % (LABEL_INFO_TABLE, category_id, game_id)
        cur.execute(sqlstr)
        n += 1
    print "update %d lable category_id" % n


print 'START STEP : %s' % __file__
conn = connections('DictCursor')
cursor = conn.cursor()

#init_all_plugin_ids(cursor)
#update_label_game_types(cursor)
#update_pkg_game_types(cursor)

init_category_id_dic(cursor)
update_label_category_id(cursor)

if cursor:
    cursor.close()
if conn:
    conn.close()
