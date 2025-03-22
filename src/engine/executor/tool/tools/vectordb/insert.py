import json
from pathlib import Path
from typing import Dict, List, Any


class VectorDBHandler:
	_memory_cache: Dict[str, Dict] = {}  # 内存缓存 {table_name: data}
	
	@classmethod
	def _get_storage_dir(cls) -> Path:
		"""计算存储目录路径"""
		current_file = Path(__file__).resolve()  # 当前脚本的绝对路径
		# 从当前脚本路径回溯到项目根目录（MindLoom-develop）
		project_root = current_file.parent.parent.parent.parent.parent.parent
		# 目标路径：项目根目录/database/vector database
		return project_root / "database" / "vector database"
	
	@classmethod
	def _load_or_create_table(cls, table_name: str) -> Dict:
		"""核心内存访问函数"""
		if table_name in cls._memory_cache:
			return cls._memory_cache[table_name]
		
		storage_dir = cls._get_storage_dir()
		storage_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
		file_path = storage_dir / f"{table_name}.json"
		
		try:
			if file_path.exists():
				with open(file_path, "r", encoding="utf-8") as f:
					data = json.load(f)
			else:
				data = {"next_index": 1, "records": []}
			
			cls._memory_cache[table_name] = data
			return data
		except Exception as e:
			raise RuntimeError(f"Failed to load/create table: {str(e)}")
	
	@classmethod
	def _save_table(cls, table_name: str) -> bool:
		"""持久化存储到文件"""
		if table_name not in cls._memory_cache:
			return False
		
		try:
			storage_dir = cls._get_storage_dir()
			file_path = storage_dir / f"{table_name}.json"
			with open(file_path, "w", encoding="utf-8") as f:
				json.dump(
					cls._memory_cache[table_name],
					f,
					indent=2,
					ensure_ascii=False
				)
			return True
		except Exception as e:
			raise RuntimeError(f"Failed to save table: {str(e)}")


class Insert:
	@staticmethod
	def metadata():
		return {
			"id": "vectordb.insert",
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
	
	
	def insert_run(inputs: Dict) -> Dict[str, bool]:
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
	
	@staticmethod
	def run(inputs):
		# 测试插入操作
		result = Insert.insert_run(inputs)
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