#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'duchunhai'
import sys
#sys.path.append("/home/mgmt/operation")
#from database.mysql_client import connections
#from database.mysql_client import IS_TEST
import urllib2, urllib, cookielib
import re
import time
import MySQLdb
import rethinkdb, base64
import urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import cgi
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from utils.logs import Log
from database import insert, select
from database.mysql_client import IS_TEST, connections


log = Log('PostRobotPlugin.log')
logger = log.get_logger()


class Discuz:
    def __init__(self,user,pwd,args):
        self.username = user
        self.password = pwd
        self.args = args
        self.regex = {
            'loginreg': '<input\s*type="hidden"\s*name="formhash"\s*value="([\w\W]+?)"\s*\/>',
            'replyreg': '<input\s*type="hidden"\s*name="formhash"\s*value="([\w\W]+?)"\s*\/>',
            'tidreg': '<tbody\s*id="normalthread_\d+">[\s\S]+?<span\s*id="thread_(\d+)">',
            'postreg': '<input\s*type="hidden"\s*name="formhash"\s*value="([\w\W]+?)"\s*\/>',
            'tidreg': '<link\s*href="([\w\W]+?)"\s*rel="canonical"\s*\/>',
            'uploadreg': '<input\s*type="hidden"\s*name="hash"\s*value="([\w\W]+?)"\s*>'
        }
        self.conn = None
        self.cur = None
        self.islogin = False
        self.login()

    def login(self):
        try:
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            user_agent = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Mozilla/4.0 \
                    (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.507'
            opener.addheaders = [('User-agent', user_agent)]
            urllib2.install_opener(opener)

            loginurl = self.args['loginurl']

            loginPage = urllib2.urlopen(self.args['loginurl']).read()
            formhash = re.search(self.regex['loginreg'], loginPage)
            formhash = formhash.group(1)

            # print 'start login...'

            postime = str(int(time.time()))
            logindata = urllib.urlencode({
                'posttime': postime,
                'formhash': formhash,
                'loginfield': 'username',
                'username': self.username,
                'password': self.password,
                'questionid': 0,
                'referer': self.args['referer']})
            request = urllib2.Request(self.args['loginsubmiturl'], logindata)
            response = urllib2.urlopen(request)
            loginresphtml = response.read()

            nPos = loginresphtml.index('succeedmessage')
            # if nPos > 0:
            #     print('login success...')

        except Exception,e:
            print 'loggin error: %s' % e

    def post_attach(self, file_name, apk_path, authorid):
        try:
            new_post_page = urllib2.urlopen(self.args['newposturl']).read()
            formhash = re.search(self.regex['uploadreg'], new_post_page)
            formhash = formhash.group(1)
            # print 'hash:', formhash
            # print 'start post attach...'
            # postime = str(int(time.time()))

            register_openers()
            datagen, headers = multipart_encode(
                {'Filedata':  open(apk_path, 'rb'),
                 'Filename': file_name,
                 'hash': formhash,
                 'uid': authorid,
                 'filetype': '.apk',
                 'Upload': 'Submit Query'})
            request = urllib2.Request(self.args['upload_url'], datagen, headers)
            rsp = urllib2.urlopen(request).read()

            return rsp.strip()
        except Exception, e:
            print 'post_attach error: %s' % e

    def post_thread(self, aid, subject, message, sortid, resource_type):
        try:
            post_page = urllib2.urlopen(self.args['post_attach_load']).read()
            # print post_page
            formhash = re.search(self.regex['postreg'], post_page)
            formhash = formhash.group(1)
            # print 'post formhash:', formhash
            #print 'start post...'
            postime = str(int(time.time()))
            postdata = urllib.urlencode({
                'allownoticeauthor': '1',
                'posttime': postime,
                'formhash': formhash,
                'message': message,
                'subject': subject,
                'usesig': '1',
                'wysiwyg': '1',
                'sortid': sortid,
                'selectsortid': sortid,
                'typeoption[resource_type]': resource_type,
                'replycredit_extcredits': '0',
                'replycredit_times': '1',
                'replycredit_membertimes': '1',
                'replycredit_random': '100',
                'readperm': '',
                'save': '',
                'attachnew[%s][description]' % aid: '',
                'attachnew[%s][readperm]' % aid: ''
            })
            request = urllib2.Request(self.args['post_attach_thread'], postdata)
            logger.debug(postdata)
            response = urllib2.urlopen(request)
            rsphtml = response.read()
            tidurl = re.search(self.regex['tidreg'], rsphtml)

            tidstr = '0'
            if tidurl is None:
                logger.debug("Post Failed: %s " % subject)
            else:
                tidurl = tidurl.group(1)
                tidstr = tidurl[tidurl.find('tid=') + 4:]
            # print 'post success... tid :', tidstr

            return tidstr
        except Exception, e:
            print 'post_thread error: %s' % e


def post_plugin(upload_plugin, rethinkdb):
    target_pkg_name = upload_plugin['target_pkg_name']
    target_ver_code = int(upload_plugin['target_ver_code'])
    username = 'robot'
    password = 'lbesecdch'
    authorid = 68
    host = 'http://www.ggzs.me'

    fid = '55' # on server

    sortid = '1'
    resource_type = 'plugin'

    if IS_TEST:
        host = 'http://192.168.1.45'
    logger.debug(host)

    args = {
        'loginurl': host + '/forum/member.php?mod=logging&action=login',
        'loginsubmiturl': host + '/forum/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LUPyq&inajax=1',
        'posturl': host + '/forum/forum.php?mod=post&action=newthread&fid=' + fid,
        'postsubmiturl': host + '/forum/forum.php?mod=post&action=newthread&fid=%s&extra=&topicsubmit=yes',
        'referer': host + '/forum/index',
        'newposturl': host + '/forum/forum.php?mod=post&action=newthread&fid='+fid + '&extra=page%3D1%26filter%3Dsortid%26sortid%3D1&sortid=' + sortid,
        'upload_url': host + '/forum/misc.php?mod=swfupload&action=swfupload&operation=upload&fid=' + fid,
        'post_attach_thread': host + '/forum/forum.php?mod=post&action=newthread&fid='+fid + '&extra=&topicsubmit=yes',
        'post_attach_load': host + '/forum/forum.php?mod=post&action=newthread&fid='+fid + '&extra=page%3D1&sortid=' + sortid
    }
    dz = Discuz(username, password, args)

    all_plugin = rethinkdb.table('PluginDef').filter({"targetName": target_pkg_name, "targetVersion": target_ver_code}).run()


    mysql_conn = connections('Cursor')
    mysql_cursor = mysql_conn.cursor()

    storageId = ""
    rel_num = 0
    plugin_pkg_name = ''
    plugin_ver_code = ''
    for def_doc in all_plugin:
        logger.debug('_________________________________________________________')
        logger.debug(def_doc)
        plugin_pkg_name = def_doc['pluginName']
        plugin_ver_code = def_doc['pluginVersion']
        storageId = def_doc['storageId']
        plugin_name = def_doc['pluginName']
        target_name = def_doc['targetName']
        target_version = def_doc['targetVersion']

        subject = plugin_name + "[" + str(def_doc['pluginVersion']) + "]"
        message = def_doc['label'].encode('UTF-8')
        format_subject = cgi.escape(subject)
        tcnt = mysql_cursor.execute("select * from forum.pre_forum_thread "
                                    "where subject = \"%s\" and authorid = %d and fid = %d and displayorder >= 0"
                                    % (format_subject, authorid, int(fid)))
        logger.debug(subject)
        logger.debug(message)
        if tcnt > 0:
            rel_num += 1
            msg = 102
            logger.debug('has thread for this plugin : %s' % subject)
            continue

        cursor = rethinkdb.table('PluginStore').filter({"id": storageId}).run()
        target_name = def_doc['targetName']

        for doc in cursor:
            logger.debug('select PluginStore')
            tmp_path = r"/tmp/%s.tmp" % plugin_name
            apk_path = r"/tmp/%s.apk" % plugin_name
            apk_name = "%s.apk" % plugin_name
            open(tmp_path, "wb").write(doc['data'])
            base64.decode(open(tmp_path, "rb"), open(apk_path, "wb"))

            aid = dz.post_attach(apk_name, apk_path, authorid)
            dz.login()
            tid = dz.post_thread(aid, subject, message, sortid, resource_type)
            logger.debug("plugin_name[version]: %s aid: %s tid: %s" % (subject, aid, tid))
            msg = 199
            if tid != '0':
                rel_num += 1
    if mysql_conn:
        mysql_conn.close()
    upload_plugin['plugin_pkg_name'] = plugin_pkg_name
    upload_plugin['plugin_ver_code'] = plugin_ver_code
    upload_plugin['target_pkg_name'] = target_pkg_name
    upload_plugin['target_ver_code'] = target_ver_code
    upload_plugin['update_timestamp'] = int(time.time())
    upload_plugin['msg'] = msg
    upload_plugin['is_finished'] = 1 
    logger.debug('POST SUCCESS')
    #return rel_num


def post_plugin_all(upload_plugin, rethinkdb):
    username = 'robot'
    password = 'lbesecdch'
    authorid = 68
    host = 'http://www.ggzs.me'

    fid = '55' # on server

    sortid = '1'
    resource_type = 'plugin'

    if IS_TEST:
        host = 'http://192.168.1.45'
    logger.debug(host)

    args = {
        'loginurl': host + '/forum/member.php?mod=logging&action=login',
        'loginsubmiturl': host + '/forum/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LUPyq&inajax=1',
        'posturl': host + '/forum/forum.php?mod=post&action=newthread&fid=' + fid,
        'postsubmiturl': host + '/forum/forum.php?mod=post&action=newthread&fid=%s&extra=&topicsubmit=yes',
        'referer': host + '/forum/index',
        'newposturl': host + '/forum/forum.php?mod=post&action=newthread&fid='+fid + '&extra=page%3D1%26filter%3Dsortid%26sortid%3D1&sortid=' + sortid,
        'upload_url': host + '/forum/misc.php?mod=swfupload&action=swfupload&operation=upload&fid=' + fid,
        'post_attach_thread': host + '/forum/forum.php?mod=post&action=newthread&fid='+fid + '&extra=&topicsubmit=yes',
        'post_attach_load': host + '/forum/forum.php?mod=post&action=newthread&fid='+fid + '&extra=page%3D1&sortid=' + sortid
    }
    dz = Discuz(username, password, args)

    all_plugin = rethinkdb.table('PluginDef').run()

    mysql_conn = connections('Cursor')
    mysql_cursor = mysql_conn.cursor()

    storageId = ""
    rel_num = 0
    plugin_pkg_name = ''
    plugin_ver_code = ''
    number = 0
    for def_doc in all_plugin:
        logger.debug('_________________________________________________________')
        logger.debug(def_doc)
        plugin_pkg_name = def_doc['pluginName']
        plugin_ver_code = def_doc['pluginVersion']
        storageId = def_doc['storageId']
        plugin_name = def_doc['pluginName']
        target_pkg_name = def_doc['targetName']
        target_ver_code = def_doc['targetVersion']

        subject = plugin_name + "[" + str(def_doc['pluginVersion']) + "]"
        message = def_doc['label'].encode('UTF-8')
        format_subject = cgi.escape(subject)
        tcnt = mysql_cursor.execute("select * from forum.pre_forum_thread "
                                    "where subject = \"%s\" and authorid = %d and fid = %d and displayorder >= 0"
                                    % (format_subject, authorid, int(fid)))
        logger.debug(subject)
        logger.debug(message)
        if tcnt > 0:
            rel_num += 1
            msg = 102
            logger.debug('has thread for this plugin : %s' % subject)
            continue
        cursor = rethinkdb.table('PluginStore').filter({"id": storageId}).run()
        n = 0
        for doc in cursor:
            n += 1
            logger.debug('select PluginStore')
            tmp_path = r"/tmp/%s.tmp" % plugin_name
            apk_path = r"/tmp/%s.apk" % plugin_name
            apk_name = "%s.apk" % plugin_name
            open(tmp_path, "wb").write(doc['data'])
            base64.decode(open(tmp_path, "rb"), open(apk_path, "wb"))

            aid = dz.post_attach(apk_name, apk_path, authorid)
            dz.login()
            tid = dz.post_thread(aid, subject, message, sortid, resource_type)
            logger.debug("plugin_name[version]: %s aid: %s tid: %s" % (subject, aid, tid))
            msg = 199
            if tid != '0':
                rel_num += 1
            upload_plugin = {}
            upload_plugin['plugin_pkg_name'] = plugin_pkg_name
            upload_plugin['plugin_ver_code'] = plugin_ver_code
            upload_plugin['target_pkg_name'] = target_pkg_name
            upload_plugin['target_ver_code'] = target_ver_code
            upload_plugin['update_timestamp'] = int(time.time())
            upload_plugin['msg'] = msg
            upload_plugin['is_finished'] = 1 
            upload_plugin['save_timestamp'] = int(time.time())
            upload_plugin['editor'] = '106.187.54.178'
            insert.insert_iplay_upload_plugin(upload_plugin)
            number += 1
            if n > 1:
                logger.debug('ERROR CURSOR IS MORE THAN ONE: target %s %d' % (target_pkg_name, target_ver_code))
    if mysql_conn:
        mysql_conn.close()
    logger.debug('INSERT INTO iplay_upload_plugin COUNT: %d' % number)


def upload_plugin(plugin_id):
    upload_plugin = select.get_google_plugin_info(plugin_id)
    try:
        rethinkdb.connect(host = 'ga-storage.lbesec.com', port = 65306, db = 'plugins').repl()
        #all_plugin = rethinkdb.table('PluginDef').filter({"storageId": "d2015549-3fb3-4748-b170-c258635df41d"}).run()
        #all_plugin = rethinkdb.table('PluginDef').filter({"pluginName": "com.gameassist.autoplugin.com.com2us.inotia3.normal.freefull.google.global.android.common"}).run()
        #all_plugin = rethinkdb.table('PluginDef').filter({"pluginName": "com.gameassist.autoplugin.com.gameloft.android.ANMP.GloftA8HM"}).run()
    except Exception as e:
        logger.debug(e)
        upload_plugin['plugin_pkg_name'] = ''
        upload_plugin['plugin_ver_code'] = ''
        upload_plugin['update_timestamp'] = int(time.time())
        upload_plugin['msg'] = 101
        upload_plugin['is_finished'] = 1 
        return upload_plugin
    try:
        post_plugin(upload_plugin, rethinkdb)
    except Exception as e:
        logger.debug(e)
        upload_plugin['plugin_pkg_name'] = ''
        upload_plugin['plugin_ver_code'] = ''
        upload_plugin['update_timestamp'] = int(time.time())
        upload_plugin['msg'] = 103
        upload_plugin['is_finished'] = 1 
        return upload_plugin
    return upload_plugin


def upload_plugin_all():
    upload_plugin = {}
    try:
        rethinkdb.connect(host = 'ga-storage.lbesec.com', port = 65306, db = 'plugins').repl()
    except Exception as e:
        logger.debug('rethinkdb error: %s' % e)
        upload_plugin['plugin_pkg_name'] = ''
        upload_plugin['plugin_ver_code'] = ''
        upload_plugin['target_pkg_name'] = ''
        upload_plugin['target_ver_code'] = ''
        upload_plugin['save_timestamp'] = int(time.time())
        upload_plugin['editor'] = '106.187.54.178'
        upload_plugin['update_timestamp'] = int(time.time())
        upload_plugin['msg'] = 101
        upload_plugin['is_finished'] = 1 
        insert.update_iplay_upload_plugin(upload_plugin)
#    try:
    if 1==1:
        post_plugin_all(upload_plugin, rethinkdb)
#    except Exception as e:
    else:
        logger.debug('post_plugin_all: %s' % e)
        upload_plugin['plugin_pkg_name'] = ''
        upload_plugin['plugin_ver_code'] = ''
        upload_plugin['target_pkg_name'] = ''
        upload_plugin['target_ver_code'] = ''
        upload_plugin['save_timestamp'] = int(time.time())
        upload_plugin['editor'] = '106.187.54.178'
        upload_plugin['update_timestamp'] = int(time.time())
        upload_plugin['msg'] = 103
        upload_plugin['is_finished'] = 1 
        insert.update_iplay_upload_plugin(upload_plugin)


if __name__ == '__main__':
    logger.debug('START PostRobotPlugin')
    if len(sys.argv) == 2:
        plugin_id = int(sys.argv[1])
        upload_plugin = upload_plugin(plugin_id)
        insert.update_iplay_upload_plugin(upload_plugin)
    if len(sys.argv) == 1:
        upload_plugin_all()
    logger.debug('END PostRobotPlugin\n\n\n')
