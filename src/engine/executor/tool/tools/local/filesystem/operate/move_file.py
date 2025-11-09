# src/engine/executor/tool/tools/local/filesystem/operate/move_file.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.operate.move_file",
            "name": "move_file",
            "description": "将文件从一个路径移动到另一个路径。",
            "inputs": [
                {"name": "source_path", "type": "string", "description": "源文件路径"},
                {"name": "destination_path", "type": "string", "description": "目标文件路径"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            return {}
        except Exception as e:
            raise ValueError(f"s")