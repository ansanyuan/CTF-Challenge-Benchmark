import pytest
import os
import sys


def run_tests():
    """
    运行测试
    """
    test_dir = os.path.join("tests")
    sys.exit(pytest.main([test_dir]))
