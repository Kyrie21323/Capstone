"""
Matching routes for Prophere.
Handles event matching, likes, passes, matches, and graph processing.

MEMORY OPTIMIZATIONS:
- Uses cached embeddings from Resume model to avoid recomputation
- Enforces MAX_MATCH_ATTENDEES limit to prevent OOM
- Processes matches in batches
- Avoids loading full document text into memory
"""
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, Event, Membership, Resume, UserInteraction, Match, ParticipantAvailability, Meeting, User
from . import matching_bp
import os
import json
import logging
import threading
import numpy as np

logger = logging.getLogger(__name__)

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
    # Debug: Confirm route is being called
    print(f"\n🔍 MATCHING ROUTE CALLED: /event/{event_id}", flush=True)
    print(f"   User: {current_user.name} (ID: {current_user.id}, Admin: {current_user.is_admin})", flush=True)
    
    # Prevent super admin from accessing matching
    if current_user.is_admin:
        print("   ❌ Blocked: User is admin", flush=True)
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
        print(f"   ⚠️ No other memberships found (reason: {no_matches_reason})", flush=True)
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
        print("   ⚠️ No available memberships (all already interacted)", flush=True)
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=[],
                             no_matches_reason='no_similar_interests')
    
    print(f"   ✅ Found {len(available_memberships)} available memberships", flush=True)
    
    # MEMORY OPTIMIZATION: Enforce MAX_MATCH_ATTENDEES limit to prevent OOM
    max_attendees = current_app.config.get('MAX_MATCH_ATTENDEES', 500)
    if len(available_memberships) > max_attendees:
        print(f"   ⚠️  Limiting matching to {max_attendees} attendees (found {len(available_memberships)})", flush=True)
        available_memberships = available_memberships[:max_attendees]
        flash(f'This event has many attendees. Showing matches from the first {max_attendees} participants.', 'info')
    
    # Import matching engine
    try:
        from matching_engine import matching_engine
        print("   ✅ Matching engine imported successfully", flush=True)
        
        # MEMORY OPTIMIZATION: Use cached extracted_text and embedding from Resume model
        # This avoids loading full document files and recomputing embeddings
        current_user_resume = Resume.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        current_user_doc_text = ""
        current_user_doc_embedding = None
        current_user_kw_embedding = None
        
        if current_user_resume:
            # Use cached text if available, otherwise extract (backward compatibility)
            if current_user_resume.extracted_text:
                current_user_doc_text = current_user_resume.extracted_text
                current_user_doc_embedding = current_user_resume.embedding
            else:
                # Fallback: extract on-the-fly (slower, but works for old resumes)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id), current_user_resume.filename)
                current_user_doc_text = matching_engine.extract_text_from_document(file_path)
                # Note: embedding not computed here to save memory - will be computed on-demand if needed
        
        # Compute keyword embedding for current user (small, so OK to compute)
        current_user_keywords = membership.get_keywords_list()
        if current_user_keywords:
            kw_text = ", ".join(current_user_keywords)
            kw_embedding = matching_engine.get_text_embedding(kw_text)
            current_user_kw_embedding = json.dumps(kw_embedding.tolist())
        
        current_user_data = {
            'user_id': current_user.id,
            'keywords': current_user_keywords,
            'document_text': current_user_doc_text,
            'cached_doc_embedding': current_user_doc_embedding,
            'cached_keyword_embedding': current_user_kw_embedding
        }
        
        # MEMORY OPTIMIZATION: Prepare user data using cached embeddings
        # Don't load full document text into memory - use cached embeddings instead
        all_users_data = []
        for mem in available_memberships:
            user = mem.user
            user_resume = Resume.query.filter_by(user_id=user.id, event_id=event_id).first()
            
            # Use cached data if available (memory optimization)
            user_doc_text = ""
            user_doc_embedding = None
            user_kw_embedding = None
            
            if user_resume:
                if user_resume.extracted_text:
                    # Use cached text and embedding (major memory savings)
                    user_doc_text = user_resume.extracted_text
                    user_doc_embedding = user_resume.embedding
                # Note: We don't load full document text if embedding exists
                # This saves significant memory for large documents
            
            # Compute keyword embedding (small, so OK)
            user_keywords = mem.get_keywords_list()
            if user_keywords:
                kw_text = ", ".join(user_keywords)
                kw_embedding = matching_engine.get_text_embedding(kw_text)
                user_kw_embedding = json.dumps(kw_embedding.tolist())
            
            user_data = {
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'keywords': user_keywords,
                'document_text': user_doc_text,  # May be empty if using cached embedding
                'cached_doc_embedding': user_doc_embedding,  # Used for matching
                'cached_keyword_embedding': user_kw_embedding,
                'has_resume': user_resume is not None,
                'resume_name': user_resume.original_name if user_resume else None,
                'joined_at': mem.joined_at.strftime('%B %Y') if mem.joined_at else 'Recently'
            }
            all_users_data.append(user_data)
        
        # MEMORY OPTIMIZATION: Use batch processing in find_best_matches
        # This processes users in chunks and only keeps top_k matches in memory
        best_matches = matching_engine.find_best_matches(
            current_user_data, 
            all_users_data, 
            top_k=20,
            batch_size=50  # Process 50 users at a time to limit peak memory
        )
        
        # Calculate scores for ALL users (for debugging) - but only if small enough
        # MEMORY OPTIMIZATION: Skip debug scoring for large events
        all_scores = []
        if len(all_users_data) <= 100:  # Only compute all scores for small events
            for user_data in all_users_data:
                score = matching_engine.calculate_match_score(current_user_data, user_data)
                all_scores.append((user_data, score))
            
            # Sort all scores by value (highest first)
            all_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Extract just the user data (without scores) for the template
        # MEMORY OPTIMIZATION: Remove cached embeddings from user_data before passing to template
        # (they're not needed in the frontend and take up memory)
        potential_matches = []
        for match_data, score in best_matches:
            # Create a clean copy without cached embeddings for template
            clean_data = {
                'user_id': match_data['user_id'],
                'name': match_data['name'],
                'email': match_data['email'],
                'keywords': match_data['keywords'],
                'has_resume': match_data['has_resume'],
                'resume_name': match_data['resume_name'],
                'joined_at': match_data['joined_at']
            }
            potential_matches.append(clean_data)
        
        # Debug: Print matching scores to terminal (with immediate flush)
        # MEMORY OPTIMIZATION: Only print debug info if we computed all scores
        if all_scores:
            MATCH_THRESHOLD = 0.26  # Matching threshold from matching_engine
            print(f"\n=== MATCHING SCORES DEBUG ===", flush=True)
            print(f"Current User: {current_user.name} (ID: {current_user.id})", flush=True)
            print(f"Event: {event.name}", flush=True)
            print(f"Session Filtering: {'Disabled (showing all)' if show_cross_session else 'Enabled (same-session only)'}", flush=True)
            print(f"User's Sessions: {list(user_session_ids)}", flush=True)
            print(f"Match Threshold: {MATCH_THRESHOLD:.4f} ({MATCH_THRESHOLD*100:.1f}%)", flush=True)
            print(f"Total users evaluated: {len(all_scores)}", flush=True)
            print(f"Matches above threshold: {len(best_matches)}", flush=True)
            print("-" * 50, flush=True)
            print("ALL USERS AND THEIR SCORES:", flush=True)
            print("-" * 50, flush=True)
            
            for i, (match_data, score) in enumerate(all_scores, 1):
                threshold_indicator = "✅" if score > MATCH_THRESHOLD else "❌"
                print(f"{i:2d}. {threshold_indicator} {match_data['name']:<20} Score: {score:.4f} ({score*100:.1f}%)", flush=True)
            
            print("-" * 50, flush=True)
            print(f"MATCHES ABOVE THRESHOLD ({MATCH_THRESHOLD*100:.1f}%):", flush=True)
            print("-" * 50, flush=True)
            
            if best_matches:
                for i, (match_data, score) in enumerate(best_matches, 1):
                    print(f"{i:2d}. {match_data['name']:<20} Score: {score:.4f} ({score*100:.1f}%)", flush=True)
            else:
                print("  No matches above threshold.", flush=True)
            
            print("=" * 50, flush=True)
        else:
            # For large events, just print summary
            print(f"   ✅ Found {len(best_matches)} matches above threshold (event too large for full debug output)", flush=True)
        
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
        print(f"   ❌ ImportError: {str(e)}", flush=True)
        print("   ⚠️ Falling back to simple matching (no scores)", flush=True)
        
        # MEMORY OPTIMIZATION: Limit fallback matching too
        max_attendees = current_app.config.get('MAX_MATCH_ATTENDEES', 500)
        if len(available_memberships) > max_attendees:
            available_memberships = available_memberships[:max_attendees]
        
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

                success = False
                message = ""
                meeting = None
                event = Event.query.get(event_id)

                # Try to auto-assign meeting (before commit)
                try:
                    from utils.auto_assign import auto_assign_meeting
                    success, message, meeting = auto_assign_meeting(
                        match.id,
                        user1_id,
                        user2_id,
                        event_id,
                        event
                    )
                    if success:
                        logger.info("Auto-assigned meeting for match %s: %s", match.id, message)
                    else:
                        match.assignment_attempted = True
                        match.assignment_failed_reason = message
                except Exception as e:
                    logger.exception("Error during auto-assignment: %s", e)
                    match.assignment_attempted = True
                    match.assignment_failed_reason = f"System error: {str(e)}"

                # Commit first so emails are only sent after match is persisted
                db.session.commit()

                # Trigger idempotent email handler in background (sends only if email_sent_at is None)
                match_id = match.id
                app = current_app._get_current_object()
                print("🚀 Starting email thread for match %s" % match_id)

                def run_handle_match_created():
                    with app.app_context():
                        try:
                            from services.email_service import handle_match_created
                            handle_match_created(match_id)
                        except Exception as e:
                            print("❌ handle_match_created failed for match_id=%s: %s" % (match_id, e))
                            logger.exception("handle_match_created failed for match_id=%s: %s", match_id, e)

                t = threading.Thread(target=run_handle_match_created, daemon=True)
                t.start()
                
                # Prepare detailed response with assignment status
                other_user = User.query.get(user2_id if current_user.id == user1_id else user1_id)
                
                response_data = {
                    'success': True,
                    'message': 'It\'s a match!',
                    'is_match': True,
                    'match_id': match.id,
                    'match_name': other_user.name,
                    'event_name': event.name,
                    'event_id': event_id,
                    'assignment_status': 'success' if success else 'failed',
                    'assignment_message': message
                }
                
                if success and meeting:
                    # Include meeting details
                    response_data['meeting'] = {
                        'id': meeting.id,
                        'start_time': meeting.start_time.strftime('%A, %B %d at %I:%M %p'),
                        'end_time': meeting.end_time.strftime('%I:%M %p'),
                        'location': meeting.location.name,
                        'session_name': meeting.session.name if meeting.session else 'TBA'
                    }
                else:
                    # No meeting assigned
                    response_data['meeting'] = None
                    response_data['failure_reason'] = match.assignment_failed_reason or "Unknown reason"
                
                return response_data, 200
        
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

@matching_bp.route('/<int:event_id>/match/<int:match_id>/assignment-status', methods=['GET'])
@login_required
def get_match_assignment_status(event_id, match_id):
    """Get the current assignment status for a match"""
    try:
        # Get the match
        match = Match.query.get(match_id)
        
        if not match:
            return {'success': False, 'message': 'Match not found'}, 404
        
        # Verify user is part of this match
        if match.user1_id != current_user.id and match.user2_id != current_user.id:
            return {'success': False, 'message': 'Unauthorized'}, 403
        
        # Verify match belongs to this event
        if match.event_id != event_id:
            return {'success': False, 'message': 'Match does not belong to this event'}, 400
        
        # Check if assignment was attempted
        if not match.assignment_attempted:
            return {
                'success': True,
                'status': 'pending',
                'message': 'Assignment in progress...'
            }, 200
        
        # Get meeting if assigned
        meeting = Meeting.query.filter_by(match_id=match_id).first()
        
        if meeting:
            # Successfully assigned
            return {
                'success': True,
                'status': 'assigned',
                'message': 'Meeting assigned successfully',
                'meeting': {
                    'id': meeting.id,
                    'start_time': meeting.start_time.strftime('%A, %B %d at %I:%M %p'),
                    'end_time': meeting.end_time.strftime('%I:%M %p'),
                    'location': meeting.location.name,
                    'session_name': meeting.session.name if meeting.session else 'TBA'
                }
            }, 200
        else:
            # Assignment failed
            return {
                'success': True,
                'status': 'failed',
                'message': 'Could not assign meeting',
                'failure_reason': match.assignment_failed_reason or 'Unknown reason'
            }, 200
            
    except Exception as e:
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
    
    # Prepare match data for template with meeting information
    match_data = []
    for match in matches:
        other_user = match.get_other_user(current_user.id)
        if other_user:
            # Get ACTIVE meeting for this match (exclude cancelled)
            meeting = Meeting.query.filter_by(
                match_id=match.id,
                status='scheduled'
            ).first()
            
            match_info = {
                'match': match,
                'other_user': other_user,
                'matched_at': match.matched_at,
                'has_meeting': meeting is not None,
                'assignment_attempted': match.assignment_attempted
            }
            
            if meeting:
                # Include meeting details
                match_info['meeting'] = {
                    'start_time': meeting.start_time,
                    'end_time': meeting.end_time,
                    'location': meeting.location.name,
                    'session_name': meeting.session.name if meeting.session else 'TBA',
                    'status': meeting.status
                }
            elif match.assignment_attempted:
                # Assignment was attempted but failed
                match_info['assignment_failed'] = True
                match_info['failure_reason'] = match.assignment_failed_reason or 'Unknown reason'
            else:
                # Assignment pending
                match_info['assignment_pending'] = True
            
            match_data.append(match_info)
    
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
