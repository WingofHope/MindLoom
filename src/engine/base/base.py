# src/engine/base/base.py

import os
from abc import ABC, abstractmethod
from bson import ObjectId
import json

# 导入配置文件从而确定根路径
from ...config import root_path
# 从配置文件获取提示模板读入的方式
from config import TEMPLATE_LOAD_METHOD
if TEMPLATE_LOAD_METHOD == 'mongodb':
    from services.mongodb.mongodb import mongo_db
elif TEMPLATE_LOAD_METHOD == 'file':
    from ...config import TEMPLATE_FILE_PATH

# 定义基础类
class Base:
    # 定义模版校验错误的类
    class TemplateError(Exception):
        pass
    # 定义值校验错误类
    class ValidationError(Exception):
        pass
    # 定义类名字映射的文件夹、数据库的名字
    CLASS_NAME_MAPPING = {
        'Action': 'action',
        'Generator': 'generator',
        'Process': 'process',
        'Task': 'task'
    }
    # 定义参数类型种类
    PARAMETER_TYPE = ['string','string-list']

    # 动态存储参数的字典
    parameters = {}

    def __init__(self, id, secret):
        self.id = id
        self.secret = secret
        # 初始化模板
        self.template = self.load_template()
        # 校验模板是否合法
        self.validate_template()

    # 从本地文件读取提示模板方法
    @staticmethod
    def load_template_by_file(index_name, id):
        # 生成完整文件夹路径名字
        folder_path = os.path.join(TEMPLATE_FILE_PATH, index_name)
        
        # 确认文件夹路径存在
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"文件夹{folder_path}不存在")
        
        try:
            # 查找匹配的文件
            for filename in os.listdir(folder_path):
                if filename.startswith(id):
                    file_path = os.path.join(folder_path, filename)
                    # 读取文件内json内容
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read()
                        data_dict = json.loads(file_content)
                        return data_dict
            raise FileNotFoundError(f"没有找到id为{id}的文件")
        except Exception as e:
            raise e

    # 从mongoDB读取提示模板方法
    @staticmethod
    def load_template_by_mongodb(index_name, id):
        try:
            # 转换字符串id为ObjectId
            object_id = ObjectId(id)
        except Exception as e:
            raise self.ValueError(f"无效的id: {id}. {str(e)}")
        
        try:
            # 使用实例化的MongoDB类的find_data方法查找数据
            data = mongo_db.find_data(index_name, {'_id': object_id})
            if not data:
                raise FileNotFoundError(f"没有找到id为{id}的数据")
            
            # 将返回的JSON字符串转换为字典
            data_dict = json.loads(data)
            return data_dict
        except Exception as e:
            raise e

    # 读取提示模板函数
    def load_template(self):
        # 获取当前类名
        class_name = self.__class__.__name__

        # 检查类名是否合法，只有Action、Generator、Process、Task可以获取提示模板
        if class_name not in self.CLASS_NAME_MAPPING:
            raise self.ValueError("class_type必须是Action、Generator、Process、Task中的一个")

        # 类名转换成索引类名
        index_name = self.CLASS_NAME_MAPPING[class_name]
        
        # 从本地文件夹读取模板
        if TEMPLATE_LOAD_METHOD == 'file':
            return self.load_template_by_file(index_name, self.id)
        # 从MongoDB中读取模板
        elif TEMPLATE_LOAD_METHOD == 'mongodb':
            return self.load_template_by_mongodb(index_name, self.id)
        else:
            return {}

    # 获取提示模板
    def get_template(self):
        return self.template

    # 校验提示模板是否合法
    def validate_template(self):
        # 检查template是否存在
        if not self.template:
            raise self.TemplateError("模板不能为空。")

        # 检查 template 是否是一个字典
        if not isinstance(self.template, dict):
            raise self.TemplateError("模板必须是一个字典。")
        
        # 检查必须的参数 name, description, inputs, outputs 是否在 template 中
        required_keys = ["name", "description", "inputs", "outputs"]
        for key in required_keys:
            if key not in self.template:
                raise self.TemplateError(f"模板必须包含'{key}'。")

        # 检查 inputs 和 outputs 是否合法
        for key in ["inputs", "outputs"]:
            # 检查inputs 和 outputs值只能是 list 或 None
            if self.template[key] is not None and not isinstance(self.template[key], list):
                raise self.TemplateError(f"'{key}'必须是一个列表或null。")
            
            # 如果是 list（不是None），则检查每个元素是否是字典，并包含 name, description, type
            if isinstance(self.template[key], list):
                for item in self.template[key]:
                    # 检查inputs 和 outputs的值只能是字典
                    if not isinstance(item, dict):
                        raise self.TemplateError(f"'{key}'中的每个元素必须是一个字典/MAP。")
                    
                    # 检查inputs 和 outputs 必须包含的元素
                    required_item_keys = ["name", "description", "type"]
                    for item_key in required_item_keys:
                        if item_key not in item:
                            raise self.TemplateError(f"'{key}'中的每个元素必须包含'{item_key}'。")

                    # 检查type类型合法性
                    type_name = item["type"]
                    if type_name not in self.PARAMETER_TYPE:
                        param_name = item["name"]
                        raise self.TemplateError(f"'{key}'中的'{param_name}'的'type'不能是'{type_name}'。")

    # 校验输入参数是否合法
    def validate_inputs(self, inputs):
        for template_input in self.template["inputs"]:
            param_name = template_input["name"]
            param_type = template_input["type"]
        
            # 检查提示模板定义的参数是否被传入
            if param_name not in inputs:
                raise self.ValidationError(f"缺少参数: {param_name}。")
            
            # 类型检查
            if param_type == 'string':
                if not isinstance(inputs[param_name], str):
                    raise self.ValidationError(f"参数 {param_name} 应该是字符串。")
            elif param_type == 'string-list':
                if not isinstance(inputs[param_name], list) or not all(isinstance(item, str) for item in inputs[param_name]):
                    raise self.ValidationError(f"参数 {param_name} 应该是一个字符串列表。")

    # 从传入的inputs中给参数字典赋值
    def set_parameters_by_inputs(self, inputs):
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
            if param_name not in self.parameters:
                raise self.ValidationError(f"缺少输出参数: {param_name}。")
            outputs[param_name] = self.parameters[param_name]
        return outputs

    # 必须重载的run函数
    @abstractmethod
    def run(self, inputs):
        return {}