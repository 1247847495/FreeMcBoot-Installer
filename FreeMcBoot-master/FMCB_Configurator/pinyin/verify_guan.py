# -*- coding: utf-8 -*-
# 验证某拼音音节的候选列表（模拟 cn_im_lookup）
import re, sys

SRC = r'k:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\cn_pinyin.c'
src = open(SRC, encoding='utf-8').read()

m = re.search(r'cn_py_pool\[\] =(.*?);', src, re.S)
pool = ''.join(re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1), re.S))
pool = pool.encode('latin-1', 'backslashreplace').decode('unicode_escape')

def arr(name):
    g = re.search(name + r'\[[^\]]*\] = \{(.*?)\};', src, re.S).group(1)
    return [int(x, 0) for x in re.findall(r'0x[0-9A-Fa-f]+|\d+', g)]

offs = arr('cn_py_off')
starts = arr('cn_py_start')
pairs = arr('cn_py_pairs')

syllables = [pool[offs[i]:offs[i+1]].rstrip('\0') for i in range(len(offs)-1)] + [pool[offs[-1]:].rstrip('\0')]
print('syllable count:', len(syllables))

target = sys.argv[1] if len(sys.argv) > 1 else 'guan'
idx = syllables.index(target) if target in syllables else -1
print('%s index: %d' % (target, idx))
if idx >= 0:
    cand = pairs[starts[idx]:starts[idx+1]]
    print('%s candidates: %d' % (target, len(cand)))
    for i, c in enumerate(cand):
        try:
            ch = bytes([c >> 8, c & 0xFF]).decode('shift_jis')
        except Exception:
            ch = '?'
        mark = '  <== ' + (sys.argv[2] if len(sys.argv) > 2 else 'TARGET') if c == 0x8AC7 else ''
        print('%2d %s %s%s' % (i + 1, hex(c), ch, mark))
