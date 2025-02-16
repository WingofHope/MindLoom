
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.scheduler.task.task import Task

t_id = 'task_template_test0001'
inputs = {
    'question' : '我想去天安门后天，什么时间合适？',
}
task_instance = Task(t_id)
result = task_instance.run(inputs)
print(result)