# -*- coding: utf-8 -*-
"""
生成 FMCB Configurator 汉化用 SJIS 字符集（裁剪版 JIS X0208）。

裁剪规则（用户确认）：
  1. 去掉不常用的字：二级汉字只保留 GB2312 可编码的
  2. 去掉无法识别的字：日本自造汉字（国字/和字）黑名单
  3. 去掉非日文假名的无关符号：希腊字母、西里尔字母、制表线框
  4. 保留：全部假名、常用标点符号（GB2312 可编码）、一级汉字、二级汉字∩GB2312

输出 charset.txt：每行 SJIS码 <TAB> Unicode <TAB> 字符，按 SJIS 码升序。
"""
import codecs
import os

# 日本自造汉字（国字），中文无法识别/GB2312 均无
WAGO_BLACKLIST = set(u'辻峠凪匂込塀枠膵噛捗岼榊糀遖匁')

# 二级汉字强制保留白名单（日文新字体，GB2312 无对应但常用；以后缺字往此加）
L2_FORCE_KEEP = set(u'録')

# 显式排除区域（GB2312 里也有这些区，但 PS2 菜单名用不上且属"非假名无关符号"）
EXCLUDE_RANGES = [
    (0x0370, 0x03FF),  # 希腊字母
    (0x0400, 0x04FF),  # 西里尔字母
    (0x2190, 0x21FF),  # 箭头（JIS 1区部分，按需可再放开）
    (0x2500, 0x257F),  # 制表线框 box drawing
]

# UI 翻译必须用到的字（config.c 译文），缺失则报错——由 check_ui() 校验
# 注意：JIS X0208 无简体字形，译文必须用日文字形汉字（設/記/確/類…）
UI_TEXTS = [
    u"設定", u"戻る", u"保存", u"載入", u"初期値", u"終了",
    u"配置", u"安装", u"閲覧", u"画面", u"色", u"網絡",
    u"言語", u"確定", u"取消", u"前一歩", u"次一歩",
    u"遊戯", u"程序", u"名称", u"路径", u"類型", u"記憶庫",
    u"無効", u"有効", u"選択", u"入力", u"削除", u"移動",
    u"複製", u"貼付", u"終端機", u"起動", u"文件", u"目録",
]


def in_exclude(cp):
    return any(lo <= cp <= hi for lo, hi in EXCLUDE_RANGES)


def main():
    def gb_ok(ch):
        try:
            ch.encode('gb2312')
            return True
        except UnicodeEncodeError:
            return False

    entries = []  # (sjis_hi, sjis_lo, cp, char)
    seen = set()

    his = list(range(0x81, 0xA0)) + list(range(0xE0, 0xF0))
    los = list(range(0x40, 0x7F)) + list(range(0x80, 0xFD))  # SJIS 低字节上限 0xFC（含）
    for hi in his:
        for lo in los:
            b = bytes([hi, lo])
            try:
                ch = b.decode('shift_jis')  # 严格 SJIS：自动排除 CP932 扩展
            except UnicodeDecodeError:
                continue
            cp = ord(ch)
            if cp in seen:
                continue
            seen.add(cp)

            if ch in WAGO_BLACKLIST or in_exclude(cp):
                continue

            is_kanji = 0x4E00 <= cp <= 0x9FFF
            is_kana = 0x3040 <= cp <= 0x30FF

            if is_kanji:
                # 一级 = 区16-47：hi 0x88-0x97 全部 + hi 0x98 低字节 <=0x9E（区47 尾部）
                is_l1 = 0x88 <= hi <= 0x97 or (hi == 0x98 and lo <= 0x9E)
                if is_l1:
                    keep = True            # 一级汉字：全留
                else:
                    keep = gb_ok(ch) or ch in L2_FORCE_KEEP  # 二级：GB2312 或白名单
            elif is_kana:
                keep = True                # 假名：全留
            else:
                keep = gb_ok(ch)           # 符号：只留 GB2312 有
            if keep:
                entries.append((hi, lo, cp, ch))

    entries.sort(key=lambda e: (e[0], e[1]))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'charset.txt')
    with open(out, 'w', encoding='utf-8') as f:
        for hi, lo, cp, ch in entries:
            f.write('0x%02X%02X\tU+%04X\t%s\n' % (hi, lo, cp, ch))

    charset = set(e[3] for e in entries)
    n_kanji = sum(1 for e in entries if 0x4E00 <= e[2] <= 0x9FFF)
    n_l1 = sum(1 for e in entries if 0x88 <= e[0] <= 0x97 and 0x4E00 <= e[2] <= 0x9FFF)
    n_l2 = n_kanji - n_l1
    n_kana = sum(1 for e in entries if 0x3040 <= e[2] <= 0x30FF)
    n_sym = len(entries) - n_kanji - n_kana
    print('总计 %d 字（一级 %d + 二级 %d 汉字，假名 %d，符号 %d）'
          % (len(entries), n_l1, n_l2, n_kana, n_sym))
    print('字体数据：%.1f KB（16x16 1bpp = 32B/字）' % (len(entries) * 32 / 1024))

    # 校验 UI 必需字符
    missing = []
    for txt in UI_TEXTS:
        for ch in txt:
            if ch not in charset and ch not in (u'\r', u'\n'):
                missing.append(ch)
    if missing:
        print('!! UI 缺字：' + ' '.join(sorted(set(missing))))
    else:
        print('UI 必需字符校验通过')


if __name__ == '__main__':
    main()
