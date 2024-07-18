# src/engine/executor/generator/generator.py

from ..executor import Executor

class Generator(Executor):
    def __init__(self, gen_id, secret):
        super().__init__(gen_id, secret)

    def run(self):
        """ 执行流程 """
        return {}