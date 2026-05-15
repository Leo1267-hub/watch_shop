import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY',"dev-secret-key")
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'