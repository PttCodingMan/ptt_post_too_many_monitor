import os

PTT1_ID = os.environ['PTT1_ID']
PTT1_PW = os.environ['PTT1_PW']

version = '0.0.1'

boards = [
    ('Wanted', 3, 'https://www.ptt.cc/bbs/Wanted/M.1608829773.A.D3B.html'),
    ('HatePolitics', 5, 'https://www.ptt.cc/bbs/HatePolitics/M.1617115262.A.D60.html'),
    ('give', 3, 'https://www.ptt.cc/bbs/give/M.1612495900.A.C32.html'),
]

post_template = '''---
title: =title=
tags:
=tags=
abbrlink: =link=
date: =date=
---
'''