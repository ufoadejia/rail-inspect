"""缺陷识别服务：多模态大模型 + 少样本提示工程。

核心思路：
1. 构造带缺陷图谱示例的 prompt（few-shot），让大模型按统一 JSON 格式输出
2. 对超声波 A 扫等专业图像，可先用传统 CV 做 ROI 提取（此处预留接口）
3. 结合缺陷当量 dB 值，按规程阈值判级
"""
import json
from loguru import logger
from app.services.llm_client import llm_client
from app.models.schemas import DefectType, grade_defect


# 少样本示例：每个缺陷类型一张代表图 + 标注（实际用真实图 URL 替换）
FEW_SHOT_EXAMPLES = [
    {
        "image": "data:image/png;base64,PLACEHOLDER_NUCLEAR",  # TODO: 换真实核伤图谱
        "answer": {"defect_type": "nuclear", "db_value": 31.0,
                   "description": "轨头中部核伤，回波当量31dB，达重伤标准。"},
    },
    {
        "image": "data:image/png;base64,PLACEHOLDER_BOLT_HOLE",
        "answer": {"defect_type": "bolt_hole", "db_value": 25.5,
                   "description": "螺孔下沿水平裂纹，回波当量25.5dB，轻伤。"},
    },
]

SYSTEM_PROMPT = """你是铁路钢轨探伤领域的资深专家。请根据上传的探伤图像判断缺陷情况。

要求：
1. 严格按照给定 JSON 格式输出，不要输出任何其他内容
2. defect_type 取值：nuclear(核伤)/bolt_hole(螺孔裂纹)/longitudinal(纵向裂纹)/spalling(剥离)/wear(磨耗)/corrugation(波磨)/weld(焊缝缺陷)/surface(表面擦伤)/normal(正常)
3. db_value 为缺陷回波当量(dB)，无缺陷填 null
4. description 用中文简要描述缺陷位置和特征

输出格式：
{"defect_type": "...", "db_value": 数字或null, "description": "..."}"""


async def detect_defect(image_url: str, image_type: str = "surface") -> dict:
    """识别单张探伤图像。

    Args:
        image_url: 图片可访问 URL（或 base64 data URI）
        image_type: surface(表面照片)/a_scan/b_scan/c_scan
    Returns:
        {defect_type, defect_grade, db_value, confidence, description}
    """
    logger.info("开始识别图片 type={} url={}", image_type, image_url[:60])

    # 构造多模态消息（few-shot + 待识别图）
    content: list[dict] = []
    for ex in FEW_SHOT_EXAMPLES:
        content.append({"type": "image_url", "image_url": {"url": ex["image"]}})
        content.append({"type": "text", "text": f"示例：{json.dumps(ex['answer'], ensure_ascii=False)}"})
    content.append({"type": "image_url", "image_url": {"url": image_url}})
    content.append({"type": "text", "text": "请判断上图缺陷，按格式输出 JSON。"})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]

    raw = await llm_client.vision_chat(messages)
    try:
        result = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        logger.error("模型返回非 JSON：{}", raw[:200])
        result = {"defect_type": "normal", "db_value": None, "description": "解析失败"}

    # 判级
    defect_type = result.get("defect_type", "normal")
    try:
        defect_type_enum = DefectType(defect_type)
    except ValueError:
        defect_type_enum = DefectType.NORMAL
    db_value = result.get("db_value")
    grade = grade_defect(defect_type_enum, db_value)

    return {
        "defect_type": defect_type,
        "defect_type_cn": {"nuclear": "钢轨核伤", "bolt_hole": "螺孔裂纹", "longitudinal": "纵向裂纹",
                            "spalling": "轨头剥离", "wear": "钢轨磨耗", "corrugation": "波形磨耗",
                            "weld": "焊缝缺陷", "surface": "表面擦伤/压溃", "normal": "正常"}.get(defect_type, defect_type),
        "defect_grade": grade,
        "db_value": db_value,
        "confidence": result.get("confidence", 0.8),
        "description": result.get("description", ""),
    }


# ===== 专业图像预处理（A 扫 ROI 提取）预留 =====
def preprocess_a_scan(image_bytes: bytes) -> bytes:
    """对超声波 A 型显示图做 ROI 提取后再喂大模型，提升稳定性。

    TODO: 用 OpenCV 形态学/阈值定位回波包络区域裁剪。
    """
    return image_bytes
