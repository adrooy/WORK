# coding=utf-8
# 更新pkg的required_plugins字段
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


# step 7 update required_plugins_ids
# xiangxiaowei update in 20141208 　去掉is_changed的过滤条件
def update_pkg_required_plugins_ids(cur):
#    n = cur.execute("UPDATE %s set `required_plugin_ids` = '',`is_plugin_required` = 0 where `is_changed` = 0" % PKG_INFO_TABLE)
#    print 'SET %d pkg is_plugin_required to 0' #% n
#    cur.execute("SELECT DISTINCT(`apk_id`) FROM %s where `is_changed` = 0" % PKG_INFO_TABLE)
    n = cur.execute("UPDATE %s set `required_plugin_ids` = '',`is_plugin_required` = 0" % PKG_INFO_TABLE)
    print 'SET %d pkg is_plugin_required to 0' #% n
    #signature_md5不等于50a993d86e797b64e18759ae7a39ff58的需要匹配插件
    cur.execute("SELECT DISTINCT(`apk_id`) FROM %s WHERE signature_md5<>'50a993d86e797b64e18759ae7a39ff58' OR signature_md5 is null" % PKG_INFO_TABLE)
    #cur.execute("SELECT DISTINCT(`apk_id`) FROM %s" % PKG_INFO_TABLE)
    n = 0
    for row in cur.fetchall():
        apk_id = row['apk_id']
        cur.execute("select `resource_id` from %s where apk_id = '%s'" % (MAPPING_TABLE, apk_id))
        res_ids = cur.fetchall()
        if len(res_ids) > 0:
            res_ids = '\n'.join(str(c['resource_id']) for c in res_ids)
            sqlstr = "UPDATE %s set `required_plugin_ids` = '%s',`is_plugin_required` = 1 where `apk_id` = '%s'" % (PKG_INFO_TABLE, res_ids, apk_id)
            cur.execute(sqlstr)
            n += 1
    print 'UPDATE %d pkg info' % n


print 'START STEP : %s' % __file__
conn = connections('DictCursor')
cursor = conn.cursor()

update_pkg_required_plugins_ids(cursor)
if cursor:
    cursor.close()
if conn:
    conn.close()
