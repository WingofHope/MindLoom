# src/engine/executor/tool/tools/local/local_address.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalAddress(ToolBase):
    
    @staticmethod
    def metadata():
        return {
            "id": "local.local_address",
            "name": "get_local_address",
            "description": "获取本地的位置描述字符串。",
            "inputs": [],
            "outputs": [
                {"name": "local_address", "type": "string", "description": "格式化的位置描述的字符串"}
            ]
        }

    def run(self, inputs):
        return {"local_address": "北京市昌平区回龙观龙跃苑二区"}