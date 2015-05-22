# -*- coding:utf-8 -*-


from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.db.models import Count, Sum, connection
from django.contrib.auth.models import User
from market.models import RecBanner, RecGame, GameLabelInfo, TopicInfo
from management.models import GameDeveloper, GameOperation

import os
import re
import csv
import time
import json
import datetime
import logging
import subprocess
from urllib import quote_plus

import sys
reload(sys)
sys.setdefaultencoding('utf8')

DIR = os.getcwd()
sys.path.append(DIR)
from iplay_utils.utils import getTimeStamp, getDate, get_perm
from forum.models import *


@csrf_exempt
@login_required
def index(request):
    username = request.user
    user = User.objects.get(username=username)
    editor = IplayEditorInfo.objects.get(name=user.last_name+user.first_name)
    gameid = request.GET.get('game_id')
    bannerid = int(request.GET.get('banner_id')) if 'banner_id' in request.GET else 0
    games = RecGame.objects.all().order_by('order_num')
    banners = RecBanner.objects.all().order_by('order_num')
    number = 1
    for banner in banners:
        banner.release_date = getDate(banner.release_date)
        banner.unrelease_date = getDate(banner.unrelease_date)
        banner.topic_id = banner.topic_id if banner.topic_id else ''
        RecBanner.objects.filter(id=banner.id).update(order_num=number)
        number += 1
    number = 1
    for game in games:
            game_id = game.game_id
            gamelabel = GameLabelInfo.objects.get(game_id=game_id)
            game.game_enabled = gamelabel.enabled
            game.release_date = getDate(game.release_date)
            game.unrelease_date = getDate(game.unrelease_date)
            game.subscript = gamelabel.subscript if gamelabel.subscript else '0'
            RecGame.objects.filter(game_id=game_id).update(order_num=number)
            number += 1
    return render_to_response('market/recommend/index.html', {
        'game_id': gameid,
        'banner_id': bannerid,
        'games': games,
        'banners': banners,
        'editor': editor,
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def addGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    game_id_index = request.GET.get('game_id')
    if game_id_index == 'undefined':
        game_id_index = ''
    DATE = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    game = {'release_date': DATE}
    return render_to_response('market/recommend/game_edit.html', {
            'game': game,
            'game_id_index': game_id_index
        }, context_instance=RequestContext(request))


@login_required
def altGame(request):
    game_id = request.GET.get('game_id')
    game = RecGame.objects.get(game_id=game_id)
    game.release_date = getDate(game.release_date)
    game.unrelease_date = getDate(game.unrelease_date)
    return render_to_response('market/recommend/game_edit.html', {
            'game': game,
            'game_id':game_id
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def editGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    game_id = request.POST.get('game_id')
    order_num = int(request.POST.get('manual_num'))
    #game_id_index = request.POST.get('game_id_index')
    release_date = request.POST.get('release_date')
    unrelease_date = request.POST.get('unrelease_date')

    release_date = getTimeStamp(release_date) if release_date else 0
    unrelease_date = getTimeStamp(unrelease_date) if unrelease_date else 0

    games = RecGame.objects.all().order_by('order_num')
    games_list = []
    for game in games:
        games_list.append(game.game_id)

    if game_id not in games_list:
        game = GameLabelInfo.objects.get(game_id=game_id)
        game_name = game.game_name
        games = RecGame(game_id=game_id, game_name=game_name, order_num=order_num, release_date=release_date, unrelease_date=unrelease_date, enabled=0)
        games.save()
        number = 1
        for game_id_ in games_list:
            if number >= order_num:
                RecGame.objects.filter(game_id=game_id_).update(order_num=number+1, release_date=release_date, unrelease_date=unrelease_date)
            number += 1
    else:
        order_num_ = int(RecGame.objects.get(game_id=game_id).order_num)
        RecGame.objects.filter(game_id=game_id).update(order_num=order_num, release_date=release_date, unrelease_date=unrelease_date)
        #后移
        if order_num_ < order_num:
            number = 1
            for game_id_ in games_list:
                if order_num >= number > order_num_:
                    RecGame.objects.filter(game_id=game_id_).update(order_num=number-1, release_date=release_date, unrelease_date=unrelease_date)
                number += 1
        #前移
        if order_num_ > order_num:
            number = 1
            for game_id_ in games_list:
                if number < order_num_ and number >= order_num:
                    RecGame.objects.filter(game_id=game_id_).update(order_num=number+1, release_date=release_date, unrelease_date=unrelease_date)
                number += 1
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场推荐页',goal='游戏id: %s' % game_id,action='增加游戏列表页游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write(str(game_id))
    return response


@csrf_exempt
@login_required
def isenabledGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_id = request.POST.get('game_id')
    RecGame.objects.filter(game_id=game_id).update(enabled=1)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场推荐页',goal='游戏id: %s' % game_id,action='启用游戏列表页游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s 已启用!!!' % str(game_id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def notenabledGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_id = request.POST.get('game_id')
    RecGame.objects.filter(game_id=game_id).update(enabled=0)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场推荐页',goal='游戏id: %s' % game_id,action='下线游戏列表页游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s 已禁用!!!' % str(game_id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def delGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    game_id = request.POST.get('game_id')
    RecGame.objects.get(game_id=game_id).delete()
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场推荐页',goal='游戏id: %s' % game_id,action='删除游戏列表页游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    order_num = 1
    games = RecGame.objects.all().order_by('order_num')
    for game in games:
        game_id = game.game_id
        RecGame.objects.filter(game_id=game_id).update(order_num=order_num)
        order_num += 1
    result = '推荐游戏列表页的%s游戏已删除！！！' % str(len(games))
    response.write(result)
    return response


@csrf_exempt
@login_required
def upGame(request):

    response=HttpResponse()  
    response['Content-Type'] = 'text/string'

    game_id = request.POST.get('game_id')

    indexs = []
    games = RecGame.objects.all().order_by('order_num')
 
    for game in games:
        indexs.append(game.game_id) 
        if game.game_id == game_id:
            game_name = game.game_name
    up_num = indexs.index(game_id)
    num = up_num + 1
    up_id = indexs[up_num-1]
    if up_num:
        num = up_num + 1
        up_id = indexs[up_num-1]
        RecGame.objects.filter(game_id=game_id).update(order_num=up_num)
        RecGame.objects.filter(game_id=up_id).update(order_num=num)
        result = 'Yes'
    else:
        result = 'Error'
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场推荐页',goal='游戏id: %s' % game_id,action='上移游戏列表页游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write(result)
    return response

@csrf_exempt
@login_required
def downGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_id = request.POST.get('game_id')
    indexs = []
    games = RecGame.objects.all().order_by('order_num')
    for game in games:
        indexs.append(game.game_id) 
        if game.game_id == game_id:
            game_name = game.game_name
    up_num = indexs.index(game_id)
    num = up_num + 1
    down_num = num + 1
    if down_num < len(games)+1:
        num = up_num + 1
        down_num = num + 1
        down_id = indexs[up_num+1]
        RecGame.objects.filter(game_id=game_id).update(order_num=down_num)
        RecGame.objects.filter(game_id=down_id).update(order_num=num)
        result = 'Yes'
    else:
        result = 'Error'
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场推荐页',goal='游戏id: %s' % game_id,action='下移游戏列表页游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write(result)
    return response


@csrf_exempt
@login_required
def addBanner(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    editor = IplayEditorInfo.objects.get(name=user.last_name+user.first_name)
    DATE = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    banner_id = request.GET.get('banner_id')
    if banner_id:
        banner = RecBanner.objects.get(id=banner_id) if banner_id else {}
        banner.release_date = getDate(banner.release_date)
        banner.unrelease_date = getDate(banner.unrelease_date)
    else:
        banner = {'release_date': DATE}
    return render_to_response('market/recommend/edit.html', {
        'banner': banner,
        'editor': editor,
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def editBanner(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    banner_id = request.POST.get('banner_id')
    name = request.POST.get('name')
    order_num = request.POST.get('order_num')
    game_id = request.POST.get('game_id')
    topic_id = request.POST.get('topic_id')
    pic_url = request.POST.get('pic_url')
    release_date = request.POST.get('release_date')
    unrelease_date = request.POST.get('unrelease_date')
    release_date = getTimeStamp(release_date) if release_date else 0
    unrelease_date = getTimeStamp(unrelease_date) if unrelease_date else 0
    target_id = game_id if game_id else topic_id
    banners = RecBanner.objects.all().order_by('order_num')
    banner_list = []
    for banner in banners:
        if banner.game_id:
            banner_list.append(banner.game_id)
        if banner.topic_id:
            banner_list.append(str(banner.topic_id))
    #　新增banner，插入位置之后的banner依次后移一位
    if target_id not in banner_list:
        if game_id:
            name = GameLabelInfo.objects.get(game_id=game_id).display_name
            RecBanner(game_id=game_id, name=name, order_num=order_num, pic_url=pic_url, release_date=release_date, unrelease_date=unrelease_date).save()
        if topic_id:
            name = TopicInfo.objects.get(id=topic_id).name
            RecBanner(topic_id=topic_id, name=name, order_num=order_num, pic_url=pic_url, release_date=release_date, unrelease_date=unrelease_date).save()
        number = 1
        for banner in banners:
            if int(number) >= int(order_num):
                RecBanner.objects.filter(id=banner.id).update(order_num=number+1)
            number += 1
        result = '%s已添加到banner列表' % target_id
    elif banner_id:
        old_order_num = RecBanner.objects.get(id=banner_id).order_num
        RecBanner.objects.filter(id=banner_id).update(order_num=order_num)
        # 后移 两位置之间的依次前移一位
        if int(old_order_num) < int(order_num):
            number = 1
            for banner in banners:
                if int(old_order_num) < number <= int(order_num):
                    RecBanner.objects.filter(id=banner.id).update(order_num=number-1, name=name)
                    number += 1
        # 前移　两位置之间的依次后移一位
        if int(old_order_num) > int(order_num):
            number = 1
            for banner in banners:
                if int(order_num) <= number < int(old_order_num):
                    RecBanner.objects.filter(id=banner.id).update(order_num=number+1, name=name)
                    number += 1
        result = '序号已更新'
    else:
        result = '%s已存在banner列表中，不需再新增' % target_id
    username = request.user
    user = User.objects.get(username=username)
    goal_id = RecBanner.objects.all().order_by('-id')[0].id
    game_operation = GameOperation(user_id=user.id, user_name=user.last_name+user.first_name, page='市场推荐页', goal='banner_id: %s' % str(goal_id), action='新增banner', operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0])
    game_operation.save()
    banner_list.append(target_id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def upBanner(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    banner_id = request.POST.get('banner_id')
    order_num = RecBanner.objects.get(id=banner_id).order_num
    up_banner_id = RecBanner.objects.get(order_num=order_num-1).id
    up_order_num = order_num - 1
    RecBanner.objects.filter(id=banner_id).update(order_num=up_order_num)
    RecBanner.objects.filter(id=up_banner_id).update(order_num=order_num)
    response.write('Yes')
    return response


@csrf_exempt
@login_required
def downBanner(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/string'
    banner_id = request.POST.get('banner_id')
    order_num = RecBanner.objects.get(id=banner_id).order_num
    down_banner_id = RecBanner.objects.get(order_num=order_num+1).id
    down_order_num = order_num + 1
    RecBanner.objects.filter(id=banner_id).update(order_num=down_order_num)
    RecBanner.objects.filter(id=down_banner_id).update(order_num=order_num)
    response.write('Yes')
    return response


@csrf_exempt
@login_required
def delBanner(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    banner_id = request.POST.get('banner_id')
    RecBanner.objects.get(id=banner_id).delete()
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id, user_name=user.last_name+user.first_name, page='市场推荐页', goal='banner_id: %s' % str(banner_id), action='删除banner',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0])
    game_operation.save()
    order_num = 1
    banners = RecBanner.objects.all().order_by('order_num')
    for banner in banners:
        banner_id = banner.id
        RecBanner.objects.filter(id=banner_id).update(order_num=order_num)
        order_num += 1
    result = '推荐游戏列表页的%s banner已删除！！！' % str(banner_id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def isenabledBanner(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    banner_id = request.POST.get('banner_id')
    RecBanner.objects.filter(id=banner_id).update(enabled=1)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场推荐页',goal='banner_id: %s' % str(banner_id),action='启用banner',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s 已启用!!!' % str(banner_id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def notenabledBanner(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    banner_id = request.POST.get('banner_id')
    RecBanner.objects.filter(id=banner_id).update(enabled=0)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场推荐页',goal='banner_id: %s' % str(banner_id),action='下线banner',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s 已禁用!!!' % str(banner_id)
    response.write(result)
    return response