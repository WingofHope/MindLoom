# src/engine/executor/tool/tools/local/filesystem/text/get_lines_count.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.text.get_lines_count",
            "name": "text_file_get_lines_count",
            "description": "获取指定文本文件的行数。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"}
            ],
            "outputs": [
                {"name": "lines_count", "type": "number", "description": "文件的行数"}
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            pass
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")