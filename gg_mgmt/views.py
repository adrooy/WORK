#!/usr/bin/python
#-*- coding:utf-8 -*-


__author__ = 'xiangxiaowei'


from django.http import HttpResponsePermanentRedirect, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db.models import Q
from django.db import connections, transaction
from forum.models import ArticleInfo, ArticleTemplateInfo, ArticleVariInfo, GameForecast, GameCategory, GameLabel, ForecastToLabel, ArticleVari, ArticleTemplate
from game.models import GamePkgInfo
#from utils import get_pagination, get_game_info, get_date, get_download_cnt, get_apk_size, get_vari_value
from utils import *
import MySQLdb
import random
import json
import re
import logging


log = logging.getLogger('error')

 
TYPE = [
    ['5', '机型相关问题'],
    ['6', '游戏数据包下载相关问题'],
    ['7', '游戏贴图错误的解决方法'],
    ['8', '游戏安装方法'],
    ['9', '黑屏的解决方法'], 
    ['10', 'GG助手修改教程'], 
    ['201', '版本'],
    ['202', '平台'], 
    ['203', '下载'],
    ['204', '问题'],
    ['205', '修改器'],
    ['206', '修改内容']
]
VARI_TYPE = {
    1: '破解信息',
    2: '适用平台',
    3: '下载方式',
    4: '问题',
    5: '修改手段',
    6: '修改内容',
    7: '手机型号',
    8: '游戏名'
}
TEMPLATE_TYPE = {
    1: '下载类',
    2: '安装类',
    3: '解决方法类',
    4: '教程类',
    5: '机型相关'
}


@csrf_exempt
def game_predict_info(request):
    game_status = int(request.GET.get('status')) if 'status' in request.GET else 1
    games = GameForecast.objects.filter(game_status=game_status)
    categorys = GameCategory.objects.filter(parent_id=0)
    for category in categorys:
        category.id = str(category.id)
    number = 0 
    for game in games:
        number += 1
        game.number = number
        game.category_ids = game.category_ids.split(',')
        game.save_timestamp = get_date(game.save_timestamp)
    infos, page_range, per_page, count_page = get_pagination(request, games, 8) 
    return render_to_response('game/game_predict_info.html', {
        'categorys': categorys,
        'infos': infos,
        'count': len(games),
        'page_range': page_range,
        'count_page': count_page,
        'status': game_status
    }, context_instance=RequestContext(request))


@csrf_exempt
def add_game_predict(request):
    cursor_m = connections['forum'].cursor()
    cursor_m.execute("SELECT * FROM `iplay_forecast_to_label_result`")
    game_ids = set()
    for row in cursor_m.fetchall():
        game_id = row[1]
        game_ids.add(game_id)
    categorys = GameCategory.objects.filter(parent_id=0)
    for category in categorys:
        category.id = str(category.id)
    try:
        game_id = request.GET.get('game_id')
        info = GameForecast.objects.get(game_id=game_id)
        if game_id in game_ids:
            label = ForecastToLabel.objects.get(game_id=game_id)
            label_id = label.label_id
            info.label_id = label_id
            label_name = get_info('game_name', 'iplay_game_label_info', 'game_id', label_id)
            info.label_name = label_name
        screen_shot_urls = []
        info.category_ids = info.category_ids.split(',')
        if info.screen_shot_urls:
            num = 1
            for screen_shot_url in info.screen_shot_urls.strip().split('\n'):
                a = {}
                a['url'] = screen_shot_url
                a['num'] = num
                num += 1
                screen_shot_urls.append(a)
    except:
        screen_shot_urls = []
        info = {}
    return render_to_response('game/add_game_predict.html', {
        'categorys': categorys,
        'screen_shot_urls': screen_shot_urls,
        'info': info
    }, context_instance=RequestContext(request))


@csrf_exempt
def save_game_predict(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    head = """
    <html>
	<head>
	</head>
	<body style='margin:0;padding:0'>
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
	</style>
    """
    foot = """
    </body>
    </html>
    """
    game_id = request.POST.get('game_id', '')
    display_name = request.POST.get('display_name', '')
    game_status = request.POST.get('game_status', '')
    game_language = request.POST.get('game_language', '')
    icon_url = request.POST.get('icon_url', '')
    screen_shot_urls = request.POST.get('screen_shot_urls', '')
    short_desc = request.POST.get('short_desc', '')
    detail_desc = request.POST.get('detail_desc', '')
    developer = request.POST.get('developer', '')
    predict_time = request.POST.get('predict_time', '')
    category_ids = request.POST.get('category_ids', '')
    banner_url = request.POST.get('banner_url', '')
    label_id = request.POST.get('label_id') if 'label_id' in request.POST else ''
    detail_desc_html = request.POST.get('detail_desc_html', '').replace('"', "'")
    log.debug('START');
    if detail_desc_html == '<p><br></p>':
        detail_desc_html = ''
    else:
        detail_desc_html = head + detail_desc_html + foot
    if not detail_desc:
        detail_desc = dehtml(detail_desc_html)
    cursor_m = connections['forum'].cursor()
    if game_id:
        sql = """ 
        UPDATE iplay_game_forecast_info SET display_name="%s", game_status="%s", game_language="%s", icon_url="%s", screen_shot_urls="%s", short_desc="%s", detail_desc="%s", developer="%s", predict_time="%s", category_ids="%s", banner_url="%s", update_timestamp="%s", detail_desc_html="%s" WHERE game_id="%s"
        """
        sql = sql % (display_name,game_status, game_language,icon_url, screen_shot_urls,short_desc, detail_desc,developer, predict_time, category_ids,banner_url, int(time.time()), detail_desc_html, game_id)
        log.debug(sql)
        cursor_m.execute(sql)
        if label_id:
            cursor_m.execute("SELECT * FROM iplay_game_forecast_info WHERE game_id='%s'" % game_id)
            for row in cursor_m.fetchall():
                game_tid = row[8]
                game_post_url = row[7]
            label = GameLabel.objects.get(game_id=label_id)
            label_tid = label.tid
            label_post_url = label.post_url
            Game = GameLabel.objects.filter(game_id=label_id).update(tid=game_tid, post_url=game_post_url, update_timestamp=int(time.time()))
            forecast_to_label = ForecastToLabel(game_id=game_id, label_id=label_id)
            forecast_to_label.save()
            sql = """
                UPDATE iplay_game_forecast_info SET tid='%s', post_url='%s' WHERE game_id='%s'
            """
            sql = sql % (label_tid, label_post_url, game_id)
            cursor_m.execute(sql)
        transaction.commit_unless_managed(using='forum')
    else:
        cursor_m.execute("SELECT * FROM `iplay_game_forecast_info`")
        number = len(cursor_m.fetchall())
        game_id = 'yg%s' % (str(number+1).zfill(6))
        sql = """ 
        INSERT INTO iplay_game_forecast_info(game_id, display_name, game_status, game_language, icon_url, screen_shot_urls, short_desc, detail_desc, developer, predict_time, category_ids, banner_url, save_timestamp, tid, wanted_counts, update_timestamp, wanted_counts_random, forum_url, post_url, detail_desc_html) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "0", "0", "%s", "%s", "", "", "%s");
        """
        wanted_counts_random = random.randint(1, 22)
        sql = sql % (game_id, display_name,game_status, game_language,icon_url, screen_shot_urls,short_desc, detail_desc,developer, predict_time, category_ids,banner_url, int(time.time()), int(time.time()), wanted_counts_random, detail_desc_html)
        cursor_m.execute(sql)
    response.write('%s' % str(sql))
    return response


@csrf_exempt
def search_game_predict(request):
    categorys = GameCategory.objects.filter(parent_id=0)
    for category in categorys:
        category.id = str(category.id)
    predict_info = request.GET.get('search_predict_info')
    try:
        games = GameForecast.objects.filter(display_name__contains=predict_info)
    except:
        try:
            games = GameForecast.objects.filter(predict_time__contains=predict_info)
        except:
            games = []
    number = 1
    for game in games:
        number += 1
        game.number = number
        game.category_ids = game.category_ids.split(',')
    infos, page_range, per_page, count_page = get_pagination(request, games, 25) 
    return render_to_response('game/game_predict_search.html', {
        'categorys': categorys,
        'infos': infos,
        'page_range': page_range,
        'count_page': count_page
    }, context_instance=RequestContext(request))


@csrf_exempt
def article_info(request):
    articles = ArticleInfo.objects.filter(parent_id=0).order_by('-article_id')
    count = len(articles)
    infos, page_range, per_page, count_page = get_pagination(request, articles, 25) 
    return render_to_response('market/article_info.html', {
        "infos": infos,
        'page_range': page_range,
        'count_page': count_page,
        "count": count
    }, context_instance=RequestContext(request))


@csrf_exempt
def article(request):
    parent_id = request.GET.get('parent_id')
    info = ArticleInfo.objects.get(article_id=parent_id)
    infos = ArticleInfo.objects.filter(parent_id=parent_id)
    return render_to_response('market/article.html', {
        'info': info,
        'infos': infos
    }, context_instance=RequestContext(request))


@csrf_exempt
def add_article(request):
    '''
    #模板类型的选择
    if 'article_type' in request.GET:
        article_type = int(request.GET.get('article_type'))
        if 'template_type' in request.GET:
            template_type = int(request.GET.get('template_type'))
        else:
            template_type = 0
        if 'template_id' in request.GET:
            template_id = int(request.GET.get('template_id'))
        else:
            template_id = 0
        author = request.GET.get('author') 
        source = request.GET.get('source')
        save_timestamp = request.GET.get('save_timestamp')
        article_status = request.GET.get('article_status')
        template_types = ArticleTemplate.objects.all()
        return render_to_response('market/add_article.html', {
            'template_types': template_types,
            'templates': templates,
            'article_type': article_type,
            'template_type': template_type,
            'template_id': template_id,
            'vari_list': vari_list,
            'content_list': content_list,
            'vari_infos': vari_infos,
            'info': info,
            'jsons': json.dumps(jsons)
        }, context_instance=RequestContext(request))
    '''
    article_id = request.GET.get('article_id')
    parent_id = request.GET.get('parent_id')
    if parent_id:
        info = ArticleInfo.objects.get(article_id=parent_id)
        info.save_timestamp = ''
        info.parent_id = info.article_id
        info.article_id = ''
        info.game_id = ''
        info.content = ''
        info.title = ''
        info.short_title = ''
        jsons = {
        'vari_list': '',
        'content_list': ''
        }
        return render_to_response('market/add_article.html', {
            'info': info,
            'jsons': json.dumps(jsons),
        }, context_instance=RequestContext(request))
    article_type = int(request.GET.get('article_type')) if 'article_type' in request.GET else 1
    template_id = 0
    template_types = []
    templates = []
    cursor_m = connections['forum'].cursor()
    cursor_m.execute("SELECT * FROM `iplay_article_template_info`")
    for row in cursor_m.fetchall():
        tem_id = int(row[0])
        title = row[1]
        content = row[2]
        tem_type = int(row[3])
        if [tem_type, TEMPLATE_TYPE[tem_type]] not in template_types:
            template_types.append([tem_type, TEMPLATE_TYPE[tem_type]])
        if 'template_type' in request.GET:
            template_type = int(request.GET.get('template_type'))
        else:
            template_type = tem_type
        if 'template_id' in request.GET:
            template_id = int(request.GET.get('template_id'))
        else:
            if tem_type == template_type:
                template_id = tem_id
        templates.append([tem_id, title, content, tem_type])
    if article_id:
        info = ArticleInfo.objects.get(article_id=article_id)
        info.save_timestamp = get_date(info.save_timestamp)
        template_id = info.template_id
        article_type = info.article_type
        game_id = info.game_id
        download_url = GamePkgInfo.objects.get(game_id=game_id, is_max_version=1).download_url
        info.download_url = download_url
        if article_type != 1:
            jsons = {}
            return render_to_response('market/add_article.html', {
                'article_type': article_type,
                'info': info,
                'jsons': json.dumps(jsons),
            }, context_instance=RequestContext(request))
    else:
        info = {}
    if template_id:
        content = ArticleTemplateInfo.objects.get(template_id=template_id).content
        title = ArticleTemplateInfo.objects.get(template_id=template_id).title
        search_mid = r'\[\[(.*?)\]\]'
        vari_list = []
        if re.search(search_mid, title):
            for cont in re.findall(search_mid, title):
                cont_id = get_info('id', 'iplay_article_vari', 'name', cont)
                info = {
                    'vari_id': cont_id,
                    'vari_name': cont
                }
                if info not in vari_list:
                    vari_list.append(info)
        content_list = []
        if re.search(search_mid, content):
            for cont in re.findall(search_mid, content):
                cont_id = get_info('id', 'iplay_article_vari', 'name', cont)
                info = {
                    'vari_id': cont_id,
                    'vari_name': cont
                }
                if info not in content_list:
                    content_list.append(info)
        vari_infos = ArticleVariInfo.objects.all()
        for vari_info in vari_infos:
            vari_info.vari_name = get_info('name', 'iplay_article_vari', 'id', vari_info.vari_id)
        jsons = {
        'content_list': content_list,
        'vari_list': vari_list
        }
    if article_id:
        info = ArticleInfo.objects.get(article_id=article_id)
        info.save_timestamp = get_date(info.save_timestamp)
        template_id = info.template_id
        template_type = ArticleTemplateInfo.objects.get(template_id=template_id).template_type
        game_id = info.game_id
        download_url = GamePkgInfo.objects.get(game_id=game_id, is_max_version=1).download_url
        info.download_url = download_url
    else:
        info = {}
    infos = GameLabel.objects.filter(display_name__contains="狂野飙车8")
    desc = ArticleTemplateInfo.objects.get(template_id=template_id).desc
    return render_to_response('market/add_article.html', {
        'template_types': template_types,
        'templates': templates,
        'article_type': article_type,
        'template_type': template_type,
        'template_id': template_id,
        'vari_list': vari_list,
        'content_list': content_list,
        'vari_infos': vari_infos,
        'desc': desc,
        'info': info,
        'jsons': json.dumps(jsons),
        'infos': infos,
    }, context_instance=RequestContext(request))


@csrf_exempt
def preview(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_id = request.POST.get('game_id')
    game_name = request.POST.get('game_name')
    log.debug([game_id])
    download_url = GamePkgInfo.objects.get(game_id=game_id, is_max_version=1).download_url
    log.debug(request.POST)
    if 'title_template' not in request.POST:
        game = GameLabel.objects.get(game_id=game_id)
        JSON = {
        'game_id': game_id,
        'game_detail_desc': game.detail_desc,
        'game_icon_url': game.icon_url,
        'game_screen_shot_urls': ','.join(game.screen_shot_urls.split('\n')),
        'download_url': download_url,
        'game_name': game_name
        }
        import json
        response.write(json.dumps(JSON))
        return response
    title_template = request.POST.get('title_template')
    content_template = request.POST.get('content_template')
    search_mid = r'\[\[(.*?)\]\]'
    vari_info_ids = set()
    content = content_template.replace('[[游戏名]]', game_name)
    title = title_template.replace('[[游戏名]]', game_name)
    if re.search(search_mid, title):
        for name in re.findall(search_mid, title):
            vari_id = get_info('id', 'iplay_article_vari', 'name', name)
            vari_type = get_info('vari_type', 'iplay_article_vari', 'name', name)
            id = request.POST.get(str(vari_id))
            value = get_info('value', 'iplay_article_vari_info', 'id', id)
            vari_info_ids.add(id)
            if vari_type == 1:
                val = get_info(value.split('.')[1], value.split('.')[0], 'game_id', game_id)
                title = title.replace('[[%s]]' % name, val)
            if vari_type == 2:
                title = title.replace('[[%s]]' % name, value)
    if re.search(search_mid, content):
        for name in re.findall(search_mid, content):
            vari_id = get_info('id', 'iplay_article_vari', 'name', name)
            vari_type = get_info('vari_type', 'iplay_article_vari', 'name', name)
            id = request.POST.get(str(vari_id))
            value = get_info('value', 'iplay_article_vari_info', 'id', id)
            vari_info_ids.add(id)
            if vari_type == 1:
                val = get_info(value.split('.')[1], value.split('.')[0], 'game_id', game_id)
                if name == 'icon':
                    val = '<img src="%s">' % val
                content = content.replace('[[%s]]' % name, val)
            if vari_type == 2:
                content = content.replace('[[%s]]' % name, value)
    game = GameLabel.objects.get(game_id=game_id)
    vari_info_ids = ','.join(list(vari_info_ids))
    download_url = GamePkgInfo.objects.get(game_id=game_id, is_max_version=1).download_url
    JSON = {
        'vari_info_ids': vari_info_ids,
        'content': content,
        'title': title,
        'game_id': game_id,
        'game_detail_desc': game.detail_desc,
        'game_icon_url': game.icon_url,
        'game_screen_shot_urls': ','.join(game.screen_shot_urls.split('\n')),
        'game_name': game_name,
        'download_url': download_url
    }
    import json
    response.write(json.dumps(JSON))
    return response
 

@csrf_exempt
def search_article(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    game_name = request.GET.get('game_name')
    search_result = []
    if not search_result:
        try:
            search_result = ArticleInfo.objects.filter(title__contains=game_name)
        except:
            search_result = []
    if not search_result:
        try:
            search_result = ArticleInfo.objects.filter(game_id=game_name)
        except:
            search_result = []
    if not search_result:
        try:
            search_result = ArticleInfo.objects.filter(content__contains=game_name)
        except:
            search_result = []
    infos = search_result
    count = len(infos)
    return render_to_response('market/article_info.html', {
        "infos": infos,
        "count": count
    }, context_instance=RequestContext(request))
    

@csrf_exempt
def save_article(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    article_id = request.POST.get('article_id')
    game_id = request.POST.get('game_id')
    game_name = request.POST.get('game_name')
    title = request.POST.get('title')
    short_title = request.POST.get('short_title')
    author = request.POST.get('author')
    source = request.POST.get('source')
    status = request.POST.get('status')
    article_type = request.POST.get('article_type')
    content = request.POST.get('content')
    content = content.replace('下载GG助手', '下载<a href="http://116.255.129.52/api/rdl?id=theapk&fromtype=10&frominfo=%s">GG助手</a>' % game_id)
    template_id = request.POST.get('template_id')
    save_timestamp = get_timestamp(request.POST.get('save_timestamp'))
    vari_info_ids = request.POST.get('vari_info_ids')
    parent_id = request.POST.get('parent_id')
    if not parent_id:
         parent_id = 0
    if int(article_type) != 1:
        if article_id:
            article = ArticleInfo.objects.filter(article_id=article_id).update(game_id=game_id,
                    title=title, short_title=short_title, author=author, source=source,
                    status=status, article_type=article_type, vari_info_ids='',
                    content=content, template_id=template_id, parent_id=parent_id,
                    save_timestamp=save_timestamp, game_name=game_name)
        else:
            article = ArticleInfo(game_id=game_id, title=title,
                short_title=short_title, author=author, source=source,
                status=status, article_type=article_type, vari_info_ids=vari_info_ids,
                content=content, template_id=template_id, parent_id=parent_id,
                save_timestamp=save_timestamp, game_name=game_name)
            article.save()
            article_id = ArticleInfo.objects.all().order_by('-article_id')[0].article_id
        JSON = {
            'article_id': article_id,
            'content': content,
            'title': title,
            'article_type': article_type,
            'save_timestamp': save_timestamp
        }
        import json
        response.write('yre')
        return response


    if article_id:
        article = ArticleInfo.objects.filter(article_id=article_id).update(
	    title=title, short_title=short_title, author=author, source=source,
	    status=status,
	    content=content,
	    save_timestamp=save_timestamp)
        result = '修改成功'
    #新增文章
    else:
        try:
            article = ArticleInfo(game_id=game_id, title=title,
	        short_title=short_title, author=author, source=source,
	        status=status, article_type=article_type, vari_info_ids=vari_info_ids,
	        content=content, template_id=template_id, parent_id=parent_id,
	        save_timestamp=save_timestamp, game_name=game_name)
            article.save()
            article_id = ArticleInfo.objects.all().order_by('-article_id')[0].article_id
            result = '添加成功'
        except:
            article_id = ArticleInfo.objects.get(title=title).article_id
            result = '<<%s>>已存在' % title
    response.write(result)
    return response


@csrf_exempt
def article_template_info(request):
    infos = ArticleTemplateInfo.objects.all().order_by('-template_id')
    for info in infos:
        info.template_type = TEMPLATE_TYPE[info.template_type]
    return render_to_response('market/article_template_info.html', {
        'infos': infos
    }, context_instance=RequestContext(request))


@csrf_exempt
def add_article_template(request):
    try:
        template_id = request.GET.get('template_id')
        info = ArticleTemplateInfo.objects.get(template_id=template_id)
    except:
        info = {}
    return render_to_response('market/add_article_template.html', {
       'info': info
    }, context_instance=RequestContext(request))


@csrf_exempt
def save_article_template(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    template_id = request.POST.get('template_id')
    title = request.POST.get('title')
    template_type = request.POST.get('template_type')
    content = request.POST.get('content')
    desc = request.POST.get('desc')
    if template_id:
        template = ArticleTemplateInfo.objects.filter(template_id=template_id).update(title=title,
            template_type=template_type, content=content, desc=desc)
    else:
        template = ArticleTemplateInfo(title=title, template_type=template_type, content=content, desc=desc)
        template.save()
    response.write('%s_%s_%s_%s' % (template_id, title, template_type, content))
    return response


@csrf_exempt
def article_vari_info(request):
    infos = ArticleVariInfo.objects.all().order_by('id')
    for info in infos:
        info.vari_name = get_info('name', 'iplay_article_vari', 'id', info.vari_id)
    return render_to_response('market/article_vari_info.html', {
        'infos': infos
    }, context_instance=RequestContext(request))


@csrf_exempt
def add_article_vari(request):
    varis = ArticleVari.objects.all()
    id = request.GET.get('id')
    try:
        info = ArticleVariInfo.objects.get(id=id)
    except:
        info = {}
    return render_to_response('market/add_article_vari.html', {
       'varis': varis,
       'info': info
    }, context_instance=RequestContext(request))


@csrf_exempt
def save_article_vari(request):
    response=HttpResponse()  
    response['Content-Type'] = 'text/string'
    id = request.POST.get('id')
    vari_id = request.POST.get('vari_id')
    value = request.POST.get('value')
    if id:
        vari = ArticleVariInfo.objects.filter(id=id).update(vari_id=vari_id, value=value)
    else:
        vari = ArticleVariInfo(vari_id=vari_id, value=value)
        vari.save()
    response.write('yes')
    return response


@csrf_exempt
def search_game(request):
    keyword = request.POST.get('keyword').strip()
    if keyword:
        datas = {}
        games = GameLabel.objects.filter(Q(display_name__contains=keyword, source=3, enabled=1, is_in_test=0) | Q(display_name__contains=keyword, source=4, enabled=1, is_in_test=0)) 
        for index, game in enumerate(games):
            datas[str(index)] = [game.game_id, game.display_name, game.icon_url]
        return HttpResponse(json.dumps(datas))
    else:
        error = ''
        return HttpResponse(error)
       

@csrf_exempt
def add_game(request):
    try:
        game_id = request.POST.get('game')
        game_info = GameLabel.objects.get(game_id=game_id)
        return HttpResponseRedirect('/market/add_article.html')
    except:
        return HttpResponse('请选择游戏！！！')
