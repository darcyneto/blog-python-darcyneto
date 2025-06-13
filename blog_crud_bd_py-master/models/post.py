from models import db
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Relacionamento com User (back_populates para corresponder ao lado do User)
    user = relationship('User', back_populates='posts')
