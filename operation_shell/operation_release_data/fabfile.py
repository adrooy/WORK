#!/usr/bin/python
# coding: utf-8


__author__ = 'xiangxiaowei'


from fabric.api import env, local, run, put, cd, settings, roles, execute, get
import os
import sys
import time
import requests
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.mysql_client import OPTIONS, HOST, USER, PWD, connections
from database.insert import update_iplay_release_list
from database.select import get_label_and_pkg
from utils.logs import Log
from utils.utils import get_date

DATE = get_date(int(time.time())).split(' ')[0]
log = Log('fabfile_%s.log' % DATE)
logger = log.get_logger()

env.roledefs = {
    '52': ['mgmt@116.255.129.52'],
    '206': ['mgmt@123.59.55.206'],
    '45': ['root@192.168.1.45']
}


def get_info_for_stat(worker):
    logger.debug('\n\n\n')
    logger.debug('START release info for stat')
    conn = connections('Cursor')
    cursor = conn.cursor()
    sql = 'create table test.iplay_game_label_info (select game_id,display_name from forum.iplay_game_label_info);'
    cursor.execute(sql)
    sql = 'create table test.iplay_game_pkg_info (select apk_id,game_id,pkg_name,market_channel from forum.iplay_game_pkg_info);'
    cursor.execute(sql)
    sql = 'create table test.iplay_ad_info (select id,title from forum.iplay_ad_info);'
    cursor.execute(sql)
    result = local('mysqldump -h%s -u%s -p%s test iplay_game_label_info > %s/iplay_game_label_info_tmp.sql' % (HOST, USER, PWD, BASE_DIR))
    logger.debug('mysqldump -h%s -u%s -p%s test iplay_game_label_info > %s/iplay_game_label_info_tmp.sql: %s' % (HOST, USER, PWD, BASE_DIR, result.succeeded))
    result = local('mysqldump -h%s -u%s -p%s test iplay_game_pkg_info > %s/iplay_game_pkg_info_tmp.sql' % (HOST, USER, PWD, BASE_DIR))
    logger.debug('mysqldump -h%s -u%s -p%s test iplay_game_pkg_info > %s/iplay_game_pkg_info_tmp.sql: %s' % (HOST, USER, PWD, BASE_DIR, result.succeeded))
    result = local('mysqldump -h%s -u%s -p%s test iplay_ad_info > %s/iplay_ad_info_tmp.sql' % (HOST, USER, PWD, BASE_DIR))
    logger.debug('mysqldump -h%s -u%s -p%s test iplay_ad_info > %s/iplay_ad_info_tmp.sql: %s' % (HOST, USER, PWD, BASE_DIR, result.succeeded))
    target_host = OPTIONS['%sDictCursor' % worker]['host']
    target_user = OPTIONS['%sDictCursor' % worker]['user']
    target_pwd = OPTIONS['%sDictCursor' % worker]['passwd']
    result = local('mysql -h%s -u%s -p%s iplayStatistics < %s/iplay_game_label_info_tmp.sql' % (target_host, target_user, target_pwd, BASE_DIR))
    logger.debug('mysql -h%s -u%s -p%s iplayStatistics < %s/iplay_game_label_info_tmp.sql: %s' % (target_host, target_user, target_pwd, BASE_DIR, result.succeeded))
    result = local('mysql -h%s -u%s -p%s iplayStatistics < %s/iplay_game_pkg_info_tmp.sql' % (target_host, target_user, target_pwd, BASE_DIR))
    logger.debug('mysql -h%s -u%s -p%s iplayStatistics < %s/iplay_game_pkg_info_tmp.sql: %s' % (target_host, target_user, target_pwd, BASE_DIR, result.succeeded))
    result = local('mysql -h%s -u%s -p%s iplayStatistics < %s/iplay_ad_info_tmp.sql' % (target_host, target_user, target_pwd, BASE_DIR))
    logger.debug('mysql -h%s -u%s -p%s iplayStatistics < %s/iplay_ad_info_tmp.sql: %s' % (target_host, target_user, target_pwd, BASE_DIR, result.succeeded))
    sql = 'DROP TABLE IF EXISTS `test`.`iplay_game_label_info`;'
    cursor.execute(sql)
    sql = 'DROP TABLE IF EXISTS `test`.`iplay_game_pkg_info`;'
    cursor.execute(sql)
    sql = 'DROP TABLE IF EXISTS `test`.`iplay_ad_info`;'
    cursor.execute(sql)
    local('rm -rf %s/iplay_game_label_info_tmp.sql' % BASE_DIR)
    local('rm -rf %s/iplay_game_pkg_info_tmp.sql' % BASE_DIR)
    local('rm -rf %s/iplay_ad_info_tmp.sql' % BASE_DIR)
    conn.commit()
    cursor.close()
    conn.close()
    logger.debug('END release info for stat')


def get_download_cnt():
    logger.debug('start update download_cnt')
    result = local('python %s/step_other_operation/update_gg_game_dl_cnt.py' % BASE_DIR)
    logger.debug('python %s/step_other_operation/update_gg_game_dl_cnt.py: %s' % (BASE_DIR, result.succeeded))
    #result = put('iplay_ad_info.sql', BASE_DIR)
    #logger.debug('scp iplay_ad_info.sql: %s' % result.succeeded)
    logger.debug('end update download_cnt')


def get_release_game(DATE):
    """
    导出需要下发的数据
    :param DATE:
    :return:
    """
    #local("sh /home/mgmt/operation_shell/cmd/178_gen_service_mapping.sh")
    DIR = os.path.join(BASE_DIR, DATE)
    get_label_and_pkg(DATE)
    local('mysqldump -h%s -u%s -p%s forum iplay_category_game_order_adjust > %s/iplay_category_game_order_adjust.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_category_to_game_result > %s/iplay_category_to_game_result.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_game_category_info > %s/iplay_game_category_info.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_game_label_to_pkg_result > %s/iplay_game_label_to_pkg_result.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_hot_search_words > %s/iplay_hot_search_words.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_recomend_banner_info > %s/iplay_recomend_banner_info.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_recomend_game > %s/iplay_recomend_game.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_resource_match_result > %s/iplay_resource_match_result.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_topic_game > %s/iplay_topic_game.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_topic_info > %s/iplay_topic_info.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum pre_iplay_game_resource_info > %s/pre_iplay_game_resource_info.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum pre_iplay_game_resource_author > %s/pre_iplay_game_resource_author.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum pre_iplay_game_resource_match_condition > %s/pre_iplay_game_resource_match_condition.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_billboard_info > %s/iplay_billboard_info.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_game_forecast_info > %s/iplay_game_forecast_info.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_game_developer > %s/iplay_game_developer.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_game_compatibility_model > %s/iplay_game_compatibility_model.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_game_compatibility_fingerprint > %s/iplay_game_compatibility_fingerprint.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_editor_info > %s/iplay_editor_info.sql' % (HOST, USER, PWD, DIR))
    local('mysqldump -h%s -u%s -p%s forum iplay_tags_category_id > %s/iplay_tags_category_id.sql' % (HOST, USER, PWD, DIR))
    #local('mysqldump -h%s -u%s -p%s forum iplay_ad_info > %s/iplay_ad_info.sql' % (HOST, USER, PWD, DIR))
    local('cd %s && tar -zcvf %s.tar.gz %s' % (BASE_DIR, DATE, DATE))


def get_data():
    local('mysqldump -h%s -u%s -p%s forum iplay_ad_info > %s/operation_release_data/iplay_ad_info.sql' % (HOST, USER, PWD, BASE_DIR))


def reload_db(worker):
    server_names = {
        '52': '116.255.129.52',
        '206': '123.59.55.206'
    }
    url = 'http://%s/api/v1/reload-ad-db?src=3' % server_names[worker]
    r = requests.post(url)
    assert r.status_code == 200
    return r.json()


def update():
    HOST = OPTIONS['206DictCursor']['host']
    USER = OPTIONS['206DictCursor']['user']
    PASSWD = OPTIONS['206DictCursor']['passwd']
    with cd('/home/mgmt'):
        if run('mysql -h%s -u%s -p%s forum < /home/mgmt/iplay_ad_info.sql' % (HOST, USER, PASSWD)):
            msg = 303
        else:
            msg = 399
    print msg
 

def release(worker):
    msg = 399
    if worker == '52':
        HOST = OPTIONS['52DictCursor']['host']
        USER = OPTIONS['52DictCursor']['user']
        PASSWD = OPTIONS['52DictCursor']['passwd']
    if worker == '206':
        HOST = OPTIONS['206DictCursor']['host']
        USER = OPTIONS['206DictCursor']['user']
        PASSWD = OPTIONS['206DictCursor']['passwd']
    if not put('iplay_ad_info.sql', '/home/mgmt'):
        msg = 302
    with cd('/home/mgmt'):
        if run('mysql -h%s -u%s -p%s forum < /home/mgmt/iplay_ad_info.sql' % (HOST, USER, PASSWD)):
            msg = 303
        else:
            run('rm -rf iplay_ad_info.sql')
    msg_json = reload_db(worker)
    if msg_json['result']['code'] != 0:
        msg = 304
    return msg


def release_ad(release_id, worker):
    msg = release(worker)
    info = {}
    info['id'] = release_id
    info['update_timestamp'] = int(time.time())
    info['is_finished'] = 1
    info['msg'] = msg
    update_iplay_release_list(info)


def release_game(release_id, worker, DATE):
    msg = 106
    DIR = os.path.join(BASE_DIR, DATE)
    with cd(BASE_DIR):
        #   失败代码。没有目录的错误怎么捕获....
        if not put('%s/%s.tar.gz' % (BASE_DIR, DATE), '.'):
            msg = 102
        else:
            local('rm -rf %s/%s.tar.gz' % (BASE_DIR, DATE))
            local('rm -rf %s/%s' % (BASE_DIR, DATE))
    try:
        with cd('%s/operation_release_data' % BASE_DIR):
            run("python update_game.py %s %s" % (DATE, worker), shell=True, timeout=400)
    except Exception as e:
        msg = 104
    info = {}
    info['id'] = release_id
    info['update_timestamp'] = int(time.time())
    info['is_finished'] = 0
    info['msg'] = msg
    print info
    logger.debug(msg)
    update_iplay_release_list(info)


def release_download_cnt():
    pass
