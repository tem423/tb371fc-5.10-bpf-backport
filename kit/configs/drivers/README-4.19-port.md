# PS5169 redriver —— 4.19.325 适配说明

## 来源

- 代码骨架与寄存器逻辑：`AkarinServer/Y700-Gen3-Droidian`（Lenovo kirby / Y700 Gen3）
  `kernel/lenovo/kirby/kernel/drivers/usb/redriver/ps5169.c`
- 4.19 调用方式：本仓库 `drivers/usb/misc/ssusb-redriver-nb7vpq904m.c`
  （extcon + power_supply + `get_redriver_exist()`）

设备树 `compatible` 两边一致：`hq_redriver,ps5169`。仓库内原驱动已经用这个
compatible，所以 **DTB 不用改**。

## 为什么要改

kirby 那份是 msm-5.10 的 `usb_redriver` 框架驱动，依赖：

```
include/linux/usb/redriver.h
drivers/usb/redriver/redriver.c    (usb_add_redriver / usb_remove_redriver)
```

4.19.325 树里没有这两个文件（`drivers/usb/phy/phy-msm-ssusb-qmp.c` 只
`extern bool get_redriver_exist(void)`），直接编译会报头文件缺失、结构体缺字段。

## 调用方式映射

| kirby（5.10 框架） | 4.19 实现 |
|---|---|
| `struct usb_redriver r` 内嵌 | 去掉，状态直接放 `struct ps5169_redriver` |
| `usb_add_redriver()` / `usb_remove_redriver()` | 删除；改由 extcon 注册/注销 |
| `release_usb_lanes(ur, ort, 4)` | `EXTCON_DISP_DP` 事件 `dp_lane == 4` → `OP_MODE_DP` |
| `release_usb_lanes(ur, ort, 2)` | `EXTCON_DISP_DP` 事件 `dp_lane == 2` → `OP_MODE_USB_AND_DP` |
| `notify_connect(ur, ort)` | `EXTCON_USB` / `EXTCON_USB_HOST` 置位 |
| `notify_disconnect(ur)` | 同上清零 → `OP_MODE_NONE` + auto power down |
| `gadget_pullup_enter/exit` | 无对应（4.19 由 vbus 状态覆盖，pullup workqueue 删除） |
| `host_powercycle` | 无对应（重新插拔即走一次 config work） |
| `r.of_node` / `r.bounded` | 不需要 |

保留不变的部分：

- 全部 PS5169 寄存器序列表（default / USB / USB_FLIP / DP / DP_FLIP / USB+DP / remove）
- chip id 读取 `0xad/0xac/0xae/0xaf`
- debugfs `ps5169_redriver/{dump_register,update_register}`
- `get_redriver_exist()` + `EXPORT_SYMBOL`（qmp.c 靠它改 PHY 0x1214/0x1614/0x1308/0x1708）
- PM suspend/resume、shutdown

## 默认序列的取值

kirby 版用 `CONFIG_ARCH_KIRBY` / `CONFIG_ARCH_LAPIS` 区分调参，TB371FC 不属于
任何一支。默认序列按 **本机原厂 4.19.157 Image-b .data** 取：

| 寄存器 | TB371FC 原厂 | kirby（else） | LAPIS |
|---|---|---|---|
| 0x50 | **0x20** | 0x00 | 0x10 |
| 0x54 | **0x11** | 0x01 | 0x11 |
| 0x5d | 0x66 | 0x66 | 0x65 |
| 0x52 | 0x50 | 0x50 | 0x50 |
| 0x5e | 0x06 | 0x06 | 0x06 |

其余 23 项完全一致。

## 安装

```bash
python3 configs/install-ps5169-4.19.py <KERNEL_ROOT>          # 预演
python3 configs/install-ps5169-4.19.py <KERNEL_ROOT> --apply  # 落地
```

脚本做四件事（幂等）：

1. 复制 `configs/drivers/ssusb-redriver-ps5169.c` → `drivers/usb/misc/`
2. `drivers/usb/misc/Kconfig` 增加 `config USB_REDRIVER_PS5169`（`select REGMAP_I2C`）
3. `drivers/usb/misc/Makefile` 增加 `obj-$(CONFIG_USB_REDRIVER_PS5169)`
4. `phy-msm-ssusb-qmp.c` 两处 `IS_BUILTIN(CONFIG_USB_REDRIVER_NB7VPQ904M)` → `PS5169`；
   `.config` 里 `NB7VPQ904M` 关、`PS5169=y`

## 编译验证

```
CC      drivers/usb/misc/ssusb-redriver-ps5169.o     (W=1 无警告)
AR      drivers/usb/misc/built-in.a
CC      drivers/usb/phy/phy-msm-ssusb-qmp.o
```

符号：

```
built-in.a:   T get_redriver_exist      (含 __ksymtab)
qmp.o:        U get_redriver_exist
```

`nb7vpq` 符号数为 0，两个驱动不会同时进内核。

## 事件链

```
Type-C 插入 → extcon(EXTCON_USB)  → config_work → 读 SS / polarity
                                                  → gen_dev_set(true)
DP alt mode → extcon(EXTCON_DISP_DP, 2 或 4 lanes) → op_mode 切换
拔线       → extcon 清零 → op_mode = NONE → 0x40 = 0x80 (auto power down)
```

设备树里 `extcon` 第 1 个 phandle 给 USB/HOST，第 2 个（可选）给 DP lane 事件；
只有一个 phandle 时 DP 事件不会进来，USB 侧照常工作。
