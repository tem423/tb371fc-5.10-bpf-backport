#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make-config-v2.2.py — 以 tb371fc/config-v2.2.txt 为基线生成 .config

用法:
    python3 make-config-v2.2.py /path/to/kernel-tree

叠加两组配置:
  1) EROFS (staging 4.19 版), 含 xattr/acl/security label/压缩
  2) 酷安帖子要求的 5.10-bpf 全部 CONFIG (含 BPF_LSM / BPF_PRELOAD / LSM=)

幂等: 先删除同名项再追加, 可重复执行; 之后由 make olddefconfig 定稿。
"""
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
BASE = ROOT / "tb371fc" / "config-v2.2.txt"
OUT = ROOT / ".config"

# EROFS: 4.19 staging 版 (drivers/staging/erofs/Kconfig)
# SECURITY label 供 SELinux 使用, ZIP 供 Android 压缩只读分区
EROFS = {
    "EROFS_FS": "y",
    "EROFS_FS_XATTR": "y",
    "EROFS_FS_POSIX_ACL": "y",
    "EROFS_FS_SECURITY": "y",
    "EROFS_FS_ZIP": "y",
    "EROFS_FS_CLUSTER_PAGE_LIMIT": "1",
}

# 帖子要求的 5.10-bpf 配置 (configs/bpf-5.10.fragment)
BPF = {
    "BPF": "y",
    "BPF_SYSCALL": "y",
    "BPF_JIT": "y",
    "BPF_JIT_ALWAYS_ON": "y",
    "HAVE_EBPF_JIT": "y",
    "CGROUP_BPF": "y",
    "NETFILTER_XT_MATCH_BPF": "y",
    "NET_CLS_BPF": "y",
    "NET_ACT_BPF": "y",
    "BPF_LSM": "y",
    "BPF_PRELOAD": "y",
    # 与 security/Kconfig 的 CONFIG_LSM 默认串一致, 末尾必须含 bpf
    "LSM": '"lockdown,yama,loadpin,safesetid,integrity,selinux,smack,tomoyo,apparmor,bpf"',
}

WANT = {**EROFS, **BPF}

if not BASE.exists():
    raise SystemExit(f"[FATAL] 基线配置不存在: {BASE}")
lines = BASE.read_text(encoding="utf-8", errors="surrogateescape").splitlines()

# 删除所有同名项 (含 "# CONFIG_X is not set"), 保留其它行
out, seen = [], set()
for ln in lines:
    hit = None
    for k in WANT:
        if ln.startswith(f"CONFIG_{k}=") or ln == f"# CONFIG_{k} is not set":
            hit = k
            break
    if hit:
        seen.add(hit)
    else:
        out.append(ln)

# 追加 (统一写, 便于核对)
out.append("")
out.append("# ---- 5.10-bpf backport: EROFS + BPF (make-config-v2.2.py) ----")
for group, name in ((EROFS, "EROFS"), (BPF, "5.10-bpf")):
    out.append(f"# {name}")
    for k, v in group.items():
        out.append(f"CONFIG_{k}={v}")

OUT.write_text("\n".join(out) + "\n", encoding="utf-8", errors="surrogateescape")
print(f"基线     : {BASE.name} ({len(lines)} 行)")
print(f"输出     : {OUT}")
print(f"覆盖原有 : {len(seen)} 项 -> {', '.join(sorted(seen))}")
print(f"写入     : EROFS {len(EROFS)} 项 + BPF {len(BPF)} 项 = {len(WANT)} 项")
