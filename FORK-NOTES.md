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

## 上游完整历史（merge 提交）

`main` 顶端有一个 merge 提交，把
[AstideLabs/android_kernel_xiaomi_sm8250](https://github.com/AstideLabs/android_kernel_xiaomi_sm8250)
的 `android17-aptusitu-new` 完整历史接入本仓库：`c22009..5bdae44` 共 **9,575 个提交**，
可一路回溯到 Linux 根提交 `1da177e4`（2.6.12-rc2），总计 888,642 个提交对象。
`git log --graph` 能看到两条父系，作者、日期、提交信息全部保留。

**为什么用 `-s ours` 而不是逐条 cherry-pick**

实测把 3,594 条第一父链逐条重放到本树上：

| 结果 | 数量 |
|---|---|
| 干净应用 | 1,263 |
| 空提交（内容已存在，自动跳过） | 185 |
| 冲突（两树 BSP 差异，跳过） | 979 |
| 私有驱动 / 机型专属（预筛排除） | 225 |
| 已合过的 BPF（预筛排除） | 846 |

1,263 条应用后编译失败，原因是上游把以下子系统做成了**成套迁移**，只 pick 一部分
必然让结构体与头文件失配：

| 报错 | 根因 |
|---|---|
| `linux/kfence.h not found` | kfence 整套引入，header 缺失 |
| `struct mm_struct 无 mmap_lock` | mmap_lock 包装只落了一半 |
| `struct vm_fault 无 vma_flags` | 同上，vma 改造不完整 |
| `struct fuse_req 无 max_pages/inline_pages/misc` | fuse 重写不完整 |
| `xa_init_flags / XA_FLAGS_LOCK_IRQ 未定义` | radix-tree → xarray 迁移半套 |
| `arch_atomic_cmpxchg` 与 `atomic_cmpxchg` 并存 | arm64 atomics 改成 arch_ 前缀，但 `include/linux/atomic.h` 仍是 4.19 版 |
| `struct fib_nh 无 nh_common` | 路由表改造半套 |
| `memcg_cache_params 无 deact_work` | slab 重构半套 |
| `get_tree_single / ramfs_fill_super 未定义` | 新 mount API 只改了一半 |
| `BPF_ATOMIC 未定义` | BPF 指令集扩展与 uapi 版本不匹配 |

两棵树没有共同祖先（本树基线来自 tarball，非克隆历史），差异 15,395 个文件、
188 万行插入，冲突率 43%。继续逐个回滚只会牵出下一层依赖，最终退化成把上游改动
全部回滚——等价于没有合并。

因此按 ours 策略保留上游完整历史图、树内容维持已验证状态。**通用更新的实际改动
落在 `9093a27..f34b2c3` 的 766 项提交里**，可正常编译。

## 构建脚本修复

`scripts/kconfig/Makefile`、`mconf.c`、`lxdialog/*`、`scripts/basic/*` 等 8 个源码文件
曾被本地 `.git/info/exclude` 整目录排除，导致 `olddefconfig` 直接报
`scripts/kconfig/Makefile: No such file or directory`，**从本仓库 clone 下来也编不过**。
已在 `f34b2c3` 补回并移除该排除规则。

