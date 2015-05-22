# coding=utf-8
# in pkg_info table, find highest version of given game and given channel, mark it for later use.
# 在渠道包信息(pkg_info)表中, 对每个特定游戏特定渠道, 找出最高版本, 做标记, 用于后续步骤
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.mysql_client import connections
import utils

PKG_INFO_TABLE = "`forum`.`iplay_game_pkg_info`"


def update_is_max_version(cur):

    print "reset is_max_versino to 0..."
    cur.execute("update %s set `is_max_version` = 0" % PKG_INFO_TABLE)

    print "reading pkg info..."
    gameinfo = {} # { (game_id, market_channel) : [ (apk_id, ver_code, ver_name, is_plugin_required), ...  ] }
    cur.execute("select `apk_id`, `game_id`, `market_channel`, `ver_code`, `ver_name`, `ver_code_by_gg` from %s where `enabled` = 1 and (is_plugin_required = 1 or source = 2 or source = 3 or source = 4)" % PKG_INFO_TABLE)
    for row in cur.fetchall():
        key = (row['game_id'], row['market_channel'])
        ver_name = utils.ver_name_to_int(row['ver_name'], row['apk_id'])
        if key in gameinfo.keys():
            gameinfo[key].append( (row['apk_id'], row['ver_code'], ver_name, row['ver_code_by_gg']) )
        else:
            gameinfo[key] = [ (row['apk_id'], row['ver_code'], ver_name, row['ver_code_by_gg']) ]

    print "finding max version pkgs..."
    for key in gameinfo.keys():
        if len(gameinfo[key]) == 1:
            continue
 
        #按ver_code排序，最前面相等的按ver_code_by_gg排序，再相等的按ver_name排序 
        gameinfo[key] = sorted(gameinfo[key], key=lambda tup: (tup[1], tup[3], tup[2]), reverse=True)

        # remove all except the 1st one
        gameinfo[key] = gameinfo[key][0:1]

    print "updating db..."
    for key in gameinfo.keys():
        cur.execute("update %s set `is_max_version` = 1 where `apk_id` = '%s'" % (PKG_INFO_TABLE, gameinfo[key][0][0]))
    #炉石传说
    cur.execute("update %s set `is_max_version` = 1 where `apk_id` = '%s'" % (PKG_INFO_TABLE, '7004667'))

print 'START STEP : %s' % __file__
conn = connections('DictCursor')
cursor = conn.cursor()
update_is_max_version(cursor)
if cursor:
    cursor.close()
if conn:
    conn.close()
