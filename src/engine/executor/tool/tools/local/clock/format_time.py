# src/engine/executor/tool/tools/local/clock/format_time.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.clock.format_time",
            "name": "format_time",
            "description": "将时间戳格式化为时间字符串。\n该工具接收一个时间戳、格式模板和可选的时区参数，将时间戳转换为指定时区下符合格式要求的时间字符串。输出字符串遵循 ISO 8601 / RFC 3339 格式并包含时区偏移，例如 '2023-12-01T12:00:00+08:00'。",
            "inputs": [
                {
                    "name": "timestamp",
                    "type": "number",
                    "description": "待格式化的时间戳，可为秒或毫秒单位。",
                    "examples": [1701412800, 1701412800123],
                    "validation": "输入必须为整数或浮点数，表示自1970年1月1日以来的秒数或毫秒数。"
                },
                {
                    "name": "format",
                    "type": "string",
                    "description": "时间格式模板，使用标准时间格式符号，例如 '%Y-%m-%d %H:%M:%S'。",
                    "examples": ["%Y-%m-%d %H:%M:%S"],
                    "validation": "必须为有效的时间格式模板字符串，否则格式化将失败并返回错误。"
                },
                {
                    "name": "timezone",
                    "type": "string",
                    "description": "时区名称，例如 'Asia/Shanghai'（可选）。\n用于指定输出时间的时区。",
                    "default": "",
                    "examples": ["Asia/Shanghai", "UTC", "Europe/London"],
                    "validation": "时区名称必须为有效的 IANA 时区字符串。"
                }
            ],
            "outputs": [
                {
                    "name": "formatted_time",
                    "type": "string",
                    "description": "格式化后的时间字符串（ISO 8601 格式），例如 '2023-12-01T12:00:00+08:00'。",
                    "examples": ["2023-12-01T12:00:00+08:00"]
                }
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")