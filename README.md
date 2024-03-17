# 目录结构
```
MindLoom/
├── prompts/                    # 存放提示模版库，格式为json
│   ├── action/                 # 执行外部动作定义
│   ├── generator/              # llm交互生成内容的模版定义
│   ├── process/                # 处理流程执行的定义，包括顺行sequential、分支选择select、循环loop、并行parallel等
│   ├── task/                   # 明确的任务定义，是引擎的入口
│   └── tool/                   # 内部调用工具类定义
│
├── src/                        # 源代码目录
│   ├── enginee/                # 引擎代码目录
│   │   ├── base/               # 引擎基类
│   │   ├── executor/            # 执行器类
│   │   │   ├── action/         # Action 与外部交互的操作类
│   │   │   ├── generator/      # Generator LLM一次内容生成于模版替换类
│   │   │   └── tool/           # Tool 引擎用到的内部工具类
│   │   │
│   │   ├── scheduler/          # 调度器类定义
│   │   │   ├── process/        # Process 处理流程类
│   │   │   └── task/           # Task 任务类，引擎的入口
│   │   │
│   │   └── utils/              # 引擎用到的应用程序或工具集模块
│   │
│   ├── services/               # 与引擎交互的服务模块
│   │   ├── logger/             # Logger 日志相关服务
│   │   ├── mongodb/            # MongoDB 数据库服务
│   │   └── rabbitmq/           # RabbitMQ 消息队列服务
│   │
│   ├── config.py               # 读取配置文件和初始化项目根路径
│   │
│   └── main.py                 # 应用程序的主入口点
│
├── config/                     # 配置文件目录
│   └── default_config.json     # 默认配置文件
│
├── log/                        # 日志文件目录
│   └── mindloom.log            # 漫璐主日志
│
├── tests/                      # 测试代码集
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