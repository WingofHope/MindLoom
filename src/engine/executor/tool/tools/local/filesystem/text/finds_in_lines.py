# src/engine/executor/tool/tools/local/filesystem/text/finds_in_lines.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.text.finds_in_lines",
            "name": "text_file_finds_in_lines",
            "description": "在文本文件的每一行中查找特定文本。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"},
                {"name": "search_text", "type": "string", "description": "要查找的文本内容"}
            ],
            "outputs": [
                {"name": "found_lines", "type": "array-object", "description": "包含查找文本的行号和行内容结构体的数组"}
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            pass
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")
