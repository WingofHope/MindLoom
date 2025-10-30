
import random
from engine.executor.tool.tools.tool_base import ToolBase

class RandomNumberGenerator(ToolBase):

	@staticmethod
	def metadata():
		return {
			"id": "random.number_generator",
			"name": "randomnumber_generator",
			"description": "生成指定范围内的随机整数，包含最小值和最大值",
			"inputs": [
				{"name": "min", "type": "number", "description": "随机数最小值（包含）"},
				{"name": "max", "type": "number", "description": "随机数最大值（包含）"}
			],
			"outputs": [
				{"name": "random_number", "type": "number", "description": "生成的随机整数"}
			]
		}
	
	def run(self, inputs):
		min_val = inputs.get("min")
		max_val = inputs.get("max")

		if min_val is None or max_val is None:
			raise ValueError("请提供随机数范围的最小和最大值")
		
		if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
			raise ValueError("参数必须是数字类型")
		
		if min_val > max_val:
			raise ValueError(f"无效的范围：{min_val} 不能大于 {max_val}")
		
		try:
			return {
				"random_number": random.randint(int(min_val), int(max_val))
			}
		except Exception as e:
			raise ValueError(f"生成随机数失败: {str(e)}")