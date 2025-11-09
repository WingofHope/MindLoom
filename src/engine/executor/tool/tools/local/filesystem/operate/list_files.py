# src/engine/executor/tool/tools/local/filesystem/operate/list_files.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.operate.list_files",
            "name": "list_files_in_directory",
            "description": "列出指定路径下所有的文件和文件夹。",
            "inputs": [
                {"name": "dir_path", "type": "string", "description": "文件夹路径"}
            ],
            "outputs": [
                {"name": "files", "type": "array-object", "description": "路径下的所有文件和文件夹名称"}
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"s")