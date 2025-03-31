# tests/tools_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.executor.tool.tool import Tool
from engine.executor.tool.tool_manager import tool_manager as tm

class TestTask(unittest.TestCase):

    def test_run_case(self):
        tool_id = 'local_vectordb.lookup_by_index'
        secret = None
        inputs = {
            'table_name': 'test_table',
            'index': 1
        }
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