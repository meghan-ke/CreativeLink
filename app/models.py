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
    videos = db.relationship('Video', backref='young_artist', lazy=True)
    applications = db.relationship('Application', backref='young_artist', lazy=True)
    
class Organisation(db.Model):
    __tablename__ = 'organisations'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    org_name = db.Column(db.String(100), nullable=False)
    org_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
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
    status = db.Column(db.String(20), default='submitted')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), nullable=False)
    receiver_id = db.Column(db.String(36), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    