# src/engine/base/base.py

import os
from abc import ABC, abstractmethod
from bson import ObjectId
import json
from ...config import TEMPLATE_LOAD_METHOD

if TEMPLATE_LOAD_METHOD == 'mongodb':
    from services.mongodb.mongodb import mongo_db
elif TEMPLATE_LOAD_METHOD == 'file':
    from ...config import TEMPLATE_FILE_PATH

class ValidationError(Exception):
    pass

# 定义基础类
class Base:

    # 定义类名字映射的文件夹、数据库的名字
    CLASS_NAME_MAPPING = {
        'Action': 'action',
        'Generator': 'generator',
        'Process': 'process',
        'Task': 'task'
    }

    def __init__(self, id, inputs, secret):
        self.id = id
        self.input_dict = inputs
        self.secret = secret
        # 初始化模板
        self.template = self.load_template()
        
        # 校验模板是否合法
        # self.validate_template()

    @staticmethod
    def load_template_by_file(type_name, id):
        # 生成完整文件夹路径名字
        folder_path = os.path.join(TEMPLATE_FILE_PATH, type_name)
        
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

    @staticmethod
    def load_template_by_mongodb(type_name, id):
        try:
            # 转换字符串id为ObjectId
            object_id = ObjectId(id)
        except Exception as e:
            raise ValueError(f"无效的id: {id}. {str(e)}")
        
        try:
            # 使用实例化的MongoDB类的find_data方法查找数据
            data = mongo_db.find_data(type_name, {'_id': object_id})
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
        class_type = self.__class__.__name__

        # 检查类名是否合法，只有Action、Generator、Process、Task可以获取提示模板
        if class_type not in self.CLASS_NAME_MAPPING:
            raise ValueError("class_type必须是Action、Generator、Process、Task中的一个")

        # 类名转换成索引类名
        type_name = self.CLASS_NAME_MAPPING[class_type]
        
        # 从本地文件夹读取模板
        if TEMPLATE_LOAD_METHOD == 'file':
            return self.load_template_by_file(type_name, self.id)
        # 从MongoDB中读取模板
        elif TEMPLATE_LOAD_METHOD == 'mongodb':
            return self.load_template_by_mongodb(type_name, self.id)
        else:
            return {}

    # 获取提示模板
    def get_template(self):
        return self.template

    # 校验提示模板是否合法
    def validate_template(self):
        # 基础的校验逻辑
        if not isinstance(self.template, dict):
            raise ValidationError(f"Template must be a dictionary, got {type(self.template)} instead.")
        if not self.template:
            raise ValidationError("Template cannot be empty.")

    # 必须重载的run函数
    @abstractmethod
    def run(self):
        return {}