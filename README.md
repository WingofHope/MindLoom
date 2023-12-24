# 目录结构
```
llm-agent-project/
│
├── src/                        # 源代码目录
│   ├── base/                   # 基类定义目录
│   │   ├── enginee_base.py     # Enginee基类定义
│   │   └── process_base.py     # Process基类定义
│   ├── agents/                 # 代理相关的模块
│   │   ├── llm_agent.py        # LLM代理的主要类
│   │   └── utils.py            # 代理使用的工具函数
│   │
│   ├── prompts/                # 引擎目录
│   │   ├── action/             # 执行外部动作
│   │   ├── generator/          # 如何和llm交互产生输出
│   │   │   └── demo.generator.json
│   │   ├── process/            # 具体的处理流程
│   │   │   ├── loop.process.json
│   │   │   ├── parallel.process.json
│   │   │   ├── select.process.json
│   │   │   └── sequential.process.json
│   │   ├── task/               # 具体的任务
│   │   │   └── demo.task.json
│   │   └── tool/               # 调用内部工具
│   │       └── get_web_page_001.tool.json
│   │
│   ├── services/               # 与代理交互的服务模块
│   │   ├── api_service.py      # API服务
│   │   └── data_service.py     # 数据处理服务
│   │
│   └── main.py                 # 应用程序的主入口点
│
├── config/                     # 配置文件目录
│   ├── default_config.json     # 默认配置文件

├── tests/                      # 测试代码
│   ├── test_llm_agent.py       # 测试LLM代理功能
│   ├── test_enginee.py         # 测试引擎功能
│   └── test_services.py        # 测试服务功能
│
├── docs/                       # 文档目录
│   └── api_documentation.md    # API文档
│
├── notebooks/                  # Jupyter笔记本，用于演示和原型设计
│   └── example_usage.ipynb     # 示例使用笔记本
│
├── requirements.txt            # 项目依赖
├── setup.py                    # 安装脚本
└── README.md                   # 项目说明文件
```