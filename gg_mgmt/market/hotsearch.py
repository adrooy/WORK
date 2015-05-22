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
from market.models import GameLabelInfo, CatGame, GameCatInfo, CatToGame, HotSearch
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

from iplay_utils.utils import getTimeStamp, getDate, get_perm

import sys
reload(sys)
sys.setdefaultencoding('utf8')

@csrf_exempt
@login_required
def index(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    words = HotSearch.objects.all().order_by('order_num')[0:3]
    auto_words = HotSearch.objects.all().order_by('order_num')[3:]
    return render_to_response('market/hotsearch/index.html', {
        'html': '/gg_mgmt/market/hotsearch/',
        'words': words,
        'auto_words': auto_words,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def add(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    word = request.POST.get('word')
    order_num = request.POST.get('order_num')
    hotsearch = HotSearch(word=word,order_num=order_num)
    hotsearch.save()
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场热门词',goal=word,action='新增热门词',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s已增加' % str(word)
    response.write(result)
    return response


@csrf_exempt
@login_required
def delete(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    word = request.POST.get('word')
    HotSearch.objects.get(word=word).delete()
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场热门词',goal=word,action='删除热门词',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s已被删除' % str(word)
    response.write(result)
    return response


@csrf_exempt
@login_required
def edit(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    word = request.POST.get('word')
    order_num = request.POST.get('order_num')
    HotSearch.objects.get(order_num=order_num).delete()
    hotsearch = HotSearch(word=word,order_num=order_num)
    hotsearch.save()
    os.system('python /home/mgmt/game-helper/hotsearch --loglevel DEBUG --settings /home/mgmt/game-helper/hotsearch/etc/hotsearch/178.json')
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='市场热门词',goal=word,action='编辑热门词序号',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '%s已被编辑' % str(word)
    response.write(result)
    return response

def search(request):
    word = request.GET.get('word')
    search_shell = '/opt/lucence/bin/searchgames2.sh %s 10' % word
    search_result = json.loads(os.popen(search_shell).readlines()[0].strip())   

    games = []
    number = 1
    for game_id in search_result:
        game = GameLabelInfo.objects.get(game_id=game_id)
        game.index = number 
        games.append(game)
        number += 1
    return render_to_response('market/hotsearch/result.html', {
            'word': word,
            'search_result': search_result,
            'game': game,
            'games': games
        }, context_instance=RequestContext(request))
