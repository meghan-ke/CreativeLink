from flask import Blueprint, render_template, session, redirect, url_for, request
from app import db
from app.models import YoungArtist, User, Application, Video, Opportunity, Message

artists_bp = Blueprint('artists', __name__)

@artists_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    print("USER ID:", session.get('user_id'))
    print("ROLE:", session.get('role'))

    artist = YoungArtist.query.filter_by(user_id=session['user_id']).first()

    active_applications = Application.query.filter_by(
        young_artist_id=artist.id, 
        status='submitted'
    ).count()

    video_count = Video.query.filter_by(
        young_artist_id=artist.id
    ).count()

    unread_messages = Message.query.filter_by(
        receiver_id=session['user_id']
    ).count()

    opportunities = Opportunity.query.filter_by(
        status='open'
    ).order_by(Opportunity.deadline.asc()).limit(3).all()

    new_opportunities = Opportunity.query.filter_by(status='open').count()

    return render_template('artist_dashboard.html',
                           artist=artist,
                           active_applications=active_applications,
                           video_count=video_count,
                           unread_messages=unread_messages,
                           opportunities=opportunities,
                           new_opportunities=new_opportunities
    )

@artists_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    artist = YoungArtist.query.filter_by(user_id=session['user_id']).first()
    user = User.query.get(session['user_id'])
    return render_template('artist_profile.html', artist=artist, user=user)


@artists_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    artist = YoungArtist.query.filter_by(user_id=session['user_id']).first()

    if request.method == 'POST':
        artist.name = request.form.get('name')
        artist.age = int(request.form.get('age'))
        artist.location = request.form.get('location')
        artist.art_form = request.form.get('art_form')
        db.session.commit()
        return redirect(url_for('artists.profile'))
    return render_template('artist_profile.html', artist=artist, edit=True)
