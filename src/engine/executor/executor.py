# src/engine/executor/executor.py

from ..base.base import Base

class Executor(Base):
    def __init__(self, id, secret):
        super().__init__(id, secret)

    def run(self, inputs):
        """ 执行流程 """
        raise NotImplementedError("Must implement run() method")