# -*- coding: utf-8 -*-
"""
fix_kb_round7.py - 词组页底部溢出修复 (byte-level)

问题: hint_y 用 HINT_ROWS(1行*20px) 反推, 词组页 7 行列表从 key_y 画起,
底部超出 hint_y, 最后两条词组画到框外; 且矩阵顶部比英文页高 20px 露黑底。
修复: hint_y 固定用 2 行(40px)预留, 与 KEY_H 的预留一致,
key_y 顶部三页对齐, 词组列表自然落在框内。
"""
import sys

SRC = r"K:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\filer.c"

FIXES = [
(b"\t\tint hint_y = ok_y - HINT_ROWS*(FONT_HEIGHT+4);",
 b"\t\tint hint_y = ok_y - 2*(FONT_HEIGHT+4); //fixed 2-row reserve, matches KEY_H"),
]


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    n_ff = data.count(b"\xff")
    for idx, (old, new) in enumerate(FIXES, 1):
        cnt = data.count(old)
        if cnt != 1:
            print("S%d: anchor count=%d (expect 1), ABORT" % (idx, cnt))
            sys.exit(1)
        data = data.replace(old, new)
        print("S%d ok" % idx)
    if data.count(b"\xff") != n_ff:
        print("0xFF count changed, ABORT")
        sys.exit(1)
    with open(SRC, "wb") as f:
        f.write(data)
    print("written, 0xFF preserved: %d" % n_ff)


if __name__ == "__main__":
    main()
