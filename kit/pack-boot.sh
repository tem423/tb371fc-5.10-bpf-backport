#!/usr/bin/env bash
# pack-boot.sh — 把编译出的 Image 打包成可 fastboot 刷入的 boot.img
#
# 原理（沿用目标仓库 tb371fc/tools/repack_boot.py）:
#   以官方 Release 的 v2.2 pure 镜像为「基底」, 保留 header v2 / 原厂 ramdisk /
#   DTB 尾, 只把 kernel 段换成我们编出的 arch/arm64/boot/Image, 并修正
#   header 的 kernel_size 与 dtb_size, 输出补齐到 96MB 分区几何。
#   不换 ramdisk = 纯净无 root 形态（不内嵌 kernelsu.ko）。
#
# 用法:
#   bash pack-boot.sh <base.img> [kernel-Image] [out.img]
#
# 基底获取（官方 Release v2.2 pure; 直连慢时用镜像代理）:
#   curl -L -o boot-v2.2-pure-flash.img \
#     "https://gh-proxy.com/https://github.com/smith-dog/kernel-tb371fc/releases/download/v2.2/boot-v2.2-pure-flash.img"
#   注意必须是完整 100663296 字节, 否则 ramdisk / DTB 尾缺失。
#
# 若要 KernelSU root 形态, 把基底换成 boot-v2.2-kspatched-flash.img 即可,
# 命令相同（工具原样保留该基底自带 KSU 的 ramdisk）。
set -euo pipefail

PKG="$(cd "$(dirname "$0")" && pwd)"
BASE="${1:-}"
KER="${2:-$PKG/dist/Image}"
OUT="${3:-$PKG/dist/boot-5.10-bpf-v2.2-pure.img}"

if [ -z "$BASE" ] || [ ! -f "$BASE" ]; then
    echo "用法: bash pack-boot.sh <base.img> [kernel-Image] [out.img]" >&2
    echo "基底需为官方 Release v2.2 的完整 boot.img (100663296 字节)" >&2
    exit 2
fi
[ -f "$KER" ] || { echo "[FATAL] 内核 Image 不存在: $KER" >&2; exit 1; }

echo "基底 : $BASE ($(wc -c < "$BASE") 字节)"
echo "内核 : $KER ($(wc -c < "$KER") 字节)"

# 前置校验: 基底必须是完整的 header v2 boot.img
python3 - "$BASE" <<'PY'
import struct, sys
d = open(sys.argv[1], "rb").read()
assert d[:8] == b"ANDROID!", "基底不是 Android boot.img"
ks, rs, page = (struct.unpack("<I", d[o:o+4])[0] for o in (8, 16, 36))
assert page == 4096, f"page_size 异常: {page}"
pad = lambda n: (n + 4095) // 4096 * 4096
end = page + pad(ks) + pad(rs)
assert len(d) > end, f"基底被截断: 需要至少 {end} 字节, 实际 {len(d)}"
assert len(d) == 100663296, f"基底大小 {len(d)} != 分区 100663296"
print(f"  基底 OK: v2 头, kernel={ks} ramdisk={rs} DTB尾={len(d)-end} 字节")
PY

echo; echo "===== repack_boot.py 打包 ====="
python3 "$PKG/tools/repack_boot.py" "$BASE" "$KER" "$OUT"

# ----------------------------------------------------------- 读回字节门禁
echo; echo "===== 从输出镜像读回校验 ====="
python3 - "$BASE" "$OUT" "$KER" <<'PY'
import struct, hashlib, sys
b = open(sys.argv[1], "rb").read()
o = open(sys.argv[2], "rb").read()
k = open(sys.argv[3], "rb").read()
pad = lambda n: (n + 4095) // 4096 * 4096
def fields(d):
    return (struct.unpack("<I", d[x:x+4])[0] for x in (8, 16, 24, 36))
ks0, rs0, ss0, pg0 = fields(b)
ks1, rs1, ss1, pg1 = fields(o)
dtb1 = struct.unpack("<I", o[1648:1652])[0]

assert o[:8] == b"ANDROID!" and pg1 == 4096, "输出头异常"
assert ks1 == len(k), f"kernel_size {ks1} != {len(k)}"
assert len(o) == 100663296, f"输出大小 {len(o)} 未补齐到分区"
# kernel 逐字节
emb = o[pg1:pg1+ks1]
assert hashlib.md5(emb).digest() == hashlib.md5(k).digest(), "内嵌 kernel 与 Image 不一致"
# ramdisk 原样
r0 = pg0 + pad(ks0); r1 = pg1 + pad(ks1)
assert b[r0:r0+rs0] == o[r1:r1+rs1], "ramdisk 被改动"
# DTB 尾原样
e0 = pg0 + pad(ks0) + pad(rs0) + pad(ss0)
e1 = pg1 + pad(ks1) + pad(rs1) + pad(ss1)
assert b[e0:e0+dtb1] == o[e1:e1+dtb1], "DTB 尾被改动"
fdt = o[e1:e1+dtb1].count(b"\xd0\x0d\xfe\xed")
print(f"  [OK] kernel md5={hashlib.md5(emb).hexdigest()} 与编出 Image 一致")
print(f"  [OK] ramdisk {rs0} 字节原样保留, DTB 尾 {dtb1} 字节原样保留 (FDT={fdt})")
print(f"  [OK] kernel_size={ks1} dtb_size={dtb1} 总大小={len(o)}")
PY

echo; echo "[OK] 产物: $OUT"
echo "     刷入: adb reboot bootloader && fastboot flash boot $(basename "$OUT") && fastboot reboot"
