"""Embedding 服务：文本向量(bge) + 图像向量(CLIP)，跨模态对齐。

为降低启动成本，未安装模型时降级到 hash 伪向量，保证流程可跑通。
真实使用时安装 sentence-transformers 即可自动启用。

LoongArch 环境：numpy 可能装不上，所有计算用纯 Python 实现，
numpy 仅作为可选加速（装上就用，没装也能跑）。
"""
import hashlib
import math
from loguru import logger

EMBED_DIM = 1024  # bge-m3 维度

_text_model = None
_clip_model = None
_USE_REAL = False

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False
    logger.info("numpy 未安装，向量计算走纯 Python（性能足够演示用）")


def _try_load():
    """尝试加载真实模型，失败则降级。"""
    global _text_model, _clip_model, _USE_REAL
    if _USE_REAL:
        return
    try:
        from sentence_transformers import SentenceTransformer
        _text_model = SentenceTransformer("BAAI/bge-m3")
        _clip_model = SentenceTransformer("clip-ViT-B-32")
        _USE_REAL = True
        logger.info("已加载真实 Embedding 模型 (bge-m3 + CLIP)")
    except Exception as e:
        logger.warning("未加载真实 Embedding 模型，使用 hash 伪向量降级：{}", str(e)[:100])
        _USE_REAL = False


def embed_text(text: str) -> list:
    """文本向量。"""
    _try_load()
    if _USE_REAL and _text_model is not None:
        vec = _text_model.encode(text, normalize_embeddings=True)
        return vec.tolist()
    return _hash_vector(text)


def embed_image(image_path_or_url: str) -> list:
    """图像向量（用于以图搜案例）。"""
    _try_load()
    if _USE_REAL and _clip_model is not None:
        try:
            vec = _clip_model.encode(image_path_or_url)
            return vec.tolist()
        except Exception as e:
            logger.warning("CLIP 编码失败，降级：{}", str(e)[:80])
    return _hash_vector(image_path_or_url)


def _hash_vector(key: str) -> list:
    """确定性伪向量：同一输入永远得到同一向量，便于演示检索效果。"""
    h = hashlib.sha256(key.encode("utf-8")).digest()
    # 扩展到 EMBED_DIM 维
    repeats = (EMBED_DIM + len(h) - 1) // len(h)
    raw = (h * repeats)[:EMBED_DIM]
    if _HAS_NUMPY:
        arr = np.frombuffer(raw, dtype=np.uint8)
        vec = (arr.astype(np.float32) - 128) / 128.0
        norm = float(np.linalg.norm(vec)) or 1.0
        return (vec / norm).tolist()
    # 纯 Python 实现
    vec = [(b - 128) / 128.0 for b in raw]
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine_similarity(a: list, b: list) -> float:
    """纯 Python 或 numpy 的余弦相似度。"""
    if _HAS_NUMPY:
        va, vb = np.array(a), np.array(b)
        denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
        return float(va @ vb) / (denom + 1e-9) if denom > 0 else 0.0
    # 纯 Python
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb + 1e-9) if na > 0 and nb > 0 else 0.0
