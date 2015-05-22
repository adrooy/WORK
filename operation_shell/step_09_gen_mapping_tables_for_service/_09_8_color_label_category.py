#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" description
color_label和category_id处理
"""

__author__ = 'wangfei'
__date__ = '2015/03/13'

from collections import defaultdict
from copy import copy
import itertools

# COLOR_GROUPS = [
# (1, 9, 10),
# (2, ),
# (3, ),
# (4, ),
# (5, 11, 12),
# (6, ),
# (7, ),
# (8, ),
# (13, 14),
# (15, 16, 17),
# (18, )]


class ColorCategory(object):
    """ 彩标和category处理
    """

    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

        # color_label到game映射
        # {'2':set([('game_id', 'save_timestamp', 'gg_download_cnt'),('game_id', 'save_timestamp', 'gg_download_cnt')])}
        self.COLOR_GAMES = defaultdict(lambda: set([]))
        # game_id到color_label映射
        # {'game_id': set(['2','3','4'])}
        self.GAME_COLORS = defaultdict(lambda: set([]))
        # category_id到game映射
        self.CATEGORY_GAMES = defaultdict(lambda: list([]))
        self.category_id = 2000001
        self.ID_COLORS = {}

    def init_table(self):
        sql_create = '''
        CREATE TABLE `iplay_tags_category_id` (
        `tags` VARCHAR(128) UNIQUE NOT NULL,
        `category_id` INTEGER UNIQUE NOT NULL
        );
        '''
        try:
            self.cursor.execute(sql_create)
        except:
            pass
        self.cursor.execute('truncate iplay_tags_category_id')

    def init_color_game(self):
        """初始化color_label 和 game之间多对多映射关系
        """
        sql = 'select color_label, game_id, download_counts, gg_download_cnt, save_timestamp, gg_download_week ' \
              'from iplay_game_label_info'
        self.cursor.execute(sql)
        for cg in self.cursor.fetchall():
            _color_labels = cg['color_label'] or ''
            color_labels = _color_labels.split('\n')

            # 过滤掉18以上的,春海新加的彩标
            bases = [str(i) for i in xrange(1, 19)]
            color_labels = [c for c in color_labels if c in bases]

            self.GAME_COLORS[cg['game_id']].update(color_labels)
            for color_label in color_labels:
                game = (cg['game_id'], cg['download_counts'], cg['gg_download_cnt'], cg['save_timestamp'],
                        cg['gg_download_week'])
                self.COLOR_GAMES[color_label].add(game)

    def gen_category_id(self):
        """ 彩标组合 生成category_id 并入库
        """
        bases = range(1, 19)
        for i in xrange(1, 6):
            for color_labels in itertools.combinations(bases, i):
                color_labels = list(color_labels)
                color_labels.sort()
                color_labels = map(str, color_labels)
                _color_labels = copy(color_labels)
                key = ','.join(color_labels)
                self.ID_COLORS[key] = self.category_id
                sql_gen_category_id = 'insert into iplay_tags_category_id (tags, category_id) ' \
                                      'values (%s, %s)'
                # key, category_id 入库
                self.cursor.execute(sql_gen_category_id, (key, self.category_id))

                # 联合筛选后的游戏
                games = reduce(lambda x, y: x & y, (self.COLOR_GAMES[c] for c in _color_labels))
                games = list(games)
                if games:
                    self.CATEGORY_GAMES[self.category_id].extend(games)
                self.category_id += 1
                # category_id, games, cur_order_num, order_type 入库. 用 executemany

    def main(self):
        self.init_color_game()
        self.gen_category_id()


if __name__ == '__main__':
    import MySQLdb
    import MySQLdb.cursors
    import time

    conn = MySQLdb.Connection(host='192.168.1.45', passwd='111111', db='forum', user='root',
                              cursorclass=MySQLdb.cursors.DictCursor)
    cursor = conn.cursor()
    t0 = time.time()
    color_category = ColorCategory(cursor, conn)
    color_category.init_table()
    color_category.main()
    print color_category.CATEGORY_GAMES
    conn.commit()
    print 'use: %s seconds' % (time.time() - t0)
