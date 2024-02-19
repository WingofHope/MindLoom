class ProcessBase:
    def __init__(self, process_config):
        self.process_config = process_config

    def setup(self):
        """ 设置流程 """
        # 实现设置流程的逻辑
        pass

    def run(self):
        """ 执行流程 """
        raise NotImplementedError("Must implement run() method")

    # 可以添加更多流程控制相关的方法


# from .base.process_base import ProcessBase
# class LoopProcess(ProcessBase):
#     def run(self):
#         """ 实现循环流程的逻辑 """
#         # 具体的循环处理逻辑
#         pass