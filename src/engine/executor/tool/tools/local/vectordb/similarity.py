import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

from engine.executor.tool.tool_base import ToolBase
from services.local_vectordb.local_vectordb_base import VectorDBHandler

class RangeQuery(ToolBase):
	def __init__(self):
		super().__init__()
		
	@staticmethod
	def metadata():
		return {
			"id": "local_vectordb.range_query",
			"name": "range_query",
			"description": "根据相似度阈值查找所有相似度大于给定值的向量记录。",
			"inputs": [
				{"name": "table_name", "type": "string", "description": "库表名"},
				{"name": "query_vector", "type": "array", "description": "查询向量（单个向量）"},
				{"name": "similarity_threshold", "type": "number", "description": "相似度阈值"}
			],
			"outputs": [
				{"name": "metadata_list", "type": "array", "description": "结构体数据（附加信息）列表"},
				{"name": "matching_indices", "type": "array", "description": "符合条件的向量索引列表"},
				{"name": "matching_similarities", "type": "array", "description": "对应的相似度列表"}
			]
		}
	
	@staticmethod
	def cosine_similarity(vec1, vec2):
		"""计算两个向量之间的余弦相似度"""
		dot_product = np.dot(vec1, vec2)
		norm_vec1 = np.linalg.norm(vec1)
		norm_vec2 = np.linalg.norm(vec2)
		return dot_product / (norm_vec1 * norm_vec2)
	
	def range_query_run(self, inputs: Dict) -> Dict[str, List]:
		try:
			# 输入参数校验
			required_fields = ["table_name", "query_vector", "similarity_threshold"]
			for field in required_fields:
				if field not in inputs:
					raise ValueError(f"Missing required field: {field}")
			
			table_name = inputs["table_name"]
			query_vector = inputs["query_vector"]
			similarity_threshold = inputs["similarity_threshold"]
			
			# 类型校验
			if not isinstance(query_vector, list) or not all(isinstance(x, (int, float)) for x in query_vector):
				raise TypeError("Invalid query_vector format")
			if not isinstance(similarity_threshold, (int, float)):
				raise TypeError("similarity_threshold must be a number")
			
			# 加载数据表
			data = VectorDBHandler._load_or_create_table(table_name)
			records = data["records"]
			
			# 检查数据库中是否有记录
			if not records:
				return {
					"metadata_list": [],
					"matching_indices": [],
					"matching_similarities": []
				}
			
			# 检查查询向量和数据库中向量的维度是否一致
			db_vector_dim = len(records[0]["vector"])
			query_vector_dim = len(query_vector)
			if query_vector_dim != db_vector_dim:
				raise ValueError(
					f"Dimension mismatch: query_vector has dimension {query_vector_dim}, "
					f"but database vectors have dimension {db_vector_dim}"
				)
			
			# 初始化结果列表
			metadata_list = []
			matching_indices = []
			matching_similarities = []
			
			# 遍历所有记录，计算相似度并筛选
			for record in records:
				vector = record["vector"]
				similarity = RangeQuery.cosine_similarity(query_vector, vector)
				if similarity > similarity_threshold:
					metadata_list.append(record["metadata"])
					matching_indices.append(record["index"])
					matching_similarities.append(similarity)
			
			return {
				"metadata_list": metadata_list,
				"matching_indices": matching_indices,
				"matching_similarities": matching_similarities
			}
		
		except Exception as e:
			print(f"查询操作异常: {str(e)}")
			return {
				"metadata_list": [],
				"matching_indices": [],
				"matching_similarities": []
			}
	
	def run(self, inputs):
		# 执行查询操作
		result = self.range_query_run(inputs)
		return result



if __name__ == "__main__":
	test_input = {
		"table_name": "test_table",
		"query_vector": [0.1, 0.2, 0.4],
		"similarity_threshold": 0.8
	}

	result = RangeQuery().run(test_input)
	print(f"查询结果: {result}")