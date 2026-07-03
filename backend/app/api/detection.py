"""缺陷识别路由。"""
from fastapi import APIRouter, UploadFile, File, Form
from app.core.storage import upload_bytes
from app.services.detection import detect_defect

router = APIRouter(prefix="/detect", tags=["缺陷识别"])


@router.post("")
async def detect(
    file: UploadFile = File(...),
    image_type: str = Form("surface"),  # surface / a_scan / b_scan / c_scan
):
    """上传探伤图片，返回缺陷识别结果。"""
    data = await file.read()
    object_name = f"detect/{file.filename}"
    image_url = upload_bytes(object_name, data, file.content_type or "image/jpeg")
    result = await detect_defect(image_url, image_type)
    result["image_url"] = image_url
    return result
