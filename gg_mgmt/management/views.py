#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Count
from management.models import GameDeveloper, GameOperation, TestImei
from forum.models import EditorInfo
from testers.models import IplayTesters
from game.models import GameLabelInfo
from iplay_utils.utils import pagination, get_perm, getDate

import os
import time
import json
import logging

@csrf_exempt
@login_required
def index(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    top_developers = GameDeveloper.objects.filter(is_top=1).order_by('manual_num')
    game_developer = GameDeveloper.objects.all()
    infos, page_range, per_page = pagination(request, game_developer)
    count = len(game_developer)
    count_page = count / 25
    return render_to_response('management/index.html', {
        'html': '/gg_mgmt/developer/index/',
        'top_developers': top_developers,
        'infos': infos,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page + 1,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def add(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    developer_id = request.GET.get('developer_id')
    if developer_id:
        developer = GameDeveloper.objects.get(id=developer_id)
    else:
        developer = {}
    return render_to_response('management/edit.html', {
        'html': '/gg_mgmt/developer/index/',
        'developer': developer
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def delete(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    try:
        dev_id = request.POST.get('dev_id')
        game_dev = GameDeveloper.objects.get(id=dev_id)
        game_dev.delete()
        game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='游戏厂商管理',goal='游戏厂商id: %s' % str(dev_id),action='删除游戏厂商',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
        game_operation.save()
        response.write('删除成功')
    except Exception as e:
        response.write(e.message)
    return response

@csrf_exempt
@login_required
def edit(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    developer_id = request.POST.get('developer_id')
    name = request.POST.get('name')
    icon_url = request.POST.get('icon_url')
    manual_num = request.POST.get('manual_num')
    is_top = request.POST.get('is_top')
    if not manual_num:
        manual_num = 0
    if developer_id:
        developer = GameDeveloper.objects.filter(id=developer_id).update(developer=name, icon_url=icon_url, manual_num=manual_num, is_top=is_top)
        result = '编辑成功！！！'
    else: 
        try:
            developer = GameDeveloper(developer=name, icon_url=icon_url, manual_num=manual_num, is_top=is_top)
            developer.save()
            result = '编辑成功！！！'
            developer_id = GameDeveloper.objects.all().order_by('-id')[0].id
        except:
            result = '厂商已添加！！！'
            developer_id = GameDeveloper.objects.get(developer=name).id
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='游戏厂商管理',goal='游戏厂商id: %s' % str(developer_id),action='修改游戏厂商名字',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write(result)
    return response


@csrf_exempt
@login_required
def game_list(request, dev_name):
    username = request.user
    user = User.objects.get(username=username)
    game_developer = GameLabelInfo.objects.using('game').filter(developer=dev_name)
    infos, page_range, per_page = pagination(request, game_developer)
    for info in infos:
        info.save_timestamp = getDate(info.save_timestamp)
    count = len(game_developer)
    count_page = count / 25
    return render_to_response('management/game_list.html', {
        'html': '/gg_mgmt/developer/index/',
        'infos': infos,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page + 1,
        'user': user,
        'dev_name': dev_name
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def operation(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    operation_date = request.GET.get('operation_date') if request.GET.get('operation_date') else getDate(time.time()).split(' ')[0] + ' - ' +getDate(time.time()).split(' ')[0]  
    user_name = request.GET.get('user_name') if 'user_name' in request.GET else '全部用户'
    page = request.GET.get('page') if 'page' in request.GET else '全部页面'
    action = request.GET.get('action')
    start_date = operation_date.split(' - ')[0] if operation_date else getDate(time.time()).split(' ')[0]
    end_date = operation_date.split(' - ')[1] if operation_date else getDate(time.time()).split(' ')[0]
    timeArray = time.strptime(start_date, '%Y-%m-%d')
    start_time = int(time.mktime(timeArray))
    timeArray = time.strptime(end_date, '%Y-%m-%d')
    end_time = int(time.mktime(timeArray)) + 86400
    Users = ['全部用户']
    Pages = ['全部页面']
    user_names = GameOperation.objects.filter(operation_time__gte=start_time,operation_time__lte=end_time).exclude(user_name='').values('user_name').annotate(count=Count('user_name'))   
    for name in user_names:
        Users.append(name['user_name'])
    if user_name == '全部用户':
        pages = GameOperation.objects.filter(operation_time__gte=start_time,operation_time__lte=end_time).values('page').annotate(count=Count('page'))   
        for Page in pages:
            Pages.append(Page['page'])
        if page  == '全部页面':
            game_developer = GameOperation.objects.filter(operation_time__gte=start_time,operation_time__lte=end_time)
        else:
            game_developer = GameOperation.objects.filter(operation_time__gte=start_time,operation_time__lte=end_time,page=page)
    else:
        pages = GameOperation.objects.filter(operation_time__gte=start_time,operation_time__lte=end_time,user_name=user_name).values('page').annotate(count=Count('page'))   
        for Page in pages:
            Pages.append(Page['page'])
        if page  == '全部页面':
            game_developer = GameOperation.objects.filter(operation_time__gte=start_time,operation_time__lte=end_time,user_name=user_name)
        else:
            game_developer = GameOperation.objects.filter(operation_time__gte=start_time,operation_time__lte=end_time,user_name=user_name,page=page)
 
    #game_developer = GameOperation.objects.filter(operation_time__gte=start_time,operation_time__lte=end_time,user_name=user_name,page=page)
    for item in game_developer:
        item.operation_time = getDate(item.operation_time)
        if item.goal.find('游戏id') != -1:
             try:
                 game_id = item.goal.split('游戏id: ')[1]
                 game = GameLabelInfo.objects.get(game_id=game_id)
                 #item.goal += item.goal + '<a href="/gg_mgmt/game/detail/?game_id=%s">%s</a>' % (game_id, game.game_name)
                 item.goal += '; 游戏名: '+ game.game_name
                 item.game_id = game_id
                 item.game_name = game.game_name
             except:
                 pass

    infos, page_range, per_page = pagination(request, game_developer)
    count = len(game_developer)
    count_page = count / 25
    return render_to_response('management/operation.html', {
        'html': '/gg_mgmt/developer/operation/',
        'infos': infos,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page + 1,
        'operation_date': operation_date,
        'pages': Pages,
        'page': page,
        'user_names': Users,
        'user_name': user_name,
#        'actions': actions,
#        'action': action,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def imei(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    game_developer = TestImei.objects.all()
    infos, page_range, per_page = pagination(request, game_developer)
    count = len(game_developer)
    count_page = count / 25
    return render_to_response('management/imei.html', {
        'html': '/gg_mgmt/developer/imei/',
        'infos': infos,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page + 1,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def editImei(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    imei = request.GET.get('imei')
    list = TestImei.objects.get(imei=imei) if imei else {}
    return render_to_response('management/editImei.html', {
        'html': '/gg_mgmt/developer/imei/',
        'list': list,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def addImei(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    try:
        imei = request.POST.get('imei')
        user_name = request.POST.get('user_name')
        game_imei = TestImei(imei=imei,user_name=user_name)
        game_imei.save()
        os.system("wget -O - 'http://116.255.129.52/cache/clear?name=iplay_test_imei'")
        game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='测试手机imei管理',goal='imeiid: %s' % str(imei),action='新增测试手机',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
        game_operation.save()
        response.write(imei)
    except Exception as e:
        response.write(e.message)
    return response


@csrf_exempt
@login_required
def deleteImei(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    try:
        imei = request.POST.get('imei')
        game_dev = TestImei.objects.get(imei=imei)
        game_dev.delete()
        os.system("wget -O - 'http://116.255.129.52/cache/clear?name=iplay_test_imei'")
        game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='测试手机imei管理',goal='imei: %s' % str(imei),action='删除测试手机',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
        game_operation.save()
        response.write('删除成功%s' % imei)
    except Exception as e:
        response.write(e.message)
    return response


@csrf_exempt
@login_required
def consumer(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    imeis = set()
    tests = TestImei.objects.all()
    for test in tests:
        imeis.add(test.imei)
    consumer = IplayTesters.objects.all().order_by('-id')
    infos, page_range, per_page = pagination(request, consumer)
    for query in infos:
        query.status = 1 if query.imei in imeis else 0
    count = len(consumer)
    count_page = count / per_page
    return render_to_response('management/consumer.html', {
        'html': '/gg_mgmt/developer/consumer/',
        'infos': infos,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page + 1,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def editor(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    try:
        editor = EditorInfo.objects.get(name=user.last_name+user.first_name)
    except:
        editor = {}
    return render_to_response('management/editor.html', {
        'html': '/gg_mgmt/developer/editor/',
        'editor': editor,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def editEditor(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    try:
        name = request.POST.get('name')
        icon_url = request.POST.get('icon_url')
        desc = request.POST.get('desc')
        editor = EditorInfo.objects.filter(name=name).update(icon_url=icon_url, user_desc=desc)
        game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='小编信息编辑',goal='name: %s' % str(name),action='修改信息',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
        game_operation.save()
        response.write('修改成功')
    except Exception as e:
        response.write(e.message)
    return response
