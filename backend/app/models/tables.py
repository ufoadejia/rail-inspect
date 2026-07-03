"""SQLAlchemy ORM 表模型。"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, Integer, Float, DateTime, ForeignKey, JSON, Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.schemas import WorkorderStatus


class Workorder(Base):
    __tablename__ = "workorders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    line_name: Mapped[str] = mapped_column(String(100))          # 线路名
    kilometer: Mapped[str] = mapped_column(String(50))           # 千米标
    rail_side: Mapped[str] = mapped_column(String(20))           # 左股/右股
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default=WorkorderStatus.CREATED.value)
    assignee: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 关联检测结果
    detections: Mapped[list["Detection"]] = relationship(back_populates="workorder", cascade="all, delete-orphan")


class Detection(Base):
    """一次缺陷检测记录。"""
    __tablename__ = "detections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workorder_id: Mapped[Optional[int]] = mapped_column(ForeignKey("workorders.id"), nullable=True)
    image_url: Mapped[str] = mapped_column(String(500))
    image_type: Mapped[str] = mapped_column(String(50))          # surface/a_scan/b_scan/c_scan
    defect_type: Mapped[str] = mapped_column(String(50))         # DefectType 值
    defect_grade: Mapped[str] = mapped_column(String(20))        # 正常/轻伤/重伤
    db_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str] = mapped_column(Text, default="")
    extra: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    workorder: Mapped[Optional["Workorder"]] = relationship(back_populates="detections")


class KnowledgeDoc(Base):
    """知识库文档元数据（向量在 Milvus）。"""
    __tablename__ = "knowledge_docs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(200))             # 来源：规程/图谱/案例
    doc_type: Mapped[str] = mapped_column(String(50))            # text/image/table
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)