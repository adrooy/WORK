# coding=utf-8
# generate game category mapping table
# 每个分类，先从iplay_category_game_order_adjust读出手动配置的top N游戏，
# 然后每个游戏类型内的游戏根据下载量排序，去除手动配置过的游戏，插入到分类结果后面
# 新锐榜　category_id=1000005 order_type=1
# 周排行　category_id=1000001 order_type=4
# 总排行　category_id=1000001 order_type=1
# 24小时最热　iplayStatistics.iplay_assistant_sta_games_time 取前一天的type='gameid'的按user24hour的top100
#       过滤掉　新锐榜top50 及　总排行的top50
import os
import sys
import time
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
sys.path.append("/home/szn/gitroot/backend/iplay/data/operation")
from database.mysql_client import connections
from _09_8_color_label_category import ColorCategory

LABEL_INFO_TABLE = "`forum`.`iplay_game_label_info`"
PKG_INFO_TABLE = "`forum`.`iplay_game_pkg_info`"
CATEGORY_TABLE = "`forum`.`iplay_game_category_info`"
MAPPING_TABLE = "`forum`.`iplay_category_to_game_result`"
GAME_ORDER_ADJUST_TABLE = "`forum`.`iplay_category_game_order_adjust`"
STA_GAME_TIME = "`iplayStatistics`.`iplay_assistant_sta_games_time`"

g_category_info = {} # { "name" : id }
g_category_other = 0


def prepare_category_info(cur):
    global g_category_info, g_category_other

    cur.execute("select `name`, `id` from %s" % CATEGORY_TABLE)
    for row in cur.fetchall():
        if row['name'] in g_category_info.keys():
            raise "More than 1 category have same name"
        else:
            g_category_info[row['name']] = row['id']

        if row['name'] == '其他':
            g_category_other = row['id']


def find_category_list(game_types):
    global g_category_info, g_category_other

    category_list = []
    if not game_types or len(game_types) == 0:
        return [g_category_other]
    for type_str in game_types.split("\n"):
        type_str = type_str.strip().rstrip()
        if len(type_str) == 0:
            continue
        for category in g_category_info.keys():
            if type_str == category :
                category_list.append(g_category_info[category])

    rtn = set(category_list)
    return len(rtn) != 0 and rtn or [g_category_other]


def gen_game_plugin_dl_cnt_dic(cur):

    # resource dl cnt
    cur.execute("SELECT aid, downloads FROM pre_forum_attachment")
    dic_resource_dl_cnt = {}
    for row in cur.fetchall():
        dic_resource_dl_cnt[row['aid']] = row['downloads']

    # pkg resource dl cnt
    cur.execute("SELECT * FROM iplay_resource_match_result")
    dic_pkg_resource = {}
    for row in cur.fetchall():
        if row['apk_id'] not in dic_pkg_resource:
            dic_pkg_resource[row['apk_id']] = []

        if row['resource_id'] not in dic_pkg_resource[row['apk_id']]:
            dic_pkg_resource[row['apk_id']].append(row['resource_id'])

    # label resource dl cnt
    cur.execute("SELECT game_id , apk_id FROM %s" % PKG_INFO_TABLE)

    dic_label_resource = {}
    for row in cur.fetchall():
        if row['game_id'] not in dic_label_resource:
            dic_label_resource[row['game_id']] = []

        if row['apk_id'] in dic_pkg_resource:
            for apk_resource in dic_pkg_resource[row['apk_id']]:
                if apk_resource not in dic_label_resource[row['game_id']]:
                    dic_label_resource[row['game_id']].append(apk_resource)

    dic_label_dl_cnt = {}
    for game_id in dic_label_resource:
        resource_dl_cnt = 0
        for resource in dic_label_resource[game_id]:
            if resource in dic_resource_dl_cnt:
                resource_dl_cnt += dic_resource_dl_cnt[resource]
        dic_label_dl_cnt[game_id] = resource_dl_cnt

    return dic_label_dl_cnt


def gen(cur):
    #cur.execute("select `game_id`, `game_types`, `download_counts` from %s where " % LABEL_INFO_TABLE)
    mapping = {} # { category_id : [ (game_id, download_count, gg_download_cnt, save_timestamp, gg_download_week),...]}

    # 彩标 color_label 映射category
    color_category = ColorCategory(cursor, conn)
    color_category.init_table()
    color_category.main()
    mapping.update(color_category.CATEGORY_GAMES)


    mapping[1000003] = []
    mapping[1000004] = []

    #新锐游戏
    recent_only = 1000005
    mapping[recent_only] = []
    cur.execute("SELECT DISTINCT label.`game_id`, label.`origin_types`, label.`download_counts`, label.`gg_download_cnt`, label.`save_timestamp`, label.`gg_download_week` FROM %s label RIGHT JOIN %s pkg ON label.game_id = pkg.game_id WHERE (label.source = 2 OR label.source = 3 OR label.source = 4) AND label.enabled = 1 AND pkg.enabled = 1 AND label.`save_timestamp` > %d " % (LABEL_INFO_TABLE, PKG_INFO_TABLE, int(time.time())-691200))
    print int(time.time())-691200
    for row in cur.fetchall():
        mapping[recent_only].append((row['game_id'], row['download_counts'], row['gg_download_cnt'], row['save_timestamp'], row['gg_download_week']))
 
    all_game_cat_id = 1000001
    mapping[all_game_cat_id] = []
   # cur.execute("SELECT DISTINCT label.`game_id`, label.`origin_types`, label.`download_counts`, label.`gg_download_cnt`, label.`save_timestamp`, label.`gg_download_week` FROM %s label RIGHT JOIN %s pkg ON label.game_id = pkg.game_id WHERE (pkg.is_plugin_required = 1  OR label.source = 2 OR label.source = 3) AND label.enabled = 1 AND pkg.enabled = 1" % (LABEL_INFO_TABLE, PKG_INFO_TABLE))
    cur.execute("SELECT DISTINCT label.`game_id`, label.`origin_types`, label.`download_counts`, label.`gg_download_cnt`, label.`save_timestamp`, label.`gg_download_week` FROM %s label RIGHT JOIN %s pkg ON label.game_id = pkg.game_id WHERE (label.source = 2 OR label.source = 3 OR label.source = 4) AND label.enabled = 1 AND pkg.enabled = 1" % (LABEL_INFO_TABLE, PKG_INFO_TABLE))
    for row in cur.fetchall():
        category_id_list = find_category_list(row['origin_types'])
        for category_id in category_id_list:
     #       if category_id == 0:
     #           print row
     #           print category_id_list
            if category_id in mapping.keys():
                mapping[category_id].append((row['game_id'], row['download_counts'], row['gg_download_cnt'], row['save_timestamp'], row['gg_download_week']))
            else:
                mapping[category_id] = [(row['game_id'], row['download_counts'], row['gg_download_cnt'], row['save_timestamp'], row['gg_download_week'])]
        mapping[all_game_cat_id].append((row['game_id'], row['download_counts'], row['gg_download_cnt'], row['save_timestamp'], row['gg_download_week']))

    all_plugin_game_cat_id = 1000002
    mapping[all_plugin_game_cat_id] = []
    dic_label_plugin_dl_cnt = gen_game_plugin_dl_cnt_dic(cur)
    cur.execute("SELECT DISTINCT label.`game_id`, label.`origin_types`, label.`download_counts`, label.`gg_download_cnt`, label.`save_timestamp`, label.`gg_download_week` FROM %s label RIGHT JOIN %s pkg ON label.game_id = pkg.game_id WHERE pkg.is_plugin_required = 1 AND label.source not in (3, 4) AND label.enabled = 1 AND pkg.enabled = 1" % (LABEL_INFO_TABLE, PKG_INFO_TABLE))
    for row in cur.fetchall():
        plugin_dl_cnt = 0
        if row['game_id'] in dic_label_plugin_dl_cnt:
            plugin_dl_cnt = dic_label_plugin_dl_cnt[row['game_id']]
        mapping[all_plugin_game_cat_id].append((row['game_id'], row['download_counts'], row['gg_download_cnt'], row['save_timestamp'], row['gg_download_week'], plugin_dl_cnt))


    #defalut order type, by PLUGINDOWNLOADCNT
    order_type = 3
    ####xiangxiaowei
    top_n_id = []
    n = cur.execute("select `game_id` from %s where category_id = %d AND enabled = 1 ORDER BY manual_num ASC" % (GAME_ORDER_ADJUST_TABLE, all_plugin_game_cat_id))
    rows = cur.fetchall()
    for i in range(0, len(rows)):
        top_n_id.append(rows[i]['game_id'])
        sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, all_plugin_game_cat_id, rows[i]['game_id'], i+1, order_type)
            
        try:
            cur.execute(sqlstr)
        except Exception as e:
            print order_type
            print sqlstr
            print e.message
            exit()

    mapping[all_plugin_game_cat_id].sort(key=lambda tup: tup[5], reverse=True)
    for i in range(0, len(mapping[all_plugin_game_cat_id])):
        if mapping[all_plugin_game_cat_id][i][0] in top_n_id:
            continue
        sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, all_plugin_game_cat_id, mapping[all_plugin_game_cat_id][i][0],  i+n+1, order_type)
        try:
            cur.execute(sqlstr)
        except Exception as e:
            print order_type, '2'
            print sqlstr
            print e.message
            exit()
    ####

    for category_id in mapping.keys():
        top_n_id = []
        n = cur.execute("select `game_id` from %s where category_id = %d AND enabled = 1 ORDER BY manual_num ASC" % (GAME_ORDER_ADJUST_TABLE, category_id))
        rows = cur.fetchall()

        #defalut order type, by MARKETDOWNLOADCNT
        order_type = 0
        for i in range(0, len(rows)):
            top_n_id.append(rows[i]['game_id'])
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, rows[i]['game_id'], i+1, order_type)
            try:
                cur.execute(sqlstr)
            except Exception as e:
                print order_type
                print sqlstr
                print e.message
                exit()

        mapping[category_id].sort(key=lambda tup: tup[1], reverse=True)
        for i in range(0, len(mapping[category_id])):
            if mapping[category_id][i][0] in top_n_id:
                continue
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, mapping[category_id][i][0],  i+n+1, order_type)
            try:
                cur.execute(sqlstr)
            except Exception as e:
                print sqlstr
                print e.message
                exit()

        #order type, by GGDOWNLOADCNT
        order_type = 1
        for i in range(0, len(rows)):
            top_n_id.append(rows[i]['game_id'])
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, rows[i]['game_id'], i+1, order_type)
            try:
                cur.execute(sqlstr)
            except Exception as e:
                print order_type, '_1'
                print sqlstr
                print e.message
                exit()

        mapping[category_id].sort(key=lambda tup: tup[2], reverse=True)
        for i in range(0, len(mapping[category_id])):
            if mapping[category_id][i][0] in top_n_id:
                continue
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, mapping[category_id][i][0], i+n+1, order_type)
            try:
          #  if 1==1:
                cur.execute(sqlstr)
            except Exception as e:
                print sqlstr
                print e.message
                exit()

        #order type, by RELEASEDATE
        order_type = 2
        for i in range(0, len(rows)):
            top_n_id.append(rows[i]['game_id'])
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, rows[i]['game_id'], i+1, order_type)
            try:
                cur.execute(sqlstr)
            except Exception as e:
                print sqlstr
                print e.message
                exit()

        mapping[category_id].sort(key=lambda tup: tup[3], reverse=True)
        for i in range(0, len(mapping[category_id])):
            if mapping[category_id][i][0] in top_n_id:
                continue
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, mapping[category_id][i][0], i+n+1, order_type)
            try:
                cur.execute(sqlstr)
            except Exception as e:
                print sqlstr
                print e.message
                exit()

        #order type, by GGDOWNLOADWEEK
        order_type = 4
        for i in range(0, len(rows)):
            top_n_id.append(rows[i]['game_id'])
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, rows[i]['game_id'], i+1, order_type)
            try:
                cur.execute(sqlstr)
            except Exception as e:
                print order_type
                print sqlstr
                print e.message
                exit()

        mapping[category_id].sort(key=lambda tup: tup[4], reverse=True)
        for i in range(0, len(mapping[category_id])):
            if mapping[category_id][i][0] in top_n_id:
                continue
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, mapping[category_id][i][0],  i+n+1, order_type)
            try:
                cur.execute(sqlstr)
            except Exception as e:
                print sqlstr
                print e.message
                exit()


# add by szn: to return game count of each top category to client
def update_category_game_count(cursor):
	sql_getcount = "select count(*) as cnt from %s where `category_id` = %d and `source` <> 1"
	sql_updatecount = "update %s set `game_count` = %d where `id` = %d"

	cursor.execute("select `id` from %s" % CATEGORY_TABLE)
	rows = cursor.fetchall()
	for row in rows:
		cid = row['id']
		cursor.execute(sql_getcount % (LABEL_INFO_TABLE, cid))
		cnt = cursor.fetchone()['cnt']
		cursor.execute(sql_updatecount % (CATEGORY_TABLE, cnt, cid))


# add by xxw: 生成24小时最热
def get_24hour_hot_game(cursor):
    print 'get_24hour_hot_game'
    category_id = 1000001
    order_type = 5
    list_to_24hour_hot_games = []
    list_to_recent_only_games = []
    list_to_total_games = []
    # 前一天玩家数top100
    sql_get_24hour_hot_games = "SELECT gameid FROM %s WHERE type='gameid' AND ymd='%s' ORDER BY user24hour DESC LIMIT 100" % (STA_GAME_TIME, '20150319')
    print sql_get_24hour_hot_games
    conn = connections('DictCursor')
    cur = conn.cursor()
    cur.execute(sql_get_24hour_hot_games)
    rows = cur.fetchall()
    for row in rows:
        game_id = row['gameid']
        list_to_24hour_hot_games.append(game_id)
    print len(rows)
    conn.commit()
    if cur:
        cur.close()
    if conn:
        conn.close()
    # 新锐榜top50
    sql_get_recent_only_games = "SELECT game_id FROM %s WHERE category_id=1000005 AND order_type=1 ORDER BY order_num LIMIT 50" % MAPPING_TABLE
    print sql_get_recent_only_games
    cursor.execute(sql_get_recent_only_games)
    rows = cursor.fetchall()
    for row in rows:
        game_id = row['game_id']
        list_to_recent_only_games.append(game_id)
    print len(rows)
    # 总排行top50
    sql_get_total_games = "SELECT game_id FROM %s WHERE category_id=1000001 AND order_type=1 ORDER BY order_num LIMIT 50" % MAPPING_TABLE
    print sql_get_total_games
    cursor.execute(sql_get_total_games)
    rows = cursor.fetchall()
    for row in rows:
        game_id = row['game_id']
        list_to_total_games.append(game_id)
    print len(rows)
    order_num = 1
    for game_id in list_to_24hour_hot_games:
        if game_id in list_to_total_games or game_id in list_to_recent_only_games:
            pass
        else:
            sqlstr = "insert into %s values (default, %d, '%s', %d, %d)" % (MAPPING_TABLE, category_id, game_id, order_num, order_type)
            cursor.execute(sqlstr)
            order_num += 1
    '''
    sql = "SELECT game_id FROM %s WHERE category_id=1000001 AND order_type=5 ORDER BY order_num" % MAPPING_TABLE
    print sql
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        game_id = row['game_id']
        if game_id in list_to_total_games or game_id in list_to_recent_only_games:
            print game_id
    '''


print 'START STEP : %s' % __file__
conn = connections('DictCursor')
cursor = conn.cursor()
cursor.execute("truncate %s" % MAPPING_TABLE)
prepare_category_info(cursor)
gen(cursor)
update_category_game_count(cursor)
get_24hour_hot_game(cursor)
conn.commit()
if cursor:
    cursor.close()
if conn:
    conn.close()
