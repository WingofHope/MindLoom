# src/engine/executor/tool/tools/local/filesystem/text/write_text.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.text.write_text",
            "name": "text_file_write_text",
            "description": "将整个文本内容写入文件，覆盖原文件内容。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"},
                {"name": "text", "type": "string", "description": "要写入的文本内容"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            pass
        except Exception as e:
            raise ValueError(f"Python工具错误：{e}")
