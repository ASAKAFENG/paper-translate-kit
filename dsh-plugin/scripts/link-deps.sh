#!/bin/bash
# 把 DSH 宿主侧 peer 依赖软链进本包 node_modules，使 ESM import 从插件源码目录可解析。
# 纯 JS 插件免构建（无 tsc），改 lib/ 后 dev_reload_package 即可热重载。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROFILE_NM="${DSH_PROFILE_NODE_MODULES:-$HOME/.dsh/profiles/node_modules}"
if [ ! -d "$PROFILE_NM/@deepseek-ai" ]; then
  echo "profile node_modules not found: $PROFILE_NM" >&2
  exit 1
fi
mkdir -p "$ROOT/node_modules/@deepseek-ai"
for pkg in schemastery dsh-llm dsh-tools cordis cosmokit; do
  target="$PROFILE_NM/@deepseek-ai/$pkg"
  if [ ! -e "$target" ]; then
    echo "missing profile dep: $target" >&2
    continue
  fi
  link="$ROOT/node_modules/@deepseek-ai/$pkg"
  rm -rf "$link"
  ln -s "$target" "$link"
  echo "linked @deepseek-ai/$pkg"
done
# cordis / cosmokit 用裸名解析（插件代码 import 'cordis' / 'cosmokit'）
for bare in cordis cosmokit; do
  target="$PROFILE_NM/@deepseek-ai/$bare"
  if [ -e "$target" ]; then
    rm -rf "$ROOT/node_modules/$bare"
    ln -s "$target" "$ROOT/node_modules/$bare"
    echo "linked bare $bare"
  fi
done
echo "OK: deps linked from $PROFILE_NM"
