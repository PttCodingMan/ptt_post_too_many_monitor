
from . import data_type
from . import i18n
from . import connect_core
from . import screens
from . import exceptions
from . import command


def del_post(
        api,
        board_info,
        board,
        post_aid: str = None,
        post_index: int = 0) -> None:
    check_author = True
    for moderator in board_info.moderators:
        if api._ID.lower() == moderator.lower():
            check_author = False
            break

    post_info = api.get_post(board, aid=post_aid, index=post_index, query=True)
    if post_info.delete_status != data_type.PostDelStatus.exist:
        if post_aid is not None:
            raise exceptions.DeletedPost(board, post_aid)
        else:
            raise exceptions.DeletedPost(board, post_index)

    if check_author:
        if api._ID.lower() != post_info.author.lower():
            raise exceptions.NoPermission(i18n.no_permission)

    api._goto_board(board)

    cmd_list = list()

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(command.enter)
    cmd_list.append('d')

    cmd = ''.join(cmd_list)

    api.confirm = False

    def confirm_delete_handler(screen):
        api.confirm = True

    target_list = [
        connect_core.TargetUnit(
            i18n.any_key_continue,
            '請按任意鍵繼續',
            response=' '),
        connect_core.TargetUnit(
            i18n.confirm_delete,
            '請確定刪除(Y/N)?[N]',
            response='y' + command.enter,
            max_match=1,
            handler=confirm_delete_handler),
        connect_core.TargetUnit(
            i18n.delete_success,
            screens.Target.InBoard,
            break_detect=True),
    ]

    index = api.connect_core.send(
        cmd,
        target_list)

    # last_screen = api.connect_core.get_screen_queue()[-1]
    # print(api.confirm)
    # print(last_screen)
    # print(index)

    if index == 1:
        if not api.confirm:
            raise exceptions.NoPermission(i18n.no_permission)

    if index == -1:
        if post_aid is not None:
            raise exceptions.NoSuchPost(board, post_aid)
        else:
            raise exceptions.NoSuchPost(board, post_index)
