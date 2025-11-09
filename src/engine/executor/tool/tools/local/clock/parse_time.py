# src/engine/executor/tool/tools/local/clock/parse_time.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.clock.parse_time",
            "name": "parse_time",
            "description": "解析时间字符串为时间戳（单位：秒）。\n该工具接收一个时间字符串和一个格式模板，按照指定的格式解析时间字符串，并将其转换为自1970年1月1日以来的秒数（即时间戳）。",
            "inputs": [
                {
                    "name": "time_string",
                    "type": "string",
                    "description": "待解析的时间字符串，应符合指定的格式模板。",
                    "examples": ["2023-12-01 12:00:00"],
                    "validation": "时间字符串必须与 'format' 中指定的模板格式完全匹配。"
                },
                {
                    "name": "format",
                    "type": "string",
                    "description": "时间字符串的格式模板，例如 '%Y-%m-%d %H:%M:%S'。",
                    "examples": ["%Y-%m-%d %H:%M:%S"],
                    "validation": "格式模板应符合标准时间格式符号要求。"
                },
                {
                    "name": "timezone",
                    "type": "string",
                    "description": "时区名称，例如 'Asia/Shanghai'（可选）。",
                    "examples": ["Asia/Shanghai", "UTC"],
                    "validation": "时区名称必须为有效的 IANA 时区字符串。"
                }
            ],
            "outputs": [
                {
                    "name": "timestamp",
                    "type": "number",
                    "description": "解析得到的时间戳（秒）。",
                    "examples": [1701412800]
                }
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")