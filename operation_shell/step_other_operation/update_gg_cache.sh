#!/bin/bash

#echo `date`
#/usr/bin/python /home/mgmt/operation/step_other_operation/update_gg_game_dl_cnt.py

wget -O -  'http://127.0.0.1:8080/gamecommunity/instruction.action?name=game_pkg_info'
wget -O -  'http://127.0.0.1:8080/gamecommunity/instruction.action?name=game_label_info'
wget -O -  'http://127.0.0.1:8080/gamecommunity/instruction.action?name=recomend_banner_info'
