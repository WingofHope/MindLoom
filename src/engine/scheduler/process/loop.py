# src/engine/scheduler/process/loop.py

import json

from engine.scheduler.process.type_process import TypeProcess

class Loop(TypeProcess):
############## 运行时相关逻辑 ##############
    def process(self):
        execution = self.process_instance.template["execution"]
        loop_type = execution["loop_type"]
        max_iterations = execution.get("max", 100)
        parameters_json = json.dumps(self.process_instance.parameters, ensure_ascii=False)
        self.process_instance.runtime_log.add_record(f"循环流程开始，循环类型: {loop_type}，当前流程空间变量: {parameters_json}。")
        
        iteration_count = 0
        while iteration_count < max_iterations:
            if loop_type == "condition":
                try:
                    ret = self.evaluate_condition(execution["condition"])
                except RuntimeError as re:
                    self.process_instance.runtime_log.add_record(f"条件判断触发错误: {str(re)}。")
                    ret = False
                except Exception as e:
                    raise RuntimeError(f"条件判断触发未知错误: {str(e)}") from e
                if not ret:
                    break
            elif loop_type == "count":
                count_value = execution["count"]["value"]
                if execution["count"]["value_type"] == "variable":
                    count_value = self.process_instance.parameters.get(count_value, 0)
                if iteration_count >= count_value:
                    break
            elif loop_type == "iterate":
                iterable_value = execution["iterable"]["value"]
                if execution["iterable"]["value_type"] == "variable":
                    iterable_value = self.process_instance.parameters.get(iterable_value, [])
                if iteration_count >= len(iterable_value):
                    break
                # 设置遍历数组参数值
                self.process_instance.parameters.set("iterable_each_value",iterable_value[iteration_count])
            
            iteration_count += 1
            parameters_json = json.dumps(self.process_instance.parameters, ensure_ascii=False)
            self.process_instance.runtime_log.add_record(f"第{iteration_count}次执行循环，当前流程空间变量: {parameters_json}。")
            self.process_instance._call_execute(execution["call"])
            
        
        parameters_json = json.dumps(self.process_instance.parameters, ensure_ascii=False)
        self.process_instance.runtime_log.add_record(f"循环流程执行完毕，当前流程空间变量: {parameters_json}。")


############## 提示模板校验相关函数 ##############

    @staticmethod
    def validate_template_execution(execution):
        errors = []  # 用于记录所有校验错误
        validated_execution = {}  # 用于存储验证通过的字段

        # 验证 execution 类型是否是 "loop"
        if execution.get("type") != "loop":
            errors.append("'execution' -> 'type' 字段必须是 'loop'。")
        else:
            validated_execution["type"] = execution["type"]

        # 验证 loop_type 字段
        valid_loop_types = {"condition", "count", "iterate"}
        if execution.get("loop_type") not in valid_loop_types:
            errors.append("'execution' -> 'loop_type' 字段必须是 'condition'、'count' 或 'iterate'。")
        else:
            validated_execution["loop_type"] = execution["loop_type"]

        # 验证 max 字段
        max_value = execution.get("max", 100)
        if not isinstance(max_value, int) or max_value <= 0:
            errors.append("'execution' -> 'max' 字段必须是大于 0 的整数。")
        else:
            validated_execution["max"] = max_value

        # 验证 condition 字段（仅当 loop_type 为 condition 时）
        if execution.get("loop_type") == "condition":
            try:
                validated_condition = TypeProcess.validate_template_condition(execution.get("condition", {}))
                validated_execution["condition"] = validated_condition
            except Loop.TemplateError as e:
                error_messages = '\n'.join(str(error) for error in e.errors)
                errors.append(f"'condition' 字段存在错误：{error_messages}")
        
        # 验证 count 字段（仅当 loop_type 为 count 时）
        if execution.get("loop_type") == "count":
            count = execution.get("count", {})
            if not isinstance(count, dict) or count.get("value_type") not in {"variable", "constant"}:
                errors.append("'count' 字段必须是一个包含 'value_type' 的对象，且值为 'variable' 或 'constant'。")
            elif count["value_type"] == "variable":
                if not isinstance(count.get("value"), str):
                    errors.append("'count' -> 'value' 字段必须是字符串。")
            elif count["value_type"] == "constant":
                if not (isinstance(count.get("value"), int) and 0 < count["value"] <= max_value):
                    errors.append(f"'count' -> 'value' 必须是一个大于 0 且小于等于 {max_value} 的整数。")
            validated_execution["count"] = count

        # 验证 iterable 字段（仅当 loop_type 为 iterate 时）
        if execution.get("loop_type") == "iterate":
            iterable = execution.get("iterable", {})
            if not isinstance(iterable, dict) or iterable.get("value_type") not in {"variable", "constant"}:
                errors.append("'iterable' 字段必须是一个包含 'value_type' 的对象，且值为 'variable' 或 'constant'。")
            elif iterable["value_type"] == "variable":
                if not isinstance(iterable.get("value"), str):
                    errors.append("'iterable' -> 'value' 字段必须是字符串。")
            elif iterable["value_type"] == "constant":
                if not (isinstance(iterable.get("value"), list) and len(iterable["value"]) <= max_value):
                    errors.append(f"'iterable' -> 'value' 必须是一个长度小于等于 {max_value} 的列表。")
            validated_execution["iterable"] = iterable

        # 验证 call 字段
        try:
            validated_call = Loop.validate_template_call(execution.get("call", {}))
            validated_execution["call"] = validated_call
        except Loop.TemplateError as e:
            error_messages = '\n'.join(str(error) for error in e.errors)
            errors.append(f"'call' 字段存在错误：{error_messages}")

        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise Loop.TemplateError(errors)

        return validated_execution
