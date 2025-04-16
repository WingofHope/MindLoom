from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 环境变量配置
API_URL = "https://gitaigc.com/v1/chat/completions"  # 替换为实际的 API URL
API_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "你是一个税务咨询助手，用中文回答相关问题")

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # 获取请求数据
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            logger.warning("用户未提供消息内容")
            return jsonify({"error": "消息内容不能为空"}), 400

        # 构造请求头和请求体
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7
        }

        # 发送请求到 AI 服务
        logger.debug(f"请求 AI 服务，URL: {API_URL}, headers: {headers}, payload: {payload}")
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=int(os.getenv("REQUEST_TIMEOUT", 30))
        )

        # 检查响应状态码
        if response.status_code != 200:
            logger.error(f"AI 服务返回错误状态码: {response.status_code}, 响应内容: {response.text}")
            return jsonify({"error": f"AI服务暂不可用，状态码: {response.status_code}"}), 500

        # 解析响应内容
        result = response.json()
        logger.debug(f"AI 服务返回结果: {result}")
        return jsonify({"reply": result['choices'][0]['message']['content'].strip()})

    except requests.exceptions.Timeout:
        logger.error("请求超时")
        return jsonify({"error": "请求超时"}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"请求异常: {str(e)}")
        return jsonify({"error": f"请求异常: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}")
        return jsonify({"error": f"内部服务器错误: {str(e)}"}), 500