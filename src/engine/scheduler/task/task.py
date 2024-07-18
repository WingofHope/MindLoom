# src/engine/scheduler/task/task.py

from ..scheduler import Scheduler

class Task(Scheduler):
    def __init__(self, id, secret):
        super().__init__(id, secret)

    def run(self, inputs):
        """ 执行流程 """
        return {'answer':'这个问题我不知道哦。'}