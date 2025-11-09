# src/engine/executor/tool/tools/local/filesystem/text/insert_by_lines.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.text.insert_by_lines",
            "name": "text_file_insert_by_lines",
            "description": "在指定行号插入文本。在最前放插入line_number是0，最后方插入就是最后的行号。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"},
                {"name": "line_number", "type": "number", "description": "插入文本的行号"},
                {"name": "text", "type": "string", "description": "需要插入的文本内容"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            pass
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")
