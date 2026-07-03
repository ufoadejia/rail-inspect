#!/bin/bash
# LoongArch 实验机环境诊断脚本 v2
# 用法: curl -sL <URL> | bash

set +e
echo "================================================"
echo "  LoongArch 实验机环境诊断 v2"
echo "  时间: $(date)"
echo "================================================"
echo

echo "### 1. 系统信息 ###"
uname -a
echo "CPU: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2)"
free -h | head -2
df -h / | tail -1
echo

echo "### 2. Python / pip ###"
python3 --version
pip3 --version
echo "--- pip 配置 ---"
pip3 config list -v 2>&1
echo "--- 代理环境变量 ---"
env | grep -i proxy || echo "(无代理环境变量)"
echo

echo "### 3. Node / npm ###"
node --version
npm --version
which node npm
echo

echo "### 4. 网络连通性 ###"
for url in \
  "https://pypi.tuna.tsinghua.edu.cn" \
  "https://files.pythonhosted.org" \
  "https://pypi.org/simple" \
  "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" \
  "https://registry.npmmirror.com"; do
  code=$(curl -s -m 8 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
  echo "  $url -> $code"
done
echo

echo "### 5. pip 安装测试 (默认 PyPI, 详细) ###"
pip3 install fastapi --user -v 2>&1 | head -40
echo

echo "### 6. pip 安装测试 (TUNA + trusted-host) ###"
pip3 install fastapi --user \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --trusted-host pypi.tuna.tsinghua.edu.cn \
  -v 2>&1 | head -40
echo

echo "### 7. pip 升级自身 ###"
pip3 install --upgrade pip --user \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --trusted-host pypi.tuna.tsinghua.edu.cn 2>&1 | tail -10
echo

echo "### 8. 升级后重试安装 ###"
pip3 install fastapi uvicorn sqlalchemy pillow requests --user \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --trusted-host pypi.tuna.tsinghua.edu.cn 2>&1 | tail -15
echo

echo "### 9. Docker 状态 ###"
sudo systemctl status docker 2>&1 | head -5 || echo "docker 服务不可用"
echo

echo "### 10. 已安装的关键包 ###"
pip3 list 2>/dev/null | grep -iE "fastapi|uvicorn|sqlalchemy|flask|django|numpy|pillow|requests" || echo "(无关键包)"
echo

echo "================================================"
echo "  诊断完成，请把以上全部输出贴回"
echo "================================================"
