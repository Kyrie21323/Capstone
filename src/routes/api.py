"""
API routes for Prophere.
Handles JSON endpoints for graph data.
"""
from flask import jsonify
from flask_login import login_required, current_user
from models import Event
from utils.graph_utils import build_event_graph
from utils.sample_graph_data import generate_small_graph, generate_medium_graph, generate_large_graph
from . import api_bp

@api_bp.route('/event/<int:event_id>/graph', methods=['GET'])
@login_required
def api_event_graph(event_id):
    """Return graph data for a given event as JSON"""
    # Check if event exists
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Only allow super admins (event organizers) to access graph data
    if not current_user.is_admin:
        return jsonify({'error': 'You must be an event organizer to access graph data'}), 403
    
    # Build and return graph data
    try:
        graph_data = build_event_graph(event_id)
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dev/graph/<size>', methods=['GET'])
@login_required
def api_dev_graph(size):
    """
    Returns synthetic graph data for stress testing the Event Graph Visualizer.
    Accessible only by admins.
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    if size == 'small':
        data = generate_small_graph()
    elif size == 'medium':
        data = generate_medium_graph()
    elif size == 'large':
        data = generate_large_graph()
    else:
        return jsonify({'error': 'Invalid dataset size. Use: small, medium, or large'}), 400
    
    return jsonify(data)
