"""Graph execution engine with nodes and edges."""

from typing import Dict, Callable, Any, List, Optional, Set
from .state import StateSchema, GraphState
import logging


logger = logging.getLogger(__name__)


class Node:
    """Represents a node in the graph that processes state."""
    
    def __init__(self, name: str, func: Callable[[StateSchema], StateSchema]):
        """Initialize a node.
        
        Args:
            name: Unique identifier for the node
            func: Function that processes state and returns updated state
        """
        self.name = name
        self.func = func
    
    def execute(self, state: StateSchema) -> StateSchema:
        """Execute the node function with the given state."""
        logger.info(f"Executing node: {self.name}")
        try:
            result = self.func(state)
            logger.info(f"Node {self.name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Node {self.name} failed: {e}")
            raise
    
    def __repr__(self) -> str:
        return f"Node('{self.name}')"


class Edge:
    """Represents an edge connecting nodes in the graph."""
    
    def __init__(self, source: str, target: str, condition: Optional[Callable[[StateSchema], bool]] = None):
        """Initialize an edge.
        
        Args:
            source: Source node name
            target: Target node name
            condition: Optional function to determine if edge should be followed
        """
        self.source = source
        self.target = target
        self.condition = condition
    
    def should_follow(self, state: StateSchema) -> bool:
        """Check if this edge should be followed given the current state."""
        if self.condition is None:
            return True
        return self.condition(state)
    
    def __repr__(self) -> str:
        condition_str = f" (condition: {self.condition.__name__})" if self.condition else ""
        return f"Edge('{self.source}' -> '{self.target}'{condition_str})"


class Graph:
    """Graph execution engine that manages nodes and edges."""
    
    def __init__(self, name: str = "graph"):
        """Initialize an empty graph."""
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.entry_point: Optional[str] = None
    
    def add_node(self, name: str, func: Callable[[StateSchema], StateSchema]) -> 'Graph':
        """Add a node to the graph."""
        if name in self.nodes:
            raise ValueError(f"Node '{name}' already exists")
        
        self.nodes[name] = Node(name, func)
        
        # If this is the first node, set it as entry point
        if self.entry_point is None:
            self.entry_point = name
        
        return self
    
    def add_edge(self, source: str, target: str, condition: Optional[Callable[[StateSchema], bool]] = None) -> 'Graph':
        """Add an edge to the graph."""
        if source not in self.nodes:
            raise ValueError(f"Source node '{source}' not found")
        if target not in self.nodes:
            raise ValueError(f"Target node '{target}' not found")
        
        self.edges.append(Edge(source, target, condition))
        return self
    
    def set_entry_point(self, node_name: str) -> 'Graph':
        """Set the entry point for the graph."""
        if node_name not in self.nodes:
            raise ValueError(f"Node '{node_name}' not found")
        self.entry_point = node_name
        return self
    
    def get_next_nodes(self, current_node: str, state: StateSchema) -> List[str]:
        """Get all possible next nodes from the current node."""
        next_nodes = []
        
        for edge in self.edges:
            if edge.source == current_node and edge.should_follow(state):
                next_nodes.append(edge.target)
        
        return next_nodes
    
    def execute(self, initial_state: StateSchema) -> StateSchema:
        """Execute the graph with the given initial state."""
        if self.entry_point is None:
            raise ValueError("Graph has no entry point")
        
        logger.info(f"Starting graph execution: {self.name}")
        
        current_state = initial_state
        current_node = self.entry_point
        visited_nodes: Set[str] = set()
        
        while current_node is not None:
            if current_node in visited_nodes:
                raise ValueError(f"Cycle detected: node '{current_node}' already visited")
            
            if current_node not in self.nodes:
                raise ValueError(f"Node '{current_node}' not found")
            
            # Execute current node
            node = self.nodes[current_node]
            current_state = node.execute(current_state)
            visited_nodes.add(current_node)
            
            # Find next nodes
            next_nodes = self.get_next_nodes(current_node, current_state)
            
            if not next_nodes:
                logger.info("No more edges to follow, execution complete")
                break
            elif len(next_nodes) > 1:
                logger.warning(f"Multiple next nodes found: {next_nodes}. Taking first: {next_nodes[0]}")
            
            current_node = next_nodes[0]
        
        logger.info(f"Graph execution completed. Visited nodes: {visited_nodes}")
        return current_state
    
    def validate(self) -> List[str]:
        """Validate the graph structure and return list of issues."""
        issues = []
        
        if not self.nodes:
            issues.append("Graph has no nodes")
        
        if self.entry_point is None:
            issues.append("Graph has no entry point")
        elif self.entry_point not in self.nodes:
            issues.append(f"Entry point '{self.entry_point}' not found in nodes")
        
        # Check for orphaned nodes (no incoming edges except entry point)
        nodes_with_incoming_edges = {self.entry_point}
        for edge in self.edges:
            nodes_with_incoming_edges.add(edge.target)
        
        for node_name in self.nodes:
            if node_name not in nodes_with_incoming_edges and node_name != self.entry_point:
                issues.append(f"Node '{node_name}' has no incoming edges and is not entry point")
        
        # Check for edges to non-existent nodes
        for edge in self.edges:
            if edge.source not in self.nodes:
                issues.append(f"Edge source '{edge.source}' not found")
            if edge.target not in self.nodes:
                issues.append(f"Edge target '{edge.target}' not found")
        
        return issues
    
    def visualize(self) -> str:
        """Return a simple text visualization of the graph."""
        if not self.nodes:
            return "Empty graph"
        
        lines = [f"Graph: {self.name}"]
        lines.append(f"Entry point: {self.entry_point}")
        lines.append("Nodes:")
        
        for node_name in self.nodes:
            lines.append(f"  - {node_name}")
        
        lines.append("Edges:")
        for edge in self.edges:
            condition_str = f" [condition: {edge.condition.__name__}]" if edge.condition else ""
            lines.append(f"  - {edge.source} -> {edge.target}{condition_str}")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"Graph(name='{self.name}', nodes={len(self.nodes)}, edges={len(self.edges)})"