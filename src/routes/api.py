"""
API routes for Prophere.
Handles JSON endpoints for graph data.
"""
from flask import jsonify, current_app
from flask_login import login_required, current_user
from models import Event
from utils.graph_utils import build_event_graph
from utils.sample_graph_data import generate_small_graph, generate_medium_graph, generate_large_graph
from . import api_bp

DEV_GRAPH_GENERATORS = {
    'small': generate_small_graph,
    'medium': generate_medium_graph,
    'large': generate_large_graph,
}

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
    """Return synthetic graph data for admin stress-testing of the visualizer."""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    generator = DEV_GRAPH_GENERATORS.get(size)
    if generator is None:
        allowed_sizes = ', '.join(DEV_GRAPH_GENERATORS.keys())
        return jsonify({'error': f'Invalid dataset size. Use: {allowed_sizes}'}), 400

    try:
        data = generator()
    except Exception as exc:  # pragma: no cover - safety net for unexpected failures
        current_app.logger.exception('Failed to generate %s dev graph dataset', size)
        return jsonify({'error': 'Failed to generate synthetic graph data. Please try again.'}), 500

    return jsonify(data)
