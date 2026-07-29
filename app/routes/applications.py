from flask import Blueprint, render_template, session, redirect, url_for, request
from app import db
from app.models import Application, YoungArtist, Opportunity, Video
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/apply/<opportunity_id>', methods=['GET', 'POST'])
def apply(opportunity_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    artist = YoungArtist.query.filter_by(user_id=session['user_id']).first()
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    videos = Video.query.filter_by(young_artist_id=artist.id).all()

    if request.method == 'POST':
        active_count = Application.query.filter_by(
            young_artist_id=artist.id,
            status='pending'
        ).count()

        if active_count >= 10:
            return redirect(url_for('opportunities.browse') + '?error=duplicate')

        showcase_video_id = request.form.get('showcase_video_id') or None
        uploaded_video = request.files.get('showcase_video')

        if uploaded_video and uploaded_video.filename:
            upload_result = cloudinary.uploader.upload(
                uploaded_video,
                resource_type='video',
                folder='creativelink/videos'
            )

            new_video = Video(
                young_artist_id=artist.id,
                title=request.form.get('showcase_video_title') or uploaded_video.filename,
                art_form=artist.art_form or 'Performance',
                video_url=upload_result['secure_url'],
                status='active'
            )
            db.session.add(new_video)
            db.session.flush()
            showcase_video_id = new_video.id

        new_application = Application(
            young_artist_id=artist.id,
            opportunity_id=opportunity_id,
            status='pending',
            full_name=request.form.get('full_name'),
            date_of_birth=request.form.get('date_of_birth'),
            nationality=request.form.get('nationality'),
            phone_number=request.form.get('phone_number'),
            cover_letter=request.form.get('cover_letter'),
            relevant_experience=request.form.get('relevant_experience'),
            availability=request.form.get('availability'),
            showcase_video_id=showcase_video_id
        )
        db.session.add(new_application)
        db.session.commit()

        return redirect(url_for('applications.my_applications'))

    return render_template('apply_opportunity.html', opportunity=opportunity, artist=artist, videos=videos)

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

@applications_bp.route('/review/<application_id>/<status>')
def review(application_id, status):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    application = Application.query.get_or_404(application_id)
    application.status = status
    db.session.commit()

    return redirect(url_for('opportunities.view_applications', opportunity_id=application.opportunity_id))

   