#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: urls.py
Author: xiangxiaowei
Date: 04/14/15
Description:
"""

from django.db import models


class IplayAdInfo(models.Model):
    id = models.IntegerField('广告id', max_length=11, primary_key=True)
    type = models.IntegerField('使用场景: type=1,用于游戏安装时的等待页面', max_length=11)
    package_name = models.CharField('游戏id, 可以为空, 表明该位置的缺省广告, 否则是对应某游戏的广告', max_length=512)
    order_num = models.IntegerField('在当前type和game_id下的顺序, 最终返回给客户端时会按照此顺序排序, 缺省广告会排在game_id专有广告之后一起返回', max_length=11)
    title = models.CharField('用于通知栏标题、应用推荐的应用名、安装界面标题等', max_length=1000)
    content = models.TextField('用于通知栏小字、应用推荐中的一句话描述、安装界面文字描述等')
    pic_url = models.CharField('用于通知栏图标、应用推荐图标、安装界面banner图等', max_length=1000)
    big_pic_url = models.CharField('目前只用于通知栏大图标', max_length=1000)
    target_type = models.IntegerField('点击后的跳转目标类型: 0-不可点击 1-网页地址,通过浏览器或webview打开 2-进入GG客户端的游戏详情页,3-通过系统downloadManager下载', max_length=11)
    target = models.CharField('点击后的动作内容,对应type. type是0时可以为空', max_length=1000)
    pkg_name = models.CharField('广告目标的包名', max_length=1000)
    ver_name = models.CharField('版本号', max_length=1000)
    size = models.IntegerField('文件大小，单位byte', max_length=11)
    filename = models.CharField('应用文件名', max_length=1000)
    show_delay = models.IntegerField('广告展示延时,单位s', max_length=11)
    next_delay = models.IntegerField('下次广告展示延时,单位s', max_length=11)
    filter_pkg_names = models.CharField('广告目标的过滤包名列表(json串),当用户安装了filter_pkg_names内的包,会在客户端过滤掉', max_length=1000)
    channels = models.CharField('渠道号', max_length=128)
    life_time = models.IntegerField('广告的生命期,单位h', max_length=11)
    monet_silent = models.IntegerField('移动网络时静默下载(0/1) 0-不静默下载, 1-静默下载', max_length=4)
    wifi_silent = models.IntegerField('wifi时静默下载(0/1) 0-不静默下载, 1-静默下载', max_length=4)
    download_dismissible = models.IntegerField('广告下载通知栏是否可被划去(0/1) 0-不可被划去, 1-可被划去', max_length=4)
    install_dismissible = models.IntegerField('广告安装通知栏是否可被划去(0/1) 0-不可被划去, 1-可被划去', max_length=4)

    class Meta:
        db_table = 'iplay_ad_info'
        verbose_name_plural = '广告平台列表'


class IplayEditorInfo(models.Model):
    name = models.CharField('编辑名称', max_length=10, primary_key=True)
    icon_url = models.CharField('编辑头像', max_length=200)
    user_desc = models.CharField('小编描述，个性签名', max_length=200)
    display_name = models.CharField('客户端展示名', max_length=10)

    class Meta:
        db_table = 'iplay_editor_info'
        verbose_name_plural = '编辑信息表'


class IplayGameLabelInfo(models.Model):
    game_id = models.CharField('', max_length=8, primary_key=True)
    display_name = models.CharField('', max_length=100)
    icon_url = models.CharField('', max_length=1000)
    source = models.IntegerField('', max_length=10)

    class Meta:
        db_table = 'iplay_game_label_info'
        verbose_name_plural = '游戏label信息表'


class IplayGamePkgInfo(models.Model):
    apk_id = models.CharField('apk_id', max_length=8, primary_key=True)
    game_id = models.CharField('game_id', max_length=8)
    market_channel = models.CharField('渠道', max_length=45)
    game_name = models.CharField('游戏名', max_length=45)
    pkg_name = models.CharField('游戏名', max_length=45)
    ver_code = models.IntegerField('游戏版本号', max_length=11)
    icon_url = models.CharField('游戏icon', max_length=1000)
    source = models.IntegerField('', max_length=10)

    class Meta:
        db_table = 'iplay_game_pkg_info'
        verbose_name_plural = '游戏pkg信息表'


class IplayToolAdChannelMapping(models.Model):
    id = models.CharField('广告渠道id', max_length=64, primary_key=True)
    name = models.CharField('广告渠道名', max_length=128)

    class Meta:
        db_table = 'iplay_tool_ad_channel_mapping'
        verbose_name_plural = '广告平台渠道列表'


class IplayReleaseList(models.Model):
    id = models.IntegerField('发布列表ID', max_length=11, primary_key=True)
    start_date = models.IntegerField('发布开始时间', max_length=11)
    end_date = models.IntegerField('发布结束时间', max_length=11)
    is_finished = models.IntegerField('发布状态', max_length=4)
    msg = models.IntegerField('发布结束信息', max_length=11)
    worker = models.CharField('服务器名称', max_length=45)
    type = models.IntegerField('发布类型：１游戏数据发布；２广告数据发布', max_length=11)

    class Meta:
        db_table = 'iplay_release_list'
        verbose_name_plural = '发布列表'


class IplayUploadPlugin(models.Model):
    id = models.IntegerField('插件入库列表ID', max_length=11, primary_key=True)
    plugin_pkg_name = models.CharField('插件包名', max_length=45)
    plugin_ver_code = models.IntegerField('插件版本号', max_length=11)
    target_pkg_name = models.CharField('目标游戏包名', max_length=45)
    target_ver_code = models.IntegerField('目标游戏版本号', max_length=11)
    editor = models.CharField('插件入库人', max_length=45)
    msg = models.IntegerField('插件入库信息', max_length=11)
    is_finished = models.IntegerField('插件入库状态', max_length=11)
    save_timestamp = models.IntegerField('插件入库开始时间', max_length=11)
    update_timestamp = models.IntegerField('插件入库结束时间', max_length=11)

    class Meta:
        db_table = 'iplay_upload_plugin'
        verbose_name_plural = '插件入库列表'

####
####
####iplay_mgmt
class RecGame(models.Model):
    game_id = models.CharField('游戏ID', max_length=11, primary_key=True)
    game_name = models.CharField('游戏名称', max_length=200)
    order_num = models.IntegerField('该游戏在推荐页中的位置', max_length=11)
    manual_num = models.IntegerField('该游戏的真实序号', max_length=11)
    enabled = models.IntegerField('有效', max_length=11)
    release_date = models.IntegerField('发布时间', max_length=11)
    unrelease_date = models.IntegerField('下线时间', max_length=11)

    class Meta:
        db_table = 'iplay_recomend_game'
        verbose_name_plural = '推荐页游戏列表'


class GameLabel(models.Model):
    game_id = models.CharField('游戏ID', max_length=8, primary_key=True)
    game_name = models.CharField('游戏名', max_length=50)
    display_name = models.CharField('游戏显示名', max_length=50)
    game_types = models.CharField('', max_length=1000)
    game_tags = models.CharField('', max_length=1000)
    screen_shot_urls = models.CharField('', max_length=5000)
    icon_url = models.CharField('', max_length=1000)
    forum_url = models.CharField('', max_length=1000)
    post_url = models.CharField('', max_length=1000)
    tid = models.IntegerField('', max_length=11)
    short_desc = models.CharField('', max_length=1000)
    detail_desc = models.TextField('', max_length=8000)
    star_num = models.IntegerField('', max_length=11)
    download_counts = models.IntegerField('', max_length=11)
    game_language = models.CharField('', max_length=200)
    save_timestamp = models.IntegerField('', max_length=11)
    update_timestamp = models.IntegerField('', max_length=11)
    min_apk_size = models.IntegerField('', max_length=11)
    max_apk_size = models.IntegerField('', max_length=11)
    min_ver_name = models.CharField('', max_length=20)
    max_ver_name = models.CharField('', max_length=20)
    enabled = models.IntegerField('', max_length=1)
    subscript = models.CharField('', max_length=50)
    color_label = models.CharField('', max_length=50)
    source = models.IntegerField('', max_length=1)
    is_changed = models.BooleanField('是否修改', max_length=1)
    game_alias = models.CharField('', max_length=5000)
    origin_types = models.CharField('', max_length=5000)
    disable_reason = models.CharField('', max_length=1000)
    developer = models.CharField('', max_length=1000)
    gg_download_cnt = models.IntegerField('', max_length=11)
    subscript_expire_time = models.IntegerField('', max_length=10)
    is_in_test = models.IntegerField('', max_length=1)
    gg_download_week = models.IntegerField('', max_length=11)

    class Meta:
        db_table = 'iplay_game_label_info'
        verbose_name_plural = '游戏信息'


class GameToResult(models.Model):
    id = models.IntegerField('', max_length=11, primary_key=True)
    category_id = models.IntegerField('分类ｉｄ', max_length=11)
    game_id = models.CharField('游戏ID', max_length=8)
    order_num = models.IntegerField('排序号码', max_length=11)
    order_type = models.IntegerField('排序方式', max_length=11)

    class Meta:
        db_table = 'iplay_category_to_game_result'
        verbose_name_plural = '返回给客户端不同排序方式的游戏结果'


class GameBanner(models.Model):
    id = models.IntegerField('ID', max_length=11, primary_key=True, null=False)
    topic_id = models.IntegerField('专题ID（对应iplay_topic_info的id）', max_length=11)
    game_id = models.CharField('游戏ID（对应game_label_info的id）', max_length=11)
    name = models.CharField('banner名称', max_length=200)
    pic_url = models.CharField('图片地址', max_length=1000)
    order_num = models.IntegerField('该banner在推荐页中的位置', max_length=11)
    enabled = models.IntegerField('有效', max_length=11)
    release_date = models.IntegerField('发布时间', max_length=11)
    unrelease_date = models.IntegerField('下线时间', max_length=11)

    class Meta:
        db_table = 'iplay_recomend_banner_info'
        verbose_name_plural = '推荐页banner列表'


class PreForumPost(models.Model):
    pid = models.IntegerField('', max_length=11)
    tid = models.IntegerField('帖子ID，关联iplay_game_label_info中的字段', max_length=11, primary_key=True)
    author = models.CharField('评论人', max_length=15)
    dateline = models.IntegerField('', max_length=10)
    message = models.CharField('评论内容', max_length=8000)

    class Meta:
        db_table = 'pre_forum_post'
        verbose_name = '评论内容列表'


class CategoryInfo(models.Model):
    id = models.IntegerField('', max_length=11, primary_key=True)
    display_name = models.CharField('', max_length=200)
    parent_id = models.IntegerField('', max_length=11)

    class Meta:
        db_table = 'iplay_game_category_info'
        verbose_name = '分类信息'


class LabelToPkg(models.Model):
    id = models.IntegerField('', max_length=11, primary_key=True)
    label_id = models.CharField('游戏ID', max_length=8)
    pkg_id = models.CharField('pkgID', max_length=8)
    order_num = models.IntegerField('', max_length=11)

    class Meta:
        db_table = 'iplay_game_label_to_pkg_result'
        verbose_name = '返回给客户端的下载顺序表'


class GamePkg(models.Model):
    apk_id = models.CharField('', max_length=8, primary_key=True)
    game_id = models.CharField('', max_length=8)
    market_channel = models.CharField('', max_length=45)
    game_name = models.CharField('', max_length=45)
    pkg_name = models.CharField('', max_length=100)
    file_md5 = models.CharField('', max_length=32)
    ver_code = models.IntegerField('', max_length=11)
    ver_name = models.CharField('', max_length=40)
    signature_md5 = models.CharField('', max_length=32)
    file_size = models.IntegerField('', max_length=11)
    download_url = models.CharField('', max_length=1000)
    forum_url = models.CharField('', max_length=1000)
    post_url = models.CharField('', max_length=1000)
    min_sdk = models.IntegerField('', max_length=11)
    game_desc = models.CharField('', max_length=8000)
    game_types = models.CharField('', max_length=1000)
    game_tags = models.CharField('', max_length=1000)
    downloaded_cnts = models.IntegerField('', max_length=11)
    is_crack_apk = models.IntegerField('', max_length=1)
    tid = models.IntegerField('', max_length=11)
    depend_google_play = models.IntegerField('', max_length=1)
    game_language = models.CharField('', max_length=200)
    save_timestamp = models.IntegerField('', max_length=11)
    update_timestamp = models.IntegerField('', max_length=11)
    screen_shot_urls = models.CharField('', max_length=5000)
    icon_url = models.CharField('', max_length=1000)
    is_max_version = models.IntegerField('', max_length=1)
    download_url_type = models.IntegerField('', max_length=4)
    enabled = models.IntegerField('', max_length=1)
    source = models.IntegerField('', max_length=1)
    url4details = models.CharField('', max_length=1000)
    is_plugin_required = models.IntegerField('', max_length=1)
    required_plugin_ids = models.CharField('', max_length=1000)
    disable_reason = models.CharField('', max_length=1000)
    is_changed = models.BooleanField('是否修改', max_length=1)
    gg_download_cnt = models.IntegerField('', max_length=11)
    gg_download_week = models.IntegerField('', max_length=11)

    class Meta:
        db_table = 'iplay_game_pkg_info'
        verbose_name_plural = '游戏安装包信息'


class ArticleInfo(models.Model):
    article_id = models.IntegerField('', max_length=11, primary_key=True)
    parent_id = models.IntegerField('', max_length=11)
    game_id = models.CharField('', max_length=8)
    game_name = models.CharField('', max_length=100)
    title = models.CharField('', max_length=100)
    short_title = models.CharField('', max_length=100)
    author = models.CharField('', max_length=100)
    source = models.CharField('', max_length=200)
    status = models.IntegerField('', max_length=11)
    article_type = models.IntegerField('', max_length=11)
    vari_info_ids = models.CharField('', max_length=100)
    content = models.CharField('', max_length=5000)
    template_id = models.IntegerField('', max_length=11)
    save_timestamp = models.IntegerField('', max_length=11)
 
    class Meta:
        db_table = 'iplay_article_info'
        verbose_name = '文章信息表'


class ArticleTemplate(models.Model):
    id = models.IntegerField('', max_length=11, primary_key=True)
    name = models.CharField('', max_length=100)

    class Meta:
        db_table = 'iplay_article_template'
        verbose_name = '模板分类表'
 

class ArticleTemplateInfo(models.Model):
    template_id = models.IntegerField('', max_length=11, primary_key=True)
    template_type = models.IntegerField('', max_length=11)
    title = models.CharField('', max_length=100)
    content = models.CharField('', max_length=5000)
    desc = models.CharField('', max_length=100)

    class Meta:
        db_table = 'iplay_article_template_info'
        verbose_name = '模板信息表'
    

class ArticleVari(models.Model):
    id = models.IntegerField('', max_length=11, primary_key=True)
    vari_type = models.IntegerField('', max_length=11)
    name = models.CharField('', max_length=45)

    class Meta:
        db_table = 'iplay_article_vari'
        verbose_name = '变量信息'


class ArticleVariInfo(models.Model):
    id = models.IntegerField('', max_length=11, primary_key=True)
    vari_id = models.IntegerField('', max_length=11)
    name = models.CharField('', max_length=45)
    value = models.CharField('', max_length=200)

    class Meta:
        db_table = 'iplay_article_vari_info'
        verbose_name = '变量可用值信息'


class GameForecast(models.Model):
    game_id = models.CharField('游戏ID', max_length=8, primary_key=True)
    display_name = models.CharField('游戏显示名', max_length=50)
    game_status = models.IntegerField('', max_length=1)
    game_language = models.CharField('', max_length=200)
    icon_url = models.CharField('', max_length=1000)
    screen_shot_urls = models.CharField('', max_length=5000)
    forum_url = models.CharField('', max_length=1000)
    post_url = models.CharField('', max_length=1000)
    tid = models.IntegerField('', max_length=11)
    short_desc = models.CharField('', max_length=1000)
    detail_desc = models.TextField('', max_length=8000)
    developer = models.CharField('', max_length=1000)
    predict_time = models.CharField('', max_length=8)
    category_ids = models.CharField('', max_length=1000)
    banner_url = models.CharField('', max_length=1000) 
    wanted_counts = models.IntegerField('', max_length=11)
    wanted_counts_random = models.IntegerField('', max_length=11)
    save_timestamp = models.IntegerField('', max_length=11)
    update_timestamp = models.IntegerField('', max_length=11)
    detail_desc_html = models.TextField('详细描述(html)', null=True)
 
    class Meta:
        db_table = 'iplay_game_forecast_info'
        verbose_name_plural = '游戏信息'


class ForecastToLabel(models.Model):
    id = models.IntegerField('ID', max_length=11, primary_key=True)
    game_id = models.CharField('游戏ID', max_length=8)
    label_id = models.CharField('游戏ID', max_length=8)
 
    class Meta:
        db_table = 'iplay_forecast_to_label_result'
        verbose_name_plural = '预测游戏与上线游戏映射表'
   

class GameCategory(models.Model):
    id = models.IntegerField('ID', max_length=11, primary_key=True)
    name = models.CharField('', max_length=200)
    parent_id = models.IntegerField('ID', max_length=11)

    class Meta:
        db_table = 'iplay_game_category_info'
        verbose_name_plural = '游戏类别信息'


class EditorInfo(models.Model):
    name = models.CharField('', max_length=10, primary_key=True)
    icon_url = models.CharField('', max_length=200)
    user_desc = models.CharField('', max_length=200)
    
    class Meta:
        db_table = 'iplay_editor_info'
        verbose_name_plural = 'GG小编信息'


class NotPlayModel(models.Model):
    id = models.IntegerField('ID', max_length=11, primary_key=True)
    gameid = models.CharField('游戏ID', max_length=8)
    model = models.CharField('游戏ID', max_length=500)
    user_name = models.CharField('游戏ID', max_length=45)
    save_timestamp = models.IntegerField('', max_length=11)
   
    class Meta:
        db_table = 'iplay_game_compatibility_model'
        verbose_name_plural = '有关机型的不可玩信息'


class NotPlayFingerprint(models.Model):
    id = models.IntegerField('ID', max_length=11, primary_key=True)
    gameid = models.CharField('游戏ID', max_length=8)
    fingerprint = models.CharField('游戏ID', max_length=500)
    user_name = models.CharField('游戏ID', max_length=45)
    save_timestamp = models.IntegerField('', max_length=11)
   
    class Meta:
        db_table = 'iplay_game_compatibility_fingerprint'
        verbose_name_plural = '有关fingerprint的不可玩信息'
