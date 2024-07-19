# src/engine/scheduler/task/task.py

from ..scheduler import Scheduler

class Task(Scheduler):
    # 定义主流程call
    main_call = {}

    def __init__(self, id, secret):
        super().__init__(id, secret)
        # 设置主流程
        self.main_call = self.template["execution"]["call"]

    # 校验提示模板是否合法
    def validate_template(self):
        super().validate_template()
        # 校验execution是否包含call，该call作为主流程
        if 'call' not in self.template["execution"]:
            raise self.TemplateError("Task模板'execution'必须包含'call'。")
        # 提取住流程字典
        main_call = self.template["execution"]["call"]
        # 校验主流程字典合法
        self.validate_template_call(main_call)

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