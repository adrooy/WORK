#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: urls.py
Author: xiangxiaowei
Date: 14/04/2015
Description:
"""


from django.conf.urls import patterns, include, url


urlpatterns = patterns('',

    # 首页
    url(r'^gg_mgmt/$', 'forum.views.iplay_ad_info', name='iplay_ad_info'),

    # 游戏信息
    url(r'^gg_mgmt/game/info/$', 'forum.game.game_info', name='game_info'),

    # 广告
    url(r'^gg_mgmt/ad/info/$', 'forum.views.iplay_ad_info', name='iplay_ad_info'),
    url(r'^gg_mgmt/ad/del/$', 'forum.views.del_iplay_ad', name='del_iplay_ad'),
    url(r'^gg_mgmt/ad/edit/$', 'forum.views.edit_iplay_ad', name='edit_iplay_ad'),
    url(r'^gg_mgmt/ad/add/$', 'forum.views.add_iplay_ad', name='add_iplay_ad'),
    url(r'^gg_mgmt/ad/up/$', 'forum.views.up_iplay_ad', name='up_iplay_ad'),
    url(r'^gg_mgmt/ad/down/$', 'forum.views.down_iplay_ad', name='down_iplay_ad'),

    # 游戏入库
    url(r'^gg_mgmt/upload/game/info/$', 'forum.game.upload_game_info', name='upload_game_info'),
    url(r'^gg_mgmt/upload/game/$', 'forum.game.upload_game', name='upload_game'),

    # 插件入库
    url(r'^gg_mgmt/upload/plugin/info/$', 'forum.views.plugin_info', name='plugin_info'),
    url(r'^gg_mgmt/upload/plugin/$', 'forum.views.upload_plugin', name='upload_plugin'),
    #url(r'^gg_mgmt/search/game/$', 'forum.views.search_game', name='game_search'),

    # 广告发布
    url(r'^gg_mgmt/release/ad/info/$', 'forum.views.release_ad_info', name='release_ad_info'),
    url(r'^gg_mgmt/release/ad/$', 'forum.views.release_ad', name='release_ad'),

    # 游戏发布
    url(r'^gg_mgmt/release/game/info/$', 'forum.views.release_game_info', name='release_game_info'),
    url(r'^gg_mgmt/release/game/$', 'forum.views.release_game', name='release_game'),
)
