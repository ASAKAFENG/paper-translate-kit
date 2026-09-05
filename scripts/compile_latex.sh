#!/usr/bin/env bash
# compile_latex.sh — 通用编译循环（自动处理 bibtex / bibunits / bbl-only）
# 用法: compile_latex.sh <dir> <main.tex> [pdflatex|xelatex|lualatex|auto]
set -uo pipefail
DIR="$1"; MAIN="$2"; ENG="${3:-auto}"
JOB="${MAIN%.*}"

cd "$DIR" || exit 1

if [ "$ENG" = "auto" ]; then
  ENG=$(python3 "$(dirname "$0")/detect_engine.py" . "$MAIN" | python3 -c "import json,sys;print(json.load(sys.stdin)['engine'])")
fi
run() { "$ENG" -interaction=nonstopmode "$MAIN" > /tmp/ptk_run.log 2>&1; echo $?; }

echo "[compile] engine=$ENG  pass1"
R1=$(run)

# bibtex 决策
AUX="$JOB.aux"
NEED_BIB=no
if grep -q '\\bibdata' "$AUX" 2>/dev/null; then
  NEED_BIB=yes
elif grep -q '\\input{.*\.bbl}' "$MAIN" 2>/dev/null; then
  NEED_BIB=no   # bbl 直接 input：绝不能跑 bibtex
fi

if [ "$NEED_BIB" = "yes" ]; then
  echo "[compile] bibtex $JOB"
  bibtex "$JOB" > /dev/null 2>&1
fi
# bibunits 支持（bu1.aux ... bu9.aux）
for i in 1 2 3 4 5 6 7 8 9; do
  [ -f "bu$i.aux" ] && { echo "[compile] bibtex bu$i"; bibtex "bu$i" > /dev/null 2>&1; }
done

echo "[compile] pass2"
run > /dev/null
echo "[compile] pass3"
R3=$(run)

PDF="${JOB}.pdf"
if [ ! -f "$PDF" ]; then
  echo "[FAIL] 未生成 $PDF"; grep -E "^!" /tmp/ptk_run.log | head -5; exit 1
fi

CIT=$(grep -c "Warning: Citation" /tmp/ptk_run.log)
ERR=$(grep -cE "^!" /tmp/ptk_run.log)
PAGES=$(pdfinfo "$PDF" 2>/dev/null | awk '/^Pages/{print $2}')
echo "[result] $PDF  pages=$PAGES  citation_warnings=$CIT  errors=$ERR"
[ "$ERR" = "0" ] && [ "$CIT" = "0" ] && echo "[OK] 验收通过" || { echo "[WARN] 见上"; exit 2; }
