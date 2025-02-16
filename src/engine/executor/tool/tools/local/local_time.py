# src/engine/executor/tool/tools/local/local_time.py

from datetime import datetime
import pytz

class LocalTime:
    @staticmethod
    def metadata():
        return {
            "id": "local.local_time",
            "name": "get_local_time",
            "description": "获取本地时间的字符串，包括日期、时间、星期和时区。",
            "inputs": [
                {"name": "timezone", "type": "string", "description": "时区名称，例如 'Asia/Shanghai'"}
            ],
            "outputs": [
                {"name": "local_time", "type": "string", "description": "格式化的本地时间字符串"}
            ]
        }

    @staticmethod
    def run(inputs):
        timezone = inputs.get("timezone", "UTC")
        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return {"local_time": now.strftime("%Y-%m-%d %H:%M:%S %A %Z")}
        except Exception as e:
            raise RuntimeError(f"Invalid timezone: {timezone}. Error: {e}")