#! -*- coding:utf-8 -*-

__author__ = 'xiangxiaowei'


from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^gg_mgmt/game/$', 'game.views.index', name='game'),
    url(r'^gg_mgmt/game/detail/$', 'game.views.detail', name='detail'),
    url(r'^gg_mgmt/game/channel/$', 'game.views.channel', name='channel'),
    url(r'^gg_mgmt/game/gameinfo/$', 'game.views.game_info', name='game_info'),
    url(r'^gg_mgmt/game/labelinfo/$', 'game.views.label_info', name='label_info'),
    url(r'^gg_mgmt/game/search/$', 'game.views.search', name='search'),
    url(r'^gg_mgmt/game/label_info_change/$', 'game.views.label_info_change', name='label_info_change'),
    url(r'^gg_mgmt/game/pkg_info_change/$', 'game.views.pkg_info_change', name='pkg_info_change'),
    url(r'^gg_mgmt/game/addScreen/$', 'game.views.addScreen', name='addScreen'),
    url(r'^gg_mgmt/game/plugin_detail/$', 'game.views.plugin_detail', name='plugin_detail'),
    url(r'^gg_mgmt/game/plugin_search/$', 'game.views.plugin_search', name='plugin_search'),
    url(r'^gg_mgmt/game/plugin/$', 'game.views.plugin', name='plugin'),
    url(r'^gg_mgmt/uploadGame/uploadGame/$', 'game.views.uploadGame', name='uploadGame'),
    url(r'^gg_mgmt/uploadGame/googleGame/$', 'game.views.googleGame', name='googleGame'),
    url(r'^gg_mgmt/uploadGame/otherGame/$', 'game.views.otherGame', name='otherGame'),
    url(r'^gg_mgmt/uploadGame/wandoujiaGame/$', 'game.views.wandoujiaGame', name='wandoujiaGame'),
    url(r'^gg_mgmt/uploadGame/forumGame/$', 'game.views.forumGame', name='forumGame'),
    url(r'^gg_mgmt/uploadGame/addGoogleGame/$', 'game.views.addGoogleGame', name='addGoogleGame'),
    url(r'^gg_mgmt/uploadGame/addOtherGame/$', 'game.views.addOtherGame', name='addOtherGame'),
    url(r'^gg_mgmt/uploadGame/addWandoujiaGame/$', 'game.views.addWandoujiaGame', name='addWandoujiaGame'),
    url(r'^gg_mgmt/uploadGame/addForumGame/$', 'game.views.addForumGame', name='addForumGame'),
    url(r'^gg_mgmt/uploadGame/forumPlugin/$', 'game.views.forumPlugin', name='forumPlugin'),
    url(r'^gg_mgmt/uploadGame/googlePlugin/$', 'game.views.googlePlugin', name='googlePlugin'),
    url(r'^gg_mgmt/uploadGame/addForumPlugin/$', 'game.views.addForumPlugin', name='addForumPlugin'),
    url(r'^gg_mgmt/uploadGame/addGooglePlugin/$', 'game.views.addGooglePlugin', name='addGooglePlugin'),
    url(r'^gg_mgmt/release/release/$', 'game.views.release', name='release'),
    url(r'^gg_mgmt/release/releaseList/$', 'game.views.releaseList', name='releaseList'),
    url(r'^gg_mgmt/release/check/$', 'game.views.check', name='check'),
    url(r'^gg_mgmt/release/releaseData/$', 'game.views.releaseData', name='releaseData'),
    url(r'^gg_mgmt/prompt/$', 'game.views.prompt', name='prompt'),
    url(r'^gg_mgmt/game/advert/$', 'game.views.advert', name='advert'),
    url(r'^gg_mgmt/game/edit_advert/$', 'game.views.edit_advert', name='edit_advert'),
    url(r'^gg_mgmt/game/add_advert/$', 'game.views.add_advert', name='add_advert'),
    url(r'^gg_mgmt/game/del_advert/$', 'game.views.del_advert', name='del_advert'),
    url(r'^gg_mgmt/game/edit_order/$', 'game.views.edit_order', name='edit_order'),
    url(r'^gg_mgmt/game/not_play/$', 'game.views.not_play', name='not_play'),
    url(r'^gg_mgmt/game/edit_not_play/$', 'game.views.edit_not_play', name='edit_not_play'),
    url(r'^gg_mgmt/game/del_not_play/$', 'game.views.del_not_play', name='del_not_play'),
)
