# 本仓库说明：5.10-BPF backport + AstideLabs 通用更新

这份树是 Lenovo TB371FC（SM8250 / kona / Linux 4.19.325）的完整内核源码，在
[smith-dog/kernel-tb371fc](https://github.com/smith-dog/kernel-tb371fc) 基础上加了两层改动：

1. **5.10 BPF 反移植** —— 补齐 Android 16 `bpfloader` 所需的 BPF 能力（ringbuf、BTF、
   `BPF_MAP_TYPE_*` 全集、map-in-map、bpf_iter 等），基线提交里已包含；
2. **AstideLabs 通用更新 766 项** —— 从
   [AstideLabs/android_kernel_xiaomi_sm8250](https://github.com/AstideLabs/android_kernel_xiaomi_sm8250)
   的 `android17-aptusitu-new` 分支筛选，只保留通用内核子系统。

## 提交历史

| 提交 | 内容 |
|---|---|
| `9093a27` | baseline：smith-dog tb371fc 4.19.325 + 5.10-bpf backport + v2.2/EROFS 配置（NB7VPQ904M redriver） |
| `e08dfdb` | 应用 AstideLabs 通用更新，第一批 25 项 |
| `a9774fb` | 应用 AstideLabs 通用更新，第二批 741 项（651 文件，+6452 / −2782） |
| `57d6657` | 回滚 `f_midi` 到基线（补丁集把 tasklet 换成 work，但结构体未同步） |
| `a1345db` | `f2fs_msg` → `f2fs_err`（树内已统一到新日志宏） |
| `8ce4eb3` | 收录 backport 工具包到 `kit/` |

`git diff 9093a27..main` 即全部改动，对应 `kit/patches/` 下四个 `git am` 补丁。

## 筛选规则

保留：`kernel/ mm/ fs/ net/ ipc/ lib/ block/ security/ crypto/ virt/`、
`drivers/{usb,mmc,hid,input,rtc,i2c,spi,gpio,pinctrl,power,thermal,hwmon,watchdog,leds,dma,base,bluetooth,scsi,...}`、
`sound/{core,pci,usb}`、`include/`、`arch/arm64/{kernel,lib,mm}`。

剔除（整条跳过，不做半应用）：
`techpack/`、`drivers/gpu/msm`、`drivers/staging/qcacld-3.0`、`drivers/media/platform/msm`、
`xiaomi/`、`arch/arm64/boot/dts/vendor/qcom`（机型 DTS）、`arch/arm64/configs/`、`Android.bp`。

62 项因与 sm8250 私有代码强耦合而跳过，清单见 `kit/` 内的冲突分析报告。

## 编译

```bash
export ARCH=arm64 SUBARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
export CC=/usr/lib/llvm-21/bin/clang

make O=out vendor/kona_defconfig
cat kit/dist/config-v2.2-bpf-erofs.config >> out/.config
make O=out olddefconfig
make O=out -j$(nproc) Image
```

实测：Ubuntu clang 21.1.8 + GNU ld 2.42，`DYNAMIC_SINGLE_CHIP=qca6390`，
产物 50,724,880 字节，SHA-256 `7637ad7ea5f1867d2d29c1c17eed49dbd26ca8b1c1726da9efb300c59dde73cb`。

`Image` / `boot.img` / `ksu.ko` 按内核默认 `.gitignore` 排除，不入库。

## kit/ 目录

| 路径 | 内容 |
|---|---|
| `kit/backport.sh` `kit/build.sh` `kit/pack-boot.sh` | 反移植、编译、boot.img 重打包 |
| `kit/configs/` | v2.2+BPF+EROFS 配置、PS5169 redriver 4.19 适配驱动与幂等安装脚本 |
| `kit/patches/` | 5.10-bpf 全量补丁、Android 16 防卡死补丁、PS5169 patch |
| `kit/reports/` | 编译报告、配置-源码比对、冲突分析、来源清单 |
| `kit/tools/` | `repack_boot.py` |

细节见 `kit/README.md`。

## 配置要点

```
CONFIG_BPF=y                  CONFIG_BPF_SYSCALL=y        CONFIG_BPF_JIT=y
CONFIG_BPF_JIT_ALWAYS_ON=y    CONFIG_HAVE_EBPF_JIT=y      CONFIG_CGROUP_BPF=y
CONFIG_NETFILTER_XT_MATCH_BPF=y                           CONFIG_NET_CLS_BPF=y
CONFIG_BPF_LSM=y              CONFIG_BPF_PRELOAD=y        CONFIG_EROFS_FS=y
```

注意 `CONFIG_LSM` 里追加 `bpf` 需要 5.10 的 LSM 框架；本树 `security/` 仍是 4.19 老式
`__security_initcall`，只有 `kernel/bpf/bpf_lsm.c` 等文件在位，钩子未注册。

## 状态

代码可编译通过，**未经真机验证**。`ksu.ko` 未编译，`boot.img` 未打包。
