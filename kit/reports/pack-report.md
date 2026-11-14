# boot.img 打包报告（5.10-bpf 内核 → 可刷镜像）

## 结论

**打包成功**。用目标仓库自带的 `tb371fc/tools/repack_boot.py`，以官方 Release v2.2
**pure 镜像**为基底，把本次编译出的 `Image` 打成可直接 `fastboot flash boot` 的
`dist/boot-5.10-bpf-v2.2-pure.img`：

| 项 | 值 |
|---|---|
| 产物 | `dist/boot-5.10-bpf-v2.2-pure.img` |
| 大小 | 100,663,296 字节（= boot_a 分区几何，96 MB） |
| 格式 | Android bootimg, header v2, page 4096 |
| sha256 | `b913ac3304cde1defaad9a8765ce128cab54117d9e34aa0c6d57b49aac57283b` |
| 形态 | **pure**（原厂 v27n89 ramdisk，无 `kernelsu.ko`，无 root） |

---

## 1. 为什么需要「基底」镜像

`boot.img` 不是把 `Image` 改个后缀——它包含 header v2、kernel、ramdisk、second、
以及高通追加的 DTB 尾，且必须补齐到分区大小。仓库 README 明确给出了自打包方式：
用 `repack_boot.py` **保留 v2 头 / ramdisk / DTB 尾**，只替换 kernel 段并修正
`kernel_size` / `dtb_size`。ramdisk 与 DTB 必须来自真机/官方基底，无法凭空构造
（尤其 DTB 尾含 3 个 FDT，是开机必需）。

基底来源：官方 Release v2.2 的 `boot-v2.2-pure-flash.img`。
> 直连 GitHub 在本沙箱约 16 KB/s（3 分钟只下 2.98 MB 被截断）；改用镜像代理
> `gh-proxy.com` 后 13 秒下完完整 96 MB。**务必校验基底是 100663296 字节**，
> 截断的基底会缺 ramdisk/DTB，`repack_boot.py` 会报错或产出坏镜像。

---

## 2. 基底核验

| 字段 | 值 |
|---|---|
| magic / header version | `ANDROID!` / v2 |
| kernel_size | 50,722,832 |
| ramdisk_size | 1,145,940 |
| page_size | 4096 |
| dtb_size（头内） | 1,609,471 |
| DTB 尾 | 3 个 FDT，1,609,471 字节有效 |
| cmdline | `console=ttyMSM0,115200n8 earlycon=msm_geni_serial,0xa90000 androidboot.hardware=qcom ...` |
| ramdisk 条目 | 15，无 `kernelsu.ko` → 确认为 pure |

---

## 3. 打包命令（一键复现）

```bash
# 1. 取完整基底（直连慢时用镜像代理）
curl -L -o boot-v2.2-pure-flash.img \
  "https://gh-proxy.com/https://github.com/smith-dog/kernel-tb371fc/releases/download/v2.2/boot-v2.2-pure-flash.img"

# 2. 打包 + 从输出字节读回校验
bash pack-boot.sh boot-v2.2-pure-flash.img dist/Image dist/boot-5.10-bpf-v2.2-pure.img
```

底层即：
```bash
python3 tools/repack_boot.py <base.img> dist/Image <out.img>
```
工具动作：读基底 → 保留 ramdisk/second/DTB 尾 → kernel 段换成新 Image →
header `kernel_size` 改为 50,724,880、`dtb_size` 保持完整尾 → 补零到 96 MB。

---

## 4. 从输出镜像读回的门禁校验（全通过）

| 检查 | 结果 |
|---|---|
| 输出 magic / page / 总大小 | `ANDROID!` / 4096 / 100663296 | 
| `kernel_size` 字段 == `Image` 实际字节 | 50,724,880 ✓ |
| 内嵌 kernel 的 md5 == 编出 `Image` 的 md5 | `dce0cd85...9f1` ✓ |
| ramdisk 与基底逐字节相同 | 1,145,940 字节 ✓ |
| DTB 尾与基底逐字节相同 | 1,609,471 字节，FDT=3 ✓ |
| `pack-boot.sh` 两次独立运行产物 | `cmp` 逐字节一致（可复现）✓ |
| 诊断插桩门禁（`t58`/`hidg ep0`/`recorder thread started`） | 空 ✓ |

镜像 `strings` 命中 `5.10.240`、`bpfloader`、`bpf_ringbuf_*`，确认 5.10-bpf
能力确实在打包进的 kernel 里；版本横幅为
`Linux version 4.19.325-perf+ ... (Ubuntu clang version 21.1.8 ..., GNU ld 2.42) #2`。

---

## 5. 刷入与形态选择

```bash
adb reboot bootloader
fastboot flash boot boot-5.10-bpf-v2.2-pure.img
fastboot reboot
```

- **本产物是 pure（无 root）**：ramdisk 原样保留官方 pure 基底，未内嵌 KernelSU。
- 若需要 KernelSU root，把 `pack-boot.sh` 的基底换成官方
  `boot-v2.2-kspatched-flash.img` 即可，命令相同——工具会原样保留该基底自带的
  KSU ramdisk，kernel 仍是本 5.10-bpf 版。
- 刷前核对 `fastboot getvar current-slot`；本镜像按 boot_a 分区几何（96 MB）生成。

---

## 6. 限制

- **未做真机验证**：沙箱无设备，能否开机、`bpfloader` 是否通过、SELinux/BPF_LSM
  行为、5.10-bpf 在 Android 16 GSI 下的实际加载，均需你在设备上确认。
- **binutils 2.42**（README 出货要求 2.46）：只影响版本横幅，不影响镜像结构。
- 基底镜像来自官方 Release v2.2，与你的设备固件版本需匹配；若设备已在别的
  Android 版本/基带，建议用与你当前 slot 对应的 stock boot 作基底（工具通用）。
