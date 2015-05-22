#!/usr/bin/python
# coding: utf-8


__author__ = 'xiangxiaowei'


import os
import sys
import time
import requests
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.insert import update_label, update_pkg
from database.mysql_client import OPTIONS
from utils.logs import Log
from utils.utils import get_date

DATE = get_date(int(time.time())).split(' ')[0]
log = Log('update_game_%s.log' % DATE)
logger = log.get_logger()


def handle_data(DIR, DATE, worker):
    if worker == '52':
        HOST = OPTIONS['52DictCursor']['host']
        USER = OPTIONS['52DictCursor']['user']
        PASSWD = OPTIONS['52DictCursor']['passwd']
    if worker == '206':
        HOST = OPTIONS['206DictCursor']['host']
        USER = OPTIONS['206DictCursor']['user']
        PASSWD = OPTIONS['206DictCursor']['passwd']
    if worker == '45':
        HOST = OPTIONS['DictCursor']['host']
        USER = OPTIONS['DictCursor']['user']
        PASSWD = OPTIONS['DictCursor']['passwd']
    logger.debug('HOST: %s' % HOST)
    logger.debug('USER: %s' % USER)
    logger.debug('PASSWD: %s' % PASSWD)
    logger.debug('worker: %s' % worker)
    try:
        tar_file = os.path.join(BASE_DIR, '%s.tar.gz' % DATE)
        os.system("tar -zxvf %s -C %s" % (tar_file, BASE_DIR))
        logger.debug('success tar -zxvf data')
    except Exception as e:
        logger.debug('ERROR in update_game.py tar -zxvf data: %s' % str(e.args))
        return
    for files in os.listdir(DIR):
        filename = os.path.join(DIR, files)
        if os.path.isfile(filename):
            if files.endswith('sql'):
                try:
                    os.system("mysql -h%s -u%s -p%s forum < %s" % (HOST, USER, PASSWD, filename))
                    logger.debug('success insert %s ' % filename)
                except Exception as e:
                    logger.debug('ERROR in insert sql: %s' % str(e.args))
                    return 102
            if files.startswith('label'):
                try:
                    update_label(filename, worker)
                    logger.debug('success insert %s ' % filename)
                except Exception as e:
                    logger.debug('ERROR in insert label: %s' % str(e.args))
                    return 103
            if files.startswith('pkg'):
                try:
                    update_pkg(filename, worker)
                    logger.debug('success insert %s ' % filename)
                except Exception as e:
                    logger.debug('ERROR in insert pkg: %s' % str(e.args))
                    return 104
    try:
        if worker == '52':
            #url = 'http://116.255.129.52/api/v1/reload-ad-db?src=3'
            os.system("sh %s/cmd/52_gen_service_mapping.sh" % BASE_DIR)
        if worker == '206':
            #url = 'http://123.59.55.206/api/v1/reload-ad-db?src=3'
            os.system("sh %s/cmd/206_gen_service_mapping.sh" % BASE_DIR)
        #r = requests.post(url)
        #assert r.status_code == 200
        #if r.json()['result']['code'] != 0:
        #    raise Exception
        logger.debug('success insert sh gen_service_mapping.sh')
    except Exception as e:
        logger.debug('ERROR in update_game.py gen_service_mapping: %s' % str(e.args))
        return 105
    return 106


if __name__ == '__main__':
    logger.debug('\n\n\n')
    logger.debug('START')
    try:
        DATE = sys.argv[1]
        worker = sys.argv[2]
        DIR = os.path.join(BASE_DIR, DATE)
        result = handle_data(DIR, DATE, worker)
        logger.debug('returns: %s' % (result))
        tar_file = os.path.join(BASE_DIR, '%s.tar.gz' % DATE)
        os.system("rm -rf  %s" % tar_file)
        tar_file = os.path.join(BASE_DIR, '%s' % DATE)
        os.system("rm -rf  %s" % tar_file)
        logger.debug('END')
        print result
    except Exception as e:
        logger.debug('ERROR in update_game.py main: %s' % str(e.args))
