# src/engine/executor/tool/tools/local/clock/get_utc_time.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.clock.get_utc_time",
            "name": "get_utc_time",
            "description": "获取当前的 UTC 时间。\n该工具返回当前协调世界时（UTC）的时间字符串，采用标准的 ISO 8601 / RFC 3339 格式，例如 '2023-12-01T04:00:00Z'。\n\n此工具常用于时间同步、跨时区数据存储、日志记录等需要统一时间基准的场景。",
            "inputs": [],
            "outputs": [
                {
                    "name": "utc_time",
                    "type": "string",
                    "description": "当前 UTC 时间字符串（ISO 8601 格式），以 'Z' 结尾表示零时区偏移，例如 '2023-12-01T04:00:00Z'。",
                    "examples": ["2023-12-01T04:00:00Z"]
                }
            ]
        }
        
    @staticmethod
    def run(inputs):
        timezone = inputs.get("timezone", "UTC")
        try:
            tz = ZoneInfo(timezone)
            now = datetime.now(tz)
            return {"local_time": now.strftime("%Y-%m-%d %H:%M:%S %A %Z")}
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")