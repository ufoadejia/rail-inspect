"""领域常量：缺陷类型、判级标准、工单状态。

参照 TB/T 2975《钢轨超声波探伤技术规程》及各铁路局探伤作业指导书整理。
"""
from enum import Enum
from typing import Optional


class DefectType(str, Enum):
    """钢轨常见缺陷类型。"""
    NUCLEAR = "nuclear"            # 钢轨核伤（内部疲劳）
    BOLT_HOLE = "bolt_hole"        # 螺孔裂纹
    LONGITUDINAL = "longitudinal"  # 纵向裂纹（水平/垂直）
    SPALLING = "spalling"          # 轨头剥离
    WEAR = "wear"                  # 钢轨磨耗（垂直/侧面）
    CORRUGATION = "corrugation"    # 波形磨耗
    WELD = "weld"                  # 焊缝缺陷
    SURFACE = "surface"            # 表面擦伤/压溃
    NORMAL = "normal"              # 正常


# 中文名称映射
DEFECT_LABELS_CN = {
    DefectType.NUCLEAR: "钢轨核伤",
    DefectType.BOLT_HOLE: "螺孔裂纹",
    DefectType.LONGITUDINAL: "纵向裂纹",
    DefectType.SPALLING: "轨头剥离",
    DefectType.WEAR: "钢轨磨耗",
    DefectType.CORRUGATION: "波形磨耗",
    DefectType.WELD: "焊缝缺陷",
    DefectType.SURFACE: "表面擦伤/压溃",
    DefectType.NORMAL: "正常",
}

# 当量 dB → 轻伤/重伤判级（示例阈值，实际以规程为准）
DEFECT_GRADE_RULES = {
    DefectType.NUCLEAR: {"light": 26, "heavy": 30},      # 回波当量 dB
    DefectType.BOLT_HOLE: {"light": 24, "heavy": 28},
    DefectType.LONGITUDINAL: {"light": 22, "heavy": 26},
    DefectType.WELD: {"light": 28, "heavy": 32},
}


def grade_defect(defect_type: DefectType, db_value: Optional[float]) -> str:
    """根据缺陷当量(dB)判级：正常/轻伤/重伤。"""
    if defect_type == DefectType.NORMAL:
        return "正常"
    rules = DEFECT_GRADE_RULES.get(defect_type)
    if not rules or db_value is None:
        return "待判定"
    if db_value >= rules["heavy"]:
        return "重伤"
    if db_value >= rules["light"]:
        return "轻伤"
    return "正常"


class WorkorderStatus(str, Enum):
    """工单状态机。"""
    CREATED = "created"        # 待派发
    ASSIGNED = "assigned"      # 已派发
    IN_PROGRESS = "in_progress"  # 作业中
    REVIEWING = "reviewing"    # 待验收
    REJECTED = "rejected"      # 验收驳回（回退到作业中）
    ARCHIVED = "archived"      # 已归档


# 允许的状态流转
STATUS_TRANSITIONS = {
    WorkorderStatus.CREATED: {WorkorderStatus.ASSIGNED},
    WorkorderStatus.ASSIGNED: {WorkorderStatus.IN_PROGRESS},
    WorkorderStatus.IN_PROGRESS: {WorkorderStatus.REVIEWING},
    WorkorderStatus.REVIEWING: {WorkorderStatus.ARCHIVED, WorkorderStatus.REJECTED},
    WorkorderStatus.REJECTED: {WorkorderStatus.IN_PROGRESS},
    WorkorderStatus.ARCHIVED: set(),
}


def can_transition(from_status: WorkorderStatus, to_status: WorkorderStatus) -> bool:
    return to_status in STATUS_TRANSITIONS.get(from_status, set())