"""Embedding 服务：文本向量(bge) + 图像向量(CLIP)，跨模态对齐。

为降低启动成本，未安装模型时降级到 hash 伪向量，保证流程可跑通。
真实使用时安装 sentence-transformers 即可自动启用。
"""
import hashlib
import numpy as np
from loguru import logger

EMBED_DIM = 1024  # bge-m3 维度

_text_model = None
_clip_model = None
_USE_REAL = False


def _try_load():
    """尝试加载真实模型，失败则降级。"""
    global _text_model, _clip_model, _USE_REAL
    if _USE_REAL:
        return
    try:
        from sentence_transformers import SentenceTransformer
        _text_model = SentenceTransformer("BAAI/bge-m3")
        # CLIP 用 openai/clip-vit-base-patch32 做图文对齐
        _clip_model = SentenceTransformer("clip-ViT-B-32")
        _USE_REAL = True
        logger.info("已加载真实 Embedding 模型 (bge-m3 + CLIP)")
    except Exception as e:
        logger.warning("未加载真实 Embedding 模型，使用 hash 伪向量降级：{}", str(e)[:100])
        _USE_REAL = False


def embed_text(text: str) -> list[float]:
    """文本向量。"""
    _try_load()
    if _USE_REAL and _text_model is not None:
        vec = _text_model.encode(text, normalize_embeddings=True)
        return vec.tolist()
    return _hash_vector(text)


def embed_image(image_path_or_url: str) -> list[float]:
    """图像向量（用于以图搜案例）。"""
    _try_load()
    if _USE_REAL and _clip_model is not None:
        try:
            vec = _clip_model.encode(image_path_or_url)
            return vec.tolist()
        except Exception as e:
            logger.warning("CLIP 编码失败，降级：{}", str(e)[:80])
    return _hash_vector(image_path_or_url)


def _hash_vector(key: str) -> list[float]:
    """确定性伪向量：同一输入永远得到同一向量，便于演示检索效果。"""
    h = hashlib.sha256(key.encode("utf-8")).digest()
    # 扩展到 EMBED_DIM 维
    repeats = (EMBED_DIM + len(h) - 1) // len(h)
    arr = np.frombuffer((h * repeats)[:EMBED_DIM], dtype=np.uint8)
    vec = (arr.astype(np.float32) - 128) / 128.0
    norm = np.linalg.norm(vec) or 1.0
    return (vec / norm).tolist()
