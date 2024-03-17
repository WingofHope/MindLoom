# template version 3
# 2023/3/14
# Hou Yi, Ke edit

# Task: template fill
# read template.json and fill the input into {} and send the messages to openai
import openai
import re
import json
import os
from collections import defaultdict

openai.api_key = "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"

def template_fill(template_file, user_inputs):
    # 确保正确地构造模板文件的路径，假设新的模板存放路径为 "prompts/generator/"
    base_dir = os.path.dirname(__file__)  # 获取当前文件夹的路径
    new_template_dir = os.path.join(base_dir, "prompts", "generator")  # 新的模板目录
    template_path = os.path.join(new_template_dir, template_file)  # 构建完整路径

    # 从文件读取模板
    with open(template_path, 'r', encoding='utf-8') as file:
        template = json.load(file)

    print("模板内容:", template)  # 打印模板内容

    # 对每条消息进行处理，替换模板中的占位符
    for message in template["template"]["post_body"]["messages"]:
        for key, value in user_inputs.items():
            placeholder = "${{{}}}".format(key)
            message["content"] = message["content"].replace(placeholder, value)

        print("修改后的消息:", message["content"])  # 打印修改后的消息

    # 调用 OpenAI API
    print("OpenAI API 请求:", template["template"])  # 打印 API 请求
    response = openai.ChatCompletion.create(**template["template"]["post_body"])
    print("OpenAI API 响应:", response)  # 打印 API 响应
    content = response.choices[0].message.content
    output = defaultdict(str)

    # 解析输出，根据正则表达式提取信息
    for key, value in template["output"][0].items():
        if "regular_expression" in value:
            expression = value["regular_expression"]
            matches = re.search(expression, content, re.DOTALL)
            if matches:
                output[key] = matches.group(1).strip()
            else:
                output[key] = content

    return output



# 这里如果作为独自运行的模板可以启用，目前不需要。
# if __name__ == "__main__":
#     # 示例模板和输入数据
#     example_template = {
#         # ...定义模板结构...
#     }
#     example_inputs = {
#         "business_name": "示例行业",
#         "question": "示例问题"
#     }

#     returned_message = template_fill("example_template_file.json", example_inputs)
#     print(returned_message)

# Task: template fill
# read template.json and fill the input into {} and send the messages to openai