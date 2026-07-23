from flask import Blueprint, render_template, session, redirect, url_for
    
videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/upload')
def upload():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('upload_video.html')
