# -*- coding: utf-8 -*-
r"""
apply_i18n.py - 把 config.c 中的英文 UI 字符串替换为 ui_text.h 中的中文宏

处理方式: 以 latin-1 读入(0xFF 图标字符 'ÿ' 原样保留)，按精确子串替换并
断言每个替换的出现次数，防止误替换。重复运行前请还原 config.c。
"""
import io
import sys

CONFIG = r"..\config.c"

Y = "\xff"  # 'ÿ' 图标字符 (0xFF)，保持原样不动

# (旧子串, 新子串, 期望次数)
REPLACEMENTS = [
    # ---- 消息 (saveFmcbCNF / loadConfig_fmcb / setLK) ----
    ('sprintf(fmcbMsg, "Failed to open %s", icon_path);',
     'sprintf(fmcbMsg, UIT_FAIL_OPEN_FMT, icon_path);', 2),
    ('sprintf(fmcbMsg, "Failed to write %s", icon_path);',
     'sprintf(fmcbMsg, UIT_FAIL_WRITE_FMT, icon_path);', 2),
    ('sprintf(fmcbMsg, "Failed to open %s", cnf_path);',
     'sprintf(fmcbMsg, UIT_FAIL_OPEN_FMT, cnf_path);', 1),
    ('sprintf(fmcbMsg, "Failed to write %s", cnf_path);',
     'sprintf(fmcbMsg, UIT_FAIL_WRITE_FMT, cnf_path);', 1),
    ('sprintf(fmcbMsg, "Saved %s", CNF);',
     'sprintf(fmcbMsg, UIT_SAVED_FMT, CNF);', 1),
    ('sprintf(fmcbMsg, "Failed to load %s", path);',
     'sprintf(fmcbMsg, UIT_FAIL_LOAD_FMT, path);', 1),
    ('sprintf(fmcbMsg, "Loaded %s", path);',
     'sprintf(fmcbMsg, UIT_LOADED_FMT, path);', 1),
    ('sprintf(fmcbMsg, "Incompatible path selected");',
     'sprintf(fmcbMsg, UIT_INCOMPATIBLE);', 3),
    # ---- Config_fmcb_key ----
    ('sprintf(c, "E%d Button Settings", LKN);',
     'sprintf(c, UIT_E_KEY_SETTINGS_FMT, LKN);', 1),
    # ---- Config_fmcb_OSDSYS_item ----
    ('sprintf(title_tmp, "Item %d Settings", item+1);',
     'sprintf(title_tmp, UIT_ITEM_SETTINGS_FMT, item+1);', 1),
    ('sprintf(c, "  Name: %s", fmcb->OSD_Name[item]);',
     'sprintf(c, UIT_NAME_FMT, fmcb->OSD_Name[item]);', 1),
    # ---- Config_fmcb_OSDSYS_scroll ----
    ('sprintf(title_tmp, "Scroll Settings");',
     'sprintf(title_tmp, UIT_SCROLL_SETTINGS);', 1),
    ('"Scroll Menu"', 'UIT_SCROLL_MENU', 2),
    ('"Displayed Items"', 'UIT_DISPLAYED_ITEMS', 1),
    ('"Menu y"', 'UIT_MENU_Y', 1),
    ('"Cursor Max Velocity"', 'UIT_CURSOR_VELOCITY', 1),
    ('"Cursor Acceleration"', 'UIT_CURSOR_ACCEL', 1),
    ('sprintf(c, "  Left Cursor: %s", fmcb->OSD_cursor[0]);',
     'sprintf(c, UIT_LEFT_CURSOR_FMT, fmcb->OSD_cursor[0]);', 1),
    ('sprintf(c, "  Rigth Cursor: %s", fmcb->OSD_cursor[1]);',
     'sprintf(c, UIT_RIGHT_CURSOR_FMT, fmcb->OSD_cursor[1]);', 1),
    ('sprintf(c, "  Top Delimiter: %s", fmcb->OSD_delimiter[0]);',
     'sprintf(c, UIT_TOP_DELIM_FMT, fmcb->OSD_delimiter[0]);', 1),
    ('sprintf(c, "  Bottom Delimiter: %s", fmcb->OSD_delimiter[1]);',
     'sprintf(c, UIT_BOTTOM_DELIM_FMT, fmcb->OSD_delimiter[1]);', 1),
    # ---- OSD_overwrite ----
    ('sprintf(c, "Overwrite item %d?", item+1);',
     'sprintf(c, UIT_OVERWRITE_FMT, item+1);', 1),
    # ---- Config_fmcb_OSDSYS ----
    ('sprintf(c, "OSD Settings");',
     'sprintf(c, UIT_OSD_SETTINGS);', 1),
    ('sprintf(c, "  Configure Item %2d : %s", osd_item+1, fmcb->OSD_Name[osd_item]);',
     'sprintf(c, UIT_CFG_ITEM_FMT, osd_item+1, fmcb->OSD_Name[osd_item]);', 1),
    ('sprintf(c, "  Configure Scrolling Options");',
     'sprintf(c, UIT_CFG_SCROLL);', 1),
    ('"Video Mode"', 'UIT_VIDEO_MODE', 3),
    ('"Skip MC update check"', 'UIT_SKIP_MC_CHECK', 2),
    ('"Skip HDD update check"', 'UIT_SKIP_HDD_CHECK', 2),
    ('"Skip Disc Boot"', 'UIT_SKIP_DISC_BOOT', 2),
    ('"Skip Sony Logo"', 'UIT_SKIP_SONY_LOGO', 2),
    ('"Go to Browser"', 'UIT_GO_BROWSER', 2),
    ('sprintf(c, "  %s", "Selected Color");',
     'sprintf(c, "  %s", UIT_SELECTED_COLOR);', 1),
    ('sprintf(c, "  %s", "Unselected Color");',
     'sprintf(c, "  %s", UIT_UNSELECTED_COLOR);', 1),
    ('"Menu X"', 'UIT_MENU_X', 1),
    ('sprintf(c, "  %s", "Version");',
     'sprintf(c, "  %s", UIT_VERSION);', 1),
    # ---- Config_ESR_path ----
    ('sprintf(title_tmp, "ESR Path");',
     'sprintf(title_tmp, UIT_ESR_TITLE);', 1),
    # ---- select_swapkeys ----
    ('printXY("Select buttons layout",',
     'printXY(UIT_SELECT_LAYOUT,', 1),
    # ---- Config_fmcb 主菜单 ----
    ('strcpy(fmcbMsg, "All set to default");',
     'strcpy(fmcbMsg, UIT_ALL_DEFAULT);', 1),
    ('printXY("Free McBoot Settings", x, y,',
     'printXY(UIT_FMCB_SETTINGS, x, y,', 1),
    ('sprintf(c, "  %s", "Load CNF from MC0");',
     'sprintf(c, "  %s", UIT_LOAD_CNF_MC0);', 1),
    ('sprintf(c, "  %s", "Load CNF from MC1");',
     'sprintf(c, "  %s", UIT_LOAD_CNF_MC1);', 1),
    ('sprintf(c, "  %s", "Load CNF from Mass");',
     'sprintf(c, "  %s", UIT_LOAD_CNF_MASS);', 1),
    ('sprintf(c, "  %s...", "Configure E1 launch keys");',
     'sprintf(c, "  %s...", UIT_CFG_E1_KEYS);', 1),
    ('sprintf(c, "  %s...", "Configure E2 launch keys");',
     'sprintf(c, "  %s...", UIT_CFG_E2_KEYS);', 1),
    ('sprintf(c, "  %s...", "Configure E3 launch keys");',
     'sprintf(c, "  %s...", UIT_CFG_E3_KEYS);', 1),
    ('sprintf(c, "  %s...", "Configure OSDSYS options");',
     'sprintf(c, "  %s...", UIT_CFG_OSDSYS);', 1),
    ('sprintf(c, "  %s...", "Configure ESR Path");',
     'sprintf(c, "  %s...", UIT_CFG_ESR);', 1),
    ('"FastBoot"', 'UIT_FASTBOOT', 3),
    ('"Debug Screen"', 'UIT_DEBUG_SCREEN', 2),
    ('"Pad Delay"', 'UIT_PAD_DELAY', 1),
    ('sprintf(c, "  %s", "Save CNF to MC0");',
     'sprintf(c, "  %s", UIT_SAVE_CNF_MC0);', 1),
    ('sprintf(c, "  %s", "Save CNF to MC1");',
     'sprintf(c, "  %s", UIT_SAVE_CNF_MC1);', 1),
    ('sprintf(c, "  %s", "Save CNF to Mass");',
     'sprintf(c, "  %s", UIT_SAVE_CNF_MASS);', 1),
    ('sprintf(c, "  %s", "Return to loader");',
     'sprintf(c, "  %s", UIT_RETURN_TO_LOADER);', 1),
    ('sprintf(c, "  %s", "PS2 Browser (FMCB Restart)");',
     'sprintf(c, "  %s", UIT_PS2_BROWSER);', 1),
    ('sprintf(c, "  %s", "Return");',
     'sprintf(c, "  %s", UIT_RETURN);', 5),
    # ---- ON/OFF 值 ----
    (', "ON");', ', UIT_ON);', 9),
    (', "OFF");', ', UIT_OFF);', 9),
    # ---- 提示条(tooltip): 含 ÿ 图标字符的行，只换实参/内嵌英文 ----
    ('"' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s SELECT:Set special START:Run", "Browse", "Clear", "Map to any MC"',
     '"' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s SELECT:" UIT_SET_SPECIAL " START:" UIT_RUN, UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC', 1),
    ('"' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s SELECT:Set special", "Browse", "Clear", "Map to any MC"',
     '"' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s SELECT:" UIT_SET_SPECIAL ", UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC', 1),
    ('"' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s", "Browse", "Clear", "Map to any MC"',
     '"' + Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s", UIT_BROWSE, UIT_CLEAR, UIT_MAP_MC', 1),
    ('"' + Y + '1:%s ' + Y + '0:%s SELECT: set default", "Add", "Subtract"',
     '"' + Y + '1:%s ' + Y + '0:%s SELECT:" UIT_SET_DEFAULT ", UIT_ADD, UIT_SUBTRACT', 2),
    ('"' + Y + '0:%s ' + Y + '1:%s SELECT: set default", "Add", "Subtract"',
     '"' + Y + '0:%s ' + Y + '1:%s SELECT:" UIT_SET_DEFAULT ", UIT_ADD, UIT_SUBTRACT', 2),
    ('"' + Y + '1:%s ' + Y + '0:%s SELECT: set default", "Type", "Clear"',
     '"' + Y + '1:%s ' + Y + '0:%s SELECT:" UIT_SET_DEFAULT ", UIT_TYPE, UIT_CLEAR', 1),
    ('"' + Y + '0:%s ' + Y + '1:%s SELECT: set default", "Type", "Clear"',
     '"' + Y + '0:%s ' + Y + '1:%s SELECT:" UIT_SET_DEFAULT ", UIT_TYPE, UIT_CLEAR', 1),
    ('sprintf(c, "SELECT: set default");',
     'sprintf(c, "SELECT:" UIT_SET_DEFAULT);', 1),
    ('"' + Y + '1:%s SELECT:Set all default", "OK"',
     '"' + Y + '1:%s SELECT:" UIT_ALL_DEFAULT ", UIT_OK', 1),
    ('"' + Y + '0:%s SELECT:Set all default", "OK"',
     '"' + Y + '0:%s SELECT:" UIT_ALL_DEFAULT ", UIT_OK', 1),
    ('"' + Y + '1:%s ' + Y + '0:%s", "Type", "Clear"',
     '"' + Y + '1:%s ' + Y + '0:%s", UIT_TYPE, UIT_CLEAR', 1),
    ('"' + Y + '0:%s ' + Y + '1:%s", "Type", "Clear"',
     '"' + Y + '0:%s ' + Y + '1:%s", UIT_TYPE, UIT_CLEAR', 1),
    ('"' + Y + '1:%s ' + Y + '0:%s", "Add", "Subtract"',
     '"' + Y + '1:%s ' + Y + '0:%s", UIT_ADD, UIT_SUBTRACT', 1),
    ('"' + Y + '0:%s ' + Y + '1:%s", "Add", "Subtract"',
     '"' + Y + '0:%s ' + Y + '1:%s", UIT_ADD, UIT_SUBTRACT', 1),
    ('"' + Y + '1:%s", "Change"', '"' + Y + '1:%s", UIT_CHANGE', 3),
    ('"' + Y + '0:%s", "Change"', '"' + Y + '0:%s", UIT_CHANGE', 3),
    ('"' + Y + '1:%s", "OK"', '"' + Y + '1:%s", UIT_OK', 6),
    ('"' + Y + '0:%s", "OK"', '"' + Y + '0:%s", UIT_OK', 6),
    ('" ' + Y + '3:%s", "Return"', '" ' + Y + '3:%s", UIT_RETURN', 6),
]


def main():
    with io.open(CONFIG, "r", encoding="latin-1", newline="") as f:
        text = f.read()

    errors = 0
    total = 0
    for old, new, count in REPLACEMENTS:
        found = text.count(old)
        if found != count:
            print("MISMATCH (expect %d, found %d): %r" % (count, found, old[:70]))
            errors += 1
            continue
        text = text.replace(old, new)
        total += count

    # 插入 #include "ui_text.h" (跟随文件行尾风格)
    eol = "\r\n" if "\r\n#include <stdbool.h>\r\n" in text else "\n"
    anchor = "#include <stdbool.h>"
    if text.count(anchor) != 1:
        print("FAILED: #include <stdbool.h> 出现次数异常")
        sys.exit(1)
    text = text.replace(anchor, anchor + eol + '#include "ui_text.h"')

    if errors:
        print("FAILED: %d 处替换不匹配，未写入文件" % errors)
        sys.exit(1)

    with io.open(CONFIG, "w", encoding="latin-1", newline="") as f:
        f.write(text)
    print("OK: %d 组替换规则, 共 %d 处替换 + 1 处 include, 已写入 %s"
          % (len(REPLACEMENTS), total, CONFIG))


if __name__ == "__main__":
    main()
