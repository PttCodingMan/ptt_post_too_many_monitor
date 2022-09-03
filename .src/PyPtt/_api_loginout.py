import re

from SingleLog import Logger

from . import _api_util
from . import check_value
from . import command
from . import config
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import screens


def logout(api) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        return

    logger = Logger('api', api.config.log_level, **config.LOGGER_CONFIG)

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('g')
    cmd_list.append(command.enter)
    cmd_list.append('y')
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.logout_success,
            '任意鍵',
            break_detect=True),
    ]

    logger.info(i18n.logout)

    try:
        api.connect_core.send(cmd, target_list)
        api.connect_core.close()
    except exceptions.ConnectionClosed:
        pass
    except RuntimeError:
        pass

    api._is_login = False

    logger.stage(i18n.success)


def login(api, ptt_id: str, ptt_pw: str, kick_other_session: bool):
    logger = Logger('api', api.config.log_level, **config.LOGGER_CONFIG)

    _api_util.one_thread(api)

    check_value.check_type(ptt_id, str, 'ptt_id')
    check_value.check_type(ptt_pw, str, 'password')
    check_value.check_type(kick_other_session, bool, 'kick_other_session')

    if api._is_login:
        api.logout()

    api.config.kick_other_session = kick_other_session

    def kick_other_login_display_msg():
        if api.config.kick_other_session:
            return i18n.kick_other_login
        return i18n.not_kick_other_login

    def kick_other_login_response(screen):
        if api.config.kick_other_session:
            return 'y' + command.enter
        return 'n' + command.enter

    api.is_mailbox_full = False

    # def is_mailbox_full():
    #     log.log(
    #         api.config,
    #         LogLevel.INFO,
    #         i18n.MailBoxFull)
    #     api.is_mailbox_full = True

    def register_processing(screen):
        pattern = re.compile('[\d]+')
        api.process_picks = int(pattern.search(screen).group(0))

    if len(ptt_pw) > 8:
        ptt_pw = ptt_pw[:8]

    ptt_id = ptt_id.strip()
    ptt_pw = ptt_pw.strip()

    api._ptt_id = ptt_id
    api._ptt_pw = ptt_pw

    api.connect_core.connect()

    logger.info(i18n.login_id, ptt_id)

    target_list = [
        connect_core.TargetUnit(
            # i18n.HasNewMailGotoMainMenu,
            i18n.mail_box,
            screens.Target.InMailBox,
            # 加個進去 A 選單再出來的動作，讓畫面更新最底下一行
            response=command.go_main_menu + 'A' + command.right + command.left,
            break_detect=True),
        connect_core.TargetUnit(
            i18n.mail_box,
            screens.Target.InMailMenu,
            response=command.go_main_menu),
        connect_core.TargetUnit(
            i18n.login_success,
            screens.Target.MainMenu,
            break_detect=True),
        connect_core.TargetUnit(
            i18n.go_main_menu,
            '【看板列表】',
            response=command.go_main_menu),
        connect_core.TargetUnit(
            i18n.wrong_id_pw,
            '密碼不對',
            break_detect=True,
            exceptions_=exceptions.WrongIDorPassword()),
        connect_core.TargetUnit(
            i18n.wrong_id_pw,
            '請重新輸入',
            break_detect=True,
            exceptions_=exceptions.WrongIDorPassword()
        ),
        connect_core.TargetUnit(
            i18n.login_too_often,
            '登入太頻繁',
            break_detect=True,
            exceptions_=exceptions.LoginTooOften()),
        connect_core.TargetUnit(
            i18n.system_busy_try_later,
            '系統過載',
            break_detect=True),
        connect_core.TargetUnit(
            i18n.del_wrong_pw_record,
            '您要刪除以上錯誤嘗試的記錄嗎',
            response='y' + command.enter),
        connect_core.TargetUnit(
            i18n.post_not_finish,
            '請選擇暫存檔 (0-9)[0]',
            response=command.enter),
        connect_core.TargetUnit(
            i18n.post_not_finish,
            '有一篇文章尚未完成',
            response='Q' + command.enter),
        # connect_core.TargetUnit(
        #     i18n.in_login_process_please_wait,
        #     '登入中，請稍候'),
        connect_core.TargetUnit(
            i18n.in_login_process_please_wait,
            '密碼正確'
        ),
        # 密碼正確
        connect_core.TargetUnit(
            kick_other_login_display_msg,
            '您想刪除其他重複登入的連線嗎',
            response=kick_other_login_response),
        connect_core.TargetUnit(
            i18n.any_key_continue,
            '◆ 您的註冊申請單尚在處理中',
            response=command.enter,
            handler=register_processing),
        connect_core.TargetUnit(
            i18n.any_key_continue,
            '任意鍵',
            response=' '),
        connect_core.TargetUnit(
            i18n.update_sync_online_user_friend_list,
            '正在更新與同步線上使用者及好友名單'),
        connect_core.TargetUnit(
            i18n.go_main_menu,
            '【分類看板】',
            response=command.go_main_menu),
        connect_core.TargetUnit(
            i18n.error_login_rich_people_go_main_menu,
            [
                '大富翁',
                '排行榜',
                '名次',
                '代號',
                '暱稱',
                '數目'
            ],
            response=command.go_main_menu),
        connect_core.TargetUnit(
            i18n.error_login_rich_people_go_main_menu,
            [
                '熱門話題'
            ],
            response=command.go_main_menu),
        connect_core.TargetUnit(
            i18n.skip_registration_form,
            '您確定要填寫註冊單嗎',
            response=command.enter * 3),
        connect_core.TargetUnit(
            i18n.skip_registration_form,
            '以上資料是否正確',
            response='y' + command.enter),
        connect_core.TargetUnit(
            i18n.skip_registration_form,
            '另外若輸入後發生認證碼錯誤請先確認輸入是否為最後一封',
            response='x' + command.enter),
        connect_core.TargetUnit(
            i18n.skip_registration_form,
            '此帳號已設定為只能使用安全連線',
            exceptions_=exceptions.OnlySecureConnection())
    ]
    #
    # #
    #
    # IAC = '\xff'
    # WILL = '\xfb'
    # NAWS = '\x1f'

    cmd_list = []
    # cmd_list.append(IAC + WILL + NAWS)
    cmd_list.append(ptt_id + ',')
    cmd_list.append(command.enter)
    cmd_list.append(ptt_pw)
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    index = api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout,
        refresh=False,
        secret=True)
    ori_screen = api.connect_core.get_screen_queue()[-1]
    if index == 0:

        current_capacity, max_capacity = _api_util.get_mailbox_capacity(api)

        logger.info(i18n.has_new_mail_goto_main_menu)

        if current_capacity > max_capacity:
            api.is_mailbox_full = True

            logger.info(i18n.mail_box_full)

        if api.is_mailbox_full:
            logger.info(i18n.use_mailbox_api_will_logout_after_execution)

        target_list = [
            connect_core.TargetUnit(
                i18n.login_success,
                screens.Target.MainMenu,
                break_detect=True)
        ]

        cmd = command.go_main_menu + 'A' + command.right + command.left

        index = api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_long_timeout,
            secret=True)
        ori_screen = api.connect_core.get_screen_queue()[-1]

    login_result = target_list[index].get_display_msg()
    if login_result != i18n.login_success:
        # print(ori_screen)
        logger.info('reason', login_result)
        raise exceptions.LoginError()

    if '> (' in ori_screen:
        api.cursor = data_type.Cursor.NEW
        logger.debug(i18n.new_cursor)
    else:
        api.cursor = data_type.Cursor.OLD
        logger.debug(i18n.old_cursor)

    if api.cursor not in screens.Target.InBoardWithCursor:
        screens.Target.InBoardWithCursor.append('\n' + api.cursor)

    if len(screens.Target.MainMenu) == len(screens.Target.CursorToGoodbye):
        if api.cursor == '>':
            screens.Target.CursorToGoodbye.append('> (G)oodbye')
        else:
            screens.Target.CursorToGoodbye.append('●(G)oodbye')

    unregistered_user = True
    if '(T)alk' in ori_screen:
        unregistered_user = False
    if '(P)lay' in ori_screen:
        unregistered_user = False
    if '(N)amelist' in ori_screen:
        unregistered_user = False

    if unregistered_user:
        logger.info(i18n.unregistered_user_cant_use_all_api)

    api.is_registered_user = not unregistered_user

    if api.process_picks != 0:
        logger.info(i18n.picks_in_register, api.process_picks)

    api._is_login = True
    logger.stage(i18n.success)
