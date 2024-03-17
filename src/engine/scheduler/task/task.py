# src/engine/scheduler/task/task.py

from ..scheduler import Scheduler

class Task(Scheduler):
    def __init__(self, t_id, inputs, secret):
        super().__init__(t_id, inputs, secret)

    def run(self):
        """ 执行流程 """
        return {'answer':'这个问题我不知道哦。'}