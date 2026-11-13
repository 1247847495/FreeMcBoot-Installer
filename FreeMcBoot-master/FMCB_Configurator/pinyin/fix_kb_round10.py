# -*- coding: utf-8 -*-
"""
fix_kb_round10.py - 英文/符号页加半角 ASCII 句点 '.' (byte-level)

用户要的是键盘上的英文半角点 (0x2E, 单字节), 用于输 "4.43" 这类版本号,
不是全角"．"也不是句号"。"。

改动:
1. cn_font.h/c: 码表最前插入 0x002E (升序首位), 附 16x16 大圆点字形
   (底部居中, 6x6 圆点, 键盘格 28px 缩放下清晰可见); CN_FONT_COUNT 4719->4720。
   输出行渲染只对 SJIS 引导字节查询字库, 0x2E 不受影响。
2. filer.c: 英文/符号页提交逻辑——码值 <0x80 按单字节 ASCII 上屏,
   其余仍按 SJIS 双字节。
"""
import sys

BASE = r"K:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator"

# ---- 1. cn_font.h ----
H_OLD = b"#define CN_FONT_COUNT 4719"
H_NEW = b"#define CN_FONT_COUNT 4720"

# ---- 2. cn_font.c ----
C_CODES_OLD = b"const unsigned short cn_font_codes[CN_FONT_COUNT] = {\r\n\t0x8140,"
C_CODES_NEW = b"const unsigned short cn_font_codes[CN_FONT_COUNT] = {\r\n\t0x002E,\r\n\t0x8140,"

C_BITS_OLD = b"const unsigned char cn_font_bits[CN_FONT_COUNT][32] = {\r\n\t{"
# 16x16 glyph for '.': 6x6 round dot, bottom-center (rows 9-14, cols 5-10)
DOT = [b"{"] + [b"0x00,0x00," for _ in range(9)] + [
    b"0x01,0x80,",  # row 9 : cols 7-8
    b"0x03,0xC0,",  # row 10: cols 6-9
    b"0x07,0xE0,",  # row 11: cols 5-10
    b"0x07,0xE0,",  # row 12: cols 5-10
    b"0x03,0xC0,",  # row 13: cols 6-9
    b"0x01,0x80,",  # row 14: cols 7-8
    b"0x00,0x00,",  # row 15
] + [b"},"]
GLYPH = b"\r\n\t" + b"".join(DOT)
C_BITS_NEW = b"const unsigned char cn_font_bits[CN_FONT_COUNT][32] = {" + GLYPH + b"\r\n\t{"

# ---- 3. filer.c commit ----
F_OLD = (
    b"\t\t\t\t\tif(en_mode == 2){  //commit selected full-width EN/symbol char\n"
    b"\t\t\t\t\t\tif(sel < CN_SYM_COUNT && (int)strlen(out)+2 < max){\n"
    b"\t\t\t\t\t\t\tmemmove(out+cur+2, out+cur, strlen(out)-cur+1);\n"
    b"\t\t\t\t\t\t\tout[cur]   = cn_sym_codes[sel] >> 8;\n"
    b"\t\t\t\t\t\t\tout[cur+1] = cn_sym_codes[sel] & 0xFF;\n"
    b"\t\t\t\t\t\t\tcur += 2;\n"
    b"\t\t\t\t\t\t}\n"
)
F_NEW = (
    b"\t\t\t\t\tif(en_mode == 2){  //commit selected EN/symbol char\n"
    b"\t\t\t\t\t\tif(sel < CN_SYM_COUNT){\n"
    b"\t\t\t\t\t\t\tif(cn_sym_codes[sel] < 0x80){  //ASCII char ('.'), single byte\n"
    b"\t\t\t\t\t\t\t\tif((int)strlen(out)+1 < max){\n"
    b"\t\t\t\t\t\t\t\t\tmemmove(out+cur+1, out+cur, strlen(out)-cur+1);\n"
    b"\t\t\t\t\t\t\t\t\tout[cur] = (char)cn_sym_codes[sel];\n"
    b"\t\t\t\t\t\t\t\t\tcur++;\n"
    b"\t\t\t\t\t\t\t\t}\n"
    b"\t\t\t\t\t\t\t}else if((int)strlen(out)+2 < max){\n"
    b"\t\t\t\t\t\t\t\tmemmove(out+cur+2, out+cur, strlen(out)-cur+1);\n"
    b"\t\t\t\t\t\t\t\tout[cur]   = cn_sym_codes[sel] >> 8;\n"
    b"\t\t\t\t\t\t\t\tout[cur+1] = cn_sym_codes[sel] & 0xFF;\n"
    b"\t\t\t\t\t\t\t\tcur += 2;\n"
    b"\t\t\t\t\t\t\t}\n"
    b"\t\t\t\t\t\t}\n"
    b"\t\t\t\t\t}\n"
)


def patch(path, pairs):
    data = open(path, "rb").read()
    n_ff = data.count(b"\xff")
    for old, new in pairs:
        c = data.count(old)
        if c == 0 and data.count(new) == 1:
            print("%s: already applied, skip" % path)
            continue
        if c != 1:
            print("%s: pattern count=%d (expect 1), ABORT" % (path, c))
            sys.exit(1)
        data = data.replace(old, new)
    if data.count(b"\xff") != n_ff:
        print("%s: 0xFF count changed, ABORT" % path)
        sys.exit(1)
    open(path, "wb").write(data)
    print("%s patched (0xFF: %d)" % (path, n_ff))


patch(BASE + r"\cn_font.h", [(H_OLD, H_NEW)])
patch(BASE + r"\cn_font.c", [(C_CODES_OLD, C_CODES_NEW), (C_BITS_OLD, C_BITS_NEW)])
patch(BASE + r"\filer.c", [(F_OLD, F_NEW)])
