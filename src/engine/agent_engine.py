import sys
sys.path.append('/path/to/src')

from engine.base.definitions import Task, Process, load_json_file
from executor.generator import template_fill
# from services.tool_engine import tool_invocation

# from action_sender import send_action  

import pika
import json

def load_process_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

process_config = load_process_config('process_config.json')


def on_message_received(ch, method, properties, body):
    message = json.loads(body.decode('utf-8'))
    print(f"收到消息: {message}")

    # 假设新的JSON结构改变了任务文件的存放路径
    task = Task(load_json_file('新的任务文件路径.json'))

    for process_info in task.processes:
        process_id = process_info.id
        # 假设过程配置文件的路径或命名方式发生变化
        process_file = process_config.get(process_id)
        if process_file:
            process = Process(load_json_file('新的过程文件路径.json'))
            process_message(task, process, message)
        else:
            print(f"未知的流程 ID: {process_id}")


def process_message(task, process, message):
    print("正在处理消息...")
    inputs = {input_item["name"]: message["inputs"][input_item["name"]] for input_item in task.inputs}
    print(f"开始处理消息: {inputs}")

    for step in process.execution['steps']:
        print(f"处理步骤: {step['id']}")
        step_class = step.get('class')

        # 如果步骤是一个过程引用（没有 'class' 键）
        if step_class is None:
            # 查找并处理子过程
            subprocess_id = step['id']
            subprocess_file = process_config.get(subprocess_id)
            if subprocess_file:
                subprocess = Process(load_json_file(subprocess_file))
                process_message(task, subprocess, message)  # 递归调用
            else:
                print(f"未找到子过程: {subprocess_id}")
        else:
            # 对于常规步骤，使用步骤处理函数
            step_handler = step_handlers.get(step_class)
            if step_handler:
                result = step_handler(step, inputs)
                inputs.update(result)
                print(f"步骤 {step['id']} 结果: {result}")
            else:
                print(f"未知的步骤类别: {step_class}")

def handle_action(step, inputs):
    # 模拟 Action 的结果
    # 假设 Action 的作用是“过滤”或“修改”输入中的 'business_name'
    # 这里我们简单地返回原始输入作为模拟结果
    print(f"执行动作: {step['id']}")
    action_result = {
        "name": inputs.get("business_name", "默认行业名"),  # 如果输入中没有 'business_name'，使用默认值
        "type": "string",
        "description": "过滤后的行业名字"
    }

    # 模拟的结果将被用于后续步骤
    return {"business_name": action_result["name"]}


def handle_generator(step, inputs):
    print(f"执行生成器: {step['id']}")
    template_file = f"prompts/generator/{step['id']}.generator.json"
    result = template_fill(template_file, inputs)

    # try:
    #     result = template_fill(template_file, inputs)
    # except FileNotFoundError:
    #     print(f"模板文件 {template_file} 未找到")
    #     return {}
    # except ValueError as e:
    #     print(f"模板文件错误: {e}")
    #     return {}
    return result


def handle_tool(step, inputs):
    print(f"执行工具: {step['id']}")
    # 从 process_config 获取对应的工具模块路径
    tool_module_path = process_config.get(step['id'])
    if not tool_module_path:
        print(f"未找到对应的工具模块: {step['id']}")
        return {}

    # 假设每个工具都需要整个 inputs 作为参数
    result = tool_invocation(tool_module_path, inputs)
    return result

# 动态步骤处理函数映射
step_handlers = {
    'action': handle_action,
    'generator': handle_generator,
    'tool': handle_tool
}

def main():
    # RabbitMQ服务器连接参数
    credentials = pika.PlainCredentials('test', 'Xu4Fg0Ut6Sf1')
    connection_params = pika.ConnectionParameters(
        host='121.37.27.62',
        port=5672,  # 使用 AMQP 端口
        virtual_host='/',
        credentials=credentials
    )


    # 创建RabbitMQ连接
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # 声明队列，确保队列存在
    channel.queue_declare(queue='task_queue')

    # # 设置回调函数处理接收到的消息
    # channel.basic_consume(queue='task_queue', on_message_callback=on_message_received, auto_ack=True)

    # print('等待消息')
    # channel.start_consuming()
    
    channel.basic_consume(queue='task_queue', on_message_callback=on_message_received, auto_ack=True)
    print('等待消息')
    channel.start_consuming()
    
    # try:
    #     channel.basic_consume(queue='task_queue', on_message_callback=on_message_received, auto_ack=True)
    #     print('等待消息')
    #     channel.start_consuming()
    # except Exception as e:
    #     print(f"发生错误: {e}")
        
if __name__ == "__main__":
    main()

