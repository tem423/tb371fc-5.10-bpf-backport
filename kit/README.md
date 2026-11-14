# TB371FC 4.19.325 → 5.10-bpf backport 工程包

针对 [smith-dog/kernel-tb371fc](https://github.com/smith-dog/kernel-tb371fc)（Lenovo TB371FC / SM8250 kona / Linux 4.19.325），
依据[酷安 tiffanyy 的帖子](https://www.coolapk.com/feed/64983795)补齐 Android 16 `bpfloader` 所需的 5.10 水平 BPF，
并把 [lss4/android_kernel_lenovo_paladin](https://github.com/lss4/android_kernel_lenovo_paladin) 的 CLO 提交接到仓库历史最前面。

---

## 结论先行

| 判断 | 依据 |
| --- | --- |
| 目标仓库是**纯净 4.19.325**，`include/uapi/linux/bpf.h` 2852 行、无 `BPF_MAP_TYPE_RINGBUF`，全树只有 `CONFIG_BPF_JIT=y` | 下载 main 源码包实测 |
| 帖子里的补丁链接**已改名/失效**，需要换成新地址 | 见第二节 |
| 帖子 25.7.27 那个 **49 提交的增量集不能直接用**在本仓库：实测 103 个文件段里 **77 处上下文冲突** | 它假设基线已是 LineageOS 22.2 / Android 15 的 5.10-bpf 水平，而本仓库没有 |
| 应改用**同平台 sm8250 的完整 1444 提交集**：777 个文件仅 25 处上下文冲突；剔除小米机型 defconfig 后只剩 **20 个 `.rej`**，且 `BPF_MAP_TYPE_RINGBUF`、`kernel/bpf/ringbuf.c` 已成功落地 | 见第五节实测 |
| lss4/paladin 与目标仓库**同源**：两者都从 Linux 根提交 `1da177e4`（2.6.12-rc2）开始，目标树里 `paladin_*_defconfig` 是指向 `kona_defconfig` 的软链 | 见第四节 |

一句话：**先接 CLO 历史，再打完整 5.10-bpf 补丁集（不是帖子那个增量集），最后补 defconfig。**

> **本工程包已实测跑通全链路**：按 README 编译链、`config-v2.2 + EROFS + 帖子 BPF` 编译出
> `dist/Image`（50,724,880 字节，0 error / 0 undefined），并以官方 v2.2 pure 基底打包出可直接
> `fastboot flash boot` 的 **`dist/boot-5.10-bpf-v2.2-pure.img`**（96 MB，读回门禁全通过）。
> 详见 `reports/build-report.md`（编译）与 `reports/pack-report.md`（打包）。

---

## 一、酷安帖子讲了什么

Android 16 beta2 起，GSI 启动时 `bpfloader` 会检查内核 BPF 能力；4.19 及更早的原生内核加载 A16 的 eBPF 程序失败，
重启原因记为 `bpfloader-failed`，表现是 DSU 一屏后回到主系统。两条解法：

1. **内核侧**：反向移植 A16 所需 BPF 程序（即"合并 BPF"）——本工程包走这条；
2. **system 层**：使用已处理好的 GSI（帖子发布时尚不可用）。

帖子明确要求"红线范围内都要合并"，并给出 defconfig 检查清单：

```
CONFIG_CGROUP_BPF=y      CONFIG_BPF=y                 CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT_ALWAYS_ON=y  CONFIG_NETFILTER_XT_MATCH_BPF=y  CONFIG_NET_CLS_BPF=y
CONFIG_BPF_JIT=y         CONFIG_HAVE_EBPF_JIT=y
```

若 backport 到 **5.10 水平**，还需追加：

```
CONFIG_BPF_LSM=y
CONFIG_BPF_PRELOAD=y
CONFIG_LSM="lockdown,yama,loadpin,safesetid,integrity,selinux,smack,tomoyo,apparmour,bpf"
```

另有两条重要提醒：**之前合过 5.4-bpf 的要全部推掉再合 5.10**；卡死重启需参考 ApartTUSITU 新增的那几个补丁。

---

## 二、帖子里的链接已经变了（重要）

| 帖子原文 | 现状 |
| --- | --- |
| `jsdizkcksv/android_kernel_xiaomi_msm8937` 的 `5.10` 分支（25.7.27 更新） | 仓库已改名为 **[Mi8937/msm-4.19](https://github.com/Mi8937/msm-4.19)**，`5.10` 分支已删除；现有 `5.10-bpf-min`、`5.15-bpf`（默认）、`lineage-22.2` |
| `jsdizkcksv/android_kernel_aresin`（4.14-BPF） | 仍在，默认分支 `A16` |
| `jsdizkcksv/android_kernel_xiaomi_sdm660`（4.4→5.4） | 仍在，默认 `main` |
| `ApartTUSITU/kernel_xiaomi_sm8250_mod/commits/android16-aptusitu/`（防卡死补丁） | 仓库现有 `backport-5.4-bpf`、**`backport-5.10-bpf`**、`android16-aptusitu`、`android16-aptusitu-new` 等分支 |
| `MTK6893/lineage_kernel_xiaomi_sdm845`（4.9→5.4） | 仍在，默认 `lineage-23.0` |

完整的提交号、下载地址与分支关系见 [reports/sources.md](reports/sources.md)。

---

## 三、目标仓库实测状态

| 项目 | 值 |
| --- | --- |
| 内核 | `4.19.325`（`Makefile`: VERSION 4 / PATCHLEVEL 19 / SUBLEVEL 325） |
| 平台 | SM8250 kona；`arch/arm64/configs/vendor/kona_defconfig`（849 行）为实际构建配置 |
| paladin 关联 | `paladin_prc_*_defconfig`、`paladin_row_*_defconfig` 全部是**指向 `kona_defconfig` / `kona-perf_defconfig` 的软链** |
| BPF 基线 | `include/uapi/linux/bpf.h` 2852 行，无 ringbuf / BPF_LSM / sk_storage / CAP_BPF |
| BPF 配置 | 主 `defconfig` 仅第 160 行 `CONFIG_BPF_JIT=y`；`CONFIG_SECURITY=y` |
| Git 历史 | 根提交 `1da177e4`（Linux-2.6.12-rc2），含完整 Linux 主线；tag `v4.19.325`、`v4.19.157`、`v1.0`~`v2.2` |

---

## 四、"在仓库最前面合上 lss4 的提交就完整了"

[lss4/android_kernel_lenovo_paladin](https://github.com/lss4/android_kernel_lenovo_paladin) 是 **CLO-rebased kernel for Lenovo TB-Q706F/Q706Z (paladin)**，
默认分支 `11`，tip `3734e88`（2024-06-02，Merge tag `LA.UM.9.12.1.r1-08900-SMxx50.QSSI12.0`）。

关键事实：

- 两个仓库都从 **同一个 Linux 根提交 `1da177e4c3f4`** 开始，共享完整主线历史；目标仓库约 81.4 万提交，paladin 约 82.2 万提交，
  差值约 **7781 个 CLO/CAF vendor 提交**（`LA.UM.*` tag 合并、msm/kgsl/npu/cnss2 修复、Loop/块层 backport 等）。
- 目标仓库的源码树本身就带 paladin 机型配置（软链），说明二者是**同一份联想 GPL/CLO 源码的不同 git 历史**，
  把 paladin 的提交接在最前面即可补齐 CLO 基线，历史与源码版本链完整，也便于后续 cherry-pick / merge 有更近的共同祖先。
- 但要注意：**paladin 的 BPF 水平同样是原生 4.19**（其 `bpf.h` 2835 行，同样没有 ringbuf / BPF_LSM），
  所以"接历史"并不会替代 5.10-bpf 补丁，两步都要做。

脚本提供三种接法（默认 `history`）：

| 模式 | 命令 | 适用 |
| --- | --- | --- |
| `history` | `git merge -s ours paladin/11` | 源码已完整，只想把 CLO 历史接到最前面（**推荐**，不改工作树内容） |
| `full` | `git merge paladin/11` | 想把 CLO 的代码改动也合进来（冲突多，需人工裁决） |
| `rebase` | `git rebase --onto paladin/11 <merge-base>` | 要求历史严格线性、paladin 全部提交位于最前 |

---

## 五、补丁集选择与实测数据

三套候选，均已下载到 `patches/`：

| 补丁集 | 规模 | 相对基线 | 对目标树试应用结果 |
| --- | --- | --- | --- |
| **`5.10-bpf-tb371fc.diff`**（推荐，由 ApartTUSITU 裁剪） | 711 文件段 / 3.6 MB | `android15-lineage22-mod → backport-5.10-bpf`（1444 提交） | **20 个 `.rej`**，核心 BPF 全部落地 |
| `apartusitu-backport-5.10-bpf.patch` | 1444 提交 / 8.1 MB 邮箱 | 同上 | 可用 `git am` 保留完整提交历史 |
| `mi8937-5.10-bpf-min.patch` | 49 提交 / 385 KB | `lineage-22.2 → 5.10-bpf-min` | **77 处冲突**（14 个 BPF 核心文件），**不可单独用于本仓库** |
| `android16-bpf-hotfix.diff` | 1 段 / 1 行 | `backport-5.10-bpf → android16-aptusitu` 的 BPF 部分 | `cgroup_sk_clone()` 补 `cgroup_bpf_get()`；**1444 集已包含，通常无需追加** |
| `apartusitu-android16-fixes.diff` | 71 提交 / 170 文件 | `android16-aptusitu → android16-aptusitu-new` | 另一条路线（含 KSU/SuSFS），**默认不叠加** |
| `apartusitu-5.4-to-5.10-bpf.diff` | 1444 提交 | `backport-5.4-bpf → backport-5.10-bpf` | 备用：仅在已合 5.4-bpf 时使用 |

**关于"卡死重启补丁"的核实**：`android16-aptusitu` 相对 `backport-5.10-bpf` 只有 15 个提交，
其中 14 个是 KernelSU / SuSFS，唯一与 BPF 相关的是 `kernel/cgroup/cgroup.c` 里
`cgroup_sk_clone()` 补一行 `cgroup_bpf_get(sock_cgroup_ptr(skcd))`。
而完整 1444 提交集的末位提交正是 `9b1f3c8738 fixup! bpf: decouple the lifetime of cgroup_bpf from cgroup itself`，
实测打完主补丁后该行**已经存在**（`kernel/cgroup/cgroup.c:6393`）。
所以脚本默认只做校验、不盲目叠加；把另一条路线的 101 段补丁强行叠上去会新增 66 个 `.rej`，得不偿失。

**为什么不用帖子那个 49 提交集**：它的基线 `Mi8937/msm-4.19:lineage-22.2` 的 `bpf.h` 已有 5134 行、含
`BPF_MAP_TYPE_RINGBUF` / `BPF_PROG_TYPE_LSM` / `BPF_LINK_CREATE` / `BPF_MAP_TYPE_STRUCT_OPS`；
而目标树只有 2852 行。49 个提交只是"从 A15 补齐到 A16"的增量，缺了 4.19→5.4/5.10 的整个主体。

**实测方法**：把 `main` 源码包解包后 `git apply --check`，再 `git apply --reject` 实打：

```
777 个文件段 → 25 处上下文冲突、48 个目标树缺失文件（全是小米机型 defconfig）
剔除 arch/arm64/configs/、.github/、README.md 后 → 711 段、20 个 .rej
结果: include/uapi/linux/bpf.h 出现 BPF_MAP_TYPE_RINGBUF、kernel/bpf/ringbuf.c 已生成
```

逐文件处理建议见 [reports/conflict-analysis.md](reports/conflict-analysis.md)。

---

## 六、操作步骤

> 脚本需要在**你本地完整的 git 仓库**上执行（沙箱内只做了试应用验证，无法推送、也无法编译）。

```bash
git clone https://github.com/smith-dog/kernel-tb371fc.git
cd kernel-tb371fc

# 默认：history 模式接 CLO 历史 + diff 模式应用补丁 + 附加补丁 + 合 defconfig
bash /path/to/tb371fc-5.10-bpf-backport/backport.sh .

# 其它组合示例
bash backport.sh . --paladin=rebase --bpf=am       # 严格线性 + 保留 1444 提交历史
bash backport.sh . --paladin=none --bpf=none --config=no   # 只跑指定步骤
bash backport.sh . --commit                        # 处理完 .rej 后自动提交
```

脚本会创建 `backport-5.10-bpf` 分支，产出 `reports/backport-run.log`、`reports/reject-files.txt`、
`reports/git-status.txt`。**默认不自动提交**，先检查 `git status` 与 `.rej`。

顺序不能颠倒：先接历史 → 再打 5.10-bpf → 校验 cgroup_bpf fixup → 最后改 defconfig。
脚本默认 `--extra=check`：确认 `cgroup_bpf_get()` 已在树中即可，缺才补 `android16-bpf-hotfix.diff`；
只有明确要走 KSU/SuSFS 那条路线时才用 `--extra=full`。
如果之前合过 5.4-bpf，按帖子要求**全部推掉重来**，不要用 `apartusitu-5.4-to-5.10-bpf.diff` 叠加。

---

## 七、defconfig

`configs/bpf-5.10.fragment` 收录帖子要求的全部配置项（含 5.10 特有的 `BPF_LSM` / `BPF_PRELOAD` / `LSM=`）。
`configs/apply-config.sh` 幂等写入三个文件（先删旧值再追加，可重复执行）：

- `arch/arm64/configs/defconfig`
- `arch/arm64/configs/vendor/kona_defconfig`
- `arch/arm64/configs/vendor/kona-perf_defconfig`

`paladin_*_defconfig` 是软链，会自动跟随 `kona_defconfig`，无需单独改。

注意：`CONFIG_HAVE_EBPF_JIT` 由架构 Kconfig `select`，`make olddefconfig` 可能自行处理；
`CONFIG_DEBUG_INFO_BTF=y` 可选（A16 ebpf 模块 / bpftool 调试用，需要 pahole ≥ 1.21 与支持 BTF 的工具链），
默认注释掉，避免构建因缺 pahole 失败。

---

## 八、编译与验证

### 原仓库要求的编译链（README.md「自己编译」章节 = v2.0 出货配方）

| 项 | 要求 |
|---|---|
| 宿主 | WSL2 Ubuntu |
| 编译器 | **Ubuntu clang 21.1.8 (6ubuntu1)**；v1.9 及更早为 Snapdragon LLVM 10.0.7 |
| 链接器 / 汇编器 | `aarch64-linux-gnu` binutils **2.46** |
| 出货横幅 | `Linux version 4.19.325-perf++ (...) (Ubuntu clang version 21.1.8 (6ubuntu1), GNU ld 2.46) #312` |
| **配置基线** | `cp tb371fc/config-v2.0.txt .config`（= 出货配置，与设备 `/proc/config.gz` 排序后逐行相等），**不是** `make defconfig` + vendor merge |
| 编译 FLAGS | `ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=clang CLANG_TRIPLE=aarch64-linux-gnu- AS=aarch64-linux-gnu-as` |
| KCFLAGS | `-Wno-error -Wno-error=strict-prototypes -Wno-error=implicit-int -Wno-error=incompatible-pointer-types -Wno-error=date-time -include $KV/drivers/staging/fw-api/fw/p226_compat.h` |
| 其它 | `-j6`、`DYNAMIC_SINGLE_CHIP=qca6390`（qcacld 取 qca6390 变体）、目标 `Image` |
| 模块链 | 同树同一份 `.config` 再跑 `make ... modules`、`make ... M=drivers/kernelsu modules`，勿混用旧产物 |

```bash
KV=$(pwd)
cp tb371fc/config-v2.0.txt .config          # 出货配置（已含 CONFIG_BPF / CGROUP_BPF）
# 再叠加 configs/bpf-5.10.fragment / apply-config.sh 中帖子要求的 BPF 项，然后：
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=clang \
     CLANG_TRIPLE=aarch64-linux-gnu- AS=aarch64-linux-gnu-as olddefconfig
make -j6 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=clang \
     CLANG_TRIPLE=aarch64-linux-gnu- AS=aarch64-linux-gnu-as \
     KCFLAGS="-Wno-error -Wno-error=strict-prototypes -Wno-error=implicit-int \
-Wno-error=incompatible-pointer-types -Wno-error=date-time \
-include $KV/drivers/staging/fw-api/fw/p226_compat.h" \
     DYNAMIC_SINGLE_CHIP=qca6390 Image
```

三个易踩的坑（均来自仓库脚本注释）：

- `CC=clang` 必须显式传——Makefile 第 421 行把 `CC` 包成 `python2 scripts/gcc-wrapper.py $(REAL_CC)`，
  仓库靠命令行覆盖掉这层 wrapper（`gcc-wrapper.py` 已被仓库改成 python3 直通）。
- `CLANG_TRIPLE=aarch64-linux-gnu-`（**gnu** triple）不能换成 android triple：
  `tb371fc/scripts/p48-v27-gnutriple.sh` 记录根因——Snapdragon LLVM 10.0.7 用 android triple 会生成
  TLS 栈金丝雀（`mrs tpidr_el0`），引导链从未初始化 TPIDR_EL0，导致开机静默死亡。
- `build.config.common` 里的 `LLVM=1` + `clang-r399163b` 是 GKI/ACK 官方 `build.config` 路径，
  本设备构建不走它；以 README 章节与 `tb371fc/scripts/` 里的 `make` 命令为准。

**配置基线**：用 v2.2 出货配置，而非 `make defconfig`：
```bash
python3 configs/make-config-v2.2.py .        # tb371fc/config-v2.2.txt + EROFS + 帖子 BPF
make ARCH=arm64 ... olddefconfig              # 用上面的 FLAGS
```
`make-config-v2.2.py` 幂等，叠加 **EROFS 6 项**（`EROFS_FS` / `XATTR` / `POSIX_ACL` / `SECURITY` / `ZIP` / `CLUSTER_PAGE_LIMIT`）
与**帖子要求的 12 项 BPF 配置**（含 `BPF_LSM` / `BPF_PRELOAD` / `LSM=`），共 18 项。

**冲突处理**：`5.10-bpf-tb371fc.diff` 应用后会产生 20 个 `.rej`，
用 `patches/resolve-conflicts.py` 一次性解决（幂等、带唯一性断言）：
```bash
git apply --reject --whitespace=nowarn patches/5.10-bpf-tb371fc.diff
python3 patches/resolve-conflicts.py .        # 合入 16 处
find . -name '*.rej' -delete
```
逐项判定见 `reports/conflict-analysis.md`：20 个 `.rej` 中只有 8 个是真缺失，
其余 12 个已被补丁其它成功 hunk 覆盖（`sysctl.h` 签名组、`exit.c`、`cgroup-defs.h`/`kernfs.h` 枚举、
`LSM_TABLE()`/`BTF`/`.BTF_ids` 段）或本就不该改（`compiler-clang.h` 的 `__assume_aligned` 仍被 `slab.h` 使用）。
`resolve-conflicts.py` 还合入编译期/链接期暴露的兼容修复（`static_assert`、`selinux.h` 恢复、
`bpf_jit_alloc_exec/free_exec` 的 `__weak` 实现等），共 18 处，全部幂等、带唯一性断言。

**环境适配（两项，均因仓库硬编码了作者本机绝对路径，与编译链本身无关）**：

| 问题 | 报错 | 处理 |
|---|---|---|
| 内建音频固件缺失 | `No rule to make target '/home/<原作者>/t34/fw/tfa98xx_QS.cnt'` | `firmware/` 随附 QS/YC 两份 `.cnt`；`configs/install-firmware.sh` 幂等复制到 `CONFIG_EXTRA_FIRMWARE_DIR` |
| techpack 断链软链 | `pinctrl-wcd.c: fatal error: 'core.h' file not found` | `patches/fix-symlinks.sh` 把 3 个指向 `/home/<原作者>/kernels/...` 的断链重指向树内相对路径 |

两项都不改 `.config`——**v2.2 出货配置与 README 编译链保持原样**。`tfa98xx_QS.cnt` 由用户按 README
说明从真机 `/vendor/firmware` 提取提供（`.txt` 仅为上传后缀，内容是原始二进制，26245 字节、`PM3_01` 魔数）。

**一键复现**：把上述补丁→冲突→配置→软链→固件→编译 7 步串起来：
```bash
bash build.sh /path/to/kernel-tree            # 产出 arch/arm64/boot/Image
bash build.sh /path/to/kernel-tree --config-only   # 只生成 .config，不编译
```

1. `make olddefconfig` 后检查 `.config` 中上述 CONFIG 均为 `y`。
2. 编译，重点盯 `kernel/bpf/`、`kernel/trace/bpf_trace.c`、`security/bpf/`、`net/core/filter.c` 的报错。
3. 刷入后开 DSU Android 16 GSI，验证：
   ```bash
   adb shell dmesg | grep -iE 'bpfloader|bpf'
   adb shell uname -r
   ```
   不再出现 `bpfloader-failed`，且 `bpfloader` 能正常加载程序，即 backport 成功。
4. 若出现卡死/重启，先确认 `kernel/cgroup/cgroup.c` 的 `cgroup_sk_clone()` 里有
   `cgroup_bpf_get(sock_cgroup_ptr(skcd))`（缺则打 `android16-bpf-hotfix.diff`），
   再检查 `CONFIG_LSM` 中 `bpf` 是否排在有效位置（BPF_LSM 需要 LSM 框架重构补丁一起到位）。

### 打包成可刷的 boot.img

`Image` 不能直接刷，需要用仓库自带的 `tb371fc/tools/repack_boot.py` 打进**基底 boot.img**
（保留 header v2 / 原厂 ramdisk / DTB 尾，只换 kernel 段）。基底必须取官方 Release
v2.2 的完整镜像（100663296 字节）：

```bash
curl -L -o boot-v2.2-pure-flash.img \
  "https://gh-proxy.com/https://github.com/smith-dog/kernel-tb371fc/releases/download/v2.2/boot-v2.2-pure-flash.img"
bash pack-boot.sh boot-v2.2-pure-flash.img dist/Image dist/boot-5.10-bpf-v2.2-pure.img
adb reboot bootloader && fastboot flash boot dist/boot-5.10-bpf-v2.2-pure.img && fastboot reboot
```

- 本产物是 **pure（无 root）**：ramdisk 原样保留官方 pure 基底，不含 `kernelsu.ko`。
  要 KernelSU root 就把基底换成 `boot-v2.2-kspatched-flash.img`，命令相同。
- `pack-boot.sh` 内置从**输出字节**读回的门禁：内嵌 kernel md5 与 `Image` 一致、
  ramdisk / DTB 尾逐字节保留、`kernel_size`/`dtb_size` 正确、补齐到 96 MB 分区。
- 直连 GitHub 在本沙箱约 16 KB/s（会截断），镜像代理 13 秒下完；务必校验基底大小。

逐项数据与校验见 `reports/pack-report.md`。

---

## 九、限制与风险

- **无法推送**：当前环境没有 GitHub 凭证，所有改动以本地分支 + 补丁文件交付，需你自行 `git push` / 提 PR。
- **编译链版本**：已装 **Ubuntu clang 21.1.8**（与 README 出货配方一致）；沙箱是 Ubuntu 24.04，
  `aarch64-linux-gnu` binutils 只有 **2.42**（README 要 2.46，需 WSL2 更新发行版）。编译器完全一致，链接器差一个小版本。
- **编译验证范围**：已按 README 配方（`CC=clang-21`、`gnu triple`、`KCFLAGS` 含 `p226_compat.h`、
  `-j6`、`DYNAMIC_SINGLE_CHIP=qca6390`、`config-v2.2` 基线）**实测编译成功**，`make Image` 退出码 0、
  0 error / 0 undefined，产出 `dist/Image`（50,724,880 字节，合法 ARM64 boot Image）；
  `vmlinux` 含 `bpf_ringbuf_*` / `bpf_trampoline_*` 等 5.10 符号，18 项配置全部生效。
  详见 `reports/build-report.md`。沙箱无真机，刷机/开机/SELinux/BPF_LSM 行为仍需你在设备上验证。
- **BPF_LSM / `CONFIG_LSM=` 风险**：会改动 SELinux / LSM 初始化顺序，务必真机验证开机与 SELinux 状态。
- **补丁集跨度大**：1444 提交里包含 cgroup_bpf 解耦、pidfd、LSM blob 管理、SELinux/Smack/Tomoyo 重构等非 BPF 改动，
  与联想 vendor 驱动可能耦合；建议先在一台可救砖的设备上验证。
- 帖子强调"注意红线范围内都要合并"：不要挑着合，缺任一环 `bpfloader` 仍会失败。

---

## 十、文件清单

```
tb371fc-5.10-bpf-backport/
├── README.md                      本文件
├── backport.sh                    工程包生成脚本（接历史 + 打补丁 + 改配置 + 报告）
├── build.sh                       ★ 一键复现：补丁→冲突→v2.2 配置→软链→固件→Image
├── pack-boot.sh                   ★ 一键打包：Image + 基底 boot.img → 可刷 boot.img（含读回门禁）
├── tools/
│   └── repack_boot.py             目标仓库自带的 boot.img 重打包工具
├── firmware/                      ★ 出货音频固件（用户提供的 QS + 仓库自带的 YC）
│   ├── tfa98xx_QS.cnt
│   └── tfa98xx_YC.cnt
├── configs/
│   ├── bpf-5.10.fragment          defconfig 配置片段
│   ├── apply-config.sh            幂等合入配置（写 defconfig）
│   ├── make-config-v2.2.py        ★ 以 config-v2.2.txt 为基线 + EROFS + 帖子 BPF 生成 .config
│   └── install-firmware.sh        ★ 幂等把两份 .cnt 复制到 CONFIG_EXTRA_FIRMWARE_DIR
├── patches/
│   ├── 5.10-bpf-tb371fc.diff      ★ 推荐：裁剪后的 5.10-bpf 聚合补丁
│   ├── resolve-conflicts.py       ★ 幂等解决 20 个 .rej + 编译/链接期兼容修复（18 处）
│   ├── fix-symlinks.sh            ★ 幂等修复 techpack 三个指向作者本机路径的断链
│   ├── android16-bpf-hotfix.diff   cgroup_bpf_get() 单行修复（主补丁已含，兜底用）
│   ├── android16-fixes-tb371fc.diff 另一路线的 101 段补丁（KSU/SuSFS，可选）
│   ├── apartusitu-backport-5.10-bpf.patch   1444 提交邮箱（保留历史用）
│   ├── apartusitu-backport-5.10-bpf.diff    原始聚合 diff
│   ├── mi8937-5.10-bpf-min.patch            帖子对应的 49 提交增量集（备查）
│   ├── apartusitu-android16-fixes.diff      原始 71 提交 diff
│   ├── aptusitu-android16-vs-5.10.diff      15 提交差异（用于核实防卡死补丁）
│   └── apartusitu-5.4-to-5.10-bpf.diff     已合 5.4-bpf 时的备用增量
├── reports/
│   ├── sources.md                 链接变更、commit SHA、补丁源映射
│   ├── conflict-analysis.md      20 个 .rej 的逐项判定（8 合 / 12 跳过）
│   ├── build-report.md           ★ 编译实测记录：编译链、10 类报错修复、最终验证
│   ├── pack-report.md            ★ boot.img 打包记录：基底、打包、读回门禁
│   └── rej-backup/               20 个原始 .rej 备份
└── dist/                          ★ 实测产物（本沙箱产出）
    ├── Image                      arch/arm64/boot/Image（50,724,880 字节）
    ├── boot-5.10-bpf-v2.2-pure.img  ★ 可 fastboot 刷入的 boot.img（96 MB, pure）
    ├── System.map
    └── config-v2.2-bpf-erofs.config   最终 .config
```
