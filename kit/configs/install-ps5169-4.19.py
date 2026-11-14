#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install-ps5169-4.19.py —— 在 4.19.325 树里安装 PS5169 redriver 驱动

做的事（幂等，可重复执行）：
  1. 复制 drivers/ssusb-redriver-ps5169.c  ->  <KERNEL>/drivers/usb/misc/
  2. Kconfig 增加 config USB_REDRIVER_PS5169（select REGMAP_I2C）
  3. Makefile 增加 obj-$(CONFIG_USB_REDRIVER_PS5169) += ssusb-redriver-ps5169.o
  4. phy-msm-ssusb-qmp.c: IS_BUILTIN(CONFIG_USB_REDRIVER_NB7VPQ904M) -> PS5169
  5. .config / arch/arm64/configs/*：NB7VPQ904M 关、PS5169=y

用法：
    python3 install-ps5169-4.19.py <KERNEL_ROOT>            # dry-run
    python3 install-ps5169-4.19.py <KERNEL_ROOT> --apply
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_C = HERE / "drivers" / "ssusb-redriver-ps5169.c"
DST_NAME = "ssusb-redriver-ps5169.c"
OLD_SYM = "CONFIG_USB_REDRIVER_NB7VPQ904M"
NEW_SYM = "CONFIG_USB_REDRIVER_PS5169"

KCONFIG_BLOCK = """config USB_REDRIVER_PS5169
\ttristate "USB 3.1 Gen1/Gen2 10Gbps re-driver driver for PS5169"
\tdepends on USB_PHY
\tselect REGMAP_I2C
\thelp
\t  Say Y here if you want to support USB super speed re-driver PS5169.
\t  This is the re-driver used on TB371FC (compatible "hq_redriver,ps5169").
"""

MAKEFILE_LINE = "obj-$(CONFIG_USB_REDRIVER_PS5169)\t+= ssusb-redriver-ps5169.o\n"


def read(p):
    return p.read_text(encoding="utf-8", errors="surrogateescape")


def write(p, s):
    p.write_text(s, encoding="utf-8", errors="surrogateescape")


def install_source(root, apply):
    dst = root / "drivers" / "usb" / "misc" / DST_NAME
    if not SRC_C.exists():
        sys.exit("source missing: %s" % SRC_C)
    same = dst.exists() and dst.read_bytes() == SRC_C.read_bytes()
    print("[src ] %s -> %s%s" % (SRC_C.name, dst,
                                 "  (already identical)" if same else ""))
    if apply and not same:
        shutil.copyfile(SRC_C, dst)


def patch_kconfig(root, apply):
    p = root / "drivers" / "usb" / "misc" / "Kconfig"
    s = read(p)
    if "config USB_REDRIVER_PS5169" in s:
        print("[kcfg] already present")
        return
    anchor = "config USB_REDRIVER_PI2DPX"
    if anchor not in s:
        anchor = "config USB_QTI_KS_BRIDGE"
    if anchor not in s:
        sys.exit("Kconfig anchor not found")
    s = s.replace(anchor, KCONFIG_BLOCK + "\n" + anchor, 1)
    print("[kcfg] insert USB_REDRIVER_PS5169 before %r" % anchor)
    if apply:
        write(p, s)


def patch_makefile(root, apply):
    p = root / "drivers" / "usb" / "misc" / "Makefile"
    s = read(p)
    if "CONFIG_USB_REDRIVER_PS5169" in s:
        print("[make] already present")
        return
    anchor = "obj-$(CONFIG_USB_REDRIVER_NB7VPQ904M)"
    idx = s.find(anchor)
    if idx < 0:
        sys.exit("Makefile anchor not found")
    end = s.find("\n", idx) + 1
    s = s[:end] + MAKEFILE_LINE + s[end:]
    print("[make] add %s" % MAKEFILE_LINE.strip())
    if apply:
        write(p, s)


def patch_qmp(root, apply):
    p = root / "drivers" / "usb" / "phy" / "phy-msm-ssusb-qmp.c"
    if not p.exists():
        print("[qmp ] not found, skip")
        return
    s = read(p)
    n = s.count(OLD_SYM)
    if n == 0:
        print("[qmp ] already on PS5169")
        return
    s = s.replace(OLD_SYM, NEW_SYM)
    print("[qmp ] %d x %s -> %s" % (n, OLD_SYM, NEW_SYM))
    if apply:
        write(p, s)


def patch_config(path, apply):
    if not path.exists():
        return
    s = read(path)
    old = "CONFIG_USB_REDRIVER_NB7VPQ904M"
    changed = False

    if re.search(r"^CONFIG_USB_REDRIVER_NB7VPQ904M=", s, re.M):
        s = re.sub(r"^CONFIG_USB_REDRIVER_NB7VPQ904M=.*$",
                   "# CONFIG_USB_REDRIVER_NB7VPQ904M is not set", s, flags=re.M)
        changed = True
    elif old not in s:
        s += "\n# CONFIG_USB_REDRIVER_NB7VPQ904M is not set\n"
        changed = True

    if re.search(r"^CONFIG_USB_REDRIVER_PS5169=", s, re.M):
        pass
    else:
        s = re.sub(r"^# CONFIG_USB_REDRIVER_PS5169 is not set$",
                   "CONFIG_USB_REDRIVER_PS5169=y", s, flags=re.M)
        if "CONFIG_USB_REDRIVER_PS5169=" not in s:
            s += "CONFIG_USB_REDRIVER_PS5169=y\n"
        changed = True

    print("[cfg ] %s%s" % (path, "" if changed else "  (unchanged)"))
    if apply and changed:
        write(path, s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kernel_root")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    root = Path(a.kernel_root).resolve()
    if not (root / "drivers" / "usb" / "misc" / "Kconfig").exists():
        sys.exit("not a kernel tree: %s" % root)

    print("kernel: %s  (%s)" % (root, "APPLY" if a.apply else "DRY-RUN"))
    install_source(root, a.apply)
    patch_kconfig(root, a.apply)
    patch_makefile(root, a.apply)
    patch_qmp(root, a.apply)

    patch_config(root / ".config", a.apply)
    for c in (root / "arch" / "arm64" / "configs").glob("*"):
        if c.is_file() and ("tb371fc" in c.name or c.name.startswith("vendor")):
            patch_config(c, a.apply)

    print("\ndone" + ("" if a.apply else " (nothing written; add --apply)"))


if __name__ == "__main__":
    main()
