# -*- coding: utf-8 -*-
"""Restore English CNF key "FastBoot" in loadConfig_fmcb (config.c).

The i18n script wrongly replaced the CNF parser's key comparison with the
Chinese label UIT_FASTBOOT, so a saved "FastBoot = 0" line never matched and
the option always fell back to its default (1 = ON).
Byte-level edit: config.c contains raw 0xFF bytes, text editors would corrupt it.
"""

PATH = r"k:\FreeMcBoot-Installer-master\FreeMcBoot-master\FMCB_Configurator\config.c"

with open(PATH, "rb") as f:
    data = f.read()

old = b'if (!strcmp(name,UIT_FASTBOOT)) {'
new = b'if (!strcmp(name,"FastBoot")) {'
assert data.count(old) == 1, data.count(old)
n_ff = data.count(b"\xff")
data = data.replace(old, new)
assert data.count(b"\xff") == n_ff, "raw 0xFF byte count changed"
assert data.count(b'"FastBoot"') == 1
with open(PATH, "wb") as f:
    f.write(data)
print('OK: CNF load key restored to "FastBoot" (display label UIT_FASTBOOT untouched)')
