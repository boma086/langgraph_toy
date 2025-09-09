"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    def test_api_health_check(self, client):
        """Test API health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "agents" in data
        assert data["ready"] is True


class TestAgentEndpoints:
    """Test agent-related endpoints."""
    
    def test_list_agents(self, client):
        """Test listing available agents."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) > 0
        
        agent = data["agents"][0]
        assert "name" in agent
        assert "description" in agent
        assert "tools" in agent
    
    def test_get_agent_tools(self, client):
        """Test getting tools for specific agent."""
        response = client.get("/api/v1/agents/simple/tools")
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent"] == "simple"
        assert "tools" in data
        assert len(data["tools"]) > 0
        
        tool = data["tools"][0]
        assert "name" in tool
        assert "description" in tool
    
    def test_get_nonexistent_agent_tools(self, client):
        """Test getting tools for nonexistent agent."""
        response = client.get("/api/v1/agents/nonexistent/tools")
        assert response.status_code == 404


class TestChatEndpoints:
    """Test chat endpoints."""
    
    def test_chat_with_simple_agent(self, client):
        """Test chatting with simple agent."""
        response = client.post("/api/v1/chat", json={
            "message": "hello",
            "agent_type": "simple"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert data["agent_type"] == "simple"
        assert "timestamp" in data
        assert len(data["response"]) > 0
    
    def test_chat_with_calculation(self, client):
        """Test chatting with calculation."""
        response = client.post("/api/v1/chat", json={
            "message": "calculate 2+2",
            "agent_type": "simple"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0
        # Should contain tool result information
    
    def test_chat_with_weather_query(self, client):
        """Test chatting with weather query."""
        response = client.post("/api/v1/chat", json={
            "message": "weather in beijing",
            "agent_type": "simple"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0
    
    def test_chat_with_search_query(self, client):
        """Test chatting with search query."""
        response = client.post("/api/v1/chat", json={
            "message": "search for python",
            "agent_type": "simple"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0
    
    def test_chat_with_invalid_agent_type(self, client):
        """Test chatting with invalid agent type."""
        response = client.post("/api/v1/chat", json={
            "message": "hello",
            "agent_type": "nonexistent"
        })
        assert response.status_code == 400
    
    def test_chat_with_empty_message(self, client):
        """Test chatting with empty message."""
        response = client.post("/api/v1/chat", json={
            "message": "",
            "agent_type": "simple"
        })
        # Should still work - empty messages are valid
        assert response.status_code == 200


class TestExecuteEndpoints:
    """Test graph execution endpoints."""
    
    def test_execute_simple_agent_graph(self, client):
        """Test executing simple agent graph."""
        response = client.post("/api/v1/execute", json={
            "graph_type": "simple_agent",
            "input_data": {"message": "hello world"}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert "execution_time" in data
        assert data["execution_time"] > 0
    
    def test_execute_with_invalid_graph_type(self, client):
        """Test executing with invalid graph type."""
        response = client.post("/api/v1/execute", json={
            "graph_type": "nonexistent",
            "input_data": {"message": "hello"}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_execute_custom_graph(self, client):
        """Test executing custom graph."""
        response = client.post("/api/v1/graph/execute", json={
            "graph_type": "simple_agent",
            "input_data": {"message": "hello world"}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert data["graph_type"] == "simple_agent"


class TestStateEndpoints:
    """Test state management endpoints."""
    
    def test_get_state(self, client):
        """Test getting state."""
        response = client.post("/api/v1/state", json={
            "state_data": {"test": "value"},
            "operation": "get"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["state"] == {"test": "value"}
    
    def test_set_agent_state(self, client):
        """Test setting agent state."""
        response = client.post("/api/v1/state", json={
            "state_data": {
                "messages": [{"role": "user", "content": "hello"}],
                "tool_calls": [],
                "intermediate_steps": [],
                "is_complete": False
            },
            "operation": "set"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "state" in data
        assert "messages" in data["state"]
    
    def test_set_graph_state(self, client):
        """Test setting graph state."""
        response = client.post("/api/v1/state", json={
            "state_data": {
                "current_node": "node1",
                "next_node": "node2",
                "context": {"input": "test"},
                "results": {}
            },
            "operation": "set"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "state" in data
        assert data["state"]["current_node"] == "node1"
    
    def test_update_state(self, client):
        """Test updating state."""
        response = client.post("/api/v1/state", json={
            "state_data": {"test": "value"},
            "operation": "update"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["state"] == {"test": "value"}
    
    def test_invalid_operation(self, client):
        """Test invalid state operation."""
        response = client.post("/api/v1/state", json={
            "state_data": {"test": "value"},
            "operation": "invalid"
        })
        assert response.status_code == 200


class TestGraphEndpoints:
    """Test graph management endpoints."""
    
    def test_validate_graph(self, client):
        """Test graph validation."""
        response = client.get("/api/v1/graph/validate")
        assert response.status_code == 200
        
        data = response.json()
        assert "graph_name" in data
        assert "nodes" in data
        assert "edges" in data
        assert "entry_point" in data
        assert "validation_issues" in data
        assert "is_valid" in data
        assert data["nodes"] > 0
        assert data["edges"] > 0
    
    def test_visualize_graph(self, client):
        """Test graph visualization."""
        response = client.get("/api/v1/graph/visualize")
        assert response.status_code == 200
        
        data = response.json()
        assert "graph_name" in data
        assert "visualization" in data
        assert len(data["visualization"]) > 0
        assert "simple_agent_graph" in data["visualization"]


class TestWebInterface:
    """Test web interface accessibility."""
    
    def test_serve_static_files(self, client):
        """Test serving static files."""
        response = client.get("/web/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        # The response should be JSON content
        content = response.json()
        assert "LangGraph Toy API" in content["message"]
        
        # Test the web interface separately
        response = client.get("/web/")
        assert response.status_code == 200
        content = response.text
        assert "LangGraph Toy" in content
        assert "Simple Agent Interface" in content


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_json(self, client):
        """Test invalid JSON in request body."""
        response = client.post("/api/v1/chat", data="invalid json")
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test missing required fields."""
        response = client.post("/api/v1/chat", json={"agent_type": "simple"})
        assert response.status_code == 422
    
    def test_server_error_handling(self, client):
        """Test server error handling."""
        # This test would need to be customized based on potential error scenarios
        pass


class TestPerformance:
    """Test performance-related functionality."""
    
    def test_execution_time_measurement(self, client):
        """Test that execution time is measured."""
        response = client.post("/api/v1/execute", json={
            "graph_type": "simple_agent",
            "input_data": {"message": "hello"}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "execution_time" in data
        assert isinstance(data["execution_time"], (int, float))
        assert data["execution_time"] >= 0
    
    def test_multiple_requests(self, client):
        """Test handling multiple requests."""
        responses = []
        for i in range(5):
            response = client.post("/api/v1/chat", json={
                "message": f"hello {i}",
                "agent_type": "simple"
            })
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert len(data["response"]) > 0