# src/engine/executor/tool/tools/local/filesystem/text/append_text.py

from engine.executor.tool.tools.tool_base import ToolBase

class LocalTime(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "local.filesystem.text.append_text",
            "name": "text_file_append_text",
            "description": "在文本文件的末尾追加文本。",
            "inputs": [
                {"name": "file_path", "type": "string", "description": "文件路径"},
                {"name": "text", "type": "string", "description": "需要追加的文本内容"}
            ],
            "outputs": []
        }

    @staticmethod
    def run(inputs):
        try:
            pass
        except Exception as e:
            raise ValueError(f"")