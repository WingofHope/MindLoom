# src/engine/scheduler/task/task.py

# 导入调度器类和流程类
from engine.scheduler.scheduler import Scheduler
from engine.scheduler.process.process import Process

class Task(Scheduler):
    def __init__(self, template_id, secret=None, task_id=None, parent_run_id=None):
        super().__init__(template_id, secret, task_id, parent_run_id)
        # 添加Process类到类映射中（这个代码有点别扭，没有更好的办法就这样弄了，待改进）
        self.EXECUTION_CLASS_MAPPING['process'] = Process

############## 运行时相关逻辑 ##############

    # 重写执行函数，Task直接调用call即可
    def _scheduler_execute(self):
        # 设置主流程
        main_call = self.template["execution"]["call"]
        self._call_execute(main_call)

############## 提示模板相关逻辑 ##############

    # 校验类函数直接复用父类
    @classmethod
    def validate_template(cls, template):
        validated_template = super().validate_template(template)
        return validated_template

############## 提示模板校验相关函数 ##############

    # execution字段校验，包含正确call结构即可
    @staticmethod
    def validate_template_execution(execution):
        errors = []  # 用于记录所有校验错误
        validated_execution = {}  # 用于存储验证通过的字段

        # 首先检查是否是字典，不是则直接返回报错
        if not isinstance(execution, dict):
            errors.append("'execution' 必须是一个结构对象。")
            raise Task.TemplateError(errors)

        # 校验call字段存在且合法
        if "call" in execution and execution["call"] != None:
            try:
                validated_execution["call"] = Task.validate_template_call(execution["call"])
            except Task.TemplateError as e:
                error_messages = '\n'.join(str(error) for error in e.errors)
                errors.append(f"Task 模板中 'execution' -> 'call' 错误：{error_messages}")
        else:
            errors.append(f"Task 模板中 'execution' 字段必须包含 'call' 字段。")

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise Task.TemplateError(errors)

        # 返回经过验证的模板
        return validated_execution

