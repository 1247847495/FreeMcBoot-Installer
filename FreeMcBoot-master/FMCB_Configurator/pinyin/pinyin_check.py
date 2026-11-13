# -*- coding: utf-8 -*-
"""查某几个字分别挂在哪些拼音音节下（普通页可见块 vs 全部）。"""
import io, os, re, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
cs = {}
for line in io.open(os.path.join(HERE, 'charset.txt'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 3:
        cs[int(p[1][2:], 16)] = int(p[0], 16)

spec = importlib.util.spec_from_file_location('gf', os.path.join(HERE, 'gen_font.py'))
gf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gf)

src = io.open(os.path.join(HERE, '..', 'cn_pinyin.c'), encoding='utf-8').read()
pool = ''.join(re.findall(r'"(.*?)"', re.search(r'cn_py_pool\[\] =\n((?:\t".*"\n)+);', src, re.S).group(1)))
pool = pool.replace('\\0', '\0')
syls = [s for s in pool.split('\0') if s]
start = [int(x) for x in re.findall(r'\d+', re.search(r'cn_py_start\[CN_PY_COUNT \+ 1\] = \{(.*?)\};', src, re.S).group(1))]
l1 = [int(x) for x in re.findall(r'\d+', re.search(r'cn_py_l1\[CN_PY_COUNT\] = \{(.*?)\};', src, re.S).group(1))]
pairs = [int(x, 16) for x in re.findall(r'0x[0-9A-F]{4}', re.search(r'cn_py_pairs\[CN_PY_PAIRS\] = \{(.*?)\};', src, re.S).group(1))]

rev = {}
for cp, sj in cs.items():
    rev.setdefault(sj, cp)

def disp(sj):
    return gf.to_display(chr(rev.get(sj, 0x3013)))

# group -> (visible set, full set)
groups = {}
for i, syl in enumerate(syls):
    lo_i, hi_i = start[i], start[i+1]
    cut = lo_i + l1[i]
    groups[syl] = ({disp(pairs[k]) for k in range(lo_i, cut)},
                   {disp(pairs[k]) for k in range(lo_i, hi_i)})

name = sys.argv[1] if len(sys.argv) > 1 else u'中文列表强化版'
for ch in name:
    if ord(ch) < 0x80:
        print('%s  ASCII（符号页输，非拼音）' % ch)
        continue
    vis = [s for s in sorted(groups) if ch in groups[s][0]]
    hid = [s for s in sorted(groups) if ch in groups[s][1] and ch not in groups[s][0]]
    s = '%s  普通页可打: %s' % (ch, ','.join(vis) if vis else '(无!)')
    if hid:
        s += '   仅5009页: %s' % ','.join(hid)
    print(s)
