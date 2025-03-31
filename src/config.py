# src/config.py

import sys
import os
import yaml
import copy
from pathlib import Path
from typing import Any, Dict, Optional, Set, List
from secret import encrypt, decrypt  # 依赖外部加解密函数

from services.logger.create_logger import base_log

# 获取当前项目根目录
ROOT_PATH: Path = Path(__file__).resolve().parent.parent

# 配置文件路径
CONFIG_PATH: Path = ROOT_PATH / "config" / "config.yaml"
DEFAULT_CONFIG_PATH: Path = ROOT_PATH / "config" / "default_config.yaml"

class Config:
    def __init__(self):
        global base_log
        from services.logger.create_logger import base_log  # 这延迟导入日志打印模块base_log

        # 如果 config.yaml 存在，则读取它，否则读取 default_config.yaml
        self.config_path = config_path if config_path.exists() else default_config_path
        self.config = self.load_config()

        # 处理当配置文件启用了字段加密功能，需要先解密
        encryption_conf = self.config.get("encryption", {})
        if encryption_conf.get("encryption_enabled", False):
            strict_mode = encryption_conf.get("strict_mode", True)
            password = os.environ.get("CONFIG_PASSWORD")

            if not password:
                print("配置文件解密错误: 未设置环境变量 CONFIG_PASSWORD，无法解密配置文件。")
                if strict_mode:
                    sys.exit(sys.exit(os.EX_CONFIG))  # 强制终止程序
            
            if not self._decrypt_config_fields(password):
                print("配置文件解密错误: 提供的密码错误，无法解密配置文件。")
                if strict_mode:
                    sys.exit(1)  # 强制终止程序

    def load_config(self):
        """加载配置文件到内存"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as config_file:
                return yaml.safe_load(config_file) or {}
        except FileNotFoundError:
            print(f"配置文件读取错误: 配置文件 {self.config_path} 未找到。")
            return {}
        except yaml.YAMLError as e:
            print(f"配置文件读取错误: 解析 YAML 文件失败: {e}")
            return {}

    def delete_default_config(self):
        if os.path.exists(default_config_path):  # 先检查文件是否存在
            os.remove(default_config_path)
            print(f"{default_config_path} 已删除")
        else:
            print(f"{default_config_path} 不存在")

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

    def save_config(self):
        """
        保存配置到 config.yaml，若启用加密机制，则先对敏感字段加密，
        注意：为避免修改内存中明文配置，采用深拷贝加密后再写入文件
        """
        encryption_conf = self.config.get("encryption", {})
        if encryption_conf.get("encryption_enabled", False):
            password = os.environ.get("CONFIG_PASSWORD")
            if not password:
                print("配置文件存储错误: 配置文件加密已启用，但环境变量 CONFIG_PASSWORD 未设置。")
                return
            # 深拷贝，避免修改内存中解密后的明文配置
            config_to_save = copy.deepcopy(self.config)
            self._encrypt_config_fields(config_to_save, password)
            try:
                with open(config_path, 'w', encoding='utf-8') as config_file:
                    yaml.dump(config_to_save, config_file, allow_unicode=True, default_flow_style=False)
            except IOError as e:
                print(f"配置文件存储错误: 保存配置文件失败: {e}")
                return False
        else:
            try:
                with open(config_path, 'w', encoding='utf-8') as config_file:
                    yaml.dump(self.config, config_file, allow_unicode=True, default_flow_style=False)
            except IOError:
                print(f"配置文件存储错误: 保存配置文件失败: {e}")
                return False
        return True

    def _collect_sensitive_keys(self, data: dict, encryption_conf: dict) -> set:
        """
        内部函数：根据 encryption_conf 中的 fields 和 patterns 规则，收集需要加/解密的字段（完整路径字符串）
        """
        fields_list = encryption_conf.get("fields", [])
        patterns_list = encryption_conf.get("patterns", [])
        sensitive_keys = set()

        # 处理 explicit fields
        for full_key in fields_list:
            keys = full_key.split('.')
            try:
                value = self._get_nested_value(data, keys)
                if isinstance(value, str):
                    sensitive_keys.add(full_key)
            except Exception:
                print(f"配置文件字段错误:  加密字段 {full_key} 失败: {e}")

        # 递归遍历 data，根据 patterns 匹配敏感字段，跳过 encryption 部分
        def collect(d, base_path):
            for k, v in d.items():
                full_path = base_path + [k]
                full_key = '.'.join(full_path)
                if base_path == [] and k == 'encryption':
                    continue
                if not isinstance(v, dict):
                    for pattern in patterns_list:
                        if pattern.startswith('*') and k.endswith(pattern[1:]):
                            sensitive_keys.add(full_key)
                        elif pattern.endswith('*') and k.startswith(pattern[:-1]):
                            sensitive_keys.add(full_key)
                        elif pattern == k:
                            sensitive_keys.add(full_key)
                else:
                    collect(v, full_path)
        collect(data, [])
        return sensitive_keys

    def _decrypt_config_fields(self, password: str) -> bool:
        """
        对 self.config 中的敏感字段进行解密，
        根据 encryption.fields 和 encryption.patterns 中定义的规则进行匹配
        返回是否所有字段都解密成功
        """
        encryption_conf = self.config.get("encryption", {})
        sensitive_keys = self._collect_sensitive_keys(self.config, encryption_conf)

        # 默认所有字段都解密成功
        is_decrypted_successfully = True

        for full_key in sensitive_keys:
            keys = full_key.split('.')
            try:
                value = self._get_nested_value(self.config, keys)
                if isinstance(value, str):
                    decrypted_value = decrypt(password, value)
                    self._set_nested_value(self.config, keys, decrypted_value)
            except Exception as e:
                is_decrypted_successfully = False
                print(f"配置文件解密错误: 解密字段 {full_key} 失败: {e}")

        return is_decrypted_successfully

    def _encrypt_config_fields(self, config_data: dict, password: str)  -> bool:
        """
        对 config_data 中的敏感字段进行加密，
        根据 encryption.fields 和 encryption.patterns 中定义的规则进行匹配
        返回是否所有字段都加密成功
        """
        encryption_conf = config_data.get("encryption", {})
        sensitive_keys = self._collect_sensitive_keys(config_data, encryption_conf)

        # 默认所有字段都加密成功
        is_encrypted_successfully = True

        for full_key in sensitive_keys:
            keys = full_key.split('.')
            try:
                value = self._get_nested_value(config_data, keys)
                if isinstance(value, str):
                    encrypted_value = encrypt(password, value)
                    self._set_nested_value(config_data, keys, encrypted_value)
            except Exception as e:
                is_encrypted_successfully = False
                print(f"配置文件加密错误: 加密字段 {full_key} 失败: {e}")

        return is_encrypted_successfully

    @staticmethod
    def _get_nested_value(d: dict, keys: list):
        """递归获取嵌套字典中的值，若键不存在则抛出 KeyError"""
        for key in keys:
            if key in d:
                d = d[key]
            else:
                raise KeyError(f"字段 {key} 未找到。")
        return d

    @staticmethod
    def _set_nested_value(d: dict, keys: list, value):
        """递归设置嵌套字典中的值"""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

# 初始化配置
config = Config()
