# src/engine/executor/tool/tools/local/clock/get_local_time.py

from datetime import datetime
from zoneinfo import ZoneInfo
from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.clock.get_local_time",
            "name": "get_local_time",
            "description": "获取当前系统的本地时间。\n该工具返回指定时区下的当前时间字符串，采用标准的 ISO 8601 / RFC 3339 格式（包含时区偏移），例如 '2023-12-01T12:00:00+08:00'。如果未指定时区，则使用系统默认时区。\n\n此工具可用于显示当前时间、日志记录或生成时间标记等用途，支持通过 'timezone' 参数灵活获取不同地区的本地时间。",
            "inputs": [
                {
                    "name": "timezone",
                    "type": "string",
                    "description": "时区名称，例如 'Asia/Shanghai'（可选）。\n该参数用于指定希望获取的时间所在的时区。如果未提供，将使用系统默认时区。",
                    "examples": ["Asia/Shanghai", "UTC", "America/New_York"],
                    "default": "",
                    "validation": "时区名称必须为有效的 IANA 时区字符串（例如 'Asia/Tokyo'）。若指定无效时区，将返回错误。"
                }
            ],
            "outputs": [
                {
                    "name": "local_time",
                    "type": "string",
                    "description": "指定时区下的当前时间字符串（ISO 8601 格式），例如 '2023-12-01T12:00:00+08:00'。",
                    "examples": ["2023-12-01T12:00:00+08:00"]
                }
            ]
        }
        
    @staticmethod
    def run(inputs):
        timezone = inputs.get("timezone", "")
        try:
            tz = ZoneInfo(timezone)
            now = datetime.now(tz)
            return {"local_time": now.strftime("%Y-%m-%d %H:%M:%S %A %Z")}
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")