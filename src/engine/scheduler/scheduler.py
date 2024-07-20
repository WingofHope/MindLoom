# src/engine/scheduler/scheduler.py

from abc import ABC, abstractmethod

# 导入配置文件从而确定根路径
from ...config import root_path
from src.engine.base.base import Base
from src.engine.executor.action.action import Action
from src.engine.executor.generator.generator import Generator
from src.engine.executor.tool.tool import Tool

class Scheduler(Base):
    # 定义提示模板中的calss字段与py定义的类名的映射关系
    EXECUTION_CLASS_MAPPING = {
        'action': Action,
        'generator': Generator,
        'process': None,
        'tool': Tool
    }

    def __init__(self, id, secret):
        super().__init__(id, secret)

    # 校验call的提示模板是否合法
    def validate_template_call(self, call_dict):   
        # 检查 call_dict 是否是一个字典
        if not isinstance(call_dict, dict):
            raise self.TemplateError("call_dict 必须是一个字典/MAP。")
        
        # 检查必要的键是否存在且类型正确
        if "class" not in call_dict or not isinstance(call_dict["class"], str) or call_dict["class"] not in self.EXECUTION_CLASS_MAPPING:
            raise self.TemplateError("class 必须是action，generator，process或者tool。")
        
        if "id" not in call_dict or not isinstance(call_dict["id"], str):
            raise self.TemplateError("id 必须存在并且是一个字符串。")
        
        if "inputs" not in call_dict or (call_dict["inputs"] is not None and not isinstance(call_dict["inputs"], list)):
            raise self.TemplateError("inputs 必须存在，要么是 None 要么是一个列表。")
        
        if "outputs" not in call_dict or (call_dict["outputs"] is not None and not isinstance(call_dict["outputs"], list)):
            raise self.TemplateError("outputs 必须存在，要么是 None 要么是一个列表。")
        
        # 检查 inputs 和 outputs 的合法性
        for key in ["inputs", "outputs"]:
            # inputs 和 outputs 必须是一个字典
            if call_dict[key] is not None:
                for item in call_dict[key]:
                    if not isinstance(item, dict):
                        raise self.TemplateError(f"{key} 必须是一个字典/MAP。")
                    
                    # inputs 和 outputs 必须包含name，type字段
                    required_item_keys = ["name", "type"]
                    for item_key in required_item_keys:
                        if item_key not in item:
                            raise self.TemplateError(f"{key} 中的必须包含 '{item_key}'。")
                    
                    # type字段的值必须是预定义的值
                    type_name = item["type"]
                    if type_name not in self.PARAMETER_TYPE:
                        param_name = item["name"]
                        raise self.TemplateError(f"'{key}'中的'{param_name}'的'type'不能是'{type_name}'。")

                    # 校验inputs必须包含source或者value
                    if key == "inputs":
                        if "source" not in item and "value" not in item:
                            raise self.TemplateError(f"{key} 中的必须包含 'source'或者'value'。")
                    # 校验outputs必须包含source
                    elif key == "outputs":
                        if "source" not in item:
                            raise self.TemplateError(f"{key} 中的必须包含 'source'。")

    # 校验提示模板是否合法
    def validate_template(self):
        super().validate_template()

        # 校验调度器必须包含execution
        if 'execution' not in self.template:
            raise self.TemplateError("调度器模板必须包含'execution'。")

    # 执行一次嵌套调用
    def call_execute(self, call_dict):
        # 根据class字段名，获取类定义
        call_class = self.EXECUTION_CLASS_MAPPING[call_dict['class']]
        # 直接新实例化一个对应类的对象！！！！！！！！！！！！！！！
        call = call_class(call_dict['id'], secret = None)
        # 运行一次获取结果
        outputs = call.run(inputs)
        for param_name in outputs:
            self.parameters[param_name] = outputs[param_name]

    @abstractmethod
    def run(self, inputs):
        return {}