#!/usr/bin/env bash
# 幂等合入 BPF defconfig 片段（先删除同名旧值，再追加 fragment）
set -euo pipefail
REPO="${1:-.}"
HERE="$(cd "$(dirname "$0")" && pwd)"
FRAG="$HERE/bpf-5.10.fragment"
[ -f "$FRAG" ] || { echo "缺少 $FRAG" >&2; exit 1; }

python3 - "$REPO" "$FRAG" <<'PY'
import sys, os, re
repo, frag = sys.argv[1], sys.argv[2]
lines = [l.rstrip('\n') for l in open(frag, encoding='utf-8') if l.strip() and not l.lstrip().startswith('#')]
keys = [l.split('=')[0].strip() for l in lines]
targets = [
    'arch/arm64/configs/defconfig',
    'arch/arm64/configs/vendor/kona_defconfig',
    'arch/arm64/configs/vendor/kona-perf_defconfig',
]
for t in targets:
    p = os.path.join(repo, t)
    if not os.path.isfile(p):
        print('  跳过（不存在）:', t)
        continue
    src = open(p, encoding='utf-8').read().splitlines()
    kept = [l for l in src if not any(
        l.strip() == k or l.strip().startswith(k + '=') or l.strip() == '# ' + k + ' is not set'
        for k in keys)]
    out = kept + ['', '# --- 5.10-bpf / Android 16 bpfloader ---'] + lines + ['']
    open(p, 'w', encoding='utf-8').write('\n'.join(out))
    print('  已更新:', t, '（新增/替换', len(lines), '项）')
PY
echo "配置合入完成；请用 make olddefconfig 或厂商构建脚本复核（CONFIG_HAVE_EBPF_JIT 可能被自动 select 覆盖）。"
