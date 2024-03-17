import pika
import json

def send_message_to_queue(message, queue_name='task_queue'):
    credentials = pika.PlainCredentials('test', 'Xu4Fg0Ut6Sf1')
    connection_params = pika.ConnectionParameters(
        host='121.37.27.62',
        port=5672,
        virtual_host='/',
        credentials=credentials
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)
    encoded_message = json.dumps(message, ensure_ascii=False).encode('utf-8')

    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=encoded_message)
    print(f"消息已发送到队列 {queue_name}")
    connection.close()

def on_received_message(ch, method, properties, body):
    received_message = json.loads(body.decode('utf-8'))
    print(f"接收到消息: {received_message}")

    # 示例：处理接收到的消息
    processed_message = {
        "id": received_message.get("id", "default_id"),
        "processed_data": "这里是处理后的数据"
    }

    # 使用send_message_to_queue函数将处理后的消息发送到另一个队列
    send_message_to_queue(processed_message, 'another_queue_name')

def main():
    credentials = pika.PlainCredentials('test', 'Xu4Fg0Ut6Sf1')
    connection_params = pika.ConnectionParameters(
        host='121.37.27.62',
        port=5672,
        virtual_host='/',
        credentials=credentials
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    queue_name = 'source_queue_name'
    channel.queue_declare(queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=on_received_message, auto_ack=True)

    print('开始监听消息...')
    channel.start_consuming()

if __name__ == "__main__":
    main()
