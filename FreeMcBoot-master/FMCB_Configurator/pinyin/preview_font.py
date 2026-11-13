# -*- coding: utf-8 -*-
# 从 cn_font.c 提取指定字的点阵，渲染 PNG 预览（放大4倍）
import re, sys
from PIL import Image

SRC = r'k:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\cn_font.c'
src = open(SRC, encoding='utf-8').read()

# 提取 cn_font_codes 和 cn_font_bits
def u16arr(name):
    g = re.search(name + r'\[[^\]]*\] = \{(.*?)\};', src, re.S).group(1)
    return [int(x, 0) for x in re.findall(r'0x[0-9A-Fa-f]+', g)]

def u8arr(name):
    g = re.search(name + r'\[[^\]]*\](?:\[[^\]]*\])? = \{(.*?)\};', src, re.S).group(1)
    return [int(x, 0) for x in re.findall(r'0x[0-9A-Fa-f]{2}\b', g)]

codes = u16arr('cn_font_codes')
bits = u8arr('cn_font_bits')
print('codes:', len(codes), 'bits:', len(bits), '(expect bits = codes*32)')

chars = u'管遊戯設定記憶中文版画面海直'
SCALE = 4
W = len(chars) * 20 * SCALE
img = Image.new('L', (W, 20 * SCALE), 255)
px = img.load()

for ci, ch in enumerate(chars):
    try:
        sj = int.from_bytes(ch.encode('shift_jis'), 'big')
    except Exception:
        print('skip', ch); continue
    try:
        i = codes.index(sj)
    except ValueError:
        print('NOT IN FONT:', ch); continue
    glyph = bits[i*32:(i+1)*32]
    ox = ci * 20 * SCALE
    for row in range(16):
        b = glyph[row*2]
        for col in range(8):
            if b & (0x80 >> col):
                for dy in range(SCALE):
                    for dx in range(SCALE):
                        px[ox + col*SCALE + dx, row*SCALE + dy] = 0
    # 8-15 行第二字节（16 宽 = 2 字节/行）
    for row in range(16):
        b = glyph[row*2 + 1]
        for col in range(8):
            if b & (0x80 >> col):
                for dy in range(SCALE):
                    for dx in range(SCALE):
                        px[ox + (8+col)*SCALE + dx, row*SCALE + dy] = 0

out = r'k:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\pinyin\font_preview.png'
img.save(out)
print('saved:', out)
