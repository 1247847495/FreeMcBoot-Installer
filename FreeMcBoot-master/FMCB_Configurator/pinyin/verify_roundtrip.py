# -*- coding: utf-8 -*-
"""round-trip 校验 ui_text.h: 宏字符串按 SJIS 解码后应与注释中文一致"""
import io
import re

bad = 0
n = 0
for line in io.open('../ui_text.h', encoding='utf-8'):
    m = re.match(r'#define (\w+)\s+(.*?)\s+//(.*)$', line.rstrip('\n'))
    if not m:
        continue
    macro, cstr, comment = m.groups()
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', cstr)
    body = ''.join(parts)
    b = bytearray()
    i = 0
    while i < len(body):
        if body[i] == '\\' and body[i + 1] == 'x':
            b.append(int(body[i + 2:i + 4], 16))
            i += 4
        else:
            b.append(ord(body[i]) if ord(body[i]) < 128 else None)
            i += 1
    text = b.decode('shift_jis')
    eng, chn = comment.rsplit(' = ', 1)
    if text != chn:
        print('MISMATCH', macro, repr(text), repr(chn))
        bad += 1
    n += 1
print('checked', n, 'macros, mismatches:', bad)
