"""文件存储：MinIO 不可用时自动降级到本地文件系统。

LoongArch 环境默认走本地文件，不依赖 MinIO。
"""
import os
from loguru import logger
from app.core.config import settings

_client = None
_tried = False

# 本地存储根目录（相对于 backend/）
LOCAL_UPLOAD_DIR = os.path.join("data", "uploads")


def get_minio():
    """返回 MinIO 客户端，连接失败返回 None（降级到本地文件）。"""
    global _client, _tried
    if _tried:
        return _client
    _tried = True
    try:
        from minio import Minio  # 函数内导入，未安装时降级
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,
        )
        if not _client.bucket_exists(settings.minio_bucket):
            _client.make_bucket(settings.minio_bucket)
        logger.info("MinIO 已连接，bucket={}", settings.minio_bucket)
        return _client
    except Exception as e:
        logger.warning("MinIO 未就绪，使用本地存储：{}", str(e)[:100])
        _client = None
        return None


def upload_bytes(object_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """上传字节数据，返回可访问 URL。MinIO 不可用时落本地。"""
    import io
    client = get_minio()
    if client is not None:
        client.put_object(
            settings.minio_bucket, object_name, io.BytesIO(data),
            length=len(data), content_type=content_type,
        )
        return f"/files/{object_name}"
    # 降级：写本地
    os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)
    safe_name = object_name.replace("/", "_")
    path = os.path.join(LOCAL_UPLOAD_DIR, safe_name)
    with open(path, "wb") as f:
        f.write(data)
    return f"/files/local/{safe_name}"
