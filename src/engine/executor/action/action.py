# src/engine/executor/action/action.py

from config import root_path
from engine.executor.executor import Executor
from services.rabbitmq.rabbitmq_producer import NoneBlockingMQClient, load_mq_config_parameters
import threading
import uuid
import json
import time

class Action(Executor):
    def __init__(self, template_id, secret=None, task_id=None, parent_run_id=None):
        super().__init__(template_id, secret, task_id, parent_run_id)
        parameters = load_mq_config_parameters()
        self.mq_client = NoneBlockingMQClient(parameters)
        self.lock = threading.Lock()  # 使用线程锁来确保线程安全
    
    # 执行流程
    def _execute(self, inputs):
        if self.commu_mode == "rabbitmq":
            return self._execute_rabbitmq(inputs)
        elif self.commu_mode == "localfile":
            return self._execute_localfile(inputs)
        elif self.commu_mode == "restapi":
            return self._execute_restapi(inputs)
        else:
            raise ValueError(f"不支持的通信模式: {self.commu_mode}")

    def _execute_rabbitmq(self, inputs):
        """通过RabbitMQ消息队列处理请求"""
        correlation_id = str(uuid.uuid4())
        request_message = json.dumps({
            "id": self.id,
            "inputs": inputs,
            "correlation_id": correlation_id
        })
        
        self.mq_client.send_one_msg('request_queue', request_message)

        timeout = 30
        start_time = time.time()

        while True:
            response = self.mq_client.fetch_one_msg('response_queue')
            
            if response is None:
                break
            
            response_data = json.loads(response)
            if response_data.get('correlation_id') == correlation_id:
                return json.loads(response_data['output'])
            else:
                self.mq_client.send_one_msg('response_queue', response)

            if time.time() - start_time > timeout:
                raise RuntimeError("action消息处理超时")

            time.sleep(1)

        raise RuntimeError(f"没有接收到Action返回。")

    def _execute_localfile(self, inputs):
        """通过本地文件处理请求"""
        import os
        import time
        
        # 定义请求和响应文件路径
        request_file = os.path.join(root_path, "tmp", "action_request.json")
        response_file = os.path.join(root_path, "tmp", "action_response.json")
        
        # 确保tmp目录存在
        os.makedirs(os.path.dirname(request_file), exist_ok=True)
        
        # 生成唯一的correlation_id
        correlation_id = str(uuid.uuid4())
        request_message = {
            "id": self.id,
            "inputs": inputs,
            "correlation_id": correlation_id
        }
        
        # 写入请求文件
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(request_message, f)
        
        # 等待响应
        timeout = 30
        start_time = time.time()
        
        while True:
            if os.path.exists(response_file):
                try:
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                        if response_data.get('correlation_id') == correlation_id:
                            # 清理文件
                            os.remove(response_file)
                            return json.loads(response_data['output'])
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
            
            if time.time() - start_time > timeout:
                raise RuntimeError("action本地文件处理超时")
                
            time.sleep(1)

    def _execute_restapi(self, inputs):
        """通过REST API处理请求"""
        import requests
        
        # 假设API端点配置在某处定义
        api_endpoint = "http://localhost:8000/action"  # 这里需要替换为实际的API端点
        
        correlation_id = str(uuid.uuid4())
        request_data = {
            "id": self.id,
            "inputs": inputs,
            "correlation_id": correlation_id
        }
        
        try:
            response = requests.post(
                api_endpoint,
                json=request_data,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            response_data = response.json()
            if response_data.get('correlation_id') == correlation_id:
                return json.loads(response_data['output'])
            else:
                raise RuntimeError("收到的响应correlation_id不匹配")
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"REST API请求失败: {str(e)}")
