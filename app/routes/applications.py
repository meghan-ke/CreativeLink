from flask import Blueprint, render_template, session, redirect, url_for
from app import db
from app.models import Application, YoungArtist, Opportunity

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/apply/<opportunity_id>', methods=['POST'])
def apply(opportunity_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    artist = YoungArtist.query.filter_by(user_id=session['user_id']).first()

    #enforce 10-applicants limit
    active_count = Application.query.filter_by(
        young_artist_id=artist.id,
        status='submitted'
    ).count()

    if active_count >= 10:
        return redirect(url_for('opportunities.browse') + '?error=duplicate')

    new_application = Application(
        young_artist_id=artist.id,
        opportunity_id=opportunity_id,
        status='submitted'
    )
    db.session.add(new_application)
    db.session.commit()

    return redirect(url_for('applications.my_applications'))

@applications_bp.route('/my-applications')
def my_applications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    artist = YoungArtist.query.filter_by(user_id=session['user_id']).first()
    applications = Application.query.filter_by(
        young_artist_id=artist.id
    ).all()

    return render_template('my_applications.html', applications=applications)

@applications_bp.route('/withdraw/<application_id>')
def withdraw(application_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    application = Application.query.get_or_404(application_id)
    application.status = 'withdrawn'
    db.session.commit()

    return redirect(url_for('applications.my_applications'))

   