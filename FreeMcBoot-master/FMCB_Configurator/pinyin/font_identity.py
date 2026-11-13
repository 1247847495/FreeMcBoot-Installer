# -*- coding: utf-8 -*-
# 验证字体身份 + 繁简对照渲染
from PIL import Image, ImageDraw, ImageFont

FONT = r'k:\FreeMcBoot-Installer-master\installer_res\__base\lang\NotoSansJP-Bold.otf'
f = ImageFont.truetype(FONT, 16)
print('family:', f.getname())

# 对比组：U+904A遊/U+6E38游  U+8A2D設/U+8BBE设  U+9332錄/U+5F55录
pairs = [(u'遊', u'游'), (u'設', u'设'), (u'錄', u'录'), (u'記', u'记'), (u'國', u'国')]
img = Image.new('L', (len(pairs) * 44 + 10, 44), 255)
d = ImageDraw.Draw(img)
for i, (a, b) in enumerate(pairs):
    d.text((i * 44 + 4, 2), a, font=f, fill=0)      # 上排：繁/日形
    d.text((i * 44 + 24, 2), b, font=f, fill=0)     # 上排右：简形
img = img.resize((img.width * 4, img.height * 4), Image.NEAREST)
img.save(r'k:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\pinyin\font_identity.png')
print('saved font_identity.png (每组左=繁/日字形 右=简体字形)')
