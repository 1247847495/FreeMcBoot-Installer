# -*- coding: utf-8 -*-
"""
fix_kb_round6.py - 统一三页框大小/位置 + 底部锚定布局 (byte-level)

问题: 拼音页框 342px、英文页 338px、词组页 302px, 切页时框跳动,
且词组页矮框遮不住下方左右两侧的黑底(菜单未绘制区域)。
修复: KEY_H 固定为最高页(拼音页)高度, 三页框完全重合;
内部改底部锚定(OK 行贴框底), 拼音页布局与原来逐像素一致。
另: 词组行距 24 -> 28, 减少词组页顶部空白。
"""
import sys

SRC = r"K:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\filer.c"

FIXES = [
# S1: 词组行距 24 -> 28
(b"\t\t\tCOM_COL_W=225, COM_CELL=24, //phrase column width / row height",
 b"\t\t\tCOM_COL_W=225, COM_CELL=28, //phrase column width / row height"),

# S2: KEY_H 固定 + 底部锚定布局
(b"\t\tint HINT_ROWS = en_mode ? 1 : 2; //hint lines below keyboard\n"
 b"\t\tint CAND_H = en_mode ? 0 : (3*32 + 8); //candidates: 3 rows (pinyin only)\n"
 b"\t\tint KEY_H = LINE_THICKNESS + 1 + FONT_HEIGHT*3 + 1 + LINE_THICKNESS\n"
 b"\t\t          + 8 + FONT_HEIGHT + 6      //pinyin/page label line\n"
 b"\t\t          + CAND_H                   //candidates: 3 rows\n"
 b"\t\t          + MATRIX_H + 4             //key matrix\n"
 b"\t\t          + HINT_ROWS*(FONT_HEIGHT+4) //key hint lines\n"
 b"\t\t          + FONT_HEIGHT + 8 + LINE_THICKNESS; //OK line\n"
 b"\t\tint KEY_Y  = Menu_tooltip_y - 4 - KEY_H;  //sit above the bottom tooltip row\n"
 b"\t\tint out_y  = KEY_Y + LINE_THICKNESS + 1;\n"
 b"\t\tint py_y   = out_y + FONT_HEIGHT*3 + 1 + LINE_THICKNESS + 8;\n"
 b"\t\tint cand_y = py_y + FONT_HEIGHT + 6;\n"
 b"\t\tint key_y  = cand_y + CAND_H;\n"
 b"\t\tint hint_y = key_y + MATRIX_H + 4;\n"
 b"\t\tint ok_y   = hint_y + HINT_ROWS*(FONT_HEIGHT+4);",
 b"\t\tint HINT_ROWS = en_mode ? 1 : 2; //hint lines below keyboard\n"
 b"\t\t//Fixed frame: identical size/position on all pages (tallest = pinyin),\n"
 b"\t\t//so switching pages never moves the frame and no background leaks out.\n"
 b"\t\tint KEY_H = LINE_THICKNESS + 1 + FONT_HEIGHT*3 + 1 + LINE_THICKNESS\n"
 b"\t\t          + 8 + FONT_HEIGHT + 6      //pinyin/page label line\n"
 b"\t\t          + (3*32 + 8)               //candidate rows (reserved)\n"
 b"\t\t          + HFONTS*CELL_H + 4        //key matrix (tallest reserved)\n"
 b"\t\t          + 2*(FONT_HEIGHT+4)        //key hint lines (max reserved)\n"
 b"\t\t          + FONT_HEIGHT + 8 + LINE_THICKNESS; //OK line\n"
 b"\t\tint KEY_Y  = Menu_tooltip_y - 4 - KEY_H;  //sit above the bottom tooltip row\n"
 b"\t\tint out_y  = KEY_Y + LINE_THICKNESS + 1;\n"
 b"\t\tint py_y   = out_y + FONT_HEIGHT*3 + 1 + LINE_THICKNESS + 8;\n"
 b"\t\t//Bottom-anchored: OK row hugs the frame bottom on every page\n"
 b"\t\tint ok_y   = KEY_Y + KEY_H - LINE_THICKNESS - 8 - FONT_HEIGHT;\n"
 b"\t\tint hint_y = ok_y - HINT_ROWS*(FONT_HEIGHT+4);\n"
 b"\t\tint key_y  = hint_y - 4 - MATRIX_H;\n"
 b"\t\tint cand_y = key_y - 8 - 3*32;"),
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
    if b"CAND_H" in data:
        print("residual CAND_H, ABORT")
        sys.exit(1)
    with open(SRC, "wb") as f:
        f.write(data)
    print("written, 0xFF preserved: %d" % n_ff)


if __name__ == "__main__":
    main()
