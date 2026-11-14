# 编译实测报告（README 编译链 · config-v2.2 + EROFS + 帖子 BPF）

## 结论

**编译成功**。`make ... Image` 退出码 0，产出合法的 ARM64 内核镜像：

| 项 | 值 |
|---|---|
| 产物 | `arch/arm64/boot/Image` → 交付于 `dist/Image` |
| 大小 | 50,724,880 字节（≈ 48.4 MB） |
| 格式 | `Linux kernel ARM64 boot executable Image, little-endian, 4K pages` |
| sha256 | `f3780bee74c89954fbd5e3052e2e4ac1003c6af35a05bee72af16c98115668a3` |
| 编译错误 / 未定义符号 | 0 / 0 |
| 版本横幅 | `Ubuntu clang version 21.1.8 (...), GNU ld (GNU Binutils for Ubuntu) 2.42` |

编译链全程按目标仓库 `README.md`「自己编译」章节，配置基线为 `tb371fc/config-v2.2.txt`
叠加 EROFS 6 项 + 酷安帖子要求的 12 项 BPF（共 18 项，最终全部生效）。

---

## 1. 编译环境

| 项 | 本沙箱实测 | README 要求 | 是否一致 |
|---|---|---|---|
| 编译器 | `Ubuntu clang version 21.1.8 (++20251221032922+...)` | Ubuntu clang 21.1.8 (6ubuntu1) | ✅ 一致 |
| 汇编/链接 | `GNU assembler (GNU Binutils for Ubuntu) 2.42` | aarch64-linux-gnu binutils 2.46 | ⚠️ 差一个小版本 |
| 宿主 | Ubuntu 24.04 (linux/amd64) | WSL2 Ubuntu | 等价 |
| triple | `CLANG_TRIPLE=aarch64-linux-gnu-`（gnu triple） | gnu triple | ✅ 一致 |

> binutils 2.42 与 2.46 的差异不影响本次链接（`LD vmlinux` / `OBJCOPY Image` 均成功），
> 但产出镜像的版本横幅会显示 2.42 而非出货横幅的 2.46。真机出货请用 WSL2 更新到 2.46 复编。

工具链安装：`apt.llvm.org noble-21` 源装 `clang-21` / `lld-21` / `llvm-21`，
命令里显式 `CC=clang-21`（覆盖 Makefile 第 421 行的 `python2 gcc-wrapper.py` 包装）。

---

## 2. 完整编译命令（README 出货配方）

```bash
KV=$(pwd)
python3 configs/make-config-v2.2.py .        # v2.2 基线 + EROFS + BPF
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=clang-21 \
     CLANG_TRIPLE=aarch64-linux-gnu- AS=aarch64-linux-gnu-as olddefconfig
make -j6 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=clang-21 \
     CLANG_TRIPLE=aarch64-linux-gnu- AS=aarch64-linux-gnu-as \
     KCFLAGS="-Wno-error -Wno-error=strict-prototypes -Wno-error=implicit-int \
-Wno-error=incompatible-pointer-types -Wno-error=date-time \
-include $KV/drivers/staging/fw-api/fw/p226_compat.h" \
     DYNAMIC_SINGLE_CHIP=qca6390 Image
```

前置步骤（均由 `build.sh` 串联）：应用 `5.10-bpf-tb371fc.diff` → `resolve-conflicts.py`
合入 `.rej` → `fix-symlinks.sh` 修断链 → `install-firmware.sh` 落位固件。

---

## 3. 逐轮迭代与错误修复过程

### 3.1 补丁残留冲突（20 个 `.rej`）

`git apply --reject` 后 20 个 `.rej`。判定：12 个已被补丁其它成功 hunk 覆盖或不该改，
8 个真缺失。`patches/resolve-conflicts.py` 幂等合入，另补多项编译/链接期兼容修复，
最终共 18 处带唯一性断言的精确替换。逐项见 `conflict-analysis.md`。

### 3.2 编译期错误（均已在 `resolve-conflicts.py` 固化）

| # | 报错 | 根因 | 修复 |
|---|---|---|---|
| 1 | `include/generated/compile.h`: `unknown type name 'Found'` | `clang -v` 输出含 `Found CUDA installation ... version ...`，被 `mkcompile_h` 的 `grep ' version '` 抓入，宏跨行 | `mkcompile_h` 取版本首行 `head -1` |
| 2 | `cgroup.h:849: redefinition of 'cgroup_id'` | 补丁把 `cgroup_id()` 提到公共区（`kn->id` 已改 u64），4.19 旧定义仍返回 `kn->id.ino` | 删除旧版定义，保留注释 |
| 3 | `tcp.h: no member named 'skb_mstamp'` | 5.10 用 `skb_mstamp_ns` | 合入 4 处：`skb_mstamp_ns` 换算、`tcp_init_transfer` 三参、`send_synack` 加 `syn_skb` |
| 4 | `skmsg.h:41: expected parameter declarator` | 4.19 `build_bug.h` 无 `static_assert()` | 补 `_Static_assert` 兼容宏 |
| 5 | `hooks.c: undeclared 'SECCLASS_ANON_INODE'` | SELinux classmap 缺 `anon_inode` | `classmap.h` 补 `{ "anon_inode", ... }` |
| 6 | `bpf_sk_storage_get_tracing_proto` 未声明 | `bpf_sk_storage.h` 被补丁当新建文件、目标树已有旧版同名头，两个 extern 没落地 | 补两个 tracing 变体 extern |

### 3.3 vendor / 环境适配（本轮新增，全部不改 `.config`）

| # | 报错 | 根因 | 修复 |
|---|---|---|---|
| 7 | `drivers/ksu_sym.c: 'linux/selinux.h' file not found` | 5.10 LSM 重构补丁删除 `include/linux/selinux.h`，vendor `ksu_sym.c` 仍 include | `resolve-conflicts.py` 的 `restore()` 恢复原 4.19 头（910 字节，与 tarball 原版逐字节一致） |
| 8 | `No rule to make target '/home/smith/t34/fw/tfa98xx_QS.cnt'` | v2.2 `CONFIG_EXTRA_FIRMWARE` 内建 QS 固件，但仓库只有 YC，且 `EXTRA_FIRMWARE_DIR` 指向作者本机路径 | 用户提供真机提取的 QS 二进制（`.txt` 仅上传后缀，26245 字节 `PM3_01` 魔数）；`firmware/` 随附两份，`install-firmware.sh` 幂等复制到目标目录 |
| 9 | `pinctrl-wcd.c: 'core.h' file not found` | `techpack/audio/soc/core.h` 等 3 个软链硬编码 `/home/smith/kernels/...`，沙箱断链；树内 `drivers/pinctrl/`、`drivers/base/regmap/` 有对应真文件 | `fix-symlinks.sh` 把断链重指向树内相对路径（幂等） |
| 10 | 链接 `undefined reference to bpf_jit_alloc_exec / bpf_jit_free_exec` | 5.10 `filter.h` 声明、trampoline/struct_ops/dispatcher 调用，但补丁源基于已含 5.4-bpf 的基线，纯净 4.19 无实现 | `resolve-conflicts.py` 按 5.10 upstream 在 `kernel/bpf/core.c` 补 `__weak` 版（`module_alloc`/`module_memfree`） |

> 说明：单独 `make xxx.o` 校验时曾出现 `soc/soundwire.h not found`，系未走 techpack
> 递归、`LINUXINCLUDE` 未带 `techpack/audio/include` 所致，全量 `make Image` 路径不存在该问题。

### 3.4 链接阶段

`MODPOST vmlinux.o` → `KSYM .tmp_kallsyms1/2.o` → `LD vmlinux` → `SORTEX` → `SYSMAP System.map`
→ `OBJCOPY arch/arm64/boot/Image`，全程仅 `-z norelro ignored` 警告（无害）。

---

## 4. 最终验证

**5.10-bpf 能力落地**（`vmlinux` 符号 / 文件核验）：

| 能力 | 证据 | 结果 |
|---|---|---|
| ringbuf map | `kernel/bpf/ringbuf.c` + `BPF_MAP_TYPE_RINGBUF` in uapi + `bpf_ringbuf_*` 符号 | ✅ |
| BPF trampoline | `bpf_trampoline_*` 符号 | ✅ |
| BPF_LSM | `security/bpf/` 目录 + `CONFIG_BPF_LSM=y` | ✅ |
| BPF_PRELOAD | `kernel/bpf/preload/` + `CONFIG_BPF_PRELOAD=y` | ✅ |
| fake uname | `kernel/sys.c` 中 `5.10.240` + bpfloader/netd 判定 | ✅ |
| Android16 防卡死 | `cgroup_sk_clone()` 含 `cgroup_bpf_get(sock_cgroup_ptr(skcd))` | ✅ |

**配置最终值**（`dist/config-v2.2-bpf-erofs.config`）：帖子 BPF 12 项 + EROFS 6 项全部生效，
`CONFIG_LSM="lockdown,yama,loadpin,safesetid,integrity,selinux,smack,tomoyo,apparmor,bpf"`。

---

## 5. 交付与限制

- 产物：`dist/Image`、`dist/System.map`、`dist/config-v2.2-bpf-erofs.config`，
  以及可直接刷入的 `dist/boot-5.10-bpf-v2.2-pure.img`（打包详见 `pack-report.md`）。
- 一键复现：`bash build.sh <kernel-tree>`；配置基线 `configs/make-config-v2.2.py`，
  冲突 `patches/resolve-conflicts.py`，环境适配 `patches/fix-symlinks.sh` +
  `configs/install-firmware.sh`，固件 `firmware/`。
- **未做真机验证**：沙箱无设备，刷机 / 开机 / SELinux / `bpfloader` / KernelSU LKM 行为
  需用户在设备上确认（刷入后开 DSU Android 16 GSI，`adb shell dmesg | grep -iE 'bpfloader|bpf'`）。
- **binutils 版本**：2.42 vs README 2.46，见第 1 节。
- 无 GitHub 凭证，未 push；工程包以本地文件交付。
