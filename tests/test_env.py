import sys

def test_environment_ready():
    """测试 Python 版本和框架基本运行"""
    assert sys.version_info >= (3, 10), f"Current python version is {sys.version_info}"
    assert True, "环境正常"
