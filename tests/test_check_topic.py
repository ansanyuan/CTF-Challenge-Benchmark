import os
import pytest
from pathlib import Path

from scripts.valid_hive_reward_json import validate_hive_reward_json


def find_project_root(start_path: Path) -> Path:
    """
    自动查找项目根目录（假设根目录包含 setup.py）
    """
    for parent in start_path.parents:
        if (parent / "setup.py").exists():
            return parent
    raise RuntimeError("无法找到项目根目录，请确保当前目录在项目结构内")


def find_hive_reward_files():
    """
    从项目根目录递归查找所有 .hive-reward.json 文件
    """
    current_file = Path(__file__).resolve()
    print(f"debug: 当前文件路径: {current_file}")

    # 查找项目根目录（假设根目录包含 setup.py）
    project_root = find_project_root(current_file)
    print(f"debug: 项目根目录: {project_root}")

    # 递归查找所有 .hive-reward.json 文件
    reward_files = list(project_root.rglob("*.hive-reward.json"))
    print(f"debug: 找到的文件数量: {len(reward_files)}")

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
