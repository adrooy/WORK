# coding=utf-8
#合并iplay_game_label_info的游戏厂商
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
from database.mysql_client import connections
import re
LABEL_INFO_TABLE = "`forum`.`iplay_game_label_info`"

developer_mapping = {
    "SQUARE ENIX Co.,Ltd.": "SQUARE ENIX",
    "SQUARE ENIX Ltd": "SQUARE ENIX",
    "GAMEVIL Inc.": "GAMEVIL",
    "GAMEVIL": "GAMEVIL",
    "Rovio Entertainment Ltd.": "Rovio",
    "Rovio Stars Ltd.": "Rovio",
    "Rovio Mobile Ltd.": "Rovio",
    "Com2uS USA": "Com2uS",
    "Com2uS": "Com2uS",
    "Electronic Arts Inc": "Electronic Arts",
    "ELECTRONIC ARTS": "Electronic Arts",
    "Activision Publishing, Inc.": "Activision Blizzard",
    "Blizzard Entertainment, Inc.": "Activision Blizzard",
    "BANDAI NAMCO Games": "BANDAI NAMCO",
    "BANDAI NAMCO Games Inc.": "BANDAI NAMCO",
    "Creative Mobile": "Creative Mobile",
    "Creative Mobile's Fun Factory": "Creative Mobile",
    "Deemedya": "Deemedya",
    "Deemedya m.s. ltd.": "Deemedya",
    "KONAMI": "KONAMI",
    "Konami Digital Entertainment, Inc.": "KONAMI",
    "SEGA CORPORATION": "SEGA",
    "SEGA of America": "SEGA",
    "Triniti Interactive Ltd.": "Triniti Interactive",
    "Triniti Interactive Studios Limited": "Triniti Interactive",
    "株式会社カプコン": "CAPCOM",
    "Capcom": "CAPCOM",
    "KONAMI": "KONAMI",
    "Konami Digital Entertainment, Inc.": "KONAMI",
    "CHILLINGO": "Chillingo",
    "Chillingo": "Chillingo"
}

def merge_developer(cur):
    for dev in developer_mapping:
        developer = developer_mapping[dev]
        sqlstr = '''UPDATE %s SET `developer` = "%s" where `developer` = "%s"''' % (LABEL_INFO_TABLE, developer, dev) 
        n = cur.execute(sqlstr)
        print dev, n

if __name__ == '__main__':
    print 'START STEP : %s' % __file__
    conn = connections('DictCursor')
    cursor =  conn.cursor()
    try:
        merge_developer(cursor)
    except Exception as e:
        print '    ERROR : %s' % e
    print "END STEP : %s" % __file__
