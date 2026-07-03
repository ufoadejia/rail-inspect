# LoongArch 实验机部署指南

> 铁轨探伤智能检修系统 · 麒麟高级服务器版 + LoongArch 架构

## 环境要求（已验证）

| 项 | 要求 | 实验机现状 |
|----|------|-----------|
| 架构 | loongarch64 | ✅ |
| 系统 | 麒麟高级服务器版 (ky11) | ✅ |
| 内核 | Linux 6.6.0 | ✅ |
| Python | 3.11+ | ✅ 3.11.6 |
| Node | 18+ | ✅ v20.18.2 |
| npm | 9+ | ✅ 10.8.2 |
| Docker | 不需要 | — |

## 技术选型（LoongArch 适配版）

| 层 | 选型 | 说明 |
|----|------|------|
| 前端 | React + Vite + TS + Ant Design | 纯 JS，无原生编译 |
| 后端 | FastAPI 0.99.1 + pydantic 1.10.13 | **锁版本绕开 Rust 编译** |
| 数据库 | SQLite | 无需 Docker，无需编译 |
| 向量检索 | 内存 numpy 检索 | 自动降级，无需 Milvus |
| 文件存储 | 本地文件系统 | 自动降级，无需 MinIO |
| 大模型 | Qwen-VL 云端 + mock 兜底 | 无 key 也能演示 |

## 部署步骤

### 第 0 步：把代码弄进实验机

实验机是隔离的浏览器终端，不能粘贴长内容。推荐方式：

**方式 A：git clone（推荐）**
```bash
git clone <你的仓库地址> rail-inspect
cd rail-inspect
```

**方式 B：下载压缩包**
```bash
curl -L -o app.tar.gz <下载地址>
tar xzf app.tar.gz
cd rail-inspect
```

### 第 1 步：安装依赖

```bash
bash deploy/run_loongarch.sh install
```

这一步会：
- 后端：`pip3 install -r backend/requirements.txt`
- 前端：`npm install`（用 npmmirror 镜像）

### 第 2 步：构建知识库

```bash
bash deploy/run_loongarch.sh build
```

### 第 3 步：启动

```bash
# 方式一：分别启动两个终端
bash deploy/run_loongarch.sh backend   # 终端1：后端
bash deploy/run_loongarch.sh frontend  # 终端2：前端

# 方式二：一条命令同时启动
bash deploy/run_loongarch.sh all
```

启动后访问：
- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs

## 配置大模型（可选）

默认走 mock 模式，无需任何配置即可演示。

如需接入真实通义千问：
```bash
vi .env
# 修改：
# DASHSCOPE_API_KEY=sk-你的key
# USE_MOCK=false
```

## 常见问题

### Q: pip 安装卡在 "Installing build dependencies"
A: 不要装 pydantic v2。本项目的 requirements.txt 已锁定 pydantic==1.10.13（纯 Python）。
   如果你之前装过 pydantic v2，先卸载：`pip3 uninstall pydantic pydantic-core -y`

### Q: npm install 很慢
A: 脚本已自动用 npmmirror 镜像。如仍慢，手动指定：
   `npm install --registry=https://registry.npmmirror.com`

### Q: 前端能打开但接口报错
A: 确认后端已启动（http://localhost:8000/docs 能打开）。
   前端默认请求 http://localhost:8000，如端口不同需改 frontend 里的配置。

### Q: 大模型调用失败
A: 默认 USE_MOCK=true，会返回模拟数据，不影响演示。
   要用真实模型需配置 DASHSCOPE_API_KEY 且实验机能访问外网。
