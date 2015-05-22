# coding=utf-8
# generate game resource mapping table
# 第一步: 从pre_forum_thread表里取出可以返回给客户端的资源帖id, 判断条件: sortid==1: 代表是资源帖, recommend_add > 100, displayorder >= 0
# 第二步: 根据获取到的tid, 到pre_iplay_game_resource_info里找到所有符合条件的resource
# 第三步: 在所有符合条件的resource里, 取出每个包名最大的版本的resource_id, 只有这些是可用的
# 第四步: 根据可用的resource_id, 在pre_iplay_game_resource_match_condition表中取出判断条件, 与iplay_game_pkg_info表中内容做匹配, 生成iplay_resource_match_result
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


# step 1, return list of thread ids
def get_qualified_thread_ids(cur):
    tids = []
    cur.execute ("select `tid` from %s where `sortid` = 1 and `displayorder` >= 0" % THREAD_TABLE)  # 调试阶段, 先不判断"赞"的数目
    for row in cur.fetchall():
        tids.append(row['tid'])
    return tids


# step 2+3, return list of resource ids
def get_qualified_resource_ids(cur, tids):
    rinfo = {} # { pkg_name : [ (resource id, version code, author_name), (), ... ] }
    cur.execute("select `id`, `pkg_name`, `ver_code`, `tid`, `author_name` from %s " % RES_INFO_TABLE)
    for row in cur.fetchall():
        if not row['tid'] in tids:
            continue
        if row['pkg_name'] in rinfo.keys():
            rinfo[row['pkg_name']].append((row['id'], row['ver_code'], row['author_name']))
        else:
            rinfo[row['pkg_name']] = [(row['id'], row['ver_code'], row['author_name'])]
    dic_rid_author = dict()
    for key in rinfo.keys():
        for res in rinfo[key]:
            dic_rid_author[res[0]] = res[2]

    return dic_rid_author


def gen_func_version(exp):
    ranges = []
    values = []
    is_wildcard = (exp == '*')
    if not is_wildcard:
        for e in exp.split(','):
            if '-' in e:
                l = e.split('-')
                ranges.append((int(l[0]),int(l[1])))
            else:
                values.append(int(e))
    def rtn(input):
        if is_wildcard:
            return True
        for v in values:
            if input == v:
                return True
        for r in ranges:
            if input >= r[0] and input <= r[1]:
                return True
        return False
    return rtn


def gen_func_pkg_name(exp):
    is_wildcard = (exp == '*')
    regex = re.compile("^" + exp.replace('.', r'\.').replace('*', '.*') + "$")
    def rtn(input):
        return is_wildcard or regex.match(input) is not None
    return rtn


def gen_func_sig(exp):
    is_wildcard = (exp == '*')
    expsave = exp
    def rtn(input):
        return is_wildcard or expsave == input
    return rtn


# step 4
def gen(cur, dic_rid_author):
    pkg_infos = [] # [ row, row, ... ]
    cur.execute("select `apk_id`, `pkg_name`, `ver_code`, `signature_md5`, `source` from %s" % PKG_INFO_TABLE)
    for row in cur.fetchall():
        pkg_infos.append(row)
    res_infos = [] # [ row, row, ...]
    cur.execute("select `resource_id`, `pkg`, `version`, `signature` from %s " % RES_CONDITION_TABLE)
    for row in cur.fetchall():
        if not row['resource_id'] in dic_rid_author.keys():
            continue
        if row['pkg'] == '*' and row['version'] == '*' and row['signature'] == '*':
            continue
        res_infos.append(row)
    for res in res_infos:
        func_pkg_name = gen_func_pkg_name(res['pkg'])
        func_version = gen_func_version(res['version'])
        func_sig = gen_func_sig(res['signature'])
        for pkg in pkg_infos:
            if pkg['source'] != 3 and dic_rid_author[res['resource_id']] == 'robot':
                continue
            if pkg['source'] == 2:
                continue
            if func_pkg_name(pkg['pkg_name']) and func_version(pkg['ver_code']) and func_sig(pkg['signature_md5']):
    #            if pkg['apk_id'] == '4b994590':
    #                continue
                try:
                    sqlstr = "insert into %s values (default, '%s', %d)" % (MAPPING_TABLE, pkg['apk_id'], res['resource_id'])
                    #print sqlstr
                    cur.execute(sqlstr)
                except Exception as e:
                    print e
    #删除掉狂野飙车8(game_id:3f0647e5, apk_id: b5e8b350)对应的大叔插件1855
    sql = "delete from %s where apk_id='67980a20' and resource_id='1855'" % MAPPING_TABLE
    cur.execute(sql)
    #删除掉狂野飙车8samsung(game_id:05fd6d3b, apk_id: 05562fba)对应的大叔插件1711
    sql = "delete from %s where apk_id='05562fba' and resource_id='1711'" % MAPPING_TABLE
    cur.execute(sql)

    sql = "delete from %s where apk_id='338205e6' and resource_id='3003'" % MAPPING_TABLE
    cur.execute(sql)
    sql = "delete from %s where apk_id='72654281' and resource_id='3003'" % MAPPING_TABLE
    cur.execute(sql)
    sql = "delete from %s where apk_id='496ade4c' and resource_id='3003'" % MAPPING_TABLE
    cur.execute(sql)
   
    

print 'START STEP : %s' % __file__
conn = connections('DictCursor')
cursor = conn.cursor()
tids = get_qualified_thread_ids(cursor)
#print "tids:", tids
rids = get_qualified_resource_ids(cursor, tids)
#print "rids:", rids
cursor.execute("truncate %s" % MAPPING_TABLE)
gen(cursor, rids)
print 'END STEP : %s' % __file__

if cursor:
    cursor.close()
if conn:
    conn.close()
