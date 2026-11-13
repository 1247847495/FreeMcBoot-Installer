# -*- coding: utf-8 -*-
"""临时排查: 找 FastBoot / ÿ3 Return / 三图标 tooltip 的所有出现位置"""
lines = open(r"..\config.c", "rb").read().decode("latin-1").split("\n")
Y = "\xff"
for i, l in enumerate(lines, 1):
    if ('"FastBoot"' in l
            or ('%s", "Return"' in l and Y + '3' in l)
            or (Y + '1:%s ' + Y + '0:%s ' + Y + '2:%s' in l)):
        print(i, repr(l.strip()[:130]))
