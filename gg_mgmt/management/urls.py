#! -*- coding:utf-8 -*-


__author__ = 'xiangxiaowei'


from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^gg_mgmt/developer/index/$', 'management.views.index', name='developer_index'),
    url(r'^gg_mgmt/developer/add/$', 'management.views.add', name='developer_add'),
    url(r'^gg_mgmt/developer/delete/$', 'management.views.delete', name='developer_delete'),
    url(r'^gg_mgmt/developer/edit/$', 'management.views.edit', name='developer_edit'),
    url(r'^gg_mgmt/developer/operation/$', 'management.views.operation', name='operation'),
    url(r'^gg_mgmt/developer/(?P<dev_name>[\w\W]*)/list/$', 'management.views.game_list', name='developer_game_list'),
    url(r'^gg_mgmt/developer/imei/$', 'management.views.imei', name='imei_index'),
    url(r'^gg_mgmt/developer/editImei/$', 'management.views.editImei', name='imei_edit'),
    url(r'^gg_mgmt/developer/addImei/$', 'management.views.addImei', name='imei_add'),
    url(r'^gg_mgmt/developer/deleteImei/$', 'management.views.deleteImei', name='imei_delete'),
    url(r'^gg_mgmt/developer/consumer/$', 'management.views.consumer', name='consumer'),
    url(r'^gg_mgmt/editor/index/$', 'management.views.editor', name='editor'),
    url(r'^gg_mgmt/editor/edit/$', 'management.views.editEditor', name='edit'),
)
