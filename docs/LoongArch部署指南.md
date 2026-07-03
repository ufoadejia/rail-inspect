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

---

## 部署步骤

### 第 0 步：把代码弄进实验机

实验机是浏览器内嵌终端，不能粘贴长内容，只能手敲短命令。代码传输有三种方式，按可行性排序：

#### 方式 A：git clone（最简单，需实验机能访问 GitHub/Gitee）

在本地把项目推到 GitHub/Gitee 后，实验机里敲：
```bash
git clone https://github.com/你的用户名/rail-inspect.git
cd rail-inspect
```

#### 方式 B：curl/wget 下载 tar 包（需实验机能访问外网）

在本地先打包：
```bash
bash deploy/pack.sh    # 产出 dist/rail-inspect.tar.gz (约84K)
```
把 tar.gz 上传到任意可访问的地方（网盘/GitHub Release/图床），实验机里敲：
```bash
curl -L -o r.tar.gz <下载地址>
tar xzf r.tar.gz
cd rail-inspect
```

#### 方式 C：纯手敲（保底方案，实验机完全隔离）

代码量不大（约20个源文件，每个几十行），可以分文件手敲。
这是最后手段，耗时长，仅在 A/B 都不行时用。

### 第 1 步：安装依赖

```bash
bash deploy/run_loongarch.sh install
```

这一步会：
- 后端：`pip3 install -r backend/requirements.txt`（约2分钟）
- 前端：`npm install`（用 npmmirror 镜像，约3分钟）

> ⚠️ 如果 pip 之前装过 pydantic v2，先卸载：
> ```bash
> pip3 uninstall pydantic pydantic-core -y
> ```

### 第 2 步：构建知识库

```bash
bash deploy/run_loongarch.sh build
```

这会往内存向量库灌入合成知识数据（探伤规程、缺陷图谱、案例）。

### 第 3 步：启动系统

```bash
# 方式一：分别启动（推荐，日志清晰）
bash deploy/run_loongarch.sh backend   # 终端1：后端
bash deploy/run_loongarch.sh frontend  # 终端2：前端

# 方式二：一条命令同时启动
bash deploy/run_loongarch.sh all
```

启动后访问：
- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs

---

## 配置大模型（可选）

默认走 mock 模式，无需任何配置即可演示。

如需接入真实通义千问 Qwen-VL：
```bash
vi .env
# 修改这两行：
# DASHSCOPE_API_KEY=sk-你的key
# USE_MOCK=false
```

然后重启后端即可。需要实验机能访问 `dashscope.aliyuncs.com`。

---

## 常见问题

### Q: pip 安装卡在 "Installing build dependencies" 不动
A: 这是在编译 pydantic-core（需要 Rust），LoongArch 上会卡死。
   本项目的 requirements.txt 已锁定 `pydantic==1.10.13`（纯 Python）。
   如果你之前装过 pydantic v2，先卸载：
   ```bash
   pip3 uninstall pydantic pydantic-core -y
   ```
   再重新 `bash deploy/run_loongarch.sh install`

### Q: pip 报 "No matching distribution found"
A: 先升级 pip：
   ```bash
   pip3 install --upgrade pip
   ```
   再重试安装。

### Q: npm install 很慢或失败
A: 脚本已自动用 npmmirror 镜像。如仍慢，手动指定：
   ```bash
   cd frontend
   npm install --registry=https://registry.npmmirror.com
   ```

### Q: 前端能打开但接口报错
A: 确认后端已启动（http://localhost:8000/docs 能打开）。
   前端通过 vite 代理转发到后端 8000 端口，两个服务都要跑。

### Q: 大模型调用失败
A: 默认 USE_MOCK=true，会返回模拟数据，不影响演示。
   要用真实模型需配置 DASHSCOPE_API_KEY 且实验机能访问外网。

### Q: docker compose up 报错
A: 本项目不依赖 Docker。实验机的 Docker daemon 未运行，直接用裸跑方式即可。

---

## 验证部署成功

1. 后端 API 文档能打开：http://localhost:8000/docs
2. 前端页面能打开：http://localhost:5173
3. 前端「缺陷识别」页面上传图片能返回结果（mock 模式返回随机缺陷）
4. 前端「知识检索」页搜索能返回知识片段
5. 前端「工单管理」能创建和查看工单
