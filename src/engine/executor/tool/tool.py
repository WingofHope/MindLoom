import importlib
import inspect
import os
import subprocess
import sys
from engine.executor.executor import Executor


class Tool(Executor):
    tools_cache = {}  # 缓存工具类

    def __init__(self, template_id, task_id=None, parent_run_id=None):
        self.tool_class = self._load_tool(template_id)
        super().__init__(template_id, task_id, parent_run_id)
        self.class_name = "tool"

    def _load_template(self):
        self.template = self.tool_class.metadata()

    def _install_package(self, requirements_path):
        # 读取requirements.txt
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = f.readlines()
        
        # 过滤空行和注释
        packages_to_install = []
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                # 提取包名（去掉版本号）
                package_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
                
                # 检查包是否已安装
                try:
                    importlib.import_module(package_name)
                    # 包已安装，跳过
                    continue
                except ImportError:
                    # 包未安装，需要安装
                    packages_to_install.append(req)
        
        # 如果有需要安装的包
        if packages_to_install:
            try:
                # 创建临时requirements文件
                temp_req_file = requirements_path + '.temp'
                with open(temp_req_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(packages_to_install))
                
                # 安装缺失的包
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", temp_req_file
                ])
                
                # 清理临时文件
                os.remove(temp_req_file)
                print(f"已安装 {len(packages_to_install)} 个包: {', '.join(packages_to_install)}")
                
            except subprocess.CalledProcessError as e:
                # 清理临时文件（如果存在）
                if os.path.exists(temp_req_file):
                    os.remove(temp_req_file)
                raise RuntimeError(f"安装依赖失败: {requirements_path}, 错误: {e}")
        else:
            print("所有依赖包已安装，跳过安装")

    def _load_tool_class(self, tool_id):
        """加载并缓存工具类"""
        module_name = f"engine.executor.tool.tools.{tool_id}"
        try:
            module = importlib.import_module(module_name)
            
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (name != "ToolBase" and 
                    hasattr(obj, "metadata") and callable(obj.metadata) and 
                    hasattr(obj, "run") and callable(obj.run)):
                    
                    metadata = obj.metadata()
                    if isinstance(metadata, dict):
                        meta_tool_id = metadata.get("id")
                        if meta_tool_id == tool_id:
                            return obj
            
            raise RuntimeError(f"模块 {module_name} 中未找到id为 '{tool_id}' 的工具类")
                
        except ImportError:
            raise RuntimeError(f"无法导入工具模块: {module_name}")
        except Exception as e:
            raise RuntimeError(f"加载工具 {tool_id} 错误: {e}")

    def _load_tool(self, tool_id):
        """根据template_id加载工具类"""
        parts = tool_id.split(".")
        tool_path = parts[:-1]  # 所有部分除了最后一部分（即路径）
        tool_end = parts[-1]    # 最后一部分是文件名（工具名）

        current_cache = Tool.tools_cache
        tools_root = os.path.join(os.path.dirname(__file__), "tools")

        # 遍历路径部分，检查每一部分是否存在于cache中
        for i, path in enumerate(tool_path):
            # 如果路径已在cache中，进入下一层
            if path in current_cache:
                current_cache = current_cache[path]
            else:
                # 构建路径
                folder_path = os.path.join(tools_root, *tool_path[:i + 1])
                if not os.path.exists(folder_path):
                    raise RuntimeError(f"工具类不存在: {tool_id}")
                
                # 检查并安装requirements.txt
                requirements_path = os.path.join(folder_path, "requirements.txt")
                if os.path.exists(requirements_path):
                    self._install_package(requirements_path)
                
                # 如果是文件夹，标记为空字典，继续
                current_cache[path] = {}

                # 进入下一层
                current_cache = current_cache[path]

        # 如果tool_end已经在缓存中，直接返回缓存的类
        if tool_end in current_cache:
            current_cache = current_cache[tool_end]
            if isinstance(current_cache, type):
                return current_cache
            else:
                raise RuntimeError(f"工具类id不完整: {tool_id}")

        # 检查 .py 文件是否存在
        file_path = os.path.join(tools_root, *tool_path, f"{tool_end}.py")
        if not os.path.exists(file_path):
            raise RuntimeError(f"工具类不存在: {tool_id}")

        # 调用加载工具类函数
        loaded_class = self._load_tool_class(tool_id)

        # 缓存并返回工具类
        current_cache[tool_end] = loaded_class
        return loaded_class

    def _execute(self, inputs):
        """执行工具"""
        outputs = self.tool_class.run(inputs)
        return outputs
