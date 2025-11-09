# src/engine/executor/tool/tools/local/filesystem/operate/delete_file.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.operate.delete_file",
            "name": "delete_file",
            "description": "删除指定路径的文件。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"s")