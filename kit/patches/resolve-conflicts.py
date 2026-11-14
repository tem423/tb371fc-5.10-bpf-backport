#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resolve-conflicts.py — 合入 5.10-bpf 聚合补丁在 4.19.325 目标树上残留的 .rej

用法:
    python3 resolve-conflicts.py /path/to/kernel-tree [--dry-run]

背景
----
apartusitu-backport-5.10-bpf.diff 应用到 smith-dog/kernel-tb371fc (4.19.325)
后产生 20 个 .rej。逐个核对目标树实际状态后的结论:

  * 12 个 .rej 已被补丁的其它成功 hunk 覆盖, 或与目标树语义冲突, 不应合入:
      - sysctl proc_handler 签名组 (7 个): 目标树 typedef 与实现均已是 void *buffer
        arch/arm64/kernel/armv8_deprecated.c / drivers/char/random.c
        include/linux/timer.h / kernel/time/timer.c / kernel/sched/fair.c
        net/ipv4/sysctl_net_ipv4.c
      - kernel/exit.c: usermode_driver.h + exit_umh() 已存在
      - include/linux/cgroup-defs.h / kernfs.h: 新增枚举值已存在
      - include/asm-generic/vmlinux.lds.h: LSM_TABLE()/BTF/.BTF_ids 已存在,
        INIT_DATA 中 SECURITY_INITCALL 已被移除
      - security/selinux/ss/services.c: selinux_initialized() 已在 10+ 处使用
      - include/linux/compiler-clang.h: __assume_aligned 仍被 slab.h 使用,
        删除会导致大量编译错误 —— 必须跳过

  * 8 个是真缺失, 且直接导致编译失败 (本脚本处理):
      include/net/tcp.h                        skb_mstamp_ns / 3 参数声明
      include/net/sock.h                       sk_bpf_storage 字段
      security/selinux/include/classmap.h      anon_inode security class
      kernel/sys.c                             bpfloader fake uname (帖子要求)
      net/ipv4/af_inet.c                       BPF_CGROUP_INET_SOCK_RELEASE
      include/linux/virtio_net.h               flow dissect 新增 net 参数
      drivers/net/wireless/virt_wifi.c         ktime_get_boottime_ns
      kernel/trace/bpf_trace.c                 bpf_trace_module / 前向声明

  * 另补 include/linux/build_bug.h 的 static_assert() (5.10 引入, 4.19 无),
    skmsg.h 与 net/core/filter.c 已在使用, 否则 "expected parameter declarator"。

  * 另补 kernel/bpf/core.c 的 bpf_jit_alloc_exec() / bpf_jit_free_exec():
    5.10 filter.h 声明并由 trampoline.c / bpf_struct_ops.c / dispatcher.c 调用,
    但补丁源树基于已含 5.4-bpf 的基线 (这两个函数是补丁里的上下文行, 源树
    已存在), 纯净 4.19.325 没有实现 -> 链接期 undefined reference。按 5.10
    upstream 补 __weak 版 (module_alloc/module_memfree, 与本文件
    bpf_jit_binary_alloc 同机制), arm64 无 BPF_JIT_REGION 覆盖时也能链接。

所有替换均为精确字符串匹配并带唯一性断言, 可重复执行 (幂等)。
"""

import sys
from pathlib import Path

DRY = "--dry-run" in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = Path(ARGS[0]).resolve() if ARGS else Path.cwd()

changes = []   # (file, description)
skips = []


# 5.10 主线删除了 include/linux/selinux.h (SELinux 不再对外导出
# selinux_is_enabled), 补丁忠实照搬了这一删除; 但 vendor 的
# drivers/ksu_sym.c (KernelSU 符号垫片) 仍 #include <linux/selinux.h>。
# 恢复原 4.19 头文件即可 (内容仅几个前向声明, 对 5.10 树无害)。
SELINUX_H = """/*
 * SELinux services exported to the rest of the kernel.
 *
 * Author: James Morris <jmorris@redhat.com>
 *
 * Copyright (C) 2005 Red Hat, Inc., James Morris <jmorris@redhat.com>
 * Copyright (C) 2006 Trusted Computer Solutions, Inc. <dgoeddel@trustedcs.com>
 * Copyright (C) 2006 IBM Corporation, Timothy R. Chavez <tinytim@us.ibm.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2,
 * as published by the Free Software Foundation.
 */
#ifndef _LINUX_SELINUX_H
#define _LINUX_SELINUX_H

struct selinux_audit_rule;
struct audit_context;
struct kern_ipc_perm;

#ifdef CONFIG_SECURITY_SELINUX

/**
 * selinux_is_enabled - is SELinux enabled?
 */
bool selinux_is_enabled(void);
#else

static inline bool selinux_is_enabled(void)
{
	return false;
}
#endif	/* CONFIG_SECURITY_SELINUX */

#endif /* _LINUX_SELINUX_H */
"""


def restore(rel, content, desc):
    """恢复被补丁删除、但 vendor 代码仍依赖的文件。"""
    p = ROOT / rel
    if p.exists():
        skips.append((rel, desc, "已存在"))
        return
    if not DRY:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", errors="surrogateescape")
    changes.append((rel, desc))


def edit(rel, old, new, desc, count=1, optional=False):
    """把 rel 文件中的 old 精确替换为 new。若 new 已存在则视为已完成。"""
    p = ROOT / rel
    if not p.exists():
        if optional:
            skips.append((rel, desc, "文件不存在"))
            return
        raise SystemExit(f"[FATAL] 文件不存在: {p}")
    s = p.read_text(encoding="utf-8", errors="surrogateescape")
    # 幂等判定: 只要目标态 new 已出现就跳过。
    # 不能附加 "and old not in s" —— 插入型替换里 new 以 old 为前缀,
    # 合入后 old 依然在 s 中, 那样会误判为未合入并重复插入。
    if new in s:
        skips.append((rel, desc, "已合入"))
        return
    n = s.count(old)
    if n != count:
        if optional and n == 0:
            skips.append((rel, desc, f"锚点未命中({n})"))
            return
        raise SystemExit(f"[FATAL] {rel}: 锚点出现 {n} 次, 期望 {count} 次 -> {desc}")
    s2 = s.replace(old, new)
    if not DRY:
        p.write_text(s2, encoding="utf-8", errors="surrogateescape")
    changes.append((rel, desc))


# ---------------------------------------------------------------- 1. tcp.h
edit("include/net/tcp.h",
     "void tcp_init_transfer(struct sock *sk, int bpf_op);",
     "void tcp_init_transfer(struct sock *sk, int bpf_op, struct sk_buff *skb);",
     "tcp_init_transfer 声明对齐 3 参数 (tcp_input.c 定义与调用已是 3 参数)")

edit("include/net/tcp.h",
     "\treturn div_u64(skb->skb_mstamp, USEC_PER_SEC / TCP_TS_HZ);",
     "\treturn div_u64(skb->skb_mstamp_ns, NSEC_PER_SEC / TCP_TS_HZ);",
     "tcp_skb_timestamp: skb_mstamp -> skb_mstamp_ns (ns 单位)")

edit("include/net/tcp.h",
     "\treturn skb->skb_mstamp;",
     "\treturn div_u64(skb->skb_mstamp_ns, NSEC_PER_USEC);",
     "tcp_skb_timestamp_us: 返回 ns/1000")

edit("include/net/tcp.h",
     """	int (*send_synack)(const struct sock *sk, struct dst_entry *dst,
			   struct flowi *fl, struct request_sock *req,
			   struct tcp_fastopen_cookie *foc,
			   enum tcp_synack_type synack_type);""",
     """	int (*send_synack)(const struct sock *sk, struct dst_entry *dst,
			   struct flowi *fl, struct request_sock *req,
			   struct tcp_fastopen_cookie *foc,
			   enum tcp_synack_type synack_type,
			   struct sk_buff *syn_skb);""",
     "send_synack 函数指针加 syn_skb (v4/v6 实现与调用已带该参数)")

# --------------------------------------------------------------- 2. sock.h
edit("include/net/sock.h",
     """	void                    (*sk_destruct)(struct sock *sk);
	struct sock_reuseport __rcu	*sk_reuseport_cb;
	struct rcu_head		sk_rcu;""",
     """	void                    (*sk_destruct)(struct sock *sk);
	struct sock_reuseport __rcu	*sk_reuseport_cb;
#ifdef CONFIG_BPF_SYSCALL
	struct bpf_local_storage __rcu	*sk_bpf_storage;
#endif
	struct rcu_head		sk_rcu;""",
     "struct sock 增加 sk_bpf_storage (net/core/bpf_sk_storage.c 依赖)")

# ----------------------------------------------------------- 3. classmap.h
edit("security/selinux/include/classmap.h",
     """	{ "perf_event",
	  {"open", "cpu", "kernel", "tracepoint", "read", "write"} },
	{ NULL }""",
     """	{ "perf_event",
	  {"open", "cpu", "kernel", "tracepoint", "read", "write"} },
	{ "anon_inode",
	  { COMMON_FILE_PERMS, NULL } },
	{ NULL }""",
     "新增 anon_inode security class (hooks.c 引用 SECCLASS_ANON_INODE)")

# ---------------------------------------------------------------- 4. sys.c
edit("kernel/sys.c",
     """SYSCALL_DEFINE1(newuname, struct new_utsname __user *, name)
{
	struct new_utsname tmp;

	down_read(&uts_sem);
	memcpy(&tmp, utsname(), sizeof(tmp));
	up_read(&uts_sem);""",
     """SYSCALL_DEFINE1(newuname, struct new_utsname __user *, name)
{
	struct new_utsname tmp;

	down_read(&uts_sem);
	memcpy(&tmp, utsname(), sizeof(tmp));
	if (!strncmp(current->comm, "bpfloader", 9) ||
	    !strncmp(current->comm, "netbpfload", 10) ||
	    !strncmp(current->comm, "netd", 4) ||
	    !strncmp(current->comm, "uprobestats", 11)) {
		strcpy(tmp.release, "5.10.240");
		pr_debug("fake uname: %s release=%s\\n",
			 current->comm, tmp.release);
	}
	up_read(&uts_sem);""",
     "bpfloader/netd 等进程伪装 uname release 为 5.10.240 (帖子要求)")

# ------------------------------------------------------------ 5. af_inet.c
edit("net/ipv4/af_inet.c",
     """int inet_release(struct socket *sock)
{
	struct sock *sk = sock->sk;

	if (sk) {
		long timeout;
""",
     """int inet_release(struct socket *sock)
{
	struct sock *sk = sock->sk;

	if (sk) {
		long timeout;

		if (!sk->sk_kern_sock)
			BPF_CGROUP_RUN_PROG_INET_SOCK_RELEASE(sk);
""",
     "inet_release 触发 BPF_CGROUP_INET_SOCK_RELEASE")

# ------------------------------------------------------- 6. virtio_net.h
edit("include/linux/virtio_net.h",
     "if (!skb_flow_dissect_flow_keys_basic(skb, &keys,",
     "if (!skb_flow_dissect_flow_keys_basic(NULL, skb, &keys,",
     "flow dissect 补齐新增的 net 首参 (skbuff.h 已是 8 参数)")

# -------------------------------------------------------- 7. virt_wifi.c
edit("drivers/net/wireless/virt_wifi.c",
     "ktime_get_boot_ns()",
     "ktime_get_boottime_ns()",
     "4.19 只有 ktime_get_boottime_ns()", optional=True)

# ------------------------------------------------------- 8. bpf_trace.c
edit("kernel/trace/bpf_trace.c",
     """#include <linux/error-injection.h>

#include "trace_probe.h\"""",
     """#include <linux/error-injection.h>
#include <linux/btf_ids.h>
#include <linux/bpf_lsm.h>

#include <net/bpf_sk_storage.h>

#include <uapi/linux/bpf.h>
#include <uapi/linux/btf.h>

#include <asm/tlb.h>

#include "trace_probe.h\"""",
     "补齐 btf_ids/bpf_lsm/bpf_sk_storage/tlb 头文件")

edit("kernel/trace/bpf_trace.c",
     """u64 bpf_get_stackid(u64 r1, u64 r2, u64 r3, u64 r4, u64 r5);
u64 bpf_get_stack(u64 r1, u64 r2, u64 r3, u64 r4, u64 r5);
""",
     """u64 bpf_get_stackid(u64 r1, u64 r2, u64 r3, u64 r4, u64 r5);
u64 bpf_get_stack(u64 r1, u64 r2, u64 r3, u64 r4, u64 r5);

#define bpf_event_rcu_dereference(p)					\\
	rcu_dereference_protected(p, lockdep_is_held(&bpf_event_mutex))

#ifdef CONFIG_MODULES
struct bpf_trace_module {
	struct module *module;
	struct list_head list;
};

static LIST_HEAD(bpf_trace_modules);
static DEFINE_MUTEX(bpf_module_mutex);

static struct bpf_raw_event_map *bpf_get_raw_tracepoint_module(const char *name)
{
	struct bpf_raw_event_map *btp, *ret = NULL;
	struct bpf_trace_module *btm;
	unsigned int i;

	mutex_lock(&bpf_module_mutex);
	list_for_each_entry(btm, &bpf_trace_modules, list) {
		for (i = 0; i < btm->module->num_bpf_raw_events; ++i) {
			btp = &btm->module->bpf_raw_events[i];
			if (!strcmp(btp->tp->name, name)) {
				if (try_module_get(btm->module))
					ret = btp;
				goto out;
			}
		}
	}
out:
	mutex_unlock(&bpf_module_mutex);
	return ret;
}
#else
static struct bpf_raw_event_map *bpf_get_raw_tracepoint_module(const char *name)
{
	return NULL;
}
#endif /* CONFIG_MODULES */

static int bpf_btf_printf_prepare(struct btf_ptr *ptr, u32 btf_ptr_size,
				  u64 flags, const struct btf **btf,
				  s32 *btf_id);
""",
     "补齐 bpf_event_rcu_dereference / bpf_trace_module / 前向声明")

# ------------------------------------------------- 9. bpf_sk_storage.h
# 补丁把该头文件当"新建文件"加入, 但 4.19 目标树已有旧版同名头文件,
# 于是两个 tracing 变体的 extern 声明没有落地 (bpf_sk_storage.c 里已定义)。
edit("include/net/bpf_sk_storage.h",
     """extern const struct bpf_func_proto bpf_sk_storage_get_proto;
extern const struct bpf_func_proto bpf_sk_storage_delete_proto;""",
     """extern const struct bpf_func_proto bpf_sk_storage_get_proto;
extern const struct bpf_func_proto bpf_sk_storage_delete_proto;
extern const struct bpf_func_proto bpf_sk_storage_get_tracing_proto;
extern const struct bpf_func_proto bpf_sk_storage_delete_tracing_proto;""",
     "补齐 sk_storage tracing 变体声明 (bpf_trace.c 依赖)")

# --------------------------------------------------------- 10. cgroup.h
# 补丁把 cgroup_id() 提到公共区 (返回 cgrp->kn->id, 此时 kernfs.h 里
# kn->id 已被补丁改成 u64), 但 4.19 原树在 #ifdef CONFIG_SOCK_CGROUP_DATA
# 分支里还有一份返回 kn->id.ino 的旧定义 -> 重复定义 + 类型错误。
edit("include/linux/cgroup.h",
     """static inline u64 cgroup_id(struct cgroup *cgrp)
{
	return cgrp->kn->id.ino;
}
""",
     """/* backport: cgroup_id() 已移至本文件公共区 (见上方) */
""",
     "删除 4.19 旧版 cgroup_id (与补丁新增的重复且 kn->id 已变 u64)",
     optional=True)

# ----------------------------------------------------- 11. mkcompile_h
# 部分环境 clang -v 会额外打印 "Found CUDA installation: ... version ...",
# 被 mkcompile_h 的 grep ' version ' 一并捕获, 使 LINUX_COMPILER 宏跨行。
edit("scripts/mkcompile_h",
     "  CC_VERSION=$($CC -v 2>&1 | grep ' version ' | sed 's/[[:space:]]*$//')",
     "  CC_VERSION=$($CC -v 2>&1 | grep ' version ' | head -1 | sed 's/[[:space:]]*$//')",
     "只取编译器版本首行, 避免 CUDA 探测行污染 compile.h",
     optional=True)

# ------------------------------------------------------ 12. selinux.h
restore("include/linux/selinux.h", SELINUX_H,
        "恢复 5.10 补丁删除的 selinux.h (vendor drivers/ksu_sym.c 依赖)")

# ------------------------------------------------------ 13. build_bug.h
edit("include/linux/build_bug.h",
     """#ifdef __GENKSYMS__
/* genksyms gets confused by _Static_assert */
#define _Static_assert(expr, ...)
#endif

#endif	/* _LINUX_BUILD_BUG_H */""",
     """#ifdef __GENKSYMS__
/* genksyms gets confused by _Static_assert */
#define _Static_assert(expr, ...)
#endif

/* 5.10 backport: skmsg.h / net/core/filter.c 使用 static_assert() */
#ifndef static_assert
#define static_assert(expr, ...) __static_assert(expr, ##__VA_ARGS__, #expr)
#define __static_assert(expr, msg, ...) _Static_assert(expr, msg)
#endif

#endif	/* _LINUX_BUILD_BUG_H */""",
     "补齐 5.10 的 static_assert() 宏 (4.19 build_bug.h 没有)")

# ------------------------------------------------------------ 14. core.c
# 5.10 trampoline/struct_ops/dispatcher 通过 filter.h 调用这两个符号,
# 但补丁集假设基线已含 5.4-bpf 的实现, 纯净 4.19 没有 -> 链接失败。
# 按 5.10 upstream kernel/bpf/core.c 的 __weak 版补齐 (module_alloc)。
edit("kernel/bpf/core.c",
     """static void bpf_jit_uncharge_modmem(u32 pages)
{
	atomic_long_sub(pages, &bpf_jit_current);
}

#if IS_ENABLED(CONFIG_BPF_JIT) && IS_ENABLED(CONFIG_CFI_CLANG)""",
     """static void bpf_jit_uncharge_modmem(u32 pages)
{
	atomic_long_sub(pages, &bpf_jit_current);
}

/* 5.10 backport: trampoline/struct_ops/dispatcher 需要, 补丁基线的
 * 5.4-bpf 已实现但 4.19 没有。__weak 便于架构后续覆盖。 */
void *__weak bpf_jit_alloc_exec(unsigned long size)
{
	return module_alloc(size);
}

void __weak bpf_jit_free_exec(void *addr)
{
	module_memfree(addr);
}

#if IS_ENABLED(CONFIG_BPF_JIT) && IS_ENABLED(CONFIG_CFI_CLANG)""",
     "补齐 bpf_jit_alloc_exec/free_exec __weak 实现 (链接期 undefined reference)")

# ------------------------------------------------------------------ report
print(f"目标树 : {ROOT}")
print(f"模式   : {'DRY-RUN (不写盘)' if DRY else '写入'}")
print()
print(f"=== 合入 {len(changes)} 处 ===")
for f, d in changes:
    print(f"  [+] {f}\n      {d}")
print()
print(f"=== 跳过 {len(skips)} 处 ===")
for f, d, why in skips:
    print(f"  [=] {f}: {why} — {d}")
