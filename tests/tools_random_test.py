# tests/tools_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.executor.tool.tool import Tool
from engine.executor.tool.tool_manager import tool_manager as tm

class TestTask(unittest.TestCase):
    # def test_run_case1(self):
        # print(tm.get_metadata('time.local_time'))

        # tool_class = tm.load_tool('calculator.add')
        # instant = tool_class()
        # inputs = {'addend':1,'augend':2}
        # print(instant.run(inputs))

        # print(tm.list_tools())
        # print(tm.export_metadata())

    def test_run_case2(self):
        tool_id = 'random.number_generator'
        secret = None
        inputs = {'min':1,'max':10}
        try:
            tool_instance = Tool(tool_id, secret)
            result = tool_instance.run(inputs)
            print(result)
        except Tool.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Tool.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")

if __name__ == '__main__':
    unittest.main()