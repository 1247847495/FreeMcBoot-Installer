# -*- coding: utf-8 -*-
"""
fix_kb_round5.py - 常用字页 -> 常用词组页 (byte-level, filer.c 含 0xFF 不可用文本编辑器)

词组表 cn_com_phrases（整词上屏），2列x7行一页放完14条：
- COM_W=2, COM_H=7, COM_COL_W=225, COM_CELL=24
- 移除 com_page 翻页（单页）
- ○ 提交整个词组字符串
- 渲染改 printXY 词组文本
"""
import sys

SRC = r"K:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\filer.c"

FIXES = [
# R1: 网格尺寸 -> 2列x7行
(b"\t\t\tCOM_W=13, COM_H=6,      //common-char grid, 78 cells per page\n",
 b"\t\t\tCOM_W=2, COM_H=7,       //phrase grid: 2 columns x 7 rows\n"),

# R2: 单元尺寸 -> 列宽/行高
(b"\t\t\tCOM_CELL=28,            //common-char cell (24px glyph)",
 b"\t\t\tCOM_COL_W=225, COM_CELL=24, //phrase column width / row height"),

# R3: 网格起点 -> 左对齐
(b"\t\t\tCOM_X0 = KEY_X + (KEY_W - COM_W*COM_CELL)/2,  //common grid, centred\n",
 b"\t\t\tCOM_X0 = KEY_X + LINE_THICKNESS + 12, //phrase list, left aligned\n"),

# R4: 删除 com_page 变量
(b"\tint en_mode=0; //0=pinyin qwerty, 1=common chars, 2=EN/symbol full-width grid\n"
 b"\tint com_page=0; //page index within the common-char grid",
 b"\tint en_mode=0; //0=pinyin qwerty, 1=common phrases, 2=EN/symbol full-width grid"),

# R5: SELECT 切换移除 com_page 复位
(b"\t\t\t\ten_mode = (en_mode + 1) % 3;\n"
 b"\t\t\t\tsel = 0;\n"
 b"\t\t\t\tcom_page = 0;",
 b"\t\t\t\ten_mode = (en_mode + 1) % 3;\n"
 b"\t\t\t\tsel = 0;"),

# R6: L1 恢复仅拼音候选翻页
(b"\t\t\t\tif(en_mode == 1 && com_page > 0){\n"
 b"\t\t\t\t\tcom_page--;\n"
 b"\t\t\t\t\tsel = 0;\n"
 b"\t\t\t\t}else if(!en_mode && cand_total > 0){",
 b"\t\t\t\tif(!en_mode && cand_total > 0){"),

# R7: R1 恢复仅拼音候选翻页
(b"\t\t\t\tif(en_mode == 1 && com_page < CN_COM_PAGES-1){\n"
 b"\t\t\t\t\tcom_page++;\n"
 b"\t\t\t\t\tsel = 0;\n"
 b"\t\t\t\t}else if(!en_mode && cand_total > 0){",
 b"\t\t\t\tif(!en_mode && cand_total > 0){"),

# R8: ○ 提交整个词组
(b"\t\t\t\t\t}else if(en_mode == 1){  //commit selected common char\n"
 b"\t\t\t\t\t\ti = com_page*COM_W*COM_H + sel;\n"
 b"\t\t\t\t\t\tif(i < CN_COM_COUNT && (int)strlen(out)+2 < max){\n"
 b"\t\t\t\t\t\t\tmemmove(out+cur+2, out+cur, strlen(out)-cur+1);\n"
 b"\t\t\t\t\t\t\tout[cur]   = cn_com_codes[i] >> 8;\n"
 b"\t\t\t\t\t\t\tout[cur+1] = cn_com_codes[i] & 0xFF;\n"
 b"\t\t\t\t\t\t\tcur += 2;\n"
 b"\t\t\t\t\t\t}\n"
 b"\t\t\t\t\t}else{",
 b"\t\t\t\t\t}else if(en_mode == 1){  //commit selected common phrase\n"
 b"\t\t\t\t\t\tif(sel < CN_COM_COUNT){\n"
 b"\t\t\t\t\t\t\tconst char *ph = cn_com_phrases[sel];\n"
 b"\t\t\t\t\t\t\tint n = strlen(ph);\n"
 b"\t\t\t\t\t\t\tif((int)strlen(out)+n < max){\n"
 b"\t\t\t\t\t\t\t\tmemmove(out+cur+n, out+cur, strlen(out)-cur+1);\n"
 b"\t\t\t\t\t\t\t\tmemcpy(out+cur, ph, n);\n"
 b"\t\t\t\t\t\t\t\tcur += n;\n"
 b"\t\t\t\t\t\t\t}\n"
 b"\t\t\t\t\t\t}\n"
 b"\t\t\t\t\t}else{"),

# R9: 页标签去掉页码
(b"\t\t\t}else if(en_mode == 1){\n"
 b"\t\t\t\tprintXY(UIT_KB_COM_PAGE, KEY_X+LINE_THICKNESS+3, py_y, setting->color[3], TRUE, 0);\n"
 b"\t\t\t\tsprintf(tmp, \"%d/%d\", com_page+1, CN_COM_PAGES);\n"
 b"\t\t\t\tprintXY(tmp, KEY_X+KEY_W-LINE_THICKNESS-13*FONT_WIDTH,\n"
 b"\t\t\t\t\tpy_y, setting->color[3], TRUE, 0);\n"
 b"\t\t\t}else{",
 b"\t\t\t}else if(en_mode == 1){\n"
 b"\t\t\t\tprintXY(UIT_KB_COM_PAGE, KEY_X+LINE_THICKNESS+3, py_y, setting->color[3], TRUE, 0);\n"
 b"\t\t\t}else{"),

# R10: 渲染 -> printXY 词组列表
(b"\t\t\t}else if(en_mode == 1){\n"
 b"\t\t\t\tfor(i = 0; i < COM_W*COM_H; i++){\n"
 b"\t\t\t\t\tint ci = com_page*COM_W*COM_H + i;\n"
 b"\t\t\t\t\tconst unsigned char *g = (ci < CN_COM_COUNT)\n"
 b"\t\t\t\t\t\t? cn_font_find(cn_com_codes[ci]) : NULL;\n"
 b"\t\t\t\t\tif(g)\n"
 b"\t\t\t\t\t\tdrawChar16s(g,\n"
 b"\t\t\t\t\t\t\tCOM_X0 + (i%COM_W)*COM_CELL,\n"
 b"\t\t\t\t\t\t\tkey_y + (i/COM_W)*COM_CELL, setting->color[3], 24);\n"
 b"\t\t\t\t}\n"
 b"\t\t\t}else{",
 b"\t\t\t}else if(en_mode == 1){\n"
 b"\t\t\t\tfor(i = 0; i < COM_W*COM_H && i < CN_COM_COUNT; i++)\n"
 b"\t\t\t\t\tprintXY(cn_com_phrases[i],\n"
 b"\t\t\t\t\t\tCOM_X0 + (i%COM_W)*COM_COL_W,\n"
 b"\t\t\t\t\t\tkey_y + (i/COM_W)*COM_CELL,\n"
 b"\t\t\t\t\t\tsetting->color[3], TRUE, 0);\n"
 b"\t\t\t}else{"),

# R11: 光标 x 按列宽定位
(b"\t\t\t\tx = COM_X0 + (sel%COM_W)*COM_CELL + (COM_CELL-24)/2 - 8;",
 b"\t\t\t\tx = COM_X0 + (sel%COM_W)*COM_COL_W - 8;"),
]


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    n_ff = data.count(b"\xff")

    for idx, (old, new) in enumerate(FIXES, 1):
        cnt = data.count(old)
        if cnt != 1:
            print("R%d: anchor count=%d (expect 1), ABORT" % (idx, cnt))
            sys.exit(1)
        data = data.replace(old, new)
        print("R%d ok" % idx)

    if data.count(b"\xff") != n_ff:
        print("0xFF count changed, ABORT")
        sys.exit(1)
    # 不应残留旧符号
    for bad in (b"com_page", b"cn_com_codes", b"CN_COM_PAGES"):
        if bad in data:
            print("residual %r, ABORT" % bad)
            sys.exit(1)
    with open(SRC, "wb") as f:
        f.write(data)
    print("written, 0xFF preserved: %d" % n_ff)


if __name__ == "__main__":
    main()
