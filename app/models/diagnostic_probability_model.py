from app import db
from sqlalchemy.dialects.postgresql import UUID

class DiagnosticProbability(db.Model):
    __tablename__ = 'diagnostic_probability'

    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('diagnostic_session.session_id', ondelete='CASCADE'), primary_key=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('subtopic.sub_id'), primary_key=True)
    p_mastery = db.Column(db.Numeric(4, 3), nullable=False, default=0.500)

    # Relaciones
    subtopic = db.relationship('Subtopic', backref='diagnostic_probabilities')