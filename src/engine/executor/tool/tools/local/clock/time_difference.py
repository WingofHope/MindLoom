# src/engine/executor/tool/tools/local/clock/time_difference.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.clock.time_difference",
            "name": "time_difference",
            "description": "计算两个时间点之间的差值（单位：秒或毫秒）。\n该工具接收两个时间字符串（或时间戳），并计算它们之间的时间差。支持指定输入时间的时区，以确保跨时区计算的准确性。",
            "inputs": [
                {
                    "name": "time_a",
                    "type": "string",
                    "description": "第一个时间点，采用 ISO 8601 格式或符合 'format' 模板的时间字符串。",
                    "examples": ["2023-12-01T12:00:00+08:00"],
                    "validation": "必须为有效的时间字符串或时间戳表示形式。"
                },
                {
                    "name": "time_b",
                    "type": "string",
                    "description": "第二个时间点，采用 ISO 8601 格式或符合 'format' 模板的时间字符串。",
                    "examples": ["2023-12-01T13:30:00+08:00"],
                    "validation": "必须为有效的时间字符串或时间戳表示形式。"
                },
                {
                    "name": "timezone",
                    "type": "string",
                    "description": "时区名称，例如 'Asia/Shanghai'（可选）。\n若输入未带时区信息，将以该时区为参考进行计算。",
                    "examples": ["Asia/Shanghai", "UTC"],
                    "validation": "时区名称必须为有效的 IANA 时区字符串。"
                },
                {
                    "name": "unit",
                    "type": "string",
                    "description": "返回的时间差单位，可为 'seconds' 或 'milliseconds'。\n默认为 'seconds'。",
                    "default": "seconds",
                    "examples": ["seconds", "milliseconds"],
                    "validation": "必须为 'seconds' 或 'milliseconds' 之一。"
                }
            ],
            "outputs": [
                {
                    "name": "difference",
                    "type": "number",
                    "description": "两个时间点之间的差值，单位由 'unit' 参数指定。",
                    "examples": [5400]
                }
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")