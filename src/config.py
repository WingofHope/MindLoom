# src/config.py

import os
import yaml

# 获取当前项目根目录
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 配置文件路径
config_path = os.path.join(root_path, 'config/config.yaml')
default_config_path = os.path.join(root_path, 'config/default_config.yaml')

class Config:
    def __init__(self):
        # 如果 config.yaml 存在，则读取它，否则读取 default_config.yaml
        self.config_path = config_path if os.path.exists(config_path) else default_config_path
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件到内存"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as config_file:
                # 使用 yaml.safe_load 来加载 YAML 文件
                return yaml.safe_load(config_file) or {}
        except (FileNotFoundError, yaml.YAMLError) as e:
            return {}

    def get(self, key, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
        except KeyError:
            return default
        return value

    def set(self, key, value):
        """设置配置项，并保存到 config.yaml"""
        keys = key.split('.')
        d = self.config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self.save_config()

    def save_config(self):
        """保存配置到 config.yaml，丢弃注释"""
        try:
            with open(config_path, 'w', encoding='utf-8') as config_file:
                # 使用 yaml.dump 保存配置，丢弃注释
                yaml.dump(self.config, config_file, allow_unicode=True, default_flow_style=False)
        except IOError as e:
            pass

# 初始化配置
config = Config()
