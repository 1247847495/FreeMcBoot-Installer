# -*- coding: utf-8 -*-
"""fix_i18n_round2.py
1. select_swapkeys 两个选项翻译为 UIT_SWAPOPT_X / UIT_SWAPOPT_O
2. 中文菜单函数内 y += FONT_HEIGHT; 行距加大为 +2 (16px 汉字不再贴行)
"""
import io
import re
import sys

CONFIG = r"..\config.c"
Y = "\xff"

# ---- Part 1: swapkeys options ----
FIX1 = [
    ('printXY("' + Y + '0: ' + Y + '1 Cancel / ' + Y + '0 OK",',
     'printXY(UIT_SWAPOPT_X,', 1),
    ('printXY("' + Y + '1: ' + Y + '0 Cancel / ' + Y + '1 OK",',
     'printXY(UIT_SWAPOPT_O,', 1),
]

# ---- Part 2: 中文菜单函数列表 ----
CN_FUNCS = [
    "Config_fmcb_key",
    "Config_fmcb_OSDSYS",
    "Config_fmcb_OSDSYS_item",
    "Config_fmcb_OSDSYS_scroll",
    "Config_ESR_path",
    "Config_fmcb",
]

FUNC_RE = re.compile(r'^(int|void)\s+(\w+)\s*\(', re.M)


def main():
    with io.open(CONFIG, "r", encoding="latin-1", newline="") as f:
        text = f.read()

    errors = 0
    for old, new, cnt in FIX1:
        found = text.count(old)
        if found != cnt:
            print("MISMATCH swapkeys (expect %d, found %d): %r" % (cnt, found, old[:60]))
            errors += 1
        else:
            text = text.replace(old, new)

    # 找出所有函数起止行号
    marks = [(m.start(), m.group(2)) for m in FUNC_RE.finditer(text)]
    marks.append((len(text), "_EOF_"))

    spacing_hits = 0
    out_parts = []
    prev_end = 0
    for i in range(len(marks) - 1):
        fstart, fname = marks[i]
        fend = marks[i + 1][0]
        out_parts.append(text[prev_end:fstart])
        body = text[fstart:fend]
        if fname in CN_FUNCS:
            n = body.count("\ty += FONT_HEIGHT;")
            body = body.replace("\ty += FONT_HEIGHT;", "\ty += FONT_HEIGHT + 2;")
            spacing_hits += n
            print("%s: %d 行距已调整" % (fname, n))
        out_parts.append(body)
        prev_end = fend
    out_parts.append(text[prev_end:])
    text = "".join(out_parts)

    if errors:
        print("FAILED: %d mismatches, file not written" % errors)
        sys.exit(1)

    with io.open(CONFIG, "w", encoding="latin-1", newline="") as f:
        f.write(text)
    print("OK: swapkeys 翻译 2 处, 行距调整 %d 处" % spacing_hits)


if __name__ == "__main__":
    main()
