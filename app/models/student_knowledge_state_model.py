from app import db
from datetime import datetime

class StudentKnowledgeState(db.Model):
    __tablename__ = 'student_knowledge_state'
    sks_id = db.Column(db.Integer, primary_key=True)
    enr_id = db.Column(db.Integer, db.ForeignKey('enrollment.enr_id', ondelete='CASCADE'), nullable=False)
    sub_id = db.Column(db.Integer, db.ForeignKey('subtopic.sub_id', ondelete='CASCADE'), nullable=False)
    mastery_level = db.Column(db.String(20), nullable=False, default='no_dominado')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación para obtener el nombre del subtema fácilmente
    subtopic = db.relationship('Subtopic', backref='knowledge_states')

