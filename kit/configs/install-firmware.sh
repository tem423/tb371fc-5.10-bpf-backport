#!/usr/bin/env bash
# install-firmware.sh — 把出货音频固件事先放到 CONFIG_EXTRA_FIRMWARE_DIR
#
# 背景
# ----
# tb371fc/config-v2.2.txt 里有:
#   CONFIG_EXTRA_FIRMWARE="tfa98xx_QS.cnt tfa98xx_YC.cnt"
#   CONFIG_EXTRA_FIRMWARE_DIR="/home/smith/t34/fw"
# 这是作者本机的绝对路径。firmware/Makefile 会用 .incbin 直接引用
#   $(fwabs)/tfa98xx_QS.cnt  和  $(fwabs)/tfa98xx_YC.cnt
# 因此编译前这两个二进制容器文件必须真实存在于该目录, 否则报:
#   *** No rule to make target '/home/smith/t34/fw/tfa98xx_QS.cnt'
#
# 仓库自带 tfa98xx_YC.cnt (firmware/ 下), 但 tfa98xx_QS.cnt 需要从真机
# /vendor/firmware 提取 (README 说明)。本工程包 firmware/ 已随附两份。
#
# 说明: 内建固件只是加速冷启动 (tfa98xx.c 里 fw_name_first/second 走
# request_firmware() 运行时回退), 但 v2.2 出货配置要求内建, 故按配置补齐,
# 不修改 .config —— 保持 v2.2 基线不变。
#
# 用法:
#   bash configs/install-firmware.sh /path/to/kernel-tree
#   (不带参数则默认当前目录)
set -euo pipefail

PKG="$(cd "$(dirname "$0")/.." && pwd)"
TREE="$(cd "${1:-.}" && pwd)"
CFG="$TREE/.config"

if [ ! -f "$CFG" ]; then
    echo "[FATAL] 找不到 $CFG，请先生成 .config" >&2
    exit 1
fi

# 从 .config 读取固件目录（去掉引号）
FWDIR="$(sed -n 's/^CONFIG_EXTRA_FIRMWARE_DIR="\(.*\)"/\1/p' "$CFG" | head -n1)"
FWDIR="${FWDIR:-/home/smith/t34/fw}"

# firmware/Makefile: 相对路径按 $(srctree) 解析，绝对路径原样使用
case "$FWDIR" in
    /*) DEST="$FWDIR" ;;
    *)  DEST="$TREE/$FWDIR" ;;
esac

mkdir -p "$DEST"
for f in tfa98xx_QS.cnt tfa98xx_YC.cnt; do
    if   [ -f "$PKG/firmware/$f" ]; then SRC="$PKG/firmware/$f"
    elif [ -f "$TREE/firmware/$f" ]; then SRC="$TREE/firmware/$f"
    else
        echo "[FATAL] 缺少固件 $f（工程包 firmware/ 与目标树 firmware/ 均无）" >&2
        exit 1
    fi
    cp "$SRC" "$DEST/$f"
    echo "  [fw] $SRC -> $DEST/$f ($(wc -c < "$SRC") 字节)"
done

echo "[OK] 固件已就位: $DEST"
