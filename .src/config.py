import os

PTT1_ID = os.environ['PTT1_ID']
PTT1_PW = os.environ['PTT1_PW']

version = '0.0.1'

board_rules = [
    ('give', [(None, 3, 1)], True, 'https://www.ptt.cc/bbs/give/M.1612495900.A.C32.html'),
    ('Wanted', [(None, 3, 1)], True, 'https://www.ptt.cc/bbs/Wanted/M.1608829773.A.D3B.html'),
    ('HatePolitics', [(None, 5, 1)], True, 'https://www.ptt.cc/bbs/HatePolitics/M.1617115262.A.D60.html'),
    ('Gossiping', [
        (None, 5, 1),
        ('[問卦]', 2, 1),
        ('[新聞]', 1, 1)
    ], True, 'https://www.ptt.cc/bbs/Gossiping/M.1637425085.A.07D.html'),
    ('AllTogether', [(None, 1, 7)], True, 'https://www.ptt.cc/bbs/AllTogether/M.1643211430.A.5FB.html'),
]

post_template = '''---
title: =title=
tags:
=tags=
abbrlink: =link=
date: =date=
---
'''
