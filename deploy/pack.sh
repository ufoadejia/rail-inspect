#!/bin/bash
# ============================================================
#  打包脚本：把项目打成 tar.gz，方便传到实验机
#  用法: bash deploy/pack.sh
#  产出: dist/rail-inspect.tar.gz
# ============================================================

set -e

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

OUT_DIR="dist"
OUT_FILE="$OUT_DIR/rail-inspect.tar.gz"

mkdir -p "$OUT_DIR"

# 用 git archive 打包（自动遵守 .gitignore，不含 node_modules/.db）
git archive --format=tar.gz --prefix=rail-inspect/ HEAD -o "$OUT_FILE"

SIZE=$(du -h "$OUT_FILE" | cut -f1)
echo "================================"
echo "  打包完成"
echo "  文件: $OUT_FILE"
echo "  大小: $SIZE"
echo "================================"
echo ""
echo "传输方式："
echo "  1. 如果实验机能访问本机：在实验机执行 wget/curl 下载"
echo "  2. 如果不能：用浏览器上传到任意网盘/图床，再在实验机下载"
echo "  3. 解压：tar xzf rail-inspect.tar.gz && cd rail-inspect"
