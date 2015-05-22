# -*- coding:utf-8 -*-


from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from market.models import GameLabelInfo, CatGame, GameCatInfo, CatToGame
from management.models import GameOperation
from forum.models import IplayEditorInfo

import os
import time
import datetime


import sys
reload(sys)
sys.setdefaultencoding('utf8')

DIR = os.getcwd()
sys.path.append(DIR)
from iplay_utils.utils import getTimeStamp, getDate, get_perm


@csrf_exempt
@login_required
def index(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    category_id = request.GET.get('category_id') if 'category_id' in request.GET else '1'
    category_infos = GameCatInfo.objects.filter(parent_id=0)
    categorys = []
    for category in category_infos:
        categorys.append([str(category.id), category.display_name])
    categorys.append(['1000001', '全部游戏'.decode('utf-8')])
    categorys.append(['1000002', '辅助专区'.decode('utf-8')])
    categorys.append(['1000003', '精选单机'.decode('utf-8')])
    categorys.append(['1000004', '热门网游'.decode('utf-8')])
    games = CatGame.objects.filter(category_id=category_id).order_by('manual_num')
    num = 1
    for game in games:
        CatGame.objects.filter(game_id=game.game_id, category_id=game.category_id).update(manual_num=num)
        num += 1
    games4peo = CatGame.objects.filter(category_id=category_id).order_by('manual_num')
    games4system = CatToGame.objects.filter(category_id=category_id, order_type=4).order_by('order_num')
    games4sys = []
    peo = set()
    for game in games4peo:
        game_id = game.game_id
        gamelabel = GameLabelInfo.objects.get(game_id=game_id)
        game.game_enabled = gamelabel.enabled
        game.game_name = gamelabel.game_name
        game.release_date = getDate(game.release_date)
        game.unrelease_date = getDate(game.unrelease_date)
        peo.add(game_id)
    for game in games4system:
        game_id = game.game_id
        gamelabel = GameLabelInfo.objects.get(game_id=game_id)
        game.enabled = gamelabel.enabled
        game.game_name = gamelabel.game_name
        if game_id not in peo: 
            games4sys.append(game)
    number = len(games4system)
    return render_to_response('market/category/index.html', {
        'html': '/gg_mgmt/market/category/',
        'games4peo': games4peo,
        'games4sys': games4sys,
        'category_id': category_id,
        'categorys': categorys,
        'number': number,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def addGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    category_id = request.GET.get('category_id')
    DATE = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    game = {'release_date': DATE}
    return render_to_response('market/category/game_edit.html', {
            'category_id': category_id,
            'game': game,
        }, context_instance=RequestContext(request))


@login_required
def alterGame(request):
    game_id = request.GET.get('game_id')
    category_id = int(request.GET.get('category_id'))
    game = CatGame.objects.get(game_id=game_id, category_id=category_id)
    game.release_date = getDate(game.release_date)
    game.unrelease_date = getDate(game.unrelease_date)
    return render_to_response('market/category/game_edit.html', {
            'category_id': category_id,
            'game': game,
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def delGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    game_id = request.POST.get('game_id')
    manual_num = request.POST.get('manual_num')
    category_id = int(request.POST.get('category_id')) if 'category_id' in request.POST else 1
    CatGame.objects.get(game_id=game_id, category_id=category_id).delete()
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id, user_name=user.last_name+user.first_name, page='市场分类页', goal='分类id: %s, 游戏id: %s' % (str(category_id), str(game_id)),action='删除游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0])
    game_operation.save()
    result = '%s已被删除' % str(game_id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def editGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_id = request.POST.get('game_id')
    manual_num = request.POST.get('manual_num')
    release_date = request.POST.get('release_date')
    unrelease_date = request.POST.get('unrelease_date')
    category_id = request.POST.get('category_id')
    release_date = getTimeStamp(release_date) if release_date else 0
    unrelease_date = getTimeStamp(unrelease_date) if unrelease_date else 0
    games = CatGame.objects.filter(category_id=category_id).order_by('manual_num')
    game_list = []
    for game in games:
        game_list.append(game.game_id)
    #　新增游戏，插入位置之后的游戏依次后移一位
    if game_id not in game_list:
        game = GameLabelInfo.objects.get(game_id=game_id)
        game_name = game.game_name
        CatGame(game_id=game_id, category_id=category_id, game_name=game_name, manual_num=manual_num, release_date=release_date, unrelease_date=unrelease_date).save()
        number = 1
        for game_id in game_list:
            if int(number) >= int(manual_num):
                CatGame.objects.filter(game_id=game_id, category_id=category_id).update(manual_num=number+1)
            number += 1
    else:
        old_manual_num = CatGame.objects.get(game_id=game_id, category_id=category_id).manual_num
        CatGame.objects.filter(game_id=game_id, category_id=category_id).update(manual_num=manual_num)
        # 后移 两位置之间的依次前移一位
        if int(old_manual_num) < int(manual_num):
            number = 1
            for game_id in game_list:
                if int(old_manual_num) < number <= int(manual_num):
                    CatGame.objects.filter(game_id=game_id, category_id=category_id).update(manual_num=number-1)
                number += 1
        # 前移　两位置之间的依次后移一位
        if int(old_manual_num) > int(manual_num):
            number = 1
            for game_id in game_list:
                if int(manual_num) <= number < int(old_manual_num):
                    CatGame.objects.filter(game_id=game_id, category_id=category_id).update(manual_num=number+1)
                number += 1
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id, user_name=user.last_name+user.first_name, page='市场分类页', goal='分类id: %s, 游戏id: %s' % (str(category_id), str(game_id)),action='新增或编辑游戏信息',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0])
    game_operation.save()
    response.write(str(game_id))
    return response


@csrf_exempt
@login_required
def isenabledGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_id = request.POST.get('game_id')
    category_id = request.POST.get('category_id')
    CatGame.objects.filter(game_id=game_id, category_id=category_id).update(enabled=1)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id, user_name=user.last_name+user.first_name, page='市场分类页', goal='分类id: %s, 游戏id: %s' % (str(category_id), str(game_id)),action='启用游戏',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0])
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
    category_id = request.POST.get('category_id')
    CatGame.objects.filter(game_id=game_id, category_id=category_id).update(enabled=0)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id, user_name=user.last_name+user.first_name, page='市场分类页', goal='分类id :%s, 游戏id :%s' % (str(category_id), str(game_id)),action='游戏下线',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0])
    game_operation.save()
    result = '%s 已禁用!!!' % str(game_id)
    response.write(result)
    return response


@csrf_exempt
@login_required
def up_game(request):
    username = request.user
    user = User.objects.get(username=username)
    editor = IplayEditorInfo.objects.get(name=user.last_name+user.first_name)
    game_id = request.GET.get('game_id')
    category_id = request.GET.get('category_id')
    manual_num = CatGame.objects.get(game_id=game_id, category_id=category_id).manual_num
    up_game_id = CatGame.objects.get(category_id=category_id, manual_num=manual_num-1).game_id
    up_manual_num = manual_num - 1
    CatGame.objects.filter(game_id=game_id, category_id=category_id).update(manual_num=up_manual_num)
    CatGame.objects.filter(game_id=up_game_id, category_id=category_id).update(manual_num=manual_num)
    category_infos = GameCatInfo.objects.filter(parent_id=0)
    categorys = []
    for category in category_infos:
        categorys.append([str(category.id), category.display_name])
    categorys.append(['1000001', '全部游戏'.decode('utf-8')])
    categorys.append(['1000002', '辅助专区'.decode('utf-8')])
    categorys.append(['1000003', '精选单机'.decode('utf-8')])
    categorys.append(['1000004', '热门网游'.decode('utf-8')])
    games4peo = CatGame.objects.filter(category_id=category_id).order_by('manual_num')
    games4system = CatToGame.objects.filter(category_id=category_id, order_type=4).order_by('order_num')
    games4sys = []
    peo = set()
    for game in games4peo:
        game_id = game.game_id
        gamelabel = GameLabelInfo.objects.get(game_id=game_id)
        game.game_enabled = gamelabel.enabled
        game.game_name = gamelabel.game_name
        game.release_date = getDate(game.release_date)
        game.unrelease_date = getDate(game.unrelease_date)
        peo.add(game_id)
    for game in games4system:
        game_id = game.game_id
        gamelabel = GameLabelInfo.objects.get(game_id=game_id)
        game.enabled = gamelabel.enabled
        game.game_name = gamelabel.game_name
    if game_id not in peo:
        games4sys.append(game)
    return render_to_response('market/category/index.html', {
        'games4peo': games4peo,
        'games4sys': games4sys,
        'category_id': category_id,
        'categorys': categorys,
        'editor': editor
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def down_game(request):
    username = request.user
    user = User.objects.get(username=username)
    editor = IplayEditorInfo.objects.get(name=user.last_name+user.first_name)
    game_id = request.GET.get('game_id')
    category_id = request.GET.get('category_id')
    manual_num = CatGame.objects.get(game_id=game_id, category_id=category_id).manual_num
    down_game_id = CatGame.objects.get(category_id=category_id, manual_num=manual_num+1).game_id
    down_manual_num = manual_num + 1
    CatGame.objects.filter(game_id=game_id, category_id=category_id).update(manual_num=down_manual_num)
    CatGame.objects.filter(game_id=down_game_id, category_id=category_id).update(manual_num=manual_num)
    category_infos = GameCatInfo.objects.filter(parent_id=0)
    categorys = []
    for category in category_infos:
        categorys.append([str(category.id), category.display_name])
    categorys.append(['1000001', '全部游戏'.decode('utf-8')])
    categorys.append(['1000002', '辅助专区'.decode('utf-8')])
    categorys.append(['1000003', '精选单机'.decode('utf-8')])
    categorys.append(['1000004', '热门网游'.decode('utf-8')])
    games4peo = CatGame.objects.filter(category_id=category_id).order_by('manual_num')
    games4system = CatToGame.objects.filter(category_id=category_id, order_type=4).order_by('order_num')
    games4sys = []
    peo = set()
    for game in games4peo:
        game_id = game.game_id
        gamelabel = GameLabelInfo.objects.get(game_id=game_id)
        game.game_enabled = gamelabel.enabled
        game.game_name = gamelabel.game_name
        game.release_date = getDate(game.release_date)
        game.unrelease_date = getDate(game.unrelease_date)
        peo.add(game_id)
    for game in games4system:
        game_id = game.game_id
        gamelabel = GameLabelInfo.objects.get(game_id=game_id)
        game.enabled = gamelabel.enabled
        game.game_name = gamelabel.game_name
    if game_id not in peo:
        games4sys.append(game)
    return render_to_response('market/category/index.html', {
        'games4peo': games4peo,
        'games4sys': games4sys,
        'category_id': category_id,
        'categorys': categorys,
        'editor': editor
    }, context_instance=RequestContext(request))