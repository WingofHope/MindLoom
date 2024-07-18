# src/engine/scheduler/scheduler.py

from ..base.base import Base

class Scheduler(Base):
    def __init__(self, id, secret):
        super().__init__(id, secret)

    def run(self):
        """ 执行流程 """
        raise NotImplementedError("Must implement run() method")