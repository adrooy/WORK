#! -*- coding:utf-8 -*-


__author__ = 'xiangxiaowei'


from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^gg_mgmt/accounts/login/$', 'accounts.views.login', name='login'),
    url(r'^gg_mgmt/accounts/logout/$', 'accounts.views.logout', name='logout'),
)
