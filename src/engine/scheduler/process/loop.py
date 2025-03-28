# src/engine/scheduler/process/loop.py

import json

from engine.scheduler.process.type_process import TypeProcess

class Loop(TypeProcess):
    # 从配置文件或Task获取任务内所有循环流程最大循环次数，暂定1000
    MAX_LOOP_COUNT = 1000
############## 运行时相关逻辑 ##############
    def process(self):
        execution = self.process_instance.template["execution"]
        loop_type = execution["loop_type"]

        # 获取最大循环次数，是任务（配置文件）限制，循环体模板限制的最小值
        max_loop_num = min(execution.get("max_loop_num", 100), self.MAX_LOOP_COUNT)

        count_num = 0
        iterable = list()
        iterable_name = ""
        # 计数循环情况的循环次数获取
        if loop_type == "count":
            count_value = execution["count"]["value"]
            if execution["count"]["value_type"] == "variable":
                count_num = self.process_instance.parameters.get(count_value, 0)
            elif execution["count"]["value_type"] == "constant":
                count_num = count_value
            if not isinstance(count_num, int) or count_num < 0:
                raise RuntimeError(f"循环次数参数 {count_value} 必须是大于0的整数。")
        # 遍历循环情况的遍历列表和循环次数获取
        elif loop_type == "iterate":
            iterable_value = execution["iterable"]["value"]
            if execution["iterable"]["value_type"] == "variable":
                iterable = self.process_instance.parameters.get(iterable_value, [])
                iterable_name = iterable_value + "_each_value"
            elif execution["iterable"]["value_type"] == "constant":
                iterable = iterable_value
                iterable_name = "_iterable_each_value"
            if not isinstance(iterable, list):
                raise RuntimeError(f"循环遍历参数类型错误，必须是一个列表。")
            count_num = len(iterable)

        # 打印流程开始记录
        parameters_json = json.dumps(self.process_instance.parameters, ensure_ascii=False)
        self.process_instance.runtime_log.add_record(f"循环流程开始，循环类型: {loop_type}，当前流程空间变量: {parameters_json}。")

        # 满足初始条件循环次数小于循环最大值
        iteration_count = 0
        while iteration_count < max_loop_num:
            # 如果是条件循环，判断条件满足继续，否则跳出循环
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
                if iteration_count >= count_num:
                    break
            # 如果是遍历循环，判断循环次数是否小于遍历变量长度，否则跳出循环，并且设置循环变量到程序内存空间
            elif loop_type == "iterate":
                if iteration_count >= count_num:
                    break
                # 设置遍历数组参数值
                self.process_instance.parameters[iterable_name] = iterable[iteration_count]
            
            # 设置循环次数变量
            iteration_count += 1
            self.process_instance.parameters["_loop_count"] = iteration_count
            # 打印执行前log
            parameters_json = json.dumps(self.process_instance.parameters, ensure_ascii=False)
            self.process_instance.runtime_log.add_record(f"循环体即将第 {iteration_count} 次执行，当前流程空间变量: {parameters_json}。")
            # 执行循环体call
            self.process_instance._call_execute(execution["call"])
            
        # 执行完毕打印记录
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

        # 验证 max_loop_num 字段
        max_value = execution.get("max_loop_num", 100)
        if not isinstance(max_value, int) or max_value <= 0:
            errors.append("'execution' -> 'max_loop_num' 字段必须是大于 0 的整数。")
        else:
            validated_execution["max_loop_num"] = max_value

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
