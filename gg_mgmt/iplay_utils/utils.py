#!/usr/bin/python
#-*- coding:utf-8 -*-

import time
import MySQLdb
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.cache import cache
from django.db import connections

import re
from django.http import HttpResponseRedirect


reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I|re.M)
reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)


#class DetectMobileBrowser():
def process_request(request):
        request.mobile = False
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            b = reg_b.search(user_agent)
            v = reg_v.search(user_agent[0:4])
            return b, v
#            if b or v:
#                return HttpResponseRedirect("http://detectmobilebrowser.com/mobile")

def getTimeStamp(date):
    timeArray = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def getDate(timeStamp):
    if timeStamp:
        timeArray = time.localtime(timeStamp)
        date = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
    else:
        date = ''
    return date

def forum_data_conn(func):
    def conn(*args, **kwargs):
        con = MySQLdb.connect(host='192.168.1.45',port=3306,user='root',passwd='111111',db='forum',charset='utf8')
#         con = MySQLdb.connect(host='localhost',port=3306,user='forum',passwd='VQq*d@GY4F7J6]MP',db='forum',charset='utf8')
        con.ping(True)
        db = con.cursor()
        result = func(db, *args, **kwargs)
        con.commit()
        con.close()
        return result
    return conn

def report_data_conn(func):
    def conn(*args, **kwargs):
        con = MySQLdb.connect(host='192.168.1.45',port=3306,user='root',passwd='111111',db='iplayReport',charset='utf8')
        # con = MySQLdb.connect(host='localhost',port=3306,user='forum',passwd='VQq*d@GY4F7J6]MP',db='iplayReport',charset='utf8')
        con.ping(True)
        db = con.cursor()
        result = func(db, *args, **kwargs)
        con.commit()
        con.close()
        return result
    return conn

def admin_data_conn(func):
    def conn(*args, **kwargs):
        con = MySQLdb.connect(host='192.168.1.45',port=3306,user='root',passwd='111111',db='admin',charset='utf8')
        # con = MySQLdb.connect(host='localhost',port=3306,user='forum',passwd='VQq*d@GY4F7J6]MP',db='admin',charset='utf8')
        con.ping(True)
        db = con.cursor()
        result = func(db, *args, **kwargs)
        con.commit()
        con.close()
        return result
    return conn

@admin_data_conn
def get_perm(db, user_id):
    sql = """
        SELECT a.group_id, b.name FROM auth_user_groups AS a JOIN auth_group AS b ON 
    a.group_id = b.id WHERE a.user_id = %s
    """
    db.execute(sql, tuple([user_id]))
    try:
        row = db.fetchall()
        perm_id = row[0][0]
        perm_name = row[0][1]
    except:
        perm_id = ''
        perm_name = ''
    return perm_id, perm_name


def get_sorted(sort_data, sort_keys, sort_key):
#    sort_key = 'a'
#    sort_keys = {'1':{'num': 4,'a':13},'2':{'num': 6,'a':24},'3':{'num': 3, 'a':2}}
#    sorted_keys = {'1':[2,3],'2':[4,8],'3':[1,1]}
#    games = {'1':3,'2':5,'3':2}
    sorted_keys = sorted(sort_keys.items(),key=lambda d:int(d[1][sort_key]),reverse = True)
    sorted_data = []
    number = 1
    for item in sorted_keys:
        game_id = item[0]
        game = sort_data[game_id]
        game.index = number 
        number += 1
        sorted_data.append(game)
    return sorted_data


def get_collapse(html):
    if html in ['/gg_mgmt/feedback/']:
        return 'collapseFour'
    elif html in ['/gg_mgmt/game/', '/gg_mgmt/game/plugin/']:
        return 'collapseOne'
    elif html in ['/gg_mgmt/developer/index/', '/gg_mgmt/developer/operation/', '/gg_mgmt/developer/imei/']:
        return 'collapseSix'
    elif html in ['/gg_mgmt/market/recommend/', '/gg_mgmt/market/topic/', '/gg_mgmt/market/category/', '/gg_mgmt/market/hotsearch/']:
        return 'collapseTwo'
    elif html in ['/gg_mgmt/release/release/', '/gg_mgmt/release/releaseList/', '/gg_mgmt/release/check/']:
        return 'collapseFive'
    elif html in ['/gg_mgmt/uploadGame/otherGame/', '/gg_mgmt/uploadGame/forumGame/', '/gg_mgmt/uploadGame/googleGame/', '/gg_mgmt/uploadGame/uploadGame/', '/gg_mgmt/uploadGame/googlePlugin/']:
        return 'collapseThree'
    else:
        return ''


def pagination(request, queryset, after_range_num=5, before_range_num=4):
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


def get_game_name(game_id):

    game_name = cache.get(game_id)
    if game_name is None:
        cursor_m = connections['market'].cursor()
        cursor_m.execute("SELECT `game_name` FROM `iplay_game_label_info` WHERE `game_id` = '%s'" % game_id)
        try:
            game_name = cursor_m.fetchone()[0]
            cache.set(game_id, game_name)
        except Exception:
            game_name = None
    return game_name


def get_GET_parm_or_default(request, name, default):
    try:
        return request.GET[name]
    except:
        return default


def get_game_info(game_id, string):
    key = '%s_%s' % (game_id, string)
    game_info = cache.get(key)
    if game_info is None:
        cursor_m = connections['game'].cursor()
        cursor_m.execute("SELECT `%s` FROM `iplay_game_label_info` WHERE `game_id` = '%s'" % (string, game_id))
        try:
            game_info = cursor_m.fetchone()[0]
            cache.set(key, game_info)
        except Exception:
            game_info = ''
    return game_info


if __name__ == '__main__':
    print int(time.time())
