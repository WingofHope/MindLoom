# src/engine/scheduler/scheduler.py

from ..base.base import Base

class Scheduler(Base):
    def __init__(self, id, inputs, secret):
        super().__init__(id, inputs, secret)

    def run(self):
        """ 执行流程 """
        raise NotImplementedError("Must implement run() method")