# -*- coding: utf-8 -*-
"""fix_i18n_round3.py
config.c:
  1. 中文菜单光标公式与 18px 行距同步
  2. Path1/2/3 标签汉化 (item 页 + ESR 页)
filer.c:
  3. 输入法界面汉化: PY:/SELECT:EN/EN页提示/OK/Cancel
  4. hint 行改两行完整中文按键说明
launchelf.h: include ui_text.h
"""
import io
import re
import sys

BASE = r".."
CONFIG = BASE + r"\config.c"
FILER = BASE + r"\filer.c"
LH = BASE + r"\launchelf.h"

CN_FUNCS = [
    "Config_fmcb_key", "Config_fmcb_OSDSYS", "Config_fmcb_OSDSYS_item",
    "Config_fmcb_OSDSYS_scroll", "Config_ESR_path", "Config_fmcb",
]
FUNC_RE = re.compile(r'^(int|void)\s+(\w+)\s*\(', re.M)


def patch_func_spacing(text):
    """CN_FUNCS 区间内同步光标公式行距"""
    marks = [(m.start(), m.group(2)) for m in FUNC_RE.finditer(text)]
    marks.append((len(text), "_EOF_"))
    rules = [
        ("y = Menu_start_y + s*FONT_HEIGHT + FONT_HEIGHT /2;",
         "y = Menu_start_y + s*(FONT_HEIGHT + 2) + FONT_HEIGHT /2;"),
        ("y = Menu_start_y + s*FONT_HEIGHT + FONT_HEIGHT/2;",
         "y = Menu_start_y + s*(FONT_HEIGHT + 2) + FONT_HEIGHT/2;"),
        ("y = Menu_start_y + (s+1)*FONT_HEIGHT;",
         "y = Menu_start_y + (s+1)*(FONT_HEIGHT + 2);"),
        ("y = Menu_start_y + (s+1)*FONT_HEIGHT + FONT_HEIGHT/2;",
         "y = Menu_start_y + (s+1)*(FONT_HEIGHT + 2) + FONT_HEIGHT/2;"),
    ]
    hits = 0
    out, prev = [], 0
    for i in range(len(marks) - 1):
        fstart, fname = marks[i]
        fend = marks[i + 1][0]
        out.append(text[prev:fstart])
        body = text[fstart:fend]
        if fname in CN_FUNCS:
            for old, new in rules:
                hits += body.count(old)
                body = body.replace(old, new)
        out.append(body)
        prev = fend
    out.append(text[prev:])
    return "".join(out), hits


def main():
    # ---------- config.c ----------
    with io.open(CONFIG, "r", encoding="latin-1", newline="") as f:
        cfg = f.read()

    cfg, n_cursor = patch_func_spacing(cfg)

    path_fixes = 0
    for n in "123":
        old = 'sprintf(c, "  Path%s: %%s", ' % n
        new = 'sprintf(c, "  " UIT_PATH%s " %%s", ' % n
        k = cfg.count(old)
        path_fixes += k
        cfg = cfg.replace(old, new)
    if path_fixes != 6:
        print("WARN: Path fixes = %d (expect 6)" % path_fixes)

    with io.open(CONFIG, "w", encoding="latin-1", newline="") as f:
        f.write(cfg)
    print("config.c: %d cursor formulas synced, %d Path labels" % (n_cursor, path_fixes))

    # ---------- filer.c ----------
    with io.open(FILER, "r", encoding="latin-1", newline="") as f:
        fil = f.read()

    fixes = [
        # PY 行 + SELECT:EN
        ('sprintf(tmp, "PY: %s_", py);',
         'sprintf(tmp, UIT_KB_PY " %s_", py);', 1),
        ('printXY("SELECT:EN", KEY_X+KEY_W-LINE_THICKNESS-10*FONT_WIDTH,',
         'printXY(UIT_KB_SELEN, KEY_X+KEY_W-LINE_THICKNESS-13*FONT_WIDTH,', 1),
        ('printXY("EN/SYM   SELECT:Chinese", KEY_X+LINE_THICKNESS+3, py_y,',
         'printXY(UIT_KB_ENPAGE, KEY_X+LINE_THICKNESS+3, py_y,', 1),
        # OK / Cancel
        ('printXY("OK",', 'printXY(UIT_OK,', 1),
        ('printXY("Cancel",', 'printXY(UIT_CANCEL,', 1),
        ('KEY_X + KEY_W - 1 - (strlen("Cancel")+2)*FONT_WIDTH,',
         'KEY_X + KEY_W - 1 - 6*FONT_WIDTH,', 1),
        ('x = KEY_X + KEY_W - 2 - (strlen("Cancel")+3)*FONT_WIDTH;',
         'x = KEY_X + KEY_W - 2 - 7*FONT_WIDTH;', 1),
    ]
    # 布局与 hint 渲染: 用正则自适应缩进
    import re as _re
    layout_rules = [
        # KEY_H 块: 增加动态 hint 行数
        (r'(\t+)int KEY_H = LINE_THICKNESS \+ 1 \+ FONT_HEIGHT\*3 \+ 1 \+ LINE_THICKNESS\n'
         r'\1          \+ 8 \+ FONT_HEIGHT \+ 6      //pinyin line\n'
         r'\1          \+ 3\*32 \+ 8                 //candidates: 3 rows\n'
         r'\1          \+ MATRIX_H \+ 4             //key matrix\n'
         r'\1          \+ FONT_HEIGHT \+ 4          //key hint line\n'
         r'\1          \+ FONT_HEIGHT \+ 8 \+ LINE_THICKNESS; //OK line',
         lambda m: (m.group(1) + 'int HINT_ROWS = en_mode ? 1 : 2; //hint lines below keyboard\n'
                    + m.group(1) + 'int KEY_H = LINE_THICKNESS + 1 + FONT_HEIGHT*3 + 1 + LINE_THICKNESS\n'
                    + m.group(1) + '          + 8 + FONT_HEIGHT + 6      //pinyin line\n'
                    + m.group(1) + '          + 3*32 + 8                 //candidates: 3 rows\n'
                    + m.group(1) + '          + MATRIX_H + 4             //key matrix\n'
                    + m.group(1) + '          + HINT_ROWS*(FONT_HEIGHT+4) //key hint lines\n'
                    + m.group(1) + '          + FONT_HEIGHT + 8 + LINE_THICKNESS; //OK line')),
        # ok_y 跟随 hint 行数
        (r'(\t+)int ok_y   = hint_y \+ FONT_HEIGHT \+ 4;',
         lambda m: m.group(1) + 'int ok_y   = hint_y + HINT_ROWS*(FONT_HEIGHT+4);'),
        # hint 渲染: 两行完整中文
        (r'(\t+)//Key hint line between keyboard and OK row\n'
         r'\1\{\n'
         r'\1\tconst char \*hint = en_mode\n'
         r'\1\t\t\? "O:input SELECT:Chinese"\n'
         r'\1\t\t: "O:type \[\]:commit L1/R1:page L2/R2:move";\n'
         r'\1\tint hx = KEY_X \+ \(KEY_W - \(int\)strlen\(hint\)\*FONT_WIDTH\)/2;\n'
         r'\1\tprintXY\(hint, hx, hint_y, setting->color\[2\], TRUE, 0\);\n'
         r'\1\}',
         lambda m: (m.group(1) + '//Key hint lines between keyboard and OK row (full Chinese guide)\n'
                    + m.group(1) + 'printXY(en_mode ? UIT_KB_EN_HINT : UIT_KB_HINT1,\n'
                    + m.group(1) + '\tKEY_X + LINE_THICKNESS + 3, hint_y, setting->color[2], TRUE, 0);\n'
                    + m.group(1) + 'if(!en_mode)\n'
                    + m.group(1) + '\tprintXY(UIT_KB_HINT2, KEY_X + LINE_THICKNESS + 3,\n'
                    + m.group(1) + '\t\thint_y + FONT_HEIGHT + 4, setting->color[2], TRUE, 0);')),
    ]
    errors = 0
    for old, new, cnt in fixes:
        found = fil.count(old)
        if found != cnt:
            print("MISMATCH filer.c (expect %d, found %d): %r" % (cnt, found, old[:60]))
            errors += 1
            continue
        fil = fil.replace(old, new)
    for pat, rep in layout_rules:
        fil, n = _re.subn(pat, rep, fil)
        if n != 1:
            print("MISMATCH layout rule (found %d): %s" % (n, pat[:60]))
            errors += 1
    if errors:
        print("FAILED: filer.c not written")
        sys.exit(1)
    with io.open(FILER, "w", encoding="latin-1", newline="") as f:
        f.write(fil)
    print("filer.c: %d fixes applied" % len(fixes))

    # ---------- launchelf.h ----------
    with io.open(LH, "r", encoding="latin-1", newline="") as f:
        lh = f.read()
    if 'ui_text.h' not in lh:
        anchor = '#include "launchelf.h"'
        # launchelf.h 自身不能 include 自己，找个稳妥位置: 文件开头版权块后
        m = re.search(r'(#include\s+<[^>]+>\s*)', lh)
        if m:
            lh = lh[:m.end()] + '\r\n#include "ui_text.h"' + lh[m.end():]
        else:
            lh = '#include "ui_text.h"\r\n' + lh
        with io.open(LH, "w", encoding="latin-1", newline="") as f:
            f.write(lh)
        print("launchelf.h: ui_text.h include added")
    else:
        print("launchelf.h: already includes ui_text.h")


if __name__ == "__main__":
    main()
