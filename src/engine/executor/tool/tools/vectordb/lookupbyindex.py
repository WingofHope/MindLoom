from pathlib import Path
from typing import Dict, Any
import json
# import sys
# from pathlib import Path
#
# project_root = Path(__file__).resolve().parents[4]
# sys.path.append(str(project_root))

from engine.executor.tool.tool_base import ToolBase
from services.local_vectordb.local_vectordb_base import VectorDBHandler



class LookupByIndex(ToolBase):
	def __init__(self):
		super().__init__()

	@staticmethod
	def metadata():
		return {
			"id": "local_vectordb.lookup_by_index",
			"name": "lookup_by_index",
			"description": "根据索引号查找向量的原始字符串和附加的结构体数据。",
			"inputs": [
				{"name": "table_name", "type": "string", "description": "库表名"},
				{"name": "index", "type": "number", "description": "向量记录的索引号"}
			],
			"outputs": [
				{"name": "raw_string", "type": "string", "description": "向量化前的原始字符串"},
				{"name": "metadata", "type": "object", "description": "结构体数据（附加信息）"}
			]
		}
	
	def lookup_by_index_run(self, inputs: Dict) -> Dict[str, Any]:
		try:
			# 输入参数校验
			required_fields = ["table_name", "index"]
			for field in required_fields:
				if field not in inputs:
					raise ValueError(f"Missing required field: {field}")
			
			table_name = inputs["table_name"]
			index = inputs["index"]
			
			# 类型校验
			if not isinstance(index, int) or index < 0:
				raise TypeError("Index must be a non-negative integer")
			
			# 加载数据表
			data = VectorDBHandler._load_or_create_table(table_name)
			
			# 查找记录
			for record in data["records"]:
				if record["index"] == index:
					return {
						"raw_string": record["raw_string"],
						"metadata": record["metadata"]
					}
			
			# 如果没有找到记录
			raise ValueError(f"Record with index {index} not found in table {table_name}")
		
		except Exception as e:
			print(f"查找操作异常: {str(e)}")
			return {"raw_string": None, "metadata": None}
	
	def run(self, inputs):
		# 执行查找操作
		result = self.lookup_by_index_run(inputs)
		return result


# #
# if __name__ == "__main__":
#
# 	test_input = {
# 		"table_name": "test_table",
# 		"index": 13
# 	}
#
# 	result = LookupByIndex.run(test_input)
#	print(f"查找结果: {result}")