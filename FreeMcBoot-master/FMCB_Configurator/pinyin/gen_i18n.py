#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
gen_i18n.py - 为 FMCB Configurator 生成中文 UI 字符串头文件 ui_text.h

用法: python gen_i18n.py
  1. 校验所有中文用字均存在于 charset.txt (JIS X0208 字集)
  2. 生成 ../ui_text.h，每个中文按 Shift-JIS 编码写成 "\xNN\xNN" 转义
约束: JIS X0208 无简体字形，只能用日文字形汉字 (設定/確認/閲覧...)。
"""

import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CHARSET_FILE = os.path.join(BASE, "charset.txt")
OUT_FILE = os.path.join(BASE, "..", "ui_text.h")

# (宏名, 英文原文, 中文文本)
TERMS = [
    # ---- 主菜单 (Config_fmcb) ----
    ("UIT_FMCB_SETTINGS",     "Free McBoot Settings",          "FMCB設定"),
    ("UIT_LOAD_CNF_MC0",      "Load CNF from MC0",             "載入MC0的CNF"),
    ("UIT_LOAD_CNF_MC1",      "Load CNF from MC1",             "載入MC1的CNF"),
    ("UIT_LOAD_CNF_MASS",     "Load CNF from Mass",            "載入USB的CNF"),
    ("UIT_CFG_E1_KEYS",       "Configure E1 launch keys",      "設定E1起動鍵"),
    ("UIT_CFG_E2_KEYS",       "Configure E2 launch keys",      "設定E2起動鍵"),
    ("UIT_CFG_E3_KEYS",       "Configure E3 launch keys",      "設定E3起動鍵"),
    ("UIT_CFG_OSDSYS",        "Configure OSDSYS options",      "設定OSDSYS選項"),
    ("UIT_CFG_ESR",           "Configure ESR Path",            "設定ESR路径"),
    ("UIT_FASTBOOT",          "FastBoot",                       "快速起動"),
    ("UIT_ON",                "ON",                             "開"),
    ("UIT_OFF",               "OFF",                            "閉"),
    ("UIT_DEBUG_SCREEN",      "Debug Screen",                   "除錯画面"),
    ("UIT_PAD_DELAY",         "Pad Delay",                      "手柄延時"),
    ("UIT_SAVE_CNF_MC0",      "Save CNF to MC0",                "保存CNF到MC0"),
    ("UIT_SAVE_CNF_MC1",      "Save CNF to MC1",                "保存CNF到MC1"),
    ("UIT_SAVE_CNF_MASS",     "Save CNF to Mass",               "保存CNF到USB"),
    ("UIT_RETURN_TO_LOADER",  "Return to loader",               "返回載入器"),
    ("UIT_PS2_BROWSER",       "PS2 Browser (FMCB Restart)",     "PS2主功能表(FMCB重啓)"),
    ("UIT_ALL_DEFAULT",       "All set to default",             "全部回復預設"),
    # ---- 各子菜单标题 ----
    ("UIT_E_KEY_SETTINGS_FMT","E%d Button Settings",            "E%d按鍵設定"),
    ("UIT_ITEM_SETTINGS_FMT", "Item %d Settings",               "項目%d設定"),
    ("UIT_OSD_SETTINGS",      "OSD Settings",                   "OSD設定"),
    ("UIT_SCROLL_SETTINGS",   "Scroll Settings",                "捲動設定"),
    ("UIT_ESR_TITLE",         "ESR Path",                       "ESR路径"),
    # ---- OSDSYS 菜单 ----
    ("UIT_CFG_ITEM_FMT",      "  Configure Item %2d : %s",      "  設定項目%2d : %s"),
    ("UIT_CFG_SCROLL",        "  Configure Scrolling Options",  "  設定捲動選項"),
    ("UIT_VIDEO_MODE",        "Video Mode",                     "影像模式"),
    ("UIT_SKIP_MC_CHECK",     "Skip MC update check",           "跳過MC更新確認"),
    ("UIT_SKIP_HDD_CHECK",    "Skip HDD update check",          "跳過HDD更新確認"),
    ("UIT_SKIP_DISC_BOOT",    "Skip Disc Boot",                 "跳過光盤起動"),
    ("UIT_SKIP_SONY_LOGO",    "Skip Sony Logo",                 "跳過Sony標誌"),
    ("UIT_GO_BROWSER",        "Go to Browser",                  "進入主功能表"),
    ("UIT_SELECTED_COLOR",    "Selected Color",                 "選中色"),
    ("UIT_UNSELECTED_COLOR",  "Unselected Color",               "未選中色"),
    ("UIT_MENU_X",            "Menu X",                         "左右位置"),
    ("UIT_MENU_Y",            "Menu y",                         "上下位置"),
    ("UIT_VERSION",           "Version",                        "版本"),
    # ---- 捲動设置菜单 ----
    ("UIT_SCROLL_MENU",       "Scroll Menu",                    "功能表捲動"),
    ("UIT_DISPLAYED_ITEMS",   "Displayed Items",                "表示項目"),
    ("UIT_CURSOR_VELOCITY",   "Cursor Max Velocity",            "游標最大速度"),
    ("UIT_CURSOR_ACCEL",      "Cursor Acceleration",            "游標加速度"),
    ("UIT_LEFT_CURSOR_FMT",   "  Left Cursor: %s",              "  左側游標: %s"),
    ("UIT_RIGHT_CURSOR_FMT",  "  Rigth Cursor: %s",             "  右側游標: %s"),
    ("UIT_TOP_DELIM_FMT",     "  Top Delimiter: %s",            "  上部分隔符: %s"),
    ("UIT_BOTTOM_DELIM_FMT",  "  Bottom Delimiter: %s",         "  下部分隔符: %s"),
    # ---- OSDSYS 项目/ESR 菜单 ----
    ("UIT_NAME_FMT",          "  Name: %s",                     "  名称: %s"),
    # ---- 提示条 (tooltips) ----
    ("UIT_OK",                "OK",                             "確定"),
    ("UIT_CANCEL",            "CANCEL",                         "取消"),
    ("UIT_UP",                "Up",                             "上層"),
    ("UIT_CHANGE_ITEM",       "Change item",                    "切換項目"),
    ("UIT_COPY_ITEM",         "Copy item",                      "複製項目"),
    ("UIT_PASTE_ITEM",        "Paste item",                     "貼上項目"),
    ("UIT_HACKED_OSDSYS",     "Hacked OSDSYS",                  "破解OSDSYS"),
    ("UIT_ENTER",             "Enter",                          "進入"),
    ("UIT_CHANGE",            "Change",                         "切換"),
    ("UIT_ADD",               "Add",                            "加"),
    ("UIT_SUBTRACT",          "Subtract",                       "減"),
    ("UIT_BROWSE",            "Browse",                         "閲覧"),
    ("UIT_CLEAR",             "Clear",                          "清除"),
    ("UIT_MAP_MC",            "Map to any MC",                 "指定任意MC"),
    ("UIT_SET_SPECIAL",       "Set special",                    "設定特殊"),
    ("UIT_RUN",               "Run",                            "執行"),
    ("UIT_TYPE",              "Type",                           "輸入"),
    ("UIT_RETURN",            "Return",                         "返回"),
    ("UIT_SET_DEFAULT",       "set default",                    "設為預設"),
    ("UIT_SELECT_LAYOUT",     "Select buttons layout",         "選択按鍵配置"),
    ("UIT_SWAPOPT_X",         "O: X Cancel / O OK",            "\xff0: \xff1取消 / \xff0確定"),
    ("UIT_SWAPOPT_O",         "X: O Cancel / X OK",            "\xff1: \xff0取消 / \xff1確定"),
    # ---- 项目/ESR 路径标签 ----
    ("UIT_PATH",              "Path",                          "路径"),
    ("UIT_PATH1",             "Path1:",                        "位置1:"),
    ("UIT_PATH2",             "Path2:",                        "位置2:"),
    ("UIT_PATH3",             "Path3:",                        "位置3:"),
    # ---- 输入法界面 ----
    ("UIT_KB_PY",             "PY:",                           "音:"),
    ("UIT_KB_SELEN",          "SELECT:EN",                     "SELECT:詞組"),
    ("UIT_KB_ENPAGE",         "EN/SYM SELECT:Chinese",         "英文/符号頁"),
    ("UIT_KB_COM_PAGE",       "Common phrases page",           "常用詞組"),
    ("UIT_KB_GBK_TAG",        "5009 GBK tag",                  "5009専用"),
    ("UIT_KB_GBK_COM_PAGE",   "Common phrases page (GBK)",     "常用詞組 5009専用"),
    ("UIT_KB_GBK_EN_PAGE",    "EN/SYM page (GBK)",             "英文/符号頁 5009専用"),
    ("UIT_KB_HINT1",          "kb hint line 1 (pinyin)",       "\xff0:輸入 \xff2:上屏 L1/R1:翻頁 \xff1:退格"),
    ("UIT_KB_HINT2",          "kb hint line 2 (pinyin)",       "L2/R2:移標 SELECT:詞組 START:確定 \xff3:取消"),
    ("UIT_KB_EN_HINT",        "kb hint (EN page)",             "\xff0:輸入 SELECT:中文 START:確定 \xff3:取消"),
    ("UIT_KB_COM_HINT",       "kb hint (common page)",         "\xff0:輸入 SELECT:英文 START:確定 \xff3:取消"),
    # ---- 消息 ----
    ("UIT_SAVED_FMT",         "Saved %s",                       "已保存 %s"),
    ("UIT_LOADED_FMT",        "Loaded %s",                      "已載入 %s"),
    ("UIT_FAIL_OPEN_FMT",     "Failed to open %s",             "開啓%s失敗"),
    ("UIT_FAIL_WRITE_FMT",    "Failed to write %s",             "保存%s失敗"),
    ("UIT_FAIL_LOAD_FMT",     "Failed to load %s",             "載入%s失敗"),
    ("UIT_INCOMPATIBLE",      "Incompatible path selected",     "路径不相容"),
    ("UIT_OVERWRITE_FMT",     "Overwrite item %d?",             "覆蓋項目%d？"),
]


def load_charset(path):
    """返回 {unicode字符: SJIS码(int)}"""
    table = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3 and parts[1].startswith("U+"):
                try:
                    cp = int(parts[1][2:], 16)
                except ValueError:
                    continue
                table[chr(cp)] = int(parts[0], 16)
    return table


def to_c_string(text, table, macro):
    r"""把中文文本转为 C 字符串字面量（SJIS 双字节 -> \xNN 转义）

    注意: 若 \xHH 转义后紧跟十六进制字符 (如 "的CNF" -> ...\x49 + 'C')，
    C 会把 \x49C 解析成一个超长转义，因此在边界处拆分为相邻字面量拼接。
    """
    out = []
    prev_escape = False
    for ch in text:
        if ord(ch) < 0x80:
            if prev_escape and ch in "0123456789abcdefABCDEF":
                out.append('" "')  # 相邻字符串字面量拼接
            if ch in ('\\', '"'):
                out.append("\\" + ch)
            else:
                out.append(ch)
            prev_escape = False
        elif ord(ch) == 0xFF:
            # 0xFF 按钮图标字符，输出 \xFF 转义；后随 hex 字符时由
            # prev_escape 的相邻字面量拆分逻辑避免 \x 贪婪
            out.append("\\xFF")
            prev_escape = True
        else:
            if ch not in table:
                print("ERROR: 字符 '%s' (U+%04X) 不在字集中: %s = %r"
                      % (ch, ord(ch), macro, text))
                sys.exit(1)
            code = table[ch]
            out.append("\\x%02X\\x%02X" % (code >> 8, code & 0xFF))
            prev_escape = True
    return '"' + "".join(out) + '"'


def main():
    table = load_charset(CHARSET_FILE)
    print("charset loaded: %d entries" % len(table))

    # 先整体校验一遍
    for macro, eng, chn in TERMS:
        for ch in chn:
            if ord(ch) >= 0x80 and ord(ch) != 0xFF and ch not in table:
                print("ERROR: 字符 '%s' (U+%04X) 不在字集中: %s = %r"
                      % (ch, ord(ch), macro, chn))
                sys.exit(1)

    lines = [
        "// ui_text.h - FMCB Configurator 中文 UI 字符串 (Shift-JIS 编码)",
        "// 由 pinyin/gen_i18n.py 生成，勿手工编辑",
        "// 字符集: JIS X0208 (charset.txt)，仅使用日文字形汉字",
        "#ifndef __UI_TEXT_H__",
        "#define __UI_TEXT_H__",
        "",
    ]
    for macro, eng, chn in TERMS:
        lines.append("#define %-24s %-48s //%s = %s" %
                     (macro, to_c_string(chn, table, macro), eng, chn))
    lines += ["", "#endif /* __UI_TEXT_H__ */", ""]

    with open(OUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("OK: %d 个词条已生成 %s" % (len(TERMS), os.path.abspath(OUT_FILE)))


if __name__ == "__main__":
    main()
