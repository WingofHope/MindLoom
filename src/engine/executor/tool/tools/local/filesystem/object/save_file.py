# src/engine/executor/tool/tools/local/filesystem/object/save_file.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.object.save_file",
            "name": "save_file",
            "description": "将文件对象的缓存内容写回磁盘。",
            "inputs": [
                {"name": "file", "type": "file", "description": "文件对象"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"s")