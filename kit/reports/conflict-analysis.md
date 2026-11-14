# 补丁试应用实测与 20 个 `.rej` 处理建议

## 实测环境与方法

- 源码：`smith-dog/kernel-tb371fc` `main` 分支源码包（解包后 66820 个文件，`Makefile` = 4.19.325）。
- 补丁：`ApartTUSITU/kernel_xiaomi_sm8250_mod` 的 `android15-lineage22-mod...backport-5.10-bpf`（1444 提交）聚合 diff。
- 命令：
  ```bash
  git apply --check --verbose apartusitu-backport-5.10-bpf.diff
  git apply --reject --whitespace=nowarn \
      --exclude='arch/arm64/configs/*' --exclude='.github/*' --exclude='README.md' \
      apartusitu-backport-5.10-bpf.diff
  ```

## 结果

| 指标 | 数值 |
| --- | --- |
| 原始 diff 文件段 | 777 |
| `git apply --check` 上下文冲突 | 25 个文件 |
| 目标树缺失文件（小米机型 defconfig / CI） | 48 个 |
| 裁剪后文件段（`5.10-bpf-tb371fc.diff`） | 711 |
| 实际 `git apply --reject` 残留 `.rej` | **20 个** |
| 已落地的核心特性 | `BPF_MAP_TYPE_RINGBUF` 已出现在 `include/uapi/linux/bpf.h`；`kernel/bpf/ringbuf.c` 已生成 |

对照组：`mi8937-5.10-bpf-min.patch`（帖子 25.7.27 的 49 提交集）在同一源码树上
**103 个文件段里 77 处上下文冲突**，冲突集中在 `kernel/bpf/verifier.c`、`kernel/bpf/syscall.c`、
`include/linux/bpf.h`、`include/uapi/linux/bpf.h`、`net/core/filter.c` 等 BPF 核心文件，
证实它不能单独用于本仓库。

## 20 个 `.rej` 逐项建议

> 注意：`git apply --reject` 是"部分 hunk 成功、部分失败"，这些文件**已经被改过一部分**。
> 不能整个丢掉重来，要针对 `.rej` 里未应用的 hunk 手工补入。

### 必须处理（8 个，直接影响 BPF 功能或编译）

| 文件 | 作用 | 建议 |
| --- | --- | --- |
| `kernel/sys.c` | **fake uname**：对 `bpfloader` / `netd` / `netbpfload` 把内核版本伪装成 `5.10.240`（帖子 25.7.27 明确要求） | 手工合入 `sys_newuname` 相关 hunk；缺此项 A16 `bpfloader` 会直接判定内核过旧 |
| `include/asm-generic/vmlinux.lds.h` | 定义 `.BTF_ids` 等 linker section，`BTF_ID_LIST` / `btf_sock_ids` 构建期解析依赖 | 合入 `BTF_ID` 段定义，否则 `kernel/bpf/` 链接报错 |
| `include/linux/cgroup-defs.h` | `cgroup_bpf` 结构与生命周期解耦（`bpf: decouple the lifetime of cgroup_bpf`） | 合入结构体字段变更，否则 `kernel/bpf/cgroup.c` 类型不匹配 |
| `include/net/sock.h` | `sk_storage`、`socket cookie`、BTF sock ID 相关声明 | 合入；`bpf_sk_storage` / `bpf_skc_to_*` 依赖 |
| `include/net/tcp.h` | `tcp_congestion_ops` / `bpf_tcp_ca` struct_ops 支持 | 合入；`BPF_MAP_TYPE_STRUCT_OPS` 依赖 |
| `kernel/trace/bpf_trace.c` | tracing / `bpf_d_path` / task local storage / `RET_PTR_TO_BTF_ID` | 合入；BTF/tracing 程序依赖 |
| `net/ipv4/af_inet.c` | `BPF_CGROUP_INET_SOCK_RELEASE`、sk lookup helpers | 合入；A16 cgroup-sock 程序依赖 |
| `security/selinux/include/classmap.h`、`security/selinux/ss/services.c` | SELinux class/perm 与 security blob 管理（BPF_LSM 前置的 LSM 重构） | 两个一起合入；启用 `CONFIG_BPF_LSM=y` 时必需 |

### 建议检查后处理（2 个）

| 文件 | 说明 |
| --- | --- |
| `include/linux/kernfs.h` | kernfs/cgroup 接口调整，可能间接影响 cgroup_bpf；若编译报 `kernfs_*` 相关错误再补 |
| `include/linux/compiler-clang.h` | 编译器宏（Clang 构建常见）；用 Clang 编译时若报 `__no_sanitize` / BTF 宏未定义再补 |

### 可安全跳过（10 个，1444 提交集附带的上游改动，与 BPF 无直接关系）

```
arch/arm64/kernel/armv8_deprecated.c
drivers/char/random.c
drivers/net/wireless/virt_wifi.c
include/linux/timer.h
include/linux/virtio_net.h
kernel/exit.c                 # pidfd / P_PIDFD（除非编译报缺 pidfd_get_pid）
kernel/sched/fair.c
kernel/time/timer.c
net/ipv4/sysctl_net_ipv4.c
include/linux/timer.h        # 与上行重复计数时以 .rej 清单为准
```

跳过方式：直接删除对应 `.rej` 文件即可；文件里已被应用的 hunk 若引起编译错误，用
`git checkout <orig> -- <file>` 整文件还原。

## 手工合入冲突的推荐做法

1. **取参考分支的完整文件**对比（同平台 sm8250，最接近）：
   ```
   https://raw.githubusercontent.com/ApartTUSITU/kernel_xiaomi_sm8250_mod/backport-5.10-bpf/<文件路径>
   ```
   例：
   ```
   https://raw.githubusercontent.com/ApartTUSITU/kernel_xiaomi_sm8250_mod/backport-5.10-bpf/kernel/sys.c
   ```
2. 用 `diff -u` 对比目标树当前文件与参考文件，只搬 BPF 相关改动，保留联想 vendor 的私有修改。
3. 或者在本地仓库把参考分支 fetch 进来后用 `git apply --3way`（有共同 blob 时可直接三方合并）：
   ```bash
   git remote add aptusitu https://github.com/ApartTUSITU/kernel_xiaomi_sm8250_mod.git
   git fetch --no-tags aptusitu backport-5.10-bpf
   git apply --3way 5.10-bpf-tb371fc.diff
   ```
4. 全部处理完后执行 `find . -name '*.rej' -delete`，再 `make olddefconfig` 与编译。

## 附加补丁（防卡死重启）的核实

帖子提到"卡死重启可参考 `android16-aptusitu` 新增那几个补丁"。核实结果：

- `backport-5.10-bpf...android16-aptusitu` 只有 **15 个提交 / 42 个文件**，
  其中 14 个提交是 KernelSU / SuSFS（`fs/`、`drivers/`、`security/selinux/hooks.c` 等），
  唯一与 BPF 相关的是 `kernel/cgroup/cgroup.c`：
  ```c
  void cgroup_sk_clone(struct sock_cgroup_data *skcd)
  {
      ...
      cgroup_get(sock_cgroup_ptr(skcd));
  +   cgroup_bpf_get(sock_cgroup_ptr(skcd));   // cgroup_bpf 生命周期解耦 fixup
  }
  ```
- 完整 1444 提交集的末位提交 `9b1f3c8738` 就是
  `fixup! bpf: decouple the lifetime of cgroup_bpf from cgroup itself`。
  在干净树上打完 `5.10-bpf-tb371fc.diff` 后实测，`kernel/cgroup/cgroup.c:6393`
  **已经有 `cgroup_bpf_get(sock_cgroup_ptr(skcd))`**，因此该 fixup 已覆盖，无需再打。
- 若把另一条路线 `android16-aptusitu-new` 的 101 段补丁强行叠加，
  `.rej` 会从 20 个激增到 **86 个**（大量是 KSU/SuSFS 与机型配置冲突），不推荐。

结论：`backport.sh` 默认 `--extra=check`，只做存在性校验；`android16-bpf-hotfix.diff`
作为兜底，仅在校验失败时应用；`--extra=full` 保留给明确需要 KSU/SuSFS 的场景。

## 48 个"目标树缺失"文件

全部是参考仓库自己的机型配置，与目标设备无关，已在 `5.10-bpf-tb371fc.diff` 中剔除：

- `arch/arm64/configs/AOSP_defconfig/*_stock-defconfig`（8 个）
- `arch/arm64/configs/vendor/xiaomi/*`（14 个）
- `arch/arm64/configs/*_defconfig`（alioth / apollo / cmi / lmi / munch / pipa / psyche / umi / cas / dagu 等，26 个）

BPF 配置不靠它们，由 `configs/bpf-5.10.fragment` 统一写入 `kona_defconfig`。
