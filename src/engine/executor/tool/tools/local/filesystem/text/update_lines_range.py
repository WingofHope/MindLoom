# src/engine/executor/tool/tools/local/filesystem/text/update_lines_range.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.text.update_lines_range",
            "name": "text_file_update_lines_range",
            "description": "通过行数组更新文本文件中指定范围的行内容，原行内容将被删除新增为新内容。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"},
                {"name": "start_line", "type": "number", "description": "起始行号"},
                {"name": "end_line", "type": "number", "description": "结束行号"},
                {"name": "new_lines", "type": "array-string", "description": "需要替换的每行内容数组，可以与原行数不一致"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            pass
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")
