"""Milvus 向量库封装：双向量列（文本+图像），支持跨模态检索。

集合设计 rail_knowledge：
  - id (INT64)         主键
  - text_vec (FLOAT_VECTOR 1024)  文本向量
  - image_vec (FLOAT_VECTOR 512)  图像向量（CLIP 维度）
  - doc_type (VARCHAR)  text/image/table
  - source (VARCHAR)    规程/图谱/案例
  - title (VARCHAR)
  - content (VARCHAR)   原文片段
  - image_url (VARCHAR) 关联图片（若有）
"""
from typing import List, Optional
from loguru import logger
from app.core.config import settings

COLLECTION = "rail_knowledge"
TEXT_DIM = 1024
IMAGE_DIM = 512  # CLIP ViT-B/32

_client = None
_collection = None
_collection_inited = False


def _get_client():
    global _client, _collection_inited
    if _client is not None:
        return _client
    try:
        from pymilvus import connections
        connections.connect(alias="default", host=settings.milvus_host, port=settings.milvus_port)
        _client = True
        logger.info("Milvus 已连接")
        return _client
    except Exception as e:
        logger.warning("Milvus 未就绪：{}。检索将降级为内存匹配。", str(e)[:80])
        return None


def init_collection():
    """创建集合（幂等）。Milvus 不可用时跳过。"""
    global _collection, _collection_inited
    if _collection_inited:
        return
    if _get_client() is None:
        return
    from pymilvus import (
        Collection, CollectionSchema, FieldSchema, DataType, utility,
    )
    if utility.has_collection(COLLECTION):
        _collection = Collection(COLLECTION)
        _collection.load()
        logger.info("已加载集合 {}", COLLECTION)
        _collection_inited = True
        return

    fields = [
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("text_vec", DataType.FLOAT_VECTOR, dim=TEXT_DIM),
        FieldSchema("image_vec", DataType.FLOAT_VECTOR, dim=IMAGE_DIM),
        FieldSchema("doc_type", DataType.VARCHAR, max_length=50),
        FieldSchema("source", DataType.VARCHAR, max_length=200),
        FieldSchema("title", DataType.VARCHAR, max_length=500),
        FieldSchema("content", DataType.VARCHAR, max_length=4000),
        FieldSchema("image_url", DataType.VARCHAR, max_length=500),
    ]
    schema = CollectionSchema(fields, "钢轨探伤多模态知识库")
    col = Collection(COLLECTION, schema)
    # 索引
    col.create_index("text_vec", {"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 128}})
    col.create_index("image_vec", {"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 128}})
    col.load()
    _collection = col
    _collection_inited = True
    logger.info("已创建并加载集合 {}", COLLECTION)


# ===== 内存降级存储（Milvus 不可用时） =====
_mem_store: List[dict] = []


def insert(item: dict, text_vec: List[float], image_vec: Optional[List[float]] = None):
    """插入一条知识。item 含 doc_type/source/title/content/image_url。"""
    global _collection
    if _collection is not None:
        _collection.insert([
            [text_vec],
            [image_vec or [0.0] * IMAGE_DIM],
            [item.get("doc_type", "text")],
            [item.get("source", "")],
            [item.get("title", "")],
            [item.get("content", "")[:4000]],
            [item.get("image_url", "")],
        ])
    else:
        _mem_store.append({**item, "text_vec": text_vec, "image_vec": image_vec})


def flush():
    if _collection is not None:
        _collection.flush()


def search_text(query_vec: List[float], topk: int = 5) -> List[dict]:
    """文本向量召回。"""
    if _collection is not None:
        _collection.load()
        res = _collection.search(
            [query_vec], "text_vec", {"metric_type": "IP", "params": {"nprobe": 16}},
            limit=topk, output_fields=["doc_type", "source", "title", "content", "image_url"],
        )
        out = []
        for hit in res[0]:
            e = hit.entity
            out.append({"score": float(hit.score), **{k: e.get(k) for k in
                       ["doc_type", "source", "title", "content", "image_url"]}})
        return out
    # 内存降级：cos 相似度
    return _mem_search(query_vec, "text_vec", topk)


def search_image(query_vec: List[float], topk: int = 5) -> List[dict]:
    """图像向量召回（以图搜案例）。"""
    if _collection is not None:
        _collection.load()
        res = _collection.search(
            [query_vec], "image_vec", {"metric_type": "IP", "params": {"nprobe": 16}},
            limit=topk, output_fields=["doc_type", "source", "title", "content", "image_url"],
        )
        out = []
        for hit in res[0]:
            e = hit.entity
            out.append({"score": float(hit.score), **{k: e.get(k) for k in
                       ["doc_type", "source", "title", "content", "image_url"]}})
        return out
    return _mem_search(query_vec, "image_vec", topk)


def _mem_search(query_vec: List[float], field: str, topk: int) -> List[dict]:
    from app.services.embedding import cosine_similarity
    scored = []
    for item in _mem_store:
        v = item.get(field) or [0.0] * len(query_vec)
        sim = cosine_similarity(query_vec, v)
        scored.append({"score": sim, "doc_type": item.get("doc_type"),
                       "source": item.get("source"), "title": item.get("title"),
                       "content": item.get("content"), "image_url": item.get("image_url")})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:topk]