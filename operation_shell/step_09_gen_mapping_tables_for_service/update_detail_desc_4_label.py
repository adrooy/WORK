# coding=utf-8
#删除iplay_game_label_info的detail_desc中的以下信息:
#=======================================
#【GG适用平台】
#【适用平台】NVDIA Tegra、高通 骁龙Snapdragon、联发科MTK、三星 猎户座Exynos
#【适用系统版Android 4.0及以上机型
#【特别注意】：暂不支持X86架构机型
import sys
sys.path.append("/home/mgmt/operation")
#sys.path.append("/root/operation")
from database.mysql_client import connections
import re
LABEL_INFO_TABLE = "`forum`.`iplay_game_label_info`"

desc_mapping = """
=======================================
【GG适用平台】
【适用平台】NVDIA Tegra、高通 骁龙Snapdragon、联发科MTK、三星 猎户座Exynos
【适用系统版本】Android 4.0及以上机型
【特别注意】：暂不支持X86架构机型"""
#

def change_detail_desc(cur):
    sqlstr = "SELECT `detail_desc`, `game_id` FROM %s WHERE `detail_desc` like '%%GG适用平台%%'" % LABEL_INFO_TABLE
    cur.execute(sqlstr)
    rows = cur.fetchall()
    print len(rows)
    n = 0
    for row in rows:
        desc = row['detail_desc'].replace(desc_mapping, '')
        game_id = row['game_id']
        try:
            sqlstr = "UPDATE %s SET `detail_desc` = '%s' where `game_id` = '%s'" % (LABEL_INFO_TABLE, desc, game_id) 
            cur.execute(sqlstr)
            n += 1
        except Exception as e:
            print '   UPDATE ERROR: %s  %s' % (game_id, e)
    print 'update %d' % n

if __name__ == '__main__':
    print 'START STEP : %s' % __file__
    conn = connections('DictCursor')
    cursor =  conn.cursor()
    try:
        change_detail_desc(cursor)
    except Exception as e:
        print '    ERROR : %s' % e
    print "END STEP : %s" % __file__
