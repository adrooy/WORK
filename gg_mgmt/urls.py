#! -*- coding:utf-8 -*-


__author__ = 'xiangxiaowei'


from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^gg_mgmt/game/predict/info/$', 'views.game_predict_info',
        name='game_predict_info'),
    url(r'^gg_mgmt/game/predict/add/$', 'views.add_game_predict',
        name='add_game_predict'),
    url(r'^gg_mgmt/game/predict/save/$', 'views.save_game_predict',
        name='save_game_predict'),
    url(r'^gg_mgmt/game/predict/search/$', 'views.search_game_predict',
        name='search_game_predict'),
    url(r'^gg_mgmt/article/search/$', 'views.search_article', name='search_article'),
    url(r'^gg_mgmt/article/info/$', 'views.article_info', name='article_info'),
    url(r'^gg_mgmt/article/$', 'views.article', name='article'),
    url(r'^gg_mgmt/article/add/$', 'views.add_article', name='add_article'),
    url(r'^gg_mgmt/article/preview/$', 'views.preview', name='preview'),
    url(r'^gg_mgmt/article/save/$', 'views.save_article', name='save_article'),
    url(r'^gg_mgmt/article/template/info/$', 'views.article_template_info', 
        name='article_template_info'),
    url(r'^gg_mgmt/article/template/add/$', 'views.add_article_template', 
        name='add_article_template'),
    url(r'^gg_mgmt/article/template/save/$', 'views.save_article_template',
        name='save_article_template'),
    url(r'^gg_mgmt/article/vari/info/$', 'views.article_vari_info',
        name='article_vari_info'),
    url(r'^gg_mgmt/article/vari/add/$', 'views.add_article_vari',
        name='add_article_vari'),
    url(r'^gg_mgmt/article/vari/save/$', 'views.save_article_vari',
        name='save_article_vari'),
    url(r'^gg_mgmt/article/game/search/$', 'views.search_game',
        name='search_game'),
    url(r'^gg_mgmt/add_game/$', 'views.add_game', name='add_game'),
)
