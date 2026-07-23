from flask import Blueprint, render_template, session, redirect, url_for

message_bp = Blueprint('messages', __name__)
@message_bp.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('messages.html')