#!/usr/bin/env python
#-*- coding:utf-8 -*-

__author__ = 'limingdong'


from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import GameLabelInfo, GamePkgInfo, GameResourceInfo, ResourceMatchResult, ResourceMatchCondition, UploadGame, ReleaseList, Advert
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from json import dumps, loads, JSONEncoder
from django.db.models.query import QuerySet
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User 
from management.models import GameDeveloper, GameOperation
from forum.models import NotPlayModel, NotPlayFingerprint


from django.db import connection
from iplay_utils.utils import getTimeStamp, getDate, get_perm, get_collapse, get_sorted, get_game_name, get_game_info

from .consts import COLOR_LABELS

import os
import json
import logging
import hashlib
import time
import sys

#sys.path.append('/home/mgmt/operation_auto_upload_apk')
#from upload_data import main


class DjangoJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, QuerySet):
            return loads(serialize('json', obj))
        return JSONEncoder.default(self, obj)


@csrf_exempt
@login_required
def not_play(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    game_id = request.GET.get('game_id')
    models = NotPlayModel.objects.filter(gameid=game_id)
    fingerprints = NotPlayFingerprint.objects.filter(gameid=game_id)
    for model in models:
        model.save_timestamp = getDate(model.save_timestamp)
    for fingerprint in fingerprints:
        fingerprint.save_timestamp = getDate(fingerprint.save_timestamp)
    game_name = GameLabelInfo.objects.get(game_id=game_id).display_name
    return render_to_response('game/not_play.html', {
        'game_id': game_id,
        'game_name': game_name,
        'models': models,
        'fingerprints': fingerprints,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def edit_not_play(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    game_id = request.POST.get('game_id')
    type = request.POST.get('type')
    if type == 'model':
        model = request.POST.get('model')
        not_play_model = NotPlayModel(gameid=game_id, model=model, user_name=user.last_name+user.first_name, save_timestamp=int(time.time()))
        not_play_model.save()
    if type == 'fingerprint':
        fingerprint = request.POST.get('fingerprint')
        not_play_fingerprint = NotPlayFingerprint(gameid=game_id, fingerprint=fingerprint, user_name=user.last_name+user.first_name, save_timestamp=int(time.time()))
        not_play_fingerprint.save()
    response.write('yes')
    return response
 

@csrf_exempt
@login_required
def del_not_play(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    id = request.POST.get('id')
    type = request.POST.get('type')
    if type == 'model':
        not_play_model = NotPlayModel.objects.get(id=id)
        not_play_model.delete()
    if type == 'fingerprint':
        not_play_fingerprint = NotPlayFingerprint.objects.get(id=id)
        not_play_fingerprint.delete()
    response.write('yes')
    return response


@login_required
def prompt(request):
    username = request.user
    user = User.objects.get(username=username)
    msg = request.GET.get('msg')
    return render_to_response('uploadGame/prompt.html', {
        'msg': msg
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def advert(request):
    TYPE = [[1, '游戏安装时'], [2, '把手'], [3, '闪屏'], [4, '通知栏'], [10000002, 'GG助手把手'], [10000003, 'GG助手闪屏'], [10000004, 'GG助手通知栏']]
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    package_name = request.GET.get('package_name')
    if not package_name:
        info1 = Advert.objects.filter(package_name='default').order_by('order_num')
        info2 = Advert.objects.exclude(package_name='default').order_by('package_name', 'order_num')
        for info in info1:
    #        info.game_name = '缺省广告'
            try:
                info.target_name = get_game_name(info.target)
            except:
                pass
        for info in info2:
        #    info.game_name = get_game_name(info.game_id)
            try:
                info.target_name = get_game_name(info.target)
            except:
                pass
#        game_name = ''
        html = '/gg_mgmt/game/advert/'
    elif package_name == 'default':
        info1 = {}
 #       game_name = '缺省广告'
        info2 = Advert.objects.filter(package_name='default').order_by('order_num')
        for info in info2:
#            info.game_name = '缺省广告'
            try:
                info.target_name = get_game_name(info.target)
            except:
                pass
        html = ''
    else:
   #     game_name = get_game_name(game_id)
        info1 = Advert.objects.filter(package_name=package_name).order_by('order_num')
        info2 = Advert.objects.filter(package_name='default').order_by('order_num')
        for info in info2:
  #          info.game_name = '缺省广告'
            try:
                info.target_name = get_game_name(info.target)
            except:
                pass
        for info in info1:
 #           info.game_name = get_game_name(info.game_id)
            try:
                info.target_name = get_game_name(info.target)
            except:
                pass
        html = ''
    return render_to_response('game/advert.html', {
        'html': html,
        'perm_id': perm_id,
        'perm_name': perm_name,
#        'package_name': package_name,
  #      'game_name': game_name,
        'TYPE': TYPE,
        'info1': info1,
        'info2': info2,
        'user': user
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def edit_advert(request):
    #TYPE = [[1, '游戏安装时'], [2, '把手'], [3, '闪屏'], [4, '通知栏'], [10000002, 'GG助手把手'], [10000003, 'GG助手闪屏'], [10000004, 'GG助手通知栏']]
    TYPE = [[1, '游戏安装时'], [2, '把手'], [3, '闪屏'], [4, '通知栏'], [5, '应用推荐']]
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    package_name = request.GET.get('package_name')
    return render_to_response('game/edit_advert.html', {
        'perm_id': perm_id,
        'perm_name': perm_name,
        'package_name': package_name,
        'TYPE': TYPE,
        'user': user
    }, context_instance=RequestContext(request))
   

@csrf_exempt
@login_required
def add_advert(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    type = request.POST.get('type', '')
    package_name = request.POST.get('package_name', '')
    order_num = request.POST.get('order_num', '')
    content = request.POST.get('content', '')
    pic_url = request.POST.get('pic_url', '')
    target_type = request.POST.get('target_type', '')
    target = request.POST.get('target', '')
    id = request.POST.get('id', '')
    title = request.POST.get('title', '')
    big_pic_url = request.POST.get('big_pic_url', '')
    pkg_name = request.POST.get('pkg_name', '')
    ver_name = request.POST.get('ver_name', '')
    size = request.POST.get('size', '')
    filename = request.POST.get('filename', '')
    show_delay = request.POST.get('show_delay', '')
    if not size:
        size = 0
    if not show_delay:
        show_delay = 0
    if id:
        advert = Advert.objects.filter(id=id).update(type=type,package_name=package_name,order_num=order_num,content=content,pic_url=pic_url,target_type=target_type,target=target,title=title,big_pic_url=big_pic_url,pkg_name=pkg_name,ver_name=ver_name,size=size,filename=filename,show_delay=show_delay)
    else:
        advert = Advert(type=type,package_name=package_name,order_num=order_num,content=content,pic_url=pic_url,target_type=target_type,target=target,title=title,big_pic_url=big_pic_url,pkg_name=pkg_name,ver_name=ver_name,size=size,filename=filename,show_delay=show_delay)
        advert.save()
    response.write('yes')
    return response


@csrf_exempt
@login_required
def del_advert(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    id = request.POST.get('id')
    advert = Advert.objects.get(id=id)
    advert.delete()
    response.write('yes')
    return response


@csrf_exempt
@login_required
def edit_order(request):
    #TYPE = [[1, '游戏安装时'], [2, '把手'], [3, '闪屏'], [4, '通知栏'], [10000002, 'GG助手把手'], [10000003, 'GG助手闪屏'], [10000004, 'GG助手通知栏']]
    TYPE = [[1, '游戏安装时'], [2, '把手'], [3, '闪屏'], [4, '通知栏'], [5, '应用推荐']]
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    id = request.GET.get('id')
    info = Advert.objects.get(id=id)
    package_name = info.package_name
    return render_to_response('game/edit_advert.html', {
        'perm_id': perm_id,
        'perm_name': perm_name,
        'package_name': package_name,
        'TYPE': TYPE,
        'info': info,
        'user': user
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def uploadGame(request):
    username = request.user
    user = User.objects.get(username=username)
    source = int(request.GET.get('source_id')) if 'source_id' in request.GET  else 3
    is_finished = int(request.GET.get('is_finished')) if 'is_finished' in request.GET else 1
    games = UploadGame.objects.all().order_by('-start_date')
    count = len(games)
    errors = {}
    errors['202']='apk_id生成错误' 
    errors['201']='上传的百度盘文件大小和分析出的大小不一致' 
    errors['404']='其他错误'
    errors['301']='爬去google信息失败'
    errors['302']='下载的google图片失败'
    errors['303']='上传图片至七牛失败'
    errors['304']='更新图片信息到数据库失败'
    errors['399']='Google游戏上传成功'
    errors['101']='爬去渠道详情也失败，请检查详情页地址是否正确或这是否被封禁'
    errors['102']='分析详情页失败，可能页面改版或者选择的上传渠道和详情页地址不匹配'
    errors['103']='获取label和pkg信息失败'
    errors['104']='插入游戏数据失败'
    errors['105']='游戏下载地址为空'
    errors['106']='渠道内下载地址apk大小和解析的apk大小不一致'
    errors['199']='国内游戏上传成功'
    number = 1
    for game in games:
        game.start_date = getDate(game.start_date)
        game.end_date = getDate(game.end_date)
        game.finished = getTimeStamp(game.end_date) - getTimeStamp(game.start_date) if game.end_date else time.time() - getTimeStamp(game.start_date)
        game.index = number 
        number += 1
        game.msg = errors[str(game.msg)] if str(game.msg) in errors else '其他错误'
        if int(game.is_finished) == 0:
            game.msg = '' 
        try:
            GAME = GamePkgInfo.objects.get(apk_id=game.apk_id)          
            game.game_id = GAME.game_id
            game.game_name = GAME.game_name
            game.icon_url = GAME.icon_url
        except:
            game.game_id = ''
    feedback, page_range, per_page = lbe_pagination(request, games)
    count_page = count / 25
    return render_to_response('uploadGame/uploadGame.html', {
        'html': '/gg_mgmt/uploadGame/uploadGame/',
        'collapse': get_collapse('/gg_mgmt/uploadGame/uploadGame/'),
        'feedback': feedback,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page+1,
        'user': user,
        'is_finished': is_finished,
        'source': source
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def googleGame(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    return render_to_response('uploadGame/googleGame.html', {
        'collapse': get_collapse('/gg_mgmt/uploadGame/googleGame/'),
        'html': '/gg_mgmt/uploadGame/googleGame/',
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def addGoogleGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_json = request.POST.get('game_json')
    baidu_url = request.POST.get('baidu_url')
    detail_url = request.POST.get('detail_url')
    channel = request.POST.get('channel')
    update_desc = request.POST.get('update_desc')
    apk_info = eval(game_json)   
    apk_info['update_desc'] = update_desc
    game = UploadGame(apk_info=apk_info,detail_url=detail_url,channel=channel,baidupan_url=baidu_url,start_date=time.time(),is_finished=0,source=3)
    game.save()
    game = UploadGame.objects.all().order_by('-id')[0] 
    username = request.user
    user = User.objects.get(username=username)
    os.system('python /home/mgmt/operation_auto_upload_apk/upload_data.py 3 %d %s &' % (game.id, user.last_name+user.first_name))
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='GooglePlay游戏入库',goal='入库记录id: %s' % str(game.id),action='游戏入库',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write('uploadGame')
    return response


@login_required
def wandoujiaGame(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    return render_to_response('uploadGame/wandoujiaGame.html', {
        'collapse': get_collapse('/gg_mgmt/uploadGame/wandoujiaGame/'),
        'html': '/gg_mgmt/uploadGame/wandoujiaGame/',
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def addWandoujiaGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_json = request.POST.get('game_json')
    baidu_url = request.POST.get('baidu_url')
    channel = request.POST.get('channel')
    detail_url = request.POST.get('detail_url')
    update_desc = request.POST.get('update_desc')
    apk_info = eval(game_json)   
    apk_info['update_desc'] = update_desc
    game = UploadGame(apk_info=apk_info,detail_url=detail_url,channel=channel,baidupan_url=baidu_url,start_date=time.time(),is_finished=0,source=1)
    game.save()
    game = UploadGame.objects.all().order_by('-id')[0] 
    username = request.user
    user = User.objects.get(username=username)
    os.system('python /home/mgmt/operation_auto_upload_apk/upload_data.py 4 %d %s &' % (game.id, user.last_name+user.first_name))
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='国内市场游戏入库',goal='入库记录id: %s' % game.id,action='游戏入库',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write('uploadGame')
    return response


@login_required
def otherGame(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    return render_to_response('uploadGame/otherGame.html', {
        'collapse': get_collapse('/gg_mgmt/uploadGame/otherGame/'),
        'html': '/gg_mgmt/uploadGame/otherGame/',
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))



@csrf_exempt
@login_required
def addOtherGame(request):
    GPU = {
        '2': 2, #ADRENO
        '3': 3, #NVIDIA
        '4': 4, #POWERVR
        '5': 5, #MALI
        '52': 2, #ADRENO
        '53': 3, #NVIDIA
        '54': 4, #POWERVR
        '55': 5 #MALI
    }
    source3 = {
        '1': 'GG官方',
        '2': '高通版',
        '3': '英伟达',
        '4': 'PowerVR',
        '5': 'Mali',
        '6': '三星',
        '7': 'GG特色版',
        '8': 'GG存档版',
        '9': 'GG纪念版',
        '30': '全球版',
        '51': 'GG官方原包',
        '52': '高通版原包',
        '53': '英伟达原包',
        '54': 'PowerVR原包',
        '55': 'Mali原包',
        '56': '三星原包'
    }
    source4 = {
        '57': 'CMGE',
        '58': '360',
        '59': '其他'
    }
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    username = request.user
    user = User.objects.get(username=username)
    save_user = user.last_name+user.first_name 
    game_json = request.POST.get('game_json')
    apk_info = eval(game_json)   
    game_id = apk_info['gameid']
    game_name = request.POST.get('game_name')
    screen_shot_urls = request.POST.get('screen_shot_urls')
    icon_url = request.POST.get('icon_url')
    detail_desc = request.POST.get('detail_desc')
    game_language = request.POST.get('game_language')
    channelid = apk_info['channelid']
    source = 3 if channelid in source3 else 4
    developer = request.POST.get('developer')
    pkg_name = apk_info['pkg_name']
    ver_code = apk_info['ver_code']
    ver_name = apk_info['ver_name']
    file_size = apk_info['file_size']
    try:
        label_info = GameLabelInfo.objects.filter(game_id=game_id)
    except:
        label_info = GameLabelInfo(game_id=game_id,game_name=game_name,screen_shot_urls=screen_shot_urls,icon_url=icon_url,detail_desc=detail_desc,game_language=game_language,source=source,developer=developer,save_user=save_user,save_timestamp=int(time.time()),update_timestamp=int(time.time()),tid=0,download_counts=0,min_apk_size=file_size,max_apk_size=file_size,min_ver_name=ver_name,max_ver_name=ver_name,enabled=1,is_changed=0,subscript_expire_time=0,is_in_test=0,update_user=save_user)
        label_info.save()
    market_channel = source3[channelid] if channelid in source3 else source4[channelid]
    ver_code_by_gg = apk_info['ggvercode']
    download_url = request.POST.get('baidu_url')
    downloaded_cnts = 0
    download_url_type = 2 
    is_crack_apk = 1
    tid = 0
    depend_google_play = 0
    enabled = 1
    is_plugin_required = 1
    is_changed = 0
    gpu_vender = GPU[apk_info['channelid']] if apk_info['channelid'] in GPU else 1
    min_sdk = apk_info['min_sdk']
    file_md5 = apk_info['file_md5']
    signature_md5 = apk_info['signature_md5']
    update_desc = request.POST.get('update_desc')
    #计算apk_id
    name = str(pkg_name) + "$" + ver_name + "$" + market_channel + "$" + ver_code_by_gg
    apk_id = hashlib.sha1(name.lower()).hexdigest().lower()[:8]
    apk_info = GamePkgInfo(apk_id=apk_id,game_id=game_id,market_channel=market_channel,game_name=game_name,pkg_name=pkg_name,ver_code=ver_code,ver_name=ver_name,file_size=file_size,download_url=download_url,game_language=game_language,screen_shot_urls=screen_shot_urls,icon_url=icon_url,file_md5=file_md5,downloaded_cnts=downloaded_cnts,download_url_type=download_url_type,is_crack_apk=is_crack_apk,tid=tid,enabled=enabled,is_plugin_required=is_plugin_required,is_changed=is_changed,gpu_vender=gpu_vender,min_sdk=min_sdk,signature_md5=signature_md5,update_desc=update_desc,save_timestamp=int(time.time()),update_timestamp=int(time.time()),depend_google_play=depend_google_play,source=source,game_desc=detail_desc,ver_code_by_gg=ver_code_by_gg) 
    apk_info.save()
    #计算apk_id
    #name = str(pkg_name) + "$" + ver_name + "$" + channel + "$" + ver_code_by_gg
    #apk_id = hashlib.sha1(name.lower()).hexdigest().lower()[:8]
    #apk_info = eval(game_json)   
    #apk_info['update_desc'] = update_desc
    #game = UploadGame(apk_info=apk_info,detail_url=detail_url,channel=channel,baidupan_url=baidu_url,start_date=time.time(),is_finished=0,source=1)
    #game.save()
    #game = UploadGame.objects.all().order_by('-id')[0] 
    #username = request.user
    #user = User.objects.get(username=username)
    #os.system('python /home/mgmt/operation_auto_upload_apk/upload_data.py 4 %d %s &' % (game.id, user.last_name+user.first_name))
    #game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='国内市场游戏入库',goal='入库记录id: %s' % game.id,action='游戏入库',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    #game_operation.save()
    response.write(game_id)
    return response
 
@csrf_exempt
@login_required
def forumGame(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    return render_to_response('uploadGame/forumGame.html', {
        'collapse': get_collapse('/gg_mgmt/uploadGame/forumGame/'),
        'html': '/gg_mgmt/uploadGame/forumGame/',
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def addForumGame(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    os.system("python /home/mgmt/operation/step_08_copy_forum_pkg_info_to_service_db/08_0_1_main.py")
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='论坛游戏入库',goal='',action='游戏入库',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    response.write('uploadGame')
    return response

@csrf_exempt
@login_required
def forumPlugin(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    return render_to_response('uploadGame/forumPlugin.html', {
        'collapse': get_collapse('/gg_mgmt/uploadGame/forumPlugin/'),
        'html': '/gg_mgmt/uploadGame/forumPlugin/',
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def addForumPlugin(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    os.system("sh /home/mgmt/operation/cmd/cmd_sync_small_crack.sh")
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='论坛插件入库',goal='',action='插件入库',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = 'addForumPlugin'
    response.write(result)
    return response

@csrf_exempt
@login_required
def googlePlugin(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    return render_to_response('uploadGame/googlePlugin.html', {
        'collapse': get_collapse('/gg_mgmt/uploadGame/googlePlugin/'),
        'html': '/gg_mgmt/uploadGame/googlePlugin/',
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def addGooglePlugin(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    pkg_name = request.POST.get('pkg_name')
    ver_code = int(request.POST.get('ver_code'))
    #sys.path.append('/home/mgmt/operation/PostRobot/')
    #from PostRobotForPlugin import post_plugin
    #returns = post_plugin(False, pkg_name, ver_code)
    os.system('python /home/mgmt/operation/PostRobot/PostRobotForPlugin.py %s %s &' % (pkg_name, ver_code))
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='GooglePlay插件入库',goal='pkg_name:%s, ver_code:%s' % (pkg_name, str(ver_code)),action='插件入库',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '插件已入库！！！'
    response.write(result)
    return response

@csrf_exempt
@login_required
def release(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    releases = ReleaseList.objects.filter(is_finished=0)
    msg = '有正在进行的发布!!!' if releases else ''
    return render_to_response('release/release.html', {
        'collapse': get_collapse('/gg_mgmt/release/release/'),
        'html': '/gg_mgmt/release/release/',
        'perm_id': perm_id,
        'perm_name': perm_name,
        'msg': msg,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def releaseList(request):
    username = request.user
    user = User.objects.get(username=username)
    games = ReleaseList.objects.all().order_by('-start_date')
    count = len(games)
    errors = {}
    errors['101']='52上解压数据错误' 
    errors['102']='同步数据到52错误' 
    errors['103']='同步数据到52错误'
    errors['104']='同步数据到52错误'
    errors['105']='52上刷新缓存错误'
    errors['106']='发布成功'
    errors['201']='178刷新缓存错误'
    errors['202']='其他错误'
    number = 1
    for game in games:
        game.start_date = getDate(game.start_date)
        game.end_date = getDate(game.end_date)
        game.finished = getTimeStamp(game.end_date) - getTimeStamp(game.start_date) if game.end_date else time.time() - getTimeStamp(game.start_date)
        game.index = number 
        number += 1
        game.msg = errors[str(game.msg)] if str(game.msg) in errors else '其他错误'
        if int(game.is_finished) == 0:
            game.msg = '' 
    feedback, page_range, per_page = lbe_pagination(request, games)
    count_page = count / 25
    return render_to_response('release/releaseList.html', {
        'collapse': get_collapse('/gg_mgmt/release/releaseList/'),
        'html': '/gg_mgmt/release/releaseList/',
        'feedback': feedback,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page+1,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def releaseData(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game = ReleaseList(start_date=time.time(),is_finished=0)
    game.save()
    game = ReleaseList.objects.all().order_by('-id')[0]   
    result = os.system('python /home/mgmt/update_52_iplay_data/release.py %d &' % game.id)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='发布页',goal=game.id,action='发布',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = '成功生成发布列表ID:%d' % game.id
    response.write(result)
    return response

@csrf_exempt
@login_required
def check(request):
    os.system("python /opt/www/gg_mgmt/iplay_utils/check_data.py > /opt/www/gg_mgmt/iplay_utils/log")
    return render_to_response('release/check.html', {
        'collapse': get_collapse('/gg_mgmt/release/check/'),
        'html': '/gg_mgmt/release/check/'
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def plugin(request):
    username = request.user
    user = User.objects.get(username=username)
    games = GameResourceInfo.objects.all().order_by("-id")
    number = 1
    for game in games:
        game.index = number 
        number += 1
    infos, page_range, per_page = lbe_pagination(request, games)
    count = len(games)
    count_page = count / 25
    # print count, page_range, per_page
    return render_to_response('game/plugin.html', {
        'collapse': get_collapse('/gg_mgmt/game/plugin/'),
        'html': '/gg_mgmt/game/plugin/',
        'infos': infos,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page+1,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def plugin_detail(request):
    username = request.user
    user = User.objects.get(username=username)

    plugin_id = int(request.GET.get('plugin_id'))
    plugin = GameResourceInfo.objects.get(id=plugin_id)
    plugs = ResourceMatchCondition.objects.filter(resource_id=plugin_id)
    pkg_name = plugin.pkg_name
    plugins = GameResourceInfo.objects.filter(pkg_name=pkg_name)
    gamess = ResourceMatchResult.objects.filter(resource_id=plugin_id)
    games = []
    for game in gamess:
        game.game_id = GamePkgInfo.objects.get(apk_id=game.apk_id).game_id
        game.pkg_name = GamePkgInfo.objects.get(apk_id=game.apk_id).pkg_name
        game.signature_md5 = GamePkgInfo.objects.get(apk_id=game.apk_id).signature_md5
        game.ver_code = GamePkgInfo.objects.get(apk_id=game.apk_id).ver_code
        if GamePkgInfo.objects.get(apk_id=game.apk_id).is_max_version == 1:
            games.append(game)
    return render_to_response('game/plugin_detail.html', {
        'games': games,
        'plugins': plugins,
        'plugs': plugs,
        'plugin': plugin
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def plugin_search(request):
    username = request.user
    user = User.objects.get(username=username)

    plugin_info = request.GET.get('search_plugin_info')

    search_result = []
    if not search_result:
        try:
            search_result = GameResourceInfo.objects.filter(pkg_name__contains=plugin_info).order_by('id')
        except:
            search_result = []
    if not search_result:
        try:
            search_result = GameResourceInfo.objects.filter(tid=plugin_info).order_by('id')
        except:
            search_result = []
    if not search_result:
        try:
            search_result = GameResourceInfo.objects.filter(id=plugin_info).order_by('id')
        except:
            search_result = []

    number = 1
    games = []
    for plugin in search_result:
    #    game = GameLabelInfo.objects.get(game_id=game_id)
        plugin.index = number 
        games.append(plugin)
        number += 1
    feedback, page_range, per_page = lbe_pagination(request, games)
    count = len(games)
    count_page = count / 25
    # print count, page_range, per_page
    return render_to_response('game/plugin_search.html', {
        'plugin_info': plugin_info,
        'feedback': feedback,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page+1,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def search(request):
    username = request.user
    user = User.objects.get(username=username)
#    is_superuser = user.is_superuser

    search_game_name = request.GET.get('search_game_name')
    #games = GameLabelInfo.objects.filter(game_name__contains=search_game_name).order_by('-download_counts')[:20]
    search_shell = '/opt/lucence/bin/searchgames2.sh %s 20' % search_game_name
    try:
        search_result = json.loads(os.popen(search_shell).readlines()[0].strip())   
    except:
        search_result = []

    games = []
    number = 1
    for game_id in search_result:
        game = GameLabelInfo.objects.get(game_id=game_id)
        game.save_timestamp = getDate(game.save_timestamp)
        game.index = number 
        games.append(game)
        number += 1
    feedback, page_range, per_page = lbe_pagination(request, games)
    count = len(games)
    count_page = count / 25
    for g in feedback:
        try:
            g.color_label = g.color_label.split('\n')
        except:
            g.color_label = []
    # print count, page_range, per_page
    return render_to_response('game/search.html', {
        'feedback': feedback,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page+1,
        'COLOR_LABELS': COLOR_LABELS,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def addScreen(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_id = request.POST.get('game_id')
    screen_shot_url = request.POST.get('screen_shot_url')
    info = GameLabelInfo.objects.get(game_id=game_id)
    screen_shot_urls = '%s\n%s' % (info.screen_shot_urls, screen_shot_url)
    info = GameLabelInfo.objects.filter(game_id=game_id).update(screen_shot_urls=screen_shot_urls)
    username = request.user
    user = User.objects.get(username=username)
    game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='游戏详情',goal='游戏id: %s' % str(game_id),action='新增截图',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
    game_operation.save()
    result = 'yes'
    response.write(result)
    return response

@csrf_exempt
@login_required
def detail(request):
    username = request.user
    user = User.objects.get(username=username)
    perm_id, perm_name = get_perm(user.id)
    game_id = request.GET.get('game_id')
    apk_id = request.GET.get('apk_id')
    channels = []
    plugin_channels = []
    info = GameLabelInfo.objects.get(game_id=game_id)
    pkgs = GamePkgInfo.objects.filter(game_id=game_id,is_max_version=1)
    for pkg in pkgs:
        if pkg.is_plugin_required == 1:
            plugin_channels.append({'apk_id': pkg.apk_id, 'channel': pkg.market_channel})
            try:
                pkg.required_plugin_ids = pkg.required_plugin_ids.split('\n')
            except:
                pass
        else:
            channels.append({'apk_id': pkg.apk_id, 'channel': pkg.market_channel})
    if apk_id:
        pkg = GamePkgInfo.objects.get(apk_id=apk_id)
        if pkg.is_plugin_required == 1:
            try:
                pkg.required_plugin_ids = pkg.required_plugin_ids.split('\n')
            except:
                pass
    else:
        try:
            pkg = pkgs[0]
            if pkg.is_plugin_required == 1:
                try:
                    pkg.required_plugin_ids = pkg.required_plugin_ids.split('\n')
                except:
                    pass
        except:
            pkg = {}
    #channels = list(set(channels))
    #plugin_channels = list(set(plugin_channels))
    color_labels = info.color_label.strip().split('\n') if info.color_label else []
    info.filter_pkg_names = info.filter_pkg_names.strip().split('\n') if info.filter_pkg_names else []
    #screen_shot_urls = info.screen_shot_urls.replace('http://ggfile.qiniudn.com/', '').strip().split('\n') if info.screen_shot_urls else []
    screen_shot_urls = []
    if info.screen_shot_urls:
        num = 1
        for screen_shot_url in info.screen_shot_urls.strip().split('\n'):
            a = {}
            a['url'] = screen_shot_url
            a['num'] = num
            num += 1
            screen_shot_urls.append(a)
    info.origin_types = info.origin_types if info.origin_types else ''
    info.origin_type_list = info.origin_types.split('\n') if info.origin_types else []
    info.subscript_expire_time = getDate(info.subscript_expire_time).split(' ')[0]
    if info.enabled == 0 and info.is_in_test == 0:
        info.status = 1
    if info.enabled == 1 and info.is_in_test == 1:
        info.status = 2
    if info.enabled == 1 and info.is_in_test == 0:
        info.status = 3
    dev_names = GameDeveloper.objects.all()
    models = NotPlayModel.objects.filter(gameid=game_id)
    fingerprints = NotPlayFingerprint.objects.filter(gameid=game_id)
    if not info.detail_desc_html:
        info.detail_desc_html = """
<html>
<head>
</head>
<body style="margin:0;padding:0">
<style>
p {
    margin-bottom: 8px;
    padding: 0;
    line-height: 18px;
}
hr {
    height: 0px;
    border-top: 1px solid #EAEAEA;
    border-right: 0px;
    border-bottom: 0px;
    border-left: 0px;
}
.color {
    color: rgb(255, 103, 29);
    font-size:14px;
}
.color img{
    width: 100%;
}
.size {
    font-size:14px;
}
</style>
<hr>
<p><span style="color:#FF0000"><strong><img alt="" src="http://7mnn9f.com1.z0.glb.clouddn.com/pojieshuoming.png" style="height:14px; width:2px" /></strong></span><span style="color:#444444"><strong>&nbsp;</strong> 破解说明</span></p>
<p class="color"><span style="font-size:14px"><span style="color:rgb(255, 103, 29)">独家破解安卓系统限制，4.2版本也可以玩</span></p>

<p class="size"><span style="font-size:14px">优点：游戏非常具有创造力，画面唯美音乐平缓舒适，在音乐中解开谜题绝对是一种享受。
一句话点评：《纪念碑谷》已经不仅仅是一款好玩的游戏，更像是一件精妙绝伦的艺术品，创新的设计，内涵而又有哲理的对话和故事交待，视觉欺骗对整体环境的影响，各种奇妙的设计与优秀的操作感令人印象深刻。</span></p>
<hr>
<p><span style="color:#FF0000"><strong><img alt="" src="http://7mnn9f.com1.z0.glb.clouddn.com/ceshijixing.png" style="height:14px; width:2px" /></strong></span><span style="color:#444444"><strong>&nbsp; </strong>实测机型</span></p>
<p class="color"><span style="font-size:14px"><span style="color:rgb(255, 103, 29)">独家破解安卓系统限制，4.2版本也可以玩</span></p>
<p class="size"><span style="font-size:14px">优点：游戏非常具有创造力，画面唯美音乐平缓舒适，在音乐中解开谜题绝对是一种享受。一句话点评：《纪念碑谷》已经不仅仅是一款好玩的游戏，更像是一件精妙绝伦的艺术品，创新的设计，>内涵而又有哲理的对话和故事交待，视觉欺骗对整体环境的影响，各种奇妙的设计与优秀的操作感令人印象深刻。</span></p>
<hr>
<p><span style="color:#FF0000"><strong><img alt="" src="http://7mnn9f.com1.z0.glb.clouddn.com/yingyongmiaoshu.png" style="height:14px; width:2px" /></strong></span><span style="color:#444444"><strong>&nbsp; </strong>应用描述</span></p>
<p class="color"><span style="font-size:14px"><span style="color:rgb(255, 103, 29)">独家破解安卓系统限制，4.2版本也可以玩</span></p>
<p class="size"><span style="font-size:14px">优点：游戏非常具有创造力，画面唯美音乐平缓舒适，在音乐中解开谜题绝对是一种享受。一句话点评：《纪念碑谷》已经不仅仅是一款好玩的游戏，更像是一件精妙绝伦的艺术品，创新的设计，>内涵而又有哲理的对话和故事交待，视觉欺骗对整体环境的影响，各种奇妙的设计与优秀的操作感令人印象深刻。</span></p>
</body>
</html>
    """
    return render_to_response('game/detail.html', {
        'info': info,
        'color_labels': color_labels,
        'screen_shot_urls': screen_shot_urls,
        'channels': channels,
        'plugin_channels': plugin_channels,
        'user': user,
        'pkg': pkg,
        'models': models,
        'fingerprints': fingerprints,
        'dev_names': dev_names,
        'perm_id': perm_id,
        'perm_name': perm_name,
        'user': user
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def index(request):
    username = request.user
    user = User.objects.get(username=username)
    source = request.GET.get('source_id') if 'source_id' in request.GET  else 3
    status = int(request.GET.get('status')) if 'status' in request.GET else 3
    sort_key = request.GET.get('sort_key') if 'sort_key' in request.GET else 'save_timestamp'
    if status == 1:
        enabled = 0
        is_in_test = 0
    if status == 2:
        enabled = 1
        is_in_test = 1
    if status == 3:    
        enabled = 1
        is_in_test = 0
    if 1==1:
        if int(source) == 1:
            games = set()
            pkgs = GamePkgInfo.objects.filter(is_plugin_required=1, source=source)
            for pkg in pkgs:
                try:
                    game_id = pkg.game_id
                    game = GameLabelInfo.objects.get(game_id=game_id, source=source, enabled=enabled, is_in_test=is_in_test)
                    games.add(game)
                except:
                    pass
            games = list(games)
        elif int(source) == 0:
            games = set()
            pkgs = GamePkgInfo.objects.filter(is_plugin_required=1, source=1)
            for pkg in pkgs:
                try:
                    game_id = pkg.game_id
                    game = GameLabelInfo.objects.get(game_id=game_id, source=1, enabled=enabled, is_in_test=is_in_test)
                    games.add(game)
                except:
                    pass
            games = list(games)
            games += list(GameLabelInfo.objects.filter(enabled=enabled, source=2, is_in_test=is_in_test).order_by('-download_counts'))
            games += list(GameLabelInfo.objects.filter(enabled=enabled, source=3, is_in_test=is_in_test).order_by('-download_counts'))
            games += list(GameLabelInfo.objects.filter(enabled=enabled, source=4, is_in_test=is_in_test).order_by('-download_counts'))
        else:
            games = GameLabelInfo.objects.filter(source=source, enabled=enabled, is_in_test=is_in_test).order_by('-download_counts')
    count = len(games)
    number = 1
    sort_data = {}
    sort_keys = {}
    for game in games:
        game.index = number 
        game.gg_download_cnt = game.gg_download_cnt if game.gg_download_cnt else 0
        game.gg_download_week = game.gg_download_week if game.gg_download_week else 0
        game.subscript = game.subscript if game.subscript else 0
        number += 1
        sort_data[str(game.game_id)] = game
        sort_keys[str(game.game_id)] = {'save_timestamp': game.save_timestamp, 'gg_download_cnt': game.gg_download_cnt, 'gg_download_week': game.gg_download_week, 'subscript': game.subscript}
        game.save_timestamp = getDate(game.save_timestamp)
    sorted_data = get_sorted(sort_data, sort_keys, sort_key) if sort_key else games
    infos, page_range, per_page = lbe_pagination(request, sorted_data)
    count_page = count / 25
    for g in infos:
        try:
            g.color_label = g.color_label.split('\n')
        except Exception as e:
            g.color_label = []
    return render_to_response('game/show.html', {
        'collapse': get_collapse('/gg_mgmt/game/'),
        'html': '/gg_mgmt/game/',
        'infos': infos,
        'page_range': page_range,
        'per_page': per_page,
        'count': count,
        'count_page': count_page+1,
        'user': user,
        'status': status,
        'sort_key': sort_key,
        'source': int(source),
        'COLOR_LABELS': COLOR_LABELS
    }, context_instance=RequestContext(request))


def label_info(request):
    error = ""
    info = ""
    if request.method == "POST" and request.is_ajax():
    # if True:
        g_id = request.POST.get('g_id')
        try:
            info = GameLabelInfo.objects.filter(game_id=g_id)
        except GameLabelInfo.DoesNotExist:
            error = "不存在"
    else:
        error = "请求错误"

    return json_return(request, error, info)


def channel(request):

    error = ""
    channels = []

    if request.method == "POST" and request.is_ajax():
    # if True:
        g_id = request.POST.get('g_id')
        # g_id = request.GET.get('id')
        # print g_id
        try:
            pkgs = GamePkgInfo.objects.filter(game_id=g_id)
            for pkg in pkgs:
                channels.append(pkg.market_channel)
            channels = list(set(channels))
        except GamePkgInfo.DoesNotExist:
            error = "不存在"
    else:
        error = "请求错误"

    return json_return(request, error, channels)


def game_info(request):

    error = ""
    # g_info = {}
    infos = ""

    if request.method == "POST" and request.is_ajax():
        g_id = request.POST.get('g_id')
        apk_id = request.POST.get('apk_id')
        try:
            if g_id and apk_id:
                infos = GamePkgInfo.objects.filter(
                    game_id=g_id,
                    enabled=1,
                    apk_id=apk_id
                )
                #for info in infos:
                #    info.required_plugin_ids = info.required_plugin_ids.split('\n') if info.required_plugin_ids else []
        except GamePkgInfo.DoesNotExist:
            error = "不存在"
    else:
        error = "请求错误"

    return json_return(request, error, infos)


def label_info_change(request):
    head = """
    <html>
	<head>
	</head>
	<body style="margin:0;padding:0">
	<style>
	p {
	    margin-bottom: 8px;
	    padding: 0;
	    line-height: 18px;
	}
	hr {
	    height: 0px;
	    border-top: 1px solid #EAEAEA;
	    border-right: 0px;
	    border-bottom: 0px;
	    border-left: 0px;
	}
        .color {
            color: rgb(255, 103, 29);
            font-size: 14px;
        }
        .color img{
            width: 100%;
        }
        .size {
            font-size:14px;
        }
	</style>
    """
    foot = """
    </body>
    </html>
    """

    error = ""
    info = ""
    username = request.user
    user = User.objects.get(username=username)

    if request.method == "POST" and request.is_ajax():
        game_id = request.POST.get('game_id')
        display_name = request.POST.get('display_name')
        subscript = request.POST.get('subscript')
        save_detail_desc_html = request.POST.get('save_detail_desc_html')
        status = request.POST.get('status')
        if status == '1':#未发布
            enabled = 0
            is_in_test = 0
        if status == '2':#内测
            enabled = 1
            is_in_test = 1
        if status == '3':#已发布
            enabled = 1
            is_in_test = 0
        disable_reason = request.POST.get('disable_reason')
        color_label = request.POST.get('color_label')
        download_num = request.POST.get('download_num') or 0
        game_language = request.POST.get('language')
        star_num = request.POST.get('star') or 0
        icon_urls = request.POST.get('icon')
        screen_shot_urls = request.POST.get('screen')
        short_desc = request.POST.get('short_desc')
        detail_desc = request.POST.get('desc')
        label_type = request.POST.get('types')
        label_category = request.POST.get('categorys')
        dev_name = request.POST.get('dev_name')
        detail_url = request.POST.get('detail_url')
        editor_desc_html = request.POST.get('editor_desc_html')
        detail_desc_html = request.POST.get('detail_desc_html')
        banner_pic = request.POST.get('banner_pic')
        filter_pkg_names = request.POST.get('filter_pkg_names')
        show_hot_icon = request.POST.get('show_hot_icon')
        if detail_desc_html == '<p><br></p>':
            detail_desc_html = ''
        if editor_desc_html == '<p><br></p>':
            editor_desc_html = ''
        if not detail_desc:
            detail_desc = dehtml(detail_desc_html)
        subscript_expire_time = request.POST.get('subscript_expire_time')
        types = set()
        for type in label_type.split('\n'):
            types.add(type)
        for type in label_category.split('\n'):
            types.add(type)
        origin_types = '\n'.join(list(types))
        game_alias = request.POST.get('game_alias')
        try:
            if game_id:
                if display_name and display_name != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(display_name=display_name)
                if download_num and download_num != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(download_counts=download_num)
                if subscript and subscript != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(subscript=subscript)
                if subscript and subscript != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(subscript=subscript)
                game = GameLabelInfo.objects.get(game_id=game_id)
                last_enabled = game.enabled
                last_is_in_test = game.is_in_test
                if enabled == 1 and is_in_test == 0 and last_enabled == 1 and last_is_in_test == 1:
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(update_timestamp=int(time.time()), save_timestamp=int(time.time()))
                if enabled == 1 and is_in_test == 0 and last_enabled == 0 and last_is_in_test == 0:
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(update_timestamp=int(time.time()), save_timestamp=int(time.time()))
                info = GameLabelInfo.objects.filter(game_id=game_id).update(enabled=enabled)
                info = GameLabelInfo.objects.filter(game_id=game_id).update(is_in_test=is_in_test)
                info = GameLabelInfo.objects.filter(game_id=game_id).update(disable_reason=disable_reason)
                info = GameLabelInfo.objects.filter(game_id=game_id).update(color_label=color_label)
                info = GameLabelInfo.objects.filter(game_id=game_id).update(origin_types=origin_types)
                info = GameLabelInfo.objects.filter(game_id=game_id).update(game_alias=game_alias)
                info = GameLabelInfo.objects.filter(game_id=game_id).update(update_timestamp=int(time.time()))
                info = GameLabelInfo.objects.filter(game_id=game_id).update(detail_url=detail_url)
                if show_hot_icon:
                    GameLabelInfo.objects.filter(game_id=game_id).update(show_hot_icon=show_hot_icon)
                GameLabelInfo.objects.filter(game_id=game_id).update(filter_pkg_names=filter_pkg_names)
                GameLabelInfo.objects.filter(game_id=game_id).update(banner_pic=banner_pic)
                if editor_desc_html:
                    editor_desc_html = head + editor_desc_html + foot
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(editor_desc_html=editor_desc_html)
                if save_detail_desc_html == '1' and detail_desc_html:
                    detail_desc_html = head + detail_desc_html + foot
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(detail_desc_html=detail_desc_html)
                if screen_shot_urls and screen_shot_urls != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(screen_shot_urls=screen_shot_urls)
                if icon_urls and icon_urls != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(icon_url=icon_urls)
                if short_desc and short_desc != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(short_desc=short_desc)
                if detail_desc and detail_desc != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(detail_desc=detail_desc)
                if star_num and star_num != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(star_num=star_num)
                if game_language and game_language != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(game_language=game_language)
                if dev_name and dev_name != 'None':
                    info = GameLabelInfo.objects.filter(game_id=game_id).update(developer=dev_name)
                subscript_expire_time = getTimeStamp('%s 00:00:00' % subscript_expire_time) if subscript_expire_time and subscript_expire_time != 'None' else 0
                info = GameLabelInfo.objects.filter(game_id=game_id).update(subscript_expire_time=subscript_expire_time)
   # os.system('python /home/mgmt/operation_auto_upload_apk/upload_data.py 3 %d %s &' % (game.id, user.last_name+user.first_name))
                info = GameLabelInfo.objects.filter(game_id=game_id).update(is_changed=True,update_user=user.last_name+user.first_name)
                username = request.user
                user = User.objects.get(username=username)
                game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='游戏详情',goal='游戏id: %s' % str(game_id),action='修改label信息',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
                game_operation.save()
              #  info = GameLabelInfo.objects.filter(game_id=game_id).update(
              #      display_name=display_name,
              #      download_counts=download_num,
              #      subscript=subscript,
              #      color_label=color_label,
              #      screen_shot_urls=screen_shot_urls,
              #      icon_url=icon_urls,
              #      short_desc=short_desc,
              #      detail_desc=detail_desc,
              #      star_num=star_num,
              #      game_language=game_language,
              #      is_changed=True
              #  )
                # print info
        except GameLabelInfo.DoesNotExist:
            error = "不存在"
    else:
        error = "请求错误"
   

    return json_return(request, error, info)


def pkg_info_change(request):

    error = ""
    info = ""

    if request.method == "POST" and request.is_ajax():
        dl_button_txt = request.POST.get('dl_button_txt')
        dl_button_color = request.POST.get('dl_button_color')
        gles_version = request.POST.get('gles_version')
        apk_id = request.POST.get('apk_id')
        enabled = request.POST.get('enabled')
        disable_reason = request.POST.get('disable_reason')

        try:
            if apk_id:
                # print info
                info = GamePkgInfo.objects.filter(apk_id=apk_id).update(enabled=enabled)
                info = GamePkgInfo.objects.filter(apk_id=apk_id).update(disable_reason=disable_reason)
                info = GamePkgInfo.objects.filter(apk_id=apk_id).update(is_changed=True)
                info = GamePkgInfo.objects.filter(apk_id=apk_id).update(dl_button_txt=dl_button_txt)
                info = GamePkgInfo.objects.filter(apk_id=apk_id).update(dl_button_color=dl_button_color)
                if gles_version:
                    info = GamePkgInfo.objects.filter(apk_id=apk_id).update(gles_version=gles_version)
                username = request.user
                user = User.objects.get(username=username)
                game_operation = GameOperation(user_id=user.id,user_name=user.last_name+user.first_name,page='游戏详情',goal='apk_id: %s' % str(apk_id),action='修改apk信息',operation_time=time.time(),operation_date=getDate(time.time()).split(' ')[0]) 
                game_operation.save()
        except GamePkgInfo.DoesNotExist:
            error = "不存在"
    else:
        error = "请求错误"

    return json_return(request, error, info)


def json_return(request, error, msg):
    """
    json返回，400为错误，200为成功
    :param request:
    :param error: 错误信息
    """

    if error:
        json_dict = {
            'status': 400,
            'error': error,
        }
        json = dumps(json_dict, cls=DjangoJSONEncoder)
    else:
        json_dict = {
            'status': 200,
            'success': '成功',
            'msg': msg
        }
        json = dumps(json_dict, cls=DjangoJSONEncoder)
    # print json
    return HttpResponse(json)


def lbe_pagination(request, queryset, after_range_num=5, before_range_num=4):
    """
    分页方法
    :param request:
    :param queryset:
    :param after_range_num:
    :param before_range_num:
    :return:
    """

    try:
        #得到request中的page参数
        per_page = int(request.GET.get('pr'))  # 每页记录数
    except:
        per_page = 25  # 默认为10

    per_page = 25
    #按参数分页
    paginator = Paginator(queryset, per_page)

    try:
        page_num = int(request.GET.get('pn'))  # 页码
    except:
        page_num = 1  # 默认为1

    try:
        objects = paginator.page(page_num)  # 尝试获得分页列表
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)  # 如果页数不存在，获得最后一页
    except PageNotAnInteger:
        objects = paginator.page(1)  # 如果不是一个整数，获得第一页

    #根据参数配置导航显示范围
    if page_num >= after_range_num:
        page_range = paginator.page_range[page_num - after_range_num: page_num + before_range_num]
    else:
        page_range = paginator.page_range[0: page_num + before_range_num]

    return objects, page_range, per_page


"""
SELECT pkg.id, pkg.pkg_name, pkg.version, pkg.game_basic_info_id, pkg.channel, pkg.url1, pkg.language, pkg.install_num, pkg.size, basic_many.*
FROM game_pkg_info pkg
LEFT JOIN game_basic_info_many basic_many
ON pkg.game_basic_info_id = basic_many.game_basic_info_id
AND pkg.channel = basic_many.channel
WHERE pkg.game_basic_info_id = 1
AND pkg.channel = '百度'
;
"""
