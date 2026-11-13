#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
fix_y255.py - 修复被 UTF-8 重存破坏的 0xFF 按钮图标引导符 (ÿ)

背景:
  filer.c / draw.c 在中文化编辑时被以 UTF-8 重新保存，字符串中的
  单字节 0xFF (ÿ，uLE 按钮图标引导符) 变成了 0xC3 0xBF。运行时
  cn_decode 把 0xC3 0xBF 当 GBK 双字节解码成 "每"，于是界面出现
  "每0:OK"、"每4 FMCB 1.9 test 22" 之类的乱码。

修复:
  把字节 0xC3 0xBF 替换为 C 源码文本  \xFF" "
  (\xFF 转义 + 关闭/重开字符串字面量)，既还原 0xFF 字节，又避免
  \x 转义贪婪吞掉后面紧跟的十六进制字符 (如 "ÿ0" 的 '0')。
  UTF-8 的自同步性保证合法 UTF-8 文件中 0xC3 0xBF 必是 ÿ。

用法:
  python fix_y255.py          仅扫描
  python fix_y255.py --do     执行替换
"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, ".."))

BAD = b"\xc3\xbf"      # UTF-8 编码的 ÿ (U+00FF)
REPL = b'\\xFF" "'     # ->  "\xFF" "...   (字符串拆分防转义贪婪)

# 只替换这两个文件：其中的 C3BF 出现在活代码字符串里，运行时被 GBK
# 解码成 "每"。其它文件 (launchelf.h / ui_text.h) 的 C3BF 仅在注释中，
# 无运行时影响，不改。
FIX_TARGETS = {"filer.c", "draw.c"}


def iter_sources():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d != "pinyin"]
        for name in sorted(filenames):
            if name.endswith((".c", ".h")):
                yield os.path.join(dirpath, name)


def line_no(data, pos):
    return data.count(b"\n", 0, pos) + 1


def main():
    do = "--do" in sys.argv
    total = 0
    for path in iter_sources():
        with open(path, "rb") as f:
            data = f.read()
        n = data.count(BAD)
        try:
            text = data.decode("utf-8")
            valid = True
        except UnicodeDecodeError as e:
            valid = False
            # 含原始非 UTF-8 字节(如原有的单字节 0xFF / SJIS)——仅报告
            if n == 0:
                print("%-16s 原始非UTF-8字节(非C3BF)，原有编码保留" % os.path.basename(path))
                continue
            print("%-16s %d 处C3BF，但整体非合法UTF-8(%s)，跳过！" %
                  (os.path.basename(path), n, e))
            continue
        if n == 0:
            na = [i + 1 for i, ln in enumerate(text.split("\n"))
                  if any(ord(c) >= 0x80 for c in ln)]
            if na:
                print("%-16s 无C3BF；其它非ASCII行(注释无害): %s" %
                      (os.path.basename(path), na))
            continue
        pos, hits = 0, []
        while True:
            i = data.find(BAD, pos)
            if i < 0:
                break
            hits.append(line_no(data, i))
            pos = i + 2
        # 除 ÿ 外的其它非 ASCII 行（如 UTF-8 中文注释）
        na = [i + 1 for i, ln in enumerate(text.split("\n"))
              if any(ord(c) >= 0x80 for c in ln) and ln.find("\xff") < 0]
        print("%-16s %d 处 ÿ，行号: %s" % (os.path.basename(path), n, hits))
        if na:
            print("%-16s 其它非ASCII行: %s" % ("", na))
        total += n
        if do:
            if os.path.basename(path) not in FIX_TARGETS:
                print("%-16s -> 仅注释，跳过替换" % "")
                continue
            with open(path, "wb") as f:
                f.write(data.replace(BAD, REPL))
            print("%-16s -> 已替换 %d 处" % ("", n))
    print("合计: %d 处%s" % (total, "" if do else "  (dry-run，加 --do 执行)"))


if __name__ == "__main__":
    main()
