"""
Synthetic graph data generator for stress testing the Event Graph Visualizer.

This module provides functions to generate sample graph data in the same format
as the graph_utils.build_event_graph() function returns.
"""


def generate_small_graph():
    """
    Generate a small graph with ~20 nodes.
    
    Topology:
    - Dense cluster (nodes 1-8, nearly fully connected)
    - Star pattern (node 9 connected to nodes 10-14)
    - Isolated nodes (nodes 15-20)
    
    Returns:
        dict: {"nodes": [...], "edges": [...]}
    """
    nodes = []
    edges = []
    
    # Create 20 nodes
    for i in range(1, 21):
        nodes.append({"id": i, "label": f"User {i}"})
    
    # Dense cluster: nodes 1-8 (nearly fully connected)
    for i in range(1, 9):
        for j in range(i + 1, 9):
            edges.append({"source": i, "target": j})
    
    # Star pattern: node 9 connected to nodes 10-14
    for i in range(10, 15):
        edges.append({"source": 9, "target": i})
    
    # Connect star to cluster (node 9 to node 1)
    edges.append({"source": 1, "target": 9})
    
    # Nodes 15-20 remain isolated
    
    return {"nodes": nodes, "edges": edges}


def generate_medium_graph():
    """
    Generate a medium graph with ~100 nodes.
    
    Topology:
    - Cluster 1: nodes 1-25 (dense, fully connected)
    - Cluster 2: nodes 26-50 (dense, fully connected)
    - Cluster 3: nodes 51-70 (sparse, chain + some connections)
    - Cluster 4: nodes 71-85 (sparse, tree-like)
    - Cross-cluster links between clusters
    - Isolated nodes: 86-100
    
    Returns:
        dict: {"nodes": [...], "edges": [...]}
    """
    nodes = []
    edges = []
    
    # Create 100 nodes
    for i in range(1, 101):
        nodes.append({"id": i, "label": f"User {i}"})
    
    # Cluster 1: nodes 1-25 (dense, fully connected)
    for i in range(1, 26):
        for j in range(i + 1, 26):
            edges.append({"source": i, "target": j})
    
    # Cluster 2: nodes 26-50 (dense, fully connected)
    for i in range(26, 51):
        for j in range(i + 1, 51):
            edges.append({"source": i, "target": j})
    
    # Cluster 3: nodes 51-70 (sparse, chain + some connections)
    # Create a chain
    for i in range(51, 70):
        edges.append({"source": i, "target": i + 1})
    # Add some cross-connections in the chain
    edges.append({"source": 51, "target": 60})
    edges.append({"source": 55, "target": 65})
    edges.append({"source": 52, "target": 68})
    
    # Cluster 4: nodes 71-85 (sparse, tree-like)
    # Create a tree structure
    edges.append({"source": 71, "target": 72})
    edges.append({"source": 71, "target": 73})
    edges.append({"source": 71, "target": 74})
    edges.append({"source": 72, "target": 75})
    edges.append({"source": 72, "target": 76})
    edges.append({"source": 73, "target": 77})
    edges.append({"source": 73, "target": 78})
    edges.append({"source": 74, "target": 79})
    edges.append({"source": 75, "target": 80})
    edges.append({"source": 76, "target": 81})
    edges.append({"source": 77, "target": 82})
    edges.append({"source": 78, "target": 83})
    edges.append({"source": 79, "target": 84})
    edges.append({"source": 80, "target": 85})
    
    # Cross-cluster links
    edges.append({"source": 1, "target": 26})   # Cluster 1 to Cluster 2
    edges.append({"source": 5, "target": 30})   # Cluster 1 to Cluster 2
    edges.append({"source": 25, "target": 51})   # Cluster 1 to Cluster 3
    edges.append({"source": 50, "target": 55})  # Cluster 2 to Cluster 3
    edges.append({"source": 30, "target": 71})  # Cluster 2 to Cluster 4
    edges.append({"source": 60, "target": 75})   # Cluster 3 to Cluster 4
    
    # Nodes 86-100 remain isolated
    
    return {"nodes": nodes, "edges": edges}


def generate_large_graph():
    """
    Generate a large graph with ~300 nodes.
    
    Topology:
    - Cluster 1: nodes 1-50 (dense, fully connected)
    - Cluster 2: nodes 51-100 (dense, fully connected)
    - Cluster 3: nodes 101-150 (medium density)
    - Cluster 4: nodes 151-200 (medium density)
    - Cluster 5: nodes 201-250 (sparse)
    - Cluster 6: nodes 251-290 (sparse)
    - Hub nodes: nodes 1, 51, 101 with many cross-cluster connections
    - Isolated nodes: 291-300
    
    Returns:
        dict: {"nodes": [...], "edges": [...]}
    """
    nodes = []
    edges = []
    
    # Create 300 nodes
    for i in range(1, 301):
        nodes.append({"id": i, "label": f"User {i}"})
    
    # Cluster 1: nodes 1-50 (dense, fully connected)
    for i in range(1, 51):
        for j in range(i + 1, 51):
            edges.append({"source": i, "target": j})
    
    # Cluster 2: nodes 51-100 (dense, fully connected)
    for i in range(51, 101):
        for j in range(i + 1, 101):
            edges.append({"source": i, "target": j})
    
    # Cluster 3: nodes 101-150 (medium density, ~60% connectivity)
    # Create a pattern: each node connects to next 5 nodes
    for i in range(101, 151):
        for j in range(i + 1, min(i + 6, 151)):
            edges.append({"source": i, "target": j})
        # Add some longer-range connections
        if i % 5 == 0:
            edges.append({"source": i, "target": min(i + 10, 150)})
    
    # Cluster 4: nodes 151-200 (medium density, similar pattern)
    for i in range(151, 201):
        for j in range(i + 1, min(i + 6, 201)):
            edges.append({"source": i, "target": j})
        if i % 5 == 0:
            edges.append({"source": i, "target": min(i + 10, 200)})
    
    # Cluster 5: nodes 201-250 (sparse, chain with branches)
    # Main chain
    for i in range(201, 250):
        edges.append({"source": i, "target": i + 1})
    # Add branches every 10 nodes
    for i in range(210, 250, 10):
        edges.append({"source": i, "target": i + 5})
        edges.append({"source": i, "target": i + 8})
    
    # Cluster 6: nodes 251-290 (sparse, tree-like)
    # Create a tree structure
    edges.append({"source": 251, "target": 252})
    edges.append({"source": 251, "target": 253})
    edges.append({"source": 251, "target": 254})
    for base in range(252, 270, 3):
        edges.append({"source": base, "target": base + 10})
        edges.append({"source": base, "target": base + 11})
        edges.append({"source": base, "target": base + 12})
    # Connect some leaves
    for i in range(270, 291):
        edges.append({"source": i, "target": min(i + 1, 290)})
    
    # Hub nodes with cross-cluster connections
    # Hub 1 (node 1) connects to other clusters
    edges.append({"source": 1, "target": 51})   # To Cluster 2
    edges.append({"source": 1, "target": 101})  # To Cluster 3
    edges.append({"source": 1, "target": 151})  # To Cluster 4
    edges.append({"source": 1, "target": 201})   # To Cluster 5
    edges.append({"source": 1, "target": 251})  # To Cluster 6
    
    # Hub 2 (node 51) connects to other clusters
    edges.append({"source": 51, "target": 101}) # To Cluster 3
    edges.append({"source": 51, "target": 151})  # To Cluster 4
    edges.append({"source": 51, "target": 201})  # To Cluster 5
    edges.append({"source": 51, "target": 251})  # To Cluster 6
    
    # Hub 3 (node 101) connects to other clusters
    edges.append({"source": 101, "target": 151}) # To Cluster 4
    edges.append({"source": 101, "target": 201}) # To Cluster 5
    edges.append({"source": 101, "target": 251}) # To Cluster 6
    
    # Additional cross-cluster links
    edges.append({"source": 25, "target": 75})   # Cluster 1 to Cluster 2
    edges.append({"source": 50, "target": 125})  # Cluster 1 to Cluster 3
    edges.append({"source": 100, "target": 175}) # Cluster 2 to Cluster 4
    edges.append({"source": 150, "target": 225}) # Cluster 3 to Cluster 5
    edges.append({"source": 200, "target": 260}) # Cluster 4 to Cluster 6
    
    # Nodes 291-300 remain isolated
    
    return {"nodes": nodes, "edges": edges}

