# -*- coding: utf-8 -*-
"""校验 cn_py_l1 切分：每组前 l1 个应全为 level-0，其后全为 level-1。"""
import io, re, importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
cs = {}
for line in io.open(os.path.join(HERE, 'charset.txt'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 3:
        cs[int(p[1][2:], 16)] = int(p[0], 16)

def lvl(sjis):
    hi, lo = sjis >> 8, sjis & 0xFF
    return 0 if (hi <= 0x97 or (hi == 0x98 and lo <= 0x9E)) else 1

spec = importlib.util.spec_from_file_location('gf', os.path.join(HERE, 'gen_font.py'))
gf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gf)

src = io.open(os.path.join(HERE, '..', 'cn_pinyin.c'), encoding='utf-8').read()
pool = ''.join(re.findall(r'"(.*?)"', re.search(r'cn_py_pool\[\] =\n((?:\t".*"\n)+);', src, re.S).group(1)))
pool = pool.replace('\\0', '\0')
syllables = [s for s in pool.split('\0') if s]
start = [int(x) for x in re.findall(r'\d+', re.search(r'cn_py_start\[CN_PY_COUNT \+ 1\] = \{(.*?)\};', src, re.S).group(1))]
l1 = [int(x) for x in re.findall(r'\d+', re.search(r'cn_py_l1\[CN_PY_COUNT\] = \{(.*?)\};', src, re.S).group(1))]
pairs = [int(x, 16) for x in re.findall(r'0x[0-9A-F]{4}', re.search(r'cn_py_pairs\[CN_PY_PAIRS\] = \{(.*?)\};', src, re.S).group(1))]

rev = {}
for cp, sj in cs.items():
    rev.setdefault(sj, cp)

bad = 0
for i in range(len(syllables)):
    lo_i, hi_i = start[i], start[i+1]
    cut = lo_i + l1[i]
    for k in range(lo_i, cut):
        if lvl(pairs[k]) != 0:
            bad += 1; print('BAD L0-in-hidden? syllable %s idx %d' % (syllables[i], k)); break
    for k in range(cut, hi_i):
        if lvl(pairs[k]) != 1:
            bad += 1; print('BAD L1-in-visible? syllable %s idx %d' % (syllables[i], k)); break
print('groups=%d pairs=%d bad=%d' % (len(syllables), len(pairs), bad))

for want in ['zu', 'pa', 'zuo', 'guan']:
    if want not in syllables:
        print('%-5s NOT FOUND' % want); continue
    i = syllables.index(want)
    lo_i, hi_i = start[i], start[i+1]
    cut = lo_i + l1[i]
    vis = ''.join(gf.to_display(chr(rev.get(c, 0x3013))) for c in pairs[lo_i:cut])
    hid = ''.join(gf.to_display(chr(rev.get(c, 0x3013))) for c in pairs[cut:hi_i])
    print('%-5s L1=%d/%d' % (want, l1[i], hi_i - lo_i))
    print('   visible[%s]' % vis)
    print('   hidden  [%s]' % hid)

for ch in [u'\u505a', u'\u6015']:  # 做怕
    sj = cs.get(ord(ch))
    print(repr(ch), 'sjis=%s level=%s' % ('None' if sj is None else '%04X' % sj, '-' if sj is None else lvl(sj)))
