from flask import Blueprint, render_template, session, redirect, url_for, request
from app import db
from app.models import Message, User
from datetime import datetime

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/send/<receiver_id>', methods=['GET', 'POST'])
def send(receiver_id=None):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        content = request.form.get('content')

        if not content or not receiver_id:
            return redirect(url_for('messages.inbox'))

        new_message = Message(
            sender_id=session['user_id'],
            receiver_id=receiver_id,
            content=content,
            sent_at=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('messages.inbox'))

    receiver = User.query.get(receiver_id)
    return render_template('send_message.html', receiver=receiver, receiver_id=receiver_id )

    
@messages_bp.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    received = Message.query.filter_by(
        receiver_id=session['user_id']
    ).order_by(Message.sent_at.desc()).all()

    sent = Message.query.filter_by(
        sender_id=session['user_id']
    ).order_by(Message.sent_at.desc()).all()

    return render_template('messages.html', received=received, sent=sent)