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
```

## Architecture

### Core Components
- **core/graph.py**: Graph execution engine with nodes and edges
- **core/state.py**: State management with schema validation
- **core/nodes.py**: Node definitions and execution logic
- **core/edges.py**: Edge routing and conditional logic
- **agents/**: Agent implementations with base interfaces
- **api/**: FastAPI web server and REST endpoints
- **web/**: Static web interface for agent interaction

### Key Design Principles
- **No SDK Dependency**: Custom implementation of LangGraph concepts
- **State Management**: Immutable state with schema validation
- **Graph Execution**: Sequential processing with conditional routing
- **Agent Framework**: Tool-based architecture with reasoning capabilities
- **Web API**: RESTful endpoints for graph execution and agent interaction

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