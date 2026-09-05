#!/usr/bin/env bash
# fetch_arxiv.sh — 下载并解压 arXiv 论文源码
# 用法: fetch_arxiv.sh <arxiv_id> <workdir>
set -euo pipefail
ID="$1"; WORK="${2:-.}"
mkdir -p "$WORK/$ID/src"
URL="https://arxiv.org/e-print/$ID"
echo "[fetch] $URL"
curl -sL -A "Mozilla/5.0 (X11; Linux x86_64) paper-translate-kit" \
     -o "$WORK/arXiv-$ID.tar.gz" "$URL"
sleep 2
FMT=$(file -b "$WORK/arXiv-$ID.tar.gz")
case "$FMT" in
  *"gzip compressed"*)
    tar -xzf "$WORK/arXiv-$ID.tar.gz" -C "$WORK/$ID/src" 2>/dev/null \
      || { mkdir -p /tmp/ptk_unpack && tar -xzf "$WORK/arXiv-$ID.tar.gz" -C /tmp/ptk_unpack; }
    ;;
  *"PDF"*)
    echo "[warn] 源码不可用，arXiv 返回了 PDF"; exit 1 ;;
  *)
    # 可能是单个 tex/gzip 文件
    cp "$WORK/arXiv-$ID.tar.gz" "$WORK/$ID/src/main_payload.bin" ;;
esac
N=$(find "$WORK/$ID/src" -type f | wc -l)
echo "[ok] $ID 解压完成: $N 个文件"
find "$WORK/$ID/src" -maxdepth 1 | head -20
