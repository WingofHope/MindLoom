# src/engine/executor/tool/tools/local/filesystem/operate/rename_file.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.operate.rename_file",
            "name": "rename_file",
            "description": "重命名指定路径的文件。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"},
                {"name": "new_name", "type": "string", "description": "新的文件名"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"s")