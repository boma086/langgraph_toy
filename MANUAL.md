# LangGraph Toy - User Manual / 用户手册

## Overview / 概述

LangGraph Toy 是一个最小化的 LangGraph 实现，无需使用官方 SDK。它提供了核心的图执行功能、状态管理、智能代理和 Web 界面。

LangGraph Toy is a minimal LangGraph implementation that doesn't require the official SDK. It provides core graph execution functionality, state management, intelligent agents, and a web interface.

## 功能特性 / Features

- 🎯 **图执行引擎 / Graph Execution Engine**: 自定义图执行，支持节点、边和条件路由 / Custom graph execution with nodes, edges, and conditional routing
- 🧠 **智能代理 / Intelligent Agent**: 简单推理代理，支持工具调用 / Simple reasoning agent with tool calling support
- 🔧 **工具系统 / Tool System**: 计算器、天气查询、搜索工具 / Calculator, weather query, and search tools
- 🌐 **Web 界面 / Web Interface**: 交互式聊天界面 / Interactive chat interface
- 🧪 **完整测试 / Complete Testing**: 106 个测试用例全部通过 / All 106 test cases passing
- 📊 **API 接口 / API Interface**: REST API 支持各种操作 / REST API supporting various operations

## 快速开始 / Quick Start

### 1. 环境准备 / Environment Setup

```bash
# 克隆项目 / Clone the project
git clone <repository-url>
cd langgraph_toy

# 创建虚拟环境 / Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows / or venv\Scripts\activate  # Windows

# 安装依赖 / Install dependencies
pip install -r requirements.txt
```

### 2. 启动应用 / Start the Application

```bash
# 启动 Web 服务器 / Start the web server
python -m uvicorn api.app:create_app --host 0.0.0.0 --port 8000 --reload

# 或使用启动脚本 / Or use the startup script
chmod +x start.sh
./start.sh
```

### 3. 访问界面 / Access the Interface

- **Web 界面 / Web Interface**: http://localhost:8000/web/
- **API 文档 / API Documentation**: http://localhost:8000/docs
- **健康检查 / Health Check**: http://localhost:8000/health

## 使用指南 / Usage Guide

### Web 界面使用 / Using the Web Interface

1. 打开浏览器访问 http://localhost:8000/web/ / Open browser and visit http://localhost:8000/web/
2. 在聊天输入框中输入消息 / Enter message in the chat input box
3. 点击发送或按 Enter 键 / Click send or press Enter key
4. 查看代理的响应 / View the agent's response

**示例对话 / Sample Conversation**:
```
你 / You: hello
代理 / Agent: Hello! I'm a simple agent that can help you with calculations, weather information, and searches. How can I assist you?

你 / You: calculate 2+2
代理 / Agent: I've used some tools to help answer your question. Tool result: 4.0

你 / You: weather in beijing
代理 / Agent: I've used some tools to help answer your question. Tool result: Weather in Beijing: 22°C, Sunny
```

### API 使用 / API Usage

#### 聊天接口 / Chat Interface

```bash
# 发送聊天消息 / Send chat message
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "calculate 2+2",
    "agent_type": "simple"
  }'

# 响应 / Response
{
  "response": "I've used some tools to help answer your question. Tool result: 4.0",
  "agent_type": "simple",
  "timestamp": 1634567890.123
}
```

#### 图执行接口 / Graph Execution Interface

```bash
# 执行图 / Execute graph
curl -X POST "http://localhost:8000/api/v1/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_type": "simple_agent",
    "input_data": {"message": "hello world"}
  }'

# 响应 / Response
{
  "success": true,
  "result": {
    "messages": [...],
    "tool_calls": [...],
    "intermediate_steps": [...],
    "is_complete": true
  },
  "execution_time": 0.023
}
```

#### 代理信息 / Agent Information

```bash
# 获取代理列表 / Get agent list
curl -X GET "http://localhost:8000/api/v1/agents"

# 获取特定代理的工具 / Get tools for specific agent
curl -X GET "http://localhost:8000/api/v1/agents/simple/tools"
```

#### 状态管理 / State Management

```bash
# 状态操作 / State operations
curl -X POST "http://localhost:8000/api/v1/state" \
  -H "Content-Type: application/json" \
  -d '{
    "state_data": {"messages": [{"role": "user", "content": "hello"}]},
    "operation": "set"
  }'
```

## 测试 / Testing

### 运行所有测试 / Run All Tests

```bash
# 激活虚拟环境 / Activate virtual environment
source venv/bin/activate

# 运行所有测试 / Run all tests
python -m pytest tests/ -v

# 运行特定测试 / Run specific tests
python -m pytest tests/test_agent.py -v
python -m pytest tests/test_graph.py -v
python -m pytest tests/test_api.py -v
```

### 测试覆盖率 / Test Coverage

```bash
# 生成测试覆盖率报告 / Generate test coverage report
pip install pytest-cov
python -m pytest tests/ --cov=. --cov-report=html
```

## 调试指南 / Debugging Guide

### 1. 日志调试 / Log Debugging

应用启动时会显示详细的执行日志 / The application displays detailed execution logs on startup:

```
INFO:core.graph:Starting graph execution: simple_agent_graph
INFO:core.graph:Executing node: input
INFO:core.graph:Node input completed successfully
INFO:core.graph:Executing node: analyze
INFO:core.graph:Node analyze completed successfully
INFO:core.graph:Executing node: respond
INFO:core.graph:Node respond completed successfully
INFO:core.graph:Executing node: check_complete
INFO:core.graph:Node check_complete completed successfully
INFO:core.graph:Executing node: output
INFO:core.graph:Node output completed successfully
INFO:core.graph:No more edges to follow, execution complete
```

### 2. Python 调试器 / Python Debugger

```python
# 在代码中添加断点 / Add breakpoint in code
import pdb; pdb.set_trace()

# 或使用 breakpoint() / Or use breakpoint()
breakpoint()
```

### 3. 常见问题排查 / Common Issue Troubleshooting

#### 问题 1: 代理返回默认响应 / Issue 1: Agent Returns Default Response
```python
# 检查 _generate_response 方法 / Check _generate_response method
# 确保用户输入匹配关键词模式 / Ensure user input matches keyword patterns
if any(word in user_input for word in ["hello", "hi", "hey"]):
    return "Hello! I'm a simple agent..."
```

#### 问题 2: 工具调用失败 / Issue 2: Tool Call Failure
```python
# 检查工具注册 / Check tool registration
agent = SimpleAgent()
print(agent.tools.keys())  # 应该显示 ['calculator', 'weather', 'search'] / Should show ['calculator', 'weather', 'search']

# 检查工具参数提取 / Check tool argument extraction
args = agent._extract_tool_args("calculate 2+2", "calculator")
print(args)  # 应该显示 {'expression': '2+2'} / Should show {'expression': '2+2'}
```

#### 问题 3: 图执行卡住 / Issue 3: Graph Execution Stuck
```python
# 检查图结构 / Check graph structure
graph = agent.create_graph()
print(f"Nodes: {list(graph.nodes.keys())}")
print(f"Edges: {len(graph.edges)}")
print(f"Entry point: {graph.entry_point}")

# 验证图 / Validate graph
issues = graph.validate()
if issues:
    print(f"Graph issues: {issues}")
```

#### 问题 4: 状态管理问题 / Issue 4: State Management Issues
```python
# 检查状态创建 / Check state creation
state = AgentState(messages=[{"role": "user", "content": "hello"}])
print(f"Messages: {state.messages}")
print(f"Tool calls: {state.tool_calls}")
print(f"Complete: {state.is_complete}")
```

### 4. 开发者调试技巧 / Developer Debugging Tips

#### 启用详细日志 / Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 检查图执行流程 / Check Graph Execution Flow
```python
# 在 SimpleAgent.run() 方法中添加调试信息 / Add debug info in SimpleAgent.run() method
def run(self, user_input: str) -> str:
    print(f"Input: {user_input}")
    initial_state = self.process_input(user_input)
    print(f"Initial state: {initial_state}")
    
    graph = self.create_graph()
    final_state = graph.execute(initial_state)
    print(f"Final state: {final_state}")
    
    return self.format_output(final_state)
```

#### 测试单个组件 / Test Individual Components
```python
# 测试状态管理 / Test state management
state = AgentState()
new_state = state.add_message("user", "hello")
print(f"Added message: {new_state.messages}")

# 测试工具执行 / Test tool execution
tool = calculator_tool
result = tool.execute(expression="2+2")
print(f"Tool result: {result}")
```

## 架构说明 / Architecture Overview

### 核心组件 / Core Components

1. **State Management** (`core/state.py`)
   - `StateSchema`: 基础状态模式 / Basic state schema
   - `AgentState`: 代理专用状态 / Agent-specific state
   - `GraphState`: 图执行状态 / Graph execution state

2. **Graph Engine** (`core/graph.py`)
   - `Graph`: 图执行引擎 / Graph execution engine
   - `Node`: 执行节点 / Execution node
   - `Edge`: 连接边 / Connection edge

3. **Agent Framework** (`agents/`)
   - `BaseAgent`: 代理基类 / Agent base class
   - `SimpleAgent`: 简单代理实现 / Simple agent implementation
   - `Tool`: 工具接口 / Tool interface

4. **API Layer** (`api/`)
   - FastAPI 应用 / FastAPI application
   - REST 接口 / REST interface
   - 请求/响应模型 / Request/response models

### 执行流程 / Execution Flow

```
用户输入 → 图执行 → 节点处理 → 状态更新 → 结果返回
User Input → Graph Execution → Node Processing → State Update → Result Return
    ↓
input → analyze → use_tool → respond → check_complete → output
```

## 性能优化 / Performance Optimization

### 1. 批量操作 / Batch Operations
```python
# 使用 MultiEdit 进行批量文件编辑 / Use MultiEdit for batch file editing
# 并行执行独立操作 / Execute independent operations in parallel
```

### 2. 缓存策略 / Caching Strategy
```python
# 缓存代理实例 / Cache agent instances
# 缓存图结构 / Cache graph structures
# 缓存工具结果 / Cache tool results
```

### 3. 内存管理 / Memory Management
```python
# 使用不可变状态避免内存泄漏 / Use immutable state to avoid memory leaks
# 及时清理临时变量 / Clean up temporary variables promptly
```

## 扩展开发 / Extension Development

### 添加新工具 / Adding New Tools

```python
# 1. 创建工具函数 / 1. Create tool function
def search_tool(query: str) -> str:
    return f"Search results for: {query}"

# 2. 注册工具 / 2. Register tool
tool = SimpleTool("search", "Search for information", search_tool)
agent.register_tool(tool)
```

### 创建新代理 / Creating New Agents

```python
class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom_agent")
        # 注册工具 / Register tools
        # 定义图结构 / Define graph structure
    
    def create_graph(self):
        # 自定义图结构 / Custom graph structure
        pass
```

### 自定义节点 / Custom Nodes

```python
def custom_node(state: AgentState) -> AgentState:
    # 自定义处理逻辑 / Custom processing logic
    return state.add_message("system", "Custom processing")

# 添加到图中 / Add to graph
graph.add_node("custom", custom_node)
```

## 故障排除 / Troubleshooting

### 常见错误 / Common Errors

1. **ImportError**: 检查虚拟环境是否激活 / Check if virtual environment is activated
2. **TypeError**: 检查函数签名和类型提示 / Check function signatures and type hints
3. **ValidationError**: 检查状态数据类型 / Check state data types
4. **ExecutionError**: 检查图结构和节点逻辑 / Check graph structure and node logic

### 调试步骤 / Debugging Steps

1. 检查日志输出 / Check log output
2. 运行测试用例 / Run test cases
3. 验证数据流 / Validate data flow
4. 检查状态变化 / Check state changes
5. 确认工具调用 / Confirm tool calls

## 部署 / Deployment

### Docker 部署 / Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api.app:create_app", "--host", "0.0.0.0", "--port", "8000"]
```

### 生产环境配置 / Production Configuration

```python
# 使用环境变量 / Use environment variables
import os
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")

# 配置日志 / Configure logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
```

## 贡献指南 / Contribution Guide

1. Fork 项目 / Fork the project
2. 创建功能分支 / Create feature branch
3. 编写测试 / Write tests
4. 提交 PR / Submit PR
5. 代码审查 / Code review

## 许可证 / License

本项目采用 MIT 许可证。/ This project uses the MIT license.

## 联系方式 / Contact

如有问题，请提交 Issue 或联系开发者。/ If you have questions, please submit an Issue or contact the developer.