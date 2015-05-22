#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: insert.py
Author: limingdong
Date: 7/10/14
Description: 
"""


from mysql_client import connections
import os
import sys
import json
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from utils.logs import Log
log = Log('insert.log')
insert_logger = log.get_logger()


#推广游戏source=4的数据入库
def insert_label_info(infos):
    """
    数据来源(source),1 抓取数据 2 论坛数据 3 google play 数据 4 推广游戏入库
    :param infos:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO iplay_game_label_info(
        game_id
        , game_name
        , screen_shot_urls
        , icon_url
        , detail_desc
        , game_language
        , save_timestamp
        , min_apk_size
        , max_apk_size
        , min_ver_name
        , max_ver_name
        , source
        , display_name
        , update_timestamp
        , origin_types
        , developer
        , save_user
        , update_user
        , enabled
        , download_counts
        , star_num
        , tid
        ) VALUES (
        %(game_id)s
        , %(game_name)s
        , %(screen_shot_urls)s
        , %(icon_url)s
        , %(detail_desc)s
        , %(game_language)s
        , %(now)s
        , %(file_size)s
        , %(file_size)s
        , %(ver_name)s
        , %(ver_name)s
        , %(source)s
        , %(game_name)s
        , %(now)s
        , %(origin_types)s
        , %(developer)s
        , %(save_user)s
        , %(save_user)s
        , %(enabled)s
        , %(downloaded_cnts)s
        , %(star_num)s
        , 0
        ) ON DUPLICATE KEY UPDATE
        enabled = VALUES(enabled)
        , icon_url = VALUES(icon_url)
        , update_timestamp = VALUES(update_timestamp)
        , save_timestamp = VALUES(save_timestamp)
        , save_user = VALUES(save_user)
        """
        cursor.execute(sql, infos)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("insert_label_info name: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_pkg_info(infos):
    """
    download_url_type: 1普通, 2百度盘
    数据来源(source): 1 抓取数据 2 论坛数据 3 google play 数据, GG官方 4 推广游戏入库
    is_plugin_required: 0不需要, 1需要
    :param infos:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO iplay_game_pkg_info(
        apk_id
        , game_id
        , market_channel
        , game_name
        , pkg_name
        , ver_code
        , ver_name
        , file_size
        , download_url
        , game_desc
        , downloaded_cnts
        , game_language
        , screen_shot_urls
        , icon_url
        , min_sdk
        , download_url_type
        , source
        , signature_md5
        , file_md5
        , origin_types
        , gpu_vender
        , ver_code_by_gg
        , update_desc
        , file_type
        , save_user 
        , update_user
	, url4details
        , save_timestamp
        , update_timestamp
        ) VALUES (
        %(apk_id)s
        , %(game_id)s
        , %(market_channel)s
        , %(game_name)s
        , %(pkg_name)s
        , %(ver_code)s
        , %(ver_name)s
        , %(file_size)s
        , %(download_url)s
        , %(game_desc)s
        , %(downloaded_cnts)s
        , %(game_language)s
        , %(screen_shot_urls)s
        , %(icon_url)s
        , %(min_sdk)s
        , %(download_url_type)s
        , %(source)s
        , %(signature_md5)s
        , %(file_md5)s
        , %(origin_types)s
        , %(gpu_vender)s
        , %(ver_code_by_gg)s
        , %(update_desc)s
        , %(file_type)s
        , %(save_user)s
        , %(save_user)s
        , %(url4details)s
        , %(now)s
        , %(now)s
        ) ON DUPLICATE KEY UPDATE
        enabled = 1
        , save_timestamp = VALUES(save_timestamp)
        , update_timestamp = VALUES(update_timestamp)
        , ver_code = VALUES (ver_code)
        , ver_name = VALUES (ver_name)
        , file_size = VALUES (file_size)
        , download_url = VALUES (download_url)
        , gpu_vender = VALUES (gpu_vender)
        , save_user = VALUES(save_user)
        """
        cursor.execute(sql, infos)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("insert_pkg_info name: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def check_developer(developer):
    """
    检查新增游戏厂商是否在厂商列表内
    :param infos:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO iplay_game_developer(developer) VALUES("%s") ON DUPLICATE KEY UPDATE developer = VALUES(developer);""" % developer
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("insert_developer name: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_iplay_upload_game(infos):
    """
    :param infos:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        INSERT IGNORE INTO iplay_upload_game(
        apk_id,
        start_date,
        source,
        msg
        ) VALUES (
        %(apk_id)s,
        %(now)s,
        %(source)s,
        %(msg)s
        )
        """
        cursor.execute(sql, infos)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("iplay_upload_game name: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_iplay_upload_game(infos):
    """
    :param infos:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        UPDATE iplay_upload_game SET
        end_date = %(now)s,
        source = %(source)s,
        is_finished = %(is_finished)s,
        msg = %(msg)s,
        apk_id = %(apk_id)s,
        channel = %(channel)s
        WHERE id = %(id)s
        """
        cursor.execute(sql, infos)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("update_iplay_upload_game name: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_iplay_upload_plugin(info):
    """
    :param info:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO iplay_upload_plugin(
        plugin_pkg_name,
        plugin_ver_code,
        target_pkg_name,
        target_ver_code,
        save_timestamp,
        editor,
        is_finished,
        msg,
        update_timestamp
        ) VALUES (
        %(plugin_pkg_name)s,
        %(plugin_ver_code)s,
        %(target_pkg_name)s,
        %(target_ver_code)s,
        %(save_timestamp)s,
        %(editor)s,
        %(is_finished)s,
        %(msg)s,
        %(update_timestamp)s
        )
        """
        cursor.execute(sql, info)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("insert_iplay_upload_plugin: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_iplay_upload_plugin(info):
    """
    :param info:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        UPDATE iplay_upload_plugin SET
        plugin_pkg_name = %(plugin_pkg_name)s,
        plugin_ver_code = %(plugin_ver_code)s,
        target_pkg_name = %(target_pkg_name)s,
        target_ver_code = %(target_ver_code)s,
        save_timestamp = %(save_timestamp)s,
        update_timestamp = %(update_timestamp)s,
        is_finished = %(is_finished)s,
        editor = %(editor)s,
        msg = %(msg)s
        WHERE id = %(id)s
        """
        cursor.execute(sql, info)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("update_iplay_upload_plugin: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_iplay_upload_game_baidupan(infos):
    """
    :param infos:百度盘中文件大小不一致,数据库更新
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        UPDATE iplay_upload_game SET
        end_date = %(now)s,
        msg = %(msg)s,
        is_finished = %(is_finished)s
        WHERE id = %(id)s
        """
        cursor.execute(sql, infos)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("update_iplay_upload_game_baidupan name: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_pkg_by_game_id(game_id):
    """
    如果国内游戏选择下载渠道为百度盘,则删除其他渠道游戏信息
    :param infos:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        UPDATE iplay_game_pkg_info SET
        enabled = 0
        WHERE game_id = %s
        """
        cursor.execute(sql, (game_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("update_pkg_by_game_id ERROR: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_label_and_pkg_img(info):
    """
    把googleplay游戏的图片地址更新为七牛的图片
    :param info:
    :return:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    print info
    try:
        label_sql = """
            UPDATE iplay_game_label_info
            SET screen_shot_urls = %(screen_shot_urls)s
            , icon_url = %(icon_url)s
            where game_id = %(game_id)s;
        """
        pkg_sql = """
            UPDATE iplay_game_pkg_info
            SET screen_shot_urls = %(screen_shot_urls)s
            , icon_url = %(icon_url)s
            where game_id = %(game_id)s;
        """
        cursor.execute(label_sql, info)
        cursor.execute(pkg_sql, info)
        conn.commit()
    except Exception as e:
        conn.rollback()
        insert_logger.debug("update_label_and_pkg_img: %s" % str(e.args))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_iplay_release_list(info):
    """
    :param info:
    """
    conn = connections('Cursor')
    cursor = conn.cursor()
    try:
        sql = """
        UPDATE iplay_release_list SET
        end_date = %(update_timestamp)s,
        is_finished = %(is_finished)s,
        msg = %(msg)s
        WHERE id = %(id)s
        """
        cursor.execute(sql, info)
        conn.commit()
        insert_logger.debug("update_iplay_release_list : %s" % str(info['id']))
    except Exception as e:
        conn.rollback()
        insert_logger.debug("update_iplay_release_list: %s : %s" % (info['id'], str(e.args)))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_label(filename, worker):
    conn = connections('%sDictCursor' % worker)
    cursor = conn.cursor()
    with open(filename) as files:
        for line in files:
            labels = json.loads(line)
            game_ids = []
            games = []
            for label in labels:
                game_id = label[0]
                game_ids.append(tuple([game_id]))
                games.append(tuple(label))
            delete_sql = """
            DELETE FROM iplay_game_label_info WHERE game_id = %s;
            """
            cursor.executemany(delete_sql, game_ids)
            insert_sql = """
            INSERT INTO iplay_game_label_info(
            game_id
            , game_name
            , game_types
            , game_tags
            , screen_shot_urls
            , icon_url
            , forum_url
            , post_url
            , tid
            , short_desc
            , detail_desc
            , star_num
            , download_counts
            , game_language
            , save_timestamp
            , update_timestamp
            , min_apk_size
            , max_apk_size
            , min_ver_name
            , max_ver_name
            , source
            , enabled
            , display_name
            , is_changed
            , subscript
            , color_label
            , disable_reason
            , origin_types
            , game_alias
            , search_boost
            , forum_plugin_screen_urls
            , developer
            , category_id
            , gg_download_cnt
            , subscript_expire_time
            , is_in_test
            , gg_download_week
            , save_user
            , update_user
            , detail_url
            , detail_desc_html
            , editor_desc_html
            , banner_pic
            , filter_pkg_names
            , show_hot_icon
            ) VALUES (
            %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s);
            """
            cursor.executemany(insert_sql, games)


def update_pkg(filename, worker):
    conn = connections('%sDictCursor' % worker)
    cursor = conn.cursor()
    with open(filename) as files:
        for line in files:
            pkgs = json.loads(line)
            apk_ids = []
            games = []
            for pkg in pkgs:
                apk_id = pkg[0]
                apk_ids.append(tuple([apk_id]))
                games.append(tuple(pkg))
            delete_sql = """
            DELETE FROM iplay_game_pkg_info WHERE apk_id = %s;
            """
            cursor.executemany(delete_sql, apk_ids)
            insert_sql = """
            INSERT INTO iplay_game_pkg_info(
            apk_id
            , game_id
            , market_channel
            , game_name
            , pkg_name
            , file_md5
            , ver_code
            , ver_name
            , signature_md5
            , file_size
            , download_url
            , forum_url
            , post_url
            , min_sdk
            , game_desc
            , game_types
            , game_tags
            , downloaded_cnts
            , is_crack_apk
            , tid
            , depend_google_play
            , game_language
            , save_timestamp
            , update_timestamp
            , screen_shot_urls
            , icon_url
            , is_max_version
            , download_url_type
            , enabled
            , source
            , is_plugin_required
            , is_changed
            , required_plugin_ids
            , url4details
            , disable_reason
            , origin_types
            , gg_download_cnt
            , gg_download_week
            , gpu_vender
            , ver_code_by_gg
            , update_desc
            , save_user
            , update_user
            , file_type
            , dl_button_txt
            , dl_button_color
            , gles_version
            ) VALUES(
            %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s);
            """
            cursor.executemany(insert_sql, games)


if __name__ == '__main__':
    a = {'plugin_ver_code': 1234, 'update_timestamp': 324114, 'plugin_pkg_name': 'a.com', 'target_pkg_name': '2', 'msg': 2, 'is_finished': 1, 'target_ver_code': 3, 'id': 1, 'editor': '\xe6\xb9\xbf\xe4\xb8\xbb\xe5\x88\xab\xe6\x85\x8c'}
    update_iplay_upload_plugin(a)
    print '11'
