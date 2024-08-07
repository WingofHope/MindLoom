# src/engine/scheduler/task/task.py

# 导入配置文件从而确定根路径
from ....config import root_path
from src.engine.scheduler.scheduler import Scheduler
from src.engine.scheduler.process.process import Process

class Task(Scheduler):
    # 定义主流程调用
    main_call = {}

    def __init__(self, id, secret):
        super().__init__(id, secret)
        # 添加Process类到类映射中
        self.EXECUTION_CLASS_MAPPING['process'] = Process
        # 设置主流程
        self.main_call = self.template["execution"]["call"]

    # 校验提示模板是否合法
    def validate_template(self):
        super().validate_template()
        # 校验execution是否包含call，该call作为主流程
        if 'call' not in self.template["execution"]:
            raise self.TemplateError("Task模板'execution'必须包含'call'。")
        # 提取主流程字典
        call_dict = self.template["execution"]["call"]
        # 校验主流程字典合法
        self.validate_template_call(call_dict)

    # 执行函数
    def run(self, inputs):
        # 校验输入参数是否合法
        self.validate_inputs(inputs)
        # 将输入参数设置到类变量列表
        self.set_parameters_by_inputs(inputs)
        # 执行主流程调用
        self.call_execute(self.main_call)
        # 获取输出参数
        outputs = self.get_outputs_by_parameters()
        return outputs