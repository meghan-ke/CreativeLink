from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import inspect, text
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

def ensure_organisation_columns(app):
    with app.app_context():
        inspector = inspect(db.engine)
        columns = {column['name'] for column in inspector.get_columns('organisations')}
        new_columns = {
            'contact_email': 'VARCHAR(120)',
            'website': 'VARCHAR(255)',
            'phone': 'VARCHAR(50)',
            'logo_url': 'VARCHAR(255)',
            'about_us': 'TEXT'
        }

        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                db.session.execute(text(f"ALTER TABLE organisations ADD COLUMN {column_name} {column_type}"))

        db.session.commit()


def create_app():
    import os
    app = Flask(__name__, 
         static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
    app.secret_key = os.getenv('JWT_SECRET_KEY')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 1800

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.artists import artists_bp
    from app.routes.organisations import organisations_bp
    from app.routes.opportunities import opportunities_bp
    from app.routes.applications import applications_bp
    from app.routes.videos import videos_bp
    from app.routes.messages import messages_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(artists_bp, url_prefix='/api/artists')
    app.register_blueprint(organisations_bp, url_prefix='/api/organisations')
    app.register_blueprint(opportunities_bp, url_prefix='/api/opportunities')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')


    @app.route('/')
    def index():
        from flask import render_template
        return render_template('landing.html')

    with app.app_context():
        db.create_all()
        ensure_organisation_columns(app)

    return app
