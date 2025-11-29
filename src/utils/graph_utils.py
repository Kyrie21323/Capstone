"""
Graph utility functions for building network visualizations.

This module provides functions to convert database relationships
into graph structures suitable for visualization.
"""

from typing import Dict, List

from models import User, Match


def build_event_graph(event_id: int) -> Dict[str, List[dict]]:
    """
    Build a simple graph representation for a given event.

    Nodes:
        - one per User who is part of this event AND participates in at least one Match for this event
        - format: {"id": user.id, "label": user.name}

    Edges:
        - one per Match row for this event (only active matches)
        - format: {"source": user1_id, "target": user2_id}

    This function returns a dict:
        {
            "nodes": [...],
            "edges": [...]
        }
    that will be JSON-serializable and consumed by the frontend later.

    Args:
        event_id: The ID of the event to build the graph for

    Returns:
        A dictionary with "nodes" and "edges" keys, each containing a list of dictionaries.
        Returns empty lists if no matches exist for the event.

    Note:
        This function is read-only and does not modify the database.
    """
    # Query all active Match records for this event
    matches = Match.query.filter_by(
        event_id=event_id,
        is_active=True
    ).all()

    if not matches:
        # Return empty graph if no matches exist
        return {
            "nodes": [],
            "edges": []
        }

    # Collect all unique user IDs that appear in matches
    user_ids = set()
    edges = []
    seen_edges = set()  # Track edges to prevent duplicates

    for match in matches:
        # Add both users to the set
        user_ids.add(match.user1_id)
        user_ids.add(match.user2_id)

        # Create edge tuple (normalized: always smaller ID first) to prevent duplicates
        edge_tuple = tuple(sorted([match.user1_id, match.user2_id]))
        if edge_tuple not in seen_edges:
            seen_edges.add(edge_tuple)
            edges.append({
                "source": match.user1_id,
                "target": match.user2_id
            })

    # Query all User records for the collected user IDs
    users = User.query.filter(User.id.in_(user_ids)).all()

    # Build nodes list (ensure no duplicates)
    nodes = []
    seen_node_ids = set()
    for user in users:
        if user.id not in seen_node_ids:
            seen_node_ids.add(user.id)
            nodes.append({
                "id": user.id,
                "label": user.name
            })

    return {
        "nodes": nodes,
        "edges": edges
    }

