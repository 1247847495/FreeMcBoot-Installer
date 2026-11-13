#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
fix_stray_quote.py - 修正 fix_osd_i18n.py 首次替换遗留的悬空引号

问题: 提示条行尾原为 `...Paste item");`，宏化后变成 `... UIT_PASTE_ITEM");`
      —— 宏本身展开为字符串字面量，其后不应再有引号；多出的 `"` 会
      开启一个跨行字符串 (stray '\377' / multi-line string 编译错误)。
正确: `... UIT_PASTE_ITEM);`  (参照 config.c 现有的 "SELECT:" UIT_SET_DEFAULT); 模式)
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.abspath(os.path.join(BASE, "..", "config.c"))

old = b'UIT_PASTE_ITEM");'
new = b'UIT_PASTE_ITEM);'

d = open(CFG, "rb").read()
n = d.count(old)
assert n == 2, "expect 2 occurrences, got %d" % n
open(CFG, "wb").write(d.replace(old, new))
print("fixed %d stray quotes" % n)
for i, l in enumerate(open(CFG, "rb").read().split(b"\n")):
    if b"UIT_PASTE_ITEM" in l:
        print(i + 1, repr(l))
