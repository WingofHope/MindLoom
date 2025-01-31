# src/engine/scheduler/process/process.py

# 导入调度器类
from engine.scheduler.scheduler import Scheduler

# 导入各类处理流程
from engine.scheduler.process.sequence import Sequence
from engine.scheduler.process.select import Select
from engine.scheduler.process.loop import Loop
from engine.scheduler.process.parallel import Parallel

class Process(Scheduler):
    # 定义各个流程类：顺行，分支选择，循环，并行
    PROCESS_TYPES_MAPPING = {
        'sequence': Sequence,
        'select': Select,
        'loop': Loop,
        'parallel': Parallel
    }
    # 实例化流程类
    process_instance = None

    def __init__(self, template_id, secret=None, task_id=None, parent_run_id=None):
        super().__init__(template_id, secret, task_id, parent_run_id)
        # 添加Process类到类映射中（这个代码有点别扭，没有更好的办法就这样弄了，待改进）
        self.EXECUTION_CLASS_MAPPING['process'] = Process
        # 根据流程类型创建具体的流程类
        ProcessType = Process.PROCESS_TYPES_MAPPING[self.template["execution"]["type"]]
        self.process_instance = ProcessType(self)

############## 运行时相关逻辑 ##############

    # 重写执行函数，根据不同的流程调用不同的执行策略
    def _scheduler_execute(self):
        # 调用不同流程类的process进行执行
        self.process_instance.process()
        
############## 提示模板相关逻辑 ##############

    # 校验类函数直接复用父类
    @classmethod
    def validate_template(cls, template):
        validated_template = super().validate_template(template)
        return validated_template

############## 提示模板校验相关函数 ##############

    # execution字段校验，根据不同的类型有不同的校验
    @staticmethod
    def validate_template_execution(execution):
        errors = []  # 用于记录所有校验错误
        validated_execution = {}  # 用于存储验证通过的字段

        # 首先检查是否是字典，不是则直接返回报错
        if not isinstance(execution, dict):
            errors.append("'execution' 必须是一个结构对象。")
            raise Process.TemplateError(errors)

        # 检查 "type" 值是否存在且合法
        if "type" not in execution:
            errors.append(" 'execution' 必须包含 'type' 字段。")
        elif not isinstance(execution["type"], str):
            errors.append(" 'execution' -> 'type' 字段必须是有效的字符串类型。")
        elif execution["type"] not in Process.PROCESS_TYPES_MAPPING:
            process_types = ', '.join(f'{t}' for t in Process.PROCESS_TYPES_MAPPING)
            errors.append(f" 'execution' -> 'type' 字段必须是 {process_types} 的一种。")
        else:
            validated_execution["type"] = execution["type"]

        # 如果类型错误直接返回，不需要再校验了
        if errors:
            raise Process.TemplateError(errors)

        # 获取对应的流程类
        ProcessType = Process.PROCESS_TYPES_MAPPING[validated_execution["type"]]
        
        # 具体流程类型校验其对应的模板
        try:
            validated_execution = ProcessType.validate_template_execution(execution)
        except ProcessType.TemplateError as e:
            error_messages = '\n'.join(str(error) for error in e.errors)
            errors.append(f"Process 模板中 'execution' 错误：{error_messages}")

        if errors:
            raise Process.TemplateError(errors)
        
        return validated_execution