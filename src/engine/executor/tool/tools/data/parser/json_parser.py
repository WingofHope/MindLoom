# src/engine/executor/tool/tools/parser/json_parser.py

import json
from engine.executor.tool.tools.tool_base import ToolBase

class JSONParser(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "parser.json_parser",
            "name": "json_parser",
            "description": "解析 JSON 字符串并转换为字典。",
            "inputs": [
                {"name": "json_string", "type": "string", "description": "JSON 格式的字符串"}
            ],
            "outputs": [
                {"name": "json_data", "type": "object", "description": "解析后的字典数据"}
            ]
        }

    @staticmethod
    def run(inputs):
        json_string = inputs.get("json_string", "").strip()
        if not json_string:
            raise ValueError("输入的 \"json_string\" 参数不能为空。")
        try:
            return {"json_data": json.loads(json_string)}
        except json.JSONDecodeError as e:
            raise ValueError(f"Json解析出错，Python执行错误：{e}")