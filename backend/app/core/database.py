"""数据库会话与 Base。

LoongArch 版本：直接用 SQLite，跳过 PostgreSQL 探测，启动更快更稳。
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

engine = None
SessionLocal = None


def init_db():
    """初始化 SQLite 数据库。"""
    global engine, SessionLocal
    if engine is not None:
        return
    db_path = settings.sqlite_path
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    engine = create_engine(
        settings.sqlite_dsn,
        connect_args={"check_same_thread": False},
        future=True,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    print(f"[INFO] 使用 SQLite 数据库: {db_path}")


def get_db():
    if engine is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    pass
