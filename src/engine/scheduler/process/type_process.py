# src/engine/scheduler/process/type_process.py

from abc import ABC, abstractmethod

from engine.scheduler.scheduler import Scheduler

class TypeProcess(ABC):
    # 在 TypeProcess 中定义 TemplateError 异常
    class TemplateError(Exception):
        def __init__(self, errors):
            super().__init__("Template 格式校验失败：")
            self.errors = errors

    # 定义流程条件，选择分支和循环会用到
    CONDITION_OPERATIONS = [
        "equals", "notEquals", "greaterThan", "lessThan", "greaterThanOrEqual", "lessThanOrEqual", 
        "contains", "startsWith", "endsWith"
    ]

    # 构造函数导入process实例
    def __init__(self, process_instance):
        self.process_instance = process_instance

    # process函数调用转化本类函数——validate_template_call
    @staticmethod
    def validate_template_call(call_dict):
        # 调用 Scheduler 的 validate_template_call
        try:
            return Scheduler.validate_template_call(call_dict)
        except Scheduler.TemplateError as e:
            # 如果发生异常，抛出 TypeProcess 中定义的 TemplateError
            raise TypeProcess.TemplateError(e.errors)

    # 抽象校验执行模板，需子类实现
    @abstractmethod
    def validate_template_execution(execution):
        pass

    # 抽象流程处理与执行函数，需子类实现
    @abstractmethod
    def process(self):
        pass

    # 条件校验模板，封装提供子类使用
    @staticmethod
    def validate_template_condition(condition):
        errors = []  # 用于记录所有校验错误
        validated_condition = {}  # 用于存储验证通过的字段

        # 校验 condition 必须是字典类型
        if not isinstance(condition, dict):
            errors.append(f"条件字段必须是结构对象。")
            raise TypeProcess.TemplateError(errors)

        # 逻辑节点校验
        if "type" in condition:
            if condition["type"] not in ["and", "or"]:
                errors.append(f"逻辑节点 'type' 必须是 'and' 或 'or'。")
            if "conditions" not in condition or not isinstance(condition["conditions"], list):
                errors.append(f"逻辑节点必须包含有效的 'conditions' 字段，并且它应该是一个数组。")
            else:
                # 校验 'conditions' 中的每个元素
                for sub_condition in condition["conditions"]:
                    try:
                        TypeProcess.validate_template_condition(sub_condition)  # 递归校验每个子条件
                    except TemplateError as e:
                        errors.extend(e.errors)  # 将错误添加到总错误列表

        # 比较节点校验
        elif "operation" in condition:
            if condition["operation"] not in TypeProcess.CONDITION_OPERATIONS:
                errors.append(f"比较操作 'operation' 的值无效。有效值为：{', '.join(TypeProcess.CONDITION_OPERATIONS)}。")

            # 校验左侧和右侧的操作数
            if "left" not in condition or "right" not in condition:
                errors.append(f"比较节点必须包含 'left' 和 'right' 字段。")
            else:
                if not isinstance(condition["left"], dict) or not isinstance(condition["right"], dict):
                    errors.append(f"比较节点的 'left' 和 'right' 必须是有效的值节点。")

                # 校验值节点的 value_type 和 value
                for side in ["left", "right"]:
                    if "value_type" not in condition[side] or "value" not in condition[side]:
                        errors.append(f"'{side}' 字段必须包含 'value_type' 和 'value'。")
                    else:
                        value_type = condition[side]["value_type"]
                        if value_type not in ["variable", "constant"]:
                            errors.append(f"'{side}' 字段的 'value_type' 必须是 'variable' 或 'constant'。")
                        # 这里可以根据具体的业务需求校验 value 是否符合规范，如类型检查

        else:
            errors.append(f"条件对象缺少有效的 'type' 或 'operation' 字段。")

        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise TypeProcess.TemplateError(errors)

        return validated_condition

