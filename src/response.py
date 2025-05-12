from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import json
import logging
import sys
import re
# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(
	level=logging.DEBUG,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/api/chat', methods=['POST'])
def chat():
	try:
		# 获取请求数据
		data = request.json
		if not data:
			logger.warning("请求体为空")
			return jsonify({"error": "请求体不能为空"}), 400
		
		user_message = data.get('message', '')
		if not user_message:
			logger.warning("用户未提供消息内容")
			return jsonify({"error": "消息内容不能为空"}), 400
		
		# 构造输入数据
		input_data = {"question": user_message}
		input_json = json.dumps(input_data, ensure_ascii=False)
		
		# 获取当前脚本所在目录
		current_dir = os.path.dirname(os.path.abspath(__file__))
		main_py_path = os.path.join(current_dir, "main.py")
		
		if not os.path.exists(main_py_path):
			logger.error(f"main.py 文件不存在于路径: {main_py_path}")
			return jsonify({"error": "服务配置错误"}), 500
		
		# 调用 main.py
		command = [
			sys.executable,  # 使用当前Python解释器
			main_py_path,
			"run",
			"-c", "task",
			"-id", "task_shuiwu_test0001",
			"-i", input_json
		]
		
		logger.debug(f"执行命令: {' '.join(command)}")
		logger.debug(f"工作目录: {current_dir}")
		logger.debug(f"输入数据: {input_json}")
		
		# 运行子进程并捕获输出
		try:
			result = subprocess.run(
				command,
				capture_output=True,
				text=True,
				encoding='utf-8',
				cwd=current_dir,
				timeout=30  # 设置超时时间
			)
		except subprocess.TimeoutExpired:
			logger.error("main.py 执行超时")
			return jsonify({"error": "服务响应超时"}), 504
		except Exception as e:
			logger.error(f"执行子进程失败: {str(e)}")
			return jsonify({"error": f"子进程执行失败: {str(e)}"}), 500
		
		# 记录完整的子进程输出
		logger.debug(f"子进程返回码: {result.returncode}")
		logger.debug(f"子进程标准输出: {result.stdout}")
		logger.debug(f"子进程错误输出: {result.stderr}")
		
		# 检查子进程是否成功执行
		if result.returncode != 0:
			error_msg = result.stderr.strip() if result.stderr else "未知错误"
			logger.error(f"main.py 执行失败 (返回码 {result.returncode}): {error_msg}")
			return jsonify({
				"error": "内部服务处理失败",
				"details": error_msg,
				"returncode": result.returncode
			}), 500
		
		# 检查是否有输出
		if not result.stdout:
			logger.error("main.py 没有返回任何输出")
			return jsonify({"error": "服务未返回有效响应"}), 500
		
		# 解析输出结果
		output = result.stdout.strip()
		logger.debug(f"output类型: {type(output)}")
		logger.debug(f"main.py 输出: {output}")
		
		
		try:
			pattern = r'<output>(.*?)</output>'
			response_data = re.findall(pattern, output, re.DOTALL)
			logger.debug(f"response_data  输出: {response_data}")
			return jsonify({"reply": response_data[0]})

		except Exception as e:
			logger.error(f"输出处理失败: {str(e)}")
			return jsonify({"error": f"输出处理失败: {str(e)}"}), 500
	
	except Exception as e:
		logger.exception("服务器发生未捕获异常")
		return jsonify({
			"error": "内部服务器错误",
			"details": str(e)
		}), 500


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=17943, debug=True)