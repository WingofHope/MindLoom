# Mindloom - AI 大语言模型 Agent 引擎

## 简介

Mindloom 由曦之翼（WingofHope）团队开发，是一个用于管理和执行 AI 大语言模型（LLM）任务的引擎。它支持基于 JSON 模板的任务定义，可调度 OpenAI API 及相似接口的 LLM，同时支持多线程并行执行。程序提供了命令行（CLI）和 Python API 两种使用方式，并允许用户通过 YAML 配置文件自定义参数。

## 特性

- **支持 OpenAI 及兼容 API**：默认支持 OpenAI API，兼容其他符合 OpenAI 接口格式的 LLM。
- **Agent运行支持**：根据 JSON 模板定义任务的执行模式，支持单线程和多线程任务。
- **任务模板管理**：支持从本地文件或 MongoDB 读取 JSON 任务模板。
- **运行日志管理**：支持将运行日志存储到本地文件或 MongoDB。
- **可选加密配置**：支持 `secure-config` 进行配置文件加密，防止敏感信息泄露。
- **跨平台支持**：可在 Windows、Linux、MacOS 上运行。

## 安装

### 1. 克隆代码仓库
```bash
git clone git@github.com:WingofHope/MindLoom.git
cd MindLoom
```

### 2. 安装依赖
确保系统安装了 Python 3，并运行以下命令安装所需依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

Mindloom 提供 **CLI 命令行接口** 和 **Python API** 两种使用方式。

### 1. CLI 命令行使用

Mindloom 提供了 `run` 命令用于执行任务，以及若干管理命令，以下是常见命令：

```bash
python main.py run -c task -id <task_id> -i '<JSON 输入>' [-p <密码>]
```

**示例**：
```bash
python main.py run -c task -id task_template -i '{"question": "我想去天安门后天，什么时间合适？"}'
```

#### CLI 命令列表

| 命令 | 说明 |
|------|------|
| `run -c <class_name> -id <task_id> -i <inputs> [-p <密码>]` | 运行指定 ID 的任务 |
| `get-template -c <class_name> -id <task_id> [-p <密码>]` | 获取指定 ID 的模板 |
| `validate-template -c <class_name> -t <template_json> [-p <密码>]` | 验证 JSON 模板 |
| `get-tools` | 列出可用工具 |
| `get-tools-template` | 导出可用工具的 JSON 模板|
| `secure-config [-s] [-p <密码>]` | 加密关键字段并保存 config.yaml 配置文件 |

### 2. Python API 使用

你可以在 Python 代码中调用 Mindloom 任务调度 API，如下示例：

```python
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engine.scheduler.task.task import Task

t_id = 'task_template'
inputs = { 'question': '我想去天安门后天，什么时间合适？' }

try:
    task_instance = Task(t_id)
    result = task_instance.run(inputs)
    print(result)
except Task.TemplateError as e:
    print("模板验证失败，错误信息如下：")
    for error in e.errors:
        print(f"- {error}")
except Task.ParameterError as e:
    print("参数校验失败，错误信息如下：")
    for error in e.errors:
        print(f"- {error}")
```

## 配置管理

### 配置文件路径
- `config/config.yaml`（用户自定义配置）
- `config/default_config.yaml`（默认配置，程序会优先读取 `config.yaml`，不存在时使用 `default_config.yaml`）

### 配置项说明
- **API 配置**：支持 OpenAI API 及相似接口的 LLM。
- **日志管理**：运行日志可以存储到本地文件或 MongoDB，路径和数据库表名在 `config.yaml` 里定义。
- **模板管理**：JSON 任务模板可从本地文件或 MongoDB 读取，路径在 `config.yaml` 配置。
- **加密配置**：`secure-config` 命令可以对 `config.yaml` 进行加密，防止敏感数据泄露。

### 配置文件加密与解密

加密 `config.yaml` 文件：
```bash
python main.py secure-config [-s] [-p <密码>] 
```

### 运行时密码输入方式
- **`-p` 选项**：可在命令行运行时输入密码。
- **环境变量**：可通过 `CONFIG_PASSWORD` 环境变量存储密码。

## 日志管理

Mindloom 记录两类日志：

1. **运行日志**：任务执行过程的成功、失败信息，存储位置（本地文件或 MongoDB）可在 `config.yaml` 配置。
2. **错误日志**：Python 级别错误（如 MongoDB 连接失败、队列错误、字段不合法等），默认存储在 `logs/` 目录，可在 `config.yaml` 配置。

## 任务执行机制

- 运行 `run` 命令或调用 `task_instance.run(inputs)` 后，Mindloom 会根据 JSON 模板执行任务。
- 任务可设定单线程或多线程模式。
- 任务优先级和超时机制由用户在 JSON 模板中定义。
- 运行过程中会生成唯一 `run_id`，日志记录任务执行信息。
- 任务可能调用 `action`，支持三种方式：
  1. **REST API**
  2. **本地文件**
  3. **RabbitMQ**

## API 兼容性

- Mindloom 兼容 OpenAI API 及类似接口的 LLM。
- API 需要在 `config.yaml` 中配置 API Key，可加密存储。
- 自定义 LLM 需符合 OpenAI API 结构（completion、chat、embedding）。

## 许可与贡献

- 本项目开源并允许商用。
- 目前不接受外部贡献，由曦之翼（WingofHope）团队独立开发。

## 联系方式

如有问题或建议，请联系曦之翼团队。

