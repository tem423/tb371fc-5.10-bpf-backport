# 内核 config 与源码一致性核对

内核树：`build2`（最终编译树，`Image` 与 `dist/Image` 字节一致）
配置：`build2/.config`（`config-v2.2.txt` 经 `olddefconfig` 展开）
启用项：1878（`=y` 1869 / `=m` 9）

## 结论

**「config 开了但源码没有」的驱动：0 项。**

逐项核对链路为：

```
.config 的 CONFIG_X=y/m
  -> 全树 Kconfig* 中找 config X / menuconfig X
  -> 定义目录的 Makefile 找 obj-$(CONFIG_X) += target
     （找不到则向上 3 层找 obj-$(CONFIG_X) += <子目录>/）
  -> target 为 foo.o 时查 foo.c / foo.S / foo-y 组合 / 自定义 pattern rule
  -> target 为 dir/ 时查目录存在且非空
```

各项数量：

| 分类 | 数量 | 含义 |
|---|---|---|
| `MISSING_SRC` | **0** | config 要编，但源文件/目录不存在 |
| `NOT_WIRED` | 794 | Kconfig 有定义，但 Makefile 不以 obj 规则接线（功能开关，见下） |
| `NO_KCONFIG` | 0 | config 有、全树 Kconfig 无定义（残留项） |
| `OK` | 1084 | 能对上源码 |

## 三处曾疑似缺失，核实均为误报

| CONFIG | 脚本初判 | 实际情况 |
|---|---|---|
| `CONFIG_CRYPTO_AES_ARM64_CE_BLK` | 缺 `aes-glue-ce.o` | 由 `$(obj)/aes-glue-%.o: $(src)/aes-glue.c` 的 **pattern rule** 从 `aes-glue.c` 生成，已编出 186,920 字节 `.o` |
| `CONFIG_CRYPTO_AES_ARM64_NEON_BLK` | 缺 `aes-glue-neon.o` | 同上，已编出 188,368 字节 `.o` |
| `CONFIG_NFC_NXP_CTN730` | 缺 `CTN730_i2c.o` | 该目标仅在 `ifeq ($(CONFIG_NXP_VERSION),y)` 分支；实际走 `else`，编的是 `ctn730.o`（源码 `ctn730.c` 61,411 字节） |

修正点：Makefile 的 `%` 通配符要转成 fnmatch 的 `*`；同一 CONFIG 的条件分支目标只要**任一**命中源码即视为 OK。

## 794 项「未接线」是什么

全部是 **Kconfig feature 开关**，不对应独立 `.o`，例：

- `CONFIG_SMP`、`CONFIG_PREEMPT`、`CONFIG_HZ_250`、`CONFIG_MODULES`
- `CONFIG_ARM64_ERRATUM_*`、`CONFIG_QCOM_FALKOR_ERRATUM_*`
- `CONFIG_EXT4_FS_ENCRYPTION`、`CONFIG_F2FS_FS_SECURITY`、`CONFIG_EROFS_FS_SECURITY`
- `CONFIG_USB_CONFIGFS_F_*`、`CONFIG_USB_F_*`（由 gadget 的 `-$(CONFIG_...)` 形式接入）
- `CONFIG_KSU_FEATURE_*`（KSU 为 `=m`，编成 `ksu.ko`，不进 `built-in.a`）

这些项通过 `ccflags-$(CONFIG_X)`、`ifeq`、`xxx-y += -$(CONFIG_X)` 或父目录 `obj-$(CONFIG_X) += dir/` 生效，不是驱动缺失。

按目录验证：`NOT_WIRED` 中 125 个含 `.c` 的目录，108 个都有非空 `built-in.a`；其余 17 个均为 feature 开关目录（`arch/arm/mm`、`drivers/bcma`、`drivers/virtio`、`kernel/gcov`、`sound/pci` 等），无一是“驱动主开关开了却没编”。

## 需要注意：9 个 `=m` 模块本次只编了 `ksu.ko`

本次执行的是 `make Image` + `make M=drivers/kernelsu modules`，其余 8 个模块**源码在、config 开，但产物里没有**：

| CONFIG | 说明 |
|---|---|
| `CONFIG_WIL6210=m` | 802.11ad 无线 |
| `CONFIG_MSM_11AD=m` | 11ad 平台驱动 |
| `CONFIG_WIGIG_SENSING_SPI=m` | wigig sensing |
| `CONFIG_DVB_MPQ=m` | 移动数字电视 |
| `CONFIG_DVB_MPQ_DEMUX=m` | 同上 demux |
| `CONFIG_MSM_RDBG=m` | 远程调试 |
| `CONFIG_LCD_CLASS_DEVICE=m` | LCD class |
| `CONFIG_QCOM_LLCC_PERFMON=m` | LLCC 性能监控 |

如果后续需要这些功能，得补 `make modules`；若确定不用，建议直接关掉，避免“看着有、实际没有”。

## 唯一在基线里存在、最终消失的项

`CONFIG_CC_HAS_AUTO_VAR_INIT_ZERO=y` → 编译器能力探测项（clang 是否支持 `-ftrivial-auto-var-init=zero`），由 Kconfig `def_bool` 自动判定，不是驱动，也不影响产物。

`config-v2.2.txt` 的 1865 个 `=y/m` 项中，1864 个在最终 `.config` 里保留；新增的 14 项全部是本工程主动叠加的 EROFS/BPF 配置及依赖联动。

## 复现

```bash
python3 tools/check-config-src.py /path/to/kernel-tree \
  --report reports/config-vs-src.json --md reports/config-vs-src.md
```

完整 794 项明细见 `reports/config-vs-src.json` 的 `NOT_WIRED` 数组。
