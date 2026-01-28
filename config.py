from decouple import config
from sqlalchemy.pool import NullPool

class Config:
  
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")
    
 
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = config("SECRET_KEY")
    JWT_SECRET_KEY = config("SECRET_KEY")