# src/engine/executor/tool/tools/local/filesystem/text/read_text.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.text.read_text",
            "name": "text_file_read_text",
            "description": "读取整个文本文件的内容。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"}
            ],
            "outputs": [
                {"name": "text", "type": "string", "description": "文本文件的所有内容"}
            ]
        }

    @staticmethod
    def run(inputs):
        try:
            pass
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")