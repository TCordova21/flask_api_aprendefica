from app import db
from datetime import datetime

class StudentDomainProgress(db.Model):
    __tablename__ = 'student_domain_progress'
    sdp_id = db.Column(db.Integer, primary_key=True)
    enr_id = db.Column(db.Integer, db.ForeignKey('enrollment.enr_id', ondelete='CASCADE'), nullable=False)
    dom_id = db.Column(db.Integer, db.ForeignKey('domain.dom_id', ondelete='CASCADE'), nullable=False)
    progress_status = db.Column(db.String(20), nullable=False, default='no_dominado')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación para obtener el nombre del dominio fácilmente
    domain = db.relationship('Domain', backref='domain_progress_entries')