# src/engine/executor/executor.py

from engine.base.base import Base

class Executor(Base):
    def __init__(self, template_id, secret=None, task_id=None, parent_run_id=None):
        super().__init__(template_id, secret, task_id, parent_run_id)

############## 执行相关逻辑 ##############

    def _execute(self, inputs):
        return {}