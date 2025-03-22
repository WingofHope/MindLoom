import sys
import subprocess
import importlib

class ToolBase:
    @staticmethod
    def metadata():
        return {}

    def __init__(self):
        self.imported_modules = {}

    def import_or_install(self, package):
        """
        尝试导入指定的包，如果不存在就提示用户进行下载。
        并将导入的模块存储在实例的 imported_modules 中。

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
        return module
# 创建 ToolBase 类的实例
toolbase = ToolBase()