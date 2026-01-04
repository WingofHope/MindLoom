# src/engine/executor/tool/tools/mindloom/identity

from engine.executor.tool.tools.tool_base import ToolBase

class Identity(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "mindloom.identity",
            "name": "identity",
            "description": "原样返回",
            "inputs": [
                {"name": "input", "type": "object", "description": "任意的对象输入"}
            ],
            "outputs": [
                {"name": "output", "type": "object", "description": "原样返回对象输入"}
            ]
        }

    @staticmethod
    def run(inputs):
        output = {
            "output" : inputs["input"]
        }
        return output