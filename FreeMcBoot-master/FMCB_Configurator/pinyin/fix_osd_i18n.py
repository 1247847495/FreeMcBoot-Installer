#!/usr/bin/env utf-8 -*-
# -*- coding: utf-8 -*-
r"""
fix_osd_i18n.py - 补翻 config.c OSD 设定菜单漏掉的英文串

背景: 早期汉化只替换了独立的字符串参数 (LNG(...) / "...")，
OSD 菜单里三处英文内嵌在格式串中或以独立参数形式漏翻：
  1. "Hacked OSDSYS" 标签       (2 处)
  2. "Enter" 标签               (1 处)
  3. 提示条 "ÿ1:OK ÿ0:Clear ÿ<|ÿ::Change item L2:Copy item R2:Paste item"
     及 swapKeys 变体            (2 处)

注意: config.c 含原始单字节 0xFF (按钮图标引导符)，文件不是合法
UTF-8，必须按字节替换，绝不能经文本编辑器重存 (否则 0xFF 又会
变成 0xC3 0xBF 产生 "每" 乱码)。
"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.abspath(os.path.join(BASE, "..", "config.c"))

Y = b"\xff"  # 原始单字节 0xFF，保持不动

# (旧字节串, 新字节串, 预期次数)
REPLACEMENTS = [
    # 标签: "Hacked OSDSYS" -> 宏
    (b'"Hacked OSDSYS"', b"UIT_HACKED_OSDSYS", 2),
    # 标签: "Enter" -> 宏
    (b'"Enter"', b"UIT_ENTER", 1),
    # 提示条 (swapKeys 分支, ÿ1 在前)。注意: 旧串需连同收尾 `");` 一起
    # 匹配——宏化的新串以宏结尾，其后不能再有引号 (否则悬空引号会开启
    # 跨行字符串，产生 stray '\377' 编译错误)
    (Y + b"1:OK " + Y + b"0:Clear " + Y + b"<|" + Y + b"::Change item"
     b' L2:Copy item R2:Paste item");',
     Y + b'1:" UIT_OK " ' + Y + b'0:" UIT_CLEAR " ' + Y + b'<|' + Y +
     b'::" UIT_CHANGE_ITEM " L2:" UIT_COPY_ITEM " R2:" UIT_PASTE_ITEM);', 1),
    # 提示条 (普通分支, ÿ0 在前)
    (Y + b"0:OK " + Y + b"1:Clear " + Y + b"<|" + Y + b"::Change item"
     b' L2:Copy item R2:Paste item");',
     Y + b'0:" UIT_OK " ' + Y + b'1:" UIT_CLEAR " ' + Y + b'<|' + Y +
     b'::" UIT_CHANGE_ITEM " L2:" UIT_COPY_ITEM " R2:" UIT_PASTE_ITEM);', 1),
]


def main():
    with open(CFG, "rb") as f:
        data = f.read()
    for old, new, expect in REPLACEMENTS:
        n = data.count(old)
        if n != expect:
            print("ABORT: %r 出现 %d 次 (预期 %d)，不替换"
                  % (old[:40], n, expect))
            sys.exit(1)
    for old, new, expect in REPLACEMENTS:
        data = data.replace(old, new)
        print("OK: %r ... -> 已替换 %d 处" % (old[:32], expect))
    with open(CFG, "wb") as f:
        f.write(data)
    # 自检: 不应引入 UTF-8 化的 0xFF，代码中的目标英文应清除
    # (注释里的 "Hacked OSDSYS" 字样保留，不影响运行)
    assert data.count(b"\xc3\xbf") == 0, "意外引入 C3BF!"
    assert b'"Hacked OSDSYS"' not in data
    assert b"Change item L2" not in data
    print("config.c 共 %d 字节，自检通过" % len(data))


if __name__ == "__main__":
    main()
