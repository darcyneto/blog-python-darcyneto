import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "supabase.db")}'
    SECRET_KEY = 'Empty password.'
    SQLALCHEMY_TRACK_MODIFICATIONS = False