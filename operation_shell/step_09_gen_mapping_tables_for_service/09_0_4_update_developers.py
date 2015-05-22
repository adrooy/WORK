# coding=utf-8
# 1. 计算developer的游戏数量
# 2. 找出开发商名下下载量最大的游戏的图标，作为该开发商的图标（运营录入的图标在另外一列）
# 3. 找出开发商名下下载量最大的前三款游戏，把游戏名填入developer表

import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.mysql_client import connections

LABEL_INFO_TABLE = "`forum`.`iplay_game_label_info`"
PKG_INFO_TABLE = "`forum`.`iplay_game_pkg_info`"
DEVELOPER_TABLE = "`forum`.`iplay_game_developer`"


def addslashes(s):
    d = {'"':'\\"', "'":"\\'", "\0":"\\\0", "\\":"\\\\"}
    return ''.join(d.get(c, c) for c in s)


def insert_developers(cur):
    sqlstr = "SELECT DISTINCT(`developer`) FROM %s" % LABEL_INFO_TABLE
    cur.execute(sqlstr)
    rows = cur.fetchall()
    for row in rows:
        developer = row['developer']
        if developer is None or len(developer) == 0:
            continue

        print "Inserting developer: %s" % developer
        try:
            sqlstr = "INSERT INTO %s VALUES(default, '%s', NULL, NULL, 0, NULL, NULL, 0)" % (DEVELOPER_TABLE, developer)
            cur.execute(sqlstr)
        except Exception as e:
            print e


def get_developers(cur):
    sqlstr = "SELECT `developer` FROM %s" % DEVELOPER_TABLE
    cur.execute(sqlstr)
    developers = []
    for developer in cur.fetchall():
        developers.append(developer['developer'])
    print 'Total: %d developers' % len(developers)
    return developers


def update_developer(cur, developer):

    print 'Updating developer: %s' % developer

    sqlstr = "SELECT `game_id`, `icon_url`, `display_name`, `is_in_test` FROM %s WHERE `developer` = '%s' and `enabled` = 1 ORDER BY `gg_download_cnt` DESC" % (LABEL_INFO_TABLE, developer.replace("'", "''"))
    cur.execute(sqlstr)
    rows = cur.fetchall()

    game_icon = ''
    game_names = []
    if len(rows) > 0:
        game_icon = rows[0]['icon_url']
        for row in rows:
            # filter out those who has no corresponding apk_id
            cur.execute("SELECT * FROM %s where `game_id` = '%s'" % (PKG_INFO_TABLE, row['game_id']))
            if len(cur.fetchall()) > 0 and row['is_in_test'] != 1:
                game_names.append(row['display_name'])

    game_count = len(game_names)
    game_names = game_names[:50] # avoid exceed column varchar length, which is 4096

    sqlstr = "UPDATE %s SET `game_icon` = '%s', `game_names` = '%s', `game_count` = %d WHERE `developer` = '%s'" % \
             (DEVELOPER_TABLE, game_icon, '\n'.join(game_names).replace("'", "''"), game_count, developer.replace("'", "''"))
    cur.execute(sqlstr)



if __name__ == '__main__':
    print 'START STEP : %s' % __file__
    conn = connections('DictCursor')
    cursor = conn.cursor()

    try:

        insert_developers(cursor)
        conn.commit()

        developers = get_developers(cursor)

        for developer in developers:
            update_developer(cursor, developer)
            conn.commit()

    except Exception as e:
        print '    ERROR : %s' % e

    print "END STEP : %s" % __file__
