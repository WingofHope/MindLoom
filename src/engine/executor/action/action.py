# src/engine/executor/action/action.py

from ....config import root_path
from src.engine.executor.executor import Executor

class Action(Executor):
    def __init__(self, id, secret):
        super().__init__(id, secret)

    def run(self, inputs):
        """ 执行流程 """
        return {}