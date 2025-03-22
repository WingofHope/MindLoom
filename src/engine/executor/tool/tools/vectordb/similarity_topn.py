import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np


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


class SortByVector:
	@staticmethod
	def metadata():
		return {
			"id": "vectordb.similar_topn",
			"name": "sort_by_vector",
			"description": "根据给定的向量，返回与之相似度最高的前N个索引,相似度值和结构体数据（附加信息）。",
			"inputs": [
				{"name": "table_name", "type": "string", "description": "库表名"},
				{"name": "query_vector", "type": "array", "description": "查询向量（单个向量）"},
				{"name": "top_n", "type": "number", "description": "返回的前N个结果数"}
			],
			"outputs": [
				{"name": "top_index", "type": "array", "description": "前N个相似度最高的索引"},
				{"name": "top_metadata", "type": "array", "description": "前N个相似度最高的索引的元数据"},
				{"name": "similarities", "type": "array", "description": "对应的相似度值"}
			]
		}
	
	@staticmethod
	def cosine_similarity(vec1, vec2):
		"""计算两个向量之间的余弦相似度"""
		dot_product = np.dot(vec1, vec2)
		norm_vec1 = np.linalg.norm(vec1)
		norm_vec2 = np.linalg.norm(vec2)
		return dot_product / (norm_vec1 * norm_vec2)
	
	@staticmethod
	def sort_by_vector_run(inputs: Dict) -> Dict[str, List]:
		try:
			# 输入参数校验
			required_fields = ["table_name", "query_vector", "top_n"]
			for field in required_fields:
				if field not in inputs:
					raise ValueError(f"Missing required field: {field}")
			
			table_name = inputs["table_name"]
			query_vector = inputs["query_vector"]
			top_n = inputs["top_n"]
			
			# 类型校验
			if not isinstance(query_vector, list) or not all(isinstance(x, (int, float)) for x in query_vector):
				raise TypeError("Invalid query_vector format")
			if not isinstance(top_n, int) or top_n <= 0:
				raise TypeError("top_n must be a positive integer")
			
			# 加载数据表
			data = VectorDBHandler._load_or_create_table(table_name)
			records = data["records"]
			
			# 检查数据库中是否有记录
			if not records:
				return {
					"top_index": [],
					"top_metadata": [],
					"similarities": []
				}
			
			# 检查查询向量和数据库中向量的维度是否一致
			db_vector_dim = len(records[0]["vector"])
			query_vector_dim = len(query_vector)
			if query_vector_dim != db_vector_dim:
				raise ValueError(
					f"Dimension mismatch: query_vector has dimension {query_vector_dim}, "
					f"but database vectors have dimension {db_vector_dim}"
				)
			
			# 计算所有记录的相似度
			similarities = []
			for record in records:
				vector = record["vector"]
				similarity = SortByVector.cosine_similarity(query_vector, vector)
				similarities.append((record["index"], record["metadata"], similarity))
			
			# 按相似度排序
			similarities.sort(key=lambda x: x[2], reverse=True)
			
			# 取前N个结果
			top_n = min(top_n, len(similarities))  # 如果数据少于N，取全部
			top_results = similarities[:top_n]
			
			# 提取结果
			top_index = [result[0] for result in top_results]
			top_metadata = [result[1] for result in top_results]
			similarities = [result[2] for result in top_results]
			
			return {
				"top_index": top_index,
				"top_metadata": top_metadata,
				"similarities": similarities
			}
		
		except Exception as e:
			print(f"查询操作异常: {str(e)}")
			return {
				"top_index": [],
				"top_metadata": [],
				"similarities": []
			}
	
	@staticmethod
	def run(inputs):
		# 执行查询操作
		result = SortByVector.sort_by_vector_run(inputs)
		return result



# if __name__ == "__main__":
#
# 	test_input = {
# 		"table_name": "test_table",
# 		"query_vector": [0.1, 0.2, 0.4],
# 		"top_n": 6
# 	}
#
# 	result = SortByVector.run(test_input)
# 	print(f"查询结果: {result}")