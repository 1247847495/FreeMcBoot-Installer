# -*- coding: utf-8 -*-
"""
从 pinyin.txt（mozillazg/pinyin-data）+ charset.txt 生成拼音输入法码表。

- 去声调；ü→v（键盘惯例）
- 只保留 charset.txt 内的字（unicode 匹配）
- 多音字展开为多对
- 组内排序：一级汉字优先，再按 SJIS 码升序
- 查找语义：用户输入为任意拼音前缀；完全匹配的拼音组排最前

输出：cn_pinyin.h / cn_pinyin.c
"""
import os
import re
import unicodedata
from opencc import OpenCC

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..'))  # FMCB_Configurator source dir

# 声调元音 → 基础字母；ü 系 → v
TONE_MAP = {}
for base in 'aeiou':
    for i, mark in enumerate(['\u0304', '\u0301', '\u030c', '\u0300']):
        TONE_MAP[unicodedata.normalize('NFD', base + mark)[0] + mark] = base
TONE_MAP.update({'ü': 'v', 'ǖ': 'v', 'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v'})

_cc = OpenCC('t2s')

#日文新字体/特有形 -> 简体（与 gen_font.py 保持一致，OpenCC t2s 覆盖不到的部分）
JP2CN = {
    '亜': '亚', '唖': '哑', '穐': '秋', '悪': '恶', '鯵': '鲹', '圧': '压',
    '囲': '围', '壱': '壹', '稲': '稻', '隠': '隐', '欝': '郁', '叡': '睿',
    '営': '营', '栄': '荣', '駅': '驿', '円': '圆', '焔': '焰', '縁': '缘',
    '艶': '艳', '薗': '园', '塩': '盐', '汚': '污', '応': '应', '鴬': '莺',
    '鴎': '鸥', '穏': '稳', '仮': '假', '価': '价', '菓': '果', '壊': '坏',
    '廻': '回', '懐': '怀', '絵': '绘', '拡': '扩', '撹': '搅', '覚': '觉',
    '楽': '乐', '潟': '泻', '渇': '渴', '鞄': '包', '竃': '灶', '栢': '柏',
    '苅': '刈', '勧': '劝', '巻': '卷', '寛': '宽', '歓': '欢', '潅': '灌',
    '観': '观', '諌': '谏', '関': '关', '陥': '陷', '巌': '岩', '帰': '归',
    '気': '气', '亀': '龟', '戯': '戏', '犠': '牺', '拠': '据', '挙': '举',
    '彊': '强', '郷': '乡', '尭': '尧', '暁': '晓', '倶': '俱', '駆': '驱',
    '駈': '驱', '勲': '勋', '薫': '熏', '珪': '硅', '恵': '惠', '渓': '溪',
    '経': '经', '継': '继', '繋': '系', '蛍': '萤', '軽': '轻', '頚': '颈',
    '鶏': '鸡', '撃': '击', '倹': '俭', '剣': '剑', '圏': '圈', '検': '检',
    '権': '权', '県': '县', '険': '险', '顕': '显', '験': '验', '鹸': '碱',
    '厳': '严', '戸': '户', '呉': '吴', '娯': '娱', '碁': '棋', '効': '效',
    '広': '广', '鉱': '矿', '砿': '矿', '黒': '黑', '梱': '捆', '歳': '岁',
    '済': '济', '砕': '碎', '斎': '齐', '剤': '剂', '咲': '笑', '埼': '崎',
    '搾': '榨', '桜': '樱', '雑': '杂', '皐': '皋', '桟': '栈', '讃': '赞',
    '賛': '赞', '姉': '姐', '歯': '齿', '児': '儿', '実': '实', '舎': '舍',
    '釈': '释', '呪': '咒', '収': '收', '繍': '绣', '讐': '仇', '従': '从',
    '渋': '涩', '獣': '兽', '縦': '纵', '粛': '肃', '楯': '盾', '処': '处',
    '奨': '奖', '渉': '涉', '焼': '烧', '粧': '妆', '醤': '酱', '乗': '乘',
    '剰': '剩', '壌': '壤', '嬢': '娘', '浄': '净', '畳': '叠', '譲': '让',
    '醸': '酿', '靭': '韧', '図': '图', '粋': '粹', '酔': '醉', '髄': '髓',
    '瀬': '濑', '斉': '齐', '摂': '摄', '専': '专', '戦': '战', '繊': '纤',
    '賎': '贱', '銭': '钱', '曽': '曾', '疎': '疏', '捜': '搜', '挿': '插',
    '掻': '挠', '巣': '巢', '痩': '瘦', '窓': '窗', '総': '总', '聡': '聪',
    '荘': '庄', '鎗': '枪', '騒': '骚', '増': '增', '臓': '脏', '蔵': '藏',
    '続': '续', '楕': '椭', '駄': '驮', '騨': '驒', '対': '对', '帯': '带',
    '滝': '泷', '択': '择', '沢': '泽', '単': '单', '団': '团', '弾': '弹',
    '値': '值', '遅': '迟', '鋳': '铸', '庁': '厅', '徴': '征', '聴': '听',
    '勅': '敕', '壷': '壶', '逓': '递', '鉄': '铁', '転': '转', '伝': '传',
    '兎': '兔', '妬': '妒', '嶋': '岛', '闘': '斗', '働': '动', '徳': '德',
    '涜': '渎', '読': '读', '呑': '吞', '縄': '绳', '弐': '贰', '韮': '韭',
    '撚': '捻', '廼': '乃', '埜': '野', '嚢': '囊', '悩': '恼', '脳': '脑',
    '覗': '觑', '覇': '霸', '廃': '废', '拝': '拜', '楳': '梅', '売': '卖',
    '蝿': '蝇', '溌': '泼', '発': '发', '醗': '酿', '髪': '发', '抜': '拔',
    '釆': '采', '晩': '晚', '毘': '毗', '姫': '姬', '氷': '冰', '鋲': '铆',
    '冨': '富', '払': '拂', '仏': '佛', '雰': '氛', '変': '变', '辺': '边',
    '舗': '铺', '歩': '步', '穂': '穗', '倣': '仿', '砲': '炮', '豊': '丰',
    '頬': '颊', '毎': '每', '槙': '桢', '侭': '尽', '満': '满', '姪': '侄',
    '麺': '面', '黙': '默', '戻': '戾', '薬': '药', '訳': '译', '鑓': '枪',
    '揺': '摇', '様': '样', '頼': '赖', '覧': '览', '竜': '龙', '両': '两',
    '猟': '猎', '瞭': '了', '燐': '磷', '隣': '邻', '瑠': '琉', '塁': '垒',
    '涙': '泪', '隷': '隶', '霊': '灵', '齢': '龄', '暦': '历', '歴': '历',
    '労': '劳', '錬': '炼', '篭': '笼', '蝋': '蜡', '脇': '胁', '椀': '碗',
}


def to_display(ch):
    """日文假字(存储形) -> 简体显示形。转不了的原样返回。"""
    s = _cc.convert(ch)
    if s != ch:
        return s
    return JP2CN.get(ch, ch)


def strip_tone(s):
    out = []
    for ch in s:
        if ch in TONE_MAP:
            out.append(TONE_MAP[ch])
            continue
        d = unicodedata.normalize('NFD', ch)
        if len(d) > 1 and unicodedata.combining(d[1]):
            out.append(d[0])
        else:
            out.append(ch)
    return ''.join(out)


def main():
    # 读字集
    cs = {}  # unicode cp -> sjis
    with open(os.path.join(HERE, 'charset.txt'), encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 3:
                cs[int(parts[1][2:], 16)] = int(parts[0], 16)

    # 读拼音
    word_py = {}  # cp -> [pinyin]
    pat = re.compile(r'^U\+([0-9A-F]{4,5}):\s*(\S+)')
    with open(os.path.join(HERE, 'pinyin.txt'), encoding='utf-8') as f:
        for line in f:
            m = pat.match(line)
            if not m:
                continue
            cp = int(m.group(1), 16)
            if cp not in cs:
                continue
            pys = [strip_tone(p) for p in m.group(2).split(',')]
            pys = [p for p in pys if re.fullmatch(r'[a-z]+', p)]
            if pys:
                word_py[cp] = sorted(set(pys))

    # 用户指定：'灌'归 guan 音（去掉 huan 读法）。
    # 实测 PS2 ROM 字库无灌本字(9FF3)，提交日文标准形 潅(8AC1)：
    # 候选显示仍为'灌'（字体层转换），日文机显示潅，5009 页自动转 GBK B9E0。
    if 0x704C in word_py:
        word_py[0x704C] = [p for p in word_py[0x704C] if p == 'guan']

    # 显示形过滤：转换成简体后必须能被 GB2312 编码（剔除和字/生僻/繁形残留）
    # 显示形映射：多个 JIS 字可能转成同一简体形（候选去重依据）
    disp_of = {}
    dropped = []
    for cp in list(word_py.keys()):
        d = to_display(chr(cp))
        try:
            d.encode('gb2312')
        except UnicodeEncodeError:
            dropped.append(chr(cp))
            del word_py[cp]
            continue
        disp_of[cp] = d

    # 展开对：(py, sjis, level, disp)
    # level: 一级(区16-47) = 0，二级 = 1（hi 0x98 且 lo<=0x9E 属区47 一级尾部）
    pairs = []
    for cp, pys in word_py.items():
        sjis = cs[cp]
        hi, lo = sjis >> 8, sjis & 0xFF
        # level 1 = JIS 二级汉字（区48+，实机 ROM 无字形）：
        # hi>=0x98（区47 尾部 0x9840-0x989E 除外）及 0xE0-0xEF；
        # 符号/假名（hi 0x81-0x87）与一级汉字均为 0（普通页可显示）
        level = 0 if (hi <= 0x97 or (hi == 0x98 and lo <= 0x9E)) else 1
        for py in pys:
            pairs.append((py, sjis, level, disp_of[cp]))

    # 拼音字典序
    all_py = sorted(set(p[0] for p in pairs))
    py_rank = {py: i for i, py in enumerate(all_py)}
    # 组内：一级优先 + SJIS 升序
    pairs.sort(key=lambda t: (py_rank[t[0]], t[2], t[1]))

    # 组内显示形去重：同一简体形只保留第一个（一级优先且 SJIS 最小的那个）
    deduped = []
    seen = set()
    cur_py = None
    for p in pairs:
        if p[0] != cur_py:
            cur_py = p[0]
            seen = set()
        if p[3] in seen:
            continue
        seen.add(p[3])
        deduped.append(p)
    pairs = deduped

    # pool
    pool = ''
    py_off = []
    for py in all_py:
        py_off.append(len(pool))
        pool += py + '\0'
    pool += '\0'

    # 每拼音在 pairs 的起点
    py_start = []
    i = 0
    for py in all_py:
        while i < len(pairs) and pairs[i][0] != py:
            i += 1
        py_start.append(i)
    py_start.append(len(pairs))

    # 每音节 level-0（一级+假名/符号）pair 数量：组内按 (level, sjis) 排序
    # 保证一级块在前，故前 cn_py_l1[i] 个即普通页可见块。
    # 普通页（日文机）按 cn_py_start[i]+cn_py_l1[i] 截断——二级字 ROM 无字形；
    # 5009 页（gbk 模式）取全部，提交时转 GBK 中文机显示正常。
    py_l1 = [0] * len(all_py)
    for idx in range(len(all_py)):
        for k in range(py_start[idx], py_start[idx+1]):
            if pairs[k][2] == 0:
                py_l1[idx] += 1

    n_py = len(all_py)
    n_pairs = len(pairs)
    n_words = len(word_py)

    # 符号/英文页：精选 78 个字符（13x6 一页）：Ａ-Ｚ ０-９ ａ-ｚ + 常用标点
    # （最后的 . 是半角 ASCII 句点——输版本号 "4.43" 用；；号在名字里用不上，舍去）
    SYM_LIST = ('ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
                '０１２３４５６７８９'
                'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
                '、。，：？！…“”「」【】（）' + '.')
    rev = {cp: sjis for cp, sjis in cs.items()}
    syms = []
    for ch in SYM_LIST:
        cp = ord(ch)
        if cp < 0x80:  #ASCII (e.g. '.') passes through as its own code
            syms.append((cp, cp))
        elif cp in rev:
            syms.append((cp, rev[cp]))
        else:
            print('警告: %s (U+%04X) 不在字集中，已跳过' % (ch, cp))
    if len(syms) != 78:
        print('注意: 精选符号数 %d (期望 78)' % len(syms))

    # ---- 常用词组页 ----
    # 用户指定的词组，一格一词组，○ 整词上屏
    COM_PHRASES = ['最', '中文版', '中文', '最新', '金手指', '模拟器',
                   '启动', '关机', '重启', '配置', '文件管理器',
                   'SMS视频播放器', '光盘启动', '内置硬盘', '灌录']
    # 反查: 简体显示形 -> (level, sjis)；一级优先、SJIS 升序（与拼音候选取码一致）
    best = {}
    for cp, sjis in cs.items():
        d = to_display(chr(cp))
        try:
            d.encode('gb2312')
        except UnicodeEncodeError:
            continue
        hi, lo = sjis >> 8, sjis & 0xFF
        lv = 0 if (hi <= 0x97 or (hi == 0x98 and lo <= 0x9E)) else 1
        if d not in best or (lv, sjis) < best[d]:
            best[d] = (lv, sjis)
    # 词组 -> C 字符串（ASCII 原样，汉字两字节全部 \xNN 转义，
    # 避免 SJIS 低位字节以 ASCII 形式与前置 \x 转义发生贪婪解析）
    coms = []  # (C 转义串, 显示文本)
    FORCE_SJIS = {}  #9FF3 实机无字形，'灌'一律走日文标准形 8AC1，反查自动命中
    missing = []
    for ph in COM_PHRASES:
        parts = []
        for ch in ph:
            if ord(ch) < 0x80:
                parts.append(ch)
            elif ch in FORCE_SJIS:
                parts.append('\\x%02X\\x%02X' % (FORCE_SJIS[ch] >> 8, FORCE_SJIS[ch] & 0xFF))
            elif ch in best:
                sj = best[ch][1]
                parts.append('\\x%02X\\x%02X' % (sj >> 8, sj & 0xFF))
            else:
                missing.append(ch)
        coms.append((''.join(parts), ph))
    if missing:
        print('常用词组缺字: %s' % ''.join(missing))
        raise SystemExit(1)
    n_com = len(coms)
    print('常用词组页: %d 条' % n_com)

    # ---- cn_pinyin.h ----
    with open(os.path.join(SRC, 'cn_pinyin.h'), 'w', encoding='utf-8') as f:
        f.write('//Auto-generated by gen_pinyin.py. DO NOT EDIT.\n')
        f.write('#ifndef CN_PINYIN_H\n#define CN_PINYIN_H\n\n')
        f.write('#define CN_PY_COUNT %d\n' % n_py)
        f.write('#define CN_PY_PAIRS %d\n' % n_pairs)
        f.write('#define CN_SYM_COUNT %d\n\n' % len(syms))
        f.write('#define CN_COM_COUNT %d\n\n' % n_com)
        f.write('extern const char cn_py_pool[]; //nul-terminated pinyin syllables\n')
        f.write('extern const unsigned short cn_py_off[CN_PY_COUNT]; //offset into pool\n')
        f.write('extern const unsigned short cn_py_start[CN_PY_COUNT + 1]; //range in pairs, dict order\n')
        f.write('extern const unsigned short cn_py_l1[CN_PY_COUNT]; //level-0 pair count per syllable\n')
        f.write('extern const unsigned short cn_py_pairs[CN_PY_PAIRS]; //SJIS codes\n')
        f.write('extern const unsigned short cn_sym_codes[CN_SYM_COUNT]; //kana+symbols, SJIS codes\n')
        f.write('extern const char * const cn_com_phrases[CN_COM_COUNT]; //common phrases, SJIS bytes\n\n')
        f.write('#endif\n')

    # ---- cn_pinyin.c ----
    with open(os.path.join(SRC, 'cn_pinyin.c'), 'w', encoding='utf-8') as f:
        f.write('//Auto-generated by gen_pinyin.py. DO NOT EDIT.\n')
        f.write('#include "cn_pinyin.h"\n\n')
        f.write('const char cn_py_pool[] =\n')
        for i in range(0, len(pool), 64):
            esc = pool[i:i+64].replace('\\', '\\\\').replace('"', '\\"')
            f.write('\t"%s"\n' % esc.replace('\0', '\\0'))
        f.write(';\n\n')
        f.write('const unsigned short cn_py_off[CN_PY_COUNT] = {\n')
        for i in range(0, n_py, 12):
            f.write('\t' + ','.join(str(v) for v in py_off[i:i+12]) + ',\n')
        f.write('};\n\n')
        f.write('const unsigned short cn_py_start[CN_PY_COUNT + 1] = {\n')
        for i in range(0, n_py + 1, 12):
            f.write('\t' + ','.join(str(v) for v in py_start[i:i+12]) + ',\n')
        f.write('};\n\n')
        f.write('const unsigned short cn_py_l1[CN_PY_COUNT] = {\n')
        for i in range(0, n_py, 12):
            f.write('\t' + ','.join(str(v) for v in py_l1[i:i+12]) + ',\n')
        f.write('};\n\n')
        f.write('const unsigned short cn_py_pairs[CN_PY_PAIRS] = {\n')
        sjis_list = [p[1] for p in pairs]
        for i in range(0, n_pairs, 10):
            f.write('\t' + ','.join('0x%04X' % v for v in sjis_list[i:i+10]) + ',\n')
        f.write('};\n\n')
        f.write('const unsigned short cn_sym_codes[CN_SYM_COUNT] = {\n')
        for i in range(0, len(syms), 10):
            f.write('\t' + ','.join('0x%04X' % t[1] for t in syms[i:i+10]) + ',\n')
        f.write('};\n\n')
        f.write('const char * const cn_com_phrases[CN_COM_COUNT] = {\n')
        for esc, disp in coms:
            f.write('\t"%s", //%s\n' % (esc, disp))
        f.write('};\n')

    print('拼音音节 %d 个，字 %d（剔除非简体 %d），(字,拼音)对 %d（去重后），pool %d 字节'
          % (n_py, n_words, len(dropped), n_pairs, len(pool)))
    # 抽查：zhong
    k = all_py.index('zhong') if 'zhong' in all_py else -1
    if k >= 0:
        chars = [chr(c) for c in word_py if 'zhong' in word_py[c]][:20]
        print('zhong 候选样本: ' + ''.join(chars))


if __name__ == '__main__':
    main()
