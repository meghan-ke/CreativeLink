from app import db
import uuid
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    young_artist = db.relationship('YoungArtist', backref='user', uselist=False)
    organisation = db.relationship('Organisation', backref='user', uselist=False)

class YoungArtist(db.Model):
    __tablename__ = 'young_artists'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    art_form = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_picture_url = db.Column(db.String(255), nullable=True)
    cover_photo_url = db.Column(db.String(255), nullable=True)
    social_links = db.Column(db.Text, nullable=True)
    videos = db.relationship('Video', backref='young_artist', lazy=True)
    applications = db.relationship('Application', backref='young_artist', lazy=True)
    
class Organisation(db.Model):
    __tablename__ = 'organisations'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    org_name = db.Column(db.String(100), nullable=False)
    org_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    about_us = db.Column(db.Text, nullable=True)
    opportunities = db.relationship('Opportunity', backref='organisation', lazy=True)

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    young_artist_id = db.Column(db.String(36), db.ForeignKey('young_artists.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    art_form = db.Column(db.String(100), nullable=False)
    video_url = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')

class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id = db.Column(db.String(36), db.ForeignKey('organisations.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    criteria = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    art_form = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='open')
    applications = db.relationship('Application', backref='opportunity', lazy=True)

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    young_artist_id = db.Column(db.String(36), db.ForeignKey('young_artists.id'), nullable=False)
    opportunity_id = db.Column(db.String(36), db.ForeignKey('opportunities.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    full_name = db.Column(db.String(120), nullable=True)
    date_of_birth = db.Column(db.String(50), nullable=True)
    nationality = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    relevant_experience = db.Column(db.Text, nullable=True)
    availability = db.Column(db.String(100), nullable=True)
    showcase_video_id = db.Column(db.String(36), db.ForeignKey('videos.id'), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), nullable=False)
    receiver_id = db.Column(db.String(36), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    