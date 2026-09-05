#!/usr/bin/env bash
# setup_chinese.sh — 从英文源码克隆中文翻译目录并注入 ctex/Noto 适配
# 用法: setup_chinese.sh <src_dir> [zh_dir]
set -euo pipefail
SRC="$1"; ZH="${2:-${SRC%/}/../zh}"
[ -d "$ZH" ] && { echo "[skip] $ZH 已存在"; exit 0; }
cp -r "$SRC" "$ZH"
# 清理构建产物
find "$ZH" -maxdepth 3 \( -name '*.aux' -o -name '*.log' -o -name '*.out' \
  -o -name '*.bbl' -o -name '*.blg' -o -name '*.pdf' -o -name 'bu*.aux' \) -delete 2>/dev/null || true

INJECT='\usepackage[UTF8,fontset=none]{ctex}
\setCJKmainfont[BoldFont={Noto Serif CJK SC Bold}]{Noto Serif CJK SC}
\setCJKsansfont[BoldFont={Noto Sans CJK SC Bold}]{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}'

python3 - "$ZH" "$INJECT" <<'PYEOF'
import re, sys, os
zh, inject = sys.argv[1], sys.argv[2]
inject = inject.replace('\\n', '\n')
changed = []
for root, _, files in os.walk(zh):
    for f in files:
        if not f.endswith('.tex'): continue
        p = os.path.join(root, f)
        t = open(p, encoding='utf-8').read()
        orig = t
        # 1) 禁用 axessibility（pdfLaTeX 专属）
        t = re.sub(r'^(\s*)\\usepackage\[accsupp\]\{axessibility\}.*$',
                   r'\1% \\usepackage[accsupp]{axessibility} % 仅支持 pdfLaTeX，为兼容中文编译已禁用（不影响排版与内容）',
                   t, flags=re.M)
        # 2) 注入 ctex（每个含 documentclass 的主/辅 tex，去重）
        if '\\documentclass' in t and 'ctex' not in t:
            t = t.replace('\\documentclass', inject + '\n\\documentclass', 1)
        if t != orig:
            open(p, 'w', encoding='utf-8').write(t)
            changed.append(os.path.relpath(p, zh))
print('[setup_chinese] 修改:', changed or '（无——请手工检查 ctex 注入位置）')
print('[setup_chinese] 提醒：')
print('  - icml2026 工程需在 \\usepackage{icml2026} 之前加 \\newdimen\\pdfpagewidth \\newdimen\\pdfpageheight')
print('  - 中文版推荐引擎 LuaLaTeX；\\title/单位请翻译；作者姓名保留拼音')
PYEOF
echo "[ok] 中文目录就绪: $ZH"
