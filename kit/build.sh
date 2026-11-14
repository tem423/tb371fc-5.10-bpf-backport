#!/usr/bin/env bash
# build.sh — 从干净的 4.19.325 目标树一键产出 arch/arm64/boot/Image
#
# 完整链路（每一步都与本次实测一致）:
#   1. 应用 5.10-bpf 主补丁 (git apply --reject 会产生 20 个 .rej, 属预期)
#   2. resolve-conflicts.py  合入残留 .rej 并补编译期兼容修复 (幂等)
#   3. make-config-v2.2.py   以 tb371fc/config-v2.2.txt 为基线, 叠加
#                            EROFS(6) + 帖子 BPF(12), 生成 .config
#   4. olddefconfig          用 README 编译链定稿 .config
#   5. fix-symlinks.sh       修复 techpack 里硬编码作者本机绝对路径的断链
#   6. install-firmware.sh   把两份 tfa98xx_*.cnt 放到
#                            CONFIG_EXTRA_FIRMWARE_DIR 指向的目录
#   7. make ... Image        原仓库 README.md 出货配方
#
# 用法:
#   bash build.sh /path/to/kernel-tree [--config-only]
#
# 环境变量:
#   CC      编译器, 默认 clang-21 (Ubuntu clang 21.1.8, README 要求)
#   JOBS    并行度, 默认 6 (README 的 -j6)
#   FWDIR   覆盖 CONFIG_EXTRA_FIRMWARE_DIR (可选, 需同时改 .config)
#
# 前置: 目标树需为 smith-dog/kernel-tb371fc 源码 (如从 tarball 解压),
#       且需有 tb371fc/config-v2.2.txt。脚本不修改仓库历史, 不 push。
set -euo pipefail

PKG="$(cd "$(dirname "$0")" && pwd)"
TREE="$(cd "${1:-.}" && pwd)"
CONFIG_ONLY=0
[ "${2:-}" = "--config-only" ] && CONFIG_ONLY=1

CC="${CC:-clang-21}"
JOBS="${JOBS:-6}"
PATCH="$PKG/patches/5.10-bpf-tb371fc.diff"

echo "工程包 : $PKG"
echo "目标树 : $TREE"
echo "编译器 : $CC   并行: -j$JOBS"
echo

cd "$TREE"

# ---------------------------------------------------------------- 1. 主补丁
# ringbuf.c 是补丁落地的核心标志, 用它判断是否已应用过 (幂等)。
if [ -f kernel/bpf/ringbuf.c ]; then
    echo "[1/7] 主补丁已应用 (kernel/bpf/ringbuf.c 存在), 跳过"
else
    echo "[1/7] 应用 5.10-bpf 主补丁 ..."
    git apply --reject --whitespace=nowarn "$PATCH" || true
    # 允许失败: 预期产生 20 个 .rej, 下一步逐个合入
    echo "      .rej 数量: $(find . -name '*.rej' | wc -l)"
fi

# ------------------------------------------------------- 2. 解决冲突/兼容修复
echo "[2/7] resolve-conflicts.py 合入残留 .rej + 编译期兼容修复 ..."
python3 "$PKG/patches/resolve-conflicts.py" "$TREE"
find . -name '*.rej' -delete
echo "      残留 .rej: $(find . -name '*.rej' | wc -l)"

# ------------------------------------------------------------- 3. 生成配置
echo "[3/7] make-config-v2.2.py 生成 .config (v2.2 + EROFS + 帖子 BPF) ..."
python3 "$PKG/configs/make-config-v2.2.py" "$TREE"

# ------------------------------------------------------------ 4. olddefconfig
echo "[4/7] olddefconfig (README 编译链) ..."
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC="$CC" \
     CLANG_TRIPLE=aarch64-linux-gnu- AS=aarch64-linux-gnu-as olddefconfig \
     >/tmp/tb371fc-olddefconfig.log 2>&1 || {
         echo "[FATAL] olddefconfig 失败, 见 /tmp/tb371fc-olddefconfig.log" >&2
         tail -n 30 /tmp/tb371fc-olddefconfig.log >&2; exit 1
     }

if [ "$CONFIG_ONLY" = 1 ]; then
    echo "[OK] --config-only: 配置已生成, 跳过软链/固件与编译"
    exit 0
fi

# ------------------------------------------------------------- 5. 修复断链
echo "[5/7] fix-symlinks.sh 修复 techpack 断链软链 ..."
bash "$PKG/patches/fix-symlinks.sh" "$TREE"

# ------------------------------------------------------------- 6. 固件落位
echo "[6/7] install-firmware.sh 落位 tfa98xx_*.cnt ..."
bash "$PKG/configs/install-firmware.sh" "$TREE"

# -------------------------------------------------------------- 7. 编译 Image
echo "[7/7] make -j$JOBS ... Image (README 出货配方) ..."
KV="$TREE"
make -j"$JOBS" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC="$CC" \
     CLANG_TRIPLE=aarch64-linux-gnu- AS=aarch64-linux-gnu-as \
     KCFLAGS="-Wno-error -Wno-error=strict-prototypes -Wno-error=implicit-int -Wno-error=incompatible-pointer-types -Wno-error=date-time -include $KV/drivers/staging/fw-api/fw/p226_compat.h" \
     DYNAMIC_SINGLE_CHIP=qca6390 Image 2>&1 | tee /tmp/tb371fc-build.log

if [ -f arch/arm64/boot/Image ]; then
    echo
    echo "[OK] 产物: $TREE/arch/arm64/boot/Image ($(wc -c < arch/arm64/boot/Image) 字节)"
else
    echo "[FATAL] 未生成 Image, 检查 /tmp/tb371fc-build.log" >&2
    exit 1
fi
