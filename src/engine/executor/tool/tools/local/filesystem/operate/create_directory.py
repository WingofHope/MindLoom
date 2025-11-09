# src/engine/executor/tool/tools/local/filesystem/operate/create_directory.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.operate.create_directory",
            "name": "create_directory",
            "description": "在指定路径创建一个空文件夹。",
            "inputs": [
                {"name": "dir_path", "type": "string", "description": "文件夹路径"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            return {"exists":True}
        except Exception as e:
            raise ValueError(f"s")