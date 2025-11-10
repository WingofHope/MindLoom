# src/engine/executor/tool/tools/local/filesystem/text/delete_lines_range.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.text.delete_lines_range",
            "name": "text_file_delete_lines_range",
            "description": "删除文本文件中指定范围的行。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"},
                {"name": "start_line", "type": "number", "description": "起始行号"},
                {"name": "end_line", "type": "number", "description": "结束行号"}
            ],
            "outputs": []
        }
        
    @staticmethod
    def run(inputs):
        try:
            pass
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")
