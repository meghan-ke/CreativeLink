from flask import Blueprint, render_template, session, redirect, url_for
from app.models import Application

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/my-applications')
def my_applications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('browse_opportunities.html', opportunities=[], placeholder=True)