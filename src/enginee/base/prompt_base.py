class PromptBase:
    def __init__(self, config):
        self.config = config

    def load_config(self, config_file):
        """ 加载配置文件 """
        # 实现加载配置文件的逻辑
        pass

    def execute(self):
        """ 执行主要的操作 """
        raise NotImplementedError("Must implement execute() method")

    # 可以根据需要添加更多共通的方法