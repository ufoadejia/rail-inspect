#!/bin/bash
# ============================================================
#  LoongArch / 麒麟实验机一键启动脚本
#  铁轨探伤智能检修系统
# ============================================================
#  用法:
#    cd 项目根目录
#    bash deploy/run_loongarch.sh install   # 首次：装依赖
#    bash deploy/run_loongarch.sh build     # 首次：构建知识库
#    bash deploy/run_loongarch.sh backend   # 启动后端
#    bash deploy/run_loongarch.sh frontend  # 启动前端(开发模式)
#    bash deploy/run_loongarch.sh all       # 后端+前端同时启动
# ============================================================

set -e

# 颜色
G="\033[32m"; Y="\033[33m"; R="\033[31m"; N="\033[0m"
info()  { echo -e "${G}[INFO]${N} $1"; }
warn()  { echo -e "${Y}[WARN]${N} $1"; }
err()   { echo -e "${R}[ERR]${N} $1"; }

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

# 复制环境配置
if [ ! -f .env ]; then
    info "复制 .env.loongarch -> .env"
    cp .env.loongarch .env
fi

case "${1:-help}" in

  install)
    info "=== 安装后端依赖 ==="
    cd backend
    pip3 install -r requirements.txt --user 2>&1 | tail -20
    info "后端依赖安装完成"
    info "=== 安装前端依赖 ==="
    cd "$ROOT/frontend"
    npm install --registry=https://registry.npmmirror.com 2>&1 | tail -20
    info "前端依赖安装完成"
    ;;

  build)
    info "=== 构建知识库 ==="
    cd backend
    python3 data_pipeline/build_knowledge.py
    info "知识库构建完成"
    ;;

  backend)
    info "=== 启动后端 (端口 8000) ==="
    cd backend
    info "API 文档: http://localhost:8000/docs"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ;;

  frontend)
    info "=== 启动前端 (端口 5173) ==="
    cd frontend
    info "前端地址: http://localhost:5173"
    npm run dev -- --host 0.0.0.0
    ;;

  all)
    info "=== 同时启动后端 + 前端 ==="
    bash "$0" backend &
    BACK_PID=$!
    sleep 3
    bash "$0" frontend &
    FRONT_PID=$!
    info "后端 PID=$BACK_PID, 前端 PID=$FRONT_PID"
    info "Ctrl+C 停止全部"
    trap "kill $BACK_PID $FRONT_PID 2>/dev/null; exit" INT TERM
    wait
    ;;

  *)
    echo "用法: bash deploy/run_loongarch.sh <命令>"
    echo ""
    echo "命令:"
    echo "  install    首次运行：安装前后端依赖"
    echo "  build      首次运行：构建知识库"
    echo "  backend    启动后端 (http://localhost:8000)"
    echo "  frontend   启动前端 (http://localhost:5173)"
    echo "  all        同时启动前后端"
    ;;

esac
