# tests/generator_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.executor.generator.generator import Generator

class TestTask(unittest.TestCase):
    # def test_run_case2(self):
    #     gen_id = 'generate_planning0001'
    #     secret = None
    #     inputs = {
    #         'question':'我想去桂林',
    #         'GNSS_address':'上海市徐汇区龙水南路龙南三村',
    #         'local_time_string':'2024-12-17 16:50:42 Tuesday UTC+08:00+0800'
    #     }
    #     # gen_instance = Generator(gen_id, secret)
    #     try:
    #         gen_instance = Generator(gen_id, secret)
    #         print(f"结果1如下：{gen_instance.get_template()}")
    #         result = gen_instance.run(inputs)
    #         print(f"结果2如下：{result}")
    #     except Generator.TemplateError as e:
    #         print("模板验证失败，错误信息如下：")
    #         for error in e.errors:
    #             print(f"- {error}")
    #     except Generator.ParameterError as e:
    #         print("参数校验失败，错误信息如下：")
    #         for error in e.errors:
    #             print(f"- {error}")
    #     except Exception as e:
    #         print(e)
    def test_run_case2(self):
        gen_id = 'generate_test0001'
        secret = None
        inputs = {
            'question':'王总股权转让100万，该交多少税'
        }
        # gen_instance = Generator(gen_id, secret)
        try:
            print("断点1")
            gen_instance = Generator(gen_id, secret)
            print("断点2")
            print(f"结果1如下：{gen_instance.get_template()}")
            result = gen_instance.run(inputs)
            print(f"结果2如下：{result}")
        except Generator.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Generator.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            print(e)

if __name__ == '__main__':
    unittest.main()