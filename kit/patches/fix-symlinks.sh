#!/usr/bin/env bash
# fix-symlinks.sh — 修复仓库里硬编码作者本机绝对路径的断链软链
#
# 背景
# ----
# smith-dog/kernel-tb371fc 的 techpack 音频目录里有 3 个软链, 内容在
# GitHub tarball 里被固化成作者本机的绝对路径 (/home/smith/kernels/...),
# 在其它机器上全部是断链, 编译时报:
#   techpack/audio/soc/pinctrl-wcd.c:18:10: fatal error: 'core.h' file not found
#
# 仓库 techpack/audio/Makefile.am 本来就写明了这些软链的意图:
#   ln -s $(KERNEL_SRC)/drivers/base/regmap/internal.h include/soc/internal.h
# 即它们应当指向**当前内核源码树内**的同名头文件。目标树里这三份文件
# 都在, 且不含引号 include (不会因软链相对解析而出错), 因此把它们重指向
# 树内相对路径即可 —— 既恢复作者本意, 又保持可移植 (不依赖任何绝对路径)。
#
# 另有一个断链 arch/arm64/boot/dts/vendor -> vendor/qcom/proprietary/...
# 只影响 dtb 构建, 本任务目标是 Image, 不改动。
#
# 用法:
#   bash patches/fix-symlinks.sh /path/to/kernel-tree   (默认当前目录)
# 幂等: 反复执行结果一致。
set -euo pipefail

TREE="$(cd "${1:-.}" && pwd)"
cd "$TREE"

# 相对软链目标 (相对于软链所在目录), 全部指向树内已有文件
declare -a LINKS=(
    "techpack/audio/soc/core.h|../../../drivers/pinctrl/core.h"
    "techpack/audio/soc/pinctrl-utils.h|../../../drivers/pinctrl/pinctrl-utils.h"
    "techpack/audio/include/soc/internal.h|../../../../drivers/base/regmap/internal.h"
)

for item in "${LINKS[@]}"; do
    link="${item%%|*}"
    target="${item##*|}"
    real="$(cd "$(dirname "$link")" 2>/dev/null && pwd)/$(basename "$link")"
    # 用 python 做与 make 一致的路径归一化, 确认目标文件真实存在
    resolved="$(python3 -c "import os,sys; print(os.path.normpath(os.path.join(sys.argv[1], sys.argv[2])))" "$(dirname "$link")" "$target")"
    if [ ! -f "$resolved" ]; then
        echo "[FATAL] $link 的目标文件不存在: $resolved" >&2
        exit 1
    fi
    if [ -L "$link" ] && [ "$(readlink "$link")" = "$target" ]; then
        echo "  [=] $link 已是正确软链"
        continue
    fi
    ln -sfn "$target" "$link"
    echo "  [+] $link -> $target (树内: $resolved)"
done

# 校验: 三个软链现在都可读
for item in "${LINKS[@]}"; do
    link="${item%%|*}"
    [ -e "$link" ] || { echo "[FATAL] 修复后仍断链: $link" >&2; exit 1; }
done
echo "[OK] techpack 软链已全部指向树内文件"
