#! -*- coding:utf-8 -*-


__author__ = 'xiangxiaowei'


from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^gg_mgmt/feedback/$', 'feedback.views.index', name='feedback'),
    url(r'^gg_mgmt/feedback/detail/', 'feedback.views.detail', name='detail'),
    url(r'^gg_mgmt/feedback/detail_download/', 'feedback.views.detail_download', name='detail_download'),
    url(r'^gg_mgmt/feedback/download/', 'feedback.views.download', name='download'),
)
