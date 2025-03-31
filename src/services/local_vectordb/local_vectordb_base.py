import json
from pathlib import Path
from typing import Dict, List, Any


class VectorDBHandlerBase:
    _memory_cache: Dict[str, Dict] = {}  # 内存缓存 {table_name: data}

    @classmethod
    def _get_storage_dir(cls) -> Path:
        """计算存储目录路径"""
        current_file = Path(__file__).resolve()  # 当前脚本的绝对路径

        project_root = current_file.parent.parent.parent.parent
        
        return project_root / "data" / "local_vector_database"

    @classmethod
    def _load_or_create_table(cls, table_name: str) -> Dict:
        """核心内存访问函数"""
        if table_name in cls._memory_cache:
            print("在内存中")
            return cls._memory_cache[table_name]

        storage_dir = cls._get_storage_dir()
        storage_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        file_path = storage_dir / f"{table_name}.json"

        try:
            if file_path.exists():
                print("不在内存")
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


# 实例化 VectorDBHandler
VectorDBHandler = VectorDBHandlerBase()