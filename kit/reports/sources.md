# 补丁源映射与链接变更记录

## 原始需求来源

- 酷安帖子：[tiffanyy《内核比rom还重要》(feed/64983795)](https://www.coolapk.com/feed/64983795)，2025-05-25 发布，含 `25.7.27`、`25.9.14` 两次更新。
- 帖子关于 4.19 的关键结论：Android 16 beta2 起 `bpfloader` 强制要求内核 BPF 能力，4.19 原生内核会 `bpfloader-failed` 重启；解法是内核侧 backport BPF 到 5.10 水平，且"红线范围内都要合并"、之前合过 5.4 的要全部推掉重来。

## 仓库改名 / 分支变更对照

| 帖子里的地址 | 现状（2026-11 核实） | 说明 |
| --- | --- | --- |
| `github.com/jsdizkcksv/android_kernel_xiaomi_msm8937` 分支 `5.10` | 仓库重定向为 **[Mi8937/msm-4.19](https://github.com/Mi8937/msm-4.19)**；`5.10` 分支已不存在 | 现有分支：`5.10-bpf-min`（2026-03-31 有 fixup）、`5.15-bpf`（默认）、`lineage-22.2` |
| `github.com/jsdizkcksv/android_kernel_aresin` | [仍在](https://github.com/jsdizkcksv/android_kernel_aresin)，默认 `A16` | 4.14-BPF Patch |
| `github.com/jsdizkcksv/android_kernel_xiaomi_sdm660` | [仍在](https://github.com/jsdizkcksv/android_kernel_xiaomi_sdm660)，默认 `main` | 4.4 → 5.4 |
| `github.com/ApartTUSITU/kernel_xiaomi_sm8250_mod/commits/android16-aptusitu/` | [仍在](https://github.com/ApartTUSITU/kernel_xiaomi_sm8250_mod)，新增 `backport-5.4-bpf`、`backport-5.10-bpf`、`android16-aptusitu-new` 等分支 | 防卡死重启 / 同平台 sm8250 完整补丁源 |
| `github.com/MTK6893/lineage_kernel_xiaomi_sdm845` | [仍在](https://github.com/MTK6893/lineage_kernel_xiaomi_sdm845)，默认 `lineage-23.0` | 4.9 → 5.4 |

## 目标与历史基底

| 仓库 | 默认分支 | tip | 规模 |
| --- | --- | --- | --- |
| [smith-dog/kernel-tb371fc](https://github.com/smith-dog/kernel-tb371fc) | `main` | `c3df39c507`（2026-11-02） | 约 814319 提交，4.19.325，SM8250 kona |
| [lss4/android_kernel_lenovo_paladin](https://github.com/lss4/android_kernel_lenovo_paladin) | `11` | `3734e88336`（2024-06-02，Merge tag `LA.UM.9.12.1.r1-08900-SMxx50.QSSI12.0`） | 约 822100 提交，CLO-rebased，TB-Q706F/Q706Z |
| [ApartTUSITU/kernel_xiaomi_sm8250_mod](https://github.com/ApartTUSITU/kernel_xiaomi_sm8250_mod) | `android16-aptusitu` | `backport-5.10-bpf` 分支为补丁源 | 1444 提交 / 777 文件 |
| [Mi8937/msm-4.19](https://github.com/Mi8937/msm-4.19) | `5.15-bpf` | `5.10-bpf-min` tip `0f9b1dab43` | 49 提交 / 25 文件（相对 `lineage-22.2`） |

两者共同根提交：`1da177e4c3f41524e886b7f1b8a0c1fc7321cac2`（`Linux-2.6.12-rc2`，2005-04-16，无父提交）。
目标 tree 中 `arch/arm64/configs/vendor/paladin_*_defconfig` 均为指向 `kona_defconfig` / `kona-perf_defconfig` 的软链，
这是它与 lss4/paladin 同源的直接证据。

## 补丁下载地址（本工程包内文件的来源）

| 文件 | 源 URL |
| --- | --- |
| `apartusitu-backport-5.10-bpf.patch` | `https://github.com/ApartTUSITU/kernel_xiaomi_sm8250_mod/compare/android15-lineage22-mod...backport-5.10-bpf.patch` |
| `apartusitu-backport-5.10-bpf.diff` | 同上 `.diff` |
| `apartusitu-android16-fixes.diff` | `https://github.com/ApartTUSITU/kernel_xiaomi_sm8250_mod/compare/android16-aptusitu...android16-aptusitu-new.diff` |
| `apartusitu-5.4-to-5.10-bpf.diff` | `https://github.com/ApartTUSITU/kernel_xiaomi_sm8250_mod/compare/backport-5.4-bpf...backport-5.10-bpf.diff` |
| `mi8937-5.10-bpf-min.patch` | `https://github.com/Mi8937/msm-4.19/compare/lineage-22.2...5.10-bpf-min.patch` |
| `aptusitu-android16-vs-5.10.diff` | `https://github.com/ApartTUSITU/kernel_xiaomi_sm8250_mod/compare/backport-5.10-bpf...android16-aptusitu.diff`（15 提交） |
| `5.10-bpf-tb371fc.diff` | 由 `apartusitu-backport-5.10-bpf.diff` 剔除 `arch/arm64/configs/`、`.github/`、`README.md` 共 66 段后生成 |
| `android16-bpf-hotfix.diff` | 由 `aptusitu-android16-vs-5.10.diff` 只保留 `kernel/cgroup/cgroup.c` 段生成 |
| `android16-fixes-tb371fc.diff` | 由 `apartusitu-android16-fixes.diff` 剔除 69 段后生成（另一条路线，默认不用） |

## 关键提交（补丁集内，便于定位）

- `syscall: Fake uname to 4.19 for bpfloader/netd` — `f02e378411`（Mi8937）/ 同名提交在 ApartTUSITU 集内
- `syscall: Increase bpf fake uname to 5.10.240` — `c28474e65f`（Mi8937）/ `0fb77bce08`（ApartTUSITU）
- `msm8937: arm64: configs: Update BPF configs` — `fb83ac7f48`
- `BACKPORT: bpf: Implement BPF ring buffer and verifier support for it` — `439b487501`
- `UPSTREAM: bpf, capability: Introduce CAP_BPF` — `1cc7cbec6a`
- `fixup! bpf: decouple the lifetime of cgroup_bpf from cgroup itself` — `9b1f3c8738`（ApartTUSITU 集末）
- `arm64: configs: Enable CONFIG_XDP_SOCKETS=y` — `c2a6123a14`

## 基线 BPF 水平对比（`include/uapi/linux/bpf.h`）

| 分支 | 行数 | RINGBUF | BPF_LSM | SOCK_RELEASE | STRUCT_OPS | BPF_LINK_CREATE |
| --- | --- | --- | --- | --- | --- | --- |
| smith-dog/main（目标） | 2852 | ✗ | ✗ | ✗ | ✗ | ✗ |
| lss4/paladin `11` | 2835 | ✗ | ✗ | ✗ | ✗ | ✗ |
| Mi8937 `lineage-22.2`（49 提交集的基线） | 5134 | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mi8937 `5.10-bpf-min` | 3887 | ✓ | ✗ | ✓ | ✓ | ✗ |

结论：目标仓库与 lss4 都是原生 4.19 BPF 水平，因此必须用**完整 1444 提交集**，
而不是帖子那个以 A15/LineageOS 为基线的 49 提交增量集。

## 关于"卡死重启补丁"的最终判定

| 分支关系 | 提交数 | 性质 |
| --- | --- | --- |
| `android15-lineage22-mod → backport-5.10-bpf` | 1444 | 4.19 → 5.10-bpf 主体（本工程包采用） |
| `backport-5.10-bpf → android16-aptusitu` | 15 | 14 个 KernelSU/SuSFS + 1 个 `cgroup_bpf_get()` fixup |
| `android16-aptusitu → android16-aptusitu-new` | 71 | 另一条路线（devmap / xdp / flow_dissector 等 + 机型配置） |

1444 提交集的末位提交 `9b1f3c8738` 已包含 `cgroup_bpf` 生命周期修复，
干净树实测打完补丁后 `kernel/cgroup/cgroup.c` 中已有该调用，故**无需额外叠加防卡死补丁**。
