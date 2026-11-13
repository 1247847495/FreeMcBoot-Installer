# -*- coding: utf-8 -*-
"""比对用户提供的 JIS 第1水準漢字 CSV 与本字库 charset.txt 的覆盖情况。"""
import csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = r"c:\Users\Administrator\.trae-cn\attachments\6ae32f35cf12968c1742c9ed\c4742eb2-262b-46e0-ab55-bfe163f06036_7c926c3f-2e6d-4590-a715-d74d0f1bb8a8_JIS_第1水準漢字_2965.csv"

# charset.txt: sjis -> (unicode, char)
ch_of = {}
with open(os.path.join(HERE, 'charset.txt'), encoding='utf-8') as f:
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) >= 3 and p[1].startswith('U+'):
            ch_of[int(p[0], 16)] = (int(p[1][2:], 16), p[2])

# 字体码表（实际编译进 ELF 的）
fsrc = open(os.path.normpath(os.path.join(HERE, '..', 'cn_font.c')), encoding='utf-8').read()
m = re.search(r'cn_font_codes\[CN_FONT_COUNT\]\s*=\s*\{(.*?)\};', fsrc, re.S)
font_codes = set(int(x, 16) for x in re.findall(r'0x([0-9A-Fa-f]{4})', m.group(1)))

rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig')))
missing_charset = []   # SJIS 码不在 charset.txt
missing_font = []      # 在 charset 但不在字体码表
mismatch = []          # 码在但字符对不上
for r in rows:
    sjis = int(r['Shift_JIS_hex'], 16)
    kan = r['漢字']
    if sjis not in ch_of:
        missing_charset.append((r['No.'], kan, r['Shift_JIS_hex'], r['Unicode']))
        continue
    cp, ch = ch_of[sjis]
    if chr(cp) != kan:
        mismatch.append((kan, chr(cp), r['Shift_JIS_hex']))
    if sjis not in font_codes:
        missing_font.append((kan, r['Shift_JIS_hex']))

print('CSV 共 %d 字' % len(rows))
print('charset.txt 缺 %d: %s' % (len(missing_charset),
      ' '.join('%s(%s)' % (k, s) for _, k, s, _ in missing_charset) or '(无)'))
print('字体码表缺 %d: %s' % (len(missing_font),
      ' '.join('%s(%s)' % (k, s) for k, s in missing_font) or '(无)'))
print('码在但字符不一致 %d: %s' % (len(mismatch),
      ' '.join('CSV:%s≠库:%s(%s)' % t for t in mismatch) or '(无)'))
