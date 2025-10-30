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
    PARAMETER_TYPE = ['string','number','bool','array','object','vector']
    
    # 定义提示模版
    template_id = None
    template = {}

    # 定义运行时id参数
    task_id = None
    parent_run_id = None
    run_id = None

    # 定义运行时log对象
    runtime_log = None

    # 构造函数赋值
    def __init__(self, template_id, task_id=None, parent_run_id=None):
        self.template_id = template_id
        self.task_id = task_id
        self.parent_run_id = parent_run_id

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
    @staticmethod
    def validate_template_params(params):
        errors = [] # 用于记录所有校验错误
        validated_params = [] # 用于存储验证通过的字段

        # 首先检查是否是字典，不是则直接返回报错
        if not isinstance(params, list):
            errors.append("该值必须是一个参数列表。")
            raise Base.TemplateError(errors)

        # 循环校验每个参数
        for item in params:
            try:
                validated_params.append(Base.validate_template_params_item(item))
            except Base.TemplateError as e:
                errors.extend(e.errors)

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise Base.TemplateError(errors)

        return validated_params

    # 校验参数内容
    @staticmethod
    def validate_template_params_item(item):
        errors = [] # 用于记录所有校验错误
        validated_item = {} # 用于记录所有校验错误

        if not isinstance(item, dict):
            errors.append("参数必须是一个结构对象。")
            raise Base.TemplateError(errors)

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
        elif item["type"] not in Base.PARAMETER_TYPE:
            base_types = ', '.join(f'{t}' for t in Base.PARAMETER_TYPE)
            errors.append(f"'{param_name}' 参数的 'type' 必须是 {base_types} 的一种。")
        else:
            validated_item["type"] = item["type"]
        
        # 获取定义的值
        item_type = validated_item.get("type","string")

        # 校验缺损值符合参数的类型定义
        if "default" in item and item["default"] != None:
            try:
                validated_item["default"] = Base.validate_value_type(item["default"],item_type)
            except Base.TemplateError as e:
                error_messages = '\n'.join(str(error) for error in e.errors)
                errors.append(f"'{param_name}' 参数的 'default' 错误：{error_messages}")

        if errors:
            raise Base.TemplateError(errors)

        return validated_item

    # 校验值是否对应相应的类型
    @staticmethod
    def validate_value_type(value,type_name):
        errors = []
        if type_name == 'string' and not isinstance(value, str):
            errors.append("参数值必须是 string 类型。")
        elif type_name == 'number' and not isinstance(value, (int, float)):
            errors.append("参数值必须是 number 类型。")
        elif type_name == 'bool' and not isinstance(value, bool):
            errors.append("参数值必须是 bool 类型。")
        elif type_name == 'array' and not isinstance(value, list):
            errors.append("参数值必须是 array 类型。")
        elif type_name == 'object' and not isinstance(value, dict):
            errors.append("参数值必须是 object 类型。")
        elif type_name == 'vector':
            if not (isinstance(value, (list, tuple)) and all(isinstance(x, (int, float)) for x in value)):
                errors.append("参数值必须是 vector 类型。")

        if errors:
            raise Base.TemplateError(errors)

        return value

############## 运行时参数校验相关逻辑 ##############

    # 校验参数的具体类型
    def _validate_type(self, value, expected_type):
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'bool':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'vector':
            return isinstance(value, (list, tuple)) and all(isinstance(x, (int, float)) for x in value)
        return False

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
            if not self._validate_type(value, expected_type):
                errors.append(f"{param_type}参数类型不匹配: {name} (期望 {expected_type}, 实际 {type(value).__name__})")
            else:
                # 参数校验通过，添加到 validated_params
                validated_params[name] = value
        
        if errors:
            raise self.ParameterError(errors)
        
        return validated_params  # 返回校验过后的参数字典