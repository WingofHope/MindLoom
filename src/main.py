# src/main.py

import sys
import os
import uuid
import json
import argparse
import getpass
import random
import string

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def get_class(class_name):
    class_mapping = {
        "task": "engine.scheduler.task.task.Task",
        "process": "engine.scheduler.process.process.Process",
        "action": "engine.executor.action.action.Action",
        "generator": "engine.executor.generator.generator.Generator",
        "tool": "engine.executor.tool.tool.Tool"
    }

    if class_name not in class_mapping:
        print(f"不支持的类名: {class_name}")
        return None

    module_path, class_name = class_mapping[class_name].rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)

def create_instance(class_name, id):
    clazz = get_class(class_name)
    if clazz:
        return clazz(id)
    return None

def run(class_name, id, inputs):
    instance = create_instance(class_name, id)
    if not instance:
        return

    run_id = str(uuid.uuid4())
    print(f"任务正在运行，run_id: {run_id}")

    try:
        inputs_dict = json.loads(inputs)
    except json.JSONDecodeError:
        print("无效的输入 JSON 格式。")
        return

    result = instance.run(inputs_dict, run_id)
    print(result)

def get_template(class_name, id):
    instance = create_instance(class_name, id)
    if not instance:
        return

    template = instance.get_template()
    print(json.dumps(template, indent=2, ensure_ascii=False))

def validate_template(class_name, template):
    try:
        template_dict = json.loads(template)
        clazz = get_class(class_name)
        if not clazz:
            print(f"不支持的类名: {class_name}")
            return

        clazz.validate_template(template_dict)
        print("模板校验通过")

    except json.JSONDecodeError:
        print("无效的模板 JSON 格式。")

    except Exception as e:
        from engine.base.base import Base
        if isinstance(e, (Base.TemplateError)):
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        else:
            print(f"未知错误: {str(e)}")

def get_tools_template():
    from engine.executor.tool.tool_manager import tool_manager as tm
    tools_template = tm.export_metadata()
    print(json.dumps(tools_template, indent=2, ensure_ascii=False))

def get_tools():
    from engine.executor.tool.tool_manager import tool_manager as tm
    tools_list = tm.list_tools()
    print(json.dumps(tools_list, indent=2, ensure_ascii=False))

def add_or_update_env_in_activate(env_name, env_value):
    """在虚拟环境的 activate 文件中添加或更新环境变量"""
    try:
        venv_path = os.environ.get("VIRTUAL_ENV")
        if not venv_path:
            print("未检测到虚拟环境，请先激活虚拟环境。")
            return

        is_windows = sys.platform.startswith("win")
        activate_path = os.path.join(venv_path, "Scripts" if is_windows else "bin", "activate")

        if not os.path.exists(activate_path):
            print(f"未找到 activate 文件: {activate_path}")
            return
        
        # 读取 activate 文件内容
        with open(activate_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 变量格式（Windows 用 set，Linux/macOS 用 export）
        env_prefix = "set " if is_windows else "export "
        env_entry = f'{env_prefix}{env_name}="{env_value}"\n'

        # 检查是否已经存在该环境变量，若存在则更新
        updated_lines = []
        found = False
        for line in lines:
            if line.startswith(f"{env_prefix}{env_name}="):  # 找到旧的，替换
                updated_lines.append(env_entry)
                found = True
            else:
                updated_lines.append(line)
        
        if not found:  # 没找到，追加到文件末尾
            updated_lines.append("\n" + env_entry)

        # 写回 activate 文件
        with open(activate_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        action = "更新" if found else "添加"
        print(f"成功{action} {env_name} 到 {activate_path}")

    except Exception as e:
        print(f"更新环境变量失败: {e}")

def secure_config(save_password):
    from config import config

    # 检查是否已有环境变量密码
    pwd = os.environ.get("CONFIG_PASSWORD")
    if not pwd:
        pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        print(f"自动生成的密码: {pwd}")
        os.environ["CONFIG_PASSWORD"] = pwd

    config.set("encryption.encryption_enabled", True)

    if config.save_config():
        print("保存加密后的配置文件成功。")
        config.delete_default_config()
        if save_password:
            add_or_update_env_in_activate("CONFIG_PASSWORD", os.environ["CONFIG_PASSWORD"])
    else:
        print("保存配置失败，安全存储配置文件操作中止。")

if __name__ == '__main__':
    # 初始化命令行参数处理
    parser = argparse.ArgumentParser(description="执行Minloom引擎的各种任务")

    # 子命令选择
    subparsers = parser.add_subparsers(dest="command")

    # 添加运行任务的子命令
    run_parser = subparsers.add_parser("run", help="运行任务")
    run_parser.add_argument("-c","--class-name", type=str, required=True, help="类名 (task, process, action, generator, tool)")
    run_parser.add_argument("-id","--id", type=str, required=True, help="任务的 ID")
    run_parser.add_argument("-i","--inputs", type=str, required=True, help="输入数据，JSON 格式的字符串")
    run_parser.add_argument("-p", "--password", nargs='?', const="", default=None, help="密码输入模式，如果使用该参数但不提供密码，则会提示输入")

    # 添加获取模板的子命令
    template_parser = subparsers.add_parser("get-template", help="获取任务模板")
    template_parser.add_argument("-c","--class-name", type=str, required=True, help="类名 (task, process, action, generator, tool)")
    template_parser.add_argument("-id","--id", type=str, required=True, help="任务的 ID")
    template_parser.add_argument("-p", "--password", nargs='?', const="", default=None, help="密码输入模式，如果使用该参数但不提供密码，则会提示输入")

    # 添加模板验证的子命令
    validate_parser = subparsers.add_parser("validate-template", help="验证模板")
    validate_parser.add_argument("-c","--class-name", type=str, required=True, help="类名 (task, process, action, generator, tool)")
    validate_parser.add_argument("-t","--template", type=str, required=True, help="模板数据，JSON 格式的字符串")
    validate_parser.add_argument("-p", "--password", nargs='?', const="", default=None, help="密码输入模式，如果使用该参数但不提供密码，则会提示输入")
    
    # 添加获取工具模板的子命令
    tools_template_parser = subparsers.add_parser("get-tools-template", help="获取工具模板列表")
    tools_template_parser.add_argument("-p", "--password", nargs='?', const="", default=None, help="密码输入模式，如果使用该参数但不提供密码，则会提示输入")

    # 添加获取工具元数据的子命令
    tools_parser = subparsers.add_parser("get-tools", help="获取工具 ID 和描述列表")
    tools_parser.add_argument("-p", "--password", nargs='?', const="", default=None, help="密码输入模式，如果使用该参数但不提供密码，则会提示输入")

    # 添加安全模式保存配置文件子命令
    secure_config_parser = subparsers.add_parser("secure-config", help="安全模式保存配置文件")
    secure_config_parser.add_argument("-s","--save-password", action="store_true", help="将密码保存到Python虚拟环境active文件中")
    secure_config_parser.add_argument("-p", "--password", nargs='?', const="", default=None, help="密码输入模式，如果使用该参数但不提供密码，则会提示输入")
    
    # 解析命令行参数
    args = parser.parse_args()

    # 如果密码参数存在则将密码存放环境变量
    if args.password is not None:
        if args.password == "":
            os.environ["CONFIG_PASSWORD"] = getpass.getpass("请输入密码：")
        else:
            os.environ["CONFIG_PASSWORD"] = args.password

    # 处理各种命令
    if args.command == "secure-config":
        secure_config(args.save_password)
    elif args.command == "run":
        run(args.class_name, args.id, args.inputs)
    elif args.command == "get-template":
        get_template(args.class_name, args.id)
    elif args.command == "validate-template":
        validate_template(args.class_name, args.template)
    elif args.command == "get-tools-template":
        get_tools_template()
    elif args.command == "get-tools":
        get_tools()
    else:
        print("未知的命令。可以使用 -h 命令查看命令参数详情。")
