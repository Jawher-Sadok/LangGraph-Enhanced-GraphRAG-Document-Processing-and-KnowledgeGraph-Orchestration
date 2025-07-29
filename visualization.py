# visualization.py
from pyvis.network import Network
import os
import tempfile

def visualize_knowledge_graph(graph, output_file=None):
    """
    Visualize a knowledge graph using PyVis
    
    Args:
        graph: A NetworkX graph
        output_file: Path to save the HTML file. If None, uses a temp file.
    
    Returns:
        Path to the generated HTML file
    """
    # Initialize network
    net = Network(
        height="750px",
        width="100%",
        notebook=False,
        directed=graph.is_directed(),
        cdn_resources='remote'
    )
    
    # Add nodes and edges
    for node in graph.nodes(data=True):
        net.add_node(node[0], **node[1])
    for edge in graph.edges(data=True):
        net.add_edge(edge[0], edge[1], **edge[2])
    
    # Set output path
    if output_file is None:
        output_file = os.path.join(tempfile.gettempdir(), "knowledge_graph.html")
    
    # Generate HTML
    try:
        net.show(output_file)
    except Exception as e:
        # Fallback for template issues
        html = net.generate_html()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
    
    return output_file