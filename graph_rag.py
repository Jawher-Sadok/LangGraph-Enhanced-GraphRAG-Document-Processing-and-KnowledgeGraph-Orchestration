# graph_rag.py
from langgraph.graph import MessageGraph
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import Dict, Any, List, Union
from pydantic import BaseModel

# Initialize global variables
kg = None
llm = None

class SubGraphMessage(BaseMessage):
    """Custom message type for subgraph data"""
    content: Dict[str, Any]
    type: str = "subgraph"

    def __init__(self, content: Dict[str, Any], **kwargs):
        super().__init__(content=content, **kwargs)

def retrieve_from_graph(messages: List[BaseMessage]) -> SubGraphMessage:
    """Retrieve relevant subgraph from knowledge graph"""
    last_message = messages[-1]
    # Convert query to graph query
    subgraph = kg.query(last_message.content) if kg else {}
    return SubGraphMessage(content=subgraph)

def generate_response(messages: List[Union[BaseMessage, Dict]]) -> AIMessage:
    """Generate response using LLM with graph context"""
    # Find the last subgraph message
    subgraph = None
    for m in messages:
        if isinstance(m, SubGraphMessage) or (isinstance(m, dict) and m.get("type") == "subgraph"):
            subgraph = m
            break
    
    if not subgraph:
        return AIMessage(content="No graph context found")
    
    # Get the actual content
    graph_content = subgraph.content if hasattr(subgraph, 'content') else subgraph.get("content", {})
    
    # Get the last human message
    last_human_msg = next(
        (m for m in reversed(messages) if isinstance(m, HumanMessage) or (isinstance(m, dict) and m.get("type") in ("human", "user"))),
        None
    )
    
    if not last_human_msg:
        return AIMessage(content="No query found")
    
    query = last_human_msg.content if hasattr(last_human_msg, 'content') else last_human_msg.get("content", "")
    
    # Generate answer using subgraph context
    response = llm.generate(query, graph_context=graph_content) if llm else f"Mock response for: {query}"
    return AIMessage(content=response)

# Initialize the workflow
workflow = MessageGraph()
workflow.add_node("retrieve", retrieve_from_graph)
workflow.add_node("generate", generate_response)
workflow.add_edge("retrieve", "generate")
workflow.set_entry_point("retrieve")
workflow.set_finish_point("generate")

def run_workflow(query: str) -> AIMessage:
    """Helper function to run the complete workflow"""
    compiled = workflow.compile()
    result = compiled.invoke([HumanMessage(content=query)])
    # Extract the final AIMessage from the result
    if isinstance(result, list):
        for msg in reversed(result):
            if isinstance(msg, AIMessage):
                return msg
    return AIMessage(content="No valid response generated")