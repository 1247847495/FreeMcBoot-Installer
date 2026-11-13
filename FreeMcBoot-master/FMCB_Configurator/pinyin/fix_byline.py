# -*- coding: utf-8 -*-
"""fix_byline.py - 标题加作者署名 by:anyi；FMCB 1.8 -> 1.9"""
import io

P1 = r"..\config.c"
P2 = r"..\draw.c"

t = io.open(P1, encoding="latin-1", newline="").read()
old1 = 'strcpy(setting->Menu_Title, "Free McBoot Configurator 1.3 beta 6");'
new1 = 'strcpy(setting->Menu_Title, "Free McBoot Configurator 1.3 beta 6 by:anyi");'
assert t.count(old1) == 1, "title anchor: %d" % t.count(old1)
io.open(P1, "w", encoding="latin-1", newline="").write(t.replace(old1, new1))
print("title ok")

t = io.open(P2, encoding="latin-1", newline="").read()
old2 = " FMCB 1.8 test 22 "
assert t.count(old2) == 1, "version anchor: %d" % t.count(old2)
io.open(P2, "w", encoding="latin-1", newline="").write(t.replace(old2, " FMCB 1.9 test 22 "))
print("version ok")
