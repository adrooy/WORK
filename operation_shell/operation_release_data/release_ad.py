#!/usr/bin/python
# coding: utf-8

__author__ = 'xiangxiaowei'


import os
import sys
import time
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
print BASE_DIR
from database.select import get_release_list
from database.insert import update_iplay_release_list
from utils.logs import Log
log = Log('release_ad.log')
logger = log.get_logger()


def main():
    logger.debug('START')
    release_type = 2
    logger.debug(release_type)
    rows = get_release_list(release_type)
    get_data_msg = os.system('cd %s/operation_release_data && fab get_data' % BASE_DIR)
    logger.debug('GET DATA: %s' % str(get_data_msg))
    for row in rows:
        worker = row['worker']
        release_id = str(int(row['id']))
        if get_data_msg != 0:
            msg = 301
            info = {}
            info['id'] = release_id
            info['update_timestamp'] = int(time.time())
            info['is_finished'] = 0
            info['msg'] = msg
            update_iplay_release_list(info)
        else:
            logger.debug('cd %s/operation_release_data && fab -R %s release_ad:release_id=%s,worker=%s' % (BASE_DIR, worker, release_id, worker))
            os.system('cd %s/operation_release_data && fab -R %s release_ad:release_id=%s,worker=%s' % (BASE_DIR, worker, release_id, worker))
    os.system('rm -rf %s/operation_release_data/iplay_ad_info.sql' % BASE_DIR)
    logger.debug('END')
    logger.debug('\n\n\n')


if __name__ == '__main__':
    main()