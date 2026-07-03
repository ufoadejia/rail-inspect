"""多模态大模型客户端：封装 Qwen-VL（云端）与 mock 两种实现。

无 DASHSCOPE_API_KEY 时自动走 mock，保证开发不阻塞。
"""
import json
import random
from typing import Any
from loguru import logger
from app.core.config import settings


def _parse_json_response(text: str) -> Any:
    """从模型回复中抽取 JSON（兼容 ```json 代码块包裹）。"""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


class LLMClient:
    """统一的大模型调用入口。"""

    async def vision_chat(self, messages: list[dict]) -> str:
        """多模态对话。messages 格式兼容 OpenAI/Qwen。"""
        if settings.use_mock or not settings.dashscope_api_key:
            return self._mock_vision(messages)
        return await self._qwen_vl_chat(messages)

    async def text_chat(self, messages: list[dict]) -> str:
        """纯文本对话。"""
        if settings.use_mock or not settings.dashscope_api_key:
            return self._mock_text(messages)
        return await self._qwen_text_chat(messages)

    # ===== Qwen-VL 云端实现 =====
    async def _qwen_vl_chat(self, messages: list[dict]) -> str:
        import dashscope
        dashscope.api_key = settings.dashscope_api_key
        # dashscope 同步接口，放到线程里异步化
        import asyncio
        loop = asyncio.get_event_loop()

        def _call():
            resp = dashscope.MultiModalConversation.call(
                model=settings.qwen_vl_model,
                messages=messages,
                result_format="message",
            )
            return resp.output.choices[0].message.content[0]["text"]

        return await loop.run_in_executor(None, _call)

    async def _qwen_text_chat(self, messages: list[dict]) -> str:
        import dashscope, asyncio
        dashscope.api_key = settings.dashscope_api_key
        loop = asyncio.get_event_loop()

        def _call():
            resp = dashscope.Generation.call(
                model=settings.qwen_text_model,
                messages=messages,
                result_format="message",
            )
            return resp.output.choices[0].message.content

        return await loop.run_in_executor(None, _call)

    # ===== Mock 实现（无 key 时） =====
    def _mock_vision(self, messages: list[dict]) -> str:
        logger.warning("使用 mock 多模态返回（未配置 DASHSCOPE_API_KEY）")
        # 随机生成一个缺陷识别结果，便于前端联调
        defects = [
            {"defect_type": "nuclear", "defect_grade": "轻伤", "db_value": 27.5, "confidence": 0.82,
             "description": "轨头内侧疑似核伤，回波当量约27.5dB，达到轻伤标准。"},
            {"defect_type": "bolt_hole", "defect_grade": "重伤", "db_value": 29.1, "confidence": 0.76,
             "description": "螺孔周边存在斜裂纹，回波当量约29.1dB，接近重伤阈值。"},
            {"defect_type": "normal", "defect_grade": "正常", "db_value": None, "confidence": 0.91,
             "description": "未发现明显缺陷回波，钢轨状态正常。"},
        ]
        result = random.choice(defects)
        return json.dumps(result, ensure_ascii=False)

    def _mock_text(self, messages: list[dict]) -> str:
        logger.warning("使用 mock 文本返回（未配置 DASHSCOPE_API_KEY）")
        user_msg = messages[-1].get("content", "") if messages else ""
        return (f"[Mock 回复] 已理解您的问题：「{user_msg[:60]}...」。"
                f"建议参照 TB/T 2975 钢轨超声波探伤技术规程执行，"
                f"对疑似伤损部位进行复核探伤并记录当量值。")


llm_client = LLMClient()
