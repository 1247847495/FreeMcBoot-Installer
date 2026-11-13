# -*- coding: utf-8 -*-
"""Fix OSDSYS settings screen cursor alignment in config.c (byte-level).

The draw section advances y by (FONT_HEIGHT+2) per row (plus half/double
gaps), but the cursor section computed Y from raw FONT_HEIGHT multiples,
so the cursor drifted up to 28px above the text rows.

Fix: anchor all lower-screen cursor rows to base_y = Y of the selected
colour row (s==SEL_COL), then add whole pitches per row:
  s=9        -> base_y                          (=210 rel MSY, FH=16)
  s=10..13   -> base_y                          (=210, RGBA numbers)
  s=15..18   -> base_y + FONT_HEIGHT            (=226, unselected numbers)
  s=14       -> base_y + (FONT_HEIGHT + 2)      (=228, unselected label)
  s=19       -> base_y + (FONT_HEIGHT + 2)*2    (=246)
  s=20..22   -> base_y + (FONT_HEIGHT + 2)*3    (=264)
  s=23..25   -> base_y + (FONT_HEIGHT + 2)*4    (=282)
  s=26       -> base_y + (FONT_HEIGHT + 2)*5 + FONT_HEIGHT/2 (=308)
Rows s=0..8 already match the drawn positions and stay unchanged.
"""

PATH = r"k:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\config.c"

with open(PATH, "rb") as f:
    data = f.read()

assert data.count(b"base_y") == 0, "unexpected existing base_y"
n_ff = data.count(b"\xff")
lines = data.split(b"\n")

# Region anchors (line numbers as in the current file)
assert b"if(event||post_event){" in lines[3878], lines[3878]
assert b"clrScr" in lines[3881], lines[3881]
assert b"y = Menu_start_y;" in lines[3887], lines[3887]
assert b"//Cursor positioning section" in lines[3981], lines[3981]
assert b"drawChar(LEFT_CUR" in lines[4037], lines[4037]


def replace_line(no, old_code, new_code):
    i = no - 1
    raw = lines[i]
    assert raw.endswith(b"\r"), (no, raw)
    body = raw[:-1].rstrip()
    tabs = body[: len(body) - len(body.lstrip(b"\t"))]
    assert body == tabs + old_code, (no, body)
    lines[i] = tabs + new_code + b"\r"
    print("L%-4d %s" % (no, new_code.decode()))


replace_line(3984, b"y = Menu_start_y + (SEL_COL+3)*FONT_HEIGHT;",
             b"y = base_y;")
replace_line(3995, b"y = Menu_start_y + (SEL_COL+4)*FONT_HEIGHT;",
             b"y = base_y + FONT_HEIGHT;")
replace_line(4010, b"y += FONT_HEIGHT + 2;",
             b"y = base_y;")
replace_line(4013, b"y = Menu_start_y + (UNSEL_COL-2)*FONT_HEIGHT + FONT_HEIGHT;",
             b"y = base_y + (FONT_HEIGHT + 2);")
replace_line(4016, b"y = Menu_start_y + (UNSEL_COL-1)*FONT_HEIGHT + FONT_HEIGHT;",
             b"y = base_y + (FONT_HEIGHT + 2)*2;")
replace_line(4019, b"y = Menu_start_y + (UNSEL_COL-1)*FONT_HEIGHT + FONT_HEIGHT*2;",
             b"y = base_y + (FONT_HEIGHT + 2)*3;")
replace_line(4027, b"y = Menu_start_y + (UNSEL_COL-1)*FONT_HEIGHT + FONT_HEIGHT*3;",
             b"y = base_y + (FONT_HEIGHT + 2)*4;")
replace_line(4035, b"y = Menu_start_y + (UNSEL_COL)*FONT_HEIGHT + FONT_HEIGHT*3 + FONT_HEIGHT/2;",
             b"y = base_y + (FONT_HEIGHT + 2)*5 + FONT_HEIGHT/2;")

# Insert base_y declaration as first statement of the display block
# (right after the if(event||post_event){ line), preserving indentation.
anchor = lines[3878]
tabs = anchor[: len(anchor) - len(anchor.lstrip(b"\t"))]
assert lines[3881].lstrip(b"\t").startswith(b"clrScr") and \
       lines[3881].startswith(tabs + b"\t"), lines[3881]
decl = (tabs + b"\t"
        + b"int base_y = Menu_start_y + (SEL_COL+1)*(FONT_HEIGHT + 2)"
          b" + FONT_HEIGHT/2 + FONT_HEIGHT/2 + FONT_HEIGHT - 2;"
          b" //cursor anchor: Y of selected-colour row\r")
lines.insert(3879, decl)

out = b"\n".join(lines)
assert out.count(b"\xff") == n_ff, "raw 0xFF byte count changed"
assert out.count(b"base_y") == 9, out.count(b"base_y")
with open(PATH, "wb") as f:
    f.write(out)
print("OK: 8 cursor rows pinned to drawn text positions; base_y declared")
