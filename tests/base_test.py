# tests/base_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.engine.base.base import Base

class TestBase(unittest.TestCase):
    def test_run_case1(self):
        t_id = 'task_0001'
        inputs = {'小C','小C是曦之翼的智能AI客服，擅长处理各种AI问题，说话幽默','WAB测试群（7）'}
        secret = None

        base_instance = Base(t_id, secret)

        # 这里编写断言来验证 run 方法的输出是否符合预期
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
