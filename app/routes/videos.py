from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app import db
from app.models import Video, YoungArtist
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

videos_bp = Blueprint('videos', __name__)

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

@videos_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    artist = YoungArtist.query.filter_by(user_id=session['user_id']).first()

    if request.method == 'POST':
        file = request.files.get('video')
        title = request.form.get('title')
        art_form = request.form.get('art_form')

        if file and title and art_form:
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type='video',
                folder='creativelink/videos'
            )

            new_video = Video(
                young_artist_id=artist.id,
                title=title,
                art_form=art_form,
                video_url=upload_result['secure_url'],
                status='active'
            )
            db.session.add(new_video)
            db.session.commit()
            return redirect(url_for('videos.upload'))

    videos = Video.query.filter_by(young_artist_id=artist.id).all()  
    return render_template('upload_video.html', artist=artist, videos=videos)

@videos_bp.route('/delete/<video_id>')
def delete(video_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('videos.upload'))


@videos_bp.route('/artist/<artist_id>')
def artist_videos(artist_id):
    artist = YoungArtist.query.get_or_404(artist_id)
    videos = Video.query.filter_by(young_artist_id=artist_id, status='active').all()
    return render_template('artist_public_profile.html', artist=artist, videos=videos)