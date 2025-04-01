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
    def __init__(self) -> None:
        """初始化配置，加载 YAML 文件，并根据加密配置进行解密"""
        self.config_path: Path = CONFIG_PATH if CONFIG_PATH.exists() else DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = self.load_config()
        
        encryption_conf: Dict[str, Any] = self.config.get("encryption", {})
        if encryption_conf.get("encryption_enabled", False):
            strict_mode: bool = encryption_conf.get("strict_mode", True)
            password: Optional[str] = os.environ.get("CONFIG_PASSWORD")
            
            if not password:
                base_log.error("未设置环境变量 CONFIG_PASSWORD，无法解密配置文件。")
                if strict_mode:
                    sys.exit(os.EX_CONFIG)
            
            if not self._decrypt_config_fields(password):
                base_log.error("提供的密码错误，无法解密配置文件。")
                if strict_mode:
                    sys.exit(os.EX_CONFIG)

    def load_config(self) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        try:
            with self.config_path.open("r", encoding="utf-8") as config_file:
                return yaml.safe_load(config_file) or {}
        except FileNotFoundError:
            base_log.error(f"配置文件 {self.config_path} 未找到。")
        except yaml.YAMLError as e:
            base_log.error(f"YAML 解析错误: {e}")
        return {}

    def delete_default_config(self) -> None:
        """删除默认配置文件"""
        if DEFAULT_CONFIG_PATH.exists():
            DEFAULT_CONFIG_PATH.unlink()
            base_log.info(f"{DEFAULT_CONFIG_PATH} 已删除")
        else:
            base_log.warning(f"{DEFAULT_CONFIG_PATH} 不存在")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """获取嵌套配置项"""
        keys: List[str] = key.split('.')
        value: Any = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """设置嵌套配置项"""
        keys: List[str] = key.split('.')
        d: Dict[str, Any] = self.config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def save_config(self) -> bool:
        """保存配置到 config.yaml"""
        encryption_conf: Dict[str, Any] = self.config.get("encryption", {})
        # 为避免修改内存中明文配置，采用深拷贝加密后再写入文件
        config_to_save: Dict[str, Any] = copy.deepcopy(self.config)

        if encryption_conf.get("encryption_enabled", False):
            password: Optional[str] = os.environ.get("CONFIG_PASSWORD")
            if not password:
                base_log.error("环境变量 CONFIG_PASSWORD 未设置，无法加密配置文件。")
                return False
            self._encrypt_config_fields(config_to_save, password)
            base_log.info(f"配置文件保密字段加密成功。")
        
        try:
            with CONFIG_PATH.open("w", encoding="utf-8") as config_file:
                yaml.dump(config_to_save, config_file, allow_unicode=True, default_flow_style=False)
                base_log.info(f"配置文件保存成功，保存路径：{CONFIG_PATH} 。")
            return True
        except Exception as e:
            base_log.error(f"保存配置文件失败: {e}")
            return False

    def _collect_sensitive_keys(self, data: Dict[str, Any], encryption_conf: Dict[str, Any]) -> Set[str]:
        """
        内部函数：根据 encryption_conf 中的 fields 和 patterns 规则，收集需要加/解密的字段（完整路径字符串）
        """
        fields: List[str] = encryption_conf.get("fields", [])
        patterns: List[str] = encryption_conf.get("patterns", [])
        sensitive_keys: Set[str] = set(fields)
        
        def collect(d: Dict[str, Any], prefix: str = "") -> None:
            for k, v in d.items():
                full_key: str = f"{prefix}.{k}" if prefix else k
                if any(full_key.startswith(p[:-1]) if p.endswith('*') else full_key.endswith(p[1:]) for p in patterns):
                    sensitive_keys.add(full_key)
                if isinstance(v, dict):
                    collect(v, full_key)

        collect(data)
        return sensitive_keys

    def _decrypt_config_fields(self, password: str) -> bool:
        """
        对 self.config 中的敏感字段进行解密，
        根据 encryption.fields 和 encryption.patterns 中定义的规则进行匹配
        返回是否所有字段都解密成功
        """
        sensitive_keys: Set[str] = self._collect_sensitive_keys(self.config, self.config.get("encryption", {}))
        success: bool = True

        for key in sensitive_keys:
            keys = key.split('.')
            try:
                value: Any = self._get_nested_value(self.config, keys)
                if isinstance(value, str):
                    decrypted_value = decrypt(password, value)
                    self._set_nested_value(self.config, keys, decrypted_value)
            except Exception as e:
                success = False
                base_log.error(f"解密字段 {key} 失败: {e}")
        return success

    def _encrypt_config_fields(self, config_data: Dict[str, Any], password: str) -> bool:
        """
        对 config_data 中的敏感字段进行加密，
        根据 encryption.fields 和 encryption.patterns 中定义的规则进行匹配
        返回是否所有字段都加密成功
        """
        sensitive_keys: Set[str] = self._collect_sensitive_keys(config_data, config_data.get("encryption", {}))
        success: bool = True

        for key in sensitive_keys:
            keys = key.split('.')
            try:
                value: Any = self._get_nested_value(config_data, keys)
                if isinstance(value, str):
                    encrypted_value = encrypt(password, value)
                    self._set_nested_value(config_data, keys, encrypted_value)
            except Exception as e:
                success = False
                base_log.error(f"加密字段 {key} 失败: {e}")
        return success

    @staticmethod
    def _get_nested_value(d: dict, keys: list) -> Dict[str, Any]:
        """递归获取嵌套字典中的值，若键不存在则抛出 KeyError"""
        for key in keys:
            if key in d:
                d = d[key]
        return d

    @staticmethod
    def _set_nested_value(d: dict, keys: list, value) -> None:
        """递归设置嵌套字典中的值"""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

# 初始化配置
config = Config()
