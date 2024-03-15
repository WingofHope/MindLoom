import json

class Step:
    def __init__(self, step_data):
        for key, value in step_data.items():
            setattr(self, key, value)

class Process:
    def __init__(self, process_data):
        self.id = process_data('id')
        self.name = process_data('name')
        self.inputs = process_data('inputs', [])
        self.outputs = process_data('outputs', [])
        self.execution = process_data('execution', {})
        self.steps = [Step(step) for step in self.execution('steps', [])]

    def get_step_by_id(self, step_id):
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def is_subprocess(self):
        # 如果这个过程没有步骤，但有一个 'id'，我们可以认为它是子过程的引用
        return not self.steps and self.id

class Task:
    def __init__(self, task_json):
        self.id = task_json('id')
        self.name = task_json('name')
        self.description = task_json('description')
        self.inputs = task_json('inputs', [])
        self.processes = [Process(process) for process in task_json('processes', [])]

    def get_input(self, input_name):
        return next((item for item in self.inputs if item('name') == input_name), None)

    def get_process_by_name(self, process_name):
        for process in self.processes:
            if process.name == process_name:
                return process
        return None

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
