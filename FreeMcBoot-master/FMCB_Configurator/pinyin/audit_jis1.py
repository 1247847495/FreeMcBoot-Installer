# -*- coding: utf-8 -*-
"""审计：JIS 第1水準(区16-47) 双向核对。
A. CSV 一级字 ⊆ 字库？（缺哪些、为什么）
B. 可提交码（拼音候选/词组/符号）里有多少在一级之外（区48+ 或其他）→ 实机空白风险
C. 缺字里哪些补进后可打（有简体显示形）
"""
import csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_font import to_display
SRC = os.path.normpath(os.path.join(HERE, '..'))
CSV = r"c:\Users\Administrator\.trae-cn\attachments\6ae32f35cf12968c1742c9ed\c4742eb2-262b-46e0-ab55-bfe163f06036_7c926c3f-2e6d-4590-a715-d74d0f1bb8a8_JIS_第1水準漢字_2965.csv"

def kuten(s):
    """SJIS -> (区, 点)，均 1-based。"""
    hi, lo = s >> 8, s & 0xFF
    hi = (hi - (0xC1 if hi >= 0xE0 else 0x81)) * 2
    if lo >= 0x9F:
        hi += 1; lo -= 0x9F
    elif lo >= 0x80:
        lo -= 0x41
    else:
        lo -= 0x40
    return hi + 1, lo + 1

def gb_ok(ch):
    try:
        ch.encode('gb2312'); return True
    except UnicodeEncodeError:
        return False

# 字库
ch_of = {}
for line in open(os.path.join(HERE, 'charset.txt'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 3 and p[1].startswith('U+'):
        ch_of[int(p[0], 16)] = chr(int(p[1][2:], 16))

# 拼音数据（判断缺字有没有读音）
import unicodedata
word_py = {}
pat = re.compile(r'^U\+([0-9A-F]{4,5}):\s*(\S+)')
for line in open(os.path.join(HERE, 'pinyin.txt'), encoding='utf-8'):
    m = pat.match(line)
    if m:
        word_py[int(m.group(1), 16)] = m.group(2)

# ---- A. 一级缺字 ----
rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig')))
csv_by_sjis = {int(r['Shift_JIS_hex'], 16): r['漢字'] for r in rows}
missing = [(int(r['Shift_JIS_hex'], 16), r['漢字']) for r in rows
           if int(r['Shift_JIS_hex'], 16) not in ch_of]
print('A. 一级 %d 字，字库缺 %d:' % (len(rows), len(missing)))
fixable, kokuji = [], []
for s, ch in missing:
    d = to_display(ch)
    ku, _ = kuten(s)
    if d != ch and gb_ok(d) and ord(ch) in word_py:
        fixable.append('%s→%s(%s)' % (ch, d, word_py[ord(ch)].split(',')[0]))
    else:
        kokuji.append(ch)
print('   有简体形+读音，补进即可打: %s' % ' '.join(fixable))
print('   无简体形/无读音(国字等): %s' % ''.join(kokuji))

# ---- B. 可提交码的区分布 ----
src = open(os.path.join(SRC, 'cn_pinyin.c'), encoding='utf-8').read()
pairs = [int(x, 16) for x in re.findall(r'0x([0-9A-Fa-f]{4})',
         re.search(r'cn_py_pairs\[CN_PY_PAIRS\]\s*=\s*\{(.*?)\};', src, re.S).group(1))]

def level_of(s):
    ku, _ = kuten(s)
    if 16 <= ku <= 47: return 1      # 一级：实机安全
    if 48 <= ku <= 84: return 2      # 二级：实机风险（灌=区62实测空白）
    return 0                          # 假名/符号：安全

l1 = [s for s in pairs if level_of(s) == 1]
l2 = [s for s in pairs if level_of(s) == 2]
other = [s for s in pairs if level_of(s) == 0]
print('B. 拼音候选 %d 码：一级 %d，假名/符号 %d，二级(风险) %d'
      % (len(pairs), len(l1), len(other), len(l2)))

# 二级候选明细（显示形汇总）
from collections import defaultdict
l2_disp = sorted(set(to_display(ch_of[s]) for s in l2))
print('   二级候选的显示形共 %d 个:' % len(l2_disp))
for i in range(0, len(l2_disp), 40):
    print('     ' + ' '.join(l2_disp[i:i+40]))

# 显示形只能靠二级提供的（过滤二级后会丢的）
disp_l1only = set(to_display(ch_of[s]) for s in l1)
lost = [d for d in l2_disp if d not in disp_l1only]
print('   其中只能由二级字提供的显示形 %d 个（过滤二级后打不出的字）:' % len(lost))
for i in range(0, len(lost), 40):
    print('     ' + ' '.join(lost[i:i+40]))

# 词组/符号
phr = re.search(r'cn_com_phrases\[CN_COM_COUNT\]\s*=\s*\{(.*?)\};', src, re.S).group(1)
pl = [int(x, 16) for x in re.findall(r'\\x([0-9A-Fa-f]{2})', phr)]
pc = [(pl[i] << 8) | pl[i+1] for i in range(0, len(pl) - 1, 2)]
sym = [int(x, 16) for x in re.findall(r'0x([0-9A-Fa-f]{4})',
       re.search(r'cn_sym_codes\[CN_SYM_COUNT\]\s*=\s*\{(.*?)\};', src, re.S).group(1))]
print('   词组码 %s（%s）；符号页 %d 码全在假名/符号区: %s'
      % (['%04X' % c for c in pc],
         '/'.join('区%d' % kuten(c)[0] for c in pc),
         len(sym), all(level_of(s) == 0 for s in sym)))
