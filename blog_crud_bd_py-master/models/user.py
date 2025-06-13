from sqlalchemy.orm import relationship
from models import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    # Relacionamento com Post (back_populates para corresponder ao lado do Post)
    posts = relationship('Post', back_populates='user', lazy='dynamic')  # Definindo posts
