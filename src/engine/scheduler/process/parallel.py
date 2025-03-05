# src/engine/scheduler/process/parallel.py

import json
import concurrent.futures
import threading

from engine.scheduler.process.type_process import TypeProcess

class Parallel(TypeProcess):
    # 从配置文件或Task获取任务内单个流程最大并行数量
    MAX_PARALLEL_NUM = 10
    MAX_THREAD_TIMEOUT = 10000
############## 运行时相关逻辑 ##############
    def process(self):
        execution = self.process_instance.template["execution"]
        # 最大线程数量
        max_workers = min(execution.get("max_parallel_num", 10), self.MAX_PARALLEL_NUM)
        # 获取所有的并行执行体的模板对象并按照优先级排序
        parallels = execution["parallels"]
        parallels.sort(key=lambda x: x['priority'], reverse=True)
        futures = []  # 用来保存提交到线程池的任务的 Future 对象
        # 初始化线程池
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

        # 遍历所有并行任务，提交到线程池中执行
        for parallel in parallels:
            # 获取任务执行函数
            task_func = parallel["call"]

            # 向线程池提交任务，传递任务函数、优先级和超时
            parallel["future"] = self.executor.submit(self.process_instance._call_execute, task_func)
            futures.append(parallel["future"])

        # 等待所有任务执行完毕或超时
        for parallel in parallels:
            future = parallel["future"]
            thread_timeout = parallel.get("time_out",self.MAX_THREAD_TIMEOUT)
            call_id = parallel["call"]["id"]
            try:
                future.result(timeout=thread_timeout)  # 等待每个任务完成
                # 任务执行返回
                self.process_instance.runtime_log.add_record(f"任务 {call_id} 执行成功。")
            except concurrent.futures.TimeoutError:
                # 任务超时
                self.process_instance.runtime_log.add_record(f"任务 {call_id} 执行超时 {thread_timeout} 秒，终止退出。")

        # 关闭线程池
        self.executor.shutdown(wait=True)


############## 提示模板校验相关函数 ##############

    # execution中的顺行流程模板校验
    @staticmethod
    def validate_template_execution(execution):
        errors = []  # 用于记录所有校验错误
        validated_execution = {}  # 用于存储验证通过的字段

        # 验证 execution 类型是否是 "parallel"
        if execution.get("type") != "parallel":
            errors.append(f" 'execution' -> 'type' 字段必须是 'parallel'。")
        else:
            validated_execution["type"] = execution["type"]

        # 验证最大并行数字段
        max_value = execution.get("max_parallel_num", 10)
        if not isinstance(max_value, int) or max_value <= 0:
            errors.append("'execution' -> 'max_parallel_num' 字段必须是大于 0 的整数。")
        else:
            validated_execution["max_parallel_num"] = max_value

        # 验证 parallels 字段
        if not isinstance(execution.get("parallels"), list):
            errors.append(" 'execution' -> 'parallels' 字段必须是一个列表。")
        else:
            # 初始化并行字段
            validated_execution["parallels"] = []
            n = 0
            for parallel in execution["parallels"]:
                parallel_errors = []
                # 每个并行校验
                n += 1
                try:
                    validated_parallel = Parallel.validate_template_execution_parallel(parallel)
                except Parallel.TemplateError as e:
                    error_messages = '\n'.join(str(error) for error in e.errors)
                    parallel_errors.append(f"第 {n} 个并行任务存在错误：{error_messages}")
                # 判断校验是否失败
                if parallel_errors:
                    errors.extend(parallel_errors)
                else:
                    validated_execution["parallels"].append(validated_parallel)

        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise Parallel.TemplateError(errors)

        return validated_execution

    # 每个并行模板校验
    @staticmethod
    def validate_template_execution_parallel(parallel):
        errors = []  # 用于记录所有校验错误
        validated_parallel = {}  # 用于存储验证通过的字段

        if not isinstance(parallel, dict):
            errors.append(f"并行体必须是结构对象。")
            raise Parallel.TemplateError(errors)

        # 验证 priority 字段
        if "priority" not in parallel:
            validated_parallel["priority"] = 100
        elif not isinstance(parallel["priority"], int):
            errors.append(" 'parallel' -> 'priority' 字段必须是整数。")
        elif parallel["priority"] > 100 or parallel["priority"] < 0:
            errors.append(" 'parallel' -> 'priority' 字段值必须在0到100之间。")
        else:
            validated_parallel["priority"] = parallel["priority"]

        # 验证 time_out 字段
        if "time_out" not in parallel:
            validated_parallel["time_out"] = 600
        elif not isinstance(parallel["time_out"], int) or parallel["time_out"] <= 0:
            errors.append("'parallel' -> 'time_out' 字段必须是大于 0 的整数。")
        else:
            validated_parallel["time_out"] = parallel["time_out"]

        # 验证 description 字段
        if "description" not in parallel:
            errors.append(" 'parallel' 缺少 'description' 字段。")
        elif not isinstance(parallel["description"], str):
            errors.append(" 'parallel' -> 'description' 字段必须是字符串。")
        else:
            validated_parallel["description"] = parallel["description"]

        # 验证 call 字段
        try:
            validated_call = Parallel.validate_template_call(parallel.get("call",{}))
            validated_parallel["call"] = validated_call
        except Parallel.TemplateError as e:
            error_messages = '\n'.join(str(error) for error in e.errors)
            errors.append(f" 'call' 字段存在错误：{error_messages}")
        
        # 如果有错误，抛出 TemplateError 异常
        if errors:
            raise Parallel.TemplateError(errors)
        
        return validated_parallel
