# src/engine/executor/tool/tools/calculator/add.py

from engine.executor.tool.tools.tool_base import ToolBase

class Add(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "calculator.add",
            "name": "calculator_add",
            "description": "执行加法运算",
            "inputs": [
                {"name": "addend", "type": "number", "description": "第一个加数"},
                {"name": "augend", "type": "number", "description": "第二个加数"}
            ],
            "outputs": [
                {"name": "sum", "type": "number", "description": "加法结果"}
            ]
        }

    @staticmethod
    def run(inputs):
        addend = inputs["addend"]
        augend = inputs["augend"]
        return {"sum": addend + augend}