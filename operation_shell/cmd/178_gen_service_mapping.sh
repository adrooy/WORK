#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/mgmt/operation_shell/

cd /home/mgmt/operation_shell/PostRobot/

/usr/bin/python PostRobotForLabel.py
/usr/bin/python PostRobotForPkg.py
/usr/bin/python PostRobotForForecast.py

cd /home/mgmt/operation_shell/step_09_gen_mapping_tables_for_service/

/usr/bin/python 09_0_1_gen_iplay_resource_match_result.py
/usr/bin/python 09_0_2_update_pkg_required_plugins.py
/usr/bin/python 09_0_3_merge_developer.py
/usr/bin/python 09_0_4_update_developers.py
/usr/bin/python 09_1_mark_pkg_max_version_in_channel.py
/usr/bin/python 09_2_update_label_sum_info_by_pkg.py
/usr/bin/python 09_3_gen_game_label_to_pkg_result.py
/usr/bin/python 09_5_1_update_game_types.py
/usr/bin/python 09_7_generate_form_url.py
/usr/bin/python 09_8_gen_category_to_game_result.py
