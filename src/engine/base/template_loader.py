# src/engine/base/template_loader.py

import os
import json

from config import config

class TemplateLoader:
    # 从本地文件读取提示模板方法
    @staticmethod
    def load_template_by_file(folder_name, template_id):
        # 生成完整文件夹路径名字
        template_file_path = config.get("prompts.file_config.file_path","prompts/")
        folder_path = os.path.join(template_file_path, folder_name)

        try:
            # 确认文件夹路径存在
            if not os.path.exists(folder_path):
                raise FileNotFoundError(f"文件夹 {folder_path} 不存在。")
            # 查找匹配的文件
            for filename in os.listdir(folder_path):
                # 获取文件名字按‘.’拆分
                name_split = filename.split(".")
                # 校验模板名字与ID是否一致，是否是json格式文件
                if len(name_split) == 3 and name_split[0] == template_id and name_split[2] == "json":
                    file_path = os.path.join(folder_path, filename)
                    # 读取文件内json内容
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read()
                        data_dict = json.loads(file_content)
                        return data_dict
            # 未找到符合id的文件，抛出文件未找到异常
            raise FileNotFoundError(f"在文件夹 {folder_path} 中没有找到template_id为 {template_id} 的文件。")
        
        except json.JSONDecodeError as e:
            # 处理JSON解码错误，提供详细的错误信息
            raise RuntimeError(f"文件 {file_path} 中的JSON格式无效。") from e
        
        except Exception as e:
            # 捕获其他异常并提供上下文信息
            raise RuntimeError(f"读取文件夹 {folder_path} 中的文件时发生异常，folder_name={folder_name}, id={template_id}。") from e

    # 从mongoDB读取提示模板方法
    @staticmethod
    def load_template_by_mongodb(db_name, object_id):
        try:
            # 使用实例化的MongoDB类的find_data方法查找数据
            data_dict = mongo_db.find_one(db_name, {'_id': object_id})
            if not data_dict:
                raise FileNotFoundError(f"MongoDB没有找到id为 {object_id} 的数据。")
            return data_dict
        except Exception as e:
            # 其他异常的处理，增加上下文信息
            raise RuntimeError(f"加载MongoDB数据时发生异常，db_name={db_name}, object_id={object_id}。") from e

    # 调用工具管理器加载工具模板
    @staticmethod
    def load_tools_template(tool_id):
        from engine.executor.tool.tool_manager import tool_manager
        return tool_manager.get_metadata(tool_id)

    # 读取提示模板函数
    @staticmethod
    def load_template(class_name, template_id):
        # 如果是工具类直接返回引擎内模板
        if class_name == 'tool':
            return TemplateLoader.load_tools_template(template_id)

        # 如果是任务、流程、操作或AI生成类则根据配置文件加载模板
        template_load_method = config.get("prompts.template_load_method","localfile")
        try:
            # 从本地文件夹读取模板
            if template_load_method == 'localfile':
                return TemplateLoader.load_template_by_file(class_name, template_id)
            # 从MongoDB中读取模板
            elif template_load_method == 'mongodb':
                return TemplateLoader.load_template_by_mongodb(class_name, template_id)
            else:
                # 如果加载方法配置无效，抛出异常
                raise ValueError(f"无效的模版加载类型: {template_load_method}，请检查配置文件 prompts->template_load_method 项。")
                
        except Exception as e:
            # 抛出其他未预见的异常，保留原始异常上下文
            raise RuntimeError(f"加载模板时发生错误，class_name={class_name}, template_id={template_id}。") from e
