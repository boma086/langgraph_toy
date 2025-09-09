"""API endpoints for LangGraph toy."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import time
import logging
from agents.simple import SimpleAgent
from core.state import AgentState, GraphState
from core.graph import Graph
from api.models import ExecuteRequest, ExecuteResponse, ChatRequest, ChatResponse, GraphStateRequest, GraphStateResponse


logger = logging.getLogger(__name__)
router = APIRouter()


# Global agent instance
simple_agent = SimpleAgent()


@router.post("/execute", response_model=ExecuteResponse)
async def execute_graph(request: ExecuteRequest):
    """Execute a graph with given input data."""
    start_time = time.time()
    
    try:
        # Create graph based on type
        if request.graph_type == "simple_agent":
            graph = simple_agent.create_graph()
            initial_state = simple_agent.process_input(request.input_data.get("message", ""))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown graph type: {request.graph_type}")
        
        # Execute graph
        result_state = graph.execute(initial_state)
        
        execution_time = time.time() - start_time
        
        return ExecuteResponse(
            success=True,
            result=result_state.to_dict(),
            execution_time=execution_time
        )
    
    except Exception as e:
        logger.error(f"Graph execution failed: {e}")
        execution_time = time.time() - start_time
        return ExecuteResponse(
            success=False,
            result={},
            execution_time=execution_time,
            error=str(e)
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with an agent."""
    try:
        agent = simple_agent
        
        if request.agent_type == "simple":
            response = agent.run(request.message)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
        
        return ChatResponse(
            response=response,
            agent_type=request.agent_type,
            timestamp=time.time()
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for bad requests)
        raise
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """List available agents."""
    return {
        "agents": [
            {
                "name": "simple",
                "description": "Simple reasoning agent with basic tools",
                "tools": simple_agent.list_tools()
            }
        ]
    }


@router.get("/agents/{agent_name}/tools")
async def get_agent_tools(agent_name: str):
    """Get tools for a specific agent."""
    if agent_name == "simple":
        return {
            "agent": agent_name,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in simple_agent.tools.values()
            ]
        }
    else:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")


@router.post("/state", response_model=GraphStateResponse)
async def manage_state(request: GraphStateRequest):
    """Manage graph state operations."""
    try:
        if request.operation == "get":
            # Just return the state data
            return GraphStateResponse(
                success=True,
                state=request.state_data,
                message="State retrieved successfully"
            )
        
        elif request.operation == "set":
            # Create new state with provided data
            if "messages" in request.state_data:
                state = AgentState(**request.state_data)
            else:
                state = GraphState(**request.state_data)
            
            return GraphStateResponse(
                success=True,
                state=state.to_dict(),
                message="State created successfully"
            )
        
        elif request.operation == "update":
            # Update existing state (this is a simplified example)
            current_state = request.state_data
            # In a real implementation, you would load the existing state and update it
            
            return GraphStateResponse(
                success=True,
                state=current_state,
                message="State updated successfully"
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {request.operation}")
    
    except Exception as e:
        logger.error(f"State operation failed: {e}")
        return GraphStateResponse(
            success=False,
            state={},
            message=str(e)
        )


@router.get("/graph/validate")
async def validate_graph():
    """Validate the current graph structure."""
    try:
        graph = simple_agent.create_graph()
        issues = graph.validate()
        
        return {
            "graph_name": graph.name,
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
            "entry_point": graph.entry_point,
            "validation_issues": issues,
            "is_valid": len(issues) == 0
        }
    
    except Exception as e:
        logger.error(f"Graph validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/visualize")
async def visualize_graph():
    """Get a text visualization of the graph."""
    try:
        graph = simple_agent.create_graph()
        visualization = graph.visualize()
        
        return {
            "graph_name": graph.name,
            "visualization": visualization
        }
    
    except Exception as e:
        logger.error(f"Graph visualization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph/execute")
async def execute_custom_graph(request: Dict[str, Any]):
    """Execute a custom graph with provided configuration."""
    try:
        # This is a simplified example - in a real implementation,
        # you would parse the graph configuration and create the graph dynamically
        
        graph_type = request.get("graph_type", "simple_agent")
        input_data = request.get("input_data", {})
        
        if graph_type == "simple_agent":
            graph = simple_agent.create_graph()
            initial_state = simple_agent.process_input(input_data.get("message", ""))
            result_state = graph.execute(initial_state)
            
            return {
                "success": True,
                "result": result_state.to_dict(),
                "graph_type": graph_type
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown graph type: {request.graph_type}")
    
    except Exception as e:
        logger.error(f"Custom graph execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "agents": len([simple_agent]),
        "ready": True
    }