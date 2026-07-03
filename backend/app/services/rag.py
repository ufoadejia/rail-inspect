"""跨模态 RAG 检索 + 答案生成（带引用溯源）。

流程：
  query → 双路召回(文本+图像) → RRF 融合 → 大模型生成(引用来源)
"""
from typing import Optional, List
from loguru import logger
from app.services.embedding import embed_text, embed_image
from app.services.vector_store import search_text, search_image
from app.services.llm_client import llm_client


def reciprocal_rank_fusion(lists: List[dict], k: int = 60) -> List[dict]:
    """RRF 融合多路召回结果。"""
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    for lst in lists:
        for rank, item in enumerate(lst):
            key = (item.get("title", "") + item.get("content", ""))[:200]
            scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
            items[key] = item
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result = []
    for key, score in ranked[:8]:
        it = items[key].copy()
        it["fused_score"] = score
        result.append(it)
    return result


async def retrieve(query: str, image_url: Optional[str] = None, topk: int = 5) -> List[dict]:
    """跨模态检索。query 文本召回 + (可选) image 图像召回。"""
    lists = []
    if query:
        qv = embed_text(query)
        lists.append(search_text(qv, topk))
    if image_url:
        iv = embed_image(image_url)
        lists.append(search_image(iv, topk))
    if not lists:
        return []
    fused = reciprocal_rank_fusion(lists) if len(lists) > 1 else lists[0]
    return fused[:topk]


async def answer_with_citations(query: str, image_url: Optional[str] = None) -> dict:
    """检索 + 生成，返回答案和引用。"""
    docs = await retrieve(query, image_url)

    if not docs:
        return {"answer": "知识库中未检索到相关内容，请先构建知识库。", "citations": [], "retrieved": []}

    # 构造带引用的 prompt
    context_blocks = []
    citations = []
    for i, d in enumerate(docs, 1):
        context_blocks.append(f"[{i}] 来源：{d.get('source','')} | {d.get('title','')}\n{d.get('content','')}")
        citations.append({
            "id": i, "source": d.get("source", ""), "title": d.get("title", ""),
            "snippet": (d.get("content", "")[:120] + "…") if d.get("content") else "",
            "image_url": d.get("image_url", ""), "score": round(d.get("fused_score", d.get("score", 0)), 4),
        })

    context = "\n\n".join(context_blocks)
    prompt = f"""你是钢轨探伤专家助手。请根据以下检索到的知识回答问题，并在每个论断后用 [编号] 标注来源。

【检索知识】
{context}

【问题】{query}

要求：
1. 回答要专业、准确、可操作
2. 每个关键结论后标注来源编号，如 ...按规程应复核探伤[1]
3. 若知识不足以回答，明确说明并建议查阅完整规程
4. 给出具体处置建议（如换轨、加固、监测等）"""

    messages = [{"role": "user", "content": prompt}]
    answer = await llm_client.text_chat(messages)

    return {"answer": answer, "citations": citations, "retrieved": docs}