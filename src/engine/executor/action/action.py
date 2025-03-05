# src/engine/executor/action/action.py

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
        # 测试样例，需要删除
        if self.id == "action_weather0001":
            outputs = {
                "weather_result": "{\"results\":[{\"location\":{\"id\":\"WX4FBXXFKE4F\",\"name\":\"北京\",\"country\":\"CN\",\"path\":\"北京,北京,中国\",\"timezone\":\"Asia/Shanghai\",\"timezone_offset\":\"+08:00\"},\"daily\":[{\"date\":\"2024-12-03\",\"text_day\":\"晴\",\"code_day\":\"0\",\"text_night\":\"多云\",\"code_night\":\"4\",\"high\":\"9\",\"low\":\"-3\",\"rainfall\":\"0.00\",\"precip\":\"0.00\",\"wind_direction\":\"西南\",\"wind_direction_degree\":\"225\",\"wind_speed\":\"8.4\",\"wind_scale\":\"2\",\"humidity\":\"47\"},{\"date\":\"2024-12-04\",\"text_day\":\"多云\",\"code_day\":\"4\",\"text_night\":\"晴\",\"code_night\":\"1\",\"high\":\"8\",\"low\":\"-2\",\"rainfall\":\"0.00\",\"precip\":\"0.00\",\"wind_direction\":\"西南\",\"wind_direction_degree\":\"225\",\"wind_speed\":\"8.4\",\"wind_scale\":\"2\",\"humidity\":\"43\"},{\"date\":\"2024-12-05\",\"text_day\":\"晴\",\"code_day\":\"0\",\"text_night\":\"多云\",\"code_night\":\"4\",\"high\":\"9\",\"low\":\"-1\",\"rainfall\":\"0.00\",\"precip\":\"0.00\",\"wind_direction\":\"西北\",\"wind_direction_degree\":\"315\",\"wind_speed\":\"3.0\",\"wind_scale\":\"1\",\"humidity\":\"59\"}],\"last_update\":\"2024-12-03T08:00:00+08:00\"}]}"
            }
            return outputs
        # 测试样例，需要删除

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
                return json.loads(response_data['output'])  # 返回解码后的输出数据
            else:
                self.mq_client.send_one_msg('response_queue', response)

            if time.time() - start_time > timeout:
                raise RuntimeError("action消息处理超时")

            time.sleep(1)

        raise RuntimeError(f"没有接收到Action返回。")
