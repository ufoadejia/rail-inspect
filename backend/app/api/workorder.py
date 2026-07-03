"""工单路由。"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import WorkorderStatus
from app.services import workorder as wo_service

router = APIRouter(prefix="/workorders", tags=["工单管理"])


class WOCreate(BaseModel):
    title: str
    line_name: str
    kilometer: str = ""
    rail_side: str = ""
    description: str = ""
    created_by: str = "system"


class WOTransition(BaseModel):
    to_status: WorkorderStatus
    assignee: Optional[str] = None


@router.get("")
def list_wo(status: Optional[str] = None, db: Session = Depends(get_db)):
    items = wo_service.list_workorders(db, status)
    return {"total": len(items), "items": [_wo_dict(w) for w in items]}


@router.post("")
def create_wo(req: WOCreate, db: Session = Depends(get_db)):
    wo = wo_service.create_workorder(db, req.dict())
    return _wo_dict(wo)


@router.get("/{wid}")
def get_wo(wid: int, db: Session = Depends(get_db)):
    wo = wo_service.get_workorder(db, wid)
    d = _wo_dict(wo)
    d["detections"] = [
        {"id": det.id, "image_url": det.image_url, "image_type": det.image_type,
         "defect_type": det.defect_type, "defect_grade": det.defect_grade,
         "db_value": det.db_value, "description": det.description}
        for det in wo.detections
    ]
    return d


@router.post("/{wid}/transition")
def transition_wo(wid: int, req: WOTransition, db: Session = Depends(get_db)):
    wo = wo_service.transition_status(db, wid, req.to_status, req.assignee)
    return _wo_dict(wo)


def _wo_dict(wo) -> dict:
    return {
        "id": wo.id, "title": wo.title, "line_name": wo.line_name,
        "kilometer": wo.kilometer, "rail_side": wo.rail_side,
        "description": wo.description, "status": wo.status.value if hasattr(wo.status, 'value') else wo.status,
        "assignee": wo.assignee, "created_by": wo.created_by,
        "created_at": wo.created_at.isoformat() if wo.created_at else None,
        "updated_at": wo.updated_at.isoformat() if wo.updated_at else None,
    }
