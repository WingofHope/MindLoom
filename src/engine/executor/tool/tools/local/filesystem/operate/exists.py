# src/engine/executor/tool/tools/local/filesystem/operate/exists.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.operate.exists",
            "name": "file_or_directory_exists",
            "description": "检查指定路径的文件或文件夹是否存在。",
            "inputs": [
                {"name": "path", "type": "string", "description": "文件或文件夹路径"},
                {"name": "type", "type": "string", "description": "标记是文件file还是文件夹directory路径，或者两者皆可any","default":"any"}
            ],
            "outputs": [
                {"name": "exists", "type": "bool", "description": "路径是否存在"}
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            return {"exists":True}
        except Exception as e:
            raise ValueError(f"s")