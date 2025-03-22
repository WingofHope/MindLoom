from pathlib import Path
from typing import Dict, Any
import json

#未对超出index的数据做出处理，默认返回值类型出错
class VectorDBHandler:
	_memory_cache: Dict[str, Dict] = {}  # 内存缓存 {table_name: data}
	
	@classmethod
	def _get_storage_dir(cls) -> Path:
		"""计算存储目录路径"""
		current_file = Path(__file__).resolve()  # 当前脚本的绝对路径
		# 从当前脚本路径回溯到项目根目录（假设项目根目录为 MindLoom-develop）
		project_root = current_file.parent.parent.parent.parent.parent.parent
		# 目标路径：项目根目录/database/vector database
		return project_root / "database" / "vector database"
	
	@classmethod
	def _load_table(cls, table_name: str) -> Dict:
		"""加载表数据（仅读取，不写入）"""
		if table_name in cls._memory_cache:
			return cls._memory_cache[table_name]
		
		storage_dir = cls._get_storage_dir()
		file_path = storage_dir / f"{table_name}.json"
		
		try:
			if file_path.exists():
				with open(file_path, "r", encoding="utf-8") as f:
					data = json.load(f)
				cls._memory_cache[table_name] = data
				return data
			else:
				raise FileNotFoundError(f"Table {table_name} does not exist")
		except Exception as e:
			raise RuntimeError(f"Failed to load table: {str(e)}")


class LookupByIndex:
	@staticmethod
	def metadata():
		return {
			"id": "vectordb.lookup_by_index",
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
	
	@staticmethod
	def lookup_by_index_run(inputs: Dict) -> Dict[str, Any]:
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
			data = VectorDBHandler._load_table(table_name)
			
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
	
	@staticmethod
	def run(inputs):
		# 执行查找操作
		result = LookupByIndex.lookup_by_index_run(inputs)
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