#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查「.config 里开了、但源码树里没有对应实现」的项。

判定链路：
    .config 的 CONFIG_X=y/m
      -> 在全部 Kconfig* 中找到 `config X` / `menuconfig X` 的定义文件
      -> 取定义文件所在目录 D 的 Makefile，找 obj-$(CONFIG_X) += target
         （找不到则向上最多 3 层找 obj-$(CONFIG_X) += <子目录>/）
      -> target 为 foo.o 时检查 foo.c / foo.S / foo-y 组合源文件
         target 为 dir/ 时检查目录存在且非空

输出四类：
  MISSING_SRC  : Makefile 明确要编 target，但对应 .c/.S/目录不存在  ← 真正的「config 有、源码没有」
  NOT_WIRED    : Kconfig 有定义，但整条 Makefile 链都没引用该 CONFIG（开了不编译任何东西）
  NO_KCONFIG   : .config 里有，但全树 Kconfig 找不到定义（残留项）
  OK           : 能对上源码

用法:
    python3 check-config-src.py <KERNEL_ROOT> [--report out.json] [--md out.md]
    python3 check-config-src.py <KERNEL_ROOT> --config <外部基准config> \\
            [--report out.json] [--md out.md]

    --config 用于「用原厂 config 核对目标树」：
      原厂开了 y/m，但目标树 Kconfig 无此符号 -> NO_KCONFIG（真缺驱动）
      原厂开了 y/m，Kconfig 有但源码缺 -> MISSING_SRC
      目标树 config 开了、原厂没开 -> 由 --extra 单独列出
"""
import argparse, fnmatch, json, os, re, sys
from pathlib import Path

SKIP_DIRS = {".git", ".tmp_versions", "Documentation", "tools/testing"}


def read_text(p):
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def parse_config(root, cfg_path=None):
    """cfg_path 为空时读 <root>/.config；否则读外部基准 config（如原厂 config）"""
    cfg = {}
    p = Path(cfg_path) if cfg_path else (root / ".config")
    if not p.exists():
        sys.exit(f"[FATAL] 找不到 {p}")
    for line in read_text(p).splitlines():
        m = re.match(r"^(CONFIG_[A-Za-z0-9_]+)=(y|m)\s*$", line.strip())
        if m:
            cfg[m.group(1)] = m.group(2)
    return cfg


def index_kconfig(root):
    """symbol -> 定义所在 Kconfig 文件"""
    idx = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.startswith("Kconfig"):
                continue
            p = Path(dirpath) / fn
            txt = read_text(p)
            for m in re.finditer(r"^\s*(?:menu)?config\s+([A-Za-z0-9_]+)\s*$", txt, re.M):
                idx.setdefault(m.group(1), p)
    return idx


OBJ_RE = re.compile(r"\bobj-\$\((CONFIG_[A-Za-z0-9_]+)\)\s*\+?=\s*(.+?)\s*$")


def makefile_obj_rules(mk):
    """config -> [target, ...]"""
    out = {}
    for raw in read_text(mk).splitlines():
        line = raw.split("#", 1)[0]
        m = OBJ_RE.search(line)
        if not m:
            continue
        for t in m.group(2).split():
            out.setdefault(m.group(1), []).append(t)
    return out


def has_any_ref(mk, sym):
    """Makefile 里是否以任何形式引用了该 CONFIG（含 ccflags/ifeq 等开关用法）"""
    return sym in read_text(mk)


def resolve_o(d, target):
    """target 形如 foo.o / foo/ ；返回 (ok, detail)"""
    if target.endswith("/"):
        sub = d / target
        if not sub.is_dir():
            return False, f"目录不存在: {target}"
        if not any(sub.iterdir()):
            return False, f"目录为空: {target}"
        return True, "dir"
    if not target.endswith(".o"):
        return True, "非 .o 目标，跳过"
    base = target[:-2]
    for ext in (".c", ".S", ".s"):
        if (d / (base + ext)).exists():
            return True, base + ext

    mk = d / "Makefile"
    mk_txt = read_text(mk) if mk.exists() else ""

    # 组合目标：foo-y := a.o b.o   /  foo-objs := ...
    if mk_txt:
        for var in (f"{base}-y", f"{base}-objs"):
            m = re.search(rf"^\s*{re.escape(var)}\s*[:+]?=\s*(.+)$", mk_txt, re.M)
            if m:
                parts = [x for x in m.group(1).split() if x.endswith(".o")]
                missing = []
                for sub in parts:
                    sb = sub[:-2]
                    if not any((d / (sb + e)).exists() for e in (".c", ".S", ".s")):
                        # 子项也可能由 pattern rule 生成，再查一次
                        if not pattern_rule_source(d, sb, mk_txt):
                            missing.append(sub)
                if missing:
                    return False, f"{target} 由 {var} 组合，缺: {', '.join(missing)}"
                return True, f"{var} ({len(parts)} 个源文件)"
        m = re.search(rf"^\s*{re.escape(base)}-\$\(CONFIG_[A-Za-z0-9_]+\)\s*[:+]?=\s*(.+)$", mk_txt, re.M)
        if m:
            return True, "条件组合目标"

        # 自定义 pattern rule：$(obj)/aes-glue-%.o: $(src)/aes-glue.c
        pr = pattern_rule_source(d, base, mk_txt)
        if pr:
            return True, pr
    return False, f"{target} 无对应源文件"


def pattern_rule_source(d, base, mk_txt):
    """匹配 $(obj)/<pattern>%.o: $(src)/<file>.c 这类规则"""
    for pat, dep in re.findall(r"\$\(obj\)/([A-Za-z0-9_\-%]+)\.o\s*:\s*(\S+)", mk_txt):
        # Makefile 的 % 通配符 -> fnmatch 的 *
        if fnmatch.fnmatchcase(base, pat.replace("%", "*")):
            src = dep.split("/")[-1]
            if (d / src).exists():
                return f"pattern {pat}.o <- {src}"
            # 规则存在但依赖文件缺失
            return None
    return None


def find_targets(sym, kfile, root):
    """在定义目录及向上 3 层找该 CONFIG 的 obj 规则；返回 (dir, [targets], note)"""
    d = kfile.parent
    rules = makefile_obj_rules(d / "Makefile") if (d / "Makefile").exists() else {}
    if sym in rules:
        return d, rules[sym], "local"

    # 上层 Makefile 以 obj-$(CONFIG_X) += <subdir>/ 接线
    cur = d
    for _ in range(3):
        parent = cur.parent
        if parent == cur or parent == root.parent:
            break
        pmk = parent / "Makefile"
        if pmk.exists():
            prules = makefile_obj_rules(pmk)
            rel = cur.name + "/"
            if sym in prules and any(t.rstrip("/") == cur.name for t in prules[sym]):
                return parent, prules[sym], f"parent({parent.relative_to(root)})"
        cur = parent
    return d, [], "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--config", default=None,
                    help="外部基准 config（如原厂 4.19.157 config）；缺省用 <root>/.config")
    ap.add_argument("--report", default=None)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()

    root = Path(a.root).resolve()
    cfg = parse_config(root, a.config)
    src = a.config or (root / ".config")
    print(f"[i] 基准 config: {src}  (启用 y/m 共 {len(cfg)} 项)")

    kc = index_kconfig(root)
    print(f"[i] Kconfig 索引: {len(kc)} 个符号")

    res = {k: [] for k in ("MISSING_SRC", "NOT_WIRED", "NO_KCONFIG", "OK")}

    for sym, val in sorted(cfg.items()):
        name = sym[len("CONFIG_"):]
        kfile = kc.get(name)
        if not kfile:
            res["NO_KCONFIG"].append({"config": sym, "type": val})
            continue

        d, targets, where = find_targets(sym, kfile, root)
        if not targets:
            # 目录 Makefile 里是否以非 obj 形式引用（feature 开关）
            mk = d / "Makefile"
            ref = has_any_ref(mk, sym) if mk.exists() else False
            res["NOT_WIRED"].append({
                "config": sym, "type": val,
                "kconfig": str(kfile.relative_to(root)),
                "dir": str(d.relative_to(root)),
                "dir_exists": d.is_dir(),
                "note": "Makefile 有引用但非 obj 规则(功能开关)" if ref else "整条链无引用",
            })
            continue

        good, bad = [], []
        for t in targets:
            ok, detail = resolve_o(d, t)
            (good if ok else bad).append(detail)
        if good:
            res["OK"].append({"config": sym, "type": val, "targets": targets, "resolved": good})
        else:
            res["MISSING_SRC"].append({
                "config": sym, "type": val,
                "kconfig": str(kfile.relative_to(root)),
                "makefile_dir": str(d.relative_to(root)),
                "wired_by": where,
                "targets": targets,
                "problems": bad,
            })

    n_dir_missing = [r for r in res["NOT_WIRED"] if not r.get("dir_exists")]
    print()
    print("=" * 78)
    print(f"  MISSING_SRC (config 开了但源码缺失) : {len(res['MISSING_SRC'])}")
    print(f"  NOT_WIRED   (Kconfig 有, Makefile 不接线): {len(res['NOT_WIRED'])}")
    print(f"    其中定义目录不存在                    : {len(n_dir_missing)}")
    print(f"  NO_KCONFIG  (config 残留, 无 Kconfig 定义): {len(res['NO_KCONFIG'])}")
    print(f"  OK          (能对上源码)                 : {len(res['OK'])}")
    print("=" * 78)

    if n_dir_missing:
        print("\n--- 定义目录不存在（Kconfig 在，但驱动目录没了）---")
        for r in n_dir_missing[:60]:
            print(f"  {r['config']}={r['type']}  dir={r['dir']}")

    if res["MISSING_SRC"]:
        print("\n--- MISSING_SRC 明细 ---")
        for r in res["MISSING_SRC"]:
            print(f"  {r['config']}={r['type']}  [{r['makefile_dir']}]")
            for p in r["problems"]:
                print(f"      {p}")

    if a.report:
        Path(a.report).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[i] JSON: {a.report}")

    if a.md:
        lines = ["# 内核 config 与源码一致性核对", "",
                 f"- 内核树: `{root}`",
                 f"- 启用项: {len(cfg)}（y/m）",
                 f"- 缺失源码: **{len(res['MISSING_SRC'])}**",
                 f"- 未接线: {len(res['NOT_WIRED'])}",
                 f"- config 残留: {len(res['NO_KCONFIG'])}", ""]
        lines += ["## 一、config 开了但源码缺失", ""]
        if res["MISSING_SRC"]:
            lines += ["| CONFIG | 类型 | Kconfig | Makefile 目录 | 缺失内容 |", "|---|---|---|---|---|"]
            for r in res["MISSING_SRC"]:
                lines.append(f"| `{r['config']}` | {r['type']} | {r['kconfig']} | "
                             f"`{r['makefile_dir']}` | {'; '.join(r['problems'])} |")
        else:
            lines.append("无。")
        lines += ["", "## 二、Kconfig 有定义但 Makefile 未接线", ""]
        if res["NOT_WIRED"]:
            lines += ["| CONFIG | 类型 | Kconfig | 说明 |", "|---|---|---|---|"]
            for r in res["NOT_WIRED"]:
                lines.append(f"| `{r['config']}` | {r['type']} | {r['kconfig']} | {r['note']} |")
        else:
            lines.append("无。")
        Path(a.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[i] Markdown: {a.md}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
