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
from market.models import TopicInfo, TopicGame, GameLabelInfo
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


@csrf_exempt
@login_required
def index(request):
    topic_types = []
    topic_types.append(['0', '普通专题'.decode('utf-8')])
    topic_types.append(['1', '神奇周五'.decode('utf-8')])
    topic_types.append(['2', 'gg特色－内购破解'.decode('utf-8')])
    topic_type = request.GET.get('source') if 'source' in request.GET else '0'
    topics = TopicInfo.objects.filter(topic_type=topic_type).order_by('order_num')
    number = 1
    for topic in topics:
        topic.topic_date = getDate(topic.topic_date)
        topic.unrelease_date = getDate(topic.unrelease_date)
        TopicInfo.objects.filter(id=topic.id).update(order_num=number)
        number += 1
    return render_to_response('market/topic/index.html', {
        'topics': topics,
        'topic_type': topic_type,
        'topic_types': topic_types,
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def add(request):
    topic_id = request.GET.get('topic_id')
    topic_type = request.GET.get('topic_type')
    if topic_id:
        topic = TopicInfo.objects.get(id=topic_id)
        topic.topic_date = getDate(topic.topic_date)
        topic.unrelease_date = getDate(topic.unrelease_date)
        games = TopicGame.objects.filter(topic_id=topic_id).order_by('order_num')
    else:
        DATE = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        topic = {'topic_date': DATE}
    return render_to_response('market/topic/edit.html', {
        'topic': topic,
        'games': games,
        'topic_type': topic_type,
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def edit(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    topic_id = request.POST.get('id', '')
    name = request.POST.get('name', '')
    short_desc = request.POST.get('short_desc', '')
    detail_desc = request.POST.get('detail_desc', '')
    pic_url = request.POST.get('pic_url', '')
    order_num = request.POST.get('order_num')
    topic_date = request.POST.get('topic_date')
    unrelease_date = request.POST.get('unrelease_date')
    not_test = request.POST.get('not_test')


    if not name or not short_desc or not pic_url:
        response.write('请输入专题信息!!!')
        return response

    topic_date = getTimeStamp(topic_date) if topic_date else 0
    unrelease_date = getTimeStamp(unrelease_date) if unrelease_date else 0

    if topic_id:
        "专题存在　更新信息"
        TopicInfo.objects.filter(id=topic_id).update(name=name, short_desc=short_desc, detail_desc=detail_desc, pic_url=pic_url, topic_date=topic_date, unrelease_date=unrelease_date,not_test=not_test)
    elif topic_id_index:
        order_num = 1
        topic = TopicInfo.objects.get(id=topic_id_index)
        order_num_index = topic.order_num

        topics = TopicInfo.objects.all().order_by('order_num')
        for topic in topics:
            topic_id = topic.id
            if int(topic_id) == int(topic_id_index):
                order_num += 1
            TopicInfo.objects.filter(id=topic_id).update(order_num=order_num)
            order_num += 1

        topic = TopicInfo(name=name, short_desc=short_desc,
                detail_desc=detail_desc, pic_url=pic_url,
                topic_date=topic_date, order_num=order_num_index, enabled=0, unrelease_date=unrelease_date,not_test=not_test)
        topic.save()
        goal_id = TopicInfo.objects.all().order_by('-id')[0].id
        username = request.user
        user = User.objects.get(username=username)
        game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='专题编辑页',goal='专题id: %s' % str(goal_id),action='新增或编辑专题信息',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
        game_operation.save()
 
        topics = TopicInfo.objects.all().order_by('id')
        for topic in topics:
            topic_id = topic.id
        result = '%s专题已添加!!!' % str(topic_id)
    else:
        order_num = 1
        topics = TopicInfo.objects.all().order_by('order_num')
        for topic in topics:
            topic_id = topic.id
            order_num += 1
            TopicInfo.objects.filter(id=topic_id).update(order_num=order_num)

        topic = TopicInfo(name=name, short_desc=short_desc,
                detail_desc=detail_desc, pic_url=pic_url,
                topic_date=topic_date, order_num=1, enabled=0, unrelease_date=unrelease_date,not_test=not_test)
        topic.save()
        goal_id = TopicInfo.objects.all().order_by('-id')[0].id
        username = request.user
        user = User.objects.get(username=username)
        game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='专题编辑页',goal='专题id: %s' % str(goal_id),action='新增或编辑专题信息',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
        game_operation.save()
        topics = TopicInfo.objects.all().order_by('id')
        for topic in topics:
            topic_id = topic.id
    response.write(topic_id)
    return response


@csrf_exempt
@login_required
def istest(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    id = request.POST.get('topic_id')
    TopicInfo.objects.filter(id=id).update(not_test=0)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场专题页',goal='专题id: %s' % str(id),action='更改为测试专题',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s 已启用!!!' % str(id)
    response.write(result)
    return response

@csrf_exempt
@login_required
def nottest(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    id = request.POST.get('topic_id')
    TopicInfo.objects.filter(id=id).update(not_test=1)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场专题页',goal='专题id: %s' % str(id),action='更改为合格专题',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s 已禁用!!!' % str(id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def isenabled(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    id = request.POST.get('topic_id')
    TopicInfo.objects.filter(id=id).update(enabled=1)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场专题页',goal='专题id: %s' % str(id),action='启用专题',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s 已启用!!!' % str(id)
    response.write(result)
    return response

@csrf_exempt
@login_required
def notenabled(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    id = request.POST.get('topic_id')
    TopicInfo.objects.filter(id=id).update(enabled=0)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场专题页',goal='专题id: %s' % str(id),action='下线专题',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s 已禁用!!!' % str(id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def up(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    topic_id = request.POST.get('topic_id')
    topic_type = request.POST.get('topic_type')
    order_num = TopicInfo.objects.get(id=topic_id).order_num
    up_topic_id = TopicInfo.objects.get(topic_type=topic_type, order_num=order_num-1).id
    up_order_num = order_num - 1
    TopicInfo.objects.filter(id=topic_id).update(order_num=up_order_num)
    TopicInfo.objects.filter(id=up_topic_id).update(order_num=order_num)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场专题页',goal='专题id: %s' % str(topic_id),action='上移专题',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write('Yes')
    return response


@csrf_exempt
@login_required
def delete(request):

    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)

    topic_id = request.POST.get('topic_id')

    TopicInfo.objects.get(id=topic_id).delete()
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场专题页',goal='专题id: %s' % str(topic_id),action='删除专题',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    order_num = 1
    topics = TopicInfo.objects.all().order_by('order_num')
    for topic in topics:
        topic_id = topic.id
        TopicInfo.objects.filter(id=topic_id).update(order_num=order_num)
        order_num += 1
    result = '专题%s已删除！！！' % str(topic_id)
    response.write(result)
    return response

@csrf_exempt
@login_required
def down(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    topic_id = request.POST.get('topic_id')
    topic_type = request.POST.get('topic_type')
    order_num = TopicInfo.objects.get(id=topic_id).order_num
    down_topic_id = TopicInfo.objects.get(topic_type=topic_type, order_num=order_num+1).id
    down_order_num = order_num + 1
    TopicInfo.objects.filter(id=topic_id).update(order_num=down_order_num)
    TopicInfo.objects.filter(id=down_topic_id).update(order_num=order_num)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场专题页',goal='专题id: %s' % str(topic_id),action='下移专题',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write('Yes')
    return response


@csrf_exempt
@login_required
def addGame(request):

    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)

    new_game_id = request.POST.get('game_id')
    game_id_index = request.POST.get('game_id_index')
    topic_id = request.POST.get('topic_id')

    try:
        game = TopicGame.objects.get(topic_id=topic_id,game_id=new_game_id)
        game_name = game.game_name
        result = '%s 已在专题列表内！！' % game_name
    except:
        if game_id_index:
            order_num = 1
            game = TopicGame.objects.get(topic_id=topic_id,game_id=game_id_index)
            order_num_index = game.order_num

            games = TopicGame.objects.filter(topic_id=topic_id).order_by('order_num')
            for game in games:
                game_id = game.game_id
                if game_id == game_id_index:
                    order_num += 1
                TopicGame.objects.filter(topic_id=topic_id,game_id=game_id).update(order_num=order_num)
                order_num += 1

            game_id = request.POST.get('game_id')
            game = GameLabelInfo.objects.get(game_id=game_id)
            game_name = game.game_name
            games = TopicGame(game_id=game_id,topic_id=topic_id,game_name=game_name,order_num=order_num_index)
            games.save()
            result = '%s已添加到%s!!! %s' % (game_name, str(topic_id), str(order_num_index))
        else:
            order_num = 1
            games = TopicGame.objects.filter(topic_id=topic_id).order_by('order_num')
            for game in games:
                order_num += 1
                game_id = game.game_id
                TopicGame.objects.filter(topic_id=topic_id,game_id=game_id).update(order_num=order_num)
                

            game_id = request.POST.get('game_id')
            game = GameLabelInfo.objects.get(game_id=game_id)
            game_name = game.game_name
            games = TopicGame(game_id=game_id,topic_id=topic_id,game_name=game_name,order_num=1)
            games.save()
            result = '%s已添加到%s!!!' % (game_name, str(topic_id))
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='专题编辑页',goal='专题id: %s, 游戏id: %s' % (str(topic_id), str(game_id)),action='新增游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
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
    topic_id = request.POST.get('topic_id')

    TopicGame.objects.get(game_id=game_id, topic_id=topic_id).delete()
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='专题编辑页',goal='专题id: %s, 游戏id: %s' % (str(topic_id), str(game_id)),action='删除游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
 
    game_operation.save()
    order_num = 1
    games = TopicGame.objects.filter(topic_id=topic_id).order_by('order_num')
    for game in games:
        game_id = game.game_id
        TopicGame.objects.filter(game_id=game_id,topic_id=topic_id).update(order_num=order_num)
        order_num += 1
 
    result = '%s下的%s游戏已删除！！！' % (str(topic_id), str(game_id))
    response.write(result)
    return response

@csrf_exempt
@login_required
def moveGame(request):

    response=HttpResponse()  
    response['Content-Type'] = 'text/string'

    game_id = request.POST.get('game_id')
    topic_id = request.POST.get('topic_id')
    index = int(request.POST.get('index'))
    old_index = int(TopicGame.objects.get(game_id=game_id,topic_id=topic_id).order_num)

    games = TopicGame.objects.filter(topic_id=topic_id).order_by('order_num')
    indexs = []
    new_indexs = []
    for game in games:
        indexs.append(game.game_id)
    if index <= 1:
        index = 1
    if index >= len(indexs):
        index = len(indexs)
    
    if old_index > index:
        new_indexs = indexs[:index-1] + [game_id] + indexs[index-1:old_index-1] + indexs[old_index:]
        order_num = 1
        for game_id in new_indexs:
            TopicGame.objects.filter(topic_id=topic_id,game_id=game_id).update(order_num=order_num)
            order_num += 1
    elif old_index < index:
        new_indexs = indexs[:old_index-1] + indexs[old_index:index] + [game_id] + indexs[index:]
        order_num = 1
        for game_id in new_indexs:
            TopicGame.objects.filter(topic_id=topic_id,game_id=game_id).update(order_num=order_num)
            order_num += 1
    else:
        pass

    result = str(indexs) + '\n' + str(new_indexs)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='专题编辑页',goal='专题id: %s, 游戏id: %s' % (str(topic_id), str(game_id)),action='移动游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
 
    game_operation.save()
    response.write(result)
    return response

@csrf_exempt
@login_required
def upGame(request):

    response=HttpResponse()  
    response['Content-Type'] = 'text/string'

    topic_id = request.POST.get('topic_id')
    game_id = request.POST.get('game_id')

    indexs = []
    games = TopicGame.objects.filter(topic_id=topic_id).order_by('order_num')
 
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
        TopicGame.objects.filter(game_id=game_id,topic_id=topic_id).update(order_num=up_num)
        TopicGame.objects.filter(game_id=up_id,topic_id=topic_id).update(order_num=num)
        result = 'Yes'
    else:
        result = 'Error'
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='专题编辑页',goal='专题id: %s, 游戏id: %s' % (str(topic_id), str(game_id)),action='上移游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
 
    game_operation.save()
    response.write(result)
    return response

@csrf_exempt
@login_required
def downGame(request):

    response=HttpResponse()  
    response['Content-Type'] = 'text/string'

    topic_id = request.POST.get('topic_id')
    game_id = request.POST.get('game_id')

    indexs = []
    games = TopicGame.objects.filter(topic_id=topic_id).order_by('order_num')
 
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
        TopicGame.objects.filter(game_id=game_id,topic_id=topic_id).update(order_num=down_num)
        TopicGame.objects.filter(game_id=down_id,topic_id=topic_id).update(order_num=num)
        result = 'Yes'
    else:
        result = 'Error'
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='专题编辑页',goal='专题id: %s, 游戏id: %s' % (str(topic_id), str(game_id)),action='下移游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
 
    game_operation.save()
 
    response.write(result)
    return response
