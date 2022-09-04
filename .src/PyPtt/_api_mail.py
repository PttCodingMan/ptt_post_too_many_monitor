from __future__ import annotations

import re
from typing import Dict

from SingleLog import LogLevel
from SingleLog import Logger

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import screens


# 寄信
def mail(api,
         ptt_id: str,
         title: str,
         content: str,
         sign_file,
         backup: bool = True) -> None:
    logger = Logger('main')

    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.Requirelogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(ptt_id, str, 'ptt_id')
    check_value.check_type(title, str, 'title')
    check_value.check_type(content, str, 'content')

    api.get_user(ptt_id)

    check_sign_file = False
    for i in range(0, 10):
        if str(i) == sign_file or i == sign_file:
            check_sign_file = True
            break

    if not check_sign_file:
        if sign_file.lower() != 'x':
            raise ValueError(f'wrong parameter sign_file: {sign_file}')

    cmd_list = []
    # 回到主選單
    cmd_list.append(command.go_main_menu)
    # 私人信件區
    cmd_list.append('M')
    cmd_list.append(command.enter)
    # 站內寄信
    cmd_list.append('S')
    cmd_list.append(command.enter)
    # 輸入 id
    cmd_list.append(ptt_id)
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    # 定義如何根據情況回覆訊息
    target_list = [
        connect_core.TargetUnit(
            i18n.send_mail,
            '主題：',
            break_detect=True),
        connect_core.TargetUnit(
            i18n.no_such_user,
            '【電子郵件】',
            exceptions_=exceptions.NoSuchUser(ptt_id))
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )

    cmd_list = []
    # 輸入標題
    cmd_list.append(title)
    cmd_list.append(command.enter)
    # 輸入內容
    cmd_list.append(content)
    # 儲存檔案
    cmd_list.append(command.ctrl_x)

    cmd = ''.join(cmd_list)

    # 根據簽名檔調整顯示訊息
    if sign_file == 0:
        sing_file_selection = i18n.no_signature_file
    else:
        sing_file_selection = i18n.replace(i18n.select_sign_file, str(sign_file))
    # 定義如何根據情況回覆訊息
    target_list = [
        connect_core.TargetUnit(
            i18n.any_key_continue,
            '請按任意鍵繼續',
            break_detect_after_send=True,
            response=command.enter),
        connect_core.TargetUnit(
            i18n.save_file,
            '確定要儲存檔案嗎',
            response='s' + command.enter, ),
        connect_core.TargetUnit(
            i18n.api_save_draft if backup else i18n.not_api_save_draft,
            '是否自存底稿',
            response=('y' if backup else 'n') + command.enter),
        connect_core.TargetUnit(
            sing_file_selection,
            '選擇簽名檔',
            response=str(sign_file) + command.enter),
        connect_core.TargetUnit(
            sing_file_selection,
            'x=隨機',
            response=str(sign_file) + command.enter),
    ]

    # 送出訊息
    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_post_timeout)

    logger.info(i18n.send_mail, i18n.success)


# --
# ※ 發信站: 批踢踢實業坊(ptt.cc)
# ◆ From: 220.142.14.95
content_start = '───────────────────────────────────────'
content_end = '--\n※ 發信站: 批踢踢實業坊(ptt.cc)'
content_ip_old = '◆ From: '

mail_author_pattern = re.compile('作者  (.+)')
mail_title_pattern = re.compile('標題  (.+)')
mail_date_pattern = re.compile('時間  (.+)')
ip_pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')


def get_mail(api, index: int, search_type: int = 0, search_condition: [str | None] = None,
             search_list: [list | None] = None) -> Dict:
    logger = Logger('get_mail')

    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.Requirelogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    if index == 0:
        return {}
    current_index = api.get_newest_index(data_type.NewIndex.MAIL)
    api.logger.info('current_index', current_index)
    check_value.check_index('index', index, current_index)

    cmd_list = []
    # 回到主選單
    cmd_list.append(command.go_main_menu)
    # 進入信箱
    cmd_list.append(command.ctrl_z)
    cmd_list.append('m')

    # 處理條件整理出指令
    _cmd_list, normal_newest_index = _api_util.get_search_condition_cmd(api, data_type.NewIndex.MAIL, None, search_type,
                                                                        search_condition, search_list)
    cmd_list.extend(_cmd_list)

    # 前進至目標信件位置
    cmd_list.append(str(index))
    cmd_list.append(command.enter)
    cmd = ''.join(cmd_list)

    # 有時候會沒有最底下一列，只好偵測游標是否出現
    if api.cursor == data_type.Cursor.NEW:
        space_length = 6 - len(api.cursor) - len(str(index))
    else:
        space_length = 5 - len(api.cursor) - len(str(index))
    fast_target = f"{api.cursor}{' ' * space_length}{index}"

    # 定義如何根據情況回覆訊息
    target_list = [
        connect_core.TargetUnit(
            i18n.mail_box,
            screens.Target.InMailBox,
            break_detect=True,
            log_level=LogLevel.DEBUG),
        connect_core.TargetUnit(
            i18n.mail_box,
            fast_target,
            break_detect=True,
            log_level=LogLevel.DEBUG)
    ]

    # 送出訊息
    api.connect_core.send(
        cmd,
        target_list)

    # 取得信件全文
    origin_mail, _ = _api_util.get_content(api, post_mode=False)

    # 使用表示式分析信件作者
    pattern_result = mail_author_pattern.search(origin_mail)
    if pattern_result is None:
        mail_author = None
    else:
        mail_author = pattern_result.group(0)[2:].strip()

    logger.debug(i18n.author, mail_author)

    # 使用表示式分析信件標題
    pattern_result = mail_title_pattern.search(origin_mail)
    if pattern_result is None:
        mail_title = None
    else:
        mail_title = pattern_result.group(0)[2:].strip()

    logger.debug(i18n.title, mail_title)

    # 使用表示式分析信件日期
    pattern_result = mail_date_pattern.search(origin_mail)
    if pattern_result is None:
        mail_date = None
    else:
        mail_date = pattern_result.group(0)[2:].strip()
    logger.debug(i18n.date, mail_date)

    # 從全文拿掉信件開頭作為信件內文
    mail_content = origin_mail[origin_mail.find(content_start) + len(content_start) + 1:]

    # 紅包偵測
    red_envelope = False
    if content_end not in origin_mail and 'Ptt幣的大紅包喔' in origin_mail:
        mail_content = mail_content.strip()
        red_envelope = True
    else:

        mail_content = mail_content[:mail_content.rfind(content_end) + 3]

    logger.debug(i18n.content, mail_content)

    if red_envelope:
        mail_ip = None
        mail_location = None
    else:
        # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 111.242.182.114
        # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 59.104.127.126 (臺灣)

        # 非紅包開始解析 ip 與 地區

        ip_line_list = origin_mail.split('\n')
        ip_line = [x for x in ip_line_list if x.startswith(content_end[3:])]

        if len(ip_line) == 0:
            # 沒 ip 就沒地區
            mail_ip = None
            mail_location = None
        else:
            ip_line = ip_line[0]

            result = ip_pattern.search(ip_line)
            if result is None:
                ip_line = [x for x in ip_line_list if x.startswith(content_ip_old)]

                if len(ip_line) == 0:
                    mail_ip = None
                else:
                    ip_line = ip_line[0]
                    result = ip_pattern.search(ip_line)
                    mail_ip = result.group(0)
            else:
                mail_ip = result.group(0)

            logger.debug('IP', mail_ip)

            location = ip_line[ip_line.find(mail_ip) + len(mail_ip):].strip()
            if len(location) == 0:
                mail_location = None
            else:
                # print(location)
                mail_location = location[1:-1]

                logger.debug('location', mail_location)

    return {
        'origin_mail': origin_mail,
        'author': mail_author,
        'title': mail_title,
        'date': mail_date,
        'content': mail_content,
        'ip': mail_ip,
        'location': mail_location,
        'is_red_envelope': red_envelope}


def del_mail(api, index) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.Requirelogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    current_index = api.get_newest_index(data_type.NewIndex.MAIL)
    check_value.check_index(index, current_index)

    cmd_list = []
    # 進入主選單
    cmd_list.append(command.go_main_menu)
    # 進入信箱
    cmd_list.append(command.ctrl_z)
    cmd_list.append('m')
    if index > 20:
        # speed up
        cmd_list.append(str(1))
        cmd_list.append(command.enter)

    # 前進到目標信件位置
    cmd_list.append(str(index))
    cmd_list.append(command.enter)
    # 刪除
    cmd_list.append('dy')
    cmd_list.append(command.enter)
    cmd = ''.join(cmd_list)

    # 定義如何根據情況回覆訊息
    target_list = [
        connect_core.TargetUnit(
            i18n.mail_box,
            screens.Target.InMailBox,
            break_detect=True,
            log_level=LogLevel.DEBUG)
    ]

    # 送出
    api.connect_core.send(
        cmd,
        target_list)

    if api.is_mailbox_full:
        api.logout()
        raise exceptions.MailboxFull()
