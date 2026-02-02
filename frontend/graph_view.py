import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

def render_graph(nodes, edges, config=None):
    """
    Renders an interactive graph using streamlit-agraph.
    """
    ag_nodes = []
    ag_edges = []
    
    # Convert dicts/objects to agraph Nodes
    for n in nodes:
        # Check if n is dict or object (depending on where it comes from)
        nid = n.get('id') if isinstance(n, dict) else (n.element_id if hasattr(n, 'element_id') else str(n))
        label = n.get('name') if isinstance(n, dict) else (n['name'] if hasattr(n, '__getitem__') else str(n))
        group = n.get('labels', ['Node'])[0] if isinstance(n, dict) and 'labels' in n else "Node"
        
        ag_nodes.append(Node(id=nid, label=label, size=25, group=group))

    for e in edges:
        source = e.get('from')
        target = e.get('to')
        label = e.get('type')
        ag_edges.append(Edge(source=source, target=target, label=label))

    if not config:
        config = Config(width=700, 
                        height=500, 
                        directed=True,
                        nodeHighlightBehavior=True, 
                        highlightColor="#F7A7A6", 
                        collapsible=False)

    return agraph(nodes=ag_nodes, edges=ag_edges, config=config)
