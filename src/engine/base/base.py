# src/engine/base/base.py

import uuid
from engine.base.runtime_log import RuntimeLog

# 定义基础类
class Base:
    # 定义模版校验错误的类
    class TemplateError(Exception):
        def __init__(self, errors):
            super().__init__("Template 格式校验失败")
            self.errors = errors
    # 定义值校验错误类
    class ParameterError(Exception):
        def __init__(self, errors):
            super().__init__("参数格式校验失败")
            self.errors = errors

    # 定义参数类型种类
    PARAMETER_TYPE = [
        'string',         # 字符串
        'number',         # 数字（含 int/float/decimal）
        'bool',           # 布尔值
        'array-number',   # 数字数组
        'array-vector',   # 表征向量或embedding
        'array-string',   # 字符串数组
        'array-object',   # 对象数组
        'object',         # 对象 / 结构体
        # 'file',            # 文件（可以是任何类型的文件，路径或URI）
        # 'audio',           # 声音（可以处理音频文件，支持多种操作如切割、合成等）
        # 'image',           # 图片（处理图像，支持多种操作如滤镜、裁剪等）
        # 'video'            # 视频（处理视频文件，支持多种操作如剪辑、拼接等）
    ]

    # 构造函数赋值
    def __init__(self, template_id, task_id=None, parent_run_id=None):
        # 确定当前模块类型
        self.class_name = "base"

        # 定义提示模版
        self.template_id = template_id
        self.template = {} 

        # 定义运行时id参数，用于记录每一次运行状态
        self.task_id = task_id
        self.parent_run_id = parent_run_id
        self.run_id = None # 需要在run函数进行赋值，如果有重试模式，可能有多个run_id

        self.runtime_log = None

        # 获取当前类名作为class_name
        class_name = self.__class__.__name__
        # 转换成小写，因为文件名和mongoDB默认用小写标记类
        self.class_name = class_name.lower()

        self._load_template()
        
    # 加载模板和校验模板
    def _load_template(self):
        from engine.base.template_loader import TemplateLoader
        template = TemplateLoader.load_template(self.class_name, self.template_id)
        self.template = self.validate_template(template)

############## 执行相关逻辑 ##############

    # 运行的主体方法
    def run(self, inputs, run_id=None):
        # 设置运行时id
        if run_id:
            self.run_id = run_id
        # 如果未传入则自动生成
        else:
            self.run_id = str(uuid.uuid4())
        # 如果是任务类运行时将自己的运行ID设置为任务ID
        if self.class_name == "task":
            self.task_id = self.run_id
        # 开始记录运行时日志
        self.runtime_log = RuntimeLog(self.template_id, self.class_name, self.run_id, self.task_id, self.parent_run_id, inputs)

        # 开始执行
        try:
            # 获取合法输入如果没有输入需要模板填充默认值，并校验是否合法，合法继续，不合法报错
            validated_inputs = self._validate_param(self.template["inputs"], inputs, "输入")
            # 开始运行打赢log记录输入
            self.runtime_log.add_record(f"当前任务 {self.run_id} 开始执行，实际使用的输入参数：{validated_inputs}")
            # 执行函数需要子类重载实现，根据输入获取输出
            outputs = self._execute(validated_inputs)
            # 打赢log记录输入
            self.runtime_log.add_record(f"当前任务 {self.run_id} 执行完毕，运行获得的返回参数：{outputs}")
            # 根据返回的outputs判断是否有没生成的，再填充默认值，并校验是否合法，不合法报错，合法则返回。
            validated_outputs = self._validate_param(self.template["outputs"], outputs, "输出")
        except self.TemplateError as te:
            errors_list = [f"{error}" for error in te.errors]
            errors_output = "模板验证失败，错误信息如下：\n" + "\n".join(errors_list)
            self.runtime_log.mark_as_failed(errors_output)
            raise te
        except self.ParameterError as pe:
            errors_list = [f"{error}" for error in pe.errors]
            errors_output = "参数校验失败，错误信息如下：\n" + "\n".join(errors_list)
            self.runtime_log.mark_as_failed(errors_output)
            raise pe
        except Exception as exc:
            self.runtime_log.mark_as_failed(exc)
            # 继续向上抛出异常错误
            raise exc
        
        # 成功运行完成，打印log
        self.runtime_log.mark_as_complete(validated_outputs)
        # 返回输出参数
        return validated_outputs

    # 子类实现的具体执行逻辑
    def _execute(self,inputs):
        return {}

############## 基础参数类型校验相关逻辑 ##############
    # 校验参数的具体类型
    @staticmethod
    def _infer_canonical_type(value):
    # 数字判定（不把 bool 当数字）
        def _is_number(v):
            return isinstance(v, (int, float)) and not isinstance(v, bool)

        if isinstance(value, str):
            return 'string'
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return 'number'
        if isinstance(value, bool):
            return 'bool'
        if isinstance(value, dict) or hasattr(value, '__dict__'):
            return 'object'
        if isinstance(value, (list, tuple)):
            if len(value) == 0:
                return None  # 空数组语义不明确 -> 未定义类型
            # 全为数字
            if all(_is_number(x) for x in value):
                return 'array-number'
            # 全为字符串
            if all(isinstance(x, str) for x in value):
                return 'array-string'
            # 全为 dict
            if all(isinstance(x, dict) for x in value):
                return 'array-object'
            # 其它混合类型无法映射到已定义的类型
            return None

        # 其它类型无法映射
        return None

    @classmethod
    def _validate_value_type(cls, value, expected_type):
        """
        校验 value 是否符合 expected_type（expected_type 已保证是 PARAMETER_TYPE 之一）。
        报错格式（TypeError）严格按照跨平台规范：
          "期望参数类型是 {expected_type}, 实际类型是 {actual_type_name_or_未定义类型}"
        返回 True 表示通过校验。
        """
        actual = cls._infer_canonical_type(value)
        if actual is None:
            # 未能映射到已定义类型
            raise TypeError(f"期望参数类型是 {expected_type}, 实际类型是 未定义类型")

        # 对于 array-vector：允许数字数组通过（因为底层两者数据结构相同）
        if expected_type == 'array-vector' and actual == 'array-number':
            return True

        if expected_type == actual:
            return True

        # 不匹配
        raise TypeError(f"期望参数类型是 {expected_type}, 实际类型是 {actual}")

############## 提示模板相关逻辑 ##############

    # 获取提示模板
    def get_template(self):
        return self.template

    # 校验模板是否合法，需要在后续继承的子类重写，且每个具体的类会增加自己的校验方案，且不需要实例化也能调用
    @classmethod
    def validate_template(cls, template):
        errors = []  # 用于记录所有校验错误
        validated_template = {}  # 用于存储验证通过的字段

        # 首先检查是否是字典，不是则直接返回报错
        if not isinstance(template, dict):
            errors.append("模板必须是一个对象。")
            raise cls.TemplateError(errors)

        # 检查模板名字是否存在且是字符串
        if "name" not in template:
            errors.append("模板必须包含 'name' 字段。")
        elif template["name"] is None or not isinstance(template["name"], str):
            errors.append("'name' 必须是一个字符串。")
        else:
            validated_template["name"] = template["name"]

        # 检查描述是否存在且是字符串
        if "description" not in template:
            errors.append("模板必须包含 'description' 字段。")
        elif template["description"] is None or not isinstance(template["description"], str):
            errors.append("'description' 必须是一个字符串。")
        else:
            validated_template["description"] = template["description"]

        # 检查输入参数是否合法
        try:
            if "inputs" in template and template["inputs"] != None:
                validated_template["inputs"] = cls.validate_template_params(template["inputs"])
            else: 
                errors.append("模板必须包含 'inputs' 字段。")
        except cls.TemplateError as e:
            error_messages = '\n'.join(f'{e}' for e in e.errors)
            errors.append(f"'inputs' 字段存在错误：{error_messages}")

        # 检查输出参数是否合法
        try:
            if "outputs" in template and template["outputs"] != None:
                validated_template["outputs"] = cls.validate_template_params(template["outputs"])
            else:
                errors.append("模板必须包含 'outputs' 字段。")
        except cls.TemplateError as e:
            error_messages = '\n'.join(str(error) for error in e.errors)
            errors.append(f"'outputs' 字段存在错误：{error_messages}")

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise cls.TemplateError(errors)

        return validated_template

############## 提示模板校验相关函数 ##############
    # 校验参数列表
    @classmethod
    def validate_template_params(cls,params):
        errors = [] # 用于记录所有校验错误
        validated_params = [] # 用于存储验证通过的字段

        # 首先检查是否是字典，不是则直接返回报错
        if not isinstance(params, list):
            errors.append("该值必须是一个参数列表。")
            raise cls.TemplateError(errors)

        # 循环校验每个参数
        for item in params:
            try:
                validated_params.append(cls.validate_template_params_item(item))
            except cls.TemplateError as e:
                errors.extend(e.errors)

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise cls.TemplateError(errors)

        return validated_params

    # 校验参数内容
    @classmethod
    def validate_template_params_item(cls,item):
        errors = [] # 用于记录所有校验错误
        validated_item = {} # 用于记录所有校验错误

        if not isinstance(item, dict):
            errors.append("参数必须是一个结构对象。")
            raise cls.TemplateError(errors)

        # 校验参数名字字段必须存在且是字符串
        if "name" not in item:
            errors.append("该参数必须包含 'name' 字段。")
        elif item["name"] is None or not isinstance(item["name"], str):
            errors.append("该参数的 'name' 必须是一个字符串。")
        else:
            validated_item["name"] = item["name"]

        # 保存参数名字，用于打印错误日志
        param_name = validated_item.get("name", "<unknown>")

        # 校验参数描述字段必须存在且是字符串
        if 'description' not in item:
            errors.append(f"'{param_name}' 参数必须包含 'description' 字段。")
        elif item["description"] is None or not isinstance(item["description"], str):
            errors.append(f"'{param_name}' 参数的 'description' 必须是一个字符串。")
        else:
            validated_item["description"] = item["description"]

        # 校验参数的类型字段是否存在且符合字段定义
        if "type" not in item:
            errors.append(f"'{param_name}' 参数必须包含 'type' 字段。")
        elif item["type"] is None or not isinstance(item["type"], str):
            errors.append(f"'{param_name}' 参数的 'type' 必须是有效的字符串类型。")
        elif item["type"] not in cls.PARAMETER_TYPE:
            base_types = ', '.join(f'{t}' for t in cls.PARAMETER_TYPE)
            errors.append(f"'{param_name}' 参数的 'type' 必须是 {base_types} 的一种。")
        else:
            validated_item["type"] = item["type"]
        
        # 获取定义的值
        item_type = validated_item.get("type","string")

        # 校验缺损值符合参数的类型定义
        if "default" in item and item["default"] != None:
            try:
                cls._validate_value_type(item["default"],item_type)
                validated_item["default"] = item["default"]
            except TypeError as e:
                errors.append(f"'{param_name}' 参数的 'default' 错误：{str(e)}")

        if errors:
            raise cls.TemplateError(errors)

        return validated_item

############## 运行时参数校验相关逻辑 ##############
    # 通用参数校验方法，保证是模板定义的参数，不多不少，类型准确
    def _validate_param(self, template_params, actual_params, param_type):
        errors = []
        validated_params = {}  # 存放校验过后的参数
        
        for param in template_params:
            name = param['name']
            expected_type = param['type']
            default_value = param.get('default', None)
            
            # 检查实际参数中是否有该字段
            if name in actual_params:
                value = actual_params[name]
            elif default_value is not None:
                value = default_value
            else:
                errors.append(f"{param_type}缺少参数: {name}")
                continue

            # 校验参数类型
            try:
                self._validate_value_type(value, expected_type)
                validated_params[name] = value
            except TypeError as e:
                errors.append(f" {param_type} 参数类型不匹配: {name} ({str(e)})")
        
        if errors:
            raise self.ParameterError(errors)
        
        return validated_params  # 返回校验过后的参数字典