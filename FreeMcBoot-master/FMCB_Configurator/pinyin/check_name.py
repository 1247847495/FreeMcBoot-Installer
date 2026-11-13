# -*- coding: utf-8 -*-
"""检查一个名字里每个字实际提交的 SJIS 码、存储的日文形、级别。
模拟 gen_pinyin.py 的 best 反查（一级优先、SJIS 升序）。"""
import io, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
cs = {}
for line in io.open(os.path.join(HERE, 'charset.txt'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 3:
        cs[int(p[1][2:], 16)] = int(p[0], 16)

spec = importlib.util.spec_from_file_location('gf', os.path.join(HERE, 'gen_font.py'))
gf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gf)

def lvl(sjis):
    hi, lo = sjis >> 8, sjis & 0xFF
    return 0 if (hi <= 0x97 or (hi == 0x98 and lo <= 0x9E)) else 1

def kuten(sjis):
    hi, lo = sjis >> 8, sjis & 0xFF
    hi = (hi - (0xC1 if hi >= 0xE0 else 0x81)) * 2
    if lo >= 0x9F:
        hi += 1; lo -= 0x9F
    elif lo >= 0x80:
        lo -= 0x41
    else:
        lo -= 0x40
    return hi + 1, lo + 1

# 反查：显示形 -> 最佳提交码（与输入法候选一致）
best = {}
for cp, sjis in cs.items():
    d = gf.to_display(chr(cp))
    try:
        d.encode('gb2312')
    except UnicodeEncodeError:
        continue
    if d not in best or (lvl(sjis), sjis) < best[d]:
        best[d] = (lvl(sjis), sjis, cp)

import sys
name = sys.argv[1] if len(sys.argv) > 1 else u'中文列表强化版峰哥'
print('%-4s %-8s %-10s %-10s %-6s %s' % ('显示', 'SJIS', '区点', '存储形', '级别', '判定'))
for ch in name:
    if ord(ch) < 0x80:
        print('%-4s %-8s %-10s %-10s %-6s %s' % (ch, 'ASCII', '-', '-', '-', '原样'))
        continue
    b = best.get(ch)
    if not b:
        print('%-4s %-8s %-10s %-10s %-6s %s' % (ch, '??', '-', '-', '-', '!!! 打不出'))
        continue
    lv, sj, cp = b
    ku, ten = kuten(sj)
    stored = chr(cp)
    verdict = '同形' if stored == ch else '日文形(%s)' % stored
    lvs = '一级' if lv == 0 else '二级!'
    print('%-4s %-8s %-10s %-10s %-6s %s' % (ch, '%04X' % sj, '区%d点%d' % (ku, ten), stored, lvs, verdict))
