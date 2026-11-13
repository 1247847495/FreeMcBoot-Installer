# -*- coding: utf-8 -*-
"""
fix_kb_round8.py - 擦除弹窗两侧的菜单框底边 (byte-level)

问题: 菜单大框(setScrTmp/drawFrame)底边在 Frame_end_y, 横贯全菜单宽
(SCREEN_MARGIN..SCREEN_WIDTH-SCREEN_MARGIN)。键盘弹窗底边恰好也在
Frame_end_y, 但弹窗只占中间 466px —— 菜单底边在弹窗左右两侧各露出
约 70px 的 3px 深色条(与弹窗底边连成一体), 即用户看到的"黑色条"。
修复: 键盘显示段每帧用背景色(color[0], clrScr 同色)覆盖弹窗两侧的
菜单底边区域, 只保留弹窗自己宽度的底边线。
"""
import sys

SRC = r"K:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\filer.c"

OLD = (b"drawFrame(\n"
       b"\t\t\t\tKEY_X, KEY_Y,\n"
       b"\t\t\t\tKEY_X+KEY_W-1, KEY_Y+KEY_H-1, setting->color[1]);\n")

NEW = (b"drawFrame(\n"
       b"\t\t\t\tKEY_X, KEY_Y,\n"
       b"\t\t\t\tKEY_X+KEY_W-1, KEY_Y+KEY_H-1, setting->color[1]);\n"
       b"\t\t\t//Hide the menu frame's bottom edge peeking out left/right\n"
       b"\t\t\t//of this popup (the frame spans the full menu width)\n"
       b"\t\t\tdrawOpSprite(setting->color[0],\n"
       b"\t\t\t\t0, Frame_end_y-LINE_THICKNESS, KEY_X-1, Frame_end_y);\n"
       b"\t\t\tdrawOpSprite(setting->color[0],\n"
       b"\t\t\t\tKEY_X+KEY_W, Frame_end_y-LINE_THICKNESS,\n"
       b"\t\t\t\tSCREEN_WIDTH-1, Frame_end_y);\n")


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    n_ff = data.count(b"\xff")
    cnt = data.count(OLD)
    if cnt != 1:
        print("anchor count=%d (expect 1), ABORT" % cnt)
        sys.exit(1)
    data = data.replace(OLD, NEW)
    if data.count(b"\xff") != n_ff:
        print("0xFF count changed, ABORT")
        sys.exit(1)
    if data.count(NEW) != 1:
        print("insert failed, ABORT")
        sys.exit(1)
    with open(SRC, "wb") as f:
        f.write(data)
    print("written, 0xFF preserved: %d" % n_ff)


if __name__ == "__main__":
    main()
