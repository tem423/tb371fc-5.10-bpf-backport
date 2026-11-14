// SPDX-License-Identifier: GPL-2.0-only
/*
 * Parade PS5169 USB Super Speed Linear Re-Driver
 *
 * 4.19 port of the downstream driver (Lenovo kirby / Y700-Gen3 tree,
 * drivers/usb/redriver/ps5169.c).
 *
 * 移植说明
 * --------
 * 下游版本基于 msm-5.10 的 usb_redriver 框架
 * (include/linux/usb/redriver.h + drivers/usb/redriver/redriver.c)，
 * 由框架回调 release_usb_lanes / notify_connect / notify_disconnect /
 * gadget_pullup_* / host_powercycle 驱动。
 *
 * 4.19.325 树里没有这套框架（phy-msm-ssusb-qmp.c 只 extern
 * get_redriver_exist()），因此本文件保留 PS5169 的全部寄存器逻辑，
 * 把事件源换成 4.19 现有的 extcon + power_supply 通知链：
 *
 *   usb_redriver 框架回调            4.19 对应实现
 *   --------------------------------  ------------------------------
 *   release_usb_lanes(ur, ort, 4)     EXTCON_DISP_DP 事件 dp_lane == 4
 *   release_usb_lanes(ur, ort, 2)     EXTCON_DISP_DP 事件 dp_lane == 2
 *   notify_connect(ur, ort)           EXTCON_USB / EXTCON_USB_HOST 置位
 *   notify_disconnect(ur)             EXTCON_USB / EXTCON_USB_HOST 清零
 *   gadget_pullup_enter/exit          (无对应，4.19 由 vbus 状态覆盖)
 *   host_powercycle                   (无对应，host 重新插拔即走一次 config)
 *
 * 设备树节点保持 compatible = "hq_redriver,ps5169"，
 * 可选属性：extcon = <&...>, <&...>;（第 2 个 phandle 用于 DP lane 事件）
 */

#include <linux/module.h>
#include <linux/of_device.h>
#include <linux/i2c.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/delay.h>
#include <linux/extcon.h>
#include <linux/power_supply.h>
#include <linux/usb/ch9.h>
#include <linux/debugfs.h>
#include <linux/uaccess.h>
#include <linux/regmap.h>
#include <linux/ctype.h>
#include <linux/seq_file.h>
#include <linux/notifier.h>

#define REDRIVER_REG_MAX		0xff
#define NOTIFIER_PRIORITY		1

#define LANES_DP			4
#define LANES_DP_AND_USB		2

/* ------------------------------------------------------------------ */
/* PS5169 register sequences                                          */
/*                                                                    */
/* Base: kirby tree ps5169.c. Values marked TB371FC are the stock      */
/* 4.19.157 Image-b .data values for this device (0x50=0x20,           */
/* 0x54=0x11); kirby/LAPIS use 0x50=0x00/0x10, 0x54=0x01/0x11.         */
/* ------------------------------------------------------------------ */

struct ps5169_reg_sequence {
	u8 reg_addr;
	u8 reg_value;
	u8 wait_time;		/* ms, 0 = write */
};

static const struct ps5169_reg_sequence ps5169_default_seq[] = {
	{0x9d, 0x80, 0},
	{0x00, 0x00, 10},
	{0x9d, 0x00, 0},
	{0x40, 0x80, 0},	/* auto power down */
	{0x04, 0x44, 0},	/* disable U1 status RX_Det */
	{0xa0, 0x02, 0},	/* disable AUX channel */
	{0x51, 0x87, 0},
	{0x50, 0x20, 0},	/* TB371FC tuning */
	{0x54, 0x11, 0},	/* TB371FC tuning */
	{0x5d, 0x66, 0},
	{0x52, 0x50, 0},	/* DP EQ 8.5dB */
	{0x55, 0x00, 0},
	{0x56, 0x00, 0},
	{0x57, 0x00, 0},
	{0x58, 0x00, 0},
	{0x59, 0x00, 0},
	{0x5a, 0x00, 0},
	{0x5b, 0x00, 0},
	{0x5e, 0x06, 0},
	{0x5f, 0x00, 0},
	{0x60, 0x00, 0},
	{0x61, 0x03, 0},
	{0x65, 0x40, 0},
	{0x66, 0x00, 0},
	{0x67, 0x03, 0},
	{0x75, 0x0c, 0},
	{0x77, 0x00, 0},
	{0x78, 0x7c, 0},
};

static const struct ps5169_reg_sequence ps5169_USB_seq[] = {
	{0x40, 0xc0, 0},	/* USB mode, no FLIP */
	{0x8d, 0x01, 0},	/* force RX1 50ohm termination on */
	{0x90, 0x01, 0},	/* force RX2 50ohm termination on */
};

static const struct ps5169_reg_sequence ps5169_USB_FLIP_seq[] = {
	{0x40, 0xd0, 0},	/* USB mode, FLIP */
	{0x8d, 0x01, 0},
	{0x90, 0x01, 0},
};

static const struct ps5169_reg_sequence ps5169_USB_remove_seq[] = {
	{0x40, 0x80, 0},	/* auto power down */
	{0x8d, 0x00, 0},
	{0x90, 0x00, 0},
};

static const struct ps5169_reg_sequence ps5169_DP_seq[] = {
	{0x40, 0xa0, 0},	/* DP mode, no FLIP */
	{0xa0, 0x00, 0},	/* enable AUX channel */
	{0xa1, 0x04, 0},	/* HPD */
};

static const struct ps5169_reg_sequence ps5169_DP_FLIP_seq[] = {
	{0x40, 0xb0, 0},	/* DP mode, FLIP */
	{0xa0, 0x00, 0},
	{0xa1, 0x04, 0},
};

static const struct ps5169_reg_sequence ps5169_DP_remove_seq[] = {
	{0x40, 0x80, 0},
	{0xa0, 0x02, 0},
	{0xa1, 0x00, 0},
};

static const struct ps5169_reg_sequence ps5169_USB_AND_DP_seq[] = {
	{0x40, 0xe0, 0},	/* USB + DP 2 lane, no FLIP */
	{0x8d, 0x01, 0},
	{0x90, 0x01, 0},
	{0xa0, 0x00, 0},
	{0xa1, 0x04, 0},
};

static const struct ps5169_reg_sequence ps5169_USB_AND_DP_FLIP_seq[] = {
	{0x40, 0xf0, 0},	/* USB + DP 2 lane, FLIP */
	{0x8d, 0x01, 0},
	{0x90, 0x01, 0},
	{0xa0, 0x00, 0},
	{0xa1, 0x04, 0},
};

static const struct ps5169_reg_sequence ps5169_USB_AND_DP_remove_seq[] = {
	{0x40, 0x80, 0},
	{0xa0, 0x02, 0},
	{0x8d, 0x00, 0},
	{0x90, 0x00, 0},
	{0xa1, 0x00, 0},
};

struct chip_id {
	u8 chip_id_1;
	u8 chip_id_2;
	u8 revision_1;
	u8 revision_2;
};

enum operation_mode {
	OP_MODE_NONE,		/* 4 lanes disabled */
	OP_MODE_USB,		/* 2 lanes USB */
	OP_MODE_DP,		/* 4 lanes DP */
	OP_MODE_USB_AND_DP,	/* 2 lanes USB + 2 lanes DP */
	OP_MODE_DEFAULT,	/* 4 lanes USB */
};

static const char * const opmode_string[] = {
	[OP_MODE_NONE] = "NONE",
	[OP_MODE_USB] = "USB",
	[OP_MODE_DP] = "DP",
	[OP_MODE_USB_AND_DP] = "USB and DP",
	[OP_MODE_DEFAULT] = "DEFAULT",
};

/* type-c 极性，取值与 extcon EXTCON_PROP_USB_TYPEC_POLARITY 对应 */
enum plug_orientation {
	ORIENTATION_CC1 = 0,
	ORIENTATION_CC2 = 1,
};

struct ps5169_redriver {
	struct device		*dev;
	struct regmap		*regmap;
	struct i2c_client	*client;

	struct power_supply	*usb_psy;
	bool			host_active;
	bool			vbus_active;
	bool			is_usb3;
	int			typec_orientation;
	enum operation_mode	op_mode;

	struct extcon_dev	*extcon_usb;
	struct extcon_dev	*extcon_dp;
	struct notifier_block	vbus_nb;
	struct notifier_block	id_nb;
	struct notifier_block	dp_nb;
	struct notifier_block	panic_nb;

	struct work_struct	config_work;
	struct workqueue_struct	*redriver_wq;

	struct chip_id		id;
	struct dentry		*debug_root;
};

static bool redriver_exist;

/* 原型仅供 -Wmissing-prototypes；调用方是 phy-msm-ssusb-qmp.c */
bool get_redriver_exist(void);

bool get_redriver_exist(void)
{
	return redriver_exist;
}
EXPORT_SYMBOL(get_redriver_exist);

static const struct regmap_config redriver_regmap = {
	.name = "ps5169",
	.max_register = REDRIVER_REG_MAX,
	.reg_bits = 8,
	.val_bits = 8,
};

static int redriver_i2c_reg_get(struct ps5169_redriver *redriver,
				u8 reg, u8 *val)
{
	unsigned int tmp;
	int ret;

	ret = regmap_read(redriver->regmap, (unsigned int)reg, &tmp);
	if (ret < 0) {
		dev_err(redriver->dev, "reading reg 0x%02x failure\n", reg);
		return ret;
	}

	*val = (u8)tmp;
	return 0;
}

static int redriver_i2c_reg_set(struct ps5169_redriver *redriver,
				u8 reg, u8 val)
{
	int ret;

	ret = regmap_write(redriver->regmap, (unsigned int)reg,
			   (unsigned int)val);
	if (ret < 0) {
		dev_err(redriver->dev, "writing reg 0x%02x failure\n", reg);
		return ret;
	}

	dev_dbg(redriver->dev, "writing reg 0x%02x=0x%02x\n", reg, val);
	return 0;
}

static int redriver_i2c_reg_table_set(struct ps5169_redriver *redriver,
				      const struct ps5169_reg_sequence *table,
				      int len)
{
	int i;
	int ret = -EINVAL;

	if (IS_ERR_OR_NULL(table))
		return ret;

	for (i = 0; i < len; i++) {
		if (table[i].wait_time != 0) {
			msleep(table[i].wait_time);
			continue;
		}

		ret = redriver_i2c_reg_set(redriver, table[i].reg_addr,
					   table[i].reg_value);
		if (ret < 0)
			dev_err(redriver->dev,
				"%s error: reg=0x%02x, value = 0x%02x\n",
				__func__, table[i].reg_addr,
				table[i].reg_value);
	}

	return ret;
}

static int redriver_set_default_mode(struct ps5169_redriver *redriver)
{
	dev_dbg(redriver->dev, "%s\n", __func__);

	return redriver_i2c_reg_table_set(redriver, ps5169_default_seq,
					  ARRAY_SIZE(ps5169_default_seq));
}

static int redriver_set_USB_mode(struct ps5169_redriver *redriver)
{
	if (redriver->typec_orientation == ORIENTATION_CC1)
		return redriver_i2c_reg_table_set(redriver, ps5169_USB_seq,
					ARRAY_SIZE(ps5169_USB_seq));
	else if (redriver->typec_orientation == ORIENTATION_CC2)
		return redriver_i2c_reg_table_set(redriver,
					ps5169_USB_FLIP_seq,
					ARRAY_SIZE(ps5169_USB_FLIP_seq));

	dev_err(redriver->dev, "%s unknow cc orientation: %d\n",
		__func__, redriver->typec_orientation);
	return -EINVAL;
}

static int redriver_set_DP_mode(struct ps5169_redriver *redriver)
{
	if (redriver->typec_orientation == ORIENTATION_CC1)
		return redriver_i2c_reg_table_set(redriver, ps5169_DP_seq,
					ARRAY_SIZE(ps5169_DP_seq));
	else if (redriver->typec_orientation == ORIENTATION_CC2)
		return redriver_i2c_reg_table_set(redriver,
					ps5169_DP_FLIP_seq,
					ARRAY_SIZE(ps5169_DP_FLIP_seq));

	dev_err(redriver->dev, "%s unknow cc orientation: %d\n",
		__func__, redriver->typec_orientation);
	return -EINVAL;
}

static int redriver_set_USB_AND_DP_mode(struct ps5169_redriver *redriver)
{
	if (redriver->typec_orientation == ORIENTATION_CC1)
		return redriver_i2c_reg_table_set(redriver,
					ps5169_USB_AND_DP_seq,
					ARRAY_SIZE(ps5169_USB_AND_DP_seq));
	else if (redriver->typec_orientation == ORIENTATION_CC2)
		return redriver_i2c_reg_table_set(redriver,
					ps5169_USB_AND_DP_FLIP_seq,
					ARRAY_SIZE(ps5169_USB_AND_DP_FLIP_seq));

	dev_err(redriver->dev, "%s unknow cc orientation: %d\n",
		__func__, redriver->typec_orientation);
	return -EINVAL;
}

static int redriver_remove_USB_mode(struct ps5169_redriver *redriver)
{
	return redriver_i2c_reg_table_set(redriver, ps5169_USB_remove_seq,
					ARRAY_SIZE(ps5169_USB_remove_seq));
}

static int redriver_remove_DP_mode(struct ps5169_redriver *redriver)
{
	return redriver_i2c_reg_table_set(redriver, ps5169_DP_remove_seq,
					ARRAY_SIZE(ps5169_DP_remove_seq));
}

static int redriver_remove_USB_AND_DP_mode(struct ps5169_redriver *redriver)
{
	return redriver_i2c_reg_table_set(redriver,
					ps5169_USB_AND_DP_remove_seq,
					ARRAY_SIZE(ps5169_USB_AND_DP_remove_seq));
}

static void ps5169_redriver_gen_dev_set(struct ps5169_redriver *redriver,
					bool on)
{
	int ret = -EINVAL;

	switch (redriver->op_mode) {
	case OP_MODE_NONE:
		/* 未连接 / probe 初始态：auto power down */
		ret = redriver_remove_USB_mode(redriver);
		break;

	case OP_MODE_USB:
	case OP_MODE_DEFAULT:
		if (on)
			ret = redriver_set_USB_mode(redriver);
		else
			ret = redriver_remove_USB_mode(redriver);
		break;

	case OP_MODE_DP:
		if (on)
			ret = redriver_set_DP_mode(redriver);
		else
			ret = redriver_remove_DP_mode(redriver);
		break;

	case OP_MODE_USB_AND_DP:
		if (on)
			ret = redriver_set_USB_AND_DP_mode(redriver);
		else
			ret = redriver_remove_USB_AND_DP_mode(redriver);
		break;

	default:
		dev_err(redriver->dev, "Error: op mode: %d.\n",
			redriver->op_mode);
		goto err_exit;
	}

	if (ret < 0)
		goto err_exit;

	return;

err_exit:
	dev_err(redriver->dev,
		"failure to (%s) the redriver chip, op mode: %d.\n",
		on ? "ENABLE" : "DISABLE", redriver->op_mode);
}

/* ------------------------------------------------------------------ */
/* config work: 4.19 事件源（extcon + power_supply）                    */
/* ------------------------------------------------------------------ */

static void ps5169_config_work(struct work_struct *w)
{
	struct ps5169_redriver *redriver = container_of(w,
			struct ps5169_redriver, config_work);
	struct extcon_dev *edev = redriver->extcon_usb;
	union extcon_property_value val;
	unsigned int extcon_id = EXTCON_NONE;
	int ret;

	dev_dbg(redriver->dev, "%s: op mode %s, vbus %d, host %d\n",
		__func__, opmode_string[redriver->op_mode],
		redriver->vbus_active, redriver->host_active);

	if (redriver->vbus_active)
		extcon_id = EXTCON_USB;
	else if (redriver->host_active)
		extcon_id = EXTCON_USB_HOST;

	if (edev && extcon_id != EXTCON_NONE &&
	    extcon_get_state(edev, extcon_id)) {
		ret = extcon_get_property(edev, extcon_id,
					  EXTCON_PROP_USB_SS, &val);
		if (!ret) {
			redriver->is_usb3 = (val.intval != 0);
			dev_dbg(redriver->dev, "SS Lane is used? [%s].\n",
				redriver->is_usb3 ? "true" : "false");
		} else {
			redriver->is_usb3 = true;
			dev_dbg(redriver->dev,
				"Default true as speed isn't reported.\n");
		}

		if (redriver->is_usb3 || redriver->op_mode != OP_MODE_USB) {
			ret = extcon_get_property(edev, extcon_id,
					EXTCON_PROP_USB_TYPEC_POLARITY, &val);
			if (!ret)
				redriver->typec_orientation = val.intval ?
					ORIENTATION_CC2 : ORIENTATION_CC1;
			else if (redriver->op_mode == OP_MODE_USB)
				redriver->typec_orientation = ORIENTATION_CC1;
			else
				dev_err(redriver->dev,
					"fail to get orientation when has DP.\n");

			ps5169_redriver_gen_dev_set(redriver, true);
		} else {
			dev_dbg(redriver->dev,
				"Disable chip when not in SS USB mode.\n");
			ps5169_redriver_gen_dev_set(redriver, false);
		}
	} else if (redriver->op_mode != OP_MODE_USB) {
		/* DP 仍在，主控可能已经关掉 USB host stack */
		dev_dbg(redriver->dev, "Update redriver operation mode.\n");
		ps5169_redriver_gen_dev_set(redriver, true);
	} else {
		dev_dbg(redriver->dev, "USB Cable is disconnected.\n");
		redriver->op_mode = OP_MODE_NONE;
		ps5169_redriver_gen_dev_set(redriver, false);
	}
}

static int ps5169_dp_notifier(struct notifier_block *nb,
			      unsigned long dp_lane, void *ptr)
{
	struct ps5169_redriver *redriver = container_of(nb,
			struct ps5169_redriver, dp_nb);
	enum operation_mode op_mode;

	dev_dbg(redriver->dev, "redriver op mode change: %ld lanes\n",
		dp_lane);

	switch (dp_lane) {
	case 0:
		op_mode = OP_MODE_USB;
		break;
	case LANES_DP_AND_USB:
		op_mode = OP_MODE_USB_AND_DP;
		break;
	case LANES_DP:
		op_mode = OP_MODE_DP;
		break;
	default:
		return 0;
	}

	if (redriver->op_mode == op_mode)
		return 0;

	redriver->op_mode = op_mode;

	queue_work(redriver->redriver_wq, &redriver->config_work);

	return 0;
}

static int ps5169_vbus_notifier(struct notifier_block *nb,
				unsigned long event, void *ptr)
{
	struct ps5169_redriver *redriver = container_of(nb,
			struct ps5169_redriver, vbus_nb);

	dev_dbg(redriver->dev, "vbus:%ld event received\n", event);

	if (redriver->vbus_active == (bool)event)
		return NOTIFY_DONE;

	redriver->vbus_active = (bool)event;

	queue_work(redriver->redriver_wq, &redriver->config_work);

	return NOTIFY_DONE;
}

static int ps5169_id_notifier(struct notifier_block *nb,
			      unsigned long event, void *ptr)
{
	struct ps5169_redriver *redriver = container_of(nb,
			struct ps5169_redriver, id_nb);
	bool host_active = (bool)event;

	dev_dbg(redriver->dev, "host_active:%s event received\n",
		host_active ? "true" : "false");

	if (redriver->host_active == host_active)
		return NOTIFY_DONE;

	redriver->host_active = host_active;

	queue_work(redriver->redriver_wq, &redriver->config_work);

	return NOTIFY_DONE;
}

static int ps5169_extcon_register(struct ps5169_redriver *redriver)
{
	struct device_node *node = redriver->dev->of_node;
	struct extcon_dev *edev;
	int ret;

	if (!node || !of_find_property(node, "extcon", NULL)) {
		dev_warn(redriver->dev,
			 "no extcon phandle, redriver stays in default mode\n");
		return 0;
	}

	edev = extcon_get_edev_by_phandle(redriver->dev, 0);
	if (IS_ERR(edev)) {
		if (PTR_ERR(edev) == -ENODEV)
			return 0;
		dev_err(redriver->dev, "failed to get extcon phandle\n");
		return PTR_ERR(edev);
	}

	redriver->extcon_usb = edev;

	redriver->vbus_nb.notifier_call = ps5169_vbus_notifier;
	redriver->vbus_nb.priority = NOTIFIER_PRIORITY;
	ret = extcon_register_notifier(edev, EXTCON_USB,
				       &redriver->vbus_nb);
	if (ret < 0) {
		dev_err(redriver->dev, "failed to register vbus notifier\n");
		return ret;
	}

	redriver->id_nb.notifier_call = ps5169_id_notifier;
	redriver->id_nb.priority = NOTIFIER_PRIORITY;
	ret = extcon_register_notifier(edev, EXTCON_USB_HOST,
				       &redriver->id_nb);
	if (ret < 0) {
		dev_err(redriver->dev, "failed to register id notifier\n");
		goto err_vbus;
	}

	edev = NULL;
	if (of_count_phandle_with_args(node, "extcon", NULL) > 1) {
		edev = extcon_get_edev_by_phandle(redriver->dev, 1);
		if (IS_ERR(edev) && PTR_ERR(edev) != -ENODEV) {
			ret = PTR_ERR(edev);
			goto err_id;
		}
	}

	if (!IS_ERR_OR_NULL(edev)) {
		redriver->extcon_dp = edev;
		redriver->dp_nb.notifier_call = ps5169_dp_notifier;
		redriver->dp_nb.priority = NOTIFIER_PRIORITY;
		ret = extcon_register_blocking_notifier(edev, EXTCON_DISP_DP,
						&redriver->dp_nb);
		if (ret < 0) {
			dev_err(redriver->dev,
				"failed to register dp notifier\n");
			goto err_id;
		}
	}

	/* 同步一次初始状态 */
	if (extcon_get_state(redriver->extcon_usb, EXTCON_USB))
		ps5169_vbus_notifier(&redriver->vbus_nb, true,
				     redriver->extcon_usb);
	else if (extcon_get_state(redriver->extcon_usb, EXTCON_USB_HOST))
		ps5169_id_notifier(&redriver->id_nb, true,
				   redriver->extcon_usb);

	return 0;

err_id:
	if (redriver->extcon_usb)
		extcon_unregister_notifier(redriver->extcon_usb,
				EXTCON_USB_HOST, &redriver->id_nb);
err_vbus:
	if (redriver->extcon_usb)
		extcon_unregister_notifier(redriver->extcon_usb,
				EXTCON_USB, &redriver->vbus_nb);
	return ret;
}

static int ps5169_panic_notifier(struct notifier_block *this,
				 unsigned long event, void *ptr)
{
	struct ps5169_redriver *redriver = container_of(this,
			struct ps5169_redriver, panic_nb);

	pr_err("%s: op mode: %d, vbus: %d, host: %d\n", __func__,
	       redriver->op_mode, redriver->vbus_active,
	       redriver->host_active);

	return NOTIFY_OK;
}

/* ------------------------------------------------------------------ */
/* debugfs                                                            */
/* ------------------------------------------------------------------ */

static int redriver_dump_reg_get(struct ps5169_redriver *redriver, u8 reg,
				 u8 *val)
{
	return redriver_i2c_reg_get(redriver, reg, val);
}

static int dump_register_show(struct seq_file *s, void *unused)
{
	struct ps5169_redriver *redriver = s->private;
	static const u8 dump_reg_list[] = {
		0x40, 0xa0, 0xa1,
		0x52, 0x5e, 0x5c,
		0x20, 0x21, 0x22, 0x23, 0x24, 0x25,
		0x50, 0x5d, 0x54, 0x51, 0x77, 0x78,
		0xac, 0xad, 0xae, 0xaf,
	};
	u8 val;
	int i, ret;

	for (i = 0; i < ARRAY_SIZE(dump_reg_list); i++) {
		ret = redriver_dump_reg_get(redriver, dump_reg_list[i], &val);
		if (ret < 0)
			seq_printf(s, "0x%02x = ERR\n", dump_reg_list[i]);
		else
			seq_printf(s, "0x%02x = 0x%02x\n",
				   dump_reg_list[i], val);
	}

	return 0;
}

static int dump_register_open(struct inode *inode, struct file *file)
{
	return single_open(file, dump_register_show, inode->i_private);
}

static const struct file_operations dump_register_ops = {
	.open		= dump_register_open,
	.read		= seq_read,
	.llseek		= seq_lseek,
	.release	= single_release,
};

static int update_register_open(struct inode *inode, struct file *file)
{
	return single_open(file, NULL, inode->i_private);
}

static ssize_t update_register_write(struct file *file,
				     const char __user *ubuf,
				     size_t count, loff_t *ppos)
{
	struct seq_file *s = file->private_data;
	struct ps5169_redriver *redriver = s->private;
	char buf[100];
	char *this_buf;
	unsigned int addr, val;

	if (count >= sizeof(buf))
		return -EINVAL;

	memset(buf, 0, sizeof(buf));
	if (copy_from_user(buf, ubuf, count))
		return -EFAULT;

	this_buf = buf;
	while (this_buf) {
		if (sscanf(this_buf, "0x%02x=0x%02x", &addr, &val) == 2) {
			if (addr > REDRIVER_REG_MAX || val > 0xff)
				return -EINVAL;
			if (redriver_i2c_reg_set(redriver, addr, val) < 0)
				return -EIO;
		} else {
			dev_err(redriver->dev,
				"cannot get register address or value\n");
		}
		strsep(&this_buf, " ");
	}

	return count;
}

static const struct file_operations update_register_ops = {
	.open		= update_register_open,
	.write		= update_register_write,
	.llseek		= seq_lseek,
	.release	= single_release,
};

static void ps5169_debugfs_entries(struct ps5169_redriver *redriver)
{
	struct dentry *ent;

	redriver->debug_root = debugfs_create_dir("ps5169_redriver", NULL);
	if (!redriver->debug_root) {
		dev_warn(redriver->dev, "Couldn't create debug dir\n");
		return;
	}

	ent = debugfs_create_file("dump_register", 0600,
				  redriver->debug_root, redriver,
				  &dump_register_ops);
	if (IS_ERR_OR_NULL(ent))
		dev_warn(redriver->dev, "Couldn't create dump_register\n");

	ent = debugfs_create_file("update_register", 0600,
				  redriver->debug_root, redriver,
				  &update_register_ops);
	if (IS_ERR_OR_NULL(ent))
		dev_warn(redriver->dev, "Couldn't create update_register\n");
}

/* ------------------------------------------------------------------ */
/* probe / remove                                                     */
/* ------------------------------------------------------------------ */

static int redriver_get_chip_id(struct ps5169_redriver *redriver)
{
	if (redriver_i2c_reg_get(redriver, 0xad, &redriver->id.chip_id_1) < 0)
		return -EINVAL;
	if (redriver_i2c_reg_get(redriver, 0xac, &redriver->id.chip_id_2) < 0)
		return -EINVAL;
	if (redriver_i2c_reg_get(redriver, 0xae, &redriver->id.revision_1) < 0)
		return -EINVAL;
	if (redriver_i2c_reg_get(redriver, 0xaf, &redriver->id.revision_2) < 0)
		return -EINVAL;

	return 0;
}

static int ps5169_probe(struct i2c_client *client,
			const struct i2c_device_id *dev_id)
{
	struct ps5169_redriver *redriver;
	union power_supply_propval pval = {0};
	int ret;

	dev_info(&client->dev, "ps5169_probe enter\n");

	redriver = devm_kzalloc(&client->dev, sizeof(*redriver), GFP_KERNEL);
	if (!redriver)
		return -ENOMEM;

	redriver->dev = &client->dev;
	redriver->client = client;
	i2c_set_clientdata(client, redriver);

	INIT_WORK(&redriver->config_work, ps5169_config_work);

	redriver->redriver_wq = alloc_ordered_workqueue("redriver_wq",
							WQ_HIGHPRI);
	if (!redriver->redriver_wq) {
		dev_err(&client->dev, "Unable to create redriver_wq\n");
		return -ENOMEM;
	}

	redriver->regmap = devm_regmap_init_i2c(client, &redriver_regmap);
	if (IS_ERR(redriver->regmap)) {
		ret = PTR_ERR(redriver->regmap);
		dev_err(&client->dev,
			"Failed to allocate register map: %d\n", ret);
		goto destroy_wq;
	}

	ret = redriver_get_chip_id(redriver);
	if (ret < 0) {
		dev_err(&client->dev,
			"Failed to get chip id: %d, continue\n", ret);
	} else {
		dev_info(&client->dev,
			 "get chip id: id_1 = 0x%02x, id_2 = 0x%02x, revision_1 = 0x%02x, revision_2 = 0x%02x\n",
			 redriver->id.chip_id_1, redriver->id.chip_id_2,
			 redriver->id.revision_1, redriver->id.revision_2);
		redriver_exist = true;
	}

	/* 上电初始态：auto power down */
	redriver->op_mode = OP_MODE_NONE;
	redriver->typec_orientation = ORIENTATION_CC1;

	ret = redriver_set_default_mode(redriver);
	if (ret < 0)
		dev_err(&client->dev, "Failed to set default mode: %d\n", ret);

	redriver->host_active = false;
	redriver->vbus_active = false;

	redriver->usb_psy = power_supply_get_by_name("usb");
	if (!redriver->usb_psy) {
		dev_warn(&client->dev, "Could not get usb power_supply\n");
	} else {
		power_supply_get_property(redriver->usb_psy,
					  POWER_SUPPLY_PROP_PRESENT, &pval);
		if (!pval.intval)
			ps5169_redriver_gen_dev_set(redriver, false);
	}

	ret = ps5169_extcon_register(redriver);
	if (ret)
		goto put_psy;

	redriver->panic_nb.notifier_call = ps5169_panic_notifier;
	atomic_notifier_chain_register(&panic_notifier_list,
				       &redriver->panic_nb);

	ps5169_debugfs_entries(redriver);

	dev_info(&client->dev, "ps5169_probe success\n");
	return 0;

put_psy:
	if (redriver->usb_psy)
		power_supply_put(redriver->usb_psy);
destroy_wq:
	destroy_workqueue(redriver->redriver_wq);
	return ret;
}

static int ps5169_remove(struct i2c_client *client)
{
	struct ps5169_redriver *redriver = i2c_get_clientdata(client);

	cancel_work_sync(&redriver->config_work);
	atomic_notifier_chain_unregister(&panic_notifier_list,
					 &redriver->panic_nb);

	if (redriver->extcon_dp)
		extcon_unregister_notifier(redriver->extcon_dp,
				EXTCON_DISP_DP, &redriver->dp_nb);
	if (redriver->extcon_usb) {
		extcon_unregister_notifier(redriver->extcon_usb,
				EXTCON_USB_HOST, &redriver->id_nb);
		extcon_unregister_notifier(redriver->extcon_usb,
				EXTCON_USB, &redriver->vbus_nb);
	}

	debugfs_remove_recursive(redriver->debug_root);

	if (redriver->usb_psy)
		power_supply_put(redriver->usb_psy);

	destroy_workqueue(redriver->redriver_wq);

	return 0;
}

static int __maybe_unused ps5169_suspend(struct device *dev)
{
	struct i2c_client *client = to_i2c_client(dev);
	struct ps5169_redriver *redriver = i2c_get_clientdata(client);

	/* 没插线时彻底关掉芯片 */
	if ((!redriver->vbus_active && !redriver->host_active &&
	     redriver->op_mode != OP_MODE_DP) ||
	    (redriver->host_active && redriver->op_mode == OP_MODE_USB_AND_DP))
		ps5169_redriver_gen_dev_set(redriver, false);

	flush_workqueue(redriver->redriver_wq);

	return 0;
}

static int __maybe_unused ps5169_resume(struct device *dev)
{
	struct i2c_client *client = to_i2c_client(dev);
	struct ps5169_redriver *redriver = i2c_get_clientdata(client);

	if (redriver->host_active && redriver->op_mode == OP_MODE_USB_AND_DP)
		ps5169_redriver_gen_dev_set(redriver, true);

	flush_workqueue(redriver->redriver_wq);

	return 0;
}

static SIMPLE_DEV_PM_OPS(ps5169_pm, ps5169_suspend, ps5169_resume);

static void ps5169_shutdown(struct i2c_client *client)
{
	struct ps5169_redriver *redriver = i2c_get_clientdata(client);

	/* 关机前回到 USB 模式并关断 */
	redriver->op_mode = OP_MODE_USB;
	ps5169_redriver_gen_dev_set(redriver, false);
}

static const struct of_device_id ps5169_match_table[] = {
	{ .compatible = "hq_redriver,ps5169" },
	{ }
};

static const struct i2c_device_id ps5169_i2c_id[] = {
	{ "ssusb redriver", 0 },
	{ }
};
MODULE_DEVICE_TABLE(i2c, ps5169_i2c_id);

static struct i2c_driver ps5169_driver = {
	.driver = {
		.name		= "ssusb redriver",
		.of_match_table	= ps5169_match_table,
		.pm		= &ps5169_pm,
	},
	.probe		= ps5169_probe,
	.remove		= ps5169_remove,
	.shutdown	= ps5169_shutdown,
	.id_table	= ps5169_i2c_id,
};

module_i2c_driver(ps5169_driver);

MODULE_DESCRIPTION("USB Super Speed Linear Re-Driver (PS5169)");
MODULE_LICENSE("GPL v2");
