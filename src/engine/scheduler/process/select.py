# src/engine/scheduler/process/select.py

import json

from engine.scheduler.process.type_process import TypeProcess

class Select(TypeProcess):
############## 运行时相关逻辑 ##############
    def process(self):
        # 获取所有条件
        cases = self.process_instance.template["execution"]["cases"]
        cases_len = len(cases)
        parameters_json = json.dumps(self.process_instance.parameters,ensure_ascii=False)
        self.process_instance.runtime_log.add_record(f"分支流程判定开始，共 {cases_len} 条件判断分支流程，当前流程空间变量是 {parameters_json}。")
        # 分支判断
        for case in cases:
            # 模版填写condition的情况
            if "condition" in case:
                try:
                    # 获取判断是否命中
                    ret = self.evaluate_condition(case["condition"])
                except RuntimeError as re:
                    self.process_instance.runtime_log.add_record(f"判断触发错误:{str(re)} 。")
                    ret = False
                except Exception as e:
                    raise RuntimeError(f"条件判断触发未知错误: {str(e)}") from e
                # 如果满足条件，调用_call_execute函数执行模板中的call
                if ret:
                    # 记录命中的条件
                    con_json = json.dumps(case["condition"],ensure_ascii=False)
                    self.process_instance.runtime_log.add_record(f"满足条件 {con_json} 开始执行。")
                    # 调用_call_execute函数执行模板中的call
                    self.process_instance._call_execute(case["call"])
                    # 命中后跳出条件判断
                    break
            # 模板填写expression的情况
            elif "expression" in case:
                pass
        # 记录分支执行完毕的情况
        parameters_json = json.dumps(self.process_instance.parameters,ensure_ascii=False)
        self.process_instance.runtime_log.add_record(f"分支流程执行完毕，当前流程空间变量是 {parameters_json}。")

############## 提示模板校验相关函数 ##############

    # execution中的顺行流程模板校验
    @staticmethod
    def validate_template_execution(execution):
        errors = []  # 用于记录所有校验错误
        validated_execution = {}  # 用于存储验证通过的字段

        # 验证 execution 类型是否是 "select"
        if execution.get("type") != "select":
            errors.append(f" 'execution' -> 'type' 字段必须是 'select'。")
        else:
            validated_execution["type"] = execution["type"]

        # 验证 cases 字段
        if not isinstance(execution.get("cases"), list):
            errors.append(" 'execution' -> 'cases' 字段必须是一个列表。")
        else:
            # 初始化步骤字段
            validated_execution["cases"] = []
            order = 0
            for case in execution["cases"]:
                case_errors = []
                try:
                    validated_case = Select.validate_template_execution_case(case)
                except Select.TemplateError as e:
                    error_messages = '\n'.join(str(error) for error in e.errors)
                    case_errors.append(f"该条件存在错误：{error_messages}")
                # 判断校验是否失败
                if case_errors:
                    errors.extend(case_errors)
                else:
                    validated_execution["cases"].append(validated_case)

        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise Select.TemplateError(errors)
        
        return validated_execution

    # 每个步骤模板校验
    @staticmethod
    def validate_template_execution_case(case):
        errors = []  # 用于记录所有校验错误
        validated_case = {}  # 用于存储验证通过的字段

        if not isinstance(case, dict):
            errors.append(f"条件字段必须是结构对象。")
            raise Select.TemplateError(errors)

        # "expression" 或者 "condition" 至少存在一个
        if "expression" not in case and "condition" not in case:
            errors.append(" 'case' 必须存在 'expression' 或 “condition” 字段作为条件表达。")
        
        # 校验expression字段合法性
        if "expression" in case:
            if not isinstance(case["expression"], str):
                errors.append(" 'case' -> 'expression' 字段必须是字符串。")
            else:
                validated_case["expression"] = case["expression"]

        # 校验condition字段合法性
        if "condition" in case:
            try:
                validated_condition = TypeProcess.validate_template_condition(case.get("condition",{}))
                validated_case["condition"] = validated_condition
            except Select.TemplateError as e:
                error_messages = '\n'.join(str(error) for error in e.errors)
                errors.append(f" 'condition' 字段存在错误：{error_messages}")

        # 验证 description 字段
        if "description" not in case:
            errors.append(" 'case' 缺少 'description' 字段。")
        elif not isinstance(case["description"], str):
            errors.append(" 'case' -> 'description' 字段必须是字符串。")
        else:
            validated_case["description"] = case["description"]

        # 验证 call 字段
        try:
            validated_call = Select.validate_template_call(case.get("call",{}))
            validated_case["call"] = validated_call
        except Select.TemplateError as e:
            error_messages = '\n'.join(str(error) for error in e.errors)
            errors.append(f" 'call' 字段存在错误：{error_messages}")
        
        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise Select.TemplateError(errors)
        
        return validated_case
