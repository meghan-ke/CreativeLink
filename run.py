from app import create_app, db
from app.models import User, YoungArtist, Organisation, Video, Opportunity, Application, Message

app = create_app()

with app.app_context():
    db.create_all()
    print("All database tables created successfully")

if __name__ == '__main__':
    app.run(debug=True, port=5000)