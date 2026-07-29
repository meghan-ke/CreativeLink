from app import create_app, db
from app.models import User, YoungArtist, Organisation, Video, Opportunity, Application, Message
from sqlalchemy import inspect, text

app = create_app()


def ensure_columns(table_name, columns):
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return

    existing_columns = {column['name'] for column in inspector.get_columns(table_name)}

    with db.engine.begin() as connection:
        for column_name, column_type in columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}'))


with app.app_context():
    ensure_columns('organisations', {
        'contact_email': 'VARCHAR(120)',
        'website': 'VARCHAR(255)',
        'phone': 'VARCHAR(50)',
        'logo_url': 'VARCHAR(255)',
        'about_us': 'TEXT'
    })
    ensure_columns('young_artists', {
        'bio': 'TEXT',
        'profile_picture_url': 'VARCHAR(255)',
        'cover_photo_url': 'VARCHAR(255)',
        'social_links': 'TEXT'
    })
    ensure_columns('applications', {
        'full_name': 'VARCHAR(120)',
        'date_of_birth': 'VARCHAR(50)',
        'nationality': 'VARCHAR(100)',
        'phone_number': 'VARCHAR(50)',
        'cover_letter': 'TEXT',
        'relevant_experience': 'TEXT',
        'availability': 'VARCHAR(100)',
        'showcase_video_id': 'VARCHAR(36)',
        'review_notes': 'TEXT'
    })
    db.create_all()
    print("All database tables created successfully")

if __name__ == '__main__':
    app.run(debug=True, port=5000)