from pydantic import BaseModel, ConfigDict
from langgraph.graph import StateGraph
import networkx as nx
from typing import Dict, List, Any

class KGState(BaseModel):
    entities: Dict[str, Dict[str, Any]]
    relations: List[Dict[str, Any]]
    graph: Any  # NetworkX graph
    metrics: Dict[str, Any] = {}
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        if 'graph' not in data:
            data['graph'] = nx.Graph()
        super().__init__(**data)

def construct_graph(state: KGState):
    # Clear existing graph to avoid duplicates
    state.graph.clear()
    
    # Add nodes with properties
    for entity, props in state.entities.items():
        state.graph.add_node(entity, **props)
    
    # Add edges with relation as an attribute
    for rel in state.relations:
        state.graph.add_edge(
            rel['source'], 
            rel['target'], 
            relation=rel.get('relation', 'related')  # Ensure 'relation' key exists
        )
    
    return state

def analyze_graph(state: KGState):
    if not hasattr(state, 'metrics'):
        state.metrics = {}
    
    state.metrics = {
        'centrality': nx.degree_centrality(state.graph),
        'communities': list(nx.algorithms.community.greedy_modularity_communities(state.graph))
    }
    return state

kg_workflow = StateGraph(KGState)
kg_workflow.add_node("build", construct_graph)
kg_workflow.add_node("analyze", analyze_graph)
kg_workflow.set_entry_point("build")
kg_workflow.add_edge("build", "analyze")
kg_workflow.set_finish_point("analyze")