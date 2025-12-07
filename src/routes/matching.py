"""
Matching routes for Prophere.
Handles event matching, likes, passes, matches, and graph processing.
"""
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, Event, Membership, Resume, UserInteraction, Match, ParticipantAvailability
from . import matching_bp
import os

@matching_bp.route('/<int:event_id>/loading')
@login_required
def matching_loading(event_id):
    """Show loading page while calculating matches"""
    # Prevent super admin from accessing matching
    if current_user.is_admin:
        flash('Super admin accounts cannot access matching!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Get the event
    event = Event.query.get(event_id)
    
    if not event:
        flash('Event not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Check if user is a member of this event
    membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('user.dashboard'))
    
    return render_template('matching_loading.html', event=event, event_id=event_id)

@matching_bp.route('/<int:event_id>')
@login_required
def event_matching(event_id):
    # Prevent super admin from accessing matching
    if current_user.is_admin:
        flash('Super admin accounts cannot access matching!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Get the event
    event = Event.query.get(event_id)
    
    if not event:
        flash('Event not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Check if user is a member of this event
    membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Get all other users who are members of this event (excluding current user)
    other_memberships = Membership.query.filter(
        Membership.event_id == event_id,
        Membership.user_id != current_user.id
    ).all()
    
    # Check if user wants to see cross-session matches
    show_cross_session = request.args.get('cross_session', 'false').lower() == 'true'
    
    # Get current user's session availability
    user_sessions = ParticipantAvailability.query.filter_by(
        user_id=current_user.id,
        event_id=event_id,
        is_available=True
    ).all()
    user_session_ids = {avail.session_id for avail in user_sessions}
    
    # Filter by shared sessions unless cross_session is enabled
    if not show_cross_session and user_session_ids:
        # Get users who share at least one session with current user
        shared_session_user_ids = set()
        shared_availabilities = ParticipantAvailability.query.filter(
            ParticipantAvailability.event_id == event_id,
            ParticipantAvailability.session_id.in_(user_session_ids),
            ParticipantAvailability.is_available == True,
            ParticipantAvailability.user_id != current_user.id
        ).all()
        
        for avail in shared_availabilities:
            shared_session_user_ids.add(avail.user_id)
        
        # Filter memberships to only shared session users
        other_memberships = [mem for mem in other_memberships if mem.user_id in shared_session_user_ids]
    
    if not other_memberships:
        # No other members to match with
        no_matches_reason = 'no_shared_sessions' if not show_cross_session else 'no_attendees'
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=[],
                             no_matches_reason=no_matches_reason,
                             show_cross_session=show_cross_session)
    
    # Filter out users that current user has already interacted with
    interacted_user_ids = set()
    interactions = UserInteraction.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).all()
    for interaction in interactions:
        interacted_user_ids.add(interaction.target_user_id)
    
    # Remove already interacted users from potential matches
    available_memberships = [mem for mem in other_memberships if mem.user_id not in interacted_user_ids]
    
    if not available_memberships:
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=[],
                             no_matches_reason='no_similar_interests')
    
    # Import matching engine
    try:
        from matching_engine import matching_engine
        
        # Prepare current user data for matching
        current_user_resume = Resume.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        current_user_doc_text = ""
        
        if current_user_resume:
            # Extract text from current user's document
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id), current_user_resume.filename)
            current_user_doc_text = matching_engine.extract_text_from_document(file_path)
        
        current_user_data = {
            'user_id': current_user.id,
            'keywords': membership.get_keywords_list(),
            'document_text': current_user_doc_text
        }
        
        # Prepare all other users data for matching
        all_users_data = []
        for mem in available_memberships:
            user = mem.user
            user_resume = Resume.query.filter_by(user_id=user.id, event_id=event_id).first()
            user_doc_text = ""
            
            if user_resume:
                # Extract text from user's document
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user.id), user_resume.filename)
                user_doc_text = matching_engine.extract_text_from_document(file_path)
            
            user_data = {
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'keywords': mem.get_keywords_list(),
                'document_text': user_doc_text,
                'has_resume': user_resume is not None,
                'resume_name': user_resume.original_name if user_resume else None,
                'joined_at': mem.joined_at.strftime('%B %Y') if mem.joined_at else 'Recently'
            }
            all_users_data.append(user_data)
        
        # Find best matches using intelligent algorithm
        best_matches = matching_engine.find_best_matches(current_user_data, all_users_data, top_k=20)
        
        # Extract just the user data (without scores) for the template
        potential_matches = [match_data for match_data, score in best_matches]
        
        # Debug: Print matching scores to terminal
        print(f"\n=== MATCHING SCORES DEBUG ===")
        print(f"Current User: {current_user.name} (ID: {current_user.id})")
        print(f"Event: {event.name}")
        print(f"Session Filtering: {'Disabled (showing all)' if show_cross_session else 'Enabled (same-session only)'}")
        print(f"User's Sessions: {list(user_session_ids)}")
        print(f"Total potential matches: {len(best_matches)}")
        print("-" * 50)
        
        for i, (match_data, score) in enumerate(best_matches, 1):
            print(f"{i:2d}. {match_data['name']:<20} Score: {score:.4f} ({score*100:.1f}%)")
        
        print("=" * 50)
        
        # Determine the reason for no matches
        no_matches_reason = None
        if len(potential_matches) == 0:
            no_matches_reason = 'no_similar_interests'
        
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=potential_matches,
                             no_matches_reason=no_matches_reason,
                             show_cross_session=show_cross_session)
        
    except ImportError as e:
        # Fallback to simple matching if engine fails
        potential_matches = []
        for mem in available_memberships:
            user = mem.user
            user_resume = Resume.query.filter_by(user_id=user.id, event_id=event_id).first()
            
            match_data = {
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'keywords': mem.get_keywords_list(),
                'has_resume': user_resume is not None,
                'resume_name': user_resume.original_name if user_resume else None,
                'joined_at': mem.joined_at.strftime('%B %Y') if mem.joined_at else 'Recently'
            }
            potential_matches.append(match_data)
    
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=potential_matches,
                             no_matches_reason=None,
                             show_cross_session=show_cross_session)

@matching_bp.route('/<int:event_id>/like/<int:target_user_id>', methods=['POST'])
@login_required
def like_user(event_id, target_user_id):
    """Handle when a user likes another user"""
    # Prevent super admin from liking users
    if current_user.is_admin:
        return {'success': False, 'message': 'Super admin accounts cannot like users'}, 403
    
    try:
        # Verify the user is a member of this event
        membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if not membership:
            return {'success': False, 'message': 'You are not a member of this event'}, 403
        
        # Check if target user is also a member
        target_membership = Membership.query.filter_by(user_id=target_user_id, event_id=event_id).first()
        if not target_membership:
            return {'success': False, 'message': 'Target user is not a member of this event'}, 404
        
        # Check if interaction already exists
        existing_interaction = UserInteraction.query.filter_by(
            user_id=current_user.id,
            target_user_id=target_user_id,
            event_id=event_id
        ).first()
        
        if existing_interaction:
            return {'success': False, 'message': 'You have already interacted with this user'}, 400
        
        # Create new interaction
        interaction = UserInteraction(
            user_id=current_user.id,
            target_user_id=target_user_id,
            event_id=event_id,
            action='like'
        )
        db.session.add(interaction)
        
        # Check if this creates a mutual match
        mutual_like = UserInteraction.query.filter_by(
            user_id=target_user_id,
            target_user_id=current_user.id,
            event_id=event_id,
            action='like'
        ).first()
        
        if mutual_like:
            # It's a match! Create match record
            # Ensure consistent ordering (lower user_id first)
            user1_id = min(current_user.id, target_user_id)
            user2_id = max(current_user.id, target_user_id)
            
            # Check if match already exists
            existing_match = Match.query.filter_by(
                user1_id=user1_id,
                user2_id=user2_id,
                event_id=event_id
            ).first()
            
            if not existing_match:
                match = Match(
                    user1_id=user1_id,
                    user2_id=user2_id,
                    event_id=event_id
                )
                db.session.add(match)
                db.session.flush()  # Get the match ID
                
                # Try to auto-assign meeting
                try:
                    from utils.auto_assign import auto_assign_meeting
                    event = Event.query.get(event_id)
                    
                    success, message, meeting = auto_assign_meeting(
                        match.id,
                        user1_id,
                        user2_id,
                        event_id,
                        event
                    )
                    
                    if success:
                        print(f"✅ Auto-assigned meeting for match {match.id}: {message}")
                        print(f"   Meeting: {meeting.start_time} at {meeting.location.name}")
                    else:
                        print(f"⚠️ Could not auto-assign meeting for match {match.id}: {message}")
                        match.assignment_attempted = True
                        match.assignment_failed_reason = message
                        
                except Exception as e:
                    print(f"❌ Error during auto-assignment: {str(e)}")
                    match.assignment_attempted = True
                    match.assignment_failed_reason = f"System error: {str(e)}"
                
                db.session.commit()
                
                return {
                    'success': True,
                    'message': 'It\'s a match!',
                    'is_match': True,
                    'match_id': match.id
                }, 200
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Like recorded',
            'is_match': False
        }, 200
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500

@matching_bp.route('/<int:event_id>/pass/<int:target_user_id>', methods=['POST'])
@login_required
def pass_user(event_id, target_user_id):
    """Handle when a user passes on another user"""
    # Prevent super admin from passing on users
    if current_user.is_admin:
        return {'success': False, 'message': 'Super admin accounts cannot pass on users'}, 403
    
    try:
        # Verify the user is a member of this event
        membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if not membership:
            return {'success': False, 'message': 'You are not a member of this event'}, 403
        
        # Check if interaction already exists
        existing_interaction = UserInteraction.query.filter_by(
            user_id=current_user.id,
            target_user_id=target_user_id,
            event_id=event_id
        ).first()
        
        if existing_interaction:
            return {'success': False, 'message': 'You have already interacted with this user'}, 400
        
        # Create new interaction
        interaction = UserInteraction(
            user_id=current_user.id,
            target_user_id=target_user_id,
            event_id=event_id,
            action='pass'
        )
        db.session.add(interaction)
        db.session.commit()
        
        return {'success': True, 'message': 'Pass recorded'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500

@matching_bp.route('/<int:event_id>/matches')
@login_required
def event_matches(event_id):
    """Show all matches for a user in an event"""
    # Prevent super admin from accessing matches
    if current_user.is_admin:
        flash('Super admin accounts cannot access matches!', 'error')
        return redirect(url_for('user.dashboard'))
    
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Get all matches for this user in this event
    matches = Match.query.filter(
        db.or_(
            db.and_(Match.user1_id == current_user.id, Match.event_id == event_id),
            db.and_(Match.user2_id == current_user.id, Match.event_id == event_id)
        ),
        Match.is_active == True
    ).all()
    
    # Prepare match data for template
    match_data = []
    for match in matches:
        other_user = match.get_other_user(current_user.id)
        if other_user:
            match_data.append({
                'match': match,
                'other_user': other_user,
                'matched_at': match.matched_at
            })
    
    return render_template('event_matches.html', 
                         event=event, 
                         matches=match_data)

@matching_bp.route('/<int:event_id>/graph', methods=['GET'])
@login_required
def event_graph_page(event_id):
    """Display the network graph visualization for a given event"""
    # Check if event exists
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Only allow super admins (event organizers) to view the graph
    if not current_user.is_admin:
        flash('You must be an event organizer to view the event network graph.', 'error')
        return redirect(url_for('user.dashboard'))
    
    return render_template('event_graph.html', event_id=event_id, event=event)
