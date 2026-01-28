from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    usr_id = db.Column(db.Integer, primary_key=True)
    usr_first_name = db.Column(db.String(50), nullable=False)
    usr_last_name = db.Column(db.String(50), nullable=False)
    usr_email = db.Column(db.String(120), nullable=False, unique=True)
    usr_password = db.Column(db.String(100), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.rol_id', ondelete='RESTRICT'), nullable=False)
    usr_status = db.Column(db.String(20), nullable=False, default='activo')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())



    def __repr__(self):
        return f"<User {self.usr_first_name} {self.usr_last_name}>"
