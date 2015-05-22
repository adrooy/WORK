# coding=utf-8
# generate pkg_info to label_info mapping table
# 根据pkg_info表中的渠道包与游戏的对应关系, 生成中间表, 根据下载量做排序
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.mysql_client import connections

PKG_INFO_TABLE = "`forum`.`iplay_game_pkg_info`"
MAPPING_TABLE = "`forum`.`iplay_game_label_to_pkg_result`"


def gen(cur):
    print "generate label to package mapping"
    cur.execute("select `apk_id`, `game_id`, `downloaded_cnts` from %s where `is_max_version` = 1" % PKG_INFO_TABLE)

    pkginfo = {} # {label_id : [(pkg_id, download_count),...]}

    for row in cur.fetchall():
        if row['game_id'] in pkginfo.keys():
            pkginfo[row['game_id']].append((row['apk_id'], row['downloaded_cnts']))
        else:
            pkginfo[row['game_id']] = [(row['apk_id'], row['downloaded_cnts'])]

    for i in pkginfo.keys():
        pkginfo[i].sort(key=lambda tup: tup[1], reverse=True)
        for j in range(1, len(pkginfo[i]) + 1):
            sqlstr = "insert into %s values (DEFAULT, '%s', '%s', %d)" % (MAPPING_TABLE, i, pkginfo[i][j-1][0], j)
            #print sqlstr
            cur.execute(sqlstr)


print 'START STEP : %s' % __file__
conn = connections('DictCursor')
cursor = conn.cursor()
cursor.execute("truncate %s" % MAPPING_TABLE)
gen(cursor)
if cursor:
    cursor.close()
if conn:
    conn.close()
