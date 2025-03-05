# src/engine/executor/tool/tool.py

from config import config
from engine.executor.executor import Executor
from engine.executor.tool.tool_manager import tool_manager as tm

class Tool(Executor):
    def __init__(self, template_id, secret=None, task_id=None, parent_run_id=None):
        super().__init__(template_id, secret, task_id, parent_run_id)
    
    # 执行流程
    def _execute(self, inputs):
        tool_class = tm.load_tool(self.template_id)
        instant = tool_class()
        outputs = instant.run(inputs)
        return outputs