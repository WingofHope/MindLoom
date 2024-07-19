# src/engine/scheduler/task/task.py

from ..scheduler import Scheduler

class Task(Scheduler):
    # 定义主流程call
    main_call = {}

    def __init__(self, id, secret):
        super().__init__(id, secret)

    # 校验提示模板是否合法
    def validate_template(self):
        super().validate_template()
        if 'call' not in self.template["execution"]:
            raise self.TemplateError("Task模板'execution'必须包含'call'。")
        self.main_call = self.template["execution"]["call"]
        self.validate_template_call(self.main_call)

    # 执行函数
    def run(self, inputs):
        self.validate_inputs(inputs)
        self.set_parameters_by_inputs(inputs)
        self.call_execute(self.main_call)
        outputs = self.get_outputs_by_parameters()
        return outputs