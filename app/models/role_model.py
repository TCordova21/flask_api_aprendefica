from app import db

class Role(db.Model):
    __tablename__ = 'roles'

    rol_id = db.Column(db.Integer, primary_key=True)
    rol_name = db.Column(db.String(50), unique=True, nullable=False)
    rol_description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    

    def __repr__(self):
        return f"<Role {self.rol_name}>"
