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
        tool_id = 'local_vectordb.insert'
        secret = None
        inputs = {
            'table_name': 'test_table',
            'vector': [0.1, 0.2, 0.4,1.0],
            'raw_string': '测试文本',
            'metadata': {'source': 'test', 'id': 123}
        }
        try:
            tool_instance = Tool(tool_id, secret)
            result = tool_instance.run(inputs)
            print(f"case1:{result}")
        except Tool.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Tool.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
                
    def test_run_case2(self):
        tool_id = 'local_vectordb.lookup_by_index'
        secret = None
        inputs = {
            'table_name': 'test_table',
            'index': 1
        }
        try:
            tool_instance = Tool(tool_id, secret)
            result = tool_instance.run(inputs)
            print(f"case2:{result}")
        except Tool.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Tool.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")

    def test_run_case3(self):
        tool_id = 'local_vectordb.range_query'
        secret = None
        inputs = {
            "table_name": "test_table",
            "query_vector": [0.1, 0.2, 0.3,0.4],
            "similarity_threshold": 0.8
        }
        try:
            tool_instance = Tool(tool_id, secret)
            result = tool_instance.run(inputs)
            print(f"case3:{result}")
        except Tool.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Tool.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")

    def test_run_case4(self):
        print("case2：")
        tool_id = 'local_vectordb.similar_topn'
        secret = None
        inputs = {
            "table_name": "test_table",
            "query_vector": [0.1, 0.2, 0.3,0.8],
            "top_n": 3
        }
        try:
            tool_instance = Tool(tool_id, secret)
            result = tool_instance.run(inputs)
            print(f"case4:{result}")
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