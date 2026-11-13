# -*- coding: utf-8 -*-
"""
fix_kb_round4.py - keyboard() 三页输入改造 (byte-level, filer.c 含 0xFF 不可用文本编辑器)

1. en_mode 三态: 0=拼音 1=常用字 2=英文/符号, SELECT 循环切换
2. 常用字页: cn_com_codes 13x6 网格, L1/R1 翻页, ○ 直接上屏
3. 网格页(常用字/英文)布局紧凑化: 跳过候选区(3*32+8), 框上移露出背景标题
"""
import sys

SRC = r"K:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\filer.c"

# (old, new) 每个锚点必须恰好出现一次
FIXES = [
# P1: 常用字网格尺寸常量
(b"\t\t\tEN_W=13, EN_H=6,        //EN/symbol grid, one page, 78 cells\n"
 b"\t\t\tCELL_W=28, CELL_H=28,   //qwerty cell (24px full-width glyph)",
 b"\t\t\tEN_W=13, EN_H=6,        //EN/symbol grid, one page, 78 cells\n"
 b"\t\t\tCOM_W=13, COM_H=6,      //common-char grid, 78 cells per page\n"
 b"\t\t\tCELL_W=28, CELL_H=28,   //qwerty cell (24px full-width glyph)\n"
 b"\t\t\tCOM_CELL=28,            //common-char cell (24px glyph)"),

# P2: 常用字网格起点
(b"\t\t\tCAND_X0 = ((SCREEN_WIDTH - (9*28-4))/2) & -2; //candidate rows, centred",
 b"\t\t\tCOM_X0 = KEY_X + (KEY_W - COM_W*COM_CELL)/2,  //common grid, centred\n"
 b"\t\t\tCAND_X0 = ((SCREEN_WIDTH - (9*28-4))/2) & -2; //candidate rows, centred"),

# P3: en_mode 三态 + 常用字页码
(b"\tint en_mode=0; //0=pinyin qwerty, 1=EN/symbol full-width grid",
 b"\tint en_mode=0; //0=pinyin qwerty, 1=common chars, 2=EN/symbol full-width grid\n"
 b"\tint com_page=0; //page index within the common-char grid"),

# P4: 布局块 - 网格页跳过候选区
(b"\t\tint GW = en_mode ? EN_W : WFONTS;  //active grid width\n"
 b"\t\tint GH = en_mode ? EN_H : HFONTS;  //active grid height\n"
 b"\t\tint NK = GW*GH;                    //active grid cells\n"
 b"\t\t//Dynamic layout: one big frame holds name/pinyin/candidates/keys/OK.\n"
 b"\t\t//Frame height adapts to the active grid and hugs the screen bottom.\n"
 b"\t\tint MATRIX_H = en_mode ? EN_H*EN_SCELL : HFONTS*CELL_H;\n"
 b"\t\tint HINT_ROWS = en_mode ? 1 : 2; //hint lines below keyboard\n"
 b"\t\tint KEY_H = LINE_THICKNESS + 1 + FONT_HEIGHT*3 + 1 + LINE_THICKNESS\n"
 b"\t\t          + 8 + FONT_HEIGHT + 6      //pinyin line\n"
 b"\t\t          + 3*32 + 8                 //candidates: 3 rows\n"
 b"\t\t          + MATRIX_H + 4             //key matrix\n"
 b"\t\t          + HINT_ROWS*(FONT_HEIGHT+4) //key hint lines\n"
 b"\t\t          + FONT_HEIGHT + 8 + LINE_THICKNESS; //OK line",
 b"\t\tint GW = (en_mode == 2) ? EN_W : (en_mode ? COM_W : WFONTS);\n"
 b"\t\tint GH = (en_mode == 2) ? EN_H : (en_mode ? COM_H : HFONTS);\n"
 b"\t\tint NK = GW*GH;                    //active grid cells\n"
 b"\t\t//Dynamic layout: one big frame holds name/pinyin/candidates/keys/OK.\n"
 b"\t\t//Frame height adapts to the active grid and hugs the screen bottom.\n"
 b"\t\t//Grid modes (common/EN) skip the candidate rows so the frame stays\n"
 b"\t\t//compact and the page title behind it stays visible.\n"
 b"\t\tint MATRIX_H = (en_mode == 2) ? EN_H*EN_SCELL\n"
 b"\t\t          : (en_mode ? COM_H*COM_CELL : HFONTS*CELL_H);\n"
 b"\t\tint HINT_ROWS = en_mode ? 1 : 2; //hint lines below keyboard\n"
 b"\t\tint CAND_H = en_mode ? 0 : (3*32 + 8); //candidates: 3 rows (pinyin only)\n"
 b"\t\tint KEY_H = LINE_THICKNESS + 1 + FONT_HEIGHT*3 + 1 + LINE_THICKNESS\n"
 b"\t\t          + 8 + FONT_HEIGHT + 6      //pinyin/page label line\n"
 b"\t\t          + CAND_H                   //candidates: 3 rows\n"
 b"\t\t          + MATRIX_H + 4             //key matrix\n"
 b"\t\t          + HINT_ROWS*(FONT_HEIGHT+4) //key hint lines\n"
 b"\t\t          + FONT_HEIGHT + 8 + LINE_THICKNESS; //OK line"),

# P5: 键盘区起点跟随 CAND_H
(b"\t\tint key_y  = cand_y + 3*32 + 8;",
 b"\t\tint key_y  = cand_y + CAND_H;"),

# P6: SELECT 三页循环
(b"\t\t\t}else if(new_pad & PAD_SELECT){     //SELECT => toggle EN/CN\n"
 b"\t\t\t\ten_mode ^= 1;\n"
 b"\t\t\t\tsel = 0;",
 b"\t\t\t}else if(new_pad & PAD_SELECT){     //SELECT => cycle PY->common->EN->PY\n"
 b"\t\t\t\ten_mode = (en_mode + 1) % 3;\n"
 b"\t\t\t\tsel = 0;\n"
 b"\t\t\t\tcom_page = 0;"),

# P7: L1 常用字翻页 + 拼音候选翻页
(b"\t\t\t}else if(new_pad & PAD_L1){\n"
 b"\t\t\t\tif(!en_mode && cand_total > 0){",
 b"\t\t\t}else if(new_pad & PAD_L1){\n"
 b"\t\t\t\tif(en_mode == 1 && com_page > 0){\n"
 b"\t\t\t\t\tcom_page--;\n"
 b"\t\t\t\t\tsel = 0;\n"
 b"\t\t\t\t}else if(!en_mode && cand_total > 0){"),

# P8: R1 常用字翻页 + 拼音候选翻页
(b"\t\t\t}else if(new_pad & PAD_R1){\n"
 b"\t\t\t\tif(!en_mode && cand_total > 0){",
 b"\t\t\t}else if(new_pad & PAD_R1){\n"
 b"\t\t\t\tif(en_mode == 1 && com_page < CN_COM_PAGES-1){\n"
 b"\t\t\t\t\tcom_page++;\n"
 b"\t\t\t\t\tsel = 0;\n"
 b"\t\t\t\t}else if(!en_mode && cand_total > 0){"),

# P9: ○ 上屏 - 英文/常用字分支
(b"\t\t\t\tif(sel < NK){  //Any key in matrix selected ?\n"
 b"\t\t\t\t\tif(en_mode){  //commit selected full-width char\n"
 b"\t\t\t\t\t\tif(sel < CN_SYM_COUNT && (int)strlen(out)+2 < max){\n"
 b"\t\t\t\t\t\t\tmemmove(out+cur+2, out+cur, strlen(out)-cur+1);\n"
 b"\t\t\t\t\t\t\tout[cur]   = cn_sym_codes[sel] >> 8;\n"
 b"\t\t\t\t\t\t\tout[cur+1] = cn_sym_codes[sel] & 0xFF;\n"
 b"\t\t\t\t\t\t\tcur += 2;\n"
 b"\t\t\t\t\t\t}\n"
 b"\t\t\t\t\t}else{",
 b"\t\t\t\tif(sel < NK){  //Any key in matrix selected ?\n"
 b"\t\t\t\t\tif(en_mode == 2){  //commit selected full-width EN/symbol char\n"
 b"\t\t\t\t\t\tif(sel < CN_SYM_COUNT && (int)strlen(out)+2 < max){\n"
 b"\t\t\t\t\t\t\tmemmove(out+cur+2, out+cur, strlen(out)-cur+1);\n"
 b"\t\t\t\t\t\t\tout[cur]   = cn_sym_codes[sel] >> 8;\n"
 b"\t\t\t\t\t\t\tout[cur+1] = cn_sym_codes[sel] & 0xFF;\n"
 b"\t\t\t\t\t\t\tcur += 2;\n"
 b"\t\t\t\t\t\t}\n"
 b"\t\t\t\t\t}else if(en_mode == 1){  //commit selected common char\n"
 b"\t\t\t\t\t\ti = com_page*COM_W*COM_H + sel;\n"
 b"\t\t\t\t\t\tif(i < CN_COM_COUNT && (int)strlen(out)+2 < max){\n"
 b"\t\t\t\t\t\t\tmemmove(out+cur+2, out+cur, strlen(out)-cur+1);\n"
 b"\t\t\t\t\t\t\tout[cur]   = cn_com_codes[i] >> 8;\n"
 b"\t\t\t\t\t\t\tout[cur+1] = cn_com_codes[i] & 0xFF;\n"
 b"\t\t\t\t\t\t\tcur += 2;\n"
 b"\t\t\t\t\t\t}\n"
 b"\t\t\t\t\t}else{"),

# P10: 页标签行 - 常用字页标签 + 页码
(b"\t\t\tif(en_mode){\n"
 b"\t\t\t\tprintXY(UIT_KB_ENPAGE, KEY_X+LINE_THICKNESS+3, py_y, setting->color[3], TRUE, 0);\n"
 b"\t\t\t}else{",
 b"\t\t\tif(en_mode == 2){\n"
 b"\t\t\t\tprintXY(UIT_KB_ENPAGE, KEY_X+LINE_THICKNESS+3, py_y, setting->color[3], TRUE, 0);\n"
 b"\t\t\t}else if(en_mode == 1){\n"
 b"\t\t\t\tprintXY(UIT_KB_COM_PAGE, KEY_X+LINE_THICKNESS+3, py_y, setting->color[3], TRUE, 0);\n"
 b"\t\t\t\tsprintf(tmp, \"%d/%d\", com_page+1, CN_COM_PAGES);\n"
 b"\t\t\t\tprintXY(tmp, KEY_X+KEY_W-LINE_THICKNESS-13*FONT_WIDTH,\n"
 b"\t\t\t\t\tpy_y, setting->color[3], TRUE, 0);\n"
 b"\t\t\t}else{"),

# P11: 键盘矩阵 - 分支条件
(b"\t\t\tif(en_mode){\n"
 b"\t\t\t\tfor(i = 0; i < EN_W*EN_H; i++){",
 b"\t\t\tif(en_mode == 2){\n"
 b"\t\t\t\tfor(i = 0; i < EN_W*EN_H; i++){"),

# P12: 键盘矩阵 - 常用字网格渲染
(b"\t\t\t\t\t\t\tkey_y + (i/EN_W)*EN_SCELL, setting->color[3], 28);\n"
 b"\t\t\t\t}\n"
 b"\t\t\t}else{",
 b"\t\t\t\t\t\t\tkey_y + (i/EN_W)*EN_SCELL, setting->color[3], 28);\n"
 b"\t\t\t\t}\n"
 b"\t\t\t}else if(en_mode == 1){\n"
 b"\t\t\t\tfor(i = 0; i < COM_W*COM_H; i++){\n"
 b"\t\t\t\t\tint ci = com_page*COM_W*COM_H + i;\n"
 b"\t\t\t\t\tconst unsigned char *g = (ci < CN_COM_COUNT)\n"
 b"\t\t\t\t\t\t? cn_font_find(cn_com_codes[ci]) : NULL;\n"
 b"\t\t\t\t\tif(g)\n"
 b"\t\t\t\t\t\tdrawChar16s(g,\n"
 b"\t\t\t\t\t\t\tCOM_X0 + (i%COM_W)*COM_CELL,\n"
 b"\t\t\t\t\t\t\tkey_y + (i/COM_W)*COM_CELL, setting->color[3], 24);\n"
 b"\t\t\t\t}\n"
 b"\t\t\t}else{"),

# P13: 按键说明行 - 三态选择
(b"\t\t\tprintXY(en_mode ? UIT_KB_EN_HINT : UIT_KB_HINT1,",
 b"\t\t\tprintXY(en_mode == 2 ? UIT_KB_EN_HINT\n"
 b"\t\t\t\t: (en_mode ? UIT_KB_COM_HINT : UIT_KB_HINT1),"),

# P14: 光标 x 定位
(b"\t\t\tif(en_mode)\n"
 b"\t\t\t\tx = EN_X0 + (sel%EN_W)*EN_SCELL - 6;\n"
 b"\t\t\telse\n"
 b"\t\t\t\tx = QW_X + (sel%WFONTS)*CELL_W + (CELL_W-24)/2 - 8;",
 b"\t\t\tif(en_mode == 2)\n"
 b"\t\t\t\tx = EN_X0 + (sel%EN_W)*EN_SCELL - 6;\n"
 b"\t\t\telse if(en_mode == 1)\n"
 b"\t\t\t\tx = COM_X0 + (sel%COM_W)*COM_CELL + (COM_CELL-24)/2 - 8;\n"
 b"\t\t\telse\n"
 b"\t\t\t\tx = QW_X + (sel%WFONTS)*CELL_W + (CELL_W-24)/2 - 8;"),

# P15: 光标 y 定位
(b"\t\t\tif(sel < NK){\n"
 b"\t\t\t\tif(en_mode)\n"
 b"\t\t\t\t\ty = key_y + (sel/EN_W)*EN_SCELL;\n"
 b"\t\t\t\telse\n"
 b"\t\t\t\t\ty = key_y + (sel/WFONTS)*CELL_H;",
 b"\t\t\tif(sel < NK){\n"
 b"\t\t\t\tif(en_mode == 2)\n"
 b"\t\t\t\t\ty = key_y + (sel/EN_W)*EN_SCELL;\n"
 b"\t\t\t\telse if(en_mode == 1)\n"
 b"\t\t\t\t\ty = key_y + (sel/COM_W)*COM_CELL;\n"
 b"\t\t\t\telse\n"
 b"\t\t\t\t\ty = key_y + (sel/WFONTS)*CELL_H;"),
]


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    n_ff_before = data.count(b"\xff")

    for idx, (old, new) in enumerate(FIXES, 1):
        cnt = data.count(old)
        if cnt != 1:
            print("P%d: anchor count=%d (expect 1), ABORT" % (idx, cnt))
            sys.exit(1)
        data = data.replace(old, new)
        print("P%d ok (+%d bytes)" % (idx, len(new) - len(old)))

    n_ff_after = data.count(b"\xff")
    if n_ff_after != n_ff_before:
        print("0xFF byte count changed %d -> %d, ABORT" % (n_ff_before, n_ff_after))
        sys.exit(1)
    with open(SRC, "wb") as f:
        f.write(data)
    print("written, 0xFF bytes preserved: %d" % n_ff_after)


if __name__ == "__main__":
    main()
