"""数据看板路由：缺陷分布、工单统计。"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.tables import Workorder, Detection

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    # 工单状态分布
    status_rows = db.execute(
        select(Workorder.status, func.count(Workorder.id)).group_by(Workorder.status)
    ).all()
    status_dist = {str(r[0].value if hasattr(r[0], 'value') else r[0]): r[1] for r in status_rows}

    # 缺陷类型分布
    defect_rows = db.execute(
        select(Detection.defect_type, func.count(Detection.id)).group_by(Detection.defect_type)
    ).all()
    defect_dist = {str(r[0]): r[1] for r in defect_rows}

    # 判级分布
    grade_rows = db.execute(
        select(Detection.defect_grade, func.count(Detection.id)).group_by(Detection.defect_grade)
    ).all()
    grade_dist = {str(r[0]): r[1] for r in grade_rows}

    total_wo = db.scalar(select(func.count(Workorder.id)))
    total_det = db.scalar(select(func.count(Detection.id)))

    return {
        "total_workorders": total_wo,
        "total_detections": total_det,
        "status_distribution": status_dist,
        "defect_type_distribution": defect_dist,
        "grade_distribution": grade_dist,
    }
