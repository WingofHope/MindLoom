# src/engine/executor/tool/tool_manager.py

import importlib
import os
import inspect

class ToolManager:
    def __init__(self):
        """
        初始化工具管理器，加载所有工具并将其元数据存储到内存中。
        """
        self.tools = self._load_tools()

    def _load_tools(self):
        """
        从 tools 目录加载所有工具，读取其元数据，并存储到内存。
        返回一个以 tool_id 为键的工具字典。
        """
        tools_directory = os.path.join(os.path.dirname(__file__), "tools")
        tools_metadata = {}

        # 遍历 tools 目录及其子目录，加载所有工具类
        for root, _, files in os.walk(tools_directory):
            for file in files:
                # 查找所有py文件，去掉__init__.py等文件
                if file.endswith(".py") and not file.startswith("__"):
                    # 获取工具相对路径，也就是tools后的路径
                    module_path = os.path.relpath(os.path.join(root, file), tools_directory)
                    # 将路径字符串转换成.号标记的模块路径
                    module_path = module_path.replace(os.sep, ".").replace(".py", "")

                    # 动态加载模块
                    try:
                        # mindloom默认运行路径是src/目录，所以需要转换成从engine开始的import
                        module = importlib.import_module(f".tools.{module_path}", package="engine.executor.tool")
                        # 遍历该py文件下所有的class定义类
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            # 判断class对象是否包含可执行的函数metadata()
                            if hasattr(obj, "metadata") and callable(obj.metadata) and hasattr(obj, "run") and callable(obj.run):
                                metadata = obj.metadata()
                                tool_id = metadata["id"]
                                tools_metadata[tool_id] = {
                                    "class": obj,
                                    "metadata": metadata
                                }
                    except Exception as e:
                        raise RuntimeError(f"加载工具模块 {module_path} 错误: {e}")

        return tools_metadata

    def load_tool(self, tool_id):
        """
        根据工具 ID 加载工具类的实例。
        """
        tool_info = self.tools.get(tool_id)
        if not tool_info:
            raise FileNotFoundError(f"工具ID： '{tool_id}' 没有找到。")
        return tool_info["class"]

    def get_metadata(self, tool_id):
        """
        根据工具 ID 获取工具的元数据。
        """
        tool_info = self.tools.get(tool_id)
        if not tool_info:
            raise FileNotFoundError(f"工具ID： '{tool_id}' 没有找到。")
        return tool_info["metadata"]

    def list_tools(self):
        """
        列出所有工具的 ID 和描述。
        返回一个包含元数据中 ID 和 description 的列表。
        """
        return [{"id": tool_id, "description": info["metadata"]["description"]}
                for tool_id, info in self.tools.items()]

    def export_metadata(self):
        """
        导出所有工具的元数据。
        返回一个包含所有元数据的列表。
        """
        return [info["metadata"] for info in self.tools.values()]


class ModuleImporter:
    def __init__(self):
        self.imported_modules = {}
    
    def import_or_install(self, package):
        """
		尝试导入指定的包，如果不存在就提示用户进行下载。

		参数:
		package (str): 要导入的包的名称。
		"""
        try:
            module = __import__(package)
            self.imported_modules[package] = module
            print(f"包 '{package}' 已成功导入。")
        except ImportError:
            # 包不存在，直接尝试下载并安装
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"模块 '{package}' 已成功安装。")
                # 重新导入包
                module = importlib.import_module(package)
                self.imported_modules[package] = module
            except subprocess.CalledProcessError as e:
                # 下载失败，抛出错误
                raise RuntimeError(f"下载模块 '{package}' 失败，错误信息: {e}")
# 实例化一个工具管理器对象
tool_manager = ToolManager()