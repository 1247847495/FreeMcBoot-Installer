# -*- coding: utf-8 -*-
"""从微软雅黑重新生成 font_uLE.c 的 63 个半角假名 8x16 字形。

优先直接渲染半角形（U+FF61-FF9F，笔画粗细与中文一致）；
无半角字形时回退：NFKC 全角形 16x16 相邻列 OR 压缩为 8x16。
"""
import os, sys, unicodedata
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_ULE = os.path.normpath(os.path.join(HERE, '..', 'font_uLE.c'))
FONT_PATH = r'C:\Windows\Fonts\msyh.ttc'
sys.stdout.reconfigure(encoding='utf-8')

font = ImageFont.truetype(FONT_PATH, 16)

def render_bbox(ch, W, H):
    """渲染 ch，墨迹 bbox 居中裁进 WxH，返回 '1' 模式图像。"""
    img = Image.new('L', (40, 40), 0)
    d = ImageDraw.Draw(img)
    d.text((20, 20), ch, font=font, anchor='mm', fill=255)
    bbox = img.getbbox()
    if bbox is None:
        return None
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    if w > W or h > H:
        return None
    out = Image.new('L', (W, H), 0)
    out.paste(img.crop((x0, y0, x1, y1)), (W // 2 - w // 2, H // 2 - h // 2))
    return out.point(lambda p: 255 if p >= 128 else 0).convert('1')

def or_compress(img16):
    """16x16 全角形相邻列 OR 压缩为 8x16。"""
    px = img16.load()
    out = Image.new('1', (8, 16), 0)
    po = out.load()
    for y in range(16):
        for x in range(8):
            po[x, y] = 255 if (px[2*x, y] or px[2*x+1, y]) else 0
    return out

glyphs = []
for b in range(0xA1, 0xE0):
    ch = bytes([b]).decode('cp932')          #半角假名/标点
    g = render_bbox(ch, 8, 16)
    how = 'half'
    if g is None:                             #回退：全角形压缩
        full = unicodedata.normalize('NFKC', ch)
        g16 = render_bbox(full, 16, 16)
        g = or_compress(g16) if g16 else Image.new('1', (8, 16), 0)
        how = 'full'
    px = g.load()
    data = [0] * 16
    for y in range(16):
        v = 0
        for x in range(8):
            v = (v << 1) | (1 if px[x, y] else 0)
        data[y] = v
    glyphs.append((b, ch, data, how))
    if any(data) is False and how == 'half':
        print('WARN empty:', hex(b), repr(ch))

#---- ASCII 预览 ----
for b, ch, data, how in glyphs:
    if b in (0xA1, 0xA5, 0xA6, 0xB1, 0xC4, 0xDD, 0xDF):
        print('--- 0x%02X %s (%s) ---' % (b, ch, how))
        for y in range(16):
            v = data[y]
            print('  ' + ''.join('#' if v & (0x80 >> x) else '.' for x in range(8)))

#---- 写回 font_uLE.c ----
lines = open(FONT_ULE, encoding='utf-8').read().split('\n')
#定位 0x0A1 第一行（行 index = 行号-1；0x0A1 首数据行 348 -> idx 347）
start = None
for i, ln in enumerate(lines):
    if '//char 0x0A1 ==' in ln:
        start = i - 1          #注释在第二行，首行是它的上一行
        break
assert start is not None, '找不到 0x0A1 区块'
end = None
for i, ln in enumerate(lines):
    if '//char 0x0E0 ==' in ln:
        end = i - 2            #跳过 '//Font position 0x0E0' 注释行
        break
assert end is not None, '找不到 0x0E0 边界'
assert end - start + 1 == 63 * 2, '区块行数不对: %d' % (end - start + 1)

new_block = []
for b, ch, data, how in glyphs:
    new_block.append('\t' + ', '.join('0x%02X' % v for v in data[:8]) + ',')
    new_block.append('\t' + ', '.join('0x%02X' % v for v in data[8:]) +
                     ', //char 0x%03X == halfwidth kana' % b)
lines[start:end + 1] = new_block
open(FONT_ULE, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('font_uLE.c 已更新 63 个假名字形（区块 %d..%d）' % (start + 1, end + 1))
