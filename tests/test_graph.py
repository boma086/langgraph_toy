"""Tests for graph execution engine."""

import pytest
from core.graph import Graph, Node, Edge
from core.state import StateSchema, GraphState


class TestNode:
    """Test Node functionality."""
    
    def test_node_creation(self):
        """Test node creation."""
        def test_func(state):
            return state.set("result", "test")
        
        node = Node("test_node", test_func)
        
        assert node.name == "test_node"
        assert node.func == test_func
    
    def test_node_execution(self):
        """Test node execution."""
        def test_func(state):
            return state.set("result", "executed")
        
        node = Node("test_node", test_func)
        state = StateSchema()
        result = node.execute(state)
        
        assert result.get("result") == "executed"
    
    def test_node_execution_error(self):
        """Test node execution error handling."""
        def error_func(state):
            raise ValueError("Test error")
        
        node = Node("error_node", error_func)
        state = StateSchema()
        
        with pytest.raises(ValueError, match="Test error"):
            node.execute(state)
    
    def test_node_representation(self):
        """Test node string representation."""
        def test_func(state):
            return state
        
        node = Node("test_node", test_func)
        assert repr(node) == "Node('test_node')"


class TestEdge:
    """Test Edge functionality."""
    
    def test_edge_creation(self):
        """Test edge creation."""
        edge = Edge("source", "target")
        
        assert edge.source == "source"
        assert edge.target == "target"
        assert edge.condition is None
    
    def test_conditional_edge_creation(self):
        """Test conditional edge creation."""
        def condition(state):
            return state.get("test") == True
        
        edge = Edge("source", "target", condition)
        
        assert edge.source == "source"
        assert edge.target == "target"
        assert edge.condition == condition
    
    def test_unconditional_edge_follow(self):
        """Test unconditional edge following."""
        edge = Edge("source", "target")
        state = StateSchema()
        
        assert edge.should_follow(state) is True
    
    def test_conditional_edge_follow_true(self):
        """Test conditional edge following when condition is true."""
        def condition(state):
            return state.get("test") == True
        
        edge = Edge("source", "target", condition)
        state = StateSchema(test=True)
        
        assert edge.should_follow(state) is True
    
    def test_conditional_edge_follow_false(self):
        """Test conditional edge following when condition is false."""
        def condition(state):
            return state.get("test") == True
        
        edge = Edge("source", "target", condition)
        state = StateSchema(test=False)
        
        assert edge.should_follow(state) is False
    
    def test_edge_representation(self):
        """Test edge string representation."""
        edge = Edge("source", "target")
        assert repr(edge) == "Edge('source' -> 'target')"
        
        def condition(state):
            return True
        
        conditional_edge = Edge("source", "target", condition)
        assert "condition" in repr(conditional_edge)


class TestGraph:
    """Test Graph functionality."""
    
    def test_empty_graph_creation(self):
        """Test empty graph creation."""
        graph = Graph("test_graph")
        
        assert graph.name == "test_graph"
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.entry_point is None
    
    def test_add_node(self):
        """Test adding nodes to graph."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        
        assert len(graph.nodes) == 1
        assert "node1" in graph.nodes
        assert graph.nodes["node1"].name == "node1"
        assert graph.entry_point == "node1"  # First node becomes entry point
    
    def test_add_duplicate_node(self):
        """Test adding duplicate node raises error."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        
        with pytest.raises(ValueError, match="Node 'node1' already exists"):
            graph.add_node("node1", test_func)
    
    def test_add_edge(self):
        """Test adding edges to graph."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        graph.add_node("node2", test_func)
        graph.add_edge("node1", "node2")
        
        assert len(graph.edges) == 1
        assert graph.edges[0].source == "node1"
        assert graph.edges[0].target == "node2"
    
    def test_add_edge_nonexistent_nodes(self):
        """Test adding edge with nonexistent nodes raises error."""
        graph = Graph("test_graph")
        
        with pytest.raises(ValueError, match="Source node 'nonexistent' not found"):
            graph.add_edge("nonexistent", "target")
        
        # Add a source node first
        def test_func(state):
            return state
        
        graph.add_node("source", test_func)
        
        with pytest.raises(ValueError, match="Target node 'nonexistent' not found"):
            graph.add_edge("source", "nonexistent")
    
    def test_set_entry_point(self):
        """Test setting entry point."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        graph.add_node("node2", test_func)
        graph.set_entry_point("node2")
        
        assert graph.entry_point == "node2"
    
    def test_set_entry_point_nonexistent(self):
        """Test setting nonexistent entry point raises error."""
        graph = Graph("test_graph")
        
        with pytest.raises(ValueError, match="Node 'nonexistent' not found"):
            graph.set_entry_point("nonexistent")
    
    def test_get_next_nodes(self):
        """Test getting next nodes."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        graph.add_node("node2", test_func)
        graph.add_node("node3", test_func)
        
        graph.add_edge("node1", "node2")
        graph.add_edge("node1", "node3")
        
        state = StateSchema()
        next_nodes = graph.get_next_nodes("node1", state)
        
        assert len(next_nodes) == 2
        assert "node2" in next_nodes
        assert "node3" in next_nodes
    
    def test_get_next_nodes_with_conditions(self):
        """Test getting next nodes with conditions."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        def condition(state):
            return state.get("test") == True
        
        graph.add_node("node1", test_func)
        graph.add_node("node2", test_func)
        graph.add_node("node3", test_func)
        
        graph.add_edge("node1", "node2", condition)
        graph.add_edge("node1", "node3")
        
        # Condition true
        state_true = StateSchema(test=True)
        next_nodes = graph.get_next_nodes("node1", state_true)
        assert len(next_nodes) == 2
        
        # Condition false
        state_false = StateSchema(test=False)
        next_nodes = graph.get_next_nodes("node1", state_false)
        assert len(next_nodes) == 1
        assert "node3" in next_nodes
    
    def test_simple_execution(self):
        """Test simple graph execution."""
        graph = Graph("test_graph")
        
        def node1_func(state):
            return state.set("step1", "completed")
        
        def node2_func(state):
            return state.set("step2", "completed")
        
        graph.add_node("node1", node1_func)
        graph.add_node("node2", node2_func)
        graph.add_edge("node1", "node2")
        
        initial_state = StateSchema()
        final_state = graph.execute(initial_state)
        
        assert final_state.get("step1") == "completed"
        assert final_state.get("step2") == "completed"
    
    def test_execution_with_conditional_edge(self):
        """Test execution with conditional edges."""
        graph = Graph("test_graph")
        
        def node1_func(state):
            return state
        
        def node2_func(state):
            return state.set("path", "taken")
        
        def node3_func(state):
            return state.set("path", "not_taken")
        
        def condition(state):
            return state.get("take_path") == True
        
        graph.add_node("node1", node1_func)
        graph.add_node("node2", node2_func)
        graph.add_node("node3", node3_func)
        
        graph.add_edge("node1", "node2", condition)
        graph.add_edge("node1", "node3")
        
        # Test condition true
        initial_state = StateSchema(take_path=True)
        final_state = graph.execute(initial_state)
        assert final_state.get("path") == "taken"
        
        # Test condition false
        initial_state = StateSchema(take_path=False)
        final_state = graph.execute(initial_state)
        assert final_state.get("path") == "not_taken"
    
    def test_execution_no_entry_point(self):
        """Test execution without entry point raises error."""
        graph = Graph("test_graph")
        
        with pytest.raises(ValueError, match="Graph has no entry point"):
            graph.execute(StateSchema())
    
    def test_execution_nonexistent_node(self):
        """Test execution with nonexistent node raises error."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        
        with pytest.raises(ValueError, match="Node 'nonexistent' not found"):
            graph.set_entry_point("nonexistent")
    
    def test_execution_cycle_detection(self):
        """Test cycle detection during execution."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        graph.add_node("node2", test_func)
        
        # Create cycle
        graph.add_edge("node1", "node2")
        graph.add_edge("node2", "node1")
        
        with pytest.raises(ValueError, match="Cycle detected"):
            graph.execute(StateSchema())
    
    def test_graph_validation(self):
        """Test graph validation."""
        graph = Graph("test_graph")
        
        # Empty graph
        issues = graph.validate()
        assert len(issues) > 0
        assert any("no nodes" in issue for issue in issues)
        
        # Graph with nodes but no entry point
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        graph.add_node("node2", test_func)
        
        issues = graph.validate()
        assert any("entry point" in issue for issue in issues)
        
        # Valid graph
        graph.set_entry_point("node1")
        graph.add_edge("node1", "node2")
        
        issues = graph.validate()
        assert len(issues) == 0
    
    def test_graph_visualization(self):
        """Test graph visualization."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        graph.add_node("node2", test_func)
        graph.add_edge("node1", "node2")
        graph.set_entry_point("node1")
        
        viz = graph.visualize()
        
        assert "Graph: test_graph" in viz
        assert "Entry point: node1" in viz
        assert "node1" in viz
        assert "node2" in viz
        assert "node1 -> node2" in viz
    
    def test_graph_representation(self):
        """Test graph string representation."""
        graph = Graph("test_graph")
        
        def test_func(state):
            return state
        
        graph.add_node("node1", test_func)
        graph.add_node("node2", test_func)
        graph.add_edge("node1", "node2")
        
        repr_str = repr(graph)
        assert "test_graph" in repr_str
        assert "nodes=2" in repr_str
        assert "edges=1" in repr_str