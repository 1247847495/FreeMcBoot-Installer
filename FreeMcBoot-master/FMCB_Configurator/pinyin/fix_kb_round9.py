# -*- coding: utf-8 -*-
"""
fix_kb_round9.py - 词组残留根因修复: 布局块移到手柄处理之后 (byte-level)

根因: key_y/MATRIX_H 等布局变量在循环顶部计算, SELECT 切页在手柄段才改
en_mode, 显示段用 [新 en_mode + 旧布局] 渲染一帧。拼音->词组切换时词组
网格按拼音页 key_y(低 112px) 画, 最后两行落到弹窗外的屏幕底部; GS 双缓冲
下这一帧永远留在另一个缓冲区, 之后任何页都擦不掉 -> 残影 "光盘启动/内置硬盘"。
修复: 布局块整体移到 pad response 之后、display section 之前,
切页后第一帧即用新页布局, 永远不会画到框外。
"""
import sys

SRC = r"K:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\filer.c"

OLD_BLOCK = (
    b"\t\t//Dynamic layout: one big frame holds name/pinyin/candidates/keys/OK.\n"
    b"\t\t//Frame height adapts to the active grid and hugs the screen bottom.\n"
    b"\t\t//Grid modes (common/EN) skip the candidate rows so the frame stays\n"
    b"\t\t//compact and the page title behind it stays visible.\n"
    b"\t\tint MATRIX_H = (en_mode == 2) ? EN_H*EN_SCELL\n"
    b"\t\t          : (en_mode ? COM_H*COM_CELL : HFONTS*CELL_H);\n"
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
    b"\t\tint hint_y = ok_y - 2*(FONT_HEIGHT+4); //fixed 2-row reserve, matches KEY_H\n"
    b"\t\tint key_y  = hint_y - 4 - MATRIX_H;\n"
    b"\t\tint cand_y = key_y - 8 - 3*32;\n"
)

NEW_BLOCK = (
    b"\t\t//Dynamic layout: one big frame holds name/pinyin/candidates/keys/OK.\n"
    b"\t\t//Computed AFTER pad handling and BEFORE the display section, so the\n"
    b"\t\t//first frame after a page switch already uses the new page layout.\n"
    b"\t\t//(The GS renders double-buffered: a single frame drawn outside the\n"
    b"\t\t//popup would linger on screen until the keyboard closes.)\n"
    b"\t\tint MATRIX_H = (en_mode == 2) ? EN_H*EN_SCELL\n"
    b"\t\t          : (en_mode ? COM_H*COM_CELL : HFONTS*CELL_H);\n"
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
    b"\t\tint hint_y = ok_y - 2*(FONT_HEIGHT+4); //fixed 2-row reserve, matches KEY_H\n"
    b"\t\tint key_y  = hint_y - 4 - MATRIX_H;\n"
    b"\t\tint cand_y = key_y - 8 - 3*32;\n"
    b"\n"
)

# unique anchor: our keyboard's display section (round-8 comment makes it unique)
ANCHOR = (b"if(t & 0x0F) event |= 4;  //repetitive timer event\n"
          b"\n"
          b"\t\tif(event||post_event){ //NB: We need to update two frame buffers per event\n"
          b"\n"
          b"\t\t\t//Display section\n"
          b"\t\t\t//One big frame holding everything")


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    n_ff = data.count(b"\xff")

    if data.count(OLD_BLOCK) != 1:
        print("layout block count=%d (expect 1), ABORT" % data.count(OLD_BLOCK))
        sys.exit(1)
    if data.count(ANCHOR) != 1:
        print("display anchor count=%d (expect 1), ABORT" % data.count(ANCHOR))
        sys.exit(1)

    # remove old block
    data = data.replace(OLD_BLOCK, b"")
    # insert new block: replace the full unique display anchor with
    # [timer line + new layout block + display section start]
    REPLACEMENT = (b"if(t & 0x0F) event |= 4;  //repetitive timer event\n"
                   b"\n"
                   + NEW_BLOCK +
                   b"\t\tif(event||post_event){ //NB: We need to update two frame buffers per event\n"
                   b"\n"
                   b"\t\t\t//Display section\n"
                   b"\t\t\t//One big frame holding everything")
    data = data.replace(ANCHOR, REPLACEMENT)

    # sanity
    if data.count(b"//Dynamic layout") != 1:
        print("new block placement failed, ABORT")
        sys.exit(1)
    if data.count(b"\xff") != n_ff:
        print("0xFF count changed, ABORT")
        sys.exit(1)
    # layout must now come after the SELECT handler
    if data.find(b"en_mode = (en_mode + 1) % 3") > data.find(b"//Dynamic layout"):
        print("layout still before SELECT handler, ABORT")
        sys.exit(1)

    with open(SRC, "wb") as f:
        f.write(data)
    print("written, 0xFF preserved: %d" % n_ff)


if __name__ == "__main__":
    main()
