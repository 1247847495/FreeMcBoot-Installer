# -*- coding: utf-8 -*-
"""fix_i18n_syntax.py - 修复 apply_i18n.py 产生的非法宏拼接行
错误模式: sprintf(c, "..SELECT:" UIT_X ", UIT_A, UIT_B);  (未闭合引号)
正确写法: sprintf(c, "..SELECT:%s", UIT_A, UIT_B, UIT_X);
"""
import io
import sys

CONFIG = r"..\config.c"
Y = "\xff"

# (old, new, expected_count)
FIXES = [
    ('sprintf(c, "' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s SELECT:" UIT_SET_SPECIAL " START:" UIT_RUN, UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC);',
     'sprintf(c, "' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s SELECT:%s START:%s", UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC, UIT_SET_SPECIAL, UIT_RUN);', 1),
    ('sprintf(c, "' + Y + '0:%s ' + Y + '1:%s ' + Y + '2:%s SELECT:Set special START:Run", "Browse", "Clear", "Map to any MC");',
     'sprintf(c, "' + Y + '0:%s ' + Y + '1:%s ' + Y + '2:%s SELECT:%s START:%s", UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC, UIT_SET_SPECIAL, UIT_RUN);', 1),
    ('sprintf(c, "' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s SELECT:" UIT_SET_SPECIAL ", UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC);',
     'sprintf(c, "' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s SELECT:%s", UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC, UIT_SET_SPECIAL);', 1),
    ('sprintf(c, "' + Y + '0:%s ' + Y + '1:%s ' + Y + '2:%s SELECT:Set special", "Browse", "Clear", "Map to any MC");',
     'sprintf(c, "' + Y + '0:%s ' + Y + '1:%s ' + Y + '2:%s SELECT:%s", UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC, UIT_SET_SPECIAL);', 1),
    ('sprintf(c, "' + Y + '1:%s ' + Y + '0:%s SELECT:" UIT_SET_DEFAULT ", UIT_ADD, UIT_SUBTRACT);',
     'sprintf(c, "' + Y + '1:%s ' + Y + '0:%s SELECT:%s", UIT_ADD, UIT_SUBTRACT, UIT_SET_DEFAULT);', 2),
    ('sprintf(c, "' + Y + '0:%s ' + Y + '1:%s SELECT:" UIT_SET_DEFAULT ", UIT_ADD, UIT_SUBTRACT);',
     'sprintf(c, "' + Y + '0:%s ' + Y + '1:%s SELECT:%s", UIT_ADD, UIT_SUBTRACT, UIT_SET_DEFAULT);', 2),
    ('sprintf(c, "' + Y + '1:%s ' + Y + '0:%s SELECT:" UIT_SET_DEFAULT ", UIT_TYPE, UIT_CLEAR);',
     'sprintf(c, "' + Y + '1:%s ' + Y + '0:%s SELECT:%s", UIT_TYPE, UIT_CLEAR, UIT_SET_DEFAULT);', 1),
    ('sprintf(c, "' + Y + '0:%s ' + Y + '1:%s SELECT:" UIT_SET_DEFAULT ", UIT_TYPE, UIT_CLEAR);',
     'sprintf(c, "' + Y + '0:%s ' + Y + '1:%s SELECT:%s", UIT_TYPE, UIT_CLEAR, UIT_SET_DEFAULT);', 1),
    ('sprintf(c, "' + Y + '1:%s SELECT:" UIT_ALL_DEFAULT ", UIT_OK);',
     'sprintf(c, "' + Y + '1:%s SELECT:%s", UIT_OK, UIT_ALL_DEFAULT);', 1),
    ('sprintf(c, "' + Y + '0:%s SELECT:" UIT_ALL_DEFAULT ", UIT_OK);',
     'sprintf(c, "' + Y + '0:%s SELECT:%s", UIT_OK, UIT_ALL_DEFAULT);', 1),
]


def main():
    with io.open(CONFIG, "r", encoding="latin-1", newline="") as f:
        text = f.read()
    errors = 0
    for old, new, cnt in FIXES:
        found = text.count(old)
        if found != cnt:
            print("MISMATCH (expect %d, found %d): %r" % (cnt, found, old[:60]))
            errors += 1
            continue
        text = text.replace(old, new)
    if errors:
        print("FAILED: %d mismatches, file not written" % errors)
        sys.exit(1)
    with io.open(CONFIG, "w", encoding="latin-1", newline="") as f:
        f.write(text)
    print("OK: all syntax fixes applied")


if __name__ == "__main__":
    main()
