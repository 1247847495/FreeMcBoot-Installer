# -*- coding: utf-8 -*-
"""
渲染 charset.txt 中全部字符为 16x16 1bpp 点阵，生成 cn_font.c / cn_font.h。

- 显示策略：简体字形显示 + SJIS 码存储（所见为简体，保存为日文假字）
  每个字符先经 OpenCC t2s 转简体；日文新字体/特有形用手工映射表兜底；
  仍无映射的和字/生僻字保留原字形渲染。
- 字体：NotoSansSC（简体字形）
- 格式：每字 32 字节，行主序，每行 2 字节，MSB=最左像素
- 布局：自定义紧凑格式 + SJIS 码升序表（运行时二分查找），码=SJIS 不变
- 附带 font_preview.png 供人工抽查
"""
import os
from PIL import Image, ImageDraw, ImageFont
from opencc import OpenCC

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..'))  # FMCB_Configurator source dir
FONT_PATH = r'C:\Windows\Fonts\msyh.ttc'  #微软雅黑常规体：笔画细，16px 屏显清晰

_cc = OpenCC('t2s')

#日文新字体/特有形 -> 简体（OpenCC t2s 覆盖不到的部分）
JP2CN = {
    '亜': '亚', '唖': '哑', '穐': '秋', '悪': '恶', '鯵': '鲹', '圧': '压',
    '囲': '围', '壱': '壹', '稲': '稻', '隠': '隐', '欝': '郁', '叡': '睿',
    '営': '营', '栄': '荣', '駅': '驿', '円': '圆', '焔': '焰', '縁': '缘',
    '艶': '艳', '薗': '园', '塩': '盐', '汚': '污', '応': '应', '鴬': '莺',
    '鴎': '鸥', '穏': '稳', '仮': '假', '価': '价', '菓': '果', '壊': '坏',
    '廻': '回', '懐': '怀', '絵': '绘', '拡': '扩', '撹': '搅', '覚': '觉',
    '楽': '乐', '潟': '泻', '渇': '渴', '鞄': '包', '竃': '灶', '栢': '柏',
    '苅': '刈', '勧': '劝', '巻': '卷', '寛': '宽', '歓': '欢', '潅': '灌',
    '観': '观', '諌': '谏', '関': '关', '陥': '陷', '巌': '岩', '帰': '归',
    '気': '气', '亀': '龟', '戯': '戏', '犠': '牺', '拠': '据', '挙': '举',
    '彊': '强', '郷': '乡', '尭': '尧', '暁': '晓', '倶': '俱', '駆': '驱',
    '駈': '驱', '勲': '勋', '薫': '熏', '珪': '硅', '恵': '惠', '渓': '溪',
    '経': '经', '継': '继', '繋': '系', '蛍': '萤', '軽': '轻', '頚': '颈',
    '鶏': '鸡', '撃': '击', '倹': '俭', '剣': '剑', '圏': '圈', '検': '检',
    '権': '权', '県': '县', '険': '险', '顕': '显', '験': '验', '鹸': '碱',
    '厳': '严', '戸': '户', '呉': '吴', '娯': '娱', '碁': '棋', '効': '效',
    '広': '广', '鉱': '矿', '砿': '矿', '黒': '黑', '梱': '捆', '歳': '岁',
    '済': '济', '砕': '碎', '斎': '齐', '剤': '剂', '咲': '笑', '埼': '崎',
    '搾': '榨', '桜': '樱', '雑': '杂', '皐': '皋', '桟': '栈', '讃': '赞',
    '賛': '赞', '姉': '姐', '歯': '齿', '児': '儿', '実': '实', '舎': '舍',
    '釈': '释', '呪': '咒', '収': '收', '繍': '绣', '讐': '仇', '従': '从',
    '渋': '涩', '獣': '兽', '縦': '纵', '粛': '肃', '楯': '盾', '処': '处',
    '奨': '奖', '渉': '涉', '焼': '烧', '粧': '妆', '醤': '酱', '乗': '乘',
    '剰': '剩', '壌': '壤', '嬢': '娘', '浄': '净', '畳': '叠', '譲': '让',
    '醸': '酿', '靭': '韧', '図': '图', '粋': '粹', '酔': '醉', '髄': '髓',
    '瀬': '濑', '斉': '齐', '摂': '摄', '専': '专', '戦': '战', '繊': '纤',
    '賎': '贱', '銭': '钱', '曽': '曾', '疎': '疏', '捜': '搜', '挿': '插',
    '掻': '挠', '巣': '巢', '痩': '瘦', '窓': '窗', '総': '总', '聡': '聪',
    '荘': '庄', '鎗': '枪', '騒': '骚', '増': '增', '臓': '脏', '蔵': '藏',
    '続': '续', '楕': '椭', '駄': '驮', '騨': '驒', '対': '对', '帯': '带',
    '滝': '泷', '択': '择', '沢': '泽', '単': '单', '団': '团', '弾': '弹',
    '値': '值', '遅': '迟', '鋳': '铸', '庁': '厅', '徴': '征', '聴': '听',
    '勅': '敕', '壷': '壶', '逓': '递', '鉄': '铁', '転': '转', '伝': '传',
    '兎': '兔', '妬': '妒', '嶋': '岛', '闘': '斗', '働': '动', '徳': '德',
    '涜': '渎', '読': '读', '呑': '吞', '縄': '绳', '弐': '贰', '韮': '韭',
    '撚': '捻', '廼': '乃', '埜': '野', '嚢': '囊', '悩': '恼', '脳': '脑',
    '覗': '觑', '覇': '霸', '廃': '废', '拝': '拜', '楳': '梅', '売': '卖',
    '蝿': '蝇', '溌': '泼', '発': '发', '醗': '酿', '髪': '发', '抜': '拔',
    '釆': '采', '晩': '晚', '毘': '毗', '姫': '姬', '氷': '冰', '鋲': '铆',
    '冨': '富', '払': '拂', '仏': '佛', '雰': '氛', '変': '变', '辺': '边',
    '舗': '铺', '歩': '步', '穂': '穗', '倣': '仿', '砲': '炮', '豊': '丰',
    '頬': '颊', '毎': '每', '槙': '桢', '侭': '尽', '満': '满', '姪': '侄',
    '麺': '面', '黙': '默', '戻': '戾', '薬': '药', '訳': '译', '鑓': '枪',
    '揺': '摇', '様': '样', '頼': '赖', '覧': '览', '竜': '龙', '両': '两',
    '猟': '猎', '瞭': '了', '燐': '磷', '隣': '邻', '瑠': '琉', '塁': '垒',
    '涙': '泪', '隷': '隶', '霊': '灵', '齢': '龄', '暦': '历', '歴': '历',
    '労': '劳', '錬': '炼', '篭': '笼', '蝋': '蜡', '脇': '胁', '椀': '碗',
    '榎': '榎', '袴': '袴', '麹': '麴', '畑': '畑',
}


def to_display(ch):
    """日文假字(存储形) -> 简体显示形。转不了的和字原样返回。"""
    s = _cc.convert(ch)
    if s != ch:
        return s
    return JP2CN.get(ch, ch)


def render_16x16(ch, font):
    """渲染单字为 16x16 1bpp 32 字节，字形墨迹中心对齐 (8,8)。"""
    img = Image.new('L', (40, 40), 0)
    d = ImageDraw.Draw(img)
    d.text((20, 20), ch, font=font, anchor='mm', fill=255)
    bbox = img.getbbox()
    if bbox is None:
        return bytes(32)
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    out = Image.new('L', (16, 16), 0)
    out.paste(img.crop((x0, y0, x1, y1)), (8 - w // 2, 8 - h // 2))  # 墨迹中心对齐 (8,8)
    px = out.load()
    data = bytearray(32)
    for y in range(16):
        row = 0
        for x in range(16):
            row = (row << 1) | (1 if px[x, y] >= 128 else 0)  #阈值128: 只保留笔画核心
        data[y * 2] = (row >> 8) & 0xFF
        data[y * 2 + 1] = row & 0xFF
    return bytes(data)


def main():
    entries = []
    with open(os.path.join(HERE, 'charset.txt'), encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 3:
                entries.append((int(parts[0], 16), parts[2]))
    assert entries, 'charset.txt 为空，先运行 gen_charset.py'

    # ASCII 固定补入（符号页输入 + - . 用；charset.txt 只含双字节 SJIS，
    # 曾靠手工往 charset.txt 加行，重生成会丢，改为在这里固定追加）
    for extra in (0x2B, 0x2D, 0x2E):  #'+' '-' '.'
        if not any(s == extra for s, _ in entries):
            entries.append((extra, chr(extra)))
    #中文特有字（无 JIS 存储形）：分配空闲 SJIS 槽位，gen_gbk.py 需同步
    if not any(s == 0x9867 for s, _ in entries):
        entries.append((0x9867, '卡'))  #0x9867 空闲槽位
    entries.sort(key=lambda e: e[0])

    font = ImageFont.truetype(FONT_PATH, 16)

    codes = []
    bits = []
    disp_stats = {'jp_left': []}
    for sjis, ch in entries:
        disp = to_display(ch)
        if disp == ch and 0x4E00 <= ord(ch) <= 0x9FFF:
            #汉字且没有简体映射（和字/生僻字），记录备查
            try:
                ch.encode('gb2312')
            except UnicodeEncodeError:
                disp_stats['jp_left'].append(ch)
        codes.append(sjis)
        bits.append(render_16x16(disp, font))

    n = len(codes)
    # ---- cn_font.h ----
    with open(os.path.join(SRC, 'cn_font.h'), 'w', encoding='utf-8') as f:
        f.write('//Auto-generated by gen_font.py. DO NOT EDIT.\n')
        f.write('#ifndef CN_FONT_H\n#define CN_FONT_H\n\n')
        f.write('#define CN_FONT_COUNT %d\n\n' % n)
        f.write('extern const unsigned short cn_font_codes[CN_FONT_COUNT]; //SJIS codes, ascending\n')
        f.write('extern const unsigned char cn_font_bits[CN_FONT_COUNT][32]; //16x16 1bpp, MSB=left\n\n')
        f.write('#endif\n')

    # ---- cn_font.c ----
    with open(os.path.join(SRC, 'cn_font.c'), 'w', encoding='utf-8') as f:
        f.write('//Auto-generated by gen_font.py. DO NOT EDIT.\n')
        f.write('#include "cn_font.h"\n\n')
        f.write('const unsigned short cn_font_codes[CN_FONT_COUNT] = {\n')
        for i in range(0, n, 10):
            f.write('\t' + ','.join('0x%04X' % c for c in codes[i:i+10]) + ',\n')
        f.write('};\n\n')
        f.write('const unsigned char cn_font_bits[CN_FONT_COUNT][32] = {\n')
        for b in bits:
            f.write('\t{' + ','.join('0x%02X' % v for v in b) + '},\n')
        f.write('};\n')

    # ---- 预览图：前 300 字 ----
    cols, rows, sc = 25, 12, 2
    pv = Image.new('L', (cols * 16, rows * 16), 0)
    for i, (sjis, ch) in enumerate(entries[:cols * rows]):
        pv.paste(Image.frombytes('1', (16, 16), bits[i]), ((i % cols) * 16, (i // cols) * 16))
    pv = pv.resize((pv.width * sc, pv.height * sc), Image.NEAREST)
    pv.save(os.path.join(HERE, 'font_preview.png'))

    print('生成 %d 字点阵（简体字形+SJIS码），cn_font.c = %.1f KB 源码'
          % (n, os.path.getsize(os.path.join(SRC, 'cn_font.c')) / 1024))
    print('保留日文原形的和字/生僻字 %d 个: %s'
          % (len(disp_stats['jp_left']), ''.join(disp_stats['jp_left'][:80])))


if __name__ == '__main__':
    main()
