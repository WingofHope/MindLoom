# tests/tools_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.executor.tool.tool import Tool
from engine.executor.tool.tool_manager import tool_manager as tm

class TestFetchWebsiteText(unittest.TestCase):
    def test_fetch_website_text(self):
        tool_id = 'search.search_url2text_static'
        secret = None
        inputs = {
            'url': 'https://www.baidu.com/'
        }
        try:
            tool_instance = Tool(tool_id, secret)
            result = tool_instance.run(inputs)
            print(result)
            self.assertIn('text', result)
            self.assertIsInstance(result['text'], str)
        except Tool.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Tool.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            print(f"测试过程中发生异常：{e}")
            self.fail("测试失败，发生异常")

if __name__ == '__main__':
    unittest.main()