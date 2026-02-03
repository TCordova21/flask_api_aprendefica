from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    audit_id = db.Column(db.BigInteger, primary_key=True)
    table_name = db.Column(db.Text, nullable=False)
    record_id = db.Column(db.Text, default='N/A')
    action = db.Column(db.Text, nullable=False)
    old_data = db.Column(JSONB)
    new_data = db.Column(JSONB)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.usr_id'), nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    changed_role = db.Column(db.Text)

    # Relación opcional para obtener datos del usuario que hizo el cambio
    user = db.relationship('User', backref='audit_actions', lazy=True)