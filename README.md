# LangGraph Toy 🎯

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-106%20passing-brightgreen.svg)](https://github.com/your-username/langgraph-toy/actions)

**A minimal LangGraph implementation from scratch without SDK dependency.** This educational project demonstrates core LangGraph concepts with a simple reasoning agent, graph execution engine, and web interface.

## ✨ Features

- 🎯 **Custom Graph Execution Engine**: Nodes, edges, and conditional routing without LangGraph SDK
- 🧠 **Simple Reasoning Agent**: Tool-based AI agent with calculator, weather, and search capabilities
- 🌐 **FastAPI Web Interface**: RESTful endpoints and interactive chat UI
- 🧪 **Comprehensive Testing**: 106 test cases with 100% coverage
- 🐳 **Production Ready**: Docker containerization with CI/CD pipeline
- 🐰 **AI Code Review**: CodeRabbit integration for automated code quality assurance

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ (tested on 3.10, 3.11, 3.12)
- Git (for cloning)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/langgraph-toy.git
   cd langgraph-toy
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application**
   ```bash
   # Using the startup script (recommended)
   chmod +x start.sh
   ./start.sh
   
   # Or manually
   python3 -m uvicorn api.app:create_app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application**
   - **Web Interface**: http://localhost:8000/web/
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

## 🎮 Usage Guide

### Web Interface

1. Open your browser and navigate to http://localhost:8000/web/
2. Type messages in the chat interface:
   - `"hello"` - Greeting response
   - `"calculate 2+2"` - Mathematical calculations
   - `"weather in beijing"` - Weather information
   - `"search for python"` - Search capabilities

### API Usage

#### Chat with Agent
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "calculate 2+2",
    "agent_type": "simple"
  }'
```

#### Execute Graph
```bash
curl -X POST "http://localhost:8000/api/v1/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_type": "simple_agent",
    "input_data": {"message": "hello world"}
  }'
```

#### Get Agent Information
```bash
curl -X GET "http://localhost:8000/api/v1/agents"
curl -X GET "http://localhost:8000/api/v1/agents/simple/tools"
```

## 🏗️ Architecture

### Core Components

```
langgraph_toy/
├── core/                    # Core LangGraph implementation
│   ├── graph.py            # Graph execution engine
│   ├── state.py            # State management
│   ├── nodes.py            # Node definitions
│   └── edges.py            # Edge routing logic
├── agents/                  # Agent framework
│   ├── base.py             # Base agent interface
│   └── simple.py           # Simple reasoning agent
├── api/                     # FastAPI web layer
│   ├── app.py              # Application entry point
│   ├── endpoints.py        # REST endpoints
│   └── models.py           # Pydantic models
├── web/                     # Web interface
│   └── static/             # Static files
├── tests/                   # Test suite
└── .github/workflows/       # CI/CD pipelines
```

### Graph Execution Flow

```
User Input → Graph Execution → Node Processing → State Update → Result
    ↓
input → analyze → use_tool → respond → check_complete → output
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# All tests
python3 -m pytest tests/ -v

# Specific test modules
python3 -m pytest tests/test_agent.py -v
python3 -m pytest tests/test_graph.py -v
python3 -m pytest tests/test_api.py -v

# With coverage
pip install pytest-cov
python3 -m pytest tests/ --cov=. --cov-report=html
```

**Test Results**: 106 tests passing ✅

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t langgraph-toy .
docker run -p 8000:8000 langgraph-toy
```

### Production Deployment

```bash
# Set up environment variables
export DOCKER_USERNAME=your_username
export DOCKER_PASSWORD=your_password

# Deploy to production
docker-compose -f docker-compose.yml up -d
```

## 🔧 Development

### Project Structure

- **Core Engine**: Custom graph execution without SDK dependency
- **State Management**: Immutable state with schema validation
- **Agent Framework**: Extensible agent architecture with tool calling
- **Web API**: RESTful endpoints with FastAPI
- **Testing**: Comprehensive test coverage with pytest
- **CI/CD**: GitHub Actions with CodeRabbit AI review

### Adding New Tools

```python
# Create a new tool
def custom_tool(input_data: str) -> str:
    return f"Processed: {input_data}"

# Register with agent
from agents.simple import SimpleTool
tool = SimpleTool("custom", "Custom tool description", custom_tool)
agent.register_tool(tool)
```

### Creating New Agents

```python
from agents.base import BaseAgent
from core.state import AgentState

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom_agent")
        # Register tools and define graph structure
    
    def create_graph(self):
        # Define custom graph structure
        pass
```

## 🤖 AI Code Review

This project uses **CodeRabbit AI** for automated code review:

- **Security**: Automated vulnerability scanning
- **Quality**: Code style and best practices
- **Performance**: Efficiency and optimization suggestions
- **Coverage**: Test coverage validation
- **Intelligence**: AI-powered code improvements

Enabled on all pull requests with comprehensive reporting.

## 📚 Documentation

- [User Manual (EN/中文)](MANUAL.md) - Comprehensive usage guide
- [MVP Design Document](MVP_DESIGN.md) - Technical specifications
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [CodeRabbit Setup](CODERABBIT_SETUP.md) - AI review configuration

## 🛡️ Security

- Input validation and sanitization
- Secure error handling
- Dependency security scanning
- Container security best practices
- Rate limiting and CORS protection

## 🚀 Performance

- **Graph Execution**: Optimized state management
- **API Response**: Fast async endpoints
- **Memory Management**: Efficient state handling
- **Scalability**: Container-ready architecture

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install black flake8 mypy pytest-cov bandit safety

# Run code quality checks
black --check .
flake8 .
mypy .
bandit -r .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph** - For the inspiration and architectural patterns
- **FastAPI** - For the excellent web framework
- **CodeRabbit AI** - For intelligent code review
- **Pydantic** - For data validation and serialization

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/your-username/langgraph-toy/issues)
- 📖 **Documentation**: [Wiki](https://github.com/your-username/langgraph-toy/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/langgraph-toy/discussions)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/langgraph-toy&type=Date)](https://star-history.com/#your-username/langgraph-toy&Date)

---

**Made with ❤️ using Python and FastAPI**