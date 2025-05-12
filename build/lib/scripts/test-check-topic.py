import os
import pytest
from pathlib import Path

from scripts.valid_hive_reward_json import validate_hive_reward_json


def find_hive_reward_files():
    """查找当前目录下所有 .hive-reward.json 文件"""
    current_dir = Path(__file__).parent  # 或使用 os.getcwd()
    reward_files = list(current_dir.glob("*.hive-reward.json"))
    return [str(f.resolve()) for f in reward_files]


# 参数化测试：每个 .hive-reward.json 文件作为一个测试用例
@pytest.mark.parametrize("file_path", find_hive_reward_files())
def test_all_hive_reward_json_files(file_path):
    """
    验证所有 .hive-reward.json 文件是否符合规范
    """
    print(f"🔍 正在验证文件: {file_path}")
    try:
        validate_hive_reward_json(file_path)
    except Exception as e:
        pytest.fail(f"文件 {file_path} 验证失败: {e}")
