# LangGraph MVP Design Document

## Project Overview
Build a minimal LangGraph implementation from scratch with core functionality only.

## Core Requirements
1. **Graph Execution Engine**: Custom implementation without SDK dependency
2. **State Management**: Schema-based state with validation
3. **Simple Agent**: Basic reasoning capabilities
4. **Web API**: RESTful endpoints for graph execution
5. **Testable**: Comprehensive test coverage
6. **Web Interface**: Simple UI for agent interaction

## Architecture Design

### Core Components
```
langgraph_toy/
├── core/
│   ├── __init__.py
│   ├── graph.py          # Graph execution engine
│   ├── state.py          # State management
│   ├── nodes.py          # Node definitions
│   └── edges.py          # Edge routing logic
├── agents/
│   ├── __init__.py
│   ├── base.py           # Base agent interface
│   └── simple.py         # Simple reasoning agent
├── api/
│   ├── __init__.py
│   ├── app.py            # FastAPI application
│   └── endpoints.py      # REST endpoints
├── web/
│   ├── static/
│   │   ├── index.html    # Simple web interface
│   │   └── style.css     # Basic styling
│   └── templates/
├── tests/
│   ├── test_graph.py     # Graph execution tests
│   ├── test_state.py     # State management tests
│   └── test_agent.py     # Agent functionality tests
├── requirements.txt
└── main.py               # Entry point
```

### Minimal Feature Set

#### 1. Graph Execution Engine
- **Nodes**: Functions that process state and return updates
- **Edges**: Define flow between nodes (conditional and sequential)
- **State**: Typed dictionary with schema validation
- **Execution**: Sequential processing with state passing

#### 2. State Management
- **StateSchema**: Base class for state definition
- **StateValidator**: Schema validation and type checking
- **StateUpdater**: Immutable state updates

#### 3. Simple Agent
- **BaseAgent**: Abstract interface for agents
- **SimpleAgent**: Basic reasoning with tool usage
- **AgentState**: State schema for agent operations

#### 4. Web API
- **POST /execute**: Execute graph with initial state
- **GET /status**: Check execution status
- **POST /agent/chat**: Chat with agent via web interface

#### 5. Web Interface
- **Chat Interface**: Simple HTML/JS for agent interaction
- **State Display**: Show current state during execution
- **Error Handling**: User-friendly error messages

## Implementation Plan

### Phase 1: Core Foundation (Days 1-2)
1. **State Management System**
   - Implement StateSchema base class
   - Create StateValidator for type checking
   - Implement StateUpdater for immutable updates

2. **Graph Execution Engine**
   - Create Graph class with node/edge management
   - Implement sequential execution
   - Add conditional edge routing

### Phase 2: Agent Implementation (Day 3)
1. **Base Agent Framework**
   - Define BaseAgent interface
   - Create AgentState schema
   - Implement basic tool calling

2. **Simple Reasoning Agent**
   - Create SimpleAgent with basic reasoning
   - Add simple tools (calculator, weather)
   - Implement agent execution graph

### Phase 3: Web Layer (Day 4)
1. **REST API**
   - Set up FastAPI application
   - Create execution endpoints
   - Add error handling and validation

2. **Web Interface**
   - Build simple HTML chat interface
   - Add JavaScript for API communication
   - Style with basic CSS

### Phase 4: Testing & Polish (Day 5)
1. **Test Suite**
   - Unit tests for core components
   - Integration tests for graph execution
   - Agent functionality tests

2. **Documentation & Examples**
   - Update README with usage examples
   - Add API documentation
   - Create simple demo

## Key Design Decisions

### 1. No SDK Dependency
- Custom implementation of LangGraph concepts
- Minimal external dependencies
- Focus on educational value

### 2. State Management
- Immutable state updates
- Schema validation with type hints
- JSON serialization for web API

### 3. Graph Execution
- Sequential execution model
- Conditional routing based on state
- Error handling and recovery

### 4. Agent Design
- Tool-based architecture
- Simple reasoning loop
- Extensible for future enhancements

## Success Criteria
1. ✅ Graph executes nodes in correct order
2. ✅ State management works with validation
3. ✅ Agent can perform basic reasoning
4. ✅ Web API handles execution requests
5. ✅ Web interface allows agent interaction
6. ✅ All tests pass
7. ✅ Code is clean and documented

## Next Steps
1. Set up project structure
2. Implement core state management
3. Build graph execution engine
4. Create simple agent
5. Add web API and interface
6. Write comprehensive tests