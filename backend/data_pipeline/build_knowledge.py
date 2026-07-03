"""知识库构建脚本：将合成/真实数据向量化并入库。

用法：
    cd backend
    python data_pipeline/build_knowledge.py

真实资料接入时，在 knowledge/raw/ 下放 PDF/Word/图片，
扩展本脚本的 load_xxx 函数即可。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from app.services.embedding import embed_text, embed_image
from app.services.vector_store import insert, flush, init_collection
from data_pipeline.synthetic_data import all_chunks


def build_from_synthetic():
    """从合成数据构建知识库。"""
    init_collection()
    chunks = all_chunks()
    logger.info("共 {} 条知识片段待入库", len(chunks))
    for i, ch in enumerate(chunks, 1):
        text_vec = embed_text(f"{ch.title} {ch.content}")
        image_vec = embed_image(ch.image_url) if ch.image_url else None
        insert(
            {"doc_type": ch.doc_type, "source": ch.source,
             "title": ch.title, "content": ch.content, "image_url": ch.image_url},
            text_vec, image_vec,
        )
        logger.info("[{}/{}] 已入库：{}", i, len(chunks), ch.title)
    flush()
    logger.info("知识库构建完成，共 {} 条", len(chunks))


def build_from_raw_dir(raw_dir: str = "knowledge/raw"):
    """从 raw 目录加载真实资料（PDF/Word/图片）。

    TODO: 实现真实文档解析，此处预留。
    - PDF/Word → unstructured 解析 → 分块
    - 图片 → Qwen-VL 生成描述 + CLIP 向量
    - 表格 → 结构化 + 自然语言描述
    """
    if not os.path.exists(raw_dir):
        logger.info("未找到 {}，跳过真实资料（使用合成数据）", raw_dir)
        return
    logger.warning("真实资料解析待实现，请参考 TODO 扩展。当前仅使用合成数据。")


if __name__ == "__main__":
    build_from_raw_dir()
    build_from_synthetic()
