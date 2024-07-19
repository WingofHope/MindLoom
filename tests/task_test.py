# tests/task_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.engine.scheduler.task.task import Task

class TestTask(unittest.TestCase):
    def test_run_case1(self):
        t_id = 'task_0001'
        inputs = {
            'name' : '小C',
            'description' : '小C是曦之翼的智能AI客服，擅长处理各种AI问题，说话幽默',
            'group_name' : 'WAB测试群（7）',
            'business_name': 'nihao ',
            'question' : ''
        }
        secret = None
        try:
            task_instance = Task(t_id, secret)
            result = task_instance.run(inputs)
        except Exception as e:
            print(e)

        print(result)
        # 这里编写断言来验证 run 方法的输出是否符合预期
        # self.assertEqual(result, {})

    # def test_run_case2(self):
    #     t_id = 'task_0002'
    #     inputs = {'name': 'haha'}
    #     secret = None

    #     task_instance = Task(t_id, inputs, secret)
    #     result = task_instance.run()
    #     print(result)

    #     # 这里编写断言来验证 run 方法的输出是否符合预期
    #     # 示例断言，你需要根据具体情况调整
    #     self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
