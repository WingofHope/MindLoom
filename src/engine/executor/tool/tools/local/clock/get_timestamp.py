# src/engine/executor/tool/tools/local/clock/get_timestamp.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.clock.get_timestamp",
            "name": "get_timestamp",
            "description": "获取当前时间戳。\n该工具返回当前时间的时间戳，可选择单位为秒或毫秒。可通过 'timezone' 参数指定参考时区（仅影响显示用例，不影响时间戳值）。\n\n此工具常用于时间计算、缓存控制、任务调度等需要精确时间值的场景。",
            "inputs": [
                {
                    "name": "unit",
                    "type": "string",
                    "description": "时间戳单位，可为 'seconds' 或 'milliseconds'。\n默认为 'seconds'。",
                    "default": "seconds",
                    "examples": ["seconds", "milliseconds"],
                    "validation": "必须为 'seconds' 或 'milliseconds' 之一，否则返回错误。"
                }
            ],
            "outputs": [
                {
                    "name": "timestamp",
                    "type": "number",
                    "description": "当前时间对应的时间戳，单位为秒或毫秒，取决于输入参数 'unit'。",
                    "examples": [1701412800, 1701412800123]
                }
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")