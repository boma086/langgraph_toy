# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a custom LangGraph MVP implementation built from scratch without using the LangGraph SDK. The project implements core LangGraph concepts including graph execution, state management, and agent functionality with a web interface.

## Development Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py

# Run tests
python3 -m pytest tests/

# Run strategy selection tests
python3 -m pytest tests/test_strategy_selector.py

# Run compilation tests  
python3 -m pytest tests/test_compilation.py
```

## Architecture

### Core Components
- **core/graph.py**: Graph execution engine with nodes and edges
- **core/state.py**: State management with schema validation
- **core/nodes.py**: Node definitions and execution logic
- **core/edges.py**: Edge routing and conditional logic
- **core/execution.py**: Strategy pattern execution system (Traditional vs Compiled)
- **core/compilation.py**: Agent compilation with LangGraph-like API
- **core/strategy_selector.py**: Multi-level strategy selection system
- **agents/**: Agent implementations with base interfaces
- **api/**: FastAPI web server with configurable strategy support
- **web/**: Static web interface for agent interaction

### Key Design Principles
- **No SDK Dependency**: Custom implementation of LangGraph concepts
- **State Management**: Immutable state with schema validation
- **Graph Execution**: Sequential processing with conditional routing
- **Strategy Pattern**: Configurable execution strategies (Traditional vs Compiled)
- **Configuration-Driven**: Multi-level strategy selection without code changes
- **Agent Framework**: Tool-based architecture with reasoning capabilities
- **Web API**: RESTful endpoints with runtime strategy selection

## Common Commands

```bash
# Start development server
python3 main.py

# Run all tests
python3 -m pytest tests/

# Run specific test file
python3 -m pytest tests/test_graph.py

# Run with coverage
python3 -m pytest tests/ --cov=core --cov=agents

# Lint code (if flake8 installed)
flake8 core agents api tests

# Type checking (if mypy installed)
mypy core agents api
```

## Testing Strategy

### Test Structure
- **test_graph.py**: Graph execution and node routing
- **test_state.py**: State management and validation
- **test_agent.py**: Agent functionality and tool usage
- **test_api.py**: Web API endpoints and integration
- **test_compilation.py**: Agent compilation and strategy tests
- **test_strategy_selector.py**: Multi-level strategy selection tests

### Test Patterns
- Test graph execution with different node configurations
- Validate state schema enforcement and immutability
- Test agent reasoning and tool calling capabilities
- Verify API endpoints handle various input scenarios
- Integration tests for complete workflows

## Development Workflow

1. **Implement Core Logic**: Add nodes, edges, or state schemas
2. **Write Tests**: Create comprehensive test coverage
3. **Test Locally**: Verify functionality with pytest
4. **API Integration**: Add web endpoints if needed
5. **Web Interface**: Update UI for new functionality
6. **Documentation**: Update code comments and docstrings

## Key Concepts

### State Management
- State is immutable and passed between nodes
- Schema validation ensures type safety
- State updates create new instances rather than modifying existing ones

### Graph Execution
- Nodes process state and return updates
- Edges define flow between nodes (sequential or conditional)
- Graph executes nodes in order based on edge routing
- Execution stops when no more edges can be followed

### Agent Framework
- Agents use tools to perform actions
- State tracks agent messages, tool calls, and intermediate steps
- Reasoning loop continues until task completion or max iterations
- Web interface provides chat-based interaction

## Execution Strategies

### Strategy Types
- **Traditional**: Creates new graph for each execution (default for debugging)
- **Compiled**: Caches and reuses graphs for better performance
- **Auto**: Intelligently selects based on request complexity

### Strategy Selection
The system supports multi-level strategy selection:
1. **Request Level**: `{"strategy": "compiled"}` in request body
2. **Header Level**: `X-Execution-Strategy: compiled` HTTP header
3. **Environment Level**: `DEFAULT_STRATEGY=compiled` environment variable
4. **Auto Selection**: `AUTO_STRATEGY=true` with complexity analysis

### Usage Examples
```python
from core.compilation import compile

# Compile agent for better performance
compiled_agent = compile(agent)
result = compiled_agent.run("Hello")

# Original approach still works unchanged
result = agent.run("Hello")
```

### Configuration
```bash
# Environment configuration
export DEFAULT_STRATEGY=compiled
export AUTO_STRATEGY=true
export COMPILED_CACHE_SIZE=50

# Start server
python main.py
```