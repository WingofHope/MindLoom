# src/engine/executor/tool/tools/local/filesystem/object/close_file.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.object.close_file",
            "name": "close_file",
            "description": "关闭已打开的文件对象并释放资源。",
            "inputs": [
                {"name": "file", "type": "file", "description": "要关闭的文件对象"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"s")