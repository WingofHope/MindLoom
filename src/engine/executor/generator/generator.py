# src/engine/executor/generator/generator.py

import re

from config import root_path
from engine.executor.executor import Executor

class Generator(Executor):
    # 定义大语言模型有多少种模式
    LLM_MODE_TYPE = ['chat','image','vision','completion','audio','speech','transcription','embedding','moderation','reasoning']

    # 定义模板变量填充模式
    PARSE_MODE_TYPE = ['static','jinjia2','regex']

    # 定义提取模式类型
    EXTRACT_MODE_TYPE = ['regex', 'json', 'xml', 'yaml']

    # 构造函数直接调用父类的构造函数加载模板和校验模板
    def __init__(self, template_id, secret=None, task_id=None, parent_run_id=None):
        super().__init__(template_id, secret, task_id, parent_run_id)

############## 执行相关逻辑 ##############

    # 重写执行方法
    def _execute(self, inputs):
        if self.template_id == "generate_planning0001":
            outputs = {
                "thinking": "用户在北京出差，期望下班后去逛后海，因此这是一个活动出行类的问题。根据用户提供的时间（每天下班时间是18:00），需要为其推荐合适的活动行程规划。后海是适合晚上游玩的地方，可以考虑天气因素来判断最合适的出行时间。所以我需要查看接下来几天的天气情况，看哪天适合去。",
                "is_weather_api": "是",
                "answer": "稍等，我正在查阅后海的天气信息，以便给你推荐合适的出行时间和活动安排。",
                "location": "Beijin",
                "start": 0,
                "days": 3,
            }
            return outputs
        elif self.template_id == "generate_planning0002":
            outputs = {
                "answer": "嘿，出差之余还想着后海浪一圈，懂享受！看天气，后天晴朗又不冷，最适合！下班后直接奔后海，7点到，先沿湖溜达拍夜景，再找家湖边小酒吧，热饮配夜风，倍儿惬意！带条围巾，别玩太晚，工作浪两不误！"
            }
            return outputs
        return {}

############## 提示模板相关逻辑 ##############

    # 校验提示模板是否合法
    @classmethod
    def validate_template(cls, template):
        errors = []  # 用于记录所有校验错误
        validated_template = {}  # 用于存储验证通过的字段

        # 调用父类的 validate_template 方法，进行基础的模板校验
        try:
            validated_template = super().validate_template(template)
        except cls.TemplateError as base_errors:
            # 从父类校验中收集错误
            errors.extend(base_errors.errors)

        # 判断 template 存在
        if "template" not in template:
            errors.append(f"Genetor 模板必须包含 'template'。")
            raise cls.TemplateError(errors)

        # 获取 outputs 的 names，方便后续validate_extract校验使用
        if "outputs" in validated_template:
            output_names = [output["name"] for output in validated_template["outputs"]]
        else:
            output_names = None

        # 校验整个模板中的 'template' 字段合法
        try:
            validated_template["template"] = Generator.validate_template_field(template["template"],output_names)
        except cls.TemplateError as e:
            errors.extend(e.errors)

        if errors:
            raise cls.TemplateError(errors)

        # 返回经过验证的模板
        return validated_template

############## 提示模板校验相关函数 ##############

    # 校验整个模板中的 'template' 字段是否存在且是字典，并且校验字段
    @staticmethod
    def validate_template_field(template_dict,output_names):
        errors = []
        validated_template_dict = {}  # 用于存储验证通过的字段

        # 首先检查是否有 'template' 字段且是字典
        if not isinstance(template_dict, dict):
            errors.append("Genetor 模板中的 'template' 字段必须是一个字典。")
            raise Generator.TemplateError(errors)

        # 校验 'llm' 字段
        try:
            if "llm" in template_dict:
                validated_template_dict["llm"] = Generator.validate_llm(template_dict["llm"])
            else:
                errors.append("Genetor 模板中的 'template' 必须包含 'llm' 字段。")
        except Generator.TemplateError as e:
            errors.extend(e.errors)

        # 校验 'parse' 字段
        try:
            if "parse" in template_dict:
                validated_template_dict["parse"] = Generator.validate_parse(template_dict["parse"])
            else:
                errors.append("Genetor 模板中的 'template' 必须包含 'parse' 字段。")
        except Generator.TemplateError as e:
            errors.extend(e.errors)

        # 校验 'post_body' 字段
        try:
            if "post_body" in template_dict:
                validated_template_dict["post_body"] = Generator.validate_post_body(template_dict["post_body"])
            else:
                errors.append("Genetor 模板中的 'template' 必须包含 'post_body' 字段。")
        except Generator.TemplateError as e:
            errors.extend(e.errors)

        # 校验 'extract' 字段
        try:
            if "extract" in template_dict:
                validated_template_dict["extract"] = Generator.validate_extract(template_dict["extract"],output_names)
            else:
                errors.append("Genetor 模板中的 'template' 必须包含 'extract' 字段。")
        except Generator.TemplateError as e:
            errors.extend(e.errors)

        # 校验 'assert' 字段（如果存在）
        try:
            if "assert" in template_dict:
                validated_template_dict["assert"] = Generator.validate_assert(template_dict["assert"])
        except Generator.TemplateError as e:
            errors.extend(e.errors)

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise Generator.TemplateError(errors)

        # 返回经过验证的 template 字段
        return validated_template_dict

    # 校验 `llm` 字段
    @staticmethod
    def validate_llm(llm):
        errors = []
        validated_llm = {}  # 用于存储验证通过的字段

        if not isinstance(llm, dict):
            errors.append("Genetor 模板中的 'template' -> 'llm' 字段必须是一个结构对象。")
            raise Generator.TemplateError(errors)

        # 校验 mode
        if "mode" not in llm or not isinstance(llm["mode"], str):
            errors.append("Genetor 模板中的 'template' -> 'llm' 必须包含有效的 'mode'（字符串）。")
        elif llm["mode"] not in Generator.LLM_MODE_TYPE:
            errors.append("Genetor 模板中的 'template' -> 'llm' -> 'mode' 不是有效值。")
        else:
            validated_llm["mode"] = llm["mode"]

        # 校验 provider
        if "provider" in llm and not isinstance(llm["provider"], str):
            errors.append("Genetor 模板中的 'template' -> 'llm' -> 'provider' 字段必须是字符串。")
        else:
            validated_llm["provider"] = llm.get("provider")

        # 校验 model
        if "model" in llm and not isinstance(llm["model"], str):
            errors.append("Genetor 模板中的 'template' -> 'llm' -> 'model' 字段必须是字符串。")
        else:
            validated_llm["model"] = llm.get("model")

        # 校验 version
        if "version" in llm and not isinstance(llm["version"], str):
            errors.append("Genetor 模板中的 'template' -> 'llm' 字段必须包含有效的 'version'（字符串）。")
        else:
            validated_llm["version"] = llm.get("version")

        # 校验 url
        if "url" not in llm or not isinstance(llm["url"], str):
            errors.append("Genetor 模板中的 'template' -> 'llm' 字段必须包含有效的 'url'（字符串）。")
        else:
            url = llm["url"]
            # 定义一个基本的URL正则表达式模式
            regex = re.compile(
                r'^(?:http)s?://'  # http:// 或 https://
                r'(?:'  # 开始非捕获分组
                r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # 域名...
                r'localhost|'  # ...或 localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...或 IPv4
                r'$[A-F0-9]*:[A-F0-9:]+$'  # ...或 IPv6 (用方括号包围)
                r')'
                r'(?::\d+)?'  # 可选端口
                r'(?:/?|[/?]\S+)$', re.IGNORECASE | re.VERBOSE)
            
            # 检查URL是否符合正则表达式模式
            if re.match(regex, url) is None:
                errors.append(f"Genetor 模板中的 'template' -> 'llm' -> 'url' 不是有效的URL值。")
            else:
                validated_llm["url"] = llm["url"]

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise Generator.TemplateError(errors)

        return validated_llm

    # 校验 `parse` 字段
    @staticmethod
    def validate_parse(parse):
        errors = []
        validated_parse = {}

        if not isinstance(parse, dict):
            errors.append("Genetor 模版中 'template' -> 'parse' 字段必须是一个结构对象。")
            raise Generator.TemplateError(errors)

        # 校验 mode 字段是否存在并且是有效值
        if "mode" not in parse:
            errors.append("Genetor 模版中 'template' -> 'parse' 必须包含 'mode' 字段。")
        elif parse["mode"] not in Generator.PARSE_MODE_TYPE:
            errors.append("'template' -> 'parse' 的 'mode' 字段必须是 'static'、'jinja2' 或 'regex' 中的一个。")
        else:
            validated_parse["mode"] = parse["mode"]  # 校验通过，保存 mode

        # 如果 mode 是 'static'，校验 placeholder_format
        if "mode" in validated_parse and validated_parse["mode"] == "static":
            if "placeholder_format" not in parse:
                errors.append("Genetor 模版中 'template' -> 'parse' 中如果 'mode' 为 'static'，必须包含 'placeholder_format' 字段。")
            else:
                placeholder_format = parse["placeholder_format"]
                # 校验 placeholder_format 格式是否正确
                if not isinstance(placeholder_format, str):
                    errors.append("Genetor 模版中 'template' -> 'parse' 中的 'placeholder_format' 必须是一个字符串。")
                else:
                    validated_parse["placeholder_format"] = placeholder_format  # 校验通过，保存 placeholder_format

        # 对于其他 mode（'jinja2' 和 'regex'），暂时不做进一步校验
        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise Generator.TemplateError(errors)

        return validated_parse

    # 校验 `post_body` 字段
    @staticmethod
    def validate_post_body(post_body):
        errors = []
        if not isinstance(post_body, dict):
            errors.append("Genetor 模版中 'template' -> 'post_body' 字段必须是一个结构对象。")
            raise Generator.TemplateError(errors)
        return post_body

    # 校验 `extract` 字段
    @staticmethod
    def validate_extract(extract, output_names):
        errors = []
        validated_extract = {}

        # 校验 extract 是否为字典
        if not isinstance(extract, dict):
            errors.append("Genetor 模版中 'template' -> 'extract' 字段必须是一个结构对象。")
            raise Generator.TemplateError(errors)

        # 校验 mode 字段是否存在并且是有效值
        if "mode" not in extract:
            errors.append("Genetor 模版中 'template' -> 'extract' 必须包含 'mode' 字段。")
        elif extract["mode"] not in Generator.EXTRACT_MODE_TYPE:
            errors.append("'template' -> 'extract' 的 'mode' 字段必须是 'regex'、'json'、'xml' 或 'yaml' 中的一个。")
        else:
            validated_extract["mode"] = extract["mode"]  # 校验通过，保存 mode

        # 校验 rules 字段
        if "rules" not in extract:
            errors.append("Genetor 模版中 'template' -> 'extract' 必须包含 'rules' 字段。")
        elif not isinstance(extract["rules"], list):
            errors.append("Genetor 模版中 'template' -> 'extract' -> 'rules' 字段必须是一个列表。")
        elif output_names != None:
            validated_extract["rules"] = list()

            # 校验每个 rule 的 variable 是否在 outputs 中的 name 中
            rules_variables = []
            for rule in extract["rules"]:
                validated_rule = dict()
                if not isinstance(rule, dict):
                    errors.append("Genetor 模版中 'template' -> 'extract' 的每个 'rules' 元素必须是一个字典。")
                    continue

                # 校验每个规则中的 variable 和提取方式
                if "variable" not in rule:
                    errors.append("Genetor 模版中 'template' -> 'extract' 的每个 'rule' 必须包含 'variable' 字段。")
                else:
                    variable = rule["variable"]
                    # 确保 variable 在 outputs 中存在
                    if variable not in output_names:
                        errors.append(f"Genetor 模版中 'template' -> 'extract' 中的 'variable' '{variable}' 必须与 'outputs' 中的字段一致。")
                    else:
                        validated_rule["variable"] = variable
                        rules_variables.append(variable)

                # 根据 mode 校验相应的提取方式
                mode = extract["mode"]
                if mode == "regex":
                    if "regex" not in rule:
                        errors.append(f"Genetor 模版中 'template' -> 'extract' 中 'mode' 为 'regex' 的规则必须包含 'regex' 字段。")
                    else:
                        # 校验 regex 是否有效
                        try:
                            re.compile(rule["regex"])
                        except re.error:
                            errors.append(f"Genetor 模版中 'template' -> 'extract' 中 'regex' 字段的值 '{rule['regex']}' 不是有效的正则表达式。")
                    validated_rule["regex"] = rule["regex"]
                elif mode in ["json", "xml", "yaml"]:
                    if "path" not in rule:
                        errors.append(f"Genetor 模版中 'template' -> 'extract' 中 'mode' 为 '{mode}' 的规则必须包含 'path' 字段。")
                    else:
                        pass
                    validated_rule["path"] = rule["path"]
                # 添加校验通过的rule字段
                validated_extract["rules"].append(validated_rule)
            # 校验 outputs 中的每个 name 是否在 rules 中找到对应的 variable
            for output_name in output_names:
                if output_name not in rules_variables:
                    errors.append(f"Genetor 模版中 'template' -> 'outputs' 中的 'name' '{output_name}' 必须在 'extract.rules' 中找到对应的 'variable'。")

        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise Generator.TemplateError(errors)

        return validated_extract

    # 校验 `assert` 字段
    @staticmethod
    def validate_assert(assert_data):
        errors = []
        if not isinstance(assert_data, dict):
            errors.append("Genetor 模版中 'template' -> 'assert_data' 字段必须是一个结构对象。")
            raise Generator.TemplateError(errors)
        return assert_data