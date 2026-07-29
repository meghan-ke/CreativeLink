from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app import db, bcrypt
from app.models import User, YoungArtist, Organisation

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def landing():
    return render_template('landing.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error='Email already registered.')
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            email=email,
            password_hash=password_hash,
            role=role
        )
        db.session.add(new_user)
        db.session.flush()

        if role == 'artist':
            artist = YoungArtist(
                user_id=new_user.id,
                name=request.form.get('name'),
                age=int(request.form.get('age')),
                location=request.form.get('location'),
                art_form=request.form.get('art-form'),
                bio=request.form.get('bio') or None,
                profile_picture_url=request.form.get('profile_picture_url') or None,
                cover_photo_url=request.form.get('cover_photo_url') or None,
                social_links=request.form.get('social_links') or None
            )
            db.session.add(artist)

        if role == 'organisation':
            org = Organisation(
                user_id=new_user.id,
                org_name=request.form.get('org_name'),
                org_type=request.form.get('org_type'),
                location=request.form.get('location'),
                contact_email=request.form.get('contact_email') or email,
                website=request.form.get('website'),
                phone=request.form.get('phone'),
                logo_url=request.form.get('logo_url'),
                about_us=request.form.get('about_us')
            )
            db.session.add(org)

        db.session.commit()
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email= request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return render_template('login.html', error='Invalid email or password')
        
        session['user_id'] = user.id
        session['role'] = user.role

        if user.role.lower() == 'artist':
            return redirect(url_for('artists.dashboard'))
        else:
            return redirect(url_for('organisations.dashboard'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


