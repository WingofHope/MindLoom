# src/engine/scheduler/scheduler.py

import time
import uuid

# 导入配置文件从而确定根路径
from engine.base.base import Base
from engine.executor.action.action import Action
from engine.executor.generator.generator import Generator
from engine.executor.tool.tool import Tool

class Scheduler(Base):
    # 定义提示模板中的calss字段与py定义的类名的映射关系
    EXECUTION_CLASS_MAPPING = {
        'action': Action,
        'generator': Generator,
        'process': None, # 该值是Process
        'tool': Tool
    }

    # 构造函数直接调用父类的构造函数加载模板和校验模板
    def __init__(self, template_id, task_id=None, parent_run_id=None):
        super().__init__(template_id, task_id, parent_run_id)
        self.class_name = "scheduler"
        # 定义流程空间动态存储变量的字典
        self.parameters = {}

############## 运行时相关逻辑 ##############

    # 重写执行方法，调度器特殊执行逻辑，需要把输入参数放入变量空间，最后输出再从变量空间取出
    def _execute(self,inputs):
        # 把输入参数设置到类变量空间参数
        self.set_parameters_by_inputs(inputs)
        # 调度器类执行函数进行实施
        self._scheduler_execute()
        # 从获取类变量空间参数获取输出参数
        outputs = self.get_outputs_by_parameters()
        return outputs

    # 子类实现的具体执行逻辑
    def _scheduler_execute():
        pass

############## 提示模板相关逻辑 ##############

    # 校验提示模板是否合法
    @classmethod
    def validate_template(cls, template):
        errors = []  # 用于记录所有校验错误
        validated_template = {}  # 用于存储验证通过的字段

        # 获取当前类名
        class_name = cls.__name__
        class_name = class_name.lower()

        # 调用父类的 validate_template 方法
        try:
            validated_template = super().validate_template(template)
        except cls.TemplateError as base_errors:
            # 从父类校验中收集错误
            errors.extend(base_errors.errors)

        # 校验调度器必须包含 'execution'
        if 'execution' in template and template['execution'] != None:
            try:
                validated_template['execution'] = cls.validate_template_execution(template['execution'])
            except Scheduler.TemplateError as e:
                error_messages = '\n'.join(str(error) for error in e.errors)
                errors.append(f"'execution' 字段存在错误：{error_messages}")
        else:
            errors.append(f"{class_name} 模板中必须包含 'execution' 字段。")

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise cls.TemplateError(errors)

        # 返回经过验证的模板
        return validated_template

############## 提示模板校验相关函数 ##############

    # 需要Process和Task重写具体校验execution模板
    @staticmethod
    def validate_template_execution(execution):
        return {}

    # 校验 call 结构模板，提供给Task和Process调用
    @staticmethod
    def validate_template_call(call_dict):
        errors = []  # 用于记录所有校验错误
        validated_call = {}  # 用于存储验证通过的字段

        if not isinstance(call_dict, dict):
            errors.append("'call' 字段必须是一个结构对象。")
            raise Scheduler.TemplateError(errors)

        # 校验class段必须存在且是流程、操作、生成内容或者工具
        if "class" not in call_dict:
            errors.append("'call' 必须包含 'class' 字段。")
        elif call_dict["class"] is None or not isinstance(call_dict["class"], str):
            errors.append("'call' -> 'class' 必须是有效的字符串类型。")
        elif call_dict["class"] not in Scheduler.EXECUTION_CLASS_MAPPING:
            execution_class = ', '.join(f'{t}' for t in Scheduler.EXECUTION_CLASS_MAPPING)
            errors.append(f"'call' -> 'class' 必须是 {execution_class} 的一种。")
        else:
            validated_call["class"] = call_dict["class"]

        # 检查 "id" 值是否合法，这里不会查询其是否存在
        if "id" not in call_dict:
            errors.append("'call' 必须包含 'id' 字段。")
        if call_dict["id"] is None or not isinstance(call_dict["id"], str):
            errors.append("'call' -> 'id' 必须是有效的字符串类型。")
        else:
            validated_call["id"] = call_dict["id"]

        # 检查 "error_handling" 值是如果存在，校验是否合法
        if "error_handling" in call_dict:
            try:
                validated_call["error_handling"] = Scheduler.validate_template_call_error_handling(call_dict["error_handling"])
            except Scheduler.TemplateError as e:
                error_messages = '\n'.join(f'{e}' for e in e.errors)
                errors.append(f"'call' -> 'error_handling' 字段存在错误：{error_messages}")

        # 检查call输入参数是否合法
        try:
            if "inputs" in call_dict and call_dict["inputs"] != None:
                validated_call["inputs"] = Scheduler.validate_template_call_params(call_dict["inputs"],"input")
            else: 
                errors.append("'call' 必须包含 'inputs' 字段。")
        except Scheduler.TemplateError as e:
            error_messages = '\n'.join(f'{e}' for e in e.errors)
            errors.append(f"'call' -> 'inputs' 字段存在错误：{error_messages}")

        # 检查call输出参数是否合法
        try:
            if "outputs" in call_dict and call_dict["outputs"] != None:
                validated_call["outputs"] = Scheduler.validate_template_call_params(call_dict["outputs"],"output")
            else: 
                errors.append("'call' 必须包含 'outputs' 字段。")
        except Scheduler.TemplateError as e:
            error_messages = '\n'.join(f'{e}' for e in e.errors)
            errors.append(f"'call' -> 'outputs' 字段存在错误：{error_messages}")

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise Scheduler.TemplateError(errors)

        # 返回经过验证的模板
        return validated_call 

    # 校验 error_handling 字段的合法性
    @staticmethod
    def validate_template_call_error_handling(error_handling):
        errors = [] # 用于记录所有校验错误
        validated_error_handling = {} # 用于存储验证通过的字段

        if not isinstance(error_handling, dict):
            errors.append("错误处理字段必须是一个结构对象。")
            raise Scheduler.TemplateError(errors)

        # 校验 strategy 字段必须是特定的字符串
        if "strategy" not in error_handling:
            errors.append("错误处理字段必须包含 'strategy' 字段。")
        elif not isinstance(error_handling["strategy"],str):
            errors.append(" 'strategy' 必须是字符串")
        elif error_handling["strategy"] not in ["skip", "abort"]:
            errors.append(" 'strategy' 字段必须是'skip', 'abort'中的一个。")
        else:
            validated_error_handling["strategy"] = error_handling["strategy"]

        # 校验重试字段
        if "retry" not in error_handling:
            errors.append("错误处理字段必须包含 'retry' 字段。")
        elif not isinstance(error_handling["retry"],dict):
            errors.append(" 'strategy' -> 'retry' 必须是结构对象。")
        else:
            validated_retry = {}
            # 校验是否重试字段合法性
            if "enabled" not in error_handling["retry"]:
                errors.append(" 'strategy' -> 'retry' 字段的 'enabled' 必须存在。")
            elif not isinstance(error_handling["retry"]["enabled"],bool):
                errors.append(" 'strategy' -> 'retry' -> 'enabled' 必须是布尔值。")
            else:
                validated_retry["enabled"] = error_handling["retry"]["enabled"]

            # 校验重试次数字段合法性
            if "retry_count" not in error_handling["retry"]:
                validated_retry["retry_count"] = 1
            elif not isinstance(error_handling["retry"]["retry_count"],int):
                errors.append(" 'strategy' -> 'retry' -> 'retry_count' 必须是整数。")
            elif error_handling["retry"]["retry_count"] < 1 or error_handling["retry"]["retry_count"] > 15:
                errors.append(" 'strategy' -> 'retry' -> 'retry_count' 的值必需要在 1 至 15 之间。")
            else:
                validated_retry["retry_count"] = error_handling["retry"]["retry_count"]

            # 校验重试等待秒数字段合法性
            if "interval" not in error_handling["retry"]:
                validated_retry["interval"] = 1
            elif not isinstance(error_handling["retry"]["interval"],int):
                errors.append(" 'strategy' -> 'retry' -> 'interval' 必须是整数。")
            elif error_handling["retry"]["interval"] < 0 or error_handling["retry"]["interval"] > 1000:
                errors.append(" 'strategy' -> 'retry' -> 'interval' 的值必需要在 0 至 1000 之间。")
            else:
                validated_retry["interval"] = error_handling["retry"]["interval"]
            
            # 填充retry结构体
            validated_error_handling["retry"] = validated_retry

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise Scheduler.TemplateError(errors)

        return validated_error_handling


    # 校验参数列表
    @staticmethod
    def validate_template_call_params(params, transfer_direction):
        errors = [] # 用于记录所有校验错误
        validated_params = [] # 用于存储验证通过的字段

        # 首先检查是否是字典，不是则直接返回报错
        if not isinstance(params, list):
            errors.append("该值必须是一个参数列表。")
            raise Scheduler.TemplateError(errors)

        # 循环校验每个参数
        for item in params:
            try:
                validated_params.append(Scheduler.validate_template_call_params_item(item,transfer_direction))
            except Scheduler.TemplateError as e:
                errors.extend(e.errors)

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise Scheduler.TemplateError(errors)

        return validated_params

    # 校验参数内容
    @staticmethod
    def validate_template_call_params_item(item, transfer_direction):
        errors = [] # 用于记录所有校验错误
        validated_item = {} # 用于记录所有校验错误

        if not isinstance(item, dict):
            errors.append("参数必须是一个结构对象。")
            raise Scheduler.TemplateError(errors)

        # 检查 "name" 值是否存在且合法
        if "name" not in item:
            errors.append("参数必须包含 'name' 字段。")
        if item["name"] is None or not isinstance(item["name"], str):
            errors.append("参数 'name' 字段必须是有效的字符串类型。")
        else:
            validated_item["name"] = item["name"]

        # 保存参数名字，用于打印错误日志
        param_name = validated_item.get("name", "<unknown>")

        # 校验type段必须存在且是流程、操作、生成内容或者工具
        if "type" not in item:
            errors.append(f"'{param_name}' 参数必须包含 'type' 字段。")
        elif item["type"] is None or not isinstance(item["type"], str):
            errors.append("'call' -> 'type' 必须是有效的字符串类型。")
        elif item["type"] not in Scheduler.PARAMETER_TYPE:
            base_types = ', '.join(f'{t}' for t in Base.PARAMETER_TYPE)
            errors.append(f"'{param_name}' 参数的 'type' 必须是 {base_types} 的一种。")
        else:
            validated_item["type"] = item["type"]

        # 获取定义的值
        item_type = validated_item.get("type","string")

        # 校验输入参数必须存在source或者value并且合法
        if transfer_direction == "input":
            if "value" in item and item["value"] != None:
                try:
                    validated_item["value"] = Scheduler.validate_value_type(item["value"],item_type)
                except Scheduler.TemplateError as e:
                    error_messages = '\n'.join(str(error) for error in e.errors)
                    errors.append(f"'{param_name}' 参数的 'value' 错误：{error_messages}")
            elif "source" in item and item["source"] != None:
                if not isinstance(item["source"], str):
                    errors.append(f"'inputs' 中的 '{param_name}' 的 'source' 必须是一个字符串。")
                else:
                    validated_item["source"] = item["source"]
            else:
                errors.append(f"'inputs' 中的 '{param_name}' 中必须包含 'source' 或 'value'。")

        # 校验输出参数必须存在target并且合法
        if transfer_direction == "output":
            if "target" not in item and item["target"] != None:
                errors.append(f"'outputs' 中的 '{param_name}' 中必须包含  'target'。")
            else:
                if not isinstance(item["target"], str):
                    errors.append(f"'outputs' 中的 '{param_name}' 的 'target' 必须是一个字符串。")
                else:
                    validated_item["target"] = item["target"]

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise Scheduler.TemplateError(errors)

        return validated_item

############## 运行时参数内存空间管理 ##############

    # 从传入的inputs中给参数字典赋值
    def set_parameters_by_inputs(self, inputs):
        # 如果提示模板规定输入变量是空值，不需要赋值
        if self.template["inputs"] == None:
            return
        # 根据模板规定需要输入，在类内存空间添加相应变量
        for template_input in self.template["inputs"]:
            param_name = template_input["name"]
            self.parameters[param_name] = inputs[param_name]

    # 从参数字典获取提示模板规定的outputs
    def get_outputs_by_parameters(self):
        # 如果提示模板规定的输出是空，直接返回空
        if self.template["outputs"] == None:
            return None
        # 如果提示模板规定的输出不是空，构造返回字典
        outputs = {}
        for template_output in self.template["outputs"]:
            param_name = template_output["name"]
            if param_name in self.parameters:
                outputs[param_name] = self.parameters[param_name]
        return outputs

############## 运行时处理逻辑 ##############

    # 执行一次嵌套call run调用
    def _call_execute(self, call_dict):
        # 获取调用模板ID
        call_template_id = call_dict['id']

        # 获取调用类型
        call_class_name = call_dict["class"]
        
        # 打印相关执行call记录log
        self.runtime_log.add_record(f"准备执行调用，调用类型： {call_class_name}\n调用ID：{call_template_id}\n调用详情：{call_dict}")

        # 根据class字段名，获取类定义
        CallClass = self.EXECUTION_CLASS_MAPPING[call_class_name]

        # 实例化一个对应类的对象，如果模板错误则终止
        try:
            call = CallClass(call_template_id, task_id=self.task_id, parent_run_id=self.run_id)
        except Scheduler.TemplateError as e:
            error_messages = [
                f"模版{call_dict['id']} 模板验证失败，错误信息如下：",
                "\n".join(e.errors)
            ]
            self.runtime_log.add_record("\n".join(error_messages))
            raise RuntimeError(f"模板 {call_template_id} 格式校验错误: {e}")
        except Exception as e:
            self.runtime_log.add_record(f"模板 {call_template_id} 运行时错误: {str(e)}")
            raise RuntimeError(f"模板未知错误: {e}")

        # 获取错误处理策略，如果不存在则填默认值abort，终止
        error_handling_strategy = call_dict.get("error_handling", {}).get("strategy","abort")
        # 获取错误处理是否重试，如果不存在则填默认值false，不重试
        error_handling_retry = call_dict.get("error_handling", {}).get("retry", {}).get("enabled",False)
        # 获取错误处理重试次数，如果不存在则填默认值1次
        if error_handling_retry:
            error_handling_retry_count = call_dict.get("error_handling", {}).get("retry", {}).get("retry_count",1)
        else:
            error_handling_retry_count = 0
        # 获取错误处理重试等待时间，如果不存在则填默认值1秒
        error_handling_retry_interval = call_dict.get("error_handling", {}).get("retry", {}).get("interval",1)
        
        # 执行call调用
        attempt = 0
        outputs = None
        while attempt <= error_handling_retry_count:
            # 生成调用的运行时ID
            call_run_id = str(uuid.uuid4())

            # 根据获取call结构定义从类内存变量空间取出对应参数
            inputs = self.get_inputs_by_definition(call_dict["inputs"])

            # 尝试执行run函数,如果执行成功，退出循环
            try:
                self.runtime_log.add_record(f"执行调用，运行ID：{call_run_id}，传入参数：{inputs}")
                outputs = call.run(inputs, call_run_id)
                break
            # 如果参数校验错误，直接返回错误
            except Scheduler.ParameterError as e:
                error_messages = [
                    f"调用参数校验失败，错误信息如下：",
                    "\n".join(e.errors)
                ]
                self.runtime_log.add_record("\n".join(error_messages))
                raise RuntimeError(f"调用参数错误: {e}")
            # 运行时错误处置
            except RuntimeError as e:
                # 打印错误日志
                self.runtime_log.add_record(f"执行调用任务 {call_run_id} 触发运行时错误: {str(e)}")
                
                # 如果error_handling_retry为True，进行重试
                if error_handling_retry:
                    attempt += 1
                    if attempt <= error_handling_retry_count:
                        self.runtime_log.add_record(f"调用开始重试第{attempt}次，等待{error_handling_retry_interval}秒后执行。")
                        time.sleep(error_handling_retry_interval)
                        continue
                    else:
                        self.runtime_log.add_record(f"调用重试次数已耗尽，调用任务执行失败。")
                
                # 根据错误处理策略决定后续行为
                if error_handling_strategy == "abort":
                    self.runtime_log.add_record(f"执行调用任务 {call_run_id} 运行时错误,执行策略为'abort'，任务终止。")
                    raise RuntimeError(f"执行调用任务失败，错误信息: {str(e)}")
                elif error_handling_strategy == "skip":
                    self.runtime_log.add_record(f"执行调用任务 {call_run_id} 执行失败，执行策略为'skip'，跳过此任务，未返回输出。")
                    outputs = None
                    break
            # 未知错误直接返回报错
            except Exception as e:
                self.runtime_log.add_record(f"执行调用运行时未知错误: {str(e)}")
                raise RuntimeError(f"执行调用运行未知错误: {e}")

        # 将输出参数设置到类内存变量空间
        if outputs is not None:
            self.runtime_log.add_record(f"执行调用任务 {call_run_id} 成功，返回 {outputs}。")
            self.set_outputs_by_target(outputs, call_dict['outputs'])

    # 将参数放置到类变量空间动态存储参数的字典
    def set_outputs_by_target(self, outputs, outputs_definition):
        parameters = {}
        # 循环赋值返回的参数
        for def_output in outputs_definition:
            output_name = def_output["name"]
            output_type = def_output["type"]
            output_target = def_output["target"]
            # 校验板定义的目标参数存在且类型合法
            if output_name not in outputs:
                raise RuntimeError(f"未返回期待的内存空间参数 {output_name}。")
            elif self._validate_type(outputs[output_name], output_type) == False:
                raise RuntimeError(f"返回的变量 {output_name} 类型与 {output_target} 期待类型不符，不是预期的 {input_type} 类型。")
            else:
                parameters[output_target] = outputs[output_name]
        
        # 当没有错误后统一设置到内存空间参数
        for parameter in parameters:
            self.parameters[parameter] = parameters[parameter]

    # 从类变量空间动态存储参数的字典，根据定义模板获取参数 
    def get_inputs_by_definition(self, inputs_definition):
        inputs = {}
        # 循环填充定义需要的输入参数
        for def_input in inputs_definition:
            # 获取对应的值内容
            value = None
            if "value" in def_input:
                # 如果模板定义存在value，则直接赋值
                value = def_input["value"]
            elif "source" in def_input:
                # 如果模板定义存在source，则在类内存空间参数字典中寻找并赋值
                input_source = def_input["source"]
                if input_source not in self.parameters:
                    raise RuntimeError(f"变量空间缺少参数 {input_source}。")
                else:
                    value = self.parameters[input_source]

            # 校验值的类型是否和模板定义相符，通过后放入返回变量
            input_name = def_input["name"]
            input_type = def_input['type']
            if self._validate_type(value, input_type):
                inputs[input_name] = value
            else:
                raise RuntimeError(f"被传入的变量 {input_name} 类型值不是预期的 {input_type} 类型。")
        # 返回获取的输入参数
        return inputs

