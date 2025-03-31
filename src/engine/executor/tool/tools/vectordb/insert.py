import json
from pathlib import Path
from typing import Dict, List, Any

# import sys
# from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent.parent))  # 添加到MindLoom根目录
from engine.executor.tool.tool_base import ToolBase
from services.local_vectordb.local_vectordb_base import VectorDBHandler

class Insert(ToolBase):
	def __init__(self):
		super().__init__()
	
	@staticmethod
	def metadata():
		return {
			"id": "local_vectordb.insert",
			"name": "vectordb_insert",
			"description": "将向量、原始字符串和结构体数据插入指定的库表",
			"inputs": [
				{"name": "table_name", "type": "string", "description": "库表名"},
				{"name": "vector", "type": "array", "description": "向量数据（单个向量）"},
				{"name": "raw_string", "type": "string", "description": "向量化前的原始字符串"},
				{"name": "metadata", "type": "object", "description": "结构体数据（附加信息）"}
			],
			"outputs": [
				{"name": "success", "type": "bool", "description": "操作是否成功"}
			]
		}
	
	
	def insert_run(self, inputs: Dict) -> Dict[str, bool]:
		try:
			# 输入参数校验
			required_fields = ["table_name", "vector", "raw_string", "metadata"]
			for field in required_fields:
				if field not in inputs:
					raise ValueError(f"Missing required field: {field}")
			
			table_name = inputs["table_name"]
			vector = inputs["vector"]
			raw_string = inputs["raw_string"]
			metadata = inputs["metadata"]
			
			# 类型校验
			if not isinstance(vector, list) or not all(isinstance(x, (int, float)) for x in vector):
				raise TypeError("Invalid vector format")
			if not isinstance(raw_string, str):
				raise TypeError("raw_string must be string")
			
			# 加载/创建数据表
			data = VectorDBHandler._load_or_create_table(table_name)
			
			# 插入新记录
			new_record = {
				"index": data["next_index"],
				"vector": vector,
				"raw_string": raw_string,
				"metadata": metadata
			}
			data["records"].append(new_record)
			data["next_index"] += 1
			
			# 持久化存储
			VectorDBHandler._save_table(table_name)
			return {"success": True}
		
		except json.JSONDecodeError as e:
			print(f"JSON 解析失败: {str(e)}")
			return {"success": False}
		except Exception as e:
			print(f"插入操作异常: {str(e)}")
			return {"success": False}
	
	def run(self, inputs):
		# 测试插入操作
		result = self.insert_run(inputs)
		print(f"插入结果: {result}")
		print(f"文件存储在: {VectorDBHandler._get_storage_dir()}")
		return result
# 示例用法
# if __name__ == "__main__":
# 	# 测试插入操作
# 	test_input = {
# 		"table_name": "test_table",
# 		"vector": [0.1, 0.2, 0.4],
# 		"raw_string": "测试文本",
# 		"metadata": {"source": "test", "id": 123}
# 	}
#
# 	result = Insert.run(test_input)
# 	print(f"插入结果: {result}")
# 	print(f"文件应存储在: {VectorDBHandler._get_storage_dir()}")