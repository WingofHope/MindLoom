# src/engine/executor/generator/generator.py

import re
import yaml
import os

from engine.executor.executor import Executor

class Generator(Executor):
    # 定义大语言模型有多少种模式
    LLM_MODE_TYPE = ['chat','image','vision','completion','audio','speech','transcription','embedding','moderation','reasoning']

    # 定义模板变量填充模式
    PARSE_MODE_TYPE = ['static','jinjia2','regex']

    # 定义提取模式类型
    EXTRACT_MODE_TYPE = ['regex', 'json', 'xml', 'yaml']

    # 构造函数直接调用父类的构造函数加载模板和校验模板
    def __init__(self, template_id, task_id=None, parent_run_id=None):
        super().__init__(template_id, task_id, parent_run_id)

############## 执行相关逻辑 ##############

    # 重写执行方法
    def _execute(self, inputs):
        # 读取密钥配置
        self.secret = self._load_secret()
        
        # print("inputs: ", inputs)
        print("template: ", self.template)

        # 获取模板配置
        llm_config = self.template["template"]["llm"]
        post_body = self.template["template"]["post_body"]
        parse_config = self.template["template"]["parse"]

        # 处理模板变量替换
        if parse_config["mode"] == "static" and isinstance(post_body, dict):
            placeholder_format = parse_config["placeholder_format"]
            post_body = self._replace_variables(post_body, inputs, placeholder_format)

        # print("post_body: ", post_body)
        # 发送请求到OpenAI API
        import requests
        try:
            response = requests.post(
                llm_config["url"],
                headers={
                    "Authorization": f"Bearer {self.secret}",
                    "Content-Type": "application/json"
                },
                json=post_body,
                timeout=30,
                stream=False  # OpenAI API 支持流式响应，这里设置为 False
            )
            response.raise_for_status()
            llm_response = response.json()
            # print("llm_response:", llm_response)
            
            # 使用extract规则从响应中提取所需信息
            extract_config = self.template["template"]["extract"]
            outputs = self._extract_outputs(llm_response, extract_config)

            print("outputs:", outputs)
            return outputs
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用LLM API失败: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"处理LLM响应失败: {str(e)}")

    def _replace_variables(self, post_body, inputs, placeholder_format):
        """替换post_body字典中的模板变量"""
        result = {}
        for key, value in post_body.items():
            if isinstance(value, dict):
                result[key] = self._replace_variables(value, inputs, placeholder_format)
            elif isinstance(value, list):
                result[key] = [
                    self._replace_variables(item, inputs, placeholder_format) if isinstance(item, dict)
                    else self._replace_string_variables(item, inputs, placeholder_format) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str):
                result[key] = self._replace_string_variables(value, inputs, placeholder_format)
            else:
                result[key] = value
        return result

    def _replace_string_variables(self, text, inputs, placeholder_format):
        """替换字符串中的模板变量"""
        for var_name, var_value in inputs.items():
            placeholder = placeholder_format.replace("variable", var_name)
            if placeholder in text:
                text = text.replace(placeholder, str(var_value))
        return text

    def _load_secret(self):
        """从配置文件加载密钥"""
        try:
            # 获取项目根目录下的配置文件路径
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
                                     "config", 
                                     "secret.yaml")
            print("config_path:", config_path)
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # 获取 API 密钥
            if 'openai' not in config or 'api_key' not in config['openai']:
                raise ValueError("配置文件中缺少 openai.api_key")
                
            return config['openai']['api_key']
            
        except FileNotFoundError:
            raise RuntimeError("找不到配置文件 config/secret.yaml")
        except yaml.YAMLError as e:
            raise RuntimeError(f"解析配置文件失败: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"读取密钥配置失败: {str(e)}")

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

    def _extract_outputs(self, llm_response, extract_config):
        """从LLM响应中提取输出"""
        if extract_config["mode"] != "xml":
            raise ValueError(f"暂不支持 {extract_config['mode']} 提取模式")
        
        try:
            from lxml import etree
            
            # 从LLM响应中获取内容
            content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError("LLM响应中没有找到有效内容")

            print("content:", content)
            # 解析XML内容
            # 将内容包装在根元素中，以处理可能的多个顶级元素
            xml_content = f"<root>{content}</root>"
            tree = etree.fromstring(xml_content.encode('utf-8'))
            
            # 找到 output 节点
            output_node = tree.find("./output")
            if output_node is None:
                raise ValueError("在响应中没有找到 output 节点")
            
            # 存储提取结果
            outputs = {}
            
            # 遍历规则进行提取
            for rule in extract_config["rules"]:
                variable = rule["variable"]
                xpath = rule["path"]
                
                # 在 output 节点中使用 xpath 提取内容
                elements = output_node.xpath(xpath)
                
                if elements:
                    # 如果找到多个匹配，取第一个
                    value = elements[0] if isinstance(elements[0], str) else elements[0].text
                    # 处理可能的空值
                    value = value.strip() if value else ""
                    outputs[variable] = value
                else:
                    # 如果没有找到匹配，设置为空字符串
                    outputs[variable] = ""
                
            return outputs
            
        except etree.XMLSyntaxError as e:
            raise RuntimeError(f"XML解析错误: {str(e)}")
        except etree.XPathEvalError as e:
            raise RuntimeError(f"XPath解析错误: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"提取输出时发生错误: {str(e)}")