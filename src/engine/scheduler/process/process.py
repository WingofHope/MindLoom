# src/engine/scheduler/process/process.py

# 导入配置文件从而确定根路径
from ....config import root_path
# 导入基础类
from src.engine.scheduler.scheduler import Scheduler

class Process(Scheduler):
    def __init__(self, id, secret):
        super().__init__(id, secret)
        # 添加Process类到类映射中
        self.EXECUTION_CLASS_MAPPING['process'] = Process

    # 校验提示模板是否合法
    def validate_template(self):
        super().validate_template()

    # 执行函数
    def run(self, inputs):
        # 校验输入参数是否合法
        self.validate_inputs(inputs)
        # 将输入参数设置到类变量列表
        self.set_parameters_by_inputs(inputs)
        ###########
        #需要在这里添加执行流程#
        print('coco')
        ###########
        # 获取输出参数
        outputs = self.get_outputs_by_parameters()
        return outputs