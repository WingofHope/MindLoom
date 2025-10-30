# src/engine/executor/tool/tools/tool_base.py

from abc import ABC, abstractmethod

class ToolBase(ABC):
    @staticmethod
    @abstractmethod
    def metadata():
        """
        返回工具的元数据，所有工具必须实现此方法。
        """
        pass

    @staticmethod
    @abstractmethod
    def run(inputs):
        """
        执行工具的操作，所有工具必须实现此方法。
        """
        pass
