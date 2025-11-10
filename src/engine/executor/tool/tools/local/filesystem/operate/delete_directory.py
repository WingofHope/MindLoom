# src/engine/executor/tool/tools/local/filesystem/operate/delete_directory.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.operate.delete_directory",
            "name": "delete_directory",
            "description": "删除指定路径的文件。",
            "inputs": [
                {"name": "dir_path", "type": "string", "description": "文件夹路径"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"s")