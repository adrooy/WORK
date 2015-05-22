#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.core.cache import cache
from django.db.models import Count, Sum, connection
from django.db import connections
from django.contrib.auth.models import User
from feedback.models import Feedback
from iplay_utils.utils import pagination, forum_data_conn, report_data_conn, get_game_name, get_GET_parm_or_default, get_perm

import os
import csv
import time
import json
import logging


option_desc_mapping = {
    1 : '游戏描述错误',  #0x1
    2 : '无法下载',#0x2
    3 : '无法安装',#0x4
    4 : '安装后无法打开',#0x8
    5 : '!!!没有这个反馈选项!!!',#0x10
    6 : '数据包安装失败',#0x20
    7 : '无法开启辅助',#0x40
    8 : '游戏闪退',#0x80
    9 : '无法正常内购',#0x100
    10: '内购失败，需要谷歌服务',#0x200
    11: '内购失败，购买成功，数量不增加',#0x400
    12: '内购失败，刷不出商品',#0x800
    13: '内购失败，购买不成功',#0x1000
    14: '内购失败，内购闪退',#0x2000
    15: '无法游戏，需要谷歌服务',#0x4000
    16: '无法游戏，必须更新游戏',#0x8000
    17: '无法游戏，游戏过程中闪退',#0x10000
    18: '无法游戏，封号',#0x20000
    19: '无法游戏，无法连接网络',#0x40000
    20: '无法游戏，需要&无法下载数据包'#0x80000
}
#option_desc_mapping = {
#    1 : '游戏描述错误',
#    2 : '无法下载',
#    3 : '无法安装',
#    4 : '安装后无法打开',
#    5 : '!!!没有这个反馈选项!!!',
#    6 : '数据包安装失败',
#    7 : '无法开启辅助',
#    8 : '游戏闪退',
#    9 : '无法正常内购'
#}

def get_options_desc(options):
    desc = []
    for i in range(0, len(option_desc_mapping)):
        if (options & (1<<i)) != 0:
            desc.append(option_desc_mapping[i+1])
    return desc

@csrf_exempt
@login_required
def detail(request):

    user = User.objects.get(username = request.user)
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    game_id = get_GET_parm_or_default(request, 'game_id', 'Invalid')
    option = get_GET_parm_or_default(request, 'option', '0')
    start_date = get_GET_parm_or_default(request, 'start_date', 'all')
    end_date = get_GET_parm_or_default(request, 'end_date', 'all')
    if start_date == '请选择起始日期' or end_date == '请选择结束日期':
        start_date = 'all'
        end_date = 'all'
    sql = "SELECT * FROM `iplay_user_feedback_view` WHERE `game_id` = '%s' AND (`options` & %d) <> 0 " \
          % (game_id, option == '0' and 0xfffffffffffffffffff or (1<<(int(option)-1)) )
    if start_date != 'all' and end_date != 'all':
        start_ymd = start_date.split(' ')[0]
        start_hms = start_date.split(' ')[1]
        end_ymd = end_date.split(' ')[0]
        end_hms = end_date.split(' ')[1]
        if start_ymd == end_ymd:
            sql += " AND ((`create_time_hms` >= '%s' AND `create_time_hms` <= '%s') AND `create_time_ymd` = '%s')" % (min(start_hms, end_hms), max(start_hms, end_hms), end_ymd)
        else:
            sql += " AND ((`create_time_ymd` = '%s' AND `create_time_hms` >= '%s') OR (`create_time_ymd` > '%s' AND `create_time_ymd` <= '%s') OR (`create_time_ymd` = '%s' AND `create_time_hms` <= '%s'))" % (start_ymd, start_hms, start_ymd, str(int(end_ymd)-1), end_ymd, end_hms)
    Feedback._meta.db_table = 'iplay_user_feedback_view'
    feedbacks_raw = Feedback.objects.raw(sql)
    feedbacks = []  # RawQuerySet没有__len__方法, 导致无法分页, 另存为一个list.
    for item in feedbacks_raw:
        feedbacks.append(item)
    
    feedback, page_range, per_page = pagination(request, feedbacks)
    count = len(feedbacks)
    count_page = count / per_page 

    for item in feedback:
        item.options_desc = get_options_desc(item.options)

    return render_to_response('feedback/detail.html', {
        'html': '/gg_mgmt/feedback2/',
        'perm_id': perm_id,
        'perm_name': perm_name,
        'game_name': get_game_name(game_id),
        'game_id': game_id,
        'option': option,
        'option_desc': option == '0' and '所有反馈' or option_desc_mapping[int(option)],
        'start_date': start_date,
        'end_date': end_date,
        'feedback': feedback,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page+1,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def index(request):
    user = User.objects.get(username = request.user)
    start_date = get_GET_parm_or_default(request, 'start_date', 'all')
    end_date = get_GET_parm_or_default(request, 'end_date', 'all')
    if start_date == '请选择起始日期' or end_date == '请选择结束日期':
        start_date = 'all'
        end_date = 'all'
    sql = "SELECT `game_id`, `options` FROM `iplay_user_feedback_view` WHERE `game_id` IS NOT NULL AND `options` IS NOT NULL AND `options` <> 0"
    if start_date != 'all' and end_date != 'all':
        start_ymd = start_date.split(' ')[0]
        start_hms = start_date.split(' ')[1]
        end_ymd = end_date.split(' ')[0]
        end_hms = end_date.split(' ')[1]
        if start_ymd == end_ymd:
            sql += " AND ((`create_time_hms` >= '%s' AND `create_time_hms` <= '%s') AND `create_time_ymd` = '%s')" % (min(start_hms, end_hms), max(start_hms, end_hms), end_ymd)
        else:
            sql += " AND ((`create_time_ymd` = '%s' AND `create_time_hms` >= '%s') OR (`create_time_ymd` > '%s' AND `create_time_ymd` <= '%s') OR (`create_time_ymd` = '%s' AND `create_time_hms` <= '%s'))" % (start_ymd, start_hms, start_ymd, str(int(end_ymd)-1), end_ymd, end_hms)
    cursor = connections['feedback'].cursor()
    cursor.execute(sql)
    info_counts = {} # { game_id : [ game_id, game_name, sum of record, [option sum of each option] ] }
    for row in cursor.fetchall():
        game_id = row[0]
        option = row[1]
        if option == 0:
            continue

        if game_id in info_counts.keys():
            info_count = info_counts[game_id]
            info_count[2] += 1
        else:
            info_count = [game_id, '', 1, [0] * len(option_desc_mapping)]
            info_counts[game_id] = info_count

        for i in range(0, len(option_desc_mapping)):
            info_count[3][i] += ((option & (1<<i)) != 0 ) and 1 or 0

    deleted_games = []
    for key in info_counts:
        game_name = get_game_name(key)
        if game_name:
            info_counts[key][1] = get_game_name(key)
        else:
            deleted_games.append(key)
    for key in deleted_games:
        del info_counts[key]

    results = info_counts.values()
    results.sort(key=lambda tup: tup[2], reverse=True)

    result, page_range, per_page = pagination(request, results)
    count_records = len(results)
    count_page = count_records / per_page

    return render_to_response('feedback/index.html', {
        'html': '/gg_mgmt/feedback/',
        'info_counts': result,
        'feedback': result,
        'start_date': start_date,
        'end_date': end_date,
        'user': user,
        'page_range': page_range,
        'per_page': per_page,
        'count': count_records,
        'count_page': count_page+1,
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def detail_download(request):
    game_id = request.POST.get('game_id', 'Invalid')
    option = request.POST.get('option', '0')
    start_date = request.POST.get('start_date', 'all')
    end_date = request.POST.get('end_date', 'all')
    if start_date == '请选择起始日期' or end_date == '请选择结束日期':
        start_date = 'all'
        end_date = 'all'
    sql = "SELECT * FROM `iplay_user_feedback_view` WHERE `game_id` = '%s' AND (`options` & %d) <> 0 " \
          % (game_id, option == '0' and 0xfffffffffffffffffff or (1<<(int(option)-1)) )
    if start_date != 'all' and end_date != 'all':
        start_ymd = start_date.split(' ')[0]
        start_hms = start_date.split(' ')[1]
        end_ymd = end_date.split(' ')[0]
        end_hms = end_date.split(' ')[1]
        if start_ymd == end_ymd:
            sql += " AND ((`create_time_hms` >= '%s' AND `create_time_hms` <= '%s') AND `create_time_ymd` = '%s')" % (min(start_hms, end_hms), max(start_hms, end_hms), end_ymd)
        else:
            sql += " AND ((`create_time_ymd` = '%s' AND `create_time_hms` >= '%s') OR (`create_time_ymd` > '%s' AND `create_time_ymd` <= '%s') OR (`create_time_ymd` = '%s' AND `create_time_hms` <= '%s'))" % (start_ymd, start_hms, start_ymd, str(int(end_ymd)-1), end_ymd, end_hms)
    Feedback._meta.db_table = 'iplay_user_feedback_view'
    feedbacks_raw = Feedback.objects.raw(sql)
    feedbacks = []  # RawQuerySet没有__len__方法, 导致无法分页, 另存为一个list.
    for item in feedbacks_raw:
        feedbacks.append(item)
    for item in feedbacks:
        item.options_desc = get_options_desc(item.options)
    option_desc = option == '0' and '所有反馈' or option_desc_mapping[int(option)],
    game_name = get_game_name(game_id)
    filename = '%s_%s_%s_%s.csv' % (game_id, start_date, end_date, option)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(BASE_DIR, 'logs', filename), 'w') as files:
        files.write('id,反馈信息,用户信息,客户端信息\n')
        for list in feedbacks:
            list.content = list.content if list.content else ''
            list.channel = list.channel if list.channel else ''
            list.signature = list.signature if list.signature else ''
            feedback_id = str(list.id)
            feedback_info = list.options_desc + [list.content]
            user_info = [str(list.imei), list.vendor, list.model, list.fingerprint, str(list.sdk), str(list.widthpixels), str(list.heightpixels), str(list.density)]
            app_info = [list.pkg_name, str(list.ver_code), str(list.signature), list.channel]
            files.write('%s,%s,%s,%s\n' % (str(feedback_id), (';'.join(feedback_info)).strip().replace(',', '.'), (';'.join(user_info)).strip().replace(',', '.'), (';'.join(app_info)).strip().replace(',', '.')))
    wrapper = FileWrapper(file(os.path.join(BASE_DIR, 'logs', filename)))
    response = HttpResponse(wrapper, content_type='text/csv')
    response['Content-Length'] = os.path.getsize(os.path.join(BASE_DIR, 'logs', filename))
    response['Content-Encoding'] = 'utf-8'
    response['Content-Disposition'] = 'attachment;filename=%s' % filename
    return response


@csrf_exempt
@login_required
def download(request):
    start_date = request.POST.get('start_date', 'all')
    end_date = request.POST.get('end_date', 'all')
    if start_date == '请选择起始日期' or end_date == '请选择结束日期':
        start_date = 'all'
        end_date = 'all'
    sql = "SELECT `game_id`, `options` FROM `iplay_user_feedback_view` WHERE `game_id` IS NOT NULL AND `options` IS NOT NULL AND `options` <> 0"
    if start_date != 'all' and end_date != 'all':
        start_ymd = start_date.split(' ')[0]
        start_hms = start_date.split(' ')[1]
        end_ymd = end_date.split(' ')[0]
        end_hms = end_date.split(' ')[1]
        if start_ymd == end_ymd:
            sql += " AND ((`create_time_hms` >= '%s' AND `create_time_hms` <= '%s') AND `create_time_ymd` = '%s')" % (min(start_hms, end_hms), max(start_hms, end_hms), end_ymd)
        else:
            sql += " AND ((`create_time_ymd` = '%s' AND `create_time_hms` >= '%s') OR (`create_time_ymd` > '%s' AND `create_time_ymd` <= '%s') OR (`create_time_ymd` = '%s' AND `create_time_hms` <= '%s'))" % (start_ymd, start_hms, start_ymd, str(int(end_ymd)-1), end_ymd, end_hms)
    cursor = connections['feedback'].cursor()
    cursor.execute(sql)
    info_counts = {} # { game_id : [ game_id, game_name, sum of record, [option sum of each option] ] }
    for row in cursor.fetchall():
        game_id = row[0]
        option = row[1]
        if option == 0:
            continue

        if game_id in info_counts.keys():
            info_count = info_counts[game_id]
            info_count[2] += 1
        else:
            info_count = [game_id, '', 1, [0] * len(option_desc_mapping)]
            info_counts[game_id] = info_count

        for i in range(0, len(option_desc_mapping)):
            info_count[3][i] += ((option & (1<<i)) != 0 ) and 1 or 0

    deleted_games = []
    for key in info_counts:
        game_name = get_game_name(key)
        if game_name:
            info_counts[key][1] = get_game_name(key)
        else:
            deleted_games.append(key)
    for key in deleted_games:
        del info_counts[key]

    results = info_counts.values()
    results.sort(key=lambda tup: tup[2], reverse=True)
    game_name = get_game_name(game_id)
    filename = '%s_%s.csv' % (start_date, end_date)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(BASE_DIR, 'logs', filename), 'w') as files:
        files.write('游戏ID,游戏名称,反馈总次数,游戏描述错误,无法下载,无法安装,无法开启辅助,游戏闪退,无法正常内购,内购失败.需要谷歌服务,内购失败.购买成功.数量不增加,内购失败.刷不出商品,内购失败.购买不成功,内购失败.内购闪退,无法游戏.需要谷歌服务,无法游戏.必须更新游戏,无法游戏.游戏过程中闪退,无法游戏.封号,无法游戏.无法连接网络,无法游戏.需要&无法下载数据包\n')
        for info in results:
            file_list = []
            file_list.append(info[0])
            file_list.append(info[1])
            file_list.append(str(info[2]))
            i = 0
            for option_count in info[3]:
                i += 1
                if i== 4 or i==5 or i==6:
                    continue
                file_list.append(str(option_count))
            files.write('%s\n' % ','.join(file_list))
    wrapper = FileWrapper(file(os.path.join(BASE_DIR, 'logs', filename)))
    response = HttpResponse(wrapper, content_type='text/csv')
    response['Content-Length'] = os.path.getsize(os.path.join(BASE_DIR, 'logs', filename))
    response['Content-Encoding'] = 'utf-8'
    response['Content-Disposition'] = 'attachment;filename=%s' % filename
    return response
