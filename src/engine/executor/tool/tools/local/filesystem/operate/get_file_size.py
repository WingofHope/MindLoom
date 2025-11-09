# src/engine/executor/tool/tools/local/filesystem/operate/get_file_size.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.operate.get_file_size",
            "name": "get_file_size",
            "description": "获取指定文件的大小（以字节为单位）。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"}
            ],
            "outputs": [
                {"name": "file_size", "type": "number", "description": "文件的大小，单位为字节"}
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"s")