# coding=utf-8
# based on pkg_info, update game_info, use highest version for each channel only.
# 依据pkg_info表中最高版本的文件信息, 更新游戏信息(label_info)表中下载量/文件大小/版本信息
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.mysql_client import connections
import utils

PKG_INFO_TABLE = "`forum`.`iplay_game_pkg_info`"
LABEL_INFO_TABLE = "`forum`.`iplay_game_label_info`"


def update(cur):

    print ("reset download_counts/apk_size/ver_name ...")
    cur.execute("update %s set `download_counts` = 0, `min_apk_size` = 0, `max_apk_size` = 0, `min_ver_name` = '', `max_ver_name` = ''" % LABEL_INFO_TABLE)

    print ("read pkg info...")
    gameinfo = {} # { game_id : [ (apk_id, downloaded_cnts, file_size, ver_name, ver_name_int), ...  ] }
    cur.execute("select `apk_id`, `game_id`, `downloaded_cnts`, `file_size`, `ver_name` from %s where `is_max_version` = 1" % PKG_INFO_TABLE)
    for row in cur.fetchall():
        key = row['game_id']
        ver_name_int = utils.ver_name_to_int(row['ver_name'], row['apk_id'])
        if key in gameinfo.keys():
            gameinfo[key].append( (row['apk_id'], row['downloaded_cnts'], row['file_size'], row['ver_name'], ver_name_int) )
        else:
            gameinfo[key] = [ (row['apk_id'], row['downloaded_cnts'], row['file_size'], row['ver_name'], ver_name_int) ]

    print ("updating label info...")
    print len(gameinfo)
    updated_count = 0
    for key in gameinfo.keys():
        total_downloaded_cnts = 0
        min_apk_size = 0
        max_apk_size = 0
        min_ver_name_int = 0
        max_ver_name_int = 0
        min_ver_name = ""
        max_ver_name = ""

        for apkinfo in gameinfo[key]:
            total_downloaded_cnts += apkinfo[1]

            if min_apk_size == 0:
                min_apk_size = apkinfo[2]
            if min_apk_size > apkinfo[2]:
                min_apk_size = apkinfo[2]

            if max_apk_size == 0:
                max_apk_size = apkinfo[2]
            if max_apk_size < apkinfo[2]:
                max_apk_size = apkinfo[2]

            if min_ver_name_int == 0:
                min_ver_name_int = apkinfo[4]
                min_ver_name = apkinfo[3]
            if min_ver_name_int > apkinfo[4]:
                min_ver_name_int = apkinfo[4]
                min_ver_name = apkinfo[3]

            if max_ver_name_int == 0:
                max_ver_name_int = apkinfo[4]
                max_ver_name = apkinfo[3]
            if max_ver_name_int < apkinfo[4]:
                max_ver_name_int = apkinfo[4]
                max_ver_name = apkinfo[3]

        sqlstr = "update %s set `download_counts` = %d, `min_apk_size` = %d, `max_apk_size` = %d, `min_ver_name` = '%s', `max_ver_name` = '%s' where `game_id` = '%s'" \
            % (LABEL_INFO_TABLE, total_downloaded_cnts, min_apk_size, max_apk_size, min_ver_name, max_ver_name, key)

        #print sqlstr
        cur.execute(sqlstr)
        updated_count += 1
    print ("%d label info updated" % updated_count)

print 'START STEP : %s' % __file__
conn = connections('DictCursor')
cursor = conn.cursor()
update(cursor)
if cursor:
    cursor.close()
if conn:
    conn.close()
