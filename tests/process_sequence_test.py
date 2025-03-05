# tests/process_sequence_test.py

import traceback
import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.scheduler.process.process import Process

class TestTask(unittest.TestCase):
    def test_run_case(self):
        process_id = 'process_template_test'
        secret = None
        inputs = {'input':"我在北京出差，会待一周，每天晚上6点下班，希望下班去逛后海，有啥推荐吗?哪天去合适？"}
        try:
            tool_instance = Process(process_id, secret)
            result = tool_instance.run(inputs)
            print(result)
        except Process.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Process.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            traceback.print_exc()

if __name__ == '__main__':
    unittest.main()