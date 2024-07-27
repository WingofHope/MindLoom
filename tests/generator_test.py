# tests/generator_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.engine.executor.generator.generator import Generator

class TestGenerator(unittest.TestCase):
    def test_run_case1(self):
        gen_id = 'generator_0001'
        inputs = {}
        secret = None

        generator_instance = Generator(gen_id, inputs, secret)
        result = generator_instance.run()
        print(result)

        # 这里编写断言来验证 run 方法的输出是否符合预期
        self.assertEqual(result, {})

    def test_run_case2(self):
        t_id = 'generator_0002'
        inputs = {'name': 'haha'}
        secret = None

        generator_instance = Generator(t_id, inputs, secret)
        result = generator_instance.run()
        print(result)

        # 这里编写断言来验证 run 方法的输出是否符合预期
        # 示例断言，你需要根据具体情况调整
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
