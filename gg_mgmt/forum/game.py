__author__ = 'xiangxiaowei'


import os
import json
import time
import logging
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

from forum.models import *


log = logging.getLogger('error')


@csrf_exempt
@login_required
def game_info(request):
    username = request.user
    user = User.objects.get(username=username)
    editor = IplayEditorInfo.objects.get(name=user.last_name+user.first_name)
    infos = IplayGameLabelInfo.objects.filter(source=3)
    return render_to_response('game_info.html', {
        'infos': infos,
        'user': editor,
        'editor': editor,
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def upload_game_info(request):
    username = request.user
    user = User.objects.get(username=username)
    editor = IplayEditorInfo.objects.get(name=user.last_name+user.first_name)
    infos = IplayUploadGame.objects.all().order_by('-id')
    return render_to_response('upload_game_info.html', {
        'infos': infos,
        'editor': editor,
        }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def upload_game(request):
    username = request.user
    user = User.objects.get(username=username)
    response=HttpResponse()
    response['Content-Type'] = 'text/string'
    '''
    target_pkg_name = request.POST.get('target_pkg_name')
    target_ver_code = request.POST.get('target_ver_code')
    ids = IplayUploadPlugin.objects.filter(is_finished=0, target_pkg_name=target_pkg_name, target_ver_code=target_ver_code)
    if ids:
        msg = 'error'
    else:
        IplayUploadPlugin(target_pkg_name=target_pkg_name, target_ver_code=target_ver_code, is_finished=0,
                          editor=user.last_name+user.first_name, save_timestamp=int(time.time())).save()
        plugin = IplayUploadPlugin.objects.filter(target_pkg_name=target_pkg_name, target_ver_code=target_ver_code).order_by('-id')[0]
        log.debug(plugin.id)
        os.system('python /home/mgmt/operation_shell/PostRobot/PostRobotForPlugin.py %s &' % plugin.id)
        log.debug('python /home/mgmt/operation_shell/PostRobot/PostRobotForPlugin.py %s &' % plugin.id)
        msg = 'success'
    '''
    response.write(msg)
    return response