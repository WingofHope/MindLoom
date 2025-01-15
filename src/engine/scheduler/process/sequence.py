# src/engine/scheduler/process/sequence.py

from engine.scheduler.process.type_process import TypeProcess

class Sequence(TypeProcess):
############## 运行时相关逻辑 ##############
    def process(self):
        # 获取所有顺行步骤
        steps = self.process_instance.template["execution"]["steps"]
        # 顺序调用_call_execute函数执行模板中的call
        for step in steps:
            self.process_instance._call_execute(step["call"])

############## 提示模板校验相关函数 ##############

    # execution中的顺行流程模板校验
    @staticmethod
    def validate_template_execution(execution):
        errors = []  # 用于记录所有校验错误
        validated_execution = {}  # 用于存储验证通过的字段

        # 验证 execution 类型是否是 "sequence"
        if execution.get("type") != "sequence":
            errors.append(f" 'execution' -> 'type' 字段必须是 'sequence'。")
        else:
            validated_execution["type"] = execution["type"]

        # 验证 steps 字段
        if not isinstance(execution.get("steps"), list):
            errors.append(" 'execution' -> 'steps' 字段必须是一个列表。")
        else:
            # 初始化步骤字段
            validated_execution["steps"] = []
            order = 0
            for step in execution["steps"]:
                step_errors = []
                order += 1
                # 每个步骤校验
                try:
                    validated_step = Sequence.validate_template_execution_step(order,step)
                except Sequence.TemplateError as e:
                    error_messages = '\n'.join(str(error) for error in e.errors)
                    step_errors.append(f"第 {order} 步存在错误：{error_messages}")
                # 判断校验是否失败
                if step_errors:
                    errors.extend(step_errors)
                else:
                    validated_execution["steps"].append(validated_step)

        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise Sequence.TemplateError(errors)
        
        return validated_execution

    # 每个步骤模板校验
    @staticmethod
    def validate_template_execution_step(order,step):
        errors = []  # 用于记录所有校验错误
        validated_step = {}  # 用于存储验证通过的字段

        if not isinstance(step, dict):
            errors.append(f"步骤必须是结构对象。")
            raise Sequence.TemplateError(errors)

        # 验证 order 字段
        if "order" not in step:
            validated_step["order"] = order
        elif not isinstance(step["order"], int):
            errors.append(" 'step' -> 'order' 字段必须是整数。")
        elif step["order"] != order:
            errors.append(" 'step' -> 'order' 字段值和顺序不对应。")
        else:
            validated_step["order"] = step["order"]

        # 验证 description 字段
        if "description" not in step:
            errors.append(" 'step' 缺少 'description' 字段。")
        elif not isinstance(step["description"], str):
            errors.append(" 'step' -> 'description' 字段必须是字符串。")
        else:
            validated_step["description"] = step["description"]

        # 验证 call 字段
        try:
            validated_call = Sequence.validate_template_call(step.get("call",{}))
            validated_step["call"] = validated_call
        except Sequence.TemplateError as e:
            error_messages = '\n'.join(str(error) for error in e.errors)
            errors.append(f"第 {order} 步 'call' 字段存在错误：{error_messages}")
        
        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise Sequence.TemplateError(errors)
        
        return validated_step