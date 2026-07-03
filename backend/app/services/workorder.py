"""工单服务：CRUD + 状态机流转。"""
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.tables import Workorder, Detection
from app.models.schemas import WorkorderStatus, can_transition


def list_workorders(db: Session, status: Optional[str] = None) -> List[Workorder]:
    q = select(Workorder).order_by(Workorder.created_at.desc())
    if status:
        # 兼容传入枚举 name 或 value
        try:
            sv = WorkorderStatus(status).value
        except ValueError:
            sv = status
        q = q.where(Workorder.status == sv)
    return list(db.scalars(q))


def get_workorder(db: Session, wid: int) -> Workorder:
    wo = db.get(Workorder, wid)
    if not wo:
        raise HTTPException(404, "工单不存在")
    return wo


def create_workorder(db: Session, data: dict) -> Workorder:
    wo = Workorder(
        title=data["title"], line_name=data["line_name"], kilometer=data.get("kilometer", ""),
        rail_side=data.get("rail_side", ""), description=data.get("description", ""),
        status=WorkorderStatus.CREATED.value, created_by=data.get("created_by", "system"),
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return wo


def transition_status(db: Session, wid: int, to_status: WorkorderStatus, assignee: Optional[str] = None) -> Workorder:
    """状态流转，校验合法性。"""
    wo = get_workorder(db, wid)
    to_enum = WorkorderStatus(to_status) if isinstance(to_status, str) else to_status
    # wo.status 可能是字符串或枚举，统一转成枚举比较
    cur_status = WorkorderStatus(wo.status) if isinstance(wo.status, str) else wo.status
    if not can_transition(cur_status, to_enum):
        raise HTTPException(400, f"不允许从 {cur_status} 流转到 {to_enum}")
    wo.status = to_enum.value
    if assignee:
        wo.assignee = assignee
    wo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(wo)
    return wo


def add_detection(db: Session, wid: int, data: dict) -> Detection:
    """往工单关联一条检测结果。"""
    get_workorder(db, wid)  # 校验存在
    det = Detection(workorder_id=wid, **data)
    db.add(det)
    db.commit()
    db.refresh(det)
    return det