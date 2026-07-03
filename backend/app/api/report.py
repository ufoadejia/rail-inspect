"""报告生成路由。"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.report import generate_report_docx

router = APIRouter(prefix="/reports", tags=["报告生成"])


@router.get("/{wid}/docx")
def download_report(wid: int, db: Session = Depends(get_db)):
    """导出工单的探伤报告（docx 或 txt 降级）。"""
    content, media_type, ext = generate_report_docx(db, wid)
    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=report_{wid}.{ext}"},
    )
