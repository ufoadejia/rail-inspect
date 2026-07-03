"""应用入口。"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from app.core.config import settings
from app.core.database import Base, init_db
from app.api import detection, rag, workorder, report, dashboard

# 统一用相对于 backend/ 目录的路径
# （uvicorn 在 backend/ 下启动，所以 data/uploads 即 backend/data/uploads）
UPLOAD_DIR = os.path.join("data", "uploads")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    logger.info("启动铁轨探伤智能检修系统...")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    init_db()
    from app.core.database import engine
    Base.metadata.create_all(bind=engine)  # 建表
    try:
        from app.services.vector_store import init_collection
        init_collection()
    except Exception as e:
        logger.warning("向量库初始化跳过：{}", str(e)[:80])
    logger.info("启动完成。API 文档：http://localhost:8000/docs")
    yield
    logger.info("关闭。")


app = FastAPI(
    title="铁轨探伤智能检修系统",
    description="基于多模态大模型技术的设备检修知识检索与作业系统 · 钢轨探伤方向",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（上传的图片代理访问）
app.mount("/files/local", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 路由
app.include_router(detection.router)
app.include_router(rag.router)
app.include_router(workorder.router)
app.include_router(report.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"name": "铁轨探伤智能检修系统", "version": "1.0.0",
            "docs": "/docs", "mock_mode": settings.use_mock}
