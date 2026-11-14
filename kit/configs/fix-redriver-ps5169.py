#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix-redriver-ps5169.py —— 把 redriver 驱动符号名对齐真原厂 (TB371FC ZUI16 / 4.19.157)

背景（实测证据，非推测）
    原厂 config（4.19.157 -perf，从 stock boot.img 的 IKCFG 段解出，亦由用户提供）:
        # CONFIG_USB_REDRIVER_NB7VPQ904M is not set
        CONFIG_USB_REDRIVER_PS5169=y
    原厂 kernel 二进制字符串指纹:
        hq_redriver,ps5169        1
        ssusb redriver            2
        Get redriver ic! ...      1
        Failed to get chip id     1
        redriver_wq               2
        parade,ps5169-redriver    0     <- Motorola 版驱动，原厂没有
        nb7vpq                    0
    结论：驱动**实现内容**本来就对（compatible = hq_redriver,ps5169，
    与联想原厂 DTB / kernel 完全一致），错的是**挂载的 Kconfig 符号名**。
    上游 paladin/11 只有 NB7VPQ904M / PI2DPX；联想的 PS5169 驱动是后来加的，
    仓库里的 ssusb-redriver-nb7vpq904m.c 实际内容就是那股 ps5169 实现。

本脚本做的事（幂等）
    1. drivers/usb/misc/ssusb-redriver-nb7vpq904m.c -> ssusb-redriver-ps5169.c
    2. Kconfig: 新增 config USB_REDRIVER_PS5169（保留 NB7VPQ904M 定义，原厂也未删）
    3. Makefile: obj-$(CONFIG_USB_REDRIVER_PS5169) += ssusb-redriver-ps5169.o
    4. drivers/usb/phy/phy-msm-ssusb-qmp.c: IS_BUILTIN(CONFIG_USB_REDRIVER_*) 改 PS5169
    5. .config / tb371fc/config-v2.2.txt:
           # CONFIG_USB_REDRIVER_NB7VPQ904M is not set
           CONFIG_USB_REDRIVER_PS5169=y

用法:
    python3 fix-redriver-ps5169.py <KERNEL_ROOT>            # dry-run
    python3 fix-redriver-ps5169.py <KERNEL_ROOT> --apply
"""
import argparse
import re
import sys
from pathlib import Path

OLD_C = "ssusb-redriver-nb7vpq904m.c"
NEW_C = "ssusb-redriver-ps5169.c"
OLD_SYM = "CONFIG_USB_REDRIVER_NB7VPQ904M"
NEW_SYM = "CONFIG_USB_REDRIVER_PS5169"

KCONFIG_BLOCK = """
config USB_REDRIVER_PS5169
\ttristate "USB 3.1 Gen2 10Gbps re-driver driver for Parade PS5169"
\tdepends on USB_PHY
\thelp
\t  Say Y here if you want to support USB super speed re-driver PS5169.
\t  This is the re-driver used on TB371FC (compatible "hq_redriver,ps5169").
"""


def read(p):
    return p.read_text(encoding="utf-8", errors="surrogateescape")


def write(p, s):
    p.write_text(s, encoding="utf-8", errors="surrogateescape")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    if not (root / "Makefile").exists():
        sys.exit(f"[FATAL] 不像内核树: {root}")

    acts = []

    # 1. 源文件改名
    old_c = root / "drivers/usb/misc" / OLD_C
    new_c = root / "drivers/usb/misc" / NEW_C
    if old_c.exists():
        acts.append(("rename", str(old_c.relative_to(root)), str(new_c.name)))
        if a.apply:
            old_c.rename(new_c)
            # 清掉旧 .o 及依赖文件，避免增量编译复用旧目标
            for suf in (".o",):
                f = root / "drivers/usb/misc" / (OLD_C[:-2] + suf)
                if f.exists():
                    f.unlink()
            for pre in (".", ""):
                for suf in (".o.cmd", ".o.d"):
                    f = root / "drivers/usb/misc" / (pre + OLD_C[:-2] + suf)
                    if f.exists():
                        f.unlink()
    elif new_c.exists():
        acts.append(("skip", NEW_C, "已改名"))
    else:
        acts.append(("warn", OLD_C, "两种文件名都不存在"))

    # 2. Kconfig
    kc = root / "drivers/usb/misc/Kconfig"
    s = read(kc)
    if "config USB_REDRIVER_PS5169" in s:
        acts.append(("skip", "Kconfig", "USB_REDRIVER_PS5169 已定义"))
    else:
        m = re.search(r"^config USB_REDRIVER_PI2DPX\b", s, re.M)
        if not m:
            acts.append(("warn", "Kconfig", "找不到插入锚点 PI2DPX"))
        else:
            s2 = s[:m.start()] + KCONFIG_BLOCK.strip("\n") + "\n\n" + s[m.start():]
            acts.append(("kconfig", "drivers/usb/misc/Kconfig", "新增 USB_REDRIVER_PS5169"))
            if a.apply:
                write(kc, s2)

    # 3. Makefile
    mk = root / "drivers/usb/misc/Makefile"
    s = read(mk)
    old_line = re.compile(rf"^obj-\$\({OLD_SYM}\)(?P<ws>\s*)\+=\s*\S+$", re.M)
    if f"obj-$({NEW_SYM})" in s:
        acts.append(("skip", "Makefile", "已接 PS5169"))
    elif old_line.search(s):
        s2 = old_line.sub(f"obj-$({NEW_SYM})\t+= {NEW_C[:-2]}.o", s, count=1)
        acts.append(("makefile", "drivers/usb/misc/Makefile",
                     f"obj-$({NEW_SYM}) += {NEW_C[:-2]}.o"))
        if a.apply:
            write(mk, s2)
    else:
        acts.append(("warn", "Makefile", "未找到 NB7VPQ904M 的 obj 规则"))

    # 4. qmp.c
    qmp = root / "drivers/usb/phy/phy-msm-ssusb-qmp.c"
    if qmp.exists():
        s = read(qmp)
        n = s.count(OLD_SYM)
        if n:
            acts.append(("qmp", "drivers/usb/phy/phy-msm-ssusb-qmp.c",
                         f"IS_BUILTIN 改 PS5169 ({n} 处)"))
            if a.apply:
                write(qmp, s.replace(OLD_SYM, NEW_SYM))
        else:
            acts.append(("skip", "phy-msm-ssusb-qmp.c", "无需改"))
    else:
        acts.append(("warn", "phy-msm-ssusb-qmp.c", "文件不存在"))

    # 5. config 文件
    for rel in (".config", "tb371fc/config-v2.2.txt"):
        p = root / rel
        if not p.exists():
            acts.append(("warn", rel, "不存在"))
            continue
        s = read(p)
        if f"{NEW_SYM}=y" in s:
            acts.append(("skip", rel, "已是 PS5169=y"))
            continue
        s2 = s.replace(f"{OLD_SYM}=y", f"# {OLD_SYM} is not set")
        if f"{NEW_SYM}" not in s2:
            s2 = s2.replace(f"# {OLD_SYM} is not set",
                            f"# {OLD_SYM} is not set\n{NEW_SYM}=y", 1)
        if s2 == s:
            acts.append(("warn", rel, "未找到 NB7VPQ904M=y 行"))
        else:
            acts.append(("config", rel, f"{NEW_SYM}=y / NB7VPQ904M not set"))
            if a.apply:
                write(p, s2)

    tag = "APPLY" if a.apply else "DRY-RUN"
    print(f"[{tag}] {root}\n")
    for kind, where, detail in acts:
        icon = {"skip": "=", "warn": "!", "rename": ">", "kconfig": "+",
                "makefile": "+", "qmp": "~", "config": "*"}.get(kind, "?")
        print(f"  {icon} [{kind:8s}] {where:44s} {detail}")

    if not a.apply:
        print("\n加 --apply 执行。")
    else:
        print("\n完成。建议接着:")
        print("  make ARCH=arm64 ... olddefconfig   # 确认 PS5169=y 未被删")
        print("  make ARCH=arm64 ... Image")
    return 0


if __name__ == "__main__":
    sys.exit(main())
