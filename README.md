# 铁轨探伤智能检修系统

> 软件杯参赛项目 · 基于多模态大模型技术的设备检修知识检索与作业系统
> 方向：钢轨探伤

面向铁路探伤工的「**拍图即识别 → 知识即检索 → 工单即作业**」一体化智能终端系统。

## 功能模块

- **多模态缺陷识别**：上传钢轨表面照片 / 超声波 A·B·C 扫图，识别缺陷类型与等级
- **跨模态知识检索**：文字、图片或组合检索探伤规程、缺陷图谱、历史案例（RAG + 引用溯源）
- **智能问答与检修建议**：基于检索结果生成处置建议，每条建议标注来源
- **作业工单系统**：创建→派发→执行→验收→归档，支持现场拍照、语音填单
- **探伤报告生成**：自动汇总检测结果，导出 Word/PDF
- **数据看板**：缺陷分布、管段健康度、作业统计

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + Vite + TypeScript + Ant Design + Tailwind |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy |
| 多模态大模型 | Qwen-VL-Max（云端）+ Qwen2-VL-7B（本地备用） |
| Embedding | bge-m3（文本）+ CLIP（图文对齐） |
| 向量库 | Milvus |
| 数据库 | PostgreSQL |
| 对象存储 | MinIO |
| 部署 | Docker Compose |

## 快速开始

### 1. 启动基础设施

```bash
cp .env.example .env       # 填入 API key（不填则用 mock）
docker compose up -d       # 启动 Milvus + PostgreSQL + MinIO
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python data_pipeline/build_knowledge.py   # 构建知识库（合成数据）
uvicorn app.main:app --reload --port 8000
```

打开 http://localhost:8000/docs 查看 API 文档。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173。

## 目录结构

```
软件杯/
├─ frontend/                 React 前端
├─ backend/                  FastAPI 后端
│  ├─ app/
│  │  ├─ api/               路由层
│  │  ├─ services/          业务服务（识别/RAG/工单/报告）
│  │  ├─ models/            数据模型
│  │  └─ core/              配置/鉴权
│  └─ data_pipeline/        知识库构建脚本
├─ knowledge/               知识库原始资料
├─ deploy/
│  └─ docker-compose.yml
└─ docs/                    方案文档、答辩材料
```

详见 `docs/方案.md`。
