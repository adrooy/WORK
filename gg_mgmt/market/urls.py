#! -*- coding:utf-8 -*-


__author__ = 'xiangxiaowei'


from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^gg_mgmt/$', 'market.topic.index', name='index topic'),
    url(r'^gg_mgmt/market/topic/$', 'market.topic.index', name='index topic'),
    url(r'^gg_mgmt/market/topic_add/$', 'market.topic.add', name='add topic'),
    url(r'^gg_mgmt/market/topic_edit/$', 'market.topic.edit', name='edit topic'),
    url(r'^gg_mgmt/market/topic_delete/$', 'market.topic.delete', name='delete topic'),
    url(r'^gg_mgmt/market/topic_isenabled/$', 'market.topic.isenabled', name='isenabled topic'),
    url(r'^gg_mgmt/market/topic_notenabled/$', 'market.topic.notenabled', name='notenabled topic'),
    url(r'^gg_mgmt/market/topic_istest/$', 'market.topic.istest', name='istest topic'),
    url(r'^gg_mgmt/market/topic_nottest/$', 'market.topic.nottest', name='nottest topic'),
    url(r'^gg_mgmt/market/topic_up/$', 'market.topic.up', name='up topic'),
    url(r'^gg_mgmt/market/topic_down/$', 'market.topic.down', name='down topic'),
    url(r'^gg_mgmt/market/topic_moveGame/$', 'market.topic.moveGame', name='moveGame topic'),
    url(r'^gg_mgmt/market/topic_addGame/$', 'market.topic.addGame', name='addGame topic'),
    url(r'^gg_mgmt/market/topic_delGame/$', 'market.topic.delGame', name='delGame topic'),
    url(r'^gg_mgmt/market/topic_upGame/$', 'market.topic.upGame', name='upGame topic'),
    url(r'^gg_mgmt/market/topic_downGame/$', 'market.topic.downGame', name='downGame topic'),
    url(r'^gg_mgmt/market/recommend/$', 'market.recommend.index', name='index recommend'),
    url(r'^gg_mgmt/market/recommend_addGame/$', 'market.recommend.addGame', name='addGame recommend'),
    url(r'^gg_mgmt/market/recommend_delGame/$', 'market.recommend.delGame', name='delGame recommend'),
    url(r'^gg_mgmt/market/recommend_editGame/$', 'market.recommend.editGame', name='editGame recommend'),
    url(r'^gg_mgmt/market/recommend_altGame/$', 'market.recommend.altGame', name='altGame recommend'),
    url(r'^gg_mgmt/market/recommend_isenabledGame/$', 'market.recommend.isenabledGame', name='isenabledGame recommend'),
    url(r'^gg_mgmt/market/recommend_notenabledGame/$', 'market.recommend.notenabledGame', name='notenabledGame recommend'),
    url(r'^gg_mgmt/market/recommend_upGame/$', 'market.recommend.upGame', name='upGame recommend'),
    url(r'^gg_mgmt/market/recommend_downGame/$', 'market.recommend.downGame', name='downGame recommend'),
    url(r'^gg_mgmt/market/recommend_addBanner/$', 'market.recommend.addBanner', name='addBanner recommend'),
    url(r'^gg_mgmt/market/recommend_editBanner/$', 'market.recommend.editBanner', name='editBanner recommend'),
    url(r'^gg_mgmt/market/recommend_upBanner/$', 'market.recommend.upBanner', name='upBanner recommend'),
    url(r'^gg_mgmt/market/recommend_downBanner/$', 'market.recommend.downBanner', name='downBanner recommend'),
    url(r'^gg_mgmt/market/recommend_isenabledBanner/$', 'market.recommend.isenabledBanner', name='isenabled banner'),
    url(r'^gg_mgmt/market/recommend_notenabledBanner/$', 'market.recommend.notenabledBanner', name='notenabled banner'),
    url(r'^gg_mgmt/market/recommend_delBanner/$', 'market.recommend.delBanner', name='delete banner'),
    url(r'^gg_mgmt/market/category/$', 'market.category.index', name='index category'),
    url(r'^gg_mgmt/market/category_addGame/$', 'market.category.addGame', name='addGame category'),
    url(r'^gg_mgmt/market/category_delGame/$', 'market.category.delGame', name='delGame category'),
    url(r'^gg_mgmt/market/category_editGame/$', 'market.category.editGame', name='editGame category'),
    url(r'^gg_mgmt/market/category_alterGame/$', 'market.category.alterGame', name='alterGame category'),
    url(r'^gg_mgmt/market/category_alterGame/$', 'market.category.alterGame', name='alterGame category'),
    url(r'^gg_mgmt/market/category/game/up/$', 'market.category.up_game', name='cat_game_up'),
    url(r'^gg_mgmt/market/category/game/down/$', 'market.category.down_game', name='cat_game_down'),
    url(r'^gg_mgmt/market/category_isenabledGame/$', 'market.category.isenabledGame', name='isenabledGame category'),
    url(r'^gg_mgmt/market/category_notenabledGame/$', 'market.category.notenabledGame', name='notenabledGame category'),
    url(r'^gg_mgmt/market/hotsearch/$', 'market.hotsearch.index', name='index hotsearch'),
    url(r'^gg_mgmt/market/hotsearch_add/$', 'market.hotsearch.add', name='add hotsearch'),
    url(r'^gg_mgmt/market/hotsearch_del/$', 'market.hotsearch.delete', name='del hotsearch'),
    url(r'^gg_mgmt/market/hotsearch_edit/$', 'market.hotsearch.edit', name='edit hotsearch'),
    url(r'^gg_mgmt/market/hotsearch_search/$', 'market.hotsearch.search', name='search hotsearch'),
#    url(r'^gg_mgmt/market/assist/$', 'market.hotsearch.assist', name='assist'),
)