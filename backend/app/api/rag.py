"""知识检索与问答路由。"""
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from pydantic import BaseModel
from app.core.storage import upload_bytes
from app.services.rag import retrieve, answer_with_citations

router = APIRouter(prefix="/rag", tags=["知识检索"])


class QueryRequest(BaseModel):
    query: str
    image_url: Optional[str] = None
    topk: int = 5


@router.post("/retrieve")
async def api_retrieve(req: QueryRequest):
    """仅检索，返回知识片段。"""
    docs = await retrieve(req.query, req.image_url, req.topk)
    return {"total": len(docs), "items": docs}


@router.post("/ask")
async def api_ask(req: QueryRequest):
    """检索 + 大模型生成答案（带引用）。"""
    return await answer_with_citations(req.query, req.image_url)


@router.post("/ask-with-image")
async def api_ask_with_image(
    file: UploadFile = File(...),
    query: str = Form(""),
):
    """上传图片 + 文字提问（跨模态）。"""
    data = await file.read()
    image_url = upload_bytes(f"query/{file.filename}", data, file.content_type or "image/jpeg")
    return await answer_with_citations(query or "请根据图片分析缺陷并给出处置建议", image_url)
