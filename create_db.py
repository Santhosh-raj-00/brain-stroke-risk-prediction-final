from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    print('Database URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    db.create_all()
    print('Tables created successfully')