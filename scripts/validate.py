import json
import math
import re
from pathlib import Path
from typing import Dict, List, Union


def validate_hive_reward_json(file_path: str) -> None:
    """
    校验 .hive-reward.json 文件是否符合 HIVE-REWARD-DATASET 规范

    参数:
        file_path (str): JSON 文件的路径

    异常:
        TypeError: 类型不匹配
        KeyError: 必填字段缺失
        ValueError: 内容格式错误
    """
    file_path = Path(file_path).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败: {file_path}，错误位置: {e.pos}") from e

    # 1. 校验根节点是否为字典
    if not isinstance(data, dict):
        raise TypeError(f"根节点必须为 dict，当前类型: {type(data)}")

    # 2. 校验必填字段是否存在
    if 'topic' not in data or 'checkpoint' not in data:
        missing = [f"'{k}'" for k in ['topic', 'checkpoint'] if k not in data]
        raise KeyError(f"缺少必填字段: {', '.join(missing)}")

    # 3. 校验 topic 字段
    topic = data['topic']
    if not isinstance(topic, str):
        raise TypeError(f"'topic' 必须是字符串，当前类型: {type(topic)}")

    # 4. 校验 checkpoint 字段
    checkpoints = data['checkpoint']
    if not isinstance(checkpoints, list):
        raise TypeError(f"'checkpoint' 必须是 list，当前类型: {type(checkpoints)}")
    if not checkpoints:
        raise ValueError("'checkpoint' 数组不能为空")

    total_score = 0.0
    for idx, item in enumerate(checkpoints):
        if not isinstance(item, dict):
            raise TypeError(f"'checkpoint' 中第 {idx + 1} 项必须是 dict，当前类型: {type(item)}")
        if len(item) != 1:
            raise ValueError(f"'checkpoint' 中第 {idx + 1} 项必须只有一个键值对")

        key, value = next(iter(item.items()))
        if not isinstance(key, str):
            raise TypeError(f"'checkpoint' 中第 {idx + 1} 项的键必须是字符串，当前类型: {type(key)}")
        if not isinstance(value, (int, float)):
            raise TypeError(f"'checkpoint' 中第 {idx + 1} 项的值必须是数字，当前类型: {type(value)}")

        value_float = float(value)
        if not (-1.0 <= value_float <= 1.0):
            raise ValueError(f"'checkpoint' 中第 {idx + 1} 项的值 {value_float} 不在 [-1, 1] 范围内")

        total_score += value_float

    # 5. 校验总分是否为 1（允许浮点误差）
    if not math.isclose(total_score, 1.0, rel_tol=1e-9):
        raise ValueError(f"所有 checkpoint 的加分比例总和必须为 1，当前总和为 {total_score}")

    def calc_regex_mode_reward(checkpoint: dict, response: str) -> float:
        """
        计算regex模式的奖励: checkpoint其中有正则表达式命中，加对应的分数
        """
        for restr, score in checkpoint.items():
            return score if re.search(restr, response) else 0.0

    def calc_normal_mode_reward(checkpoint: dict, response: str) -> float:
        """
        计算normal模式的奖励: checkpoint其中有关键词命中，加对应的分数
        :param checkpoint: 参考答案
        :param response: 用户答案
        """
        for keyword, score in checkpoint.items():
            return score if keyword in response else 0.0

    for i in range(len(data['checkpoint'])):
        if 'matchingmethod' in data and isinstance(data['matchingmethod'], list) and i < len(data['matchingmethod']) and data['matchingmethod'][i] == 'regex':
            calc_regex_mode_reward(data['checkpoint'][i], 'response')
        else:
            calc_normal_mode_reward(data['checkpoint'][i], 'response')
