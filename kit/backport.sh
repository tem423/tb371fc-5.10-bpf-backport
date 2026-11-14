#!/usr/bin/env bash
# =============================================================================
# TB371FC (SM8250 / kona, Linux 4.19.325) -> 5.10-bpf backport
#   1) 把 lss4/android_kernel_lenovo_paladin 的 CLO 提交接到仓库历史最前面
#   2) 应用 Android 16 bpfloader 所需的 5.10-bpf 补丁集
#   3) 校验防卡死重启用的 cgroup_bpf fixup / 补齐 BPF defconfig
#
# 用法:
#   ./backport.sh /path/to/kernel-tb371fc [选项]
#
# 选项:
#   --paladin=history|full|rebase|none   默认 history
#       history : git merge -s ours，只把 CLO 历史接进来，不改源码（推荐，源码已完整时）
#       full    : git merge，把 CLO 代码改动一起合入（会产生较多冲突，需人工裁决）
#       rebase  : git rebase --onto paladin/11 <merge-base>，历史严格线性、paladin 全在最前
#       none    : 跳过
#   --bpf=diff|am|none                  默认 diff
#       diff    : git apply --reject 应用裁剪后的聚合 diff（快，保留 .rej 供人工处理）
#       am      : git am 应用 1444 个提交的邮箱补丁（保留完整提交历史，遇冲突需 git am --continue）
#       none    : 跳过
#   --extra=check|full|no               默认 check
#       check : 检查 cgroup_bpf_get() 修复是否已随 1444 补丁集落地，缺才补（推荐）
#       full  : 额外应用 android16-aptusitu-new 路线的 101 段补丁（含 KSU/SuSFS，
#               会产生大量 .rej，仅在明确需要时启用）
#       no    : 跳过防卡死校验
#   --config=no                        跳过 defconfig 合入
#   --commit                           处理完后自动提交（不会提交 .rej / .orig）
#   --branch=NAME                      工作分支名，默认 backport-5.10-bpf
# =============================================================================
set -euo pipefail

REPO="${1:-}"
[ -n "$REPO" ] || { echo "用法: $0 <kernel-repo-dir> [选项]" >&2; exit 1; }
shift || true

PALADIN_MODE=history
BPF_MODE=diff
DO_EXTRA=check
DO_CONFIG=yes
DO_COMMIT=no
BRANCH=backport-5.10-bpf
for a in "$@"; do
  case "$a" in
    --paladin=*) PALADIN_MODE="${a#*=}" ;;
    --bpf=*)     BPF_MODE="${a#*=}" ;;
    --extra=*)   DO_EXTRA="${a#*=}" ;;
    --config=no) DO_CONFIG=no ;;
    --commit)    DO_COMMIT=yes ;;
    --branch=*)  BRANCH="${a#*=}" ;;
    *) echo "未知选项: $a" >&2; exit 1 ;;
  esac
done

HERE="$(cd "$(dirname "$0")" && pwd)"
PATCHES="$HERE/patches"
REPORTS="$HERE/reports"
mkdir -p "$REPORTS"
LOG="$REPORTS/backport-run.log"
: > "$LOG"
log(){ echo "$*" | tee -a "$LOG"; }

cd "$REPO"
[ -d .git ] || { echo "$REPO 不是 git 仓库" >&2; exit 1; }
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "工作区不干净，请先提交或 stash" >&2; exit 1
fi
BASE_BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null || echo main)"
ORIG_HEAD="$(git rev-parse HEAD)"
log "仓库: $REPO"
log "基准分支: $BASE_BRANCH @ $ORIG_HEAD"
log "工作分支: $BRANCH"

# ---------------------------------------------------------------- 0. 分支
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  log "分支 $BRANCH 已存在，直接切换"
  git checkout "$BRANCH"
else
  git checkout -b "$BRANCH" "$BASE_BRANCH"
fi

# ------------------------------------------------- 1. 把 paladin CLO 历史前置
if [ "$PALADIN_MODE" != none ]; then
  log ""
  log "=== Step 1: 合入 lss4/android_kernel_lenovo_paladin (分支 11) ==="
  if ! git remote get-url paladin >/dev/null 2>&1; then
    git remote add paladin https://github.com/lss4/android_kernel_lenovo_paladin.git
  fi
  # 两个仓库共享 Linux 根提交 1da177e4，fetch 会复用绝大部分对象
  git fetch --no-tags paladin 11
  PAL="$(git rev-parse FETCH_HEAD)"
  log "paladin/11 tip: $PAL"
  case "$PALADIN_MODE" in
    history)
      log "模式 history: merge -s ours（仅补历史，源码保持 TB371FC 现状）"
      git merge --no-edit -s ours -m "chore: graft lss4/paladin CLO history ahead of TB371FC tree" "$PAL" || {
        log "merge 失败，可改用 --paladin=none 跳过此步"; exit 1; }
      ;;
    full)
      log "模式 full: 常规 merge（CLO 代码改动一并合入，冲突需人工裁决）"
      git merge --no-edit -m "Merge lss4/paladin CLO baseline into TB371FC" "$PAL" || {
        log "merge 出现冲突：git status 查看，解决后 git add -A && git commit"; exit 1; }
      ;;
    rebase)
      MB="$(git merge-base HEAD "$PAL")"
      log "merge-base: $MB"
      log "模式 rebase: 把 TB371FC 独有提交重放到 paladin/11 之上"
      git rebase --onto "$PAL" "$MB" "$BRANCH" || {
        log "rebase 出现冲突：解决后 git rebase --continue"; exit 1; }
      ;;
    *) echo "未知的 --paladin 模式: $PALADIN_MODE" >&2; exit 1 ;;
  esac
  log "Step 1 完成"
else
  log "Step 1 跳过 (--paladin=none)"
fi

# ------------------------------------------------------- 2. 5.10-bpf 补丁集
if [ "$BPF_MODE" != none ]; then
  log ""
  log "=== Step 2: 应用 5.10-bpf 补丁集 ==="
  if [ "$BPF_MODE" = diff ]; then
    P="$PATCHES/5.10-bpf-tb371fc.diff"
    log "使用裁剪版聚合 diff（已剔除小米机型 defconfig / CI 文件）"
    git apply --reject --whitespace=nowarn "$P" >> "$LOG" 2>&1 || true
    log "git apply 完成，详见 $LOG"
  elif [ "$BPF_MODE" = am ]; then
    P="$PATCHES/apartusitu-backport-5.10-bpf.patch"
    log "使用 1444 提交邮箱补丁（保留提交历史）"
    if ! git am --whitespace=nowarn "$P" >> "$LOG" 2>&1; then
      log "git am 中断（冲突）。处理顺序："
      log "  git status -> 手工解决 -> git add -A && git am --continue"
      log "  若某提交完全不需要：git am --skip"
      log "  放弃全部：git am --abort"
      exit 1
    fi
  else
    echo "未知的 --bpf 模式: $BPF_MODE" >&2; exit 1
  fi
  # 校验核心特性确实落地
  if grep -q 'BPF_MAP_TYPE_RINGBUF' include/uapi/linux/bpf.h && [ -f kernel/bpf/ringbuf.c ]; then
    log "校验通过: BPF ring buffer 已落地"
  else
    log "警告: 未检测到 BPF_MAP_TYPE_RINGBUF / kernel/bpf/ringbuf.c，请检查补丁应用情况" >&2
  fi
else
  log "Step 2 跳过 (--bpf=none)"
fi

# ------------------------------------------- 3. 防卡死重启 fixup 校验
log ""
log "=== Step 3: 防卡死重启 cgroup_bpf fixup 校验 ==="
case "$DO_EXTRA" in
  check)
    # 完整 1444 提交集的 tip 就是 "fixup! bpf: decouple the lifetime of
    # cgroup_bpf from cgroup itself"，通常已包含此修复
    if grep -q 'cgroup_bpf_get(sock_cgroup_ptr(skcd))' kernel/cgroup/cgroup.c 2>/dev/null; then
      log "cgroup_bpf_get() 修复已随 5.10-bpf 补丁集落地，无需追加"
    else
      log "未检测到 cgroup_bpf_get() 修复，补入 android16-bpf-hotfix.diff"
      git apply --reject --whitespace=nowarn "$PATCHES/android16-bpf-hotfix.diff" >> "$LOG" 2>&1 || true
    fi
    ;;
  full)
    log "模式 full: 应用 android16-aptusitu-new 路线补丁（含 KSU/SuSFS，会产生较多 .rej）"
    git apply --reject --whitespace=nowarn "$PATCHES/android16-fixes-tb371fc.diff" >> "$LOG" 2>&1 || true
    ;;
  no)
    log "跳过 (--extra=no)"
    ;;
  *) echo "未知的 --extra 模式: $DO_EXTRA" >&2; exit 1 ;;
esac

# -------------------------------------------------------- 4. defconfig
if [ "$DO_CONFIG" = yes ]; then
  log ""
  log "=== Step 4: 合入 BPF defconfig 片段 ==="
  bash "$HERE/configs/apply-config.sh" "$REPO" | tee -a "$LOG"
fi

# -------------------------------------------------------- 5. 报告
log ""
log "=== Step 5: 冲突/改动汇总 ==="
REJ="$(find . -type f -name '*.rej' | sort)"
printf '%s\n' "$REJ" > "$REPORTS/reject-files.txt"
N_REJ=$(printf '%s\n' "$REJ" | grep -c '\.rej$' || true)
log "残留 .rej 文件数: $N_REJ  (清单: $REPORTS/reject-files.txt)"
log "改动文件数: $(git status --porcelain | wc -l)"
git status --short > "$REPORTS/git-status.txt"
if [ "$N_REJ" -gt 0 ]; then
  log "注意: 请按 reports/conflict-analysis.md 逐项处理 .rej，特别是 kernel/sys.c（fake uname）"
  log "      与 include/asm-generic/vmlinux.lds.h（BTF_ID 段）。"
fi

if [ "$DO_COMMIT" = yes ]; then
  if [ "$N_REJ" -gt 0 ]; then
    log "存在未解决的 .rej，拒绝自动提交。处理完后加 --commit 重跑或手动提交。" >&2
    exit 1
  fi
  find . -type f -name '*.orig' -delete
  git add -A
  git commit -m "bpf: backport 5.10-bpf for Android 16 bpfloader (TB371FC/kona)

Graft lss4/paladin CLO history, apply the 4.19->5.10-bpf backport series
and enable the BPF/LSM defconfig options required by Android 16 bpfloader."
  log "已提交: $(git rev-parse --short HEAD)"
else
  log "未自动提交。检查无误后执行: git add -A && git commit"
fi

log ""
log "后续: make olddefconfig（或厂商 build 脚本）-> 编译 -> 刷入 -> 开 DSU Android 16 GSI 验证"
log "验证: adb shell dmesg | grep -i bpfloader ; adb shell getprop | grep -i bpf"
log "完成。日志: $LOG"
