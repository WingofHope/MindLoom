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

    # 抽象校验执行模板，需子类实现
    @abstractmethod
    def validate_template_execution(execution):
        pass

    # 抽象流程处理与执行函数，需子类实现
    @abstractmethod
    def process(self):
        pass
############## 提示模板校验相关逻辑 ##############

    # 导入call模板校验函数
    @staticmethod
    def validate_template_call(call_dict):
        # 调用 Scheduler 的 validate_template_call
        try:
            return Scheduler.validate_template_call(call_dict)
        except Scheduler.TemplateError as e:
            # 如果发生异常，抛出 TypeProcess 中定义的 TemplateError
            raise TypeProcess.TemplateError(e.errors)

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
            # 校验Type字段
            if condition["type"] not in ["and", "or"]:
                errors.append(f"逻辑节点 'type' 必须是 'and' 或 'or'。")
            validated_condition["type"] = condition["type"]
            # 校验条件列表字段
            if "conditions" not in condition or not isinstance(condition["conditions"], list):
                errors.append(f"逻辑节点必须包含有效的 'conditions' 字段，并且它应该是一个数组。")
            else:
                # 校验 'conditions' 中的每个元素
                validated_condition["conditions"] = list()
                for sub_conditions in condition["conditions"]:
                    try:
                        validated_sub_conditions = TypeProcess.validate_template_condition(sub_conditions)  # 递归校验每个子条件
                        validated_condition["conditions"].append(validated_sub_conditions)
                    except TemplateError as e:
                        errors.extend(e.errors)  # 将错误添加到总错误列表
        # 比较节点校验
        elif "operation" in condition:
            # 校验操作数类型是否合法
            if condition["operation"] not in TypeProcess.CONDITION_OPERATIONS:
                errors.append(f"比较操作 'operation' 的值无效。有效值为：{', '.join(TypeProcess.CONDITION_OPERATIONS)}。")
            validated_condition["operation"] = condition["operation"]
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
                        
                        # 校验 value 是否符合规范

                validated_condition["left"] = condition["left"]
                validated_condition["right"] = condition["right"]

        else:
            errors.append(f"条件对象缺少有效的 'type' 或 'operation' 字段。")

        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise TypeProcess.TemplateError(errors)

        return validated_condition

############## 运行时执行相关逻辑 ##############

    def evaluate_value_node(self,value_node):
        """
        评估值节点，返回实际值。
        :param value_node: 包含 value_type 和 value 的字典
        :return: 实际值
        """
        parameters = self.process_instance.parameters
        if value_node["value_type"] == "variable":
            var_name = value_node["value"]
            if var_name not in parameters:
                raise RuntimeError(f"变量 '{var_name}' 在参数中未定义。")
            var_value = parameters[var_name]

            # 检查变量的值是否为基本类型
            if not isinstance(var_value, (int, float, str, list, bool)):
                raise RuntimeError(f"变量 '{var_name}' 的值类型不支持: {type(var_value)}。")
            return var_value

        elif value_node["value_type"] == "constant":
            return value_node["value"]
        else:
            raise RuntimeError(f"无效的 'value_type': {value_node['value_type']}。")

    def evaluate_condition(self,condition):
        """
        递归评估条件是否成立。
        :param condition: 条件的字典结构
        :return: 条件是否成立 (True 或 False)
        """
        # 判断是否为逻辑节点
        if "type" in condition:
            logic_type = condition["type"]

            # 根据逻辑类型递归评估子条件
            if logic_type == "and":
                return all(self.evaluate_condition(sub_condition) for sub_condition in condition["conditions"])
            elif logic_type == "or":
                return any(self.evaluate_condition(sub_condition) for sub_condition in condition["conditions"])

        # 判断是否为比较节点
        elif "operation" in condition:
            operation = condition["operation"]

            # 计算左操作数和右操作数的值
            left_value = self.evaluate_value_node(condition["left"])
            right_value = self.evaluate_value_node(condition["right"])

            # 根据操作符进行比较
            if operation == "equals":
                return left_value == right_value
            elif operation == "notEquals":
                return left_value != right_value
            elif operation == "greaterThan":
                return left_value > right_value
            elif operation == "lessThan":
                return left_value < right_value
            elif operation == "greaterThanOrEqual":
                return left_value >= right_value
            elif operation == "lessThanOrEqual":
                return left_value <= right_value
            elif operation == "contains":
                if not isinstance(left_value, (str, list)):
                    raise RuntimeError(f"'contains' 操作的左操作数必须是字符串或数组。")
                return right_value in left_value
            elif operation == "startsWith":
                if not isinstance(left_value, str):
                    raise RuntimeError(f"'startsWith' 操作的左操作数必须是字符串。")
                return left_value.startswith(right_value)
            elif operation == "endsWith":
                if not isinstance(left_value, str):
                    raise RuntimeError(f"'endsWith' 操作的左操作数必须是字符串。")
                return left_value.endswith(right_value)
