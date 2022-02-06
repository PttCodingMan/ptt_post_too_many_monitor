import re

from SingleLog.log import Logger

from . import command
from . import connect_core
from . import i18n
from . import screens

pattern = re.compile('[\d]+:[\d][\d]')


def get_time(api) -> str:
    cmd_list = list()
    cmd_list.append(command.go_main_menu)
    cmd_list.append('A')
    cmd_list.append(command.right)
    cmd_list.append(command.left)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.query_ptt_time_success,
            screens.Target.MainMenu,
            log_level=Logger.DEBUG,
            break_detect=True),
    ]

    index = api.connect_core.send(cmd, target_list)
    if index != 0:
        return None

    ori_screen = api.connect_core.get_screen_queue()[-1]
    line_list = ori_screen.split('\n')[-3:]

    # 0:00

    for line in line_list:
        if '星期' in line and '線上' in line and '我是' in line:
            result = pattern.search(line)
            if result is not None:
                return result.group(0)
    return None
