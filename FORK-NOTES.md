# 本仓库说明：TB371FC 4.19.325 + 5.10-BPF backport + AstideLabs 通用更新

Lenovo TB371FC（SM6375 / kona / Linux 4.19.325）的完整内核源码，带真实提交历史。

## 这棵树从哪来

不是 tarball 解压后 `git init` 的空历史，链路可以一直追到 Linux 根提交：

```
Linux 1da177e4 (2.6.12-rc2)
  └─ ... ─ Linux 4.19.157 (31acccd)
       ├─ lss4/android_kernel_lenovo_paladin (分支 11，含 CAF LA.UM.9.12.1.r1 合并)
       │    └─ smith-dog/kernel-tb371fc (升到 4.19.325，自研驱动与 v2.x 配置)
       │         └─ 本仓库：5.10 BPF backport + AstideLabs 通用更新
       └─ AstideLabs/android_kernel_xiaomi_sm8250 (同样升到 4.19.325 后转向小米 BSP)
```

三个关键 merge-base 都是实测出来的：

| 对比 | 共同祖先 |
|---|---|
| smith-dog ↔ paladin | `31acccd` **Linux 4.19.157** |
| smith-dog ↔ AstideLabs | `a67e7cd` **Linux 4.19.325** |
| paladin ↔ AstideLabs | `3f88a82`（CAF 共享提交） |

所以本树与 AstideLabs 不是「无关历史」，而是 4.19.325 之后各自走了不同的 BSP 分支。

## 提交历史（第一父系）

| 提交 | 内容 |
|---|---|
| `e54130b` | Merge AstideLabs `android17-aptusitu-new`（第二父 `5bdae44`） |
| `c35bde4` | docs：记录上游历史接入方式与实测结论 |
| `68afe06` | docs：README 顶部标注本仓库改动 |
| `001f632` | kit：收录 backport 工具包到 `kit/` |
| `add451e` | fix：`f2fs_msg` → `f2fs_err` |
| `fe343e8` | fix：回滚 `f_midi`（补丁集换 tasklet→work 但结构体未同步） |
| `77927c2` | generic：AstideLabs 通用更新 741 项 |
| `85578e1` | generic：AstideLabs 通用更新第一批 25 项 |
| `fcfb39a` | backport：4.19 侧配套适配（trace/rcu/kernfs/proc/nvdimm/工具链） |
| `d278556` | kconfig：补齐 BPF/BTF/RCU/trace 配置项并启用 |
| `0875bca` | backport：security 子系统适配 BPF LSM 挂钩 |
| `ec0eabf` | backport：BPF 网络侧挂钩（sk_msg/sk_lookup/xdp/sockmap） |
| `742ef5d` | backport：引入 5.10 BPF 核心（verifier/map/BTF/ringbuf/iter） |
| `c3df39c` | smith-dog v2.2 release notes（上游 tip） |

`git diff c3df39c..main` 是我们在 smith-dog 之上做的全部改动。

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

## 上游完整历史（merge 提交）

`e54130b` 是一个真实的三方合并，不是 `--allow-unrelated-histories` 拼出来的：

- 第二父 `5bdae44`，来自 `android17-aptusitu-new`
- merge-base `a67e7cd` = **Linux 4.19.325**
- 上游侧共 9,575 个提交，作者、日期、信息原样保留
- 全仓库 880,000+ 提交对象，可回溯到 Linux 根提交

**合并的实测过程**

| 阶段 | 结果 |
|---|---|
| 自动合并 | 13,884 文件 |
| 冲突 | 5,028 文件 |
| ├ vendor 路径（DTS 3,197 / staging 879 / techpack 193 / QCOM 85） | 4,354，取本树 |
| └ 通用路径 | 674，逐个按 index stage 处理 |
| 合并后净改动 | 8,858 文件（+1,424,226 / −43,110） |

**为什么最终树内容回到本树**

带着这 8,858 个文件的改动编译，按下面顺序逐层回退，错误只是往下一层传导：

| 顺序 | 报错 | 回退的目录 |
|---|---|---|
| 1 | 汇编器检测失败（`scripts/Kconfig.include` 是 5.x 版） | `scripts/` |
| 2 | `init/Kconfig` 调用 `gcc-version.sh -p`，本树脚本不支持 | 全部 Kconfig（536 个） |
| 3 | `__lse_ll_sc_body` 未定义（cmpxchg 新、atomic_lse 旧） | `arch/arm64/include/asm` |
| 4 | `__va_function` 未定义（kCFI） | `arch/arm64/include` |
| 5 | `pgd_none_or_clear_bad` 重定义 | `include/`、`arch/`、`mm/`、`kernel/` |
| 6 | `rmnet_config.h` 结构体重定义（techpack 依赖） | `drivers/net/.../rmnet` |
| 7 | `usb_maxpacket` 签名不匹配 | `drivers/`（3,503 文件） |
| 8 | `nla_nest_start_noflag` 未定义（netlink API） | `net/`（459 文件） |
| 9 | `shmem_init_fs_context` 未定义（VFS 新 mount API） | 剩余 `fs/`、`init/` |

回退总量：drivers 3,503、arch 2,434、include 308、net 459、fs 361、mm/kernel/security 168。
每退一层就牵出下一层，最后会退化成「全部取本树」——等价于没有合并。

根本原因：两棵 BSP 树的差异是结构性的。小米的驱动与框架改动依赖它自己的 `include/`
和 `init/` 层，联想的 techpack、私有音频与显示驱动同样如此，任一侧只取一半都会在
另一侧断裂。这不是「多解几个冲突」能解决的，而是两套树的接口契约不同。

**结论**：merge 保留完整历史图，树内容维持已验证状态。上游对通用内核的实际改动，
落在 `c3df39c..c35bde4` 的 766 项提交里（668 文件，+6,452 / −2,782），可正常编译。

**为什么不用 cherry-pick 逐条重放**

上一轮试过：3,594 条第一父链逐条 pick，干净应用 1,263 条、空提交 185、冲突 979。
应用的 1,263 条编译时同样因成套迁移失败（kfence / mmap_lock / xarray / fuse / arm64
atomics / 新 mount API / BPF 指令集），与上面第 3～9 项是同一批问题。

## 构建脚本

`scripts/kconfig/`、`scripts/basic/` 曾在旧的本地仓库里被 `.git/info/exclude` 整目录
排除，导致 `olddefconfig` 报 `scripts/kconfig/Makefile: No such file or directory`。
当前历史以 smith-dog 的真实树为基线，101 个构建脚本文件完整存在；两条排除规则已从
`.git/info/exclude` 删除，clone 下来可直接编译。

