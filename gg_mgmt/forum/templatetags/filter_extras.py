# -*- coding: utf-8 -*-
import time
from django import template
from django.core.cache import cache
from django.db import connections
register = template.Library()


__author__ = 'xiangxiaowei'


@register.simple_tag()
def current_time(timestamp, format_string):
    """Return date from timestamp"""
    return time.strftime(format_string, time.localtime(timestamp))


@register.simple_tag()
def trinocular(condition, true_part, false_part):
    """
    :param condition:
    :param true_part:
    :param false_part:
    :return:
    """
    value = true_part if condition else false_part
    return value


@register.simple_tag()
def minue_time(minued, subtrahend):
    """
    :param minued:
    :param subtrahend:
    :return:
    """
    if minued:
        return round(minued - subtrahend, 2)
    else:
        return round(time.time() - subtrahend, 2)


@register.simple_tag()
def get_groups_old(channel, ads):
    """
    获取可用的渠道(与下发过的渠道去重)
    :param channel: {'id': 'B1', 'name': 'GG助手渠道'}
    :param ads:
    :return:
    """
    channel_ids = []
    for ad in ads:
        channel_ids.append(ad)
    if channel.id in channel_ids:
        return ''
    else:
        return '<option value="'+channel.id+'">'+channel.name+'('+channel.id+')'+'</option>'


@register.simple_tag()
def get_upload_plugin_msg(key):
    """
    :param key:
    :return:
    """
    msg = {
        101: 'rethinkdb error',
        102: '插件早已入库',
        103: '其他错误',
        199: '入库完成'
    }
    value = msg[key]
    return value


@register.simple_tag()
def get_game_info(target, table, vari_name, vari_value):
    key = '%s_%s_%s_%s' % (target, table, vari_name, vari_value)
    target_value = cache.get(key)
    if target_value is None:
        cursor_m = connections['forum'].cursor()
        cursor_m.execute("SELECT `%s` FROM `%s` WHERE `%s` = '%s'" % (target, table, vari_name, vari_value))
        try:
            target_value = cursor_m.fetchone()[0]
            cache.set(key, target_value)
        except Exception:
            target_value = ''
    return target_value


@register.simple_tag()
def get_upload_game_msg(key):
    """
    :param key:
    :return:
    """
    msg = {
        202: 'apk_id生成错误',
        201: '上传的百度盘文件大小和分析出的大小不一致',
        404: '其他错误',
        301: '爬去google信息失败',
        302: '下载的google图片失败',
        303: '上传图片至七牛失败',
        304: '更新图片信息到数据库失败',
        305: '插入数据错误',
        399: 'Google游戏入库成功',
        101: '爬去渠道详情也失败，请检查详情页地址是否正确或这是否被封禁',
        102: '分析详情页失败，可能页面改版或者选择的上传渠道和详情页地址不匹配',
        103: '获取label和pkg信息失败',
        104: '插入游戏数据失败',
        105: '游戏下载地址为空',
        106: '渠道内下载地址apk大小和解析的apk大小不一致',
        199: '国内游戏入库成功',
        501: '获取数据错误',
        502: '插入数据错误',
        599: '游戏入库成功'
    }
    value = msg[key] if key in msg else '其他错误'
    return value


@register.simple_tag()
def get_release_msg(key):
    """
    :param key:
    :return:
    """
    msg = {
        101: '52上解压数据错误',
        102: '同步数据到52错误',
        103: '同步数据到52错误',
        104: '同步数据到52错误',
        105: '52上刷新缓存错误',
        106: '发布成功',
        201: '178刷新缓存错误',
        202: '其他错误',
        301: '广告导出失败',
        302: '下发广告失败',
        303: '更新广告失败',
        304: '服务刷新失败',
        399: '广告发布成功'
    }
    value = msg[key] if key in msg else ''
    return value


@register.simple_tag()
def get_release_type(key):
    """
    :param key:
    :return:
    """
    types = {
        1: '游戏数据发布',
        2: '广告数据发布',
    }
    value = types[key] if key in types else '其他数据'
    return value
