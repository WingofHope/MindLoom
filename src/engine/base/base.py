# src/engine/base/base.py

class Base:
    def __init__(self, id, inputs, secret):
        pass

    def run(self):
        """ 执行流程 """
        raise NotImplementedError("Must implement run() method")