# src/engine/executor/generator/generator.py

from ..executor import Executor

class Generator(Executor):
    def __init__(self, gen_id, inputs, secret):
        super().__init__(gen_id, inputs, secret)

    def run(self):
        """ 执行流程 """
        return {}